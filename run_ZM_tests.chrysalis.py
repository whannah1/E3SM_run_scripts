#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
#---------------------------------------------------------------------------------------------------
import sys, os, datetime
home = os.getenv('HOME')
generate, compare, verbose, debug_script = False, False, False, False
#---------------------------------------------------------------------------------------------------
project = 'e3sm'

test_root = '/lcrc/group/e3sm/ac.whannah/ZM_testing'
# test_root = '/lcrc/group/e3sm/ac.whannah/scratch/chrys'
# test_root = '/lcrc/group/e3sm/ac.whannah/scratch/chrys/tests'

# src_dir = f'{home}/E3SM/E3SM_SRC1'; compare  = True # compare to baselines
# baseline_branch = 'master'; baseline_root = None

# src_dir = f'{home}/E3SM/E3SM_SRC0'; generate = True # generate baselines
# src_dir = f'{home}/E3SM/E3SM_SRC1'; compare  = True # compare to baselines
#baseline_branch = 'zm_cleanup_09' ; baseline_root = f'{test_root}/baselines'

# src_dir = f'{home}/E3SM/E3SM_SRC1'; generate = True # generate baselines
# src_dir = f'{home}/E3SM/E3SM_SRC2'; compare  = True # compare to baselines
# baseline_branch = 'zm_bridge_00' ; baseline_root = f'{test_root}/baselines'

# src_dir = f'{home}/E3SM/E3SM_SRC2'; generate = True # generate baselines
src_dir = f'{home}/E3SM/E3SM_SRC3'; compare  = True # compare to baselines
baseline_branch = 'zm_bridge_02' ; baseline_root = f'{test_root}/baselines'
#---------------------------------------------------------------------------------------------------
verbose      = True      # print commands
# debug_script = True      # do not submit test - used for debugging this script
#---------------------------------------------------------------------------------------------------

tests = [ # standard test suite for ZM dev
        'e3sm_atm_developer_intel',
        'e3sm_atm_developer_gnu',
        'SMS_Ld32.ne30pg2_r05_oECv3.F2010.chrysalis_intel',
        'SMS_Ld32.ne30pg2_r05_oECv3.F2010.chrysalis_gnu',
        'SMS_Ld32.ne4pg2_oQU480.F2010.chrysalis_intel',
        'SMS_Ld32.ne4pg2_oQU480.F2010.chrysalis_gnu',
        'SMS_Lh4.ne4pg2_ne4pg2.F2010-SCREAMv1.chrysalis_gnu.eamxx-output-preset-1--eamxx-prod',
        ]


# tests = [ # use these for BFB debugging
#        # 'SMS_Ln5.ne4pg2_oQU480.F2010.chrysalis_intel',
#        # 'SMS_Ln5.ne4pg2_oQU480.F2010.chrysalis_gnu',
#        # 'SMS_D_Ln5.ne4pg2_oQU480.F2010.chrysalis_intel',
#        'SMS_D_Ln5.ne4pg2_oQU480.F2010.chrysalis_gnu',
#        ]

# simple EAMxx tests
# tests = ['SMS_Lh4.ne4pg2_ne4pg2.F2010-SCREAMv1.chrysalis_gnu.eamxx-output-preset-1--eamxx-prod']

# src_dir = f'{home}/E3SM/E3SM_SRC0'; baseline_branch='master'; baseline_root=None
# tests = [ # test dcpae diags problem found on gcp
#         # 'ERP_Ld3.ne4pg2_oQU480.F2010.chrysalis_gnu.eam-condidiag_dcape',
#         'SMS_D_Ln5.ne4pg2_oQU480.F2010.chrysalis_gnu.eam-condidiag_dcape',
#         ]


# tests = [ # non-BFB tests - make sure to run: source  /lcrc/soft/climate/e3sm-unified/load_latest_cime_env.sh
#         'MVK_PS.ne4pg2_oQU480.F2010.chrysalis_intel',
#         'PGN_P1x1.ne4pg2_oQU480.F2010.chrysalis_intel',
#         'TSC_PS.ne4pg2_oQU480.F2010.chrysalis_intel',
#         ]


#---------------------------------------------------------------------------------------------------
'''PR message template:

The following tests pass on Chrysalis:
```
  e3sm_atm_developer_intel
  e3sm_atm_developer_gnu
  SMS_Ld32.ne30pg2_r05_oECv3.F2010.chrysalis_intel
  SMS_Ld32.ne30pg2_r05_oECv3.F2010.chrysalis_gnu
  SMS_Ld32.ne4pg2_oQU480.F2010.chrysalis_intel
  SMS_Ld32.ne4pg2_oQU480.F2010.chrysalis_gnu
```

The performance of the SMS_Ld32 tests are effectively identical, here's on of the ZM timers from `SMS_Ld32.ne30pg2_r05_oECv3.F2010.chrysalis_intel`:
```
              name                                            on  processes  threads        count      walltotal   wallmax (proc   thrd  )   wallmin (proc   thrd  )
    base: "a:zm_conv_tend"                                 -        128      256 2.360832e+06   1.579500e+04    72.009 (     1      0)    51.040 (    27      0)
    test: "a:zm_conv_tend"                                 -        128      256 2.360832e+06   1.579500e+04    72.009 (     1      0)    51.040 (    27      0)
```

'''
#---------------------------------------------------------------------------------------------------
'''
ls /lcrc/group/e3sm/ac.whannah/scratch/ZM_testing
ls /lcrc/group/e3sm/ac.whannah/scratch/chrys/ZM_testing
ls /lcrc/group/e3sm/ac.whannah/scratch/chrys
ls /lcrc/group/e3sm/ac.whannah/scratch/chrys/tests
'''
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if debug_script : verbose = True

now = datetime.datetime.utcnow()
# timestamp = '{:%Y-%m-%d_%H%M%S}'.format(now)
timestamp = '{:%Y%m%d_%H%M%S}'.format(now)
# timestamp = '{:%Y-%m-%d}'.format(now)
# timestamp = '{:%Y%m%d%H%M%S}'.format(now)

# case_dir = f'{test_root}'
# case_dir = f'{test_root}/{timestamp}'

if     generate: case_dir = f'{test_root}/{timestamp}_base'
if not generate: case_dir = f'{test_root}/{timestamp}_test'

print()
print('-'*100)
print(f'test_root : {clr.CYAN}{test_root}{clr.END}')
print(f'case_dir  : {clr.CYAN}{case_dir}{clr.END}')
print(f'base_root : {clr.CYAN}{baseline_root}{clr.END}')
print('-'*100)
print()

for test in tests :
    #---------------------------------------------------------------------------
    # check for invalid options
    if generate and baseline_root is None: exit(f"\n{clr.RED}WTF do you think you're doing?!?!{clr.END}\n")
    #---------------------------------------------------------------------------
    compiler = None
    if test=='e3sm_atm_developer_intel'  : test,compiler='e3sm_atm_developer',  'intel'
    if test=='e3sm_atm_developer_gnu'    : test,compiler='e3sm_atm_developer',  'gnu'
    if test=='e3sm_atm_integration_intel': test,compiler='e3sm_atm_integration','intel'
    if test=='e3sm_atm_integration_gnu'  : test,compiler='e3sm_atm_integration','gnu'
    if compiler is     None: log_file = f'{case_dir}/{timestamp}.{test}.log'
    if compiler is not None: log_file = f'{case_dir}/{timestamp}.{test}.{compiler}.log'
    #---------------------------------------------------------------------------
    cmd = f'{src_dir}/cime/scripts/create_test   {test}'
    cmd = f'nohup {cmd}'
    cmd +=f' --ignore-memleak'
    cmd +=f' --output-root {case_dir}'
    cmd +=f' --parallel-jobs 2'
    cmd +=f' --wait'
    # cmd +=f' --project  {project}'
    # cmd +=f' --input-dir /lcrc/group/e3sm/data/inputdata'
    # if baseline_root is not None : cmd +=f' --baseline-root {baseline_root}'
    if compiler is not None: cmd +=f' --compiler {compiler}'
    #---------------------------------------------------------------------------
    if generate: cmd +=f' --generate --baseline-name {baseline_branch} --allow-baseline-overwrite '
    if compare : cmd +=f' --compare  --baseline-name {baseline_branch} '
    if baseline_root is not None: cmd +=f' --baseline-root {baseline_root}'
    # if compare  and baseline_root is not None: cmd +=f' --baseline-root {baseline_root}'
    
    #---------------------------------------------------------------------------
    if 'ne30' in test:
        cmd +=f' --walltime 01:00:00'
        cmd +=f' --queue regular'
    #---------------------------------------------------------------------------
    cmd +=f'  >& {log_file} &'
    #---------------------------------------------------------------------------
    # print(f'\n{clr.GREEN}{cmd}{clr.END}\n')
    # print('STOPPING - no test submitted\n')
    # exit()
    #---------------------------------------------------------------------------
    # create directory using timestamp
    if not os.path.exists(case_dir): os.makedirs(case_dir)
    #---------------------------------------------------------------------------
    # submit the test
    print(f'\n{clr.GREEN}{cmd}{clr.END}\n')
    if not debug_script : os.system(cmd)
    #---------------------------------------------------------------------------
print()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
