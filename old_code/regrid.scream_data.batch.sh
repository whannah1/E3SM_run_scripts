#!/bin/bash
#SBATCH --account=CLI115
#SBATCH --time=2:00:00
#SBATCH --nodes=1
###SBATCH --partition=batch
#SBATCH --partition=gpu
#SBATCH --job-name=regrid_scream
#SBATCH --output=slurm-%x-%j.out
#SBATCH --mail-user=hannah6@llnl.gov
#SBATCH --mail-type=END,FAIL
#SBATCH --mem=0

# To run this batch script, use the command below to set the output grid from the command line:
# NE=1024; VGRID=L128; sbatch --job-name=hiccup_ne$NE --output=logs_slurm/slurm-%x-%j.out --export=NE=$NE,VGRID=$VGRID

# sbatch ./regrid.scream_data.batch.sh

# Load the python environment
source activate hiccup_env

time python -u regrid.scream_data.py
