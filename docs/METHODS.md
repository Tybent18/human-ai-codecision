# Methods

[← Home](../README.md) · [Architecture](ARCHITECTURE.md) · [Evidence](EVIDENCE.md) · [Human study](HUMAN_STUDY.md)

## Collaborative state

At trial \(t\), the observable collaborative state is:

\[
s_t = (U_t, C_t, R_t, T_t, W_t)
\]

where \(U\) is inferred human uncertainty, \(C\) is calibrated AI confidence, \(R\) is predicted decision risk, \(T\) is the bounded trust state, and \(W\) is workload.

## Human uncertainty

The reference estimator combines normalized latency \(l\), hesitation \(h\), revisions \(v\), recent error rate \(e\), and inverse self-reported confidence \(1-c_h\):

\[
U = 0.20l + 0.22h + 0.13v + 0.18e + 0.27(1-c_h)
\]

These fixed Stage One weights are operational assumptions, not validated psychological coefficients. Participant data must be used to fit and externally validate future estimators.

Stage One thresholds were frozen after a single calibration run that inspected score distributions without testing an outcome hypothesis: uncertainty `0.42`, AI confidence `0.25`, critical risk `0.55`, and AI-over-human confidence margin `0.05`. They must be evaluated on new seeds before confirmatory use.

## AI confidence

AI confidence is normalized predictive-entropy reduction:

\[
C = 1 - \frac{-\sum_i p_i \log p_i}{\log K}
\]

The late-stage synthetic trials add model noise to emulate distribution shift and test whether intervention policies remain safe when AI reliability deteriorates.

## Adaptive override gate

Override requires all of the following:

1. Human and AI disagree.
2. Human uncertainty exceeds its threshold.
3. AI confidence exceeds its threshold.
4. predicted risk exceeds its critical threshold.
5. AI confidence exceeds human confidence by a safety margin.
6. collaborative trust remains above a minimum.

Failing the gate produces assistance, recommendation, or deference—not an override.

## Trust dynamics

Trust is updated in log-odds space and mapped back to \([0,1]\). Incorrect AI interventions incur a larger negative update than the positive update from correct interventions. The target is calibrated reliance, not maximum trust.

## Collaborative utility

The Stage One score weights accuracy, trust calibration, efficiency, and autonomy, with a penalty for unnecessary overrides. It is a declared design objective used for comparison—not a universal ethical value function.
