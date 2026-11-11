#!/usr/bin/env python3
#============================================================================================================================
#   Jan, 2017   Walter Hannah    Lawrence Livermore National Lab
#   Automated E3SM testing script specific to OLCF systems
#==================================================================================================
import sys,os,datetime
generate, compare, debug_script = False, False, False

home = os.getenv('HOME')
project = 'cli115'
output_root = f'/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch/frontier/tests'
output_root = f'/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch/tests'

# src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC0'; generate = True # generate baselines
# src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC4'; compare  = True # compare to baselines
# src_dir = os.getenv('HOME')+'/E3SM/E3SM_BASE'                  # just run tests, no comparison
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC1'                  # just run tests, no comparison

# generate     = True   # generate baselines
# compare      = True   # compare to baselines
# debug_script = True   # do not submit test - for debugging this script

# compiler = 'gnu'

baseline_branch_name = 'master'

# tests = ['e3sm_mmf_integration']
# tests = ['e3sm_atm_developer']

tests = [
        # 'SMS_Ld5_Vmct.T62_oQU240.GMPAS-IAF.frontier_craygnu-mphipcc',
        # 'SMS_Ld5_Vmoab.T62_oQU240.GMPAS-IAF.frontier_craygnu-mphipcc',
        # 'SMS_Ld5.T62_oQU240.GMPAS-IAF.frontier_craygnu-mphipcc',
        'SMS_Ln5_Vmct.ne4pg2_ne4pg2.F2010-SCREAMv1.frontier_craygnu-mphipcc',
        'SMS_Ln5_Vmoab.ne4pg2_ne4pg2.F2010-SCREAMv1.frontier_craygnu-mphipcc',
        ]

#==================================================================================================
verbose      = True      # print commands
# debug_script = True      # do not submit test - for debugging this script
#==================================================================================================
if debug_script : verbose = True

now = datetime.datetime.utcnow()
timestamp = '{:%Y-%m-%d_%H%M%S}'.format(now)

print(f'\n{timestamp}')

# case_dir = os.getenv('HOME')+'/E3SM/test_cases/'+timestamp
case_dir = f'{output_root}/{timestamp}'

if generate : case_dir = case_dir+'_baseline'

for test in tests :

    if not os.path.exists(case_dir) : os.makedirs(case_dir)
    log_file = f'{case_dir}/{timestamp}.{test}.log'
    
    cmd = f'nohup {src_dir}/cime/scripts/create_test {test}'
    cmd += f' --test-root {case_dir}'
    cmd += f' --output-root {case_dir} '
    cmd += f' --project {project}'
    cmd += f' --wait -j2 '                       
    # cmd = cmd+' --baseline-root '+output_root+'/baselines '

    if generate : 
        cmd += f' --generate '
        cmd += f' --allow-baseline-overwrite '
        cmd += f' -b {master_branch_name} '
    if compare :
        cmd += ' -c '
        cmd += f' -b {master_branch_name} '

    # cmd += f' --queue debug --walltime 00:30:00 '
    cmd += f' --queue regular --walltime 01:00:00 '

    cmd += f'  >& {log_file} &'

    #--------------------------------------------
    # Machine-specific configurations
    #--------------------------------------------
    # # use regular queue for debug run since they need a longer wall clock limit
    # if debug_test :
    #     cmd = cmd+' --queue regular '
    # else :
    #     cmd = cmd+' --queue debug '
    #--------------------------------------------
    #--------------------------------------------

    # print the command for starting the test
    if verbose : print('\n'+cmd+'')

    # submit the test
    if not debug_script : os.system(cmd)

print()
#==================================================================================================
#==================================================================================================
