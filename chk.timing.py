#!/usr/bin/env python3

# conda create --name base++ -c conda-forge natsort
# conda activate base++

import sys, os, fileinput, re, subprocess as sp, glob
from optparse import OptionParser
import importlib
natsort_spec = None
# natsort_spec = importlib.util.find_spec("natsort")
natsort_found = natsort_spec is not None
if natsort_found: from natsort import natsorted, ns
# print(natsort_found)
# exit()
#-------------------------------------------------------------------------------
# Set up terminal colors
#-------------------------------------------------------------------------------
class bcolor:
   ENDC    = '\033[0m';  BLACK  = '\033[30m'; RED   = '\033[31m'  
   GREEN   = '\033[32m'; YELLOW = '\033[33m'; BLUE  = '\033[34m'
   MAGENTA = '\033[35m'; CYAN   = '\033[36m'; WHITE = '\033[37m'
#-------------------------------------------------------------------------------
# command line options
#-------------------------------------------------------------------------------
parser = OptionParser()
parser.add_option('-n',dest='num_file',default=-1,help='number of files to print')
parser.add_option("--all",action="store_true", dest="show_all", default=False,help="ahow all component timers")
parser.add_option('--params', dest='params', default=None,help='Comma separated list of params')
parser.add_option("--partial",action="store_true", dest="allow_partial_match", default=False,help="allow partial matches of input search strings")
parser.add_option("--alt",action="store_true", dest="predefined_case", default=False,help="let predefined cases override input arguments")
(opts, args) = parser.parse_args()
#-------------------------------------------------------------------------------
# define list of cases
#-------------------------------------------------------------------------------

top_dir_list = []
top_dir_list.append( os.getenv('HOME')+'/E3SM/Cases' )
top_dir_list.append( os.getenv('HOME')+'/E3SM/scratch' )
top_dir_list.append( os.getenv('HOME')+'/E3SM/scratch_v3' )
top_dir_list.append( os.getenv('HOME')+'/E3SM/scratch_pm-cpu' )
top_dir_list.append( os.getenv('HOME')+'/E3SM/scratch_pm-gpu' )
top_dir_list.append( os.getenv('HOME')+'/E3SM/scratch-llnl' )
top_dir_list.append( os.getenv('HOME')+'/E3SM/scratch-llnl1' )
top_dir_list.append( os.getenv('HOME')+'/E3SM/scratch-llnl2' )
top_dir_list.append( os.getenv('HOME')+'/E3SM/scratch-frontier-proj' )
top_dir_list.append( os.getenv('HOME')+'/SCREAM/scratch' )
top_dir_list.append( os.getenv('HOME')+'/SCREAM/scratch_pm-cpu' )
top_dir_list.append( os.getenv('HOME')+'/SCREAM/scratch_pm-gpu' )

#-------------------------------------------------------------------------------

if opts.predefined_case:

   print(f'{bcolor.RED}WARNING{bcolor.ENDC} - overriding input arguments - {bcolor.RED}WARNING{bcolor.ENDC}')

   case_list = []

   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne30pg2.dt_phy_100.dyn_fac_12.rmp_fac_2.trc_fac_12.trc_ss_2')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne30pg2.dt_phy_100.dyn_fac_12.rmp_fac_2.trc_fac_6.trc_ss_1')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne30pg2.dt_phy_75.dyn_fac_8.rmp_fac_2.trc_fac_8.trc_ss_2')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne30pg2.dt_phy_75.dyn_fac_8.rmp_fac_2.trc_fac_4.trc_ss_1')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne30pg2.dt_phy_75.dyn_fac_9.rmp_fac_1.trc_fac_9.trc_ss_2')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne30pg2.dt_phy_75.dyn_fac_10.rmp_fac_1.trc_fac_5.trc_ss_1')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne30pg2.dt_phy_60.dyn_fac_6.rmp_fac_3.trc_fac_6.trc_ss_1')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne30pg2.dt_phy_60.dyn_fac_6.rmp_fac_2.trc_fac_6.trc_ss_1')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne30pg2.dt_phy_60.dyn_fac_6.rmp_fac_3.trc_fac_6.trc_ss_2')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne30pg2.dt_phy_60.dyn_fac_6.rmp_fac_2.trc_fac_6.trc_ss_2')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne30pg2.dt_phy_60.dyn_fac_7.rmp_fac_1.trc_fac_7.trc_ss_2')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne30pg2.dt_phy_60.dyn_fac_8.rmp_fac_2.trc_fac_8.trc_ss_2')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne30pg2.dt_phy_60.dyn_fac_8.rmp_fac_2.trc_fac_4.trc_ss_1')

   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne256pg2.dt_phy_100.dyn_fac_12.rmp_fac_2.trc_fac_6.trc_ss_1')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne256pg2.dt_phy_100.dyn_fac_12.rmp_fac_2.trc_fac_12.trc_ss_2')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne256pg2.dt_phy_75.dyn_fac_10.rmp_fac_1.trc_fac_5.trc_ss_1')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne256pg2.dt_phy_75.dyn_fac_9.rmp_fac_1.trc_fac_9.trc_ss_2')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne256pg2.dt_phy_75.dyn_fac_8.rmp_fac_2.trc_fac_8.trc_ss_2')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne256pg2.dt_phy_75.dyn_fac_8.rmp_fac_2.trc_fac_4.trc_ss_1')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne256pg2.dt_phy_60.dyn_fac_8.rmp_fac_2.trc_fac_4.trc_ss_1')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne256pg2.dt_phy_60.dyn_fac_8.rmp_fac_2.trc_fac_8.trc_ss_2')
   # case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne256pg2.dt_phy_60.dyn_fac_7.rmp_fac_1.trc_fac_7.trc_ss_2')

   case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne1024pg2.dt_phy_100.dyn_fac_12.rmp_fac_2.trc_fac_6.trc_ss_1')
   case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne1024pg2.dt_phy_100.dyn_fac_12.rmp_fac_2.trc_fac_12.trc_ss_2')
   case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne1024pg2.dt_phy_75.dyn_fac_10.rmp_fac_1.trc_fac_5.trc_ss_1')
   case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne1024pg2.dt_phy_75.dyn_fac_9.rmp_fac_1.trc_fac_9.trc_ss_2')
   case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne1024pg2.dt_phy_75.dyn_fac_8.rmp_fac_2.trc_fac_8.trc_ss_2')
   case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne1024pg2.dt_phy_75.dyn_fac_8.rmp_fac_2.trc_fac_4.trc_ss_1')
   case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne1024pg2.dt_phy_60.dyn_fac_8.rmp_fac_2.trc_fac_4.trc_ss_1')
   case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne1024pg2.dt_phy_60.dyn_fac_8.rmp_fac_2.trc_fac_8.trc_ss_2')
   case_list.append('SCREAM.2025-DT-00.F2010-SCREAMv1.ne1024pg2.dt_phy_60.dyn_fac_7.rmp_fac_1.trc_fac_7.trc_ss_2')

   alt_format = True

else:

   alt_format = False

   case_list = []
   path_list = []

   for top_dir in top_dir_list:

      dirs = glob.glob( top_dir+'/*' )
      ndir = len(dirs)

      # arguments are used to provide a string to search case names
      if len(args) < 1 :
         exit('\nERROR: no search string provided!\n')
      else :
         search_strings = args

      # loop over case directories
      for tdir in dirs :
         case = tdir.replace(top_dir+'/','')
         found = True
         if search_strings : 
            found = False
            for sub_string in search_strings :
               # if sub_string in case : found = True
               if opts.allow_partial_match:
                  if sub_string in case : found = True
               else:
                  if sub_string == case : found = True
         if found : 
            case_list.append(case)
            if 'Cases' in top_dir:
               tmp_path = f'{top_dir}/{case}/timing'
            else:
               tmp_path = f'{top_dir}/{case}/case_scripts/timing'
            path_list.append(tmp_path)
         else:
            continue

   # sort the cases alphabetically
   if natsort_found:
      case_list = natsorted(case_list)
   else:
      case_list.sort()

   case_list.sort()
   path_list.sort()

   case_list = args

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

path_list = [None]*len(case_list)
for c,case in enumerate(case_list):
   path_list[c] = f'/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch/{case}/case_scripts/timing'

# print()
# for c in case_list: print(c)
# print()
# exit()

#-------------------------------------------------------------------------------
# Define timing file parameters to be parsed
#-------------------------------------------------------------------------------
if opts.params is None:
   param_list = []
   # param_list.append('Throughput')
   # param_list.append('Cost')
   # param_list.append('run length  :')
   # param_list.append('Run Time    :')

   if opts.show_all:
      param_list.append('TOT Run Time:')
      param_list.append('CPL Run Time:')
      param_list.append('ATM Run Time')
      param_list.append('LND Run Time:')
      param_list.append('OCN Run Time:')
      param_list.append('ICE Run Time:')
   else:
      # param_list.append('ATM Run Time')
      param_list.append('TOT Run Time:')
      # param_list.append('Throughput')

   # param_list.append('CPL:ATM_RUN')

   # param_list.append('a:CAM_run1')
   # param_list.append('a:CAM_run2')
   # param_list.append('a:CAM_run3')
   # param_list.append('a:CAM_run4')

   # param_list.append('a:crm')
   # param_list.append('a:radiation')

   # param_list.append('a:EAMxx::homme::run"')
   # param_list.append('a:EAMxx::physics::run"')

   if opts.predefined_case:
      param_list = []
      param_list.append('TOT Run Time:')
      param_list.append('a:EAMxx::homme::run"')
      param_list.append('a:EAMxx::physics::run"')

else:
   param_list = opts.params.split(',')

avg_param_list = []
avg_param_list.append('Throughput')
avg_param_list.append('Cost')
avg_param_list.append('TOT Run Time:')
avg_param_list.append('ATM Run Time:')
avg_param_list.append('CPL:ATM_RUN')



#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def is_stat_param(param):
   if 'a:'   in param: return True
   if 'a_i:' in param: return True
   if 'CPL:' in param: return True
   return False
#-------------------------------------------------------------------------------
# make sure all logs are unzipped
#-------------------------------------------------------------------------------
max_case_len = 0
for c,case in enumerate(case_list):
   # timing_dir = os.getenv('HOME')+f'/E3SM/Cases/{case}/timing'
   timing_dir = path_list[c]
   timing_stat_gz_path = f'{timing_dir}/*.gz'
   if len(glob.glob(timing_stat_gz_path))>0: os.system(f'gunzip {timing_stat_gz_path} ')
   # find max char len for case name
   if len(case)>max_case_len: max_case_len = len(case)

max_case_len = max_case_len+4

#-------------------------------------------------------------------------------
# Loop through parameters and cases
#-------------------------------------------------------------------------------
print('-'*100)
for param in param_list :
   case_cnt = 0
   for c,case in enumerate(case_list):
      case_cnt += 1
      # print('')
      if case=='':
         print('')
         continue
      # timing_dir = os.getenv('HOME')+f'/E3SM/Cases/{case}/timing'
      timing_dir = path_list[c]
      
      # if 'RGMA-timing' in case: timing_dir = timing_dir.replace('/Cases/','/Cases/RGMA_timing/')
      
      case_name_fmt = bcolor.CYAN+f'{case:{max_case_len}}'+bcolor.ENDC

      # check that the timing files exist
      timing_file_path = f'{timing_dir}/*'
      if len(glob.glob(timing_file_path))==0: 
         print(f'{case_name_fmt}  No files!')
         continue

      #-------------------------------------------------------------------------
      # grep for the appropriate line in the stat files

      # if 'a:' in param : 
      #    cmd = 'grep  \''+param+f'\"\'  {timing_dir}/*'
      # else:
      #    cmd = 'grep  \''+param+f'\'  {timing_dir}/*'
      # proc = sp.Popen(cmd, stdout=sp.PIPE, shell=True, universal_newlines=True)
      # (msg, err) = proc.communicate()
      # msg = msg.split('\n')
      # stat_file = msg[0].split(':')[0]

      stat_file = f'{timing_dir}/e3sm_timing*'
      if 'CPL:' in param: stat_file = stat_file.replace('*','_stats*')
      cmd = f'grep  --with-filename \'{param}\'  {stat_file}'
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
         # line = line.replace('e3sm_timing_stats.'  ,'e3sm_timing_stats  ')
         if 'e3sm_timing_stats' in line: line = line[40:]
         line = line.replace(f'e3sm_timing      ','')
         # line = line[23:] # drop job number string
         # Add case name
         if line!='': line = case_name_fmt+line
         msg[m] = line
         
      # # don't show file or case
      # for m in range(len(msg)): 
      #    if msg[m]!='':
      #       if ':' in msg[m]: msg[m] = msg[m].split(':')[1:]
      #       if isinstance(msg[m],list): msg[m] = ':'.join(msg[m])
      #-------------------------------------------------------------------------
      # print stat file header with indentation
      if is_stat_param(param):
         head = sp.check_output(['head',stat_file],universal_newlines=True).split('\n')
         for line in head: 
            if 'walltotal' in line:
               # indent = len(msg[0].split(':')[0])+1 - 12
               indent = max_case_len
               line = ' '*indent+line
               hline = line
               # # Get rid of some dead space
               # line = line.replace('name        ','name')

               if alt_format: hline = ' '*64 + hline.replace(' '*32,'').strip(' ')

               if c==0: print(hline)
               break
      #-------------------------------------------------------------------------
      # set up character indices for color
      if is_stat_param(param):
         n1 = hline.find('walltotal')    +3*1
         n2 = hline.find('wallmax')      +3*2
         n3 = hline.find('wallmin')      +3*3
      else:
         line = msg[0]
         n1 = line.replace(':','', 1).find(':')+2
         num_in_list = re.findall(r'\d+\.\d+', line[n1:])
         n2 = line.find(num_in_list[0])+len(num_in_list[0])

      #-------------------------------------------------------------------------
      # print the timing data
      num_file = -int(opts.num_file)-1
      if opts.num_file==-1 : num_file = -len(msg)
      cnt = 0
      for line in msg[num_file:] : 
         if line=='': continue
         if is_stat_param(param):
            line = line[:n1] \
                 +bcolor.MAGENTA +line[n1:n2] +bcolor.CYAN +line[n2:n3] \
                 +bcolor.GREEN   +line[n3:] +bcolor.ENDC
            # # Get rid of some dead space
            # line = line.replace('        ','')
         else:
            # line = line[:n1] \
            #      +bcolor.GREEN +line[n1:n2]+bcolor.ENDC \
            #      +line[n2:]
            tstr = line[n2:]
            tn1 = tstr.find('seconds/mday')+len('seconds/mday')
            tn2 = tstr.find('myears/wday')
            tn3 = tstr.find('myears/wday')+len('myears/wday')
            line = line[:n1] + bcolor.GREEN + tstr[tn1:tn2] + bcolor.ENDC + tstr[tn2:tn3]
            # line = line[:n1] + bcolor.GREEN + tstr[tn1:tn2] + bcolor.ENDC + 'sypd'

            # calculate average/mean of total throughput
            if param in avg_param_list:
               if cnt==0: avg_throughput = 0
               if param=='Throughput'   : tmp = float(line[n1:n2])
               if param=='Cost'         : tmp = float(line[n1:n2])
               if param=='TOT Run Time:': tmp = float(tstr[tn1:tn2])
               if param=='ATM Run Time:': tmp = float(tstr[tn1:tn2])
               avg_throughput = ( avg_throughput*cnt + tmp ) / (cnt+1)
               cnt += 1
                 
            
            
            # Print conversion to min and hours for specific params
            offset = len(bcolor.GREEN)
            if param=='Run Time    :' and line[n1+offset:n2+offset]!='' :
               sec = float( line[n1+offset:n2+offset] )
               line = line+'  ('+bcolor.GREEN+f'{sec/60:.2f}'     +bcolor.ENDC+' min)'
               line = line+'  ('+bcolor.GREEN+f'{sec/60/60:.2f}'  +bcolor.ENDC+' hour)'
         line = line.replace(': ','') # drop the extra colon
         # print the line divider
         # if case_cnt==1: print('-'*100)
         # if case_cnt==1: print('-'*len(line.rstrip())) # not sure why this doesn't work...

         if alt_format:
            alt_case = case
            alt_case = alt_case.replace('SCREAM.2025-DT-00.F2010-SCREAMv1.ne1024pg2.','')
            alt_case = alt_case.split('.')
            alt_case = [f'{a:12}' for a in alt_case]
            alt_case = ' '.join(alt_case).rstrip(' ')
            line = line.replace(case,'')
            line = line.replace('\033[36m','')
            line = line.replace('\033[0m','')
            line = line.lstrip(' ')
            line = f'{alt_case}    {line}'
            line = line.replace(stat_file[-21:],'')
            # line = line.replace(' '*40,'')
            line = line.replace(' '*32,'')
            line = line+bcolor.ENDC
            # print(line)
            # exit()

         # print the line
         print(line)

      if param in avg_param_list and num_file>1:
         avg_throughput = bcolor.GREEN+f'{avg_throughput:.2f}'+bcolor.ENDC
         if param=='Throughput'   : print(f'    Average Throughput: {avg_throughput} sypd')
         if param=='Cost'         : print(f'    Average Cost: {avg_throughput} pe-hrs/simulated_year')
         if param=='TOT Run Time:': print(f'    Average {param}: {avg_throughput} sypd')
         if param=='ATM Run Time:': print(f'    Average {param}: {avg_throughput} sypd')

      # if case_cnt>1: print('-'*64)
   print('-'*100)
         

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
