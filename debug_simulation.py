#!/usr/bin/env python3
"""
Debug script to run simulation and analyze results.
Run from project root: python3 debug_simulation.py [config.json]
"""
import sys
import numpy as np
from core.model import TaxComplianceModel
from core.config import SimulationConfig


def print_header(text):
    print(f"\n{'='*60}")
    print(f" {text}")
    print('='*60)


def run_analysis(config_path=None):
    print_header("SIMULATION SETUP")
    
    if config_path:
        print(f"Loading config: {config_path}")
        cfg = SimulationConfig.from_json(config_path)
    else:
        cfg = SimulationConfig.default()
    
    print(f"Agents: {cfg.simulation['n_agents']}")
    rates = cfg.enforcement['audit_rate']
    print(f"Audit rate: {rates['private']:.1%} private, {rates['business']:.2%} business")
    print(f"Penalty rate: {cfg.enforcement['penalty_rate']}x")
    print(f"Tax rate: {cfg.enforcement['tax_rate']:.1%}")
    print(f"Belief strategy: {cfg.belief_strategy}")
    
    model = TaxComplianceModel(config=cfg, seed=42)
    
    # Initial state
    print_header("INITIAL STATE (t=0)")
    
    private = [a for a in model.agents if a.occupation == "private"]
    business = [a for a in model.agents if a.occupation == "business"]
    
    print(f"Private agents: {len(private)} ({len(private)/len(list(model.agents)):.1%})")
    print(f"Business agents: {len(business)} ({len(business)/len(list(model.agents)):.1%})")
    
    print(f"\nPrivate avg income: €{np.mean([a.true_income for a in private]):,.0f}")
    print(f"Business avg income: €{np.mean([a.true_income for a in business]):,.0f}")
    
    print(f"\nAvg personal norms (private): {np.mean([a.traits.personal_norms for a in private]):.2f}")
    print(f"Avg personal norms (business): {np.mean([a.traits.personal_norms for a in business]):.2f}")
    
    print(f"\nAvg subjective audit prob (private): {np.mean([a.traits.subjective_audit_prob for a in private]):.1f}%")
    print(f"Avg subjective audit prob (business): {np.mean([a.traits.subjective_audit_prob for a in business]):.1f}%")
    
    # Run simulation
    print_header("RUNNING SIMULATION (100 steps)")
    model.run(100)
    
    df = model.datacollector.get_model_vars_dataframe()
    
    # Results over time
    print_header("RESULTS OVER TIME")
    
    steps_to_show = [0, 10, 25, 50, 75, 99]
    print(f"{'Step':>6} {'Compliance':>12} {'Tax Gap':>14}")
    print("-" * 36)
    for step in steps_to_show:
        row = df.iloc[step]
        print(f"{step:>6} {row['Compliance_Rate']:>12.1%} {row['Tax_Gap']:>14,.0f}")
    
    # Final state analysis
    print_header("FINAL STATE (t=100)")
    
    compliant = [a for a in model.agents if a.is_compliant]
    evaders = [a for a in model.agents if not a.is_compliant]
    
    print(f"Compliant agents: {len(compliant)} ({len(compliant)/len(list(model.agents)):.1%})")
    print(f"Evading agents: {len(evaders)} ({len(evaders)/len(list(model.agents)):.1%})")
    
    if evaders:
        print(f"\nEvaders breakdown:")
        private_evaders = [a for a in evaders if a.occupation == "private"]
        business_evaders = [a for a in evaders if a.occupation == "business"]
        print(f"  Private: {len(private_evaders)}")
        print(f"  Business: {len(business_evaders)}")
        print(f"  Avg evaded amount: €{np.mean([a.evaded_income for a in evaders]):,.0f}")
    
    print(f"\nFinal social norms (private): {np.mean([a.traits.social_norms for a in private]):.2f}")
    print(f"Final social norms (business): {np.mean([a.traits.social_norms for a in business]):.2f}")
    
    print(f"\nFinal societal norms (private): {np.mean([a.traits.societal_norms for a in private]):.2f}")
    print(f"Final societal norms (business): {np.mean([a.traits.societal_norms for a in business]):.2f}")
    
    print(f"\nFinal subjective audit prob (private): {np.mean([a.traits.subjective_audit_prob for a in private]):.1f}%")
    print(f"Final subjective audit prob (business): {np.mean([a.traits.subjective_audit_prob for a in business]):.1f}%")
    
    # Summary statistics
    print_header("SUMMARY STATISTICS")
    
    print(f"Initial compliance: {df['Compliance_Rate'].iloc[0]:.1%}")
    print(f"Final compliance: {df['Compliance_Rate'].iloc[-1]:.1%}")
    print(f"Min compliance: {df['Compliance_Rate'].min():.1%} (step {df['Compliance_Rate'].idxmin()})")
    print(f"Max compliance: {df['Compliance_Rate'].max():.1%} (step {df['Compliance_Rate'].idxmax()})")
    
    print(f"\nInitial tax gap: €{df['Tax_Gap'].iloc[0]:,.0f}")
    print(f"Final tax gap: €{df['Tax_Gap'].iloc[-1]:,.0f}")
    print(f"Max tax gap: €{df['Tax_Gap'].max():,.0f}")
    
    print(f"\nTotal taxes collected over 100 years: €{df['Total_Taxes'].sum():,.0f}")
    
    # Critical analysis
    print_header("CRITICAL ANALYSIS")
    
    issues = []
    
    if df['Compliance_Rate'].iloc[-1] > 0.99:
        issues.append("Compliance converges to 100%")
    
    if df['Compliance_Rate'].std() < 0.01:
        issues.append("Very low variance in compliance")
    
    if np.mean([a.traits.social_norms for a in model.agents]) < 1.5:
        issues.append("Social norms collapsed to minimum")
    
    if np.mean([a.traits.subjective_audit_prob for a in model.agents]) > 90:
        issues.append("Audit probability very high")
    
    if not evaders:
        issues.append("No evaders at end")
    
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("✓ No obvious issues detected")
    
    print()


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    run_analysis(config_path)
