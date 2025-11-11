#!/usr/bin/env python
import sys, os, datetime
generate, compare, verbose, debug_script = False, False, False, False
#===================================================================================================
#===================================================================================================
### Perlmutter
# project = 'e3sm_g' # m1517 / e3sm_g
project = 'm4842' # e3sm / m3312 / m3305/ m4842 (SOHIP)
output_root = '/pscratch/sd/w/whannah/e3sm_scratch/perlmutter/tests'
#===================================================================================================
#===================================================================================================

# src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC0'; generate = True # generate baselines
# src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC4'; compare  = True # compare to baselines
# src_dir = os.getenv('HOME')+'/E3SM/E3SM_BASE'                  # just run tests, no comparison
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC4'                  # just run tests, no comparison
# src_dir = '/pscratch/sd/w/whannah/tmp_e3sm_src'


verbose      = True      # print commands
# debug_script = True      # do not submit test - for debugging this script

master_branch_name = 'master'

# tests = ['e3sm_mmf_integration']
# tests = ['e3sm_developer']
# tests = ['e3sm_atm_developer']
# tests = ['mmf_tmp']
# tests = ['e3sm_mmf']

tests = [ 
        # 'ERP_Ld3.ne4pg2_oQU480.F2010.pm-cpu_gnu',
        'ERP_Ld3.ne4pg2_oQU480.F2010.pm-cpu_intel',
        'SMS.ne4pg2_oQU480.F2010.pm-cpu_intel.eam-preqx_ftype0',
        # 'SMS.ne4pg2_oQU480.F2010.pm-cpu_intel.eam-preqx_ftype1',
        # 'SMS.ne4pg2_oQU480.F2010.pm-cpu_intel.eam-preqx_ftype4',
        'SMS_R_Ld5.ne4_ne4.FSCM-ARM97.pm-cpu_intel.eam-scm',
        ]


# tests = [ 
        # 'ERS_Ln9.ne30pg2_r05_IcoswISC30E3r5.F2010.pm-cpu_intel', 
        # 'ERS_Ln9.ne30pg2_r05_IcoswISC30E3r5.F2010.pm-cpu_gnu', 
        # 'ERS_Ln9_Ln12.ne30pg2_r05_IcoswISC30E3r5.F2010.pm-cpu_intel', 
        # 'ERS_Ln9_Ln12.ne30pg2_r05_IcoswISC30E3r5.F2010.pm-cpu_gnu', 
        # 'ERS_Ln9_P512x1.ne30pg2_r05_IcoswISC30E3r5.F2010.pm-cpu_intel', 
        # 'ERS_D_Ld5_P512x1.ne30pg2_r05_IcoswISC30E3r5.F2010.pm-cpu_gnu',
        # 'ERS_D_Ld5_P1024x1.ne30pg2_r05_IcoswISC30E3r5.F2010.pm-cpu_gnu',
        # 'SMS_R_Ld5.ne4_ne4.FSCM-ARM97.pm-cpu_gnu.eam-scm',
        # 'SMS_Ln9.ne4pg2_ne4pg2.F2010-MMF1.pm-gpu_gnugpu'
        # ]

# tests = [ 'SMS_Ln3.ne4pg2_oQU480.F2010-MMF2.pm-cpu_intel' ]
#         'SMS_Ln3.ne4pg2_ne4pg2.F2010-MMF2.pm-cpu_gnu',       # 
#         # 'ERS_Ln9_P96x1.ne4pg2_oQU480.F2010-MMF2.pm-cpu_gnu',       # 
#         # 'SMS_Ln9_P96x1.ne4pg2_oQU480.F2010-MMF2.pm-cpu_gnu',       # 
#         # 'SMS_D_Ln9_P96x1.ne4pg2_oQU480.F2010-MMF2.pm-cpu_gnu',     # 
#         # 'SMS_Ln5_P1x1.ne4_ne4.FSCM-ARM97-MMF2.pm-cpu_gnu',         # 
#         # 'SMS_D_Ln5_P1x1.ne4_ne4.FSCM-ARM97-MMF2.pm-cpu_gnu',
#         ]

# tests = ['ERS_Ln9.ne4pg2_ne4pg2.FAQP']
# tests = ['ERP_Ln9.ne4pg2_oQU240.WCYCL20TR-MMF1.eam-mmf_fixed_subcycle']
# tests = ['ERP_Ln9.ne4pg2_oQU240.WCYCL1950-MMF1.eam-mmf_fixed_subcycle']

# tests = ['SMS_Ln5.ne4_ne4.FSCM-ARM97-MMF1'
#         ,'SMS_D_Ln5.ne4_ne4.FSCM-ARM97-MMF1']

# tests = [
#         'SMS_Ld1_P64x1.ne4pg2_ne4pg2.F2010-CICE.cori-knl_intel.eam-rrtmgp',
#         'SMS_Ld1_P64x1.ne4pg2_ne4pg2.F2010-CICE.cori-knl_intel.eam-rrtmgpxx',
#         ]


### non-BFB tests
# tests = ['PGN_P96x1.ne4pg2_ne4pg2.F-MMF1.cori-knl_intel',
#          'TSC_P96x1.ne4pg2_ne4pg2.F-MMF1.cori-knl_intel',
#          'MVK_P96x1.ne4pg2_ne4pg2.F-MMF1.cori-knl_intel',]

#==================================================================================================
#==================================================================================================
if debug_script : verbose = True

now = datetime.datetime.utcnow()
timestamp = '{:%Y-%m-%d_%H%M%S}'.format(now)

print('\n'+timestamp+'')

case_dir = os.getenv('HOME')+'/E3SM/test_cases/'+timestamp

if generate : case_dir = case_dir+'_baseline'

for test in tests :

    if not os.path.exists(case_dir) : os.makedirs(case_dir)
    log_file = case_dir+'/'+timestamp+'.'+test+'.log'
    
    cmd = 'nohup '+src_dir+'/cime/scripts/create_test   '+test
    cmd = cmd+' --test-root '+case_dir             
    cmd = cmd+' --project   '+project              
    cmd = cmd+' --wait -j2 '                       
    # cmd = cmd+' --baseline-root '+output_root+'/baselines '
    
    if 'output_root' in globals(): cmd = cmd+' --output-root   '+output_root+' '

    if generate : 
        cmd = cmd+' --generate '
        cmd = cmd+' --allow-baseline-overwrite '
        cmd = cmd+f' -b {master_branch_name} '
    if compare :
        cmd = cmd+' -c '
        cmd = cmd+f' -b {master_branch_name} '

    cmd = cmd+' --queue debug '
    cmd = cmd+' --walltime 00:30:00 '

    # cmd = cmd+' --queue regular '
    # cmd = cmd+' --walltime 01:00:00 '

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
