#!/usr/bin/env python3
import sys, os, fileinput, re, subprocess as sp, glob
from optparse import OptionParser
#-------------------------------------------------------------------------------
# Set up terminal colors
#-------------------------------------------------------------------------------
class tcolor:
   ENDC    = '\033[0m';  BLACK  = '\033[30m'; RED   = '\033[31m'  
   GREEN   = '\033[32m'; YELLOW = '\033[33m'; BLUE  = '\033[34m'
   MAGENTA = '\033[35m'; CYAN   = '\033[36m'; WHITE = '\033[37m'
#-------------------------------------------------------------------------------
# command line options
#-------------------------------------------------------------------------------
parser = OptionParser()
parser.add_option('-n',dest='num_file',default=-1,help='number of files to print')
parser.add_option('--params', dest='params', default=None,help='Comma separated list of params')
(opts, args) = parser.parse_args()
#-------------------------------------------------------------------------------
# define list of cases
#-------------------------------------------------------------------------------

top_dir = os.getenv('HOME')+'/E3SM/Cases'
dirs = glob.glob( top_dir+'/*' )
ndir = len(dirs)
cases = []

indent = ' '*4

# arguments are used to provide a string to search case names
if len(args) < 1 :
   exit('\nERROR: no case names provided!\n')
else :
   search_strings = args

# loop over case directories
for tdir in dirs :
   case = tdir.replace(top_dir+'/','')
   found = True
   if search_strings : 
      found = False
      for sub_string in search_strings :
         if sub_string in case :
            found = True
   if found : 
      cases.append(case)
   else:
      continue

# sort the cases alphabetically
cases.sort()

#-------------------------------------------------------------------------------
# Loop through parameters and cases
#-------------------------------------------------------------------------------
for c,case in enumerate(cases):   
  print('-'*80)  
  print(tcolor.GREEN + f'{case}\n' + tcolor.ENDC)

  os.chdir(f'{top_dir}/{case}')
  
  cmd = './preview_run'
  # os.system(cmd)
  (msg, err) = sp.Popen(cmd, stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()

  for line in msg.split('\n'):
    print(indent+line)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
