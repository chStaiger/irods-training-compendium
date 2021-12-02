# RDM & compute training: ACES

## Target audience

To follow this training you need to be familiar with an HPC environment and the python programming language.

## Setup

Login to `login1.anunna.wur.nl` and clone the git repo:

```bash
git clone https://git.wur.nl/rdm-infrastructure/irods-training.git
cd irods-training/13-HPC-RDM-Training/iRODS-Compute-Tutorial-ACES
```

## Training

Please start with the jupyter notebook `ACES-RDM-on-HPC.ipynb`. You will get some valid iRODS credentials from your iRODS provider and can hence follow the code in the notebook.
Go to https://notebook.anunna.wur.nl and launch a local server. In that server navigate to `ACES-RDM-on-HPC.ipynb` and follow the tutorial.

Once you finished the tutorial in the notebook and you want to launch a remote job on the HPC cluster, open the job script `job-aces-anunna` and adjust your iRODS credentials and folder paths on the scratch file system.

You can start and monitor a job like this:

```
[login@login1] sbatch job-aces-anunna
Submitted batch job <id>

[login@login1] squeue -l -j <id>
Fri Jun 25 17:40:59 2021
             JOBID PARTITION     NAME     USER    STATE       TIME TIME_LIMI  NODES NODELIST(REASON)
          <id>      main     aces <USER>  RUNNING       4:03  20:00:00      1 node116

```

If you submitted several jobs, you canlist them all with:
```
squeue -u <username on anunna>
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          <id>      main     aces <USER>  R       0:20      1 node023

```



