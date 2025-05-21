#!/usr/bin/env python3
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
project = 'e3sm'

output_root = '/lcrc/group/e3sm/whannah/e3sm_scratch/tests'

# src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC0'; generate = True # generate baselines
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC2'; compare  = True # compare to baselines
# src_dir = os.getenv('HOME')+'/E3SM/E3SM_BASE'                  # just run tests, no comparison
# src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC1'                  # just run tests, no comparison

# baseline_branch_name = 'custom_baseline'
baseline_branch_name = 'master'

verbose      = True      # print commands
# debug_script = True      # do not submit test - for debugging this script

# tests = ['e3sm_mmf_integration']
# tests = ['e3sm_developer']
tests = ['e3sm_atm_developer']
# tests = ['e3sm_atm_integration']
# tests = ['mmf_tmp']
# tests = ['e3sm_orodrag_developer']

# tests = [ 'SMS_Ln5.ne4pg2_oQU480.F2010.chrysalis_intel' ]

# tests = [
#         'SMS_D_Ln5.ne4pg2_oQU480.F2010.chrysalis_intel.eam-orodrag_ne4pg2', # from oro drag test suite
#         # 'SMS_Ld1.ne4pg2_oQU480.F2010.chrysalis_intel',
#         # 'SMS_Ld1.ne4pg2_oQU480.F2010.chrysalis_intel.eam-orodrag_ne4pg2',
#         ]

# tests = [ 'SMS_Ln3.ne4pg2_oQU480.F2010-MMF2.chrysalis_intel' ]

# tests = [
#         'ERP_Ln9.ne4pg2_oQU480.WCYCL20TRNS-MMF1.chrysalis_intel.allactive-mmf_fixed_subcycle',
#         # 'ERS_Ln9_P96x1.ne4pg2_ne4pg2.F2010-MMF2.chrysalis_intel',       # PASS?
#         # 'ERS_Ln9_P96x1.ne4pg2_oQU480.F2010-MMF2.chrysalis_intel',       # 
#         # 'SMS_Ln9_P96x1.ne4pg2_oQU480.F2010-MMF2.chrysalis_intel',       # 
#         # 'SMS_D_Ln9_P96x1.ne4pg2_oQU480.F2010-MMF2.chrysalis_intel',     # PASS
#         # 'SMS_Ln5_P1x1.ne4_ne4.FSCM-ARM97-MMF2.chrysalis_intel',         # PASS
#         # 'SMS_D_Ln5_P1x1.ne4_ne4.FSCM-ARM97-MMF2.chrysalis_intel',
#         ]

# tests = ['ERS_Ln9.ne4pg2_ne4pg2.FRCE.chrysalis_intel.eam-cosp_nhtfrq9']
# tests = ['ERS_Ln9.ne4pg2_ne4pg2.F2010.chrysalis_intel.eam-cosp_nhtfrq9']

# tests = ['ERP_Ln9.ne4pg2_oQU480.WCYCL20TRNS-MMF1.chrysalis_intel.allactive-mmf_fixed_subcycle']
# tests = ['ERS_Ln9.ne4pg2_ne4pg2.F2010-MMF1.chrysalis_intel.eam-mmf_crmout']

### non-BFB tests
# tests = ['PGN_P96x1.ne4pg2_ne4pg2.F-MMF1.chrysalis_intel',
#          'TSC_P96x1.ne4pg2_ne4pg2.F-MMF1.chrysalis_intel',
#          'MVK_P96x1.ne4pg2_ne4pg2.F-MMF1.chrysalis_intel',]

#==================================================================================================
#==================================================================================================
if debug_script : verbose = True

now = datetime.datetime.utcnow()
timestamp = '{:%Y-%m-%d_%H%M%S}'.format(now)

print('\n'+timestamp+'')

case_dir = home+'/E3SM/test_cases/'+timestamp

if generate : case_dir = case_dir+'_baseline'

for test in tests :

    if not os.path.exists(case_dir) : os.makedirs(case_dir)
    log_file = case_dir+'/'+timestamp+'.'+test+'.log'

    
    cmd = 'nohup '+src_dir+'/cime/scripts/create_test   '+test
    cmd = cmd+' --test-root '+case_dir             
    cmd = cmd+' --project   '+project              
    cmd = cmd+' --wait -j2 '                       
    # cmd = cmd+' --baseline-root '+output_root+'/baselines '  
    cmd = cmd+' --output-root   '+output_root+' '
    cmd +=' --input-dir /lcrc/group/e3sm/data/inputdata'

    # if 'FSCM5A97' in test : cmd = cmd+' --queue debug '
    # cmd = cmd+' --queue debug '
    
    if generate : 
        cmd = cmd+' --generate '
        cmd = cmd+' --allow-baseline-overwrite '
        cmd = cmd+f' -b {baseline_branch_name} '
    if compare :
        cmd = cmd+' -c '
        cmd = cmd+f' -b {baseline_branch_name} '
        # cmd = cmd+f' -b whannah/atm/aqua_planet_fix '

    cmd = cmd+' --walltime 00:30:00 '
    cmd = cmd+'  >& '+log_file+' &'

    #--------------------------------------------
    # Machine-specific configurations
    #--------------------------------------------
    ### use regular queue for debug run since they need a longer wall clock limit
    # if debug_test :
    #     cmd = cmd+' --queue regular '
    # else :
    #     cmd = cmd+' --queue debug '

    #--------------------------------------------
    #--------------------------------------------

    ### print the command for starting the test
    if verbose : print('\n'+cmd+'')

    ## submit the test
    if not debug_script : os.system(cmd)

print
#==================================================================================================
#==================================================================================================
