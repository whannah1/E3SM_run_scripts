#!/usr/bin/env python
#==========================================================================================
#   This script runs simulations of ACME-SP
#
#    2017  Walter Hannah       Lawrence Livermore National Lab
#
# NOTES:    
#       ?
#==========================================================================================
#import datetime
import sys
import os
import numpy as np
home = os.getenv("HOME")
host = os.getenv("HOST")

if "edison" in host : host = "edison"
if "blogin" in host : host = "anvil"
if "titan"  in host : host = "titan"

#==========================================================================================
#==========================================================================================
newcase,config,build,copyinit,runsim = False,False,False,False,False

# newcase  = True
# config   = True
build    = True
# runsim   = True

case_num = "00"

res = "ne30"
cld = "ZM"     #  ZM / SP
exp = "CTL"    # CTL / EXP

cflag = "FALSE"                      # Don't forget to set this!!!! 

if cld=="ZM" :
    ndays = 365 #4*365
    resub = 0 #8 #4
if cld=="SP" :
    ndays = 73
    resub = 1*5-1 # [#years]*5-1

ndays = 1
resub = 0

case_name = "ACME_"+cld+"_"+exp+"_"+res+"_"+case_num

#==================================================================================================
#==================================================================================================
top_dir     = home+"/ACME/"
srcmod_dir  = top_dir+"mod_src/"
nmlmod_dir  = top_dir+"mod_nml/"

src_dir = "~/ACME/ACME_SRC/"

# "/global/cscratch1/sd/whannah"

scratch_dir = os.getenv("CSCRATCH","")
if scratch_dir=="" : 
    if host=="titan" : scratch_dir = "/lustre/atlas1/cli115/scratch/hannah6"

run_dir = scratch_dir+"/"+case_name+"/run"

#==================================================================================================
#==================================================================================================
os.system("cd "+top_dir)
case_dir  = top_dir+"Cases/"+case_name+"/"
cdcmd = "cd "+case_dir+" ; "
print
print "  case : "+case_name
print
#==================================================================================================
# Create new case
#==================================================================================================
if newcase == True:
    # if cld=="ZM" : 
        # if case_num == "00" : compset_opt = "-compset FC5AV1C "

    compset_opt = "-compset FC5AV1C-L "
    
    newcase_cmd = src_dir+"cime/scripts/create_newcase"
    cmd = newcase_cmd+" -case "+case_dir+" "+compset_opt+" -res "+res+"_"+res+" -mach "+host
    print cmd
    os.system(cmd)

#==================================================================================================
# Configure the case
#==================================================================================================
if config == True:
    #------------------------------------------------
    # run-time variables
    #------------------------------------------------
    if exp=="CTL" : 
        if case_num == "00" : start_date = "2000-01-01"
    # if exp=="EXP" : start_date = "2100-01-01"
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id RUN_STARTDATE  -val "+start_date)
    # os.system(cdcmd+"./xmlchange -file env_run.xml   -id CLM_CO2_TYPE   -val diagnostic")
    # os.system(cdcmd+"./xmlchange -file env_run.xml   -id CCSM_BGC       -val CO2A")
    #------------------------------------------------
    # Copy the custom namelist file
    #------------------------------------------------
    nml_file = ""
    nml_file = nmlmod_dir+"user_nl_cam.F."+exp+"."+case_num
    
    if not os.path.isfile(nml_file) :
        print "ERROR: CAM namelist file does not exist! ("+nml_file+")"
        exit()
    
    os.system("cp "+nml_file+"  "+case_dir+"user_nl_cam ")
    #------------------------------------------------
    # copy any modified source code (preserve permissions)
    #------------------------------------------------
    # if cld=="ZM" and case_num=="01" :
        # os.system("cp -rp "+srcmod_dir+"zm_conv_intr.no-CMT.F90  "+case_dir+"SourceMods/src.cam/zm_conv_intr.F90 ")
    #------------------------------------------------
    # configure the case
    #------------------------------------------------

    # os.system(cdcmd+"./xmlchange -file env_run.xml  DIN_LOC_ROOT='/global/cscratch1/sd/acmedata' ")
    # os.system(cdcmd+"./xmlchange -file env_run.xml   -id DIN_LOC_ROOT       -val '/global/cscratch1/sd/acmedata/inputdata' ")

    os.system(cdcmd+"./case.setup --clean")
    os.system(cdcmd+"./case.setup")
    
    #os.system(cdcmd+"./xmlchange -file env_run.xml     -id RUN_TYPE    -val startup")

#==================================================================================================
# Build the model
#==================================================================================================
if build == True:
    os.system(cdcmd+"./case.build --clean")
    #os.system(cdcmd+"cp "+srcmod_dir+"* ./SourceMods/src.cam/")    # copy the modified source code
    os.system(cdcmd+"./case.build")

#==================================================================================================
# Copy init data
#==================================================================================================
# if copyinit == True:
#     print 
#     if case_num=="01" : branch_data = "/glade/p/work/whannah/"+ref_case+"/"+ref_date+"-00000/* "
#     if case_num=="02" : branch_data = "/glade/p/work/whannah/"+ref_case+"/"+ref_date+"-00000/* "
#     os.system("cp "+branch_data+" "+run_dir+case_name+"/run")

#==================================================================================================
# Run the simulation
#==================================================================================================
if runsim == True:
    runfile = case_dir+case_name+".run"
    subfile = case_dir+case_name+".submit"
    
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_N       -val "+str(ndays)) 
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id RESUBMIT     -val "+str(resub))
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id CONTINUE_RUN -val "+cflag)
    #os.system(cdcmd+"./xmlchange -file env_run.xml   -id CONTINUE_RUN -val FALSE")
    
    # os.system("sed -i '/#BSUB -R \"select*/d'  "+runfile)
    # os.system("sed -i '/#BSUB -W/ c\#BSUB -W 1:00'  "+runfile)
    
    os.system(cdcmd+subfile)
    
    
#==================================================================================================
#==================================================================================================
# del case_dir

