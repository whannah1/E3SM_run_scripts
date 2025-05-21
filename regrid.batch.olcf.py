#!/bin/bash
#SBATCH -A CLI115
#SBATCH -J regrid_batch
#SBATCH -N 1
#SBATCH -p batch
#SBATCH -t 8:00:00
###SBATCH -o $HOME/Research/E3SM/slurm_logs/regrid.batch.slurm-%A.out
#SBATCH -o slurm.log.regrid.batch.%A.out
#SBATCH --mail-user=hannah6@llnl.gov
#SBATCH --mail-type=END,FAIL

# command to submit:  sbatch regrid.batch.olcf.py

source activate pyn_env 

date


time python -u regrid.ne30pg2.py

date