#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
#---------------------------------------------------------------------------------------------------
import sys, os, datetime
home = os.getenv('HOME')
generate, compare, verbose, debug_script = False, False, False, False
#---------------------------------------------------------------------------------------------------
project = 'e3sm'

test_root = '/pscratch/sd/w/whannah/e3sm_scratch/ZM_testing'

# src_dir = f'{home}/E3SM/E3SM_SRC2'; generate = True # generate baselines
src_dir = f'{home}/E3SM/E3SM_SRC3'; compare  = True # compare to baselines

baseline_root = f'{test_root}/baselines'

baseline_branch = 'zm_bridge_02'
#---------------------------------------------------------------------------------------------------
verbose      = True      # print commands
# debug_script = True      # do not submit test - used for debugging this script
#---------------------------------------------------------------------------------------------------

# tests = [  # use these for BFB debugging 
# 'SMS_Ln5.ne4pg2_oQU480.F2010.pm-cpu_intel',
# 'SMS_Ln5.ne4pg2_oQU480.F2010.pm-cpu_gnu',
# 'SMS_D_Ln5.ne4pg2_oQU480.F2010.pm-cpu_intel',
# 'SMS_D_Ln5.ne4pg2_oQU480.F2010.pm-cpu_gnu',
# 'ERP_Ld3.ne4pg2_oQU480.F2010.pm-cpu_gnu',
# 'SMS_D_Ln5.ne4pg2_oQU480.F2010xx.pm-cpu_gnu',
# ]

tests = [
# 'SMS_Ln5.ne4pg2_oQU480.F2010.pm-cpu_intel',   # use these for BFB debugging 
# 'SMS_Ln5.ne4pg2_oQU480.F2010.pm-cpu_gnu',     # use these for BFB debugging 
# 'SMS_D_Ln5.ne4pg2_oQU480.F2010.pm-cpu_intel', # use these for BFB debugging 
# 'SMS_D_Ln5.ne4pg2_oQU480.F2010.pm-cpu_gnu',   # use these for BFB debugging 
'e3sm_atm_developer_intel',
'e3sm_atm_developer_gnu',
# 'SMS_Ld32.ne30pg2_r05_oECv3.F2010.pm-cpu_intel',
# 'SMS_Ld32.ne30pg2_r05_oECv3.F2010.pm-cpu_gnu',
'SMS_Ld32.ne4pg2_oQU480.F2010.pm-cpu_intel',
'SMS_Ld32.ne4pg2_oQU480.F2010.pm-cpu_gnu',
]

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if debug_script : verbose = True

now = datetime.datetime.utcnow()

timestamp = '{:%Y%m%d_%H%M%S}'.format(now)

# case_dir = f'{test_root}'
# case_dir = f'{test_root}/{timestamp}'

if     generate: case_dir = f'{test_root}/{timestamp}_base'
if not generate: case_dir = f'{test_root}/{timestamp}_test'

print()
print('-'*100)
print(f'test_root : {clr.CYAN}{test_root}{clr.END}')
print(f'base_root : {clr.CYAN}{baseline_root}{clr.END}')
print(f'case_dir  : {clr.CYAN}{case_dir}{clr.END}')
print('-'*100)
print()

for test in tests :
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
    cmd +=f' --parallel-jobs 1'
    cmd +=f' --wait'
    cmd +=f' --project  {project}'
    if compiler is not None : cmd +=f' --compiler {compiler}'
    #---------------------------------------------------------------------------
    if generate: cmd +=f' --generate --baseline-name {baseline_branch} -o '
    if compare : cmd +=f' --compare  --baseline-name {baseline_branch} '
    if generate or compare: cmd +=f' --baseline-root {baseline_root}'
    #---------------------------------------------------------------------------
    if 'ne30' in test:
        cmd +=f' --walltime 01:00:00'
        cmd +=f' --queue regular'
    else:
        cmd +=f' --queue debug'
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
