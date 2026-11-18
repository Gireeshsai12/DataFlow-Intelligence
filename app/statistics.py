from math import ceil, sqrt

from scipy.stats import norm


def checkout_experiment(arms):
    control, treatment = (arms.get(key, (0, 0)) for key in ("Control", "Treatment"))
    n1, x1 = control
    n2, x2 = treatment
    if min(n1, n2) == 0:
        return {"control_sessions": n1, "treatment_sessions": n2, "recommendation": "Collect observations in both arms."}
    p1, p2 = x1 / n1, x2 / n2
    delta = p2 - p1
    pooled = (x1 + x2) / (n1 + n2)
    expected = min(n1*pooled, n1*(1-pooled), n2*pooled, n2*(1-pooled))
    if expected >= 5:
        se = sqrt(pooled * (1-pooled) * (1/n1 + 1/n2))
        p = float(2 * norm.sf(abs(delta / se)))
        margin = float(norm.ppf(.975)) * sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)
    else:
        p, margin = None, None
    recommendation = "Collect more observations for the normal approximation."
    if p is not None:
        recommendation = "The test did not detect a difference at the 5% level."
        if p < .05:
            recommendation = "Review practical impact and guardrails before rollout." if delta > 0 else "Treatment reduced conversion. Review the checkout design."
    return dict(control_sessions=n1, treatment_sessions=n2, control_rate_pct=100*p1,
                treatment_rate_pct=100*p2, effect_pp=100*delta,
                relative_lift_pct=100*delta/p1 if p1 else None, p_value=p,
                ci_low_pp=100*(delta-margin) if margin is not None else None,
                ci_high_pp=100*(delta+margin) if margin is not None else None,
                recommendation=recommendation)


def sample_size(baseline, target, power=.8):
    if not (0 < baseline < 1 and 0 < target < 1 and baseline != target and .5 < power < 1):
        raise ValueError("Provide different proportions in (0,1) and power in (.5,1).")
    mean = (baseline + target) / 2
    signal = norm.ppf(.975)*sqrt(2*mean*(1-mean))
    noise = norm.ppf(power)*sqrt(baseline*(1-baseline)+target*(1-target))
    return ceil(((signal+noise)/(target-baseline))**2)


def describe(values):
    import numpy as np
    import pandas as pd

    series = pd.to_numeric(pd.Series(values, dtype=object), errors="coerce").dropna()
    clean = series[np.isfinite(series)].to_numpy(dtype=float)
    if not clean.size:
        return dict(observations=0, mean=None, median=None, p90=None, variance=None, standard_deviation=None)
    return dict(observations=int(clean.size), mean=float(np.mean(clean)), median=float(np.median(clean)),
                p90=float(np.percentile(clean,90)), variance=float(np.var(clean,ddof=1)) if clean.size>1 else None,
                standard_deviation=float(np.std(clean,ddof=1)) if clean.size>1 else None)
