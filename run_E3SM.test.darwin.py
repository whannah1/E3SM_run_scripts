#!/usr/bin/env python
#============================================================================================================================
#   Jan, 2017   Walter Hannah    Lawrence Livermore National Lab
#   Automated ECP testing procesdure
#==================================================================================================
import sys
import os
import datetime
home = os.getenv('HOME')
generate, compare, verbose, debug_script = False, False, False, False
#==================================================================================================
#==================================================================================================
project = 'm3312'

# src_dir = home+'/E3SM/E3SM_BASE'
src_dir = home+'/E3SM/E3SM_SRC1'

master_branch_name = 'master'
# master_branch_name = 'next'
 
# generate     = True      # generate baselines
# compare      = True      # compare to baselines
verbose      = True      # print commands
# debug_script = True      # do not submit test - for debugging this script

tests = []

### test suites
# tests.append('e3sm_atm_developer')
# tests.append('e3sm_developer')
# tests.append('e3sm_atm_integration')
# tests.append('e3sm_mmf')

### non-MMF tests
# tests.append('SMS_Ln3_P1x1.ne4pg2_ne4pg2.FC5AV1C-L')
# tests.append('SMS_Ln9.ne4_ne4.F-EAMv1-RCEMIP')
# tests.append('ERP_Ln9.ne4_ne4.F-EAMv1-AQP1')

### MMF tests
tests.append('SMS_Ln3.ne4pg2_ne4pg2.F-MMF1-AQP1')
# tests.append('ERS_Ln9_P96.ne4pg2_ne4pg2.F-MMF1')
# tests.append('ERS_Ln9_P96x1.ne4pg2_ne4pg2.F-MMF1.cori-knl_intel.cam-crmout')
# tests.append('ERS_Ln9_P96.ne4pg2_ne4pg2.F-MMF2-ECPP.cori-knl_intel')

### non-BFB tests
# tests.append('PGN_P96x1.ne4pg2_ne4pg2.F-MMF1.cori-knl_intel')
# tests.append('TSC_P96x1.ne4pg2_ne4pg2.F-MMF1.cori-knl_intel')
# tests.append('MVK_P96x1.ne4pg2_ne4pg2.F-MMF1.cori-knl_intel')

#==================================================================================================
#==================================================================================================
if debug_script : verbose = True

now = datetime.datetime.utcnow()
timestamp = '{:%Y-%m-%d_%H%M%S}'.format(now)

print('\n'+timestamp+'')

case_dir = home+'/E3SM/test_cases/'+timestamp

if generate : case_dir = case_dir+'_baseline'

for test in tests :

    test_output_root = f'{home}/E3SM/scratch/tests'
    base_output_root = f'{home}/E3SM/scratch/baselines'

    if not os.path.exists(case_dir) : os.makedirs(case_dir)
    log_file = case_dir+'/'+timestamp+'.'+test+'.log'

    cmd = f'nohup {src_dir}/cime/scripts/create_test {test} --wait -j2'
    cmd += f' --machine mac-mini'
    cmd += f' --test-root {case_dir}'
    cmd += f' --project   {project}'   
    cmd += f' --baseline-root {base_output_root}'
    cmd += f' --output-root   {test_output_root}'
    
    if generate: cmd += f' -b {master_branch_name} --generate --allow-baseline-overwrite '
    if compare : cmd += f' -b {master_branch_name} -c '

    # cmd += ' --walltime 00:30:00 '
    cmd += '  >& '+log_file+' &'
    #--------------------------------------------
    #--------------------------------------------

    ### print the command for starting the test
    if verbose : print('\n'+cmd+'')

    ## submit the test
    if not debug_script : os.system(cmd)

print
#==================================================================================================
#==================================================================================================
