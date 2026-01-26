#!/usr/bin/env python3
# Calibration Validation: 5000 agents × 50 steps × 15 seeds
import sys, os, gc, numpy as np
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.model import TaxComplianceModel
from core.config import SimulationConfig

def run_seed(seed):
    cfg = SimulationConfig.from_json('core/configs/config_final.json')
    model = TaxComplianceModel(config=cfg, seed=seed)
    
    biz = [a for a in model.agents if a.occupation == 'business']
    biz_d, biz_h = [a for a in biz if a.behavior_type == 'dishonest'], [a for a in biz if a.behavior_type == 'honest']
    priv = [a for a in model.agents if a.occupation == 'private']
    priv_d, priv_h = [a for a in priv if a.behavior_type == 'dishonest'], [a for a in priv if a.behavior_type == 'honest']
    priv_d_ratio = len(priv_d) / len(priv) * 100 if priv else 0
    
    results = []
    for step in range(1, 51):
        model.step()
        if step in [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]:
            ev_mass = sum(a.evaded_income for a in biz_d)
            err_mass = sum(a.evaded_income for a in biz_h)
            biz_inc = sum(a.true_income for a in biz)
            gap = (ev_mass + err_mass) / biz_inc * 100 if biz_inc > 0 else 0
            err_share = err_mass / (ev_mass + err_mass) * 100 if (ev_mass + err_mass) > 0 else 0
            
            priv_ev = sum(a.evaded_income for a in priv_d)
            priv_err = sum(a.evaded_income for a in priv_h)
            priv_inc = sum(a.true_income for a in priv)
            priv_gap = (priv_ev + priv_err) / priv_inc * 100 if priv_inc > 0 else 0
            
            results.append({
                'step': step, 'gap': gap, 'err_share': err_share,
                'evading': len([a for a in biz_d if a.evaded_income > 0]),
                'priv_gap': priv_gap, 'priv_d_ratio': priv_d_ratio,
                'biz_h_cmp': len([a for a in biz_h if a.is_compliant]) / len(biz_h) * 100 if biz_h else 0,
                'biz_d_cmp': len([a for a in biz_d if a.is_compliant]) / len(biz_d) * 100 if biz_d else 0,
                'priv_h_cmp': len([a for a in priv_h if a.is_compliant]) / len(priv_h) * 100 if priv_h else 0,
                'priv_d_cmp': len([a for a in priv_d if a.is_compliant]) / len(priv_d) * 100 if priv_d else 0,
            })
    del model; gc.collect()
    return results

if __name__ == "__main__":
    print("="*80)
    print("CALIBRATION VALIDATION (5000 agents × 50 steps × 15 seeds)")
    print("="*80)
    print("Targets: SME Gap 4.5-5.5%, Error Share 50-65%, Priv Gap 0.2-0.5%, Priv Dishonest 15-25%\n")
    
    seeds = list(range(42, 57))
    print(f"Running {len(seeds)} seeds in parallel...")
    with Pool(15, maxtasksperchild=1) as pool:
        all_results = pool.map(run_seed, seeds)
    print("Done!\n")
    
    steps = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    print(f"{'Step':>4} | {'SME Gap':>12} | {'Biz H':>10} | {'Biz D':>10} | {'Prv H':>10} | {'Prv D':>10}")
    print("-"*80)
    
    data = {}
    for i, step in enumerate(steps):
        g = [r[i]['gap'] for r in all_results]
        e = [r[i]['err_share'] for r in all_results]
        pg = [r[i]['priv_gap'] for r in all_results]
        pd = [r[i]['priv_d_ratio'] for r in all_results]
        ev = [r[i]['evading'] for r in all_results]
        bhc = [r[i]['biz_h_cmp'] for r in all_results]
        bdc = [r[i]['biz_d_cmp'] for r in all_results]
        phc = [r[i]['priv_h_cmp'] for r in all_results]
        pdc = [r[i]['priv_d_cmp'] for r in all_results]
        data[step] = {'g': np.mean(g), 'e': np.mean(e), 'pg': np.mean(pg), 'pd': np.mean(pd),
                      'ev': np.mean(ev), 'bhc': np.mean(bhc), 'bdc': np.mean(bdc), 'phc': np.mean(phc), 'pdc': np.mean(pdc)}
        print(f"{step:4d} | {np.mean(g):5.2f}% ±{np.std(g):4.2f} | {np.mean(bhc):5.1f}%±{np.std(bhc):3.1f} | {np.mean(bdc):5.1f}%±{np.std(bdc):3.1f} | {np.mean(phc):5.1f}%±{np.std(phc):3.1f} | {np.mean(pdc):5.1f}%±{np.std(pdc):3.1f}")
    
    s1, s50 = data[1], data[50]
    print("\n" + "="*80)
    print("STABILITY ANALYSIS")
    print("="*80)
    print(f"\nDrift (Step 1 → 50):")
    print(f"  SME Gap:     {s1['g']:.2f}% → {s50['g']:.2f}% (Δ = {s50['g']-s1['g']:+.2f}%)")
    print(f"  Error Share: {s1['e']:.1f}% → {s50['e']:.1f}% (Δ = {s50['e']-s1['e']:+.1f}%)")
    print(f"  Private Gap: {s1['pg']:.2f}% → {s50['pg']:.2f}%")
    print(f"\nCompliance Rates:")
    print(f"  SME Honest:    {s1['bhc']:.1f}% → {s50['bhc']:.1f}%  |  SME Dishonest:    {s1['bdc']:.1f}% → {s50['bdc']:.1f}%")
    print(f"  Priv Honest:   {s1['phc']:.1f}% → {s50['phc']:.1f}%  |  Priv Dishonest:   {s1['pdc']:.1f}% → {s50['pdc']:.1f}%")
    
    print("\n" + "="*80)
    print("TARGET CHECK")
    print("="*80)
    def chk(n, v, lo, hi): return f"{'✓' if lo <= v <= hi else '✗'} {n}: {v:.2f}% (target: {lo}-{hi}%)"
    print(f"\nStep 1: {chk('SME Gap', s1['g'], 4.5, 5.5)} | {chk('Err Share', s1['e'], 50, 65)}")
    print(f"        {chk('Priv Gap', s1['pg'], 0.2, 0.5)} | {chk('Priv Dshst', s1['pd'], 15, 25)}")
    g_ok = 4.5 <= s1['g'] <= 5.5 and 4.5 <= s50['g'] <= 5.5
    e_ok = 50 <= s1['e'] <= 65 and abs(s50['e'] - s1['e']) <= 10
    pg_ok = 0.2 <= s1['pg'] <= 0.5
    pd_ok = 15 <= s1['pd'] <= 25
    print("\n" + "="*80)
    print("🎉 ALL METRICS IN TARGET!" if (g_ok and e_ok and pg_ok and pd_ok) else "⚠ Some metrics need adjustment")
    print("="*80)
