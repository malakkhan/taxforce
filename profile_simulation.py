#!/usr/bin/env python3
"""
Profiling script for tax compliance simulation.
Identifies performance bottlenecks and potential parallelization opportunities.

Run from project root: python3 profile_simulation.py [config.json]
"""
import sys
import time
import cProfile
import pstats
import io
import numpy as np
from functools import wraps

from core.model import TaxComplianceModel
from core.config import SimulationConfig
from core.simcache import clear_all_caches


# ============================================================================
# Timing Utilities
# ============================================================================

class TimingContext:
    """Context manager for timing code blocks."""
    def __init__(self, name, collector):
        self.name = name
        self.collector = collector
    
    def __enter__(self):
        self.start = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        elapsed = time.perf_counter() - self.start
        self.collector[self.name] = self.collector.get(self.name, 0) + elapsed


class InstrumentedModel(TaxComplianceModel):
    """Wraps TaxComplianceModel to collect per-phase timing data."""
    
    def __init__(self, *args, **kwargs):
        self.phase_times = {
            "agent_steps": 0.0,
            "audits": 0.0,
            "norm_updates": 0.0,
            "data_collection": 0.0,
        }
        self.step_times = []
        super().__init__(*args, **kwargs)
    
    def step(self):
        step_start = time.perf_counter()
        self.current_step += 1
        
        with TimingContext("agent_steps", self.phase_times):
            self.agents.shuffle_do("step")
        
        with TimingContext("audits", self.phase_times):
            self.run_audits()
        
        with TimingContext("norm_updates", self.phase_times):
            self.update_norms()
        
        with TimingContext("data_collection", self.phase_times):
            self.datacollector.collect(self)
        
        clear_all_caches()
        self.step_times.append(time.perf_counter() - step_start)


# ============================================================================
# Profiling Functions
# ============================================================================

def run_cprofile(config, steps=100, seed=42):
    """Run simulation with cProfile and return stats."""
    profiler = cProfile.Profile()
    
    profiler.enable()
    model = TaxComplianceModel(config=config, seed=seed)
    model.run(steps)
    profiler.disable()
    
    # Capture stats
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats('cumulative')
    stats.print_stats(30)
    
    return stream.getvalue(), stats


def run_instrumented(config, steps=100, seed=42):
    """Run simulation with per-phase instrumentation."""
    
    # Time initialization
    init_start = time.perf_counter()
    model = InstrumentedModel(config=config, seed=seed)
    init_time = time.perf_counter() - init_start
    
    # Time simulation
    sim_start = time.perf_counter()
    model.run(steps)
    sim_time = time.perf_counter() - sim_start
    
    return {
        "init_time": init_time,
        "sim_time": sim_time,
        "total_time": init_time + sim_time,
        "phase_times": model.phase_times,
        "step_times": model.step_times,
        "model": model,
    }


def analyze_parallelization(results):
    """Analyze potential parallelization opportunities."""
    opportunities = []
    phase_times = results["phase_times"]
    total = sum(phase_times.values())
    
    if total == 0:
        return opportunities
    
    # Agent steps are embarrassingly parallel
    agent_pct = phase_times["agent_steps"] / total * 100
    if agent_pct > 20:
        opportunities.append({
            "target": "Agent Steps (behavior.decide)",
            "time_pct": agent_pct,
            "approach": "joblib.Parallel or multiprocessing.Pool - each agent is independent",
            "complexity": "Medium - need to handle Mesa agent state carefully",
        })
    
    # Norm updates involve neighbor interactions
    norm_pct = phase_times["norm_updates"] / total * 100
    if norm_pct > 20:
        opportunities.append({
            "target": "Norm Updates",
            "time_pct": norm_pct,
            "approach": "Pre-compute interaction matrix, vectorize norm calculations with NumPy",
            "complexity": "Medium - interaction sets can be computed in parallel",
        })
    
    # Audits are typically fast but may benefit from vectorization
    audit_pct = phase_times["audits"] / total * 100
    if audit_pct > 10:
        opportunities.append({
            "target": "Audit Selection",
            "time_pct": audit_pct,
            "approach": "Vectorize risk score comparisons with NumPy",
            "complexity": "Low",
        })
    
    return opportunities


# ============================================================================
# Output Formatting
# ============================================================================

def print_header(text):
    print(f"\n{'='*70}")
    print(f" {text}")
    print('='*70)


def print_phase_breakdown(results):
    """Print per-phase timing breakdown."""
    phase_times = results["phase_times"]
    total = sum(phase_times.values())
    
    print(f"\n{'Phase':<25} {'Time (s)':<12} {'% of Sim':<10}")
    print("-" * 50)
    
    for phase, time_val in sorted(phase_times.items(), key=lambda x: -x[1]):
        pct = (time_val / total * 100) if total > 0 else 0
        print(f"{phase:<25} {time_val:<12.4f} {pct:<10.1f}%")
    
    print("-" * 50)
    print(f"{'Total Simulation':<25} {total:<12.4f}")


def print_step_analysis(results):
    """Print per-step timing analysis."""
    step_times = results["step_times"]
    if not step_times:
        return
    
    arr = np.array(step_times)
    print(f"\nPer-step timing (n={len(step_times)}):")
    print(f"  Mean:   {arr.mean()*1000:.2f} ms")
    print(f"  Std:    {arr.std()*1000:.2f} ms")
    print(f"  Min:    {arr.min()*1000:.2f} ms")
    print(f"  Max:    {arr.max()*1000:.2f} ms")
    print(f"  Median: {np.median(arr)*1000:.2f} ms")


def print_parallelization_analysis(opportunities):
    """Print parallelization opportunities."""
    if not opportunities:
        print("No significant parallelization opportunities identified.")
        return
    
    for i, opp in enumerate(opportunities, 1):
        print(f"\n{i}. {opp['target']} ({opp['time_pct']:.1f}% of runtime)")
        print(f"   Approach: {opp['approach']}")
        print(f"   Complexity: {opp['complexity']}")


# ============================================================================
# Main
# ============================================================================

def main(config_path=None, steps=100):
    print_header("SIMULATION PROFILING")
    
    # Load config
    if config_path:
        print(f"Loading config: {config_path}")
        config = SimulationConfig.from_json(config_path)
    else:
        config = SimulationConfig.default()
    
    n_agents = config.simulation["n_agents"]
    print(f"Agents: {n_agents}, Steps: {steps}")
    
    # -------------------------------------------------------------------------
    # Phase 1: Instrumented run for phase-level timing
    # -------------------------------------------------------------------------
    print_header("PHASE-LEVEL TIMING")
    
    results = run_instrumented(config, steps=steps)
    
    print(f"\nInitialization time: {results['init_time']:.4f}s")
    print(f"Simulation time:     {results['sim_time']:.4f}s")
    print(f"Total time:          {results['total_time']:.4f}s")
    
    print_phase_breakdown(results)
    print_step_analysis(results)
    
    # -------------------------------------------------------------------------
    # Phase 2: cProfile for function-level breakdown
    # -------------------------------------------------------------------------
    print_header("FUNCTION-LEVEL PROFILING (cProfile)")
    
    profile_output, stats = run_cprofile(config, steps=steps)
    print(profile_output)
    
    # -------------------------------------------------------------------------
    # Phase 3: Parallelization analysis
    # -------------------------------------------------------------------------
    print_header("PARALLELIZATION OPPORTUNITIES")
    
    opportunities = analyze_parallelization(results)
    print_parallelization_analysis(opportunities)
    
    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    print_header("SUMMARY")
    
    total = results["total_time"]
    per_step = (results["sim_time"] / steps) * 1000
    
    print(f"Total runtime:      {total:.2f}s")
    print(f"Per-step average:   {per_step:.2f} ms")
    print(f"Projected 1000 steps: {per_step * 10:.2f}s")
    
    # Identify biggest bottleneck
    phase_times = results["phase_times"]
    if phase_times:
        biggest = max(phase_times.items(), key=lambda x: x[1])
        pct = biggest[1] / sum(phase_times.values()) * 100
        print(f"\nBiggest bottleneck: {biggest[0]} ({pct:.1f}%)")
    
    print()


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    steps = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    main(config_path, steps)
