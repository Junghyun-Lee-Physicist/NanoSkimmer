# NanoAODSkim

Utilities for running NanoAOD post-processing without modifying the upstream `PhysicsTools/NanoAODTools` package.

## Setup
1. Prepare a CMSSW area and fetch the official NanoAOD tools:
   ```bash
   git cms-init
   git cms-addpkg PhysicsTools/NanoAODTools
   ```
2. Place the contents of this `NanoAODSkim` directory inside your CMSSW working area.

## Local skimming
`scripts/nano_postproc.py` wraps the standard `NanoAODTools` post-processor and records the start, finish and possible failure of each input file.  A summary is written to `postproc.log`.

Example:
```bash
python3 scripts/nano_postproc.py outDir input.root -I MyModule myConstr
```

## CRAB submission
`crab/submit_and_monitor.py` submits one CRAB task per dataset and periodically checks their status.  Progress for each task is stored in `crab_status.log`.

Example:
```bash
python3 crab/submit_and_monitor.py --datasets /A/B/C /D/E/F --interval 600
```

The script will keep polling until all jobs complete, allowing unfinished samples or files to be spotted easily.
