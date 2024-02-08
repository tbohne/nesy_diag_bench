# NeSy Diag Benchmark

Toy world (evaluation system) for neuro-symbolic (**Symbolic[Neuro]**) diagnosis systems.

## Usage

```
$ python instance_gen.py --seed 42 --components 6 --input-error-codes 1 --anomaly-percentage 0.2 --affected-by-ub-percentage 0.3 --fault-path-comp-ub-percentage 1 --distractor-ub-percentage 0.5 [--extend-kg]
```

## Naming scheme for generated instances

```
<components>_<error_codes>_<input_errors>_<seed>.json
```
