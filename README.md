# NeSy Diag Benchmark

Toy world (evaluation system) for neuro-symbolic (**Symbolic[Neuro]**) diagnosis systems.

## Usage

```
$ python instance_gen.py --seed 42 --components 15 --anomaly-percentage 0.2 --affected-by-ub-percentage 1 --fault-path-comp-ub-percentage 1 --distractor-ub-percentage 0.5 [--extend-kg]
```

## Naming scheme for generated instances

```
<num_comp>_<num_errors>_<anomaly_percentage>_<affected_by_ub>_<fault_path_comp_ub>_<distractor_ub>_<seed>.json
```
