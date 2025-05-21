#!/usr/bin/env python3
#=============================================================================================================
#  Feb, 2018 - Walter Hannah - Lawrence Livermore National Lab
#=============================================================================================================
import sys, os, subprocess
home = os.getenv("HOME")

from optparse import OptionParser
parser = OptionParser()
(opts, args) = parser.parse_args()

#=============================================================================================================
# arguments are used to provide a string to search case names for, like "SP" or "ZM" or a case number
#=============================================================================================================
# if len(sys.argv) < 2 :
if len(args) < 1 :
    print
    print("ERROR: no search string provided!")
    print
    exit()


os.system(home+"/E3SM/chk.case.py  "+str(args[0]) )
os.system(home+"/E3SM/chk.files.py "+str(args[0])+" -n 3 ")
os.system(home+"/E3SM/chk.logs.py  "+str(args[0])+" -n 3 ")

#=============================================================================================================
#=============================================================================================================
