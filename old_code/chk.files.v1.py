#!/usr/bin/env python3
#=============================================================================================================
#  Nov, 2017 - Walter Hannah - Lawrence Livermore National Lab
#  This script checks the output files of current E3SM cases (i.e. debug mode, compset, misc flags, etc.)
#=============================================================================================================
import sys, os, fileinput, glob
import subprocess
home = os.getenv('HOME')

from optparse import OptionParser
parser = OptionParser('./chk.files.py CASE [options]\n\nlist the latest files for a given case\nDefault is set to look for files matching *eam.h1*')

parser.add_option('--no-indent',action='store_false', dest='indent_flag', default=True,help='do not indent long variables')
parser.add_option('-n',dest='num_file',default=5,help='sets number of files to print')
parser.add_option('--alt',dest='alt_search_str',default='E3SM',help='Sets alternate search string to use when searching case name')
parser.add_option('--file',dest='file_type',default='h0',help='file type to search for (default="h0")')
parser.add_option('--comp',dest='component',default='eam',help='model component history file to search for (default="eam")')
parser.add_option('--partial',action='store_true', dest='allow_partial_match', default=False,help='allow partial matches of input search strings')

(opts, args) = parser.parse_args()

# Set up terminal colors
class bcolor:
    HEADER    = '\033[95m'
    BLUE      = '\033[94m'
    GREEN     = '\033[92m'
    RED       = '\033[91m'
    WARN      = '\033[93m'
    FAIL      = '\033[91m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'

# workdir = os.getenv('MEMBERWORK')
# workdir = '/lustre/atlas/scratch/hannah6/' 
#=============================================================================================================
# arguments are used to provide a string to search case names for, like 'SP' or 'ZM' or a case number
#=============================================================================================================
# if len(sys.argv) < 2 :
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

top_dir = [ home+'/E3SM/scratch',
            home+'/E3SM/scratch2',
            home+'/E3SM/scratch_v3',
            home+'/E3SM/scratch-cori',
            home+'/E3SM/scratch_pm',
            home+'/E3SM/scratch_pm-cpu',
            home+'/E3SM/scratch_pm-gpu',
            '/pscratch/sd/w/whannah/E3SMv3_dev',
            home+'/E3SM/scratch-summit',
            home+'/E3SM/scratch-llnl1',
            home+'/E3SM/scratch-llnl2',
            home+'/SCREAM/scratch_pm-cpu',
            home+'/SCREAM/scratch_pm-gpu',
            home+'/SCREAM/scratch-summit',
          ]

# make sure list of top dir's don't end with "/"
for t,top_dir_tmp in enumerate(top_dir) :
    if top_dir_tmp[-1]=='/': top_dir[t] = top_dir[t][0:-1]

# dirs = glob.glob( top_dir[0]+'*/*' )

dirs = []
for top_dir_tmp in top_dir : 
    dirs = dirs + glob.glob(f'{top_dir_tmp}/*')

ndir = len(dirs)

out = ['' for n in range(ndir)]
cnt = 0


### specify string lengths for nice formatting
indent_len  = 40
xmlfile_len = 15
param_len   = 20
total_len   = indent_len + xmlfile_len + param_len

### use multiple lines for variables with long values
status_len_limit = 80

#=============================================================================================================
# Start looping through case directories
#=============================================================================================================


for tdir in dirs :
    case = tdir
    for top in top_dir: 
        case = case.replace(top+'/','')
    if ('E3SM' in case  
        or 'ACME' in case 
        or 'CLM_spinup' in case
        or 'ELM_spinup' in case
        or '.v3alpha' in case
        or 'v3.F2010' in case
        or 'INCITE' in case
        or opts.alt_search_str in case) and 'timing' not in case and 'old_' not in case :
        found = True
        
        if search_strings : 
            found = False
            for sub_string in search_strings :
                # if sub_string in case : found = True
                if opts.allow_partial_match:
                    if sub_string in case : found = True
                else:
                    if sub_string == case : found = True
        # check for "run" subdirectory
        if found :
            run_dirs = glob.glob( f'{tdir}/run' )
            if run_dirs==[]: found = False
        if found :
            #-------------------------------------------------------
            #-------------------------------------------------------
            comp = opts.component
            if 'E3SM.PI-CPL.v1.' in case: comp = 'cam'

            # cmd = f'ls  {tdir}/run/{case}.{comp}.{opts.file_type}.*'
            cmd = f'ls  {tdir}/run/*{opts.file_type}*'

            # print(cmd)
            proc = subprocess.Popen([cmd+' | tail -n '+str(opts.num_file)+' '], \
                                    stdout=subprocess.PIPE, shell=True, universal_newlines=True)
            (msg, err) = proc.communicate()

            ### strip the path off the filenames
            # file_list = msg.replace(home+'/E3SM/scratch/'+case+'/run/','    ')

            ### Pad each filename with leading spaces
            file_list = msg.replace(home,'    '+home)

            ### print the case name only on the first line
            # if pcnt==0 :
            #     out[cnt] = case.ljust(indent_len)
            # else:
            #     out[cnt] = out[cnt]+'\n'+' '.ljust(indent_len)
            out[cnt] = bcolor.BOLD + case.ljust(indent_len) + bcolor.ENDC + '\n'
            
            out[cnt] = out[cnt]+'\n'+file_list

            # #-------------------------------------------------------
            # # Loop through parameters
            # #-------------------------------------------------------
            # pcnt = 0
            # for param in param_list :

            #     proc = subprocess.Popen(['grep  '\''+param+'\''  '+tdir+'/*.xml '], stdout=subprocess.PIPE, shell=True)
            #     (msg, err) = proc.communicate()

            #     ### Parse out file name and status
            #     msg1 = msg.split(':')
            #     msg2 = msg.split('\'')
            #     xmlfile = msg1[0]
            #     status  = msg2[3]

            #     ### strip the path off the xml file
            #     xmlfile = xmlfile.replace(home+'/E3SM/Cases/'+case+'/','')
                
            #     ### Color the output to highlight special circumstances
            #     clr = ''
            #     if 'DEBUG'    in param and 'TRUE' in status : clr = bcolor.RED
            #     if 'CONTINUE' in param and 'TRUE' in status : clr = bcolor.GREEN
            #     status = status.replace('TRUE',clr+'TRUE'+bcolor.ENDC)
                
            #     # print the case name only on the first line
            #     if pcnt==0 :
            #         out[cnt] = case.ljust(indent_len)
            #     else:
            #         out[cnt] = out[cnt]+'\n'+' '.ljust(indent_len)



            #     out[cnt] = out[cnt]+'  '+xmlfile.ljust(xmlfile_len)      # print xml file name
            #     out[cnt] = out[cnt]+'  '+param.ljust(param_len)        # print parameter name

            #     if len(status)>status_len_limit and opts.indent_flag :
            #         ### for long straings like CAM_CONFIG_OPTS, break the status message into multiple lines and justify,
            #         ### split the status by word count and character length for better readability
            #         status_split = status.split()
            #         word_cnt = 0
            #         line_len = 0
            #         for word in status_split :
            #             ### first check if we should jump to the next line
            #             if (word_cnt==10) or (line_len+len(word))>(80):
            #                 out[cnt] = out[cnt]+'\n'+' '.ljust(total_len+4)
            #                 word_cnt = 0
            #                 line_len = 0
            #             ### now add the next part of the status
            #             out[cnt] = out[cnt]+'  '+word
            #             line_len = line_len + len(word)
            #             word_cnt = word_cnt + 1
            #     else :
            #         out[cnt] = out[cnt]+'  '+status             # print parameter value

            #     pcnt = pcnt+1
            #-------------------------------------------------------
            #-------------------------------------------------------
            cnt = cnt+1

### sort the cases alphbetically
out.sort()

print
for line in out : 
    if line!='' : print( line )


# for case in os.walk(top_dir) :
#   print(case)



#=============================================================================================================
#=============================================================================================================
