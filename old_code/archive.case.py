#!/usr/bin/env python
#======================================================================================================================
#   Feb, 2018 - Walter Hannah - Lawrence Livermore National Lab
#   This script copys data from project space to an archive system (e.g. HPSS)
#======================================================================================================================
import sys
import os
import datetime
home = os.getenv("HOME")
host = os.getenv("HOST")

from optparse import OptionParser
parser = OptionParser()
# parser.add_option("--old",action="store_true", dest="use_old_scratch", default=False,help="switch to alternate source scratch directory")
(opts, args) = parser.parse_args()

if "edison" in host : host = "edison"
if "blogin" in host : host = "anvil"
if "titan"  in host : host = "titan"

scratch_dir = ""
project_dir = ""
if host == "titan"  : 
    project_dir = "/lustre/atlas/proj-shared/cli115/hannah6/E3SM/"


if project_dir=="" :
    print("ERROR: project directory not set!")
    exit()
#======================================================================================================================
#======================================================================================================================
do_h0, do_h1, do_h2, do_rest, overwrite = False, False, False, False, False

if len(sys.argv) < 2 :
    cases = ["default"]
    print("ERROR: no case name provided!")
    exit()
    
else :
    cases = sys.argv[1:]

#======================================================================================================================
#======================================================================================================================
for case in cases :
    print 
    #----------------------------------------------------
    # Generate new timestamp
    #----------------------------------------------------
    now = datetime.datetime.utcnow()
    timestamp = '{:%Y-%m-%d_%H%M%S}'.format(now)
    print("\n  time stamp: "+timestamp+"\n")

    #----------------------------------------------------
    # specify directory to archive 
    # (files and sub-dirs are archived recursively)
    #----------------------------------------------------
    # src_dir = project_dir+case+"/*"
    src_dir = project_dir+case

    #----------------------------------------------------
    # submit htar command
    #----------------------------------------------------
    cmd = "htar -cv -f "+case+"."+timestamp+".tar "+src_dir
    print(cmd)
    os.system(cmd)
    
    #----------------------------------------------------
    #----------------------------------------------------
    
    print("")
    print("-------------------------------------------------------------------------------------------")

#======================================================================================================================
#======================================================================================================================
