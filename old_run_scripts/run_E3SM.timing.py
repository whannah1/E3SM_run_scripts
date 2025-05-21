#!/usr/bin/env python
#===============================================================================================================================================================
#   This script runs atmosphere only simulations of E3SM
#
#    Jan, 2017  Walter Hannah       Lawrence Livermore National Lab
#
#===============================================================================================================================================================
import sys
import os
import getopt
from optparse import OptionParser

# import numpy as np
home = os.getenv("HOME")
host = os.getenv("HOST")

workdir = os.getenv("MEMBERWORK")

if "edison" in host : host = "edison"
if "blogin" in host : host = "anvil"
if "titan"  in host : host = "titan"

parser = OptionParser()

parser.add_option("-n", dest="ntask",help="sets NTASKS_ATM")
parser.add_option("-g", dest="dycor",help="sets the dycore grid")
parser.add_option("-c", dest="cld"  ,help="Cloud option - SP2 / SP1 / ZM")
parser.add_option("-f", dest="nfac" ,help="factor to control processors dedicated to dycore")
parser.add_option("--UM5",action="store_true", dest="UM5_flag", default=False,help="Switch to UM5 advection")
parser.add_option("--LB2",action="store_true", dest="LB2_flag", default=False,help="enable load_balance = 2 option")
parser.add_option("--master",action="store_true", dest="master_flag", default=False,help="Switch to current master branch")
# parser.add_option("--rrtmg",action="store_true", dest="rrtmg_flag", default=False,help="Switch to radiation to rrtmg (only SP1)")

parser.add_option("--crm_nx"    , dest="crm_nx"    , default=32,help="sets crm_nx")
parser.add_option("--crm_ny"    , dest="crm_ny"    , default=1, help="sets crm_ny")
parser.add_option("--crm_nx_rad", dest="crm_nx_rad", default=32,help="sets crm_nx_rad")

parser.add_option("-u", dest="user" ,help="specify a specific user")

(opts, args) = parser.parse_args()

# ensemble_mode = True
# if opts.ntask==None :
#     ensemble_mode = False
# else:
    
case_num = opts.ntask  if opts.ntask!=None else exit("ERROR: missing ntask argument! (-n) ")
res      = opts.dycor  if opts.dycor!=None else exit("ERROR: missing dycor grid argument! (-g) ")
cld      = opts.cld    if opts.cld  !=None else exit("ERROR: missing cld argument! (-c) ")
nfac     = opts.nfac   if opts.nfac !=None else exit("ERROR: missing nfac argument! (-f) ")

crm_nx = opts.crm_nx
crm_ny = opts.crm_ny

crm_nx_rad = opts.crm_nx_rad

#===============================================================================================================================================================
#===============================================================================================================================================================
newcase,config,build,copyinit,runsim,debug,clean,test_run = False,False,False,False,False,False,False,False

newcase  = True
config   = True
clean    = True
build    = True
runsim   = True

#==================================================
#==================================================
# if not ensemble_mode :
#     res = "ne120"
#     cld = "ZM"
#     # nf  = 1
#     nfac = 4

#     crm_nx = 32
#     crm_ny = 1

#     crm_nx_rad = crm_nx
#     # crm_nx_rad = 8
#     # crm_nx_rad = 1

#     case_num = "21600"

#==================================================
#==================================================

cflag = "FALSE"     # continue flag - leave as False for timing runs

ndays = 5
resub = 0

if cld=="ZM" : ndays = 30
if cld=="ZM" and res=="ne4"   : ndays = 60
if cld=="ZM" and res=="ne120" : ndays = 5

crmdim  = ""
mod_str = ""
if "SP" in cld :
    crmdim = "_"+str(crm_nx)+"x"+str(crm_ny) 
    # crmdim = "_"+str(crm_nx)+"x"+str(crm_ny)+"_nr"+str(crm_nx_rad)
    mod_str = mod_str = "_1km"
    # if crm_nx==32  : mod_str = mod_str = "_2km"
    # if crm_nx==64  : mod_str = mod_str = "_1km"
    # if crm_nx==128 : mod_str = mod_str = "_0.5km"

if opts.master_flag : mod_str = mod_str+"_master"
if opts.UM5_flag    : mod_str = mod_str+"_UM5" 
if opts.LB2_flag    : mod_str = mod_str+"_LB2"  
# if opts.rrtmg_flag  : mod_str = mod_str+"_rrtmg"  

case_name = "E3SM_timing2_"+res+crmdim+"_"+cld+mod_str+"_f"+str(nfac)+"_"+str(case_num)


#===============================================================================================================================================================
#===============================================================================================================================================================
print
print "  case : "+case_name
print

acct = "cli115"
# acct = "csc249"

top_dir     = home+"/E3SM/"
srcmod_dir  = top_dir+"mod_src/"
nmlmod_dir  = top_dir+"mod_nml/"

src_dir = "~/E3SM/E3SM_SRC_master"
# switch to alternate code base if the case number is negative
# if "-" in case_num : src_dir = "~/E3SM/E3SM-master"
if opts.master_flag : src_dir = "~/E3SM/E3SM-master"

scratch_dir = os.getenv("CSCRATCH","")
if scratch_dir=="" : 
    if host=="titan" : 
        if acct == "cli115" : 
            scratch_dir = "/lustre/atlas1/"+acct+"/scratch/hannah6/"
        else : 
            scratch_dir = "/lustre/atlas/scratch/hannah6/"+acct+"/"

run_dir = scratch_dir+"/"+case_name+"/run"

init_dir = "/lustre/atlas1/cli115/scratch/hannah6/init_files/"
# init_dir = "/ccs/home/hannah6/E3SM/init_files/"

if res=="ne4"   and int(nfac)==1 : num_dyn = 96
if res=="ne16"  and int(nfac)==1 : num_dyn = 1536
if res=="ne30"  and int(nfac)==1 : num_dyn = 5400
if res=="ne120" and int(nfac)==1 : num_dyn = 86400

if res=="ne4"   and int(nfac)==4 : num_dyn = 24
if res=="ne16"  and int(nfac)==4 : num_dyn = 384
if res=="ne30"  and int(nfac)==4 : num_dyn = 1350
if res=="ne120" and int(nfac)==4 : num_dyn = 21600

if int(case_num) < num_dyn : num_dyn = int(case_num)

#===================================================================================
#===================================================================================
os.system("cd "+top_dir)
case_dir  = top_dir+"Cases/"+case_name 
cdcmd = "cd "+case_dir+" ; "
#===============================================================================================================================================================
#===============================================================================================================================================================
# Create new case
#===============================================================================================================================================================
#===============================================================================================================================================================
if newcase == True:

    if host=="titan" and acct=="csc249" : os.system("echo '"+acct+"' > "+home+"/.cesm_proj")         # temporarily change project on titan

    compset_opt = "-compset FC5AV1C-L "
    # compset_opt = "-compset FC5AV1C-04P2 "

    if opts.master_flag : compset_opt = "-compset FC5AV1C-04P2 "

    newcase_cmd = src_dir+"/cime/scripts/create_newcase"
    cmd = newcase_cmd+" -case "+case_dir+" "+compset_opt+" -res "+res+"_"+res+" -mach  "+host
    print cmd
    os.system(cmd)

    if host=="titan" and acct=="csc249" : os.system("echo 'CSC249ADSE15' > "+home+"/.cesm_proj")       # change project name back


case_dir = case_dir+"/"

#===============================================================================================================================================================
#===============================================================================================================================================================
# Configure the case
#===============================================================================================================================================================
#===============================================================================================================================================================
if config == True:
    #------------------------------------------------
    # set vertical levels
    #------------------------------------------------
    nlev_gcm = 72
    
    crm_adv = "MPDATA"

    if opts.UM5_flag : crm_adv = "UM5"

    crm_dt = 5
    crm_dx = 1000
    # crm_nx = 32
    # crm_ny = 1

    if mod_str == "_2km":
        crm_dt = 10
        crm_dx = 2000
    if mod_str == "_0.5km":
        crm_dt = 5
        crm_dx = 500

    nlev_crm = 58

    if cld=="SP1-old" :
        nlev_gcm = 26
        nlev_crm = 24
        crm_dx = 4000
        crm_dt = 20

    if cld=="SP2-old" : 
        nlev_gcm = 30
        nlev_crm = 28
        crm_dx = 4000
        crm_dt = 20

    #------------------------------------------------
    # set CAM_CONFIG_OPTS
    #------------------------------------------------
    # cam_opt = "-rad rrtmg -phys cam5 -nlev "+str(nlev_gcm)+"  -clubb_sgs -microphys mg2 -chem trop_mam3 -rain_evap_to_coarse_aero -bc_dep_to_snow_updates"     # this is the default for non-SP runs

    if cld=="ZM" :
        cam_opt = " -rad rrtmg -nlev "+str(nlev_gcm)+"  -clubb_sgs -microphys mg2 "

        chem_opt = " -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates "

        cpp_opt = ""
        # cpp_opt = " -cppdefs ' -DWH_MPI_TEST' "
        
        if opts.master_flag : cam_opt  = cam_opt+" -phys cam5 "
        # if opts.master_flag : chem_opt = ""
        # if opts.master_flag : cpp_opt  = ""
            
        cam_opt = cam_opt+chem_opt+cpp_opt #+" ' "

    if "SP" in cld :
        
        cam_opt = " -use_SPCAM  -rad rrtmg  -nlev "+str(nlev_gcm)+"  -crm_nz "+str(nlev_crm)+" -crm_adv "+crm_adv+" "\
                 +" -crm_nx "+str(crm_nx)+" -crm_ny "+str(crm_ny)+" -crm_dx "+str(crm_dx)+" -crm_dt "+str(crm_dt)

        # 1-moment microphysics
        if cld=="SP1" : cam_opt = cam_opt + " -SPCAM_microp_scheme sam1mom   " 
            
        # 2-moment microphysics
        if cld=="SP2" : cam_opt = cam_opt + " -SPCAM_microp_scheme m2005  " 


        #-------------------------------
        #-------------------------------
        
        # Use mg2 since mg1 isn't supported anymore
        cam_opt = cam_opt + " -microphys mg2 "

        # always reduce rad columns by factor of 8 (new default)
        cam_opt = cam_opt+" -crm_nx_rad 8 -crm_ny_rad 1 "

        # use the same chem and aerosol options for SP1 and SP2
        chem_opt = " -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates "

        # set CPP variables
        cpp_opt = "-cppdefs ' -DSP_DIR_NS  -DSP_TK_LIM  "

        #-------------------------------
        # Old configuration
        #-------------------------------

        if cld=="SP1-old" : 
            cam_opt = " -use_SPCAM  -rad camrt  -nlev "+str(nlev_gcm)+"  -crm_nz "+str(nlev_crm)+" -crm_adv "+crm_adv+" "\
                     +" -crm_nx "+str(crm_nx)+" -crm_ny "+str(crm_ny)+" -crm_dx "+str(crm_dx)+" -crm_dt "+str(crm_dt)            
            cam_opt = cam_opt + " -SPCAM_microp_scheme sam1mom   " 
            chem_opt = " -chem none "
            cpp_opt = "-cppdefs ' -DSP_DIR_NS  "

        if cld=="SP2-old" :
            cam_opt = " -use_SPCAM  -rad rrtmg  -nlev "+str(nlev_gcm)+"  -crm_nz "+str(nlev_crm)+" -crm_adv "+crm_adv+" "\
                     +" -crm_nx "+str(crm_nx)+" -crm_ny "+str(crm_ny)+" -crm_dx "+str(crm_dx)+" -crm_dt "+str(crm_dt)            
            cam_opt = cam_opt + " -SPCAM_microp_scheme m2005  " 
            chem_opt = " -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates "
            cpp_opt = "-cppdefs ' -DSP_DIR_NS  "

        #-------------------------------
        #-------------------------------

        cam_opt = cam_opt+chem_opt+cpp_opt+" ' "


    print("------------------------------------------------------------")
    CMD = cdcmd+"./xmlchange --file env_build.xml --id CAM_CONFIG_OPTS --val \""+cam_opt+"\""
    print(CMD)
    os.system(CMD)
    print("------------------------------------------------------------")

    #------------------------------------------------
    # for FV runs we need to set this here
    # otherwise it will complain about not having a default ncdata
    #------------------------------------------------
    if res=="1.9x2.5" :
        nfile = case_dir+"user_nl_cam"
        file = open(nfile,'w') 
        file.write(" ncdata  = '"+init_dir+"hp_built_for_wh_1.9x2.5_L72_20081014_12Z_ECMWF.cam2.i.2008-10-14-43200_r2.nc' \n") 
        file.close() 
    #------------------------------------------------
    # set run-time variables
    #------------------------------------------------
    start_date = "2000-01-01"
    
    os.system(cdcmd+"./xmlchange --file env_run.xml   --id RUN_STARTDATE  --val "+start_date)

    if host=="titan" :
        # if acct != "cli115" : os.system(cdcmd+"./xmlchange --file env_run.xml --id RUNDIR  --val "+workdir+"/"+acct+"/"+case_name+"/run ")
        # os.system(cdcmd+"./xmlchange --file env_run.xml --id RUNDIR  --val "+workdir+"/"+acct_dir+"/"+case_name+"/run ")
        if acct == "cli115" : os.system(cdcmd+"./xmlchange --file env_run.xml --id RUNDIR  --val /lustre/atlas1/cli115/scratch/hannah6/"+case_name+"/run ")
        if acct == "csc249" : os.system(cdcmd+"./xmlchange --file env_run.xml --id RUNDIR  --val /lustre/atlas/scratch/hannah6/csc249/" +case_name+"/run ")
        

    if host=="anvil" :
        scratch_root_dir   = "/lcrc/group/E3SM/whannah/E3SM_simulations/"
        short_term_archive = "/lcrc/group/E3SM/whannah/archive/"+case_name
        
        os.system(cdcmd+"./xmlchange --file env_run.xml --id DOUT_S_ROOT --val "+short_term_archive)
        os.system(cdcmd+"./xmlchange --file env_run.xml --id EXEROOT --val "+scratch_root_dir+case_name+"/bld")
        os.system(cdcmd+"./xmlchange --file env_run.xml --id RUNDIR  --val "+scratch_root_dir+case_name+"/run")
        # os.system(cdcmd+"./xmlchange --file env_run.xml --id CAM_NML_USE_CASE  --val 2000_cam5_av1c-SP1")

    if " camrt " in cam_opt :
        os.system(cdcmd+"./xmlchange --file env_run.xml --id CAM_NML_USE_CASE  --val 2000_cam5_av1c-SP1_no-linoz")

    #------------------------------
    # Change processor count
    #------------------------------
    # if res=="ne4" :
    #     os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val 64 ")
    # if res=="ne16" :
    #     # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val 256 ")
    #     os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val 128 ")

    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val "+case_num+" ")

    # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_LND -val "+case_num+" ")
    # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ICE -val "+case_num+" ")
    # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_OCN -val "+case_num+" ")
    # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_CPL -val "+case_num+" ")
    # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_GLC -val "+case_num+" ")
    # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_RTM -val "+case_num+" ")
    # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_WAV -val "+case_num+" ")

    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_LND -val "+str(num_dyn)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ICE -val "+str(num_dyn)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_OCN -val "+str(num_dyn)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_CPL -val "+str(num_dyn)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_GLC -val "+str(num_dyn)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_RTM -val "+str(num_dyn)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ROF -val "+str(num_dyn)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_WAV -val "+str(num_dyn)+" ")

    ### This might be needed for ne120
    if res=="ne120" and int(case_num) >= 21600 :
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_ATM -val 1 ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_OCN -val 1 ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_LND -val 1 ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_CPL -val 1 ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_GLC -val 1 ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_ICE -val 1 ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_ROF -val 1 ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_RTM -val 1 ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_WAV -val 1 ")
        
    #------------------------------------------------
    # configure the case
    #------------------------------------------------

    if os.path.isfile(case_dir+"case.setup") :
        if clean : os.system(cdcmd+"./case.setup --clean")
        os.system(cdcmd+"./case.setup")
    else :
        os.system(cdcmd+"./cesm_setup")     # older versions
    
    #os.system(cdcmd+"./xmlchange -file env_run.xml     -id RUN_TYPE    -val startup")

#===============================================================================================================================================================
#===============================================================================================================================================================
# Build the model
#===============================================================================================================================================================
#===============================================================================================================================================================
if build == True:

    # os.system(cdcmd+"./xmlchange -file env_build.xml   -id CESMSCRATCHROOT   -val $MEMBERWORK/cli115")
    # os.system(cdcmd+"./xmlchange -file env_build.xml   -id CIME_OUTPUT_ROOT  -val $MEMBERWORK/cli115")

    if "titan"  in host : 
        # os.system(cdcmd+"./xmlchange -file env_build.xml   -id CESMSCRATCHROOT   -val $ENV{MEMBERWORK}/"+acct
        # if acct == "csc249" : os.system(cdcmd+"./xmlchange -file env_build.xml   -id CIME_OUTPUT_ROOT  -val "+workdir+"/"+acct)
        if acct=="cli115": os.system(cdcmd+"./xmlchange -file env_build.xml   -id CIME_OUTPUT_ROOT  -val /lustre/atlas1/cli115/scratch/hannah6/")
        if acct=="csc249": os.system(cdcmd+"./xmlchange -file env_build.xml   -id CIME_OUTPUT_ROOT  -val /lustre/atlas/scratch/hannah6/csc249/" )
    
    # os.system(cdcmd+"./xmlchange -file env_build.xml   -id CIME_OUTPUT_ROOT  -val "+workdir+"/"+acct_dir)
    

    if os.path.isfile(case_dir+"case.build") :
        if clean : os.system(cdcmd+"./case.build --clean")                  # Clean previous build    
        os.system(cdcmd+"./case.build")
    else :
        os.system(cdcmd+"./"+case_name+".clean_build")
        os.system(cdcmd+"./"+case_name+".build")

#=================================================================================================================================
# Write a custom namelist options
#=================================================================================================================================
if runsim == True:

    nfile = case_dir+"user_nl_cam"
    file = open(nfile,'w') 
 
    # file.write(" nhtfrq    = 0,-6 \n") 
    # file.write(" mfilt     = 1, 4 \n") 
    # file.write(" fincl2    = 'TMQ','PRECT','TS','LHFLX','SHFLX' ")
    # file.write(" fincl2    = 'T','Q','OMEGA','U','V''Z3' ")
    # file.write(            ",'QRL','QRS'")
    # file.write(            ",'PS','TS','TMQ','PRECT'")
    # file.write(            ",'LHFLX','SHFLX'")
    # file.write(            ",'FLNS','FLNT','FSNS','FSNT','FLUT' ")
    file.write("\n")
    
    # file.write(" phys_alltoall = 1      \n")
    if opts.LB2_flag : file.write(" phys_loadbalance = 2   \n")
    file.write(" srf_flux_avg = 1       \n")

    file.write(" dyn_npes = "+str(num_dyn)+" \n")

    if res=="1.9x2.5" : 
        file.write(" ncdata  = '"+init_dir+"hp_built_for_wh_1.9x2.5_L72_20081014_12Z_ECMWF.cam2.i.2008-10-14-43200_r2.nc' \n") 
        file.write(" dyn_npes = "+case_num+"  \n")


    # enforce defaults for the split parameters - in case a previous test run modified them
    # file.write(" qsplit    = 1 \n") 
    # file.write(" rsplit    = 3 \n") 
    # file.write(" se_nsplit = 2 \n") 

    file.close() 

    if nfac != "0" :
        if 'dyn_npes' not in open(nfile).read():
            exit("ERROR: dyn_npes was not set in the namelist - this must be specified for consistency in timing tests!")

    ### Turn off CICE history files
    # nfile = case_dir+"user_nl_cice"
    # file = open(nfile,'w') 
    # file.write(" histfreq = 'x','x','x','x','x' \n")
    # file.close()

#===============================================================================================================================================================
#===============================================================================================================================================================
# Run the simulation
#===============================================================================================================================================================
#===============================================================================================================================================================
if runsim == True:

    # ncdata = '/lustre/atlas1/cli115/scratch/hannah6/E3SM_SP2_CTL_ne30_01/run/cami-mam3_0000-01-01_ne30np4_L30_c130424.modified.nc'
    # os.system(cdcmd+"./xmlchange --file env_run.xml   --id RUN_STARTDATE  --val 0006-01-01")

    # if cld=="SP1" and not opts.rrtmg_flag : os.system(cdcmd+"./xmlchange --file env_run.xml --id CAM_NML_USE_CASE  --val 2000_cam5_av1c-SP1")

    runfile = case_dir+"case.run"
    subfile = case_dir+"case.submit"
        
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id REST_OPTION  -val never ")     # Disable restart file write for timing

    os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_OPTION  -val ndays ")
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_N       -val "+str(ndays)) 
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id RESUBMIT     -val "+str(resub))
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id CONTINUE_RUN -val "+cflag)
    #os.system(cdcmd+"./xmlchange -file env_run.xml   -id CONTINUE_RUN -val FALSE")

    if "SP" in cld and res=="ne4" :
            os.system(cdcmd+"./xmlchange --file env_run.xml --id ATM_NCPL --val 24 ") # default is 12

    #------------------------------
    # set the queue
    #------------------------------
    # os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val debug")
    os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val batch")
 
    #------------------------------
    # Set the wall clock limit
    #------------------------------
    if cld=="ZM"  : os.system(cdcmd+"./xmlchange -file env_batch.xml -id JOB_WALLCLOCK_TIME -val 2:00:00")
    if cld=="SP1" : os.system(cdcmd+"./xmlchange -file env_batch.xml -id JOB_WALLCLOCK_TIME -val 4:00:00")
    if cld=="SP2" : os.system(cdcmd+"./xmlchange -file env_batch.xml -id JOB_WALLCLOCK_TIME -val 8:00:00")
    
    #------------------------------
    # Submit the run
    #------------------------------
    # os.system(cdcmd+subfile)

    if "titan"  in host :
        if acct == "csc249" :
            os.system(cdcmd+subfile+" -a '-A csc249adse15' --mail-user hannah6@llnl.gov  -M end -M fail  ")
        else :
            os.system(cdcmd+subfile)
    else :
        os.system(cdcmd+subfile)
    
    
#==================================================================================================
#==================================================================================================
# del case_dir

