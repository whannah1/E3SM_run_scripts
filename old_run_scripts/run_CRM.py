#!/usr/bin/env python
#===============================================================================================================================================================
#   This script runs the "standalone CRM" harness of ACME-SP created by Matt Norman (ORNL)
#
#    Jun, 2017  Walter Hannah       Lawrence Livermore National Lab
#
#===============================================================================================================================================================
import sys
import os
# import numpy as np
home = os.getenv("HOME")
host = os.getenv("HOST")

if "edison" in host : host = "edison"
if "blogin" in host : host = "anvil"
if "titan"  in host : host = "titan"

#===============================================================================================================================================================
#===============================================================================================================================================================
newcase,config,build,copyinit,runsim,debug,clean,test_run,mk_nml = False,False,False,False,False,False,False,False,False

newcase  = True
config   = True
clean    = True
build    = True
# mk_nml   = True
runsim   = True

verbose = True 		# print the commands
debug   = True 		# Don't actually run the commands


case_num = "00"

cld = "SP1"    # SP1 / SP2
# mod = "ATM"    # CPL / ATM  
res = "ne16"   # ne30 / ne16 / 0.9x1.25

cflag = "FALSE"                      # Don't forget to set this!!!! 
# cflag = "TRUE"

if "ZM" in cld :
    ndays = 1 #4*365
    resub = 0 #8 #4
if "SP" in cld :
    ndays = 73
    resub = 1*5-1 # [#years]*5-1

crm_ny = 32
crm_nx = 1


crmdim = "_"+str(crm_ny)+"x"+str(crm_nx) 

mod_str = ""
# mod_str = "_4km"
# mod_str = "_0.5km"


# case_name = "CRM_"+cld+"_"+res+crmdim+mod_str+"_"+case_num
case_name = "CRM_"+cld+"_"+case_num

# input_file = "/ccs/home/imn/crm_in.nc"
# input_file = "/ccs/home/hannah6/ACME/CRM_Cases/crm_in.nc"
# input_file = "/lustre/atlas1/cli115/scratch/hannah6/CRM/crm_in.nc"

if cld == "SP1" : input_file = "/lustre/atlas1/cli115/scratch/hannah6/CRM/crm_in_1mom.nc"
if cld == "SP2" : input_file = "/lustre/atlas1/cli115/scratch/hannah6/CRM/crm_in_2mom.nc"


output_dir = "/lustre/atlas1/cli115/scratch/hannah6/CRM/"+case_name

case_root = "/lustre/atlas1/cli115/scratch/hannah6/CRM/"+case_name

# build_root = "/ccs/home/hannah6/ACME/CRM_Cases/"+case_name
build_root = case_root+"/bld"



#===============================================================================================================================================================
#===============================================================================================================================================================
top_dir     = home+"/ACME/"
srcmod_dir  = top_dir+"mod_src/"
nmlmod_dir  = top_dir+"mod_nml/"

src_dir = home+"/ACME/ACME_SRC"
# src_dir = home+"/ACME/ACME-master"

crm_dir = src_dir+"/components/cam/src/physics/crm"

scratch_dir = os.getenv("CSCRATCH","")
if scratch_dir=="" : 
    if host=="titan" : scratch_dir = "/lustre/atlas1/cli115/scratch/hannah6"

run_dir = scratch_dir+"/"+case_name+"/run"

#===================================================================================
#===================================================================================
os.system("cd "+top_dir)
case_dir  = top_dir+"Cases/"+case_name 
cdcmd = "cd "+case_dir+" ; "
print
print "  case : "+case_name
print

if not os.path.exists(build_root):
    os.makedirs(build_root)
#===============================================================================================================================================================
#===============================================================================================================================================================
#===============================================================================================================================================================
#===============================================================================================================================================================

cdcmd = "cd "+crm_dir+"/standalone ; "

# cmd = "cd "+crm_dir+"/standalone"
# if verbose : print("\n"+cmd+"\n")
# os.system(cmd)

# cmd = "source "+src_dir+"/components/cam/src/physics/crm/standalone/environments/env_titan_pgi.sh"
# cmd = cdcmd+"source environments/env_titan_pgi.sh"
cmd = "source "+crm_dir+"/standalone/environments/env_titan_pgi.sh"
if verbose : print("\n"+cmd+"\n")
if not debug : os.system(cmd)

cdcmd = "cd "+crm_dir+"/standalone/utils ; "

# cmd = "cd utils"
# if verbose : print("\n"+cmd+"\n")
# os.system(cmd)

cmd = cdcmd+"./setup_from_file.sh -crm_root "+crm_dir+" -build_root "+build_root+" -file "+input_file
if verbose : print("\n"+cmd+"\n")
if not debug : os.system(cmd)

cdcmd = "cd "+build_root+" ; "

# cmd = "cd "+build_root
# if verbose : print("\n"+cmd+"\n")
# os.system(cmd)

# cmd = cdcmd+"make -j32 > bld.out "
cmd = cdcmd+"make -j32 "
if verbose : print("\n"+cmd+"\n")
if not debug : os.system(cmd)

cdcmd = "cd "+case_root+" ; "

cmd = cdcmd+"aprun -n 16 "+build_root+"/crm_standalone "+input_file+"  "+output_dir+"/"+case_name
if verbose : print("\n"+cmd+"\n")
if not debug : os.system(cmd)



# ./collect_files.sh -prefix [/path/]output_prefix

# ./compute_diffs.sh -f1 standalone_output_1.nc -f2 standalone_output_2.nc

# vim timing_stats
    
    
#==================================================================================================
#==================================================================================================