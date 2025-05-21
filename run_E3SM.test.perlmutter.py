#!/usr/bin/env python
import sys, os, datetime
generate, compare, verbose, debug_script = False, False, False, False
#===================================================================================================
#===================================================================================================
### Cori
# project = 'm3312' # m3312 / m3305
# output_root = '/global/cscratch1/sd/whannah/e3sm_scratch/cori-knl/tests'

### Perlmutter
project = 'e3sm' # m1517 / e3sm_g
output_root = '/pscratch/sd/w/whannah/e3sm_scratch/perlmutter/tests'
# output_root = '/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/tests'
#===================================================================================================
#===================================================================================================

# src_dir = os.getenv('HOME')+'/E3SM/E3SM_BASE'; generate = True # generate baselines
# src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC4'; compare  = True # compare to baselines
# src_dir = os.getenv('HOME')+'/E3SM/E3SM_BASE'                  # just run tests, no comparison
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC4'                  # just run tests, no comparison


verbose      = True      # print commands
# debug_script = True      # do not submit test - for debugging this script

master_branch_name = 'master'

# tests = ['e3sm_mmf_integration']
# tests = ['e3sm_developer']
# tests = ['e3sm_atm_developer']
# tests = ['mmf_tmp']
# tests = ['e3sm_mmf']

# tests = ['SMS_Ln5.conusx4v1_r05_oECv3.F2010.pm-cpu_intel']
tests = ['SMS_Ln3.ne4pg2_oQU480.F2010-MMF1.pm-gpu_gnugpu']

# tests = [
        # "SMS_Ln5.ne4_ne4.FSCM-ARM97-MMF1.pm-cpu_gnu",
        # "SMS_Ln5.ne4_ne4.FSCM-ARM97-MMF2.pm-cpu_gnu",
        # "SMS_Ln5.ne4_ne4.FSCM-RICO-MMF1.pm-cpu_gnu",
        # "SMS_Ln5.ne4_oQU480.FSCM-RICO-MMF1.pm-cpu_gnu",
        # "SMS_Ln5.ne4_ne4.FSCM-RICO-MMF2.pm-cpu_gnu",
        # "SMS_Ln5.ne4pg2_oQU480.F2010-MMF1.pm-cpu_gnu",
        # "SMS_Ln5.ne4pg2_oQU480.F2010-MMF2.pm-cpu_gnu",
        # "SMS_Ln5.ne4pg2_oQU480.F2010-MMF2.pm-gpu_gnu",
        # "SMS_Ln3.ne4pg2_ne4pg2.F2010-MMF2.pm-cpu_gnu",
        # "ERS_Ln9.ne4pg2_oQU480.F2010-MMF2.pm-cpu_gnu",
        # ]

# tests = [
#        #'SMS_D_Ln9.ne4pg2_ne4pg2.FRCE-MMF1.pm-cpu_gnu.eam-cosp_nhtfrq9',
#        # 'SMS_D_Ln3.ne4pg2_ne4pg2.F2010-MMF1.pm-cpu_gnu',
#        # 'ERP_Ln9.ne4pg2_oQU480.WCYCL20TRNS-MMF1.pm-cpu_gnu.eam-mmf_fixed_subcycle',
#        'ERP_Ln9.ne4pg2_oQU480.WCYCL20TRNS-MMF1.pm-cpu_gnu.allactive-mmf_fixed_subcycle',
#        ]

# tests =[
        # 'SMS_Ln3.ne4pg2_ne4pg2.F2010-CICE.perlmutter_gnu',
        # 'SMS_Ln3.ne4pg2_ne4pg2.F2010-CICE.perlmutter_gnu.eam-rrtmgpxx',
        # 'SMS_Ln3.ne4pg2_ne4pg2.F2010-CICE.perlmutter_gnugpu.eam-rrtmgpxx',
        # 'SMS_Ln3.ne4pg2_ne4pg2.F-MMFXX.perlmutter_gnugpu',
        # 'SMS_Ln3.ne4pg2_ne4pg2.F-MMFXX.perlmutter_gnugpu.eam-mmf_fixed_subcycle',
        # 'ERP_Ln9.ne4pg2_ne4pg2.F-MMFXX.perlmutter_gnugpu.eam-mmf_fixed_subcycle',
        # 'SMS_Ln3.ne4pg2_ne4pg2.F-MMFXX.perlmutter_gnu',
        # 'SMS_Ln3.ne4pg2_ne4pg2.F-MMFXX.perlmutter_gnu.eam-rrtmgp',
        # ]

# tests = ['SMS_Ln9_P96x1.ne4pg2_ne4pg2.F-MMFXX.cori-knl_intel.eam-mmf_use_ESMT',
         # 'SMS_Ln9.ne4pg2_ne4pg2.F-MMFXX.cori-knl_intel.eam-mmf_use_ESMT',]

# tests = ['SMS_Ln5_P1350x1.ne30pg2_r05_oECv3.F20TR-MMFXX-CMIP6.cori-knl_intel',]

# tests = [
        # 'SMS_Ln5.ne4_ne4.F-MMF1-SCM-ARM97.cori-knl_intel.eam-scm_output',
        # 'SMS_Ln5.ne4_ne4.F-MMFXX-SCM-ARM97',
        # 'SMS_R_Ln5.ne4_ne4.F-MMF1-SCM-RICO.cori-knl_intel',
        # 'SMS_Ln5.ne4_ne4.F-MMFXX-SCM-RICO.cori-knl_intel',
        # 'ERS_Ln9.ne4pg2_ne4pg2.FC5AV1C-L.cori-knl_intel',
        # 'ERS_Ln9.ne4pg2_ne4pg2.FC5AV1C-L.cori-knl_gnu',
        # 'ERS_D_Ln9.ne4pg2_ne4pg2.FC5AV1C-L.cori-knl_gnu',
        # 'SMS_Ln3.ne4pg2_ne4pg2.F-MMFXX.cori-knl_intel.eam-mmf_fixed_subcycle',
        # 'SMS_Ln3.ne4pg2_ne4pg2.F-MMF1.cori-knl_intel.eam-mmf_fixed_subcycle',
        # 'ERS_Ln9.ne4pg2_ne4pg2.F-MMFXX',
        # 'ERS_Ln9.ne4pg2_ne4pg2.F-MMF1',
        # 'SMS_Ln5_P96x1.ne4pg2_ne4pg2.F-MMF1',
        # 'SMS_Ln5_P96x1.ne4pg2_ne4pg2.F-MMFOMP',
        # 'SMS_Ln5_P96x1.ne4pg2_ne4pg2.F-MMF2-ECPP',
        # 'SMS_Ln3_P96x1.ne4pg2_ne4pg2.F-MMFXX.cori-knl_intel.eam-mmf3D',
        # 'SMS_Ln3_P96x2.ne4pg2_ne4pg2.F-MMFXX.cori-knl_intel.eam-mmf3D',
        # 'ERS_Ln3.ne4pg2_ne4pg2.F-MMFXX.cori-knl_intel.eam-mmf_use_ESMT',
        #'ERS_Ln3.ne4pg2_ne4pg2.F-MMFXX.cori-knl_intel.eam-mmf_use_ESMT',
        #'SMS_Ln3.ne4pg2_ne4pg2.F-MMFXX.cori-knl_intel.eam-mmf_use_VT',
        # 'SMS_Ln3_P96x2.ne4pg2_ne4pg2.F-MMFXX.cori-knl_intel.eam-mmf_use_VT',
        # 'ERS_Ln9_P96x2.ne4pg2_ne4pg2.F-MMFXX.cori-knl_intel.eam-mmf_use_VT',
        # 'SMS_Ld1.ne4_ne4.F-MMF1-SCM-ARM97.cori-knl_intel',
        # 'SMS_Ld1.ne4_ne4.F-MMF1-SCM-RICO.cori-knl_intel',
        #]


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
    # cmd = cmd+' --test-root '+case_dir             
    cmd = cmd+' --project   '+project              
    cmd = cmd+' --wait -j2 '                       
    # cmd = cmd+' --baseline-root '+output_root+'/baselines '  
    
    # if 'output_root' in locals():
    cmd = cmd+' --output-root   '+output_root+' '

    # if 'FSCM5A97' in test : cmd = cmd+' --queue debug '
    # cmd = cmd+' --queue debug '
    
    if generate : 
        cmd = cmd+' --generate '
        cmd = cmd+' --allow-baseline-overwrite '
        cmd = cmd+f' -b {master_branch_name} '
    if compare :
        cmd = cmd+' -c '
        cmd = cmd+f' -b {master_branch_name} '
        # cmd = cmd+' -b whannah/atm/aqua_planet_fix '

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
