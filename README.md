# NeSy Diag Benchmark

Toy world (evaluation system) for neuro-symbolic (**Symbolic[Neuro]**) diagnosis systems.

## Usage

*Instance set generation:*
```
$ python nesy_diag_bench/instance_gen.py --seed 42 --components 129 --anomaly-percentage 0.1 --affected-by-ub-percentage 0.2 --fault-path-comp-ub-percentage 0.5 --distractor-ub-percentage 0.5 --instances-per-conf 100 --model-acc-lb 0.6 --model-acc-ub 0.95 [--sim-classification-models] [--extend-kg]
```

*Evaluation:*
```
$ python nesy_diag_bench/eval.py --instances instances/ [--v] [--sim]
```

## Naming scheme for generated instances

```
<num_comp>_<anomaly_percentage>_<affected_by_ub>_<fault_path_comp_ub>_<distractor_ub>_<model_acc_lb>_<model_acc_ub>_<seed>_<idx>.json
```

## Component -> UCR-Dataset Mapping

|component | dataset        | model | test_data | precision | accuracy | recall | architecture | #train | #test | len    | #classes | desc                                          |
|----------|----------------|-------|-----------|-----------|----------|--------|--------------|--------|-------|--------|----------|-----------------------------------------------|
| C0       | Coffee (ID 10) | C0.h5 | C0.tsv    | 1.0       | 1.0      | 1.0    | FCN          | 28     | 28    | 286    | 2        | spectrographs: dist. Robusta / Arabica coffee |
