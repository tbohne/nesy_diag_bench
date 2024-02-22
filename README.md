# NeSy Diag Benchmark

Toy world (evaluation system) for neuro-symbolic (**Symbolic[Neuro]**) diagnosis systems.

## Usage

*Instance generation:*
```
$ python nesy_diag_bench/instance_gen.py --seed 42 --components 129 --anomaly-percentage 0.1 --affected-by-ub-percentage 0.2 --fault-path-comp-ub-percentage 0.5 --distractor-ub-percentage 0.5 --instances-per-conf 100 [--extend-kg]
```

*Evaluation:*
```
$ python nesy_diag_bench/eval.py --instances instances/
```

## Naming scheme for generated instances

```
<num_comp>_<num_errors>_<anomaly_percentage>_<affected_by_ub>_<fault_path_comp_ub>_<distractor_ub>_<seed>_<idx>.json
```

## Component-Dataset Mapping

|component | dataset        | model | test_data |
|----------|----------------|-------| --------- |
| C0       | Coffee (ID 10) | C0.h5 | C0.tsv    |
