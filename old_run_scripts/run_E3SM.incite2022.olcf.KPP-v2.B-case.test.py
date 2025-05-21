#!/usr/bin/env python3
#============================================================================================================================
#   Jan, 2017   Walter Hannah    Lawrence Livermore National Lab
#   Automated E3SM testing script specific to OLCF systems
#==================================================================================================
import sys,os,datetime
generate, compare, debug_script = False, False, False

home = os.getenv('HOME')
project = 'cli115'
# output_root = f'/gpfs/alpine/scratch/hannah6/{project}/e3sm_scratch/tests'
output_root = f'/gpfs/alpine/{project}/proj-shared/hannah6/e3sm_scratch/tests'

# src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC0'; generate = True # generate baselines
# src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC4'; compare  = True # compare to baselines
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC1'                  # just run tests, no comparison

# generate     = True   # generate baselines
# compare      = True   # compare to baselines
# debug_script = True   # do not submit test - for debugging this script

baseline_branch_name = 'master'

# tests = ['PFS_P512x7.ne120pg2_r0125_oRRS18to6v3.WCYCL1950.summit_gnu.bench-wcycl-hires']
tests = ['PFS_D_P512x7.ne120pg2_r0125_oRRS18to6v3.WCYCL1950.summit_gnu.bench-wcycl-hires']

#==================================================================================================
#==================================================================================================
timestamp = '{:%Y-%m-%d_%H%M%S}'.format(datetime.datetime.utcnow())
case_dir = os.getenv('HOME')+'/E3SM/test_cases/'+timestamp
if generate : case_dir = case_dir+'_baseline'

print('\n'+case_dir+'')

for test in tests :
    if not os.path.exists(case_dir) : os.makedirs(case_dir)
    log_file = case_dir+'/'+timestamp+'.'+test+'.log'

    cmd = f'nohup {src_dir}/cime/scripts/create_test {test}'
    cmd +=f' --test-root {case_dir}'
    cmd +=f' --project {project}'
    cmd +=f' --output-root {output_root} '
    cmd +=' --wait -j2 '
    # cmd +=' --input-dir /gpfs/alpine/cli115/world-shared/e3sm/inputdata'
    # if 'compiler' in locals(): cmd +=f' --compiler {compiler} '
    cmd +=' --queue debug '
    # cmd +=' --no-build --no-setup '
    
    if generate or compare:
        cmd +=' --baseline-root '+output_root+'/baselines '  
    if generate : 
        cmd +=f' --generate -b {baseline_branch_name} '
        cmd +=' --allow-baseline-overwrite '
    if compare :
        cmd += f'-c -b {baseline_branch_name} '

    cmd += ' --walltime 00:20 '
    cmd += '  >& '+log_file+' &'
    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    # print the command for the test
    print('\n'+cmd+'\n')

    # submit the test
    if not debug_script : os.system(cmd)

print()
#==================================================================================================
#==================================================================================================
