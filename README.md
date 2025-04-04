# NeSy Diag Benchmark

Toy world (evaluation system) for neuro-symbolic (**Symbolic[Neuro]**) diagnosis systems.
<img src="img/eval_proc.svg" width="420">

## Usage

*Instance set generation:*
```
$ python nesy_diag_bench/instance_gen.py --seed 42 --components 129 --anomaly-percentage 0.1 --affected-by-ub-percentage 0.2 --fault-path-comp-ub-percentage 0.5 --distractor-ub-percentage 0.5 --instances-per-conf 100 --model-acc-lb 0.6 --model-acc-ub 0.95 [--sim-classification-models] [--extend-kg]
```

*Evaluation:*
```
$ python nesy_diag_bench/eval.py --instances instances/ [--v] [--sim]
```

*Generation of cumulative results:*
```
$ python nesy_diag_bench/analyze_res.py --instance-set-sol SOLUTION_DIR/
```

## Naming scheme for generated instances

```
<num_comp>_<anomaly_percentage>_<affected_by_ub>_<fault_path_comp_ub>_<distractor_ub>_<model_acc_lb>_<model_acc_ub>_<seed>_<idx>.json
```

## Parameter Config for the Experiments

The semantics of all specified parameters are defined in the paper. All parameters considered are either set to practically plausible, domain-agnostic values or intervals were specified, the limits of which are empirically justified in the paper.

- $C \in [10, 25, 50, 75, 100, 250, 500, 1000]$
- $\alpha \in [.01, .02, .03, .05, .1, .15, .2]$
- $\beta \in [.05, .1, .2]$
- $\epsilon \in [.25, .5, 1.0]$
- $\delta \in [.05, .1, .25, .5]$
- $\gamma^{LB} \in [.65, .75, .85, .90, .95, 1.0]$
- $\gamma^{UB} \in [.75, .85, .95, .95, .99, 1.0]$

## Reduced Parameter Config Used in the Paper

- $C := 129$
- $\alpha \in [.01, .05, .1, .2]$
- $\beta \in [.05, .1, .2]$
- $\epsilon := .5$
- $\delta := .1$
- $\gamma^{LB} \in [.90, .95, 1.0]$
- $\gamma^{UB} \in [.95, .99, 1.0]$

## Component -> UCR-Dataset (`UCRArchive_2018`) Mapping

|component | dataset        | model | test_data | precision | accuracy | recall | architecture | #train | #test | len    | #classes | desc                                          |
|----------|----------------|-------|-----------|-----------|----------|--------|--------------|--------|-------|--------|----------|-----------------------------------------------|
| C0       | Coffee (ID 10) | C0.h5 | C0.tsv    | 1.0       | 1.0      | 1.0    | FCN          | 28     | 28    | 286    | 2        | spectrographs: dist. Robusta / Arabica coffee |
