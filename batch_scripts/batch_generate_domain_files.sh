#!/bin/bash
#SBATCH --account=m3312
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --job-name=generate_domain_ensemble
#SBATCH --output=generate_domain_ensemble-%x-%j.out
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#---------------------------------------------------------------------------

source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh

time python -u code_grid/2024_generate_aqua_sensitivity_grids.py # > /global/homes/w/whannah/E3SM/generate_domain_ensemble.out 