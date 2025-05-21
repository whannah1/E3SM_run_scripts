#!/usr/bin/env python3
#=============================================================================================================
#  May, 2018 - Walter Hannah - Lawrence Livermore National Lab
#  This script checks the status of the latest regression test
#=============================================================================================================
import sys, os, fileinput, glob, subprocess

# from optparse import OptionParser
# parser = OptionParser()
# # parser.add_option('--no-indent',action='store_false', dest='indent_flag', default=True,help='do not indent long variables')
# parser.add_option('-n',dest='num_test',default=1,help='sets number of tests to search for. Only considers tests newer than newest baseline.')
# parser.add_option('-b',action='store_true', dest='show_base', default=False,help='show recent baseline status instead of test')
# parser.add_option('-t',action='store_true', dest='truncate_flag', default=False,help='truncate output for small screens')
# (opts, args) = parser.parse_args()
# num_test = int(opts.num_test)

# Set up terminal colors
class bcolor:
    ENDC     = '\033[0m'
    BLACK    = '\033[30m'
    RED      = '\033[31m'
    GREEN    = '\033[32m'
    YELLOW   = '\033[33m'
    BLUE     = '\033[34m'
    MAGENTA  = '\033[35m'
    CYAN     = '\033[36m'
    WHITE    = '\033[37m'

#=============================================================================================================
#=============================================================================================================

top_dir = os.getenv('HOME')+'/E3SM/'

proc = subprocess.Popen(['ls -1d '+top_dir+'E3SM_SRC* '], \
                        stdout=subprocess.PIPE, \
                        shell=True, universal_newlines=True)
(msg, err) = proc.communicate()
src_dirs = msg.rstrip().split('\n')

for src in src_dirs :
    os.chdir( src )

    proc = subprocess.Popen(['git branch --list -vv '],  \
                            stdout=subprocess.PIPE,     \
                            shell=True, universal_newlines=True)
    (msg, err) = proc.communicate()
    msg = msg.rstrip().split('\n')

    #--------------------------------------------
    # Only print current branch
    #--------------------------------------------
    # for line in msg : 
    #     if  '*' in line :
    #         line = line.replace('* ','')
    #         line1 = line.split(' ')[0]
    #         line2 = line.replace(line1,'').lstrip()
    #         status = src.replace(top_dir,'') 
    #         status = status +'  >  '+ line1.ljust(30)
    #         status = status +' '+ line2
    #         print( status )

    #--------------------------------------------
    # Print all branches
    #--------------------------------------------
    print('\n' + bcolor.MAGENTA + src.replace(top_dir,'') + bcolor.ENDC + '\n')
    for line in msg : 
        if  '*' in line : line = bcolor.GREEN + line + bcolor.ENDC
        print('  '+line)


#=============================================================================================================
#=============================================================================================================
