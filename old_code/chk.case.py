#!/usr/bin/env python3
#=============================================================================================================
#  Nov, 2017 - Walter Hannah - Lawrence Livermore National Lab
#  This script checks the status of current E3SM cases (i.e. debug mode, compset, misc flags, etc.)
#=============================================================================================================
import sys, os, fileinput, glob, subprocess as sp
home = os.getenv('HOME')
if os.path.islink(home): home = os.readlink(home)
# # Use this method in case $HOME is a symlink
# home = sp.check_output('echo '$(cd -P $HOME && pwd)'', shell=True, universal_newlines=True).rstrip()

from optparse import OptionParser
parser = OptionParser()

parser.add_option('--no-indent',action='store_false', dest='indent_flag', default=True,help='do not indent long variables')
parser.add_option('--params', dest='params', default=None,help='Comma separated list of params')
parser.add_option('--partial',action='store_true', dest='allow_partial_match', default=False,help='allow partial matches of input search strings')

(opts, args) = parser.parse_args()

# Set up terminal colors
class bcolor:
   ENDC     = '\033[0m'
   BOLD     = '\033[1m'
   BLACK    = '\033[30m'
   RED      = '\033[31m'
   GREEN    = '\033[32m'
   YELLOW   = '\033[33m'
   BLUE     = '\033[34m'
   MAGENTA  = '\033[35m'
   CYAN     = '\033[36m'
   WHITE    = '\033[37m'
   ULINEON  = '\033[4m'
   ULINEOFF = '\033[24m'

# workdir = os.getenv('MEMBERWORK')
# workdir = '/lustre/atlas/scratch/hannah6/'


#=============================================================================================================
# arguments are used to provide a string to search case names for, like 'SP' or 'ZM' or a case number
#=============================================================================================================
if len(args) < 1 :
   # print all cases
   search_strings = []

   print
   print('ERROR: no search string provided!')
   print
   exit()
else :
   # search_strings = sys.argv[1:]
   search_strings = args

#=============================================================================================================
# Specify what we want to see in the output 
#=============================================================================================================
# Specify default list of parameters to search for in case xml files
if opts.params is None :
   # param_list = ['DEBUG','CONTINUE_RUN']
   # param_list = ['DEBUG','CONTINUE_RUN','STOP_N','JOB_WALLCLOCK_TIME']
   # param_list = ['COMPILER','OPT','BFBFLAG','se_nsplit','ATM_NCPL','DEBUG','CONTINUE_RUN','STOP_N','STOP_OPTION','RESUBMIT','JOB_WALLCLOCK_TIME','COMPSET','nhtfrq','CAM_CONFIG_OPTS']
   param_list=['COMPSET','NTASKS','NTHRDS',
            'MAX_TASKS_PER_NODE',
            'MAX_MPITASKS_PER_NODE',
            'JOB_WALLCLOCK_TIME','JOB_QUEUE',
            'se_tstep','dt_remap_factor','dt_tracer_factor',
            # 'se_nsplit','rsplit','qsplit',
            'hypervis_scaling','hypervis_subcycle','hypervis_subcycle_q','hypervis_subcycle_tom',
            # 'nu','nu_div','nu_top','nu_p','nu_q','nu_s',
            'nhtfrq','ncdata','finidat',
            'BFBFLAG','NCPL','CONTINUE_RUN','STOP_N','STOP_OPTION','RESUBMIT',
            'CAM_NML_USE_CASE','DEBUG','CAM_CONFIG_OPTS',
            ]
else:
   param_list = opts.params.split(',')
           

# param_list = ['ATM_NCPL']


top_dir_list = []
# top_dir_list.append( home+'/E3SM/Cases' )
top_dir_list.append( home+'/E3SM/scratch' )
top_dir_list.append( home+'/E3SM/scratch2' )
top_dir_list.append( home+'/E3SM/scratch_v3' )
top_dir_list.append( home+'/E3SM/scratch-frontier' )
top_dir_list.append( home+'/E3SM/scratch-frontier-proj' )
top_dir_list.append( home+'/E3SM/scratch-crusher' )
top_dir_list.append( home+'/E3SM/scratch_pm' )
top_dir_list.append( home+'/E3SM/scratch_pm-gpu' )
top_dir_list.append( home+'/E3SM/scratch_pm-cpu' )
top_dir_list.append( home+'/E3SM/scratch-summit' )
top_dir_list.append( home+'/E3SM/scratch-llnl1' )
top_dir_list.append( home+'/E3SM/scratch-llnl2' )


# replace linked paths with full path
for i,top_dir in enumerate(top_dir_list):
   if os.path.exists(top_dir) and os.path.islink(top_dir):
      top_dir_list[i] = os.readlink(top_dir)


case_list = []
path_list = []
run_path_list = []

ndir_max = 0

for top_dir in top_dir_list:

   dirs = glob.glob( top_dir+'/*' )
   ndir = len(dirs)

   ndir_max = max(ndir_max,ndir)

   ### specify string lengths for nice formatting
   indent_len  = 2
   xmlfile_len = 18
   param_len   = 20
   total_len   = indent_len + xmlfile_len + param_len

   ### use multiple lines for variables with long values
   status_len_limit = 80

   #=============================================================================================================
   # Start looping through case directories
   #=============================================================================================================

   for tdir in dirs :
      case = tdir.replace(top_dir,'').replace('/','')
      found = True
      # if search_strings : 
      #    found = False
      #    for sub_string in search_strings :
      #       # if sub_string in case : found = True
      #       if opts.allow_partial_match:
      #          if sub_string in case : found = True
      #       else:
      #          if sub_string == case : found = True
      # if not found : continue
      if search_strings : 
         found = False
         for sub_string in search_strings :
            # if sub_string in case : found = True
            if opts.allow_partial_match:
               if sub_string in case : found = True
            else:
               if sub_string == case : found = True
      if found:
         if 'Cases' in top_dir:
            tmp_path = f'{top_dir}/{case}'
            os.chdir(tdir)
            (msg, err) = sp.Popen([f'./xmlquery --value RUNDIR'], 
                           stdout=sp.PIPE, shell=True, 
                           universal_newlines=True).communicate()
            tmp_run_path = msg
            os.chdir(f'{home}/E3SM')
         else:
            tmp_path = f'{top_dir}/{case}/case_scripts'
            if not os.path.exists(tmp_path): found = False
            tmp_run_path = f'{top_dir}/{case}/run'
         if found:
            case_list.append(case)
            path_list.append(tmp_path)
            run_path_list.append(tmp_run_path)
      else:
         continue


out = ['' for n in range(ndir_max+1)]
cnt = 0

case_cnt = 0
for c,case in enumerate(case_list):
   case_cnt += 1
   tdir = path_list[c]
   trun = run_path_list[c]
   #----------------------------------------------------------------------------
   # Loop through parameters
   #----------------------------------------------------------------------------
   pcnt = 0
   for param in param_list :
      
      alternate = False
      #-------------------------------------------------------------------------
      # Macros file settings
      if param == 'OPT' :
         proc = sp.Popen([f'grep  \'ifeq (\$(DEBUG), FALSE)\'  {tdir}/Macros.make -A1 '], \
                     stdout=sp.PIPE, shell=True, universal_newlines=True)
         (msg, err) = proc.communicate()
         msg1 = msg.split('\n')
         # xmlfile = 'Macros.make'
         
         if msg1!=[''] :
            status  = msg1[1].lstrip()
            alternate = True
      #-------------------------------------------------------------------------
      # Time step (NCPL) 
      if param == 'NCPL' :
         alternate = True
         os.chdir(tdir)
         ncpl_params = []
         ncpl_params.append('ATM_NCPL'),ncpl_params.append('LND_NCPL')
         ncpl_params.append('ICE_NCPL'),ncpl_params.append('OCN_NCPL')
         ncpl_params.append('GLC_NCPL'),ncpl_params.append('ROF_NCPL')
         ncpl_params.append('WAV_NCPL'),ncpl_params.append('IAC_NCPL')

         xmlfile = None
         status = ''
         ncpl_cnt = 0
         for p in ncpl_params:
            (msg, err) = sp.Popen([f'./xmlquery --full {p}'], 
                           stdout=sp.PIPE, shell=True, 
                           universal_newlines=True).communicate()
            ### Parse out file name and status
            for line in msg.split('\n') :
               if 'file:' in line and xmlfile is None : 
                  xmlfile = line.split(':')[1].lstrip().replace('/global/u1','/global/homes')
               if f'{p}:' in line : 
                  tmp_status = line.replace(f'{p}:','').lstrip().replace('value=','')
                  if ncpl_cnt>0: status += ', '
                  status += (p.replace('_NCPL',''))+f':{tmp_status}'
                  ncpl_cnt+=1
         status = f'[{status}]'

      #-------------------------------------------------------------------------
      # Namelist variables
      if param in ['rsplit','qsplit','se_nsplit','nhtfrq',
               'se_tstep','dt_remap_factor','dt_tracer_factor',
               'hypervis_order','hypervis_scaling',
               'hypervis_subcycle','hypervis_subcycle_q','hypervis_subcycle_tom',
               'nu','nu_div','nu_top','nu_p','nu_q','nu_s',
               'ncdata','finidat','fsurdat','bnd_topo',
               'dtime',
               ] :
         xmlfile = 'atm_in'
         if param in ['finidat','fsurdat']: xmlfile = 'lnd_in'
         # tmp_path = glob.glob(os.getenv('HOME')+f'/E3SM/scratch*/{case}/run')[0]
         # tmp_path = glob.glob(f'{top_dir}/{case}/run')[0]
         # tmp_path = glob.glob(f'{trun}')[0]
         
         nml_file = f'{trun}/{xmlfile}'
         
         if not os.path.exists(nml_file):
            continue
         else:
            cmd = f'grep  \'{param}\s\' {nml_file}'
            (msg, err) = sp.Popen([cmd], 
                           stdout=sp.PIPE, shell=True, 
                           universal_newlines=True).communicate()
            status = msg
            status = status.replace(f' {param} ','')
            status = status.replace('=','')
            status = status.replace('\'','')
            status = status.replace('\n','')
            status = status.lstrip()
            alternate = True

      #-------------------------------------------------------------------------
      # XML file variables
      if not alternate : 
         os.chdir(tdir)
         (msg, err) = sp.Popen(['./xmlquery --full  '+param+'  '], 
                        stdout=sp.PIPE, shell=True, 
                        universal_newlines=True).communicate()

         # Parse out file name and status
         for line in msg.split('\n') :
            if 'file:' in line : 
               xmlfile = line.split(':')[1].lstrip()
               xmlfile = xmlfile.replace('/global/u1','/global/homes')
            if (param+':') in line : status = line.replace(param+':','').lstrip().replace('value=','')

      #-------------------------------------------------------------------------
      # format message
      # strip the path off the xml file
      if 'scratch' in xmlfile:
         tmp_path = glob.glob(os.getenv('HOME')+f'/E3SM/scratch*/{case}/case_scripts/')[0]
         # replace scratch soft link with full scratch path
         scratch_link = tmp_path.replace(f'/{case}/case_scripts/','')
         scratch_full = os.readlink(scratch_link)
         tmp_path = tmp_path.replace(scratch_link,scratch_full)
      else:
         tmp_path = f'{home}/E3SM/Cases/{case}/'
      tmp_path = tmp_path.replace('//','/')
      xmlfile = xmlfile.replace(tmp_path,'')
      
      #-------------------------------------------------------------------------
      # Color the output to highlight special circumstances
      clr = ''
      if 'BFBFLAG'  in param and 'FALSE' in status : clr = bcolor.RED
      if 'DEBUG'    in param and 'TRUE'  in status : clr = bcolor.RED
      if 'CONTINUE' in param and 'TRUE'  in status : clr = bcolor.GREEN
      status = status.replace('TRUE' ,clr+'TRUE' +bcolor.ENDC)
      status = status.replace('FALSE',clr+'FALSE'+bcolor.ENDC)

      # print the case name only on the first line
      if pcnt==0 : 
         tmp_msg = bcolor.BOLD+bcolor.ULINEON+'\n'+case.ljust(indent_len)+bcolor.ENDC+bcolor.ULINEOFF
         out[cnt] += tmp_msg
         
      out[cnt] = out[cnt]+'\n'+' '.ljust(indent_len)
      out[cnt] = out[cnt]+'  '+xmlfile.ljust(xmlfile_len)  # print xml file name
      out[cnt] = out[cnt]+'  '+param.ljust(param_len)      # print parameter name

      #-------------------------------------------------------------------------
      # break up long lines if indent_flag is False
      if len(status)>status_len_limit and opts.indent_flag and status[0]!='[' and len(status.split())>1 :
         ### for long straings like CAM_CONFIG_OPTS, break the status message into multiple lines and justify,
         ### split the status by word count and character length for better readability
         status_split = status.split()
         word_cnt = 0
         line_len = 0
         for word in status_split :
            ### first check if we should jump to the next line
            if (word_cnt==10) or (line_len+len(word))>(80):
               out[cnt] = out[cnt]+'\n'+' '.ljust(total_len+4)
               word_cnt = 0
               line_len = 0
            ### now add the next part of the status
            out[cnt] = out[cnt]+'  '+word
            line_len = line_len + len(word)
            word_cnt = word_cnt + 1
      else :
         # # convert list into multiple lines
         # if status[0]=='[':
         #     status = status.replace('[','')
         #     status = status.replace(']','')
         #     status = status.replace('\'','')
         #     status = status.replace(', ','\n'+' '.ljust(indent_len+xmlfile_len+param_len+6))
         out[cnt] = out[cnt]+'  '+status             # print parameter value

      pcnt = pcnt+1
      #-------------------------------------------------------------------------
   cnt = cnt+1

#-------------------------------------------------------------------------------
# sort the cases alphbetically
out.sort()

#-------------------------------------------------------------------------------
# color the file names
for file_name in ['atm_in','env_build.xml','env_run.xml','env_case.xml'] :
   if file_name=='atm_in'          : clr = bcolor.RED
   if file_name=='env_build.xml'   : clr = bcolor.GREEN
   if file_name=='env_run.xml'     : clr = bcolor.MAGENTA
   if file_name=='env_case.xml'    : clr = bcolor.CYAN
   for l in range(len(out)) :
      out[l] = out[l].replace(file_name,clr+file_name+bcolor.ENDC) 

print
for line in out : 
   if line!='' : print( line )


#=============================================================================================================
#=============================================================================================================
