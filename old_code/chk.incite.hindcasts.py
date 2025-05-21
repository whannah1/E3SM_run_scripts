#!/usr/bin/env python3
#=============================================================================================================
#  Nov, 2017 - Walter Hannah - Lawrence Livermore National Lab
#  This script checks the output files of current E3SM cases (i.e. debug mode, compset, misc flags, etc.)
#=============================================================================================================
import sys, os, fileinput, glob, subprocess as sp
home = os.getenv('HOME')

from optparse import OptionParser
parser = OptionParser()

parser.add_option('--no-indent',action='store_false', dest='indent_flag', default=True,help='do not indent long variables')
parser.add_option('-n',dest='num_file',default=5,help='sets number of files to print')
parser.add_option('--alt',dest='alt_search_str',default='E3SM',help='Sets alternate search string to use when searching case name')
parser.add_option('--file',dest='file_type',default='h1',help='file type to search for')
parser.add_option('--comp',dest='component',default='eam',help='model component history file to search for')

(opts, args) = parser.parse_args()

# Set up terminal colors
class tcolor: 
    ENDC,RED,GREEN,YELLOW,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m'
    BLUE      = '\033[94m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'

search_strings = 'INCITE2020.HC'

#=============================================================================================================
# Specify what we want to see in the output 
#=============================================================================================================

top_dir = [ home+'/E3SM/scratch' ]

dirs = glob.glob( top_dir[0]+'/*' )
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
max_case_len = 0
for tdir in dirs :
    case = tdir
    for top in top_dir: case = case.replace(top+'/','')
    if 'INCITE2020.HC' in case :
        if len(case)>max_case_len : max_case_len = len(case)

for g in range(2):
    out_msg = []
    for tdir in dirs :
        case = tdir
        for top in top_dir: case = case.replace(top+'/','')
        if 'INCITE2020.HC' in case :

            if g==0 and 'BVT'     in case: continue
            if g==1 and 'BVT' not in case: continue

            hist_path = f'{tdir}/run'
            rgrd_path = f'{tdir}/data_remap_180x360'
            
            hist_files = glob.glob(f'{hist_path}/*eam.h1*')
            num_hist = len(hist_files)

            if os.path.exists(rgrd_path):
                rgrd_files = glob.glob(f'{rgrd_path}/*eam.h1*')
                num_rgrd = len(rgrd_files)
            else:
                num_rgrd = 0

            msg = f'{case:{max_case_len}}'
            hmsg = f'# hist : {num_hist:4}'
            rmsg = f'# regridded : {num_rgrd:4}'

            #-------------------------------------------------------
            # add color
            #-------------------------------------------------------
            # if '32x1'  in msg: msg = tcolor.GREEN  + msg + tcolor.ENDC
            if '32x32' in msg: msg = tcolor.BOLD  + msg + tcolor.ENDC

            if 'L_50'  in msg: msg = tcolor.MAGENTA + msg + tcolor.ENDC
            if 'L_125' in msg: msg = tcolor.CYAN    + msg + tcolor.ENDC
            if 'L_250' in msg: msg = tcolor.BLUE    + msg + tcolor.ENDC

            full_hist = num_hist==6
            part_hist = num_hist>0 and num_hist<6
            if full_hist: hmsg = tcolor.GREEN  + hmsg + tcolor.ENDC
            if part_hist: hmsg = tcolor.YELLOW + hmsg + tcolor.ENDC

            if part_hist and num_rgrd==num_hist: rmsg = tcolor.YELLOW + rmsg + tcolor.ENDC
            if full_hist and num_rgrd==num_hist: rmsg = tcolor.GREEN + rmsg + tcolor.ENDC
            if full_hist and num_rgrd <num_hist: rmsg = tcolor.RED   + rmsg + tcolor.ENDC

            #-------------------------------------------------------
            # combine
            #-------------------------------------------------------
            out_msg.append(f'{msg}    {hmsg}    {rmsg}')

            #-------------------------------------------------------
            #-------------------------------------------------------
            cnt = cnt+1

    ### sort the cases alphbetically
    out_msg.sort()

    print()
    for line in out_msg : 
        if line!='' : print( line )



#=============================================================================================================
#=============================================================================================================