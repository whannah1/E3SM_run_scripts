#!/usr/bin/env python3
import sys, os, fileinput, re, subprocess as sp
from glob import glob
from optparse import OptionParser
parser = OptionParser()
# Set up terminal colors
class bcolor:
   ENDC    = '\033[0m';  BLACK  = '\033[30m'; RED   = '\033[31m'  
   GREEN   = '\033[32m'; YELLOW = '\033[33m'; BLUE  = '\033[34m'
   MAGENTA = '\033[35m'; CYAN   = '\033[36m'; WHITE = '\033[37m'
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
parser.add_option('-n',dest='num_file',default=-1,help='number of files to print')
(opts, args) = parser.parse_args()


cases = []

#------------
# Round 1
#------------
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.F-MMF1.ntasks_5400.00')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.F-MMF1.ntasks_10800.00')
# cases.append('')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.F-MMF1.ntasks_10800.01')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.FC5AV1C-L.ntasks_5400.00')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.FC5AV1C-L.ntasks_10800.00')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.FC5AV1C-L.ntasks_10800.01')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.FC5AV1C-L.ntasks_10800.nthrds_2.00')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.FC5AV1C-L.ntasks_10800.nthrds_1.00')
# cases.append('E3SM.RGMA-timing.ne120pg2_r05_oECv3.FC5AV1C-H01A.ntasks_5400.00')  # memory error
# cases.append('E3SM.RGMA-timing.ne120pg2_r05_oECv3.FC5AV1C-H01A.ntasks_10800.00')
# cases.append('E3SM.RGMA-timing.ne120pg2_r05_oECv3.FC5AV1C-H01A.ntasks_10800.01')  # crashed
# cases.append('E3SM.RGMA-timing.ne120pg2_r05_oECv3.FC5AV1C-H01A.ntasks_10800.nthrds_2.00')
# cases.append('E3SM.RGMA-timing.ne120pg2_r05_oECv3.FC5AV1C-H01A.ntasks_10800.nthrds_1.00')

#------------
# Round 2
#------------

# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.FC5AV1C-L.ntasks_10800.02')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.CRMNX_128.RADNX_8.ntasks_10800.02')

# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.CRMNX_64.RADNX_1.ntasks_10800.03')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.CRMNX_64.RADNX_4.MSA_2.ntasks_8000.03')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.CRMNX_64.RADNX_4.MSA_4.ntasks_8000.03')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.CRMNX_64.RADNX_4.ntasks_10800.02')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.CRMNX_64.RADNX_4.MSA_4.ntasks_10800.03')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.CRMNX_64.RADNX_4.MSA_4.ntasks_10800.03.hist_ouput')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.CRMNX_64.RADNX_4.MSA_4.ntasks_10800.03.hist_ouput2')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.CRMNX_64.RADNX_8.MSA_4.ntasks_10800.03.hist_ouput2')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.CRMNX_64.RADNX_4.MSA_4.ntasks_10800.03.hist_ouput3')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.CRMNX_64.RADNX_4.MSA_4.ntasks_10800.03.hist_ouput4')
# cases.append('')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.CRMNX_128.RADNX_4.MSA_4.ntasks_10800.03.hist_ouput2')
# cases.append('')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.CRMNX_48.RADNX_1.ntasks_10800.03')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.CRMNX_48.RADNX_4.ntasks_10800.02')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.CRMNX_48.RADNX_4.ntasks_10800.03')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.CRMNX_48.RADNX_4.MSA_4.ntasks_10800.03')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.CRMNX_48.RADNX_4.ntasks_10800.03.hist_ouput')
# cases.append('')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.CRMNX_32.RADNX_4.ntasks_10800.03')
# cases.append('')
# cases.append('E3SM.RGMA-timing.ne120pg2_r05_oECv3.FC5AV1C-H01A.ntasks_10800.02')
# cases.append('E3SM.RGMA-timing.ne120pg2_r05_oECv3.FC5AV1C-H01A.ntasks_10800.03.hist_ouput')
# cases.append('E3SM.RGMA-timing.ne120pg2_r05_oECv3.FC5AV1C-H01A.ntasks_8000.03')
# cases.append('E3SM.RGMA-timing.ne120pg2_r05_oECv3.FC5AV1C-H01A.ntasks_8000.03.hist_ouput')
# cases.append('E3SM.RGMA-timing.ne120pg2_r05_oECv3.FC5AV1C-H01A.ntasks_10800.03.hist_ouput2')
# cases.append('E3SM.RGMA-timing.ne120pg2_r05_oECv3.FC5AV1C-H01A.ntasks_10800.03.hist_ouput3')
# cases.append('E3SM.RGMA-timing.ne120pg2_r05_oECv3.FC5AV1C-H01A.ntasks_10800.03.hist_ouput4')

# cases.append('')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.F-MMF1.CRMNX_64.CRMDX_2000.CRMDT_5.RADNX_4.MSA_4.ntasks_10800.04.hist_ouput')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.F-MMF1.CRMNX_64.CRMDX_2000.CRMDT_6.RADNX_4.MSA_4.ntasks_10800.04.hist_ouput')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.F-MMF1.CRMNX_64.CRMDX_2000.CRMDT_6.RADNX_4.MSA_3.ntasks_10800.04.hist_ouput')
# cases.append('E3SM.RGMA-timing.ne30pg2_r05_oECv3.F-MMF1.CRMNX_64.CRMDX_2000.CRMDT_10.RADNX_4.MSA_2.ntasks_10800.04.hist_ouput')
cases.append('')

cases.append('E3SM.RGMA.ne30pg2_r05_oECv3.FC5AV1C-L.00')
cases.append('')
cases.append('E3SM.RGMA.ne120pg2_r05_oECv3.FC5AV1C-H01A.00')
cases.append('')
cases.append('E3SM.RGMA.ne30pg2_r05_oECv3.F-MMF1.CRMNX_64.CRMDX_2000.RADNX_4.00')
cases.append('')

# cases.append('')

#------------
#------------

param_list = []
param_list.append('Throughput')
# param_list.append('Run Time    :')
# param_list.append('ATM Run Time')
# param_list.append('CPL Run Time:')
# param_list.append('\"a:crm\"')
# param_list.append('a:CAM_run3')
# param_list.append('a:CAM_run4')

#-------------------------------------------------------------------------------
# make sure all logs are unzipped
#-------------------------------------------------------------------------------
max_case_len = 0
for c,case in enumerate(cases):
   timing_dir = os.getenv('HOME')+f'/E3SM/Cases/{case}/timing'
   timing_stat_gz_path = f'{timing_dir}/*.gz'
   if len(glob(timing_stat_gz_path))>0: os.system(f'gunzip {timing_stat_gz_path} ')
   # find max char len for case name
   if len(case)>max_case_len: max_case_len = len(case)

#-------------------------------------------------------------------------------
# Loop through parameters and cases
#-------------------------------------------------------------------------------
for param in param_list :
   print('-'*80)
   for c,case in enumerate(cases):
      if case=='':
         print('')
         continue
      timing_dir = os.getenv('HOME')+f'/E3SM/Cases/{case}/timing'
      
      # if 'RGMA-timing' in case: timing_dir = timing_dir.replace('/Cases/','/Cases/RGMA_timing/')
      
      case_name_fmt = bcolor.CYAN+f'{case:{max_case_len}}'+bcolor.ENDC

      # check that the timing files exist
      timing_file_path = f'{timing_dir}/*'
      if len(glob(timing_file_path))==0: 
         print(f'{case_name_fmt}  No files!')
         continue

      #-------------------------------------------------------------------------
      # grep for the appendropriate line in the stat files
      cmd = 'grep  \''+param+f'\'  {timing_dir}/*'
      proc = sp.Popen(cmd, stdout=sp.PIPE, shell=True, universal_newlines=True)
      (msg, err) = proc.communicate()
      msg = msg.split('\n')

      stat_file = msg[0].split(':')[0]

      #-------------------------------------------------------------------------
      # Clean up message but don't print yet
      for m in range(len(msg)): 
         line = msg[m]
         line = line.replace(timing_dir+'/','')
         line = line.replace(f'e3sm_timing.{case}.','e3sm_timing        ')
         line = line.replace('e3sm_timing_stats.'  ,'e3sm_timing_stats  ')
         # Add case name
         if line!='': line = case_name_fmt+line
         line = line.replace(f'e3sm_timing      ','')
         msg[m] = line
      #-------------------------------------------------------------------------
      # print stat file header with indentation
      if 'a:' in param : 
         head = sp.check_output(['head',stat_file],universal_newlines=True).split('\n')
         for line in head: 
            if 'walltotal' in line:
               indent = len(msg[0].split(':')[0])+1
               line = ' '*indent+line
               hline = line
               # Get rid of some dead space
               line = line.replace('name        ','name')
               print(hline)
               break
      #-------------------------------------------------------------------------
      # set up character indices for color
      if 'a:' in param:
         n1 = hline.find('walltotal')    +len('walltotal')
         n2 = hline.find('wallmax')      +len('wallmax')
         n3 = hline.find('wallmax')      +len('wallmax (proc   thrd  )')
         n4 = hline.find('wallmin')      +len('wallmin')
      else:
         line = msg[0]
         n1 = line.replace(':','', 1).find(':')+2
         num_in_list = re.findall(r'\d+\.\d+', line[n1:])
         n2 = line.find(num_in_list[0])+len(num_in_list[0])

      #-------------------------------------------------------------------------
      # print the timing data
      num_file = -int(opts.num_file)-1
      if opts.num_file==-1 : num_file = -len(msg)
      for line in msg[num_file:] : 
         if line=='': continue
         if 'a:' in param : 
            line = line[:n1] \
                 +bcolor.CYAN  +line[n1:n2]+bcolor.CYAN +line[n2:n3] \
                 +bcolor.GREEN +line[n3:n4]+bcolor.ENDC +line[n4:]
            # Get rid of some dead space
            line = line.replace('        ','')
         else:
            line = line[:n1] \
                 +bcolor.GREEN +line[n1:n2]+bcolor.ENDC \
                 +line[n2:]
            # Print conversion to min aand hours for specific params
            offset = len(bcolor.GREEN)
            if param=='Run Time    :' and line[n1+offset:n2+offset]!='' :
               sec = float( line[n1+offset:n2+offset] )
               line = line+'  ('+bcolor.GREEN+f'{sec/60:.2f}'     +bcolor.ENDC+' min)'
               line = line+'  ('+bcolor.GREEN+f'{sec/60/60:.2f}'  +bcolor.ENDC+' hour)'
         # print the line
         print(line)
         


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
