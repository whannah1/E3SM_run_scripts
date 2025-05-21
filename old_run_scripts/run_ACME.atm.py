#!/usr/bin/env python
#==========================================================================================
#   This script runs atmosphere only simulations of ACME version ????
#
#    Jan, 2017  Walter Hannah       Lawrence Livermore National Lab
#
# NOTES:    
#       ?
#==========================================================================================
import sys
import os
home = os.getenv("HOME")
#==========================================================================================
#==========================================================================================
newcase,config,build,copyinit,runsim = False,False,False,False,False

newcase  = True
# config   = True
# build    = True
# runsim   = True

case_num = "00"

res = "ne30"
cld = "SP"     #  ZM / SP
exp = "CTL"    # CTL / EXP

cflag = "FALSE"                      # Don't forget to set this!!!! 

if cld=="ZM" :
    ndays = 1 #4*365
    resub = 0 #8 #4
if cld=="SP" :
    ndays = 73
    resub = 1*5-1 # [#years]*5-1

case_name = "ACME_"+cld+"_"+exp+"_"+res+"_"+case_num

#===================================================================================
#===================================================================================
top_dir     = home+"/ACME/"
srcmod_dir  = top_dir+"mod_src/"
nmlmod_dir  = top_dir+"mod_nml/"

# run_dir = "/glade/scratch/whannah/"
src_dir = "~/ACME/ACME_SRC/acme-master/"

#===================================================================================
#===================================================================================
os.system("cd "+top_dir)
case_dir  = top_dir+"Cases/"+case_name+"/"
cdcmd = "cd "+case_dir+" ; "
print
print "  case : "+case_name
print
#--------------------------
# Create new case
#--------------------------
if newcase == True:
    if cld=="ZM" : 
        if case_num == "00" : compset_opt = "-compset FC5AV1C-L "
    
    newcase_cmd = src_dir+"cime/scripts/create_newcase"
    cmd = newcase_cmd+" -case "+case_dir+" "+compset_opt+" -res "+res+"_"+res+" -mach  anvil "
    print cmd
    os.system(cmd)
#--------------------------
# Configure the case
#--------------------------
if config == True:
    # set run-time variables
    if exp=="CTL" : 
        if case_num == "00" : start_date = "2000-01-01"
    # if exp=="EXP" : start_date = "2100-01-01"
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id RUN_STARTDATE  -val "+start_date)
    # os.system(cdcmd+"./xmlchange -file env_run.xml   -id CLM_CO2_TYPE   -val diagnostic")
    # os.system(cdcmd+"./xmlchange -file env_run.xml   -id CCSM_BGC       -val CO2A")
    #------------------------------------------------
    # Copy the custom namelist file
    #------------------------------------------------
    # nml_file = ""
    nml_file = nmlmod_dir+"user_nl_cam.F."+exp+"."+case_num
    
    if not os.path.isfile(nml_file) :
        print "ERROR: Modified ATM namelist file does not exist! ("+nml_file+")"
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
    os.system(cdcmd+"./case.setup -clean")
    os.system(cdcmd+"./case.setup")
    
    #os.system(cdcmd+"./xmlchange -file env_run.xml     -id RUN_TYPE    -val startup")
#--------------------------
# Build the model
#--------------------------
if build == True:
    #os.system(cdcmd+"cp "+srcmod_dir+"* ./SourceMods/src.cam/")    # copy the modified source code
    os.system(cdcmd+"./case.build")                  # Clean previous build    
#--------------------------
# Copy init data
#--------------------------
# if copyinit == True:
#     print 
#     if case_num=="01" : branch_data = "/glade/p/work/whannah/"+ref_case+"/"+ref_date+"-00000/* "
#     if case_num=="02" : branch_data = "/glade/p/work/whannah/"+ref_case+"/"+ref_date+"-00000/* "
#     os.system("cp "+branch_data+" "+run_dir+case_name+"/run")
#--------------------------
# Run the simulation
#--------------------------
if runsim == True:
    runfile = case_dir+"case.run"
    subfile = case_dir+"case.submit"
    
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_N       -val "+str(ndays)) 
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id RESUBMIT     -val "+str(resub))
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id CONTINUE_RUN -val "+cflag)
    #os.system(cdcmd+"./xmlchange -file env_run.xml   -id CONTINUE_RUN -val FALSE")
    
    #os.system("sed -i '/#BSUB -R \"select*/d'  "+runfile)
    #os.system("sed -i '/#BSUB -W/ c\#BSUB -W 1:00'  "+runfile)
    
    os.system(cdcmd+subfile)
    
    
#--------------------------
#--------------------------
del case_dir

