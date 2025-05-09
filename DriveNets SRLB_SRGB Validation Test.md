# DriveNets SRLB/SRGB Validation Test

1. #### Verify that the configured ranges for srlb and srgb (isis-sr) match the actual ("In use") ranges. The ranges for SRLB and SRGB should be as follows:

```

| Protocols   | Total labels   | Label ranges   |
|-------------+----------------+----------------|
| srlb        | 1000           | 15000-15999    |
| srgb        | 400000         | 400000-799999  |
```

Execute on DUT: `show mpls label-allocation tables` command.

- Command output:
```
In use:

| Protocols                  | Total labels   | Label ranges                            |
|----------------------------+----------------+-----------------------------------------|
| srlb                       | 1000           | 15000-15999                             |
| srgb                       | 400000         | 400000-799999                           |

Configured:

| Protocols   | Total labels   | Label ranges   |
|-------------+----------------+----------------|
| srlb        | 1000           | 15000-15999    |
| srgb        | 400000         | 400000-799999  |
```

## Note: 'Total labels' column represents the size, i.e. the diff from the end to the start.

2. #### Output to the User:

List each device on which the validation occured. For each device list the confirmation whether the 'In-use' ranges are according to the ranges given in the step 1.

If Failure - detailed reason why and where.