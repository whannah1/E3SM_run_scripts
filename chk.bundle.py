#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
# Check the status of an E3SM bundle
#   ./chk.bundle.py              # use the newest bundle under {scratch_root}/bundles
#   ./chk.bundle.py <name>       # use the newest bundle matching *<name>*
#---------------------------------------------------------------------------------------------------
import os, sys, glob, subprocess as sp
import chk_methods
host = chk_methods.get_host()
tclr = chk_methods.tclr
#---------------------------------------------------------------------------------------------------
scratch_root = None
if host=='alcf' : scratch_root = '/lus/flare/projects/E3SM_Dec/whannah/scratch'
if host=='nersc': scratch_root = '/pscratch/sd/w/whannah/e3sm_scratch'
if host=='olcf' : scratch_root = '/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch'
if host=='lcrc' : scratch_root = '/lcrc/group/e3sm/whannah/e3sm_scratch'

if scratch_root is None: sys.exit(f'{tclr.RED}ERROR: scratch root not defined for host: {host}{tclr.END}')

bundle_root = f'{scratch_root}/bundles'
#---------------------------------------------------------------------------------------------------
# find bundle directory - use newest match if multiple are found
bundle_name = sys.argv[1] if len(sys.argv)>1 else ''

# the slurm job has the "bundle." prefix - so chop it off here for easy copy/paste
if bundle_name[:7]=='bundle.':
  bundle_name = bundle_name.replace('bundle.','')

bundle_dirs = [d for d in glob.glob(f'{bundle_root}/*{bundle_name}*') if os.path.isdir(d)]

if len(bundle_dirs)==0: sys.exit(f'{tclr.RED}ERROR: no bundle found matching: {bundle_root}/*{bundle_name}*{tclr.END}')

bundle_dir = max(bundle_dirs, key=os.path.getmtime)

if len(bundle_dirs)>1:
  print(f'\n{tclr.YLW}WARNING: multiple bundles found - using newest:{tclr.END}')
  for d in sorted(bundle_dirs, key=os.path.getmtime): print(f'  {d}', flush=True)
#---------------------------------------------------------------------------------------------------
bundle_job = f'{bundle_dir}/bundle.job'
if not os.path.isfile(bundle_job): sys.exit(f'{tclr.RED}ERROR: bundle job file not found: {bundle_job}{tclr.END}')

print(f'\n{tclr.BLD}bundle: {tclr.CYN}{bundle_dir}{tclr.END}\n', flush=True)

sp.run(['python3',bundle_job,'--status'])
#---------------------------------------------------------------------------------------------------
