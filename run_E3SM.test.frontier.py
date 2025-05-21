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

# src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC0'; generate = True # generate baselines
# src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC4'; compare  = True # compare to baselines
# src_dir = os.getenv('HOME')+'/E3SM/E3SM_BASE'                  # just run tests, no comparison
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC5'                  # just run tests, no comparison

# generate     = True   # generate baselines
# compare      = True   # compare to baselines
# debug_script = True   # do not submit test - for debugging this script

# compiler = 'gnu'

baseline_branch_name = 'master'

# tests = ['e3sm_mmf_integration']
# tests = ['e3sm_atm_developer']
# tests = ['ERP_Ln9.ne4pg2_ne4pg2.FC5AV1C-L.summit_gnu'
#         ,'ERP_Ln9.ne4pg2_ne4pg2.FC5AV1C-L.summit_ibm']

# tests = ['ERP_Ln9.ne4pg2_ne4pg2.F2010-MMF1.summit_gnu.eam-mmf_fixed_subcycle']
# tests = ['SMS_Ln9.ne4pg2_ne4pg2.F2010-MMF1.summit_gnugpu']

# PAM tests
# tests = ['e3sm_mmf_pam_dev',]
tests = [
        # "SMS_Ln5.ne4pg2_ne4pg2.F2010-MMF1.eam-mmf_crmout",
        "SMS_Ln3.ne4pg2_ne4pg2.F2010-MMF1.frontier_crayclanggpu",
        # "ERS_Ln9.ne4pg2_ne4pg2.F2010-MMF1",
        # "ERS_Ln9.ne4pg2_ne4pg2.F2010-MMF2",
        ]


# tests = ['e3sm_mmf']
# tests = ['e3sm_developer']

#==================================================================================================
#==================================================================================================
timestamp = '{:%Y-%m-%d_%H%M%S}'.format(datetime.datetime.utcnow())
case_dir = os.getenv('HOME')+'/E3SM/test_cases/'+timestamp
if generate : case_dir = case_dir+'_baseline'

print('\n'+case_dir+'')

for test in tests :
    if not os.path.exists(case_dir) : os.makedirs(case_dir)
    log_file = case_dir+'/'+timestamp+'.'+test+'.log'

    cmd = src_dir+'/cime/scripts/create_test '+test
    cmd = 'nohup '+cmd
    # cmd +=' --test-root '+case_dir
    cmd +=' --project '+project
    cmd +=' --output-root '+output_root+' '
    cmd +=' --wait -j2 '
    # cmd +=' --input-dir /gpfs/alpine/cli115/world-shared/e3sm/inputdata'
    cmd +=' --input-dir /lustre/orion/cli115/world-shared/e3sm/inputdata'
    # if 'compiler' in locals(): cmd +=f' --compiler {compiler} '
    # cmd +=' --queue regular '
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
print
#==================================================================================================
#==================================================================================================
