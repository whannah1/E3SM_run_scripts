#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
import sys, os, fileinput, re, subprocess as sp, glob
from optparse import OptionParser
import importlib
#---------------------------------------------------------------------------------------------------
natsort_spec = None
natsort_found = natsort_spec is not None
if natsort_found: from natsort import natsorted, ns
#---------------------------------------------------------------------------------------------------
class clr:
   END      = '\033[0m'
   BLACK    = '\033[30m'
   RED      = '\033[31m'
   GREEN    = '\033[32m'
   YELLOW   = '\033[33m'
   BLUE     = '\033[34m'
   MAGENTA  = '\033[35m'
   CYAN     = '\033[36m'
   WHITE    = '\033[37m'
#---------------------------------------------------------------------------------------------------
def print_line(line_length=80,char='-'):
   dline = ''
   for c in range(line_length): dline+= char
   print(dline)
#---------------------------------------------------------------------------------------------------
def run_cmd(cmd,verbose=False,suppress_output=False,execute=True):
   if suppress_output : cmd = cmd + ' > /dev/null'
   if verbose: print(f'\n{clr.GREEN}{cmd}{clr.END}')
   if execute:
      (msg,err) = sp.Popen(cmd, stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
      return msg
   else:
      return
#---------------------------------------------------------------------------------------------------
# command line options

parser = OptionParser()
parser.add_option('-n',dest='num_file',default=-1,help='number of files to print')
parser.add_option("--all",action="store_true", dest="show_all", default=False,help="ahow all component timers")
parser.add_option("--partial",action="store_true", dest="allow_partial_match", default=False,help="allow partial matches of input search strings")

# parser.add_option('-n',dest='num_test',default=1,help='sets number of tests to search for. Only considers tests newer than newest baseline.')
parser.add_option('-b',action='store_true', dest='show_base', default=False,help='show recent baseline status instead of test')
# parser.add_option('-t',action='store_true', dest='truncate_flag', default=False,help='truncate output for small screens')
# parser.add_option('-m',dest='method',default=0,help='Method of checking tests - 0=parse logs, 1=use cs.status script')
# parser.add_option('--no-color',action='store_false', dest='use_color', default=True,help='disable colored output')

(opts, args) = parser.parse_args()
#---------------------------------------------------------------------------------------------------

test_root = '/pscratch/sd/w/whannah/e3sm_scratch/ZM_testing'
# test_root = '/lcrc/group/e3sm/ac.whannah/ZM_testing'

test_list = [ 
            # 'SMS_Ld32.ne30pg2_r05_oECv3.F2010.chrysalis_intel',
            # 'SMS_Ld32.ne30pg2_r05_oECv3.F2010.chrysalis_gnu',
            'SMS_Ld32.ne4pg2_oQU480.F2010.pm-cpu_intel',
            'SMS_Ld32.ne4pg2_oQU480.F2010.pm-cpu_gnu',
            ]

#---------------------------------------------------------------------------------------------------
# Define timing file parameters to be parsed

param_list = []
# param_list.append('Throughput')
# param_list.append('Cost')
# param_list.append('run length  :')
# param_list.append('Run Time    :')

# param_list.append('Throughput')
# param_list.append('TOT Run Time:')
# param_list.append('CPL Run Time:')
param_list.append('ATM Run Time')
# param_list.append('LND Run Time:')
# param_list.append('OCN Run Time:')
# param_list.append('ICE Run Time:')
# param_list.append('CPL:ATM_RUN')

param_list.append('a:zm_conv_tend')
# param_list.append('a:zm_convr')
# param_list.append('a:zm_conv_evap')
# param_list.append('a:radiation')

#-------------------------------------------------------------------------------
def is_stat_param(param):
   if 'a:'   in param: return True
   if 'a_i:' in param: return True
   if 'CPL:' in param: return True
   return False
#---------------------------------------------------------------------------------------------------
# Loop through each test
for t,test in enumerate(test_list):
   # print()
   #----------------------------------------------------------------------------
   # Find the most recent test and baseline pairs
   base = run_cmd(f'ls -1dt {test_root}/*_base/{test}* ').rstrip().split('\n')[0]
   test = run_cmd(f'ls -1dt {test_root}/*_test/{test}* ').rstrip().split('\n')[0]

   #----------------------------------------------------------------------------
   print('-'*140)
   # print()
   print(f'  base: {clr.GREEN}{base}{clr.END}')
   print(f'  test: {clr.GREEN}{test}{clr.END}')
   print()
   #----------------------------------------------------------------------------
   # grab timing files
   base_prof_file = run_cmd(f'ls -1t {base}/timing/e3sm_timing* '      ).rstrip().split('\n')[0]
   test_prof_file = run_cmd(f'ls -1t {test}/timing/e3sm_timing* '      ).rstrip().split('\n')[0]
   base_stat_file = run_cmd(f'ls -1t {base}/timing/e3sm_timing_stats* ').rstrip().split('\n')[0]
   test_stat_file = run_cmd(f'ls -1t {test}/timing/e3sm_timing_stats* ').rstrip().split('\n')[0]
   #----------------------------------------------------------------------------
   # print(f'  base_prof_file: {clr.CYAN}{base_prof_file}{clr.END}')
   # print(f'  base_stat_file: {clr.CYAN}{base_stat_file}{clr.END}')
   # print(f'  test_prof_file: {clr.CYAN}{test_prof_file}{clr.END}')
   # print(f'  test_stat_file: {clr.CYAN}{test_stat_file}{clr.END}')
   # print()
   #----------------------------------------------------------------------------
   # make sure all timing files are unzipped
   timing_file_list = base_prof_file \
                     +base_prof_file \
                     +test_stat_file \
                     +test_stat_file
   for f,tf in enumerate(timing_file_list):
      if '.gz' in tf:
         run_cmd(f'gunzip {tf} ')
         timing_file_list[f] = tf.replace('.gz','')
   #----------------------------------------------------------------------------   
   indent = ' '*4
   for param in param_list:
      base_file = base_stat_file if is_stat_param(param) else base_prof_file
      test_file = test_stat_file if is_stat_param(param) else test_prof_file
      
      if is_stat_param(param):
         print(indent+'      '+run_cmd(f'head {base_stat_file} -n 10')  .lstrip().rstrip().replace(' '*30+'on','on').split('\n')[6])
         print(indent+'base: '+run_cmd(f'grep \'{param}\'  {base_file}').lstrip().rstrip().replace(' '*30+'- ','- '))
         print(indent+'test: '+run_cmd(f'grep \'{param}\'  {test_file}').lstrip().rstrip().replace(' '*30+'- ','- '))
      else:
         print(indent+'base: '+run_cmd(f'grep \'{param}\'  {base_file}').lstrip().rstrip())
         print(indent+'test: '+run_cmd(f'grep \'{param}\'  {test_file}').lstrip().rstrip())
      print()

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
