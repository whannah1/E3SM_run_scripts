#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
import sys, os, fileinput, glob, subprocess as sp
import chk_methods
home = os.getenv('HOME')
tclr = chk_methods.tclr
#---------------------------------------------------------------------------------------------------
from optparse import OptionParser
parser = OptionParser('./chk.files.py CASE [options]\n\nlist the latest files for a given case\nDefault is set to look for files matching *eam.h1*')
# parser.add_option('--no-indent',action='store_false', dest='indent_flag', default=True,help='do not indent long variables')
parser.add_option('-n',       dest='num_file',      default=5, type='int',  help='number of files to print for each case')
parser.add_option('--alt',    dest='alt_search',    default=None,           help='alternate search string to use when searching case name')
parser.add_option('--sub',    dest='sub',           default='run',          help='case subdirectory to search for output files')
parser.add_option('--file',   dest='file_type',     default='eam.h0',       help='file type to search for')
# parser.add_option('--comp',   dest='component',     default='eam',          help='model component history file to search for (default="eam")')
# parser.add_option('--cnt',    dest='print_cnt',     default=False, action='store_true',help='flag to print total file number')
parser.add_option('--partial',dest='allow_partial', default=False, action='store_true',help='allow partial matches of input search strings')
(opts, args) = parser.parse_args()
opts.print_cnt = True
#---------------------------------------------------------------------------------------------------
# arguments are used to provide a string to search case names for
if len(args) < 1 : exit('\nERROR: no search string provided!\n')

search_string_list = args


# specify string lengths for nice formatting
indent_len  = 40
xmlfile_len = 15
param_len   = 20
total_len   = indent_len + xmlfile_len + param_len

# use multiple lines for variables with long values
status_len_limit = 80
#---------------------------------------------------------------------------------------------------
# Specify what we want to see in the output 

scratch_path_list = chk_methods.get_scratch_path_list()

dirs = []
for scratch_path in scratch_path_list : 
    dirs = dirs + glob.glob(f'{scratch_path}/*')

ndir = len(dirs)

msg_list = [None]
cnt = 0

#---------------------------------------------------------------------------------------------------
# loop through case directories

if opts.alt_search is not None:
    case_search_list = [opts.alt_search]
else:
    case_search_list = []
    case_search_list.append('E3SM')
    case_search_list.append('v3.F2010')
    
case_avoid_list = []
case_avoid_list.append('timing')
case_avoid_list.append('old_')

for tdir in dirs :
    case = tdir
    for top in scratch_path_list: 
        case = case.replace(top+'/','')
    if      any(s     in case for s in case_search_list) \
        and all(a not in case for a in case_avoid_list):
        found = True
        
        if search_string_list : 
            found = False
            for search_string in search_string_list :
                if     opts.allow_partial and search_string in case : found = True
                if not opts.allow_partial and search_string == case : found = True
        if found and not os.path.exists(f'{tdir}/{opts.sub}'): found = False
        if found :
            file_list = glob.glob(f'{tdir}/{opts.sub}/*{opts.file_type}*')
            file_list.sort()

            # build the output message
            msg_tmp = ''
            msg_tmp += '\n'
            msg_tmp += tclr.BLD + case.ljust(indent_len) + tclr.END
            if opts.print_cnt:
                file_cnt = len(file_list)
                # msg_tmp += f' - number of files: {tclr.BLD}{file_cnt}{tclr.END}'
                msg_tmp += f'\n  number of files: {tclr.BLD}{file_cnt}{tclr.END}'

            if file_list!=[]:
                # limit list to last file specified by opts.num_file
                if len(file_list)>opts.num_file:
                    file_list = file_list[-1*opts.num_file:]
                # left-pad file names
                for f,ff in enumerate(file_list):
                    file_list[f] = ' '*4+file_list[f]
                # join the list into a string
                file_list_str = '\n'.join(file_list)
                
                msg_tmp += '\n'
                msg_tmp += file_list_str
            
            msg_list.append(msg_tmp)
            cnt = cnt+1

#---------------------------------------------------------------------------------------------------
# msg_list.sort()

print()
for msg in msg_list:
    print(msg)
#---------------------------------------------------------------------------------------------------
