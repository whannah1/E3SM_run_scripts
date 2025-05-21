#!/usr/bin/env python
#===============================================================================================================================================================
#  Jan, 2017 - Walter Hannah - Lawrence Livermore National Lab
#  This script runs atmosphere only simulations of ACME
#===============================================================================================================================================================
import sys
import os
import fileinput
import subprocess
# import numpy as np
home = os.getenv("HOME")
host = os.getenv("HOST")

# workdir = os.getenv("MEMBERWORK")
# workdir = "/lustre/atlas/scratch/hannah6/"

if "edison" in host : host = "edison"
if "blogin" in host : host = "anvil"
if "titan"  in host : 
    host = "titan"
    acct = "cli115"
    # acct = "csc249"
#===============================================================================================================================================================
#===============================================================================================================================================================
newcase,config,build,runsim,clean,mk_nml,use_GNU,copyinit,debug,debug_log,debug_ddt,test_run,drop_opt,lower_dt,inc_remap,disable_bfb  = False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False

# newcase  = True
# clean    = True
# config   = True
# build    = True
# mk_nml   = True
runsim   = True

# use_GNU     = True       # use the GNU compiler instead of the default
# copyinit    = True       # copy new initialization files for branch run
# test_run    = True       # special debug mode - only run a few time steps (see namelist section)
debug       = True       # enable debug flags
# debug_log   = True       # enable debug output in log files (adds WH_DEBUG flag)
# debug_ddt   = True       # also change ntask for running DDT - only works with debug 
# drop_opt    = True       # Reduce optimization in Macros file                 requires rebuild
lower_dt    = True       # Reduce timestep by half (from 30 to 15 minutes)    requires re-config
    
# inc_remap   = True       # Increase vertical remap parameter to reduce timestep via atm namelist
# disable_bfb = True       # Use this to get past a random crash (slightly alters the weather of the restart)

# coarse_vres = True       # use custom coarse vertical grid (not CAM5 grid)

#--------------------------------------------------------
#--------------------------------------------------------
# case_num = "00"     # control - all current defaults  
# case_num = "01"     # control - all current defaults + SP_FLUX_BYPASS
# case_num = "02"     # same as 00 but lower timestep
# case_num = "03"     # same as 00 but without bypassing thermodynamic diffusion (SP_USE_DIFF)
# case_num = "04"     # use custom coarse vertical grid (not CAM5 grid)
case_num = "04a"     # spinup run for 04
# case_num = "05"     # remove SP_DIR_NS
# case_num = "06"     # SP_CRM_SPLIT
# case_num = "07"     # 30L + SP_DYNAMIC_DX
# case_num = "08"     # 30L w/ SP_CRM_SPLIT 

# case_num = "09"     # ne16 + 30L tuning run - control
# case_num = "09a"    # ne16 + 30L tuning run - SP_FAST_ICE + SP_TUNING_A - decrease autoconversion threshold
# case_num = "09b"    # ne16 + 30L tuning run - SP_FAST_ICE + SP_TUNING_B - increase autoconversion coeff
# case_num = "09c"    # ne16 + 30L tuning run - SP_FAST_ICE + SP_TUNING_C - combine A + B
# case_num = "09d"    # ne16 + 30L tuning run - SP_FAST_ICE + SP_TUNING_D - larger fall speed parameters
# case_num = "09e"    # ne16 + 30L tuning run - SP_FAST_ICE + SP_TUNING_E - combine C + D
# case_num = "09f"    # ne16 + 30L tuning run - SP_FAST_ICE + SP_TUNING_F - combine B + D

### initial tuning runs used this:
### case_num = "09"     # 30L w/ SP_FAST_ICE  
### case_num = "09a"     # 30L w/ SP_LOWER_ICE_AUTOCONV
### case_num = "09b"     # 30L w/ SP_FAST_ICE + SP_LOWER_ICE_AUTOCONV

# case_num = "10"     # SP_LIMIT_QP_EVAP_00_PCT       (limit precip evap both in and outside of cloud)
# case_num = "11"     # SP_LIMIT_QP_EVAP_20_PCT
# case_num = "12"     # SP_LIMIT_QP_EVAP_50_PCT
# case_num = "13"     # SP_LIMIT_QP_EVAP_80_PCT


# case_num = "80"    # 30L - SP1+RRTMG 
# case_num = "31"    # ECPP test
# case_num = "32"    # 30L ECPP test
# case_num = "33"    # 30L ECPP test w/ CAMRT

# case_num = "20"    # CAMRT, -chem none
# case_num = "21"    # RRTMG, -chem none
# case_num = "22"    # RRTMG, -chem none, MG

### SRC1 runs
# case_num = "s1_00"    # SP w/ SOM
# case_num = "s1_01"    # SP w/ fully coupled

### scalar momentum tests
# case_num = "s2_68a"   # initial test of SP_ORIENT_RAND - w/o SP_ESMT
# case_num = "s2_69a"   # SP_ORIENT_RAND + SP_ESMT + SP_USE_ESMT + SP_ESMF_PGF

#--------------------------------------------------------
#--------------------------------------------------------

cld = "SP1"    # ZM / SP1 / SP2
exp = "CTL"    # CTL / EXP / AMIP / BRANCH / TEST
res = "ne30"   # ne30 / ne16 / 0.9x1.25 / 1.9x2.5

cflag = "FALSE"                      # Don't forget to set this!!!! 
# cflag = "TRUE"

wall_time       =  "4:00:00"
wall_time_debug =  "1:00:00"

if "ZM" in cld : ndays,resub = (73*2),(10)  # 5=2yr, 15=6yr, 25=10yr
if "SP" in cld :
    # ndays,resub = 8,(4*3-1 )
    # ndays,resub = 5,(6*3-1 )
    ndays,resub = 1,3

nsteps = 48*1  # only for debug and test_run modes


# crm_nx,crm_ny,mod_str = 32,1,"_1km"
# crm_nx,crm_ny,mod_str = 32,1,"_4km"
crm_nx,crm_ny,mod_str = 64,1,"_1km"
# crm_nx,crm_ny,mod_str = 64,1,"_4km"
# crm_nx,crm_ny,mod_str = 128,1,"_2km"



if case_num in ['04','04a','04b','04c','04d'] :
    ndays,resub = 1,1
    crm_nx,crm_ny,mod_str = 64,1,"_1km"

#--------------------------------------------------------
# Special Cases
#--------------------------------------------------------

flux_avg_omit_list = [] # ['','']


if case_num in ['31','32','33'] : cld = "SP2"   # ECPP tests

if case_num == '02'  : lower_dt = True

if debug or test_run : resub = 0

#--------------------------------------------------------
# Setup the case name
#--------------------------------------------------------

if "SP" in cld :
    crmdim = "_"+str(crm_nx)+"x"+str(crm_ny) 
else :
    crmdim  = ""
    mod_str = ""

case_name = "ACME_"+cld+"_"+exp+"_"+res+crmdim+mod_str+"_"+case_num

#===============================================================================================================================================================
# Various settings for account / system / directories
#===============================================================================================================================================================
top_dir     = home+"/ACME/"
srcmod_dir  = top_dir+"mod_src/"
nmlmod_dir  = top_dir+"mod_nml/"

src_dir = home+"/ACME/ACME_SRC_master"
# switch to alternate code base if the case number is negative
# if case_num == "-2" : src_dir = home+"/ACME/ACME_SRC_master"
if "s1"  in case_num : src_dir = home+"/ACME/ACME_SRC1"
if "s2"  in case_num : src_dir = home+"/ACME/ACME_SRC2"
if "old" in case_num : src_dir = home+"/ACME/ACME_SRC_master_old"

scratch_dir = os.getenv("CSCRATCH","")
if scratch_dir=="" : 
    if host=="titan" :
        if acct == "cli115" : 
            scratch_dir = "/lustre/atlas1/"+acct+"/scratch/hannah6/"
        else : 
            scratch_dir = "/lustre/atlas/scratch/hannah6/"+acct+"/"

run_dir = scratch_dir+"/"+case_name+"/run"

if res=="ne4"  : num_dyn = 96
if res=="ne16" : num_dyn = 1536
if res=="ne30" : num_dyn = 5400
if res=="0.9x1.25" : num_dyn = 1536
if res=="1.9x2.5"  : num_dyn = 1536
# if res=="ne120" : num_dyn = 86400
# if int(case_num) < num_dyn : num_dyn = int(case_num)

if lower_dt :
    dtime = 15*60
else :
    dtime = 30*60
ncpl  = 86400 / dtime

os.system("cd "+top_dir)
case_dir  = top_dir+"Cases/"+case_name 
cdcmd = "cd "+case_dir+" ; "
print
print("  case : "+case_name)
print
#===============================================================================================================================================================
#===============================================================================================================================================================
# Create new case
#===============================================================================================================================================================
#===============================================================================================================================================================

compset_opt = " -compset FC5AV1C-L "
grid_opt    = res+"_"+res
    
if exp == "AMIP" : 
    compset_opt = " -compset F20TRC5AV1C-L"
    # if res=="ne30" : grid_opt = "ne30_oECv3_ICG"
    if res=="ne30" : grid_opt = "ne30_oECv3"

use_SP_compset = False

if case_num in ['s1_00'] :
    if cld=="SP1" : compset_opt = " -compset ESP1V1 "  # SOM compset
    # if cld=="SP1" : compset_opt = " -compset FSP1V1 "
    # if cld=="SP2" : compset_opt = " -compset FSP2V1 "
    use_SP_compset = True

if case_num in ['s1_01'] :
    # if cld=="SP1" : compset_opt = " -compset A_WCYCL2000_SP1 " # Fully coupled
    if cld=="SP1" : compset_opt = " -compset A_WCYCL1850S_SP1 " # Fully coupled
    use_SP_compset = True
    grid_opt    = res+"_oECv3_ICG"


    

if newcase == True:
    # compfile = "/home/whannah/ACME/mod_compset/F_CUSTOM.xml"
    # compset_opt = "-compset FC5AV1C-L "
    # if cld=="SP" and mod=="ATM" : compset_opt = "-compset F2000_SPCAM4_1MOM -compset_file "+compfile

    # if cld=="SP" and mod=="ATM" : compset_opt = "-user_compset 2000_CAM5_CLM45%CNDV_DICE%NULL_DOCN%DOM_SROF_SGLC_SWAV"
    # if cld=="SP" and mod=="ATM" : compset_opt = "-user_compset 2000_CAM4%SP_CLM45_DICE%NULL_DOCN_SROF_SGLC_SWAV"


    if host=="titan" and acct == "csc249" : os.system("echo '"+acct+"' > "+home+"/.cesm_proj")         # temporarily change project on titan

    newcase_cmd = src_dir+"/cime/scripts/create_newcase"
    cmd = newcase_cmd+" -case "+case_dir+" "+compset_opt+" -res "+grid_opt+" -mach  "+host
    if use_GNU : cmd + " -compiler gnu "
    print
    print(cmd)
    print
    os.system(cmd)

    if host=="titan" and acct == "csc249" : os.system("echo 'CSC249ADSE15' > "+home+"/.cesm_proj")       # change project name back


case_dir = case_dir+"/"

### set location and file name for initialization
init_dir = init_dir = "/lustre/atlas/scratch/hannah6/"+acct+"/init_files/"
if acct == "cli115" :  init_dir = "/lustre/atlas1/cli115/scratch/hannah6/init_files/"
cami_file = "default"
if case_num in ['04','04a','04b','04c','04d'] : 
    cami_file = "cami_mam3_Linoz_ne30np4_L44_c160214.nc"

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
    nlev_crm = 58

    if case_num in ['04','04a','04b','04c','04d'] : 
        nlev_gcm = 44
        nlev_crm = 30

    if any(c in case_num for c in ['07','08','09','80','32','33']) :
        nlev_gcm = 30
        nlev_crm = 28

    if any(c in case_num for c in ['20']) :
        nlev_gcm = 26
        nlev_crm = 24
    
    crm_adv = "MPDATA"

    # if case_num in [''] :
    #     crm_adv = "UM5"        

    crm_dt = 5    # 10
    crm_dx = 1000

    if mod_str == "_4km":
        crm_dx = 4000
        # if nlev_gcm == 26 : crm_dt = 10
    if mod_str == "_2km":
        # crm_dt = 10
        crm_dx = 2000
    if mod_str == "_0.5km":
        # crm_dt = 2
        crm_dx = 500

    
    if case_num in ['07'] : crm_dx = 2000


    #------------------------------------------------
    # set CAM_CONFIG_OPTS
    #------------------------------------------------
    # cam_opt = " -rad rrtmg -phys cam5 -nlev "+str(nlev_gcm)+"  -clubb_sgs -microphys mg2 -chem trop_mam3 -rain_evap_to_coarse_aero -bc_dep_to_snow_updates"     # this is the default for non-SP runs

    if cld=="ZM" :
        cam_opt = " -rad rrtmg -nlev "+str(nlev_gcm)+"  -clubb_sgs -microphys mg2 "

        chem_opt = " -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates "

        # cpp_opt = ""
        cpp_opt = " -cppdefs ' "
        
        # if case_num in ['25'] : cpp_opt = cpp_opt+" -DZM_ED_MOD " 
        # if case_num in [] : cpp_opt = cpp_opt+" -DZM_TAU_MOD "
        # if case_num in [] : cpp_opt = cpp_opt+" -DZM_PE_MOD "

        cpp_opt = cpp_opt+" ' "
        cam_opt = cam_opt+chem_opt+cpp_opt 
        cam_crm_rad_opt = ""
    
    if "SP" in cld :

        # set options common to all SP setups
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
        cam_crm_rad_opt = " -crm_nx_rad 8 -crm_ny_rad 1 "
        cam_opt = cam_opt+cam_crm_rad_opt

        # use the same chem and aerosol options for SP1 and SP2
        chem_opt = " -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates "

        # set CPP variables
        cpp_opt = " -cppdefs ' -DSP_DIR_NS  -DSP_TK_LIM  -DSUPPRESS_QNEG_MSG  "

        # if crm_nx>1 and crm_ny>1 : cpp_opt = cpp_opt + " -DCRM3D "

        # cpp_opt = cpp_opt+" -DSPMOMTRANS "
        # cpp_opt = cpp_opt+" -DCRM_SINGLE_PRECISION"

        #-------------------------------
        # Special cases
        #-------------------------------

        if case_num in ['01'] : 
            cpp_opt = cpp_opt+" -DSP_FLUX_BYPASS  "

        if case_num in ['03'] : 
            cpp_opt = cpp_opt+" -DSP_USE_DIFF "   # enable normal GCM thermodynamic diffusion

        if case_num in ['04a'] : 
            cam_opt = cam_opt+" -clubb_sgs "    # will this help the spinup process?
        
        if case_num in ['05'] : cpp_opt = cpp_opt.replace("-DSP_DIR_NS","")    # remove SP_DIR_NS

        if case_num in ['06'] : cpp_opt = cpp_opt+" -DSP_CRM_SPLIT "                    # split CRM integration across BC and AC physics
        if case_num in ['07'] : cpp_opt = cpp_opt+" -DSP_DYNAMIC_DX   "     # dynamically modified CRM DX
        if case_num in ['08'] : cpp_opt = cpp_opt+" -DSP_CRM_SPLIT  "                   # split CRM integration with modified forcing
        # if case_num in [''] : cpp_opt = cpp_opt+" -DSP_CRM_SPLIT -DSP_ALT_FORCING "   # split CRM integration across BC and AC physics
        # if case_num in [''] : cpp_opt = cpp_opt+" -DSP_CRM_DOUBLE_CALL "   # split GCM integration across BC and AC physics

        # if case_num in ['09'] : cpp_opt = cpp_opt+"  "
        if case_num in ['09a'] : cpp_opt = cpp_opt+" -DSP_FAST_ICE -DSP_TUNING_A "
        if case_num in ['09b'] : cpp_opt = cpp_opt+" -DSP_FAST_ICE -DSP_TUNING_B "
        if case_num in ['09c'] : cpp_opt = cpp_opt+" -DSP_FAST_ICE -DSP_TUNING_C "
        if case_num in ['09d'] : cpp_opt = cpp_opt+" -DSP_FAST_ICE -DSP_TUNING_D "
        if case_num in ['09e'] : cpp_opt = cpp_opt+" -DSP_FAST_ICE -DSP_TUNING_E "
        if case_num in ['09f'] : cpp_opt = cpp_opt+" -DSP_FAST_ICE -DSP_TUNING_F "
        
        if case_num in ['10'] : cpp_opt = cpp_opt+" -DSP_LIMIT_QP_EVAP_00_PCT  " # limit evap of precip outside of cloud completely
        if case_num in ['11'] : cpp_opt = cpp_opt+" -DSP_LIMIT_QP_EVAP_20_PCT  " # limit evap of precip outside of cloud to 20%
        if case_num in ['12'] : cpp_opt = cpp_opt+" -DSP_LIMIT_QP_EVAP_50_PCT  " # limit evap of precip outside of cloud to 50%
        if case_num in ['13'] : cpp_opt = cpp_opt+" -DSP_LIMIT_QP_EVAP_80_PCT  " # limit evap of precip outside of cloud to 80%

        if cld=="SP1" and any(c in case_num for c in ['20']) :
            cam_opt = cam_opt.replace("-microphys mg2"," ")          # CAMRT doesn't play nice with MG2, so remove it - revert to default RK
            cam_opt = cam_opt.replace("-rad rrtmg","-rad camrt")
            chem_opt = " -chem none"


        if any(c in case_num for c in ['31','32','33']) :
            chem_opt = chem_opt + " -use_ECPP "
            # cpp_opt = cpp_opt+" -DECPP_DEBUG "
            # use this to disable physics)update for ECPP section of crm_physics
            # cpp_opt = cpp_opt+" -DECPP_DEBUG1 "
            # cpp_opt = cpp_opt+" -DECPP_DEBUG2 "  
            # cpp_opt = cpp_opt+" -DECPP_LEV_MOD "


        # if case_num == '' : cpp_opt = cpp_opt+" -DSP_PHYS_BYPASS "
        # if case_num == '' : cpp_opt = cpp_opt+" -DSP_ESMT  -DSPMOMTRANS  -DSP_USE_ESMT  "
        # if case_num == '' : cpp_opt = cpp_opt+" -DSP_ESMT -DSP_USE_ESMT -DSP_ESMT_PGF " 

        if case_num in ['s2_68','s2_68a'] : 
            cpp_opt = cpp_opt+" -DSP_ORIENT_RAND " 
        if case_num in ['s2_69','s2_69a'] : 
            cpp_opt = cpp_opt+" -DSP_ESMT -DSP_USE_ESMT -DSP_ORIENT_RAND " # -DSP_ESMT_PGF

        # if case_num == "" : cpp_opt = cpp_opt+" -DSP_CRM_REINIT -DSP_CRM_REINIT_UV -DSP_CRM_REINIT_W -DSP_CRM_REINIT_T -DSP_CRM_REINIT_Q "
        # if case_num == "" : cpp_opt = cpp_opt+" -DSP_CRM_REINIT -DSP_CRM_REINIT_T  -DSP_CRM_REINIT_Q " # Omit all wind variables
        # if case_num == "" : cpp_opt = cpp_opt+" -DSP_CRM_REINIT -DSP_CRM_REINIT_UV -DSP_CRM_REINIT_W " # Omit T & Q (including condensate)

        #-------------------------------
        #-------------------------------

        ### use all columns for radiation with CAMRT
        if " camrt " in cam_opt : cam_opt = cam_opt.replace(cam_crm_rad_opt,"")

        if debug_log : cpp_opt = cpp_opt+" -DWH_DEBUG "

        cam_opt = cam_opt+chem_opt+cpp_opt+" ' "


    if cld=="ZM" or ( "SP" in cld and not use_SP_compset ) : 
        print("------------------------------------------------------------")
        CMD = cdcmd+"./xmlchange --file env_build.xml --id CAM_CONFIG_OPTS --val \""+cam_opt+"\""
        print(CMD)
        os.system(CMD)
        print("------------------------------------------------------------")

    # for F-compsets turn off river transport model (RTM) - unless MPI bug fix is merged 
    # CMD = cdcmd+"./xmlchange --file env_build.xml --id RTM_MODE --val NULL "
    # print(CMD)
    # os.system(CMD)

    #------------------------------------------------
    # for FV runs we need to set this here
    # otherwise it will complain about not having a default ncdata
    #------------------------------------------------
    # if nlev_gcm==72 and res=="1.9x2.5" :
    #     # init_dir = "/lustre/atlas1/"+acct+"/scratch/hannah6/init_files/"
    #     # init_dir = "/lustre/atlas/scratch/hannah6/"+acct+"/"
    #     nfile = case_dir+"user_nl_cam"
    #     file = open(nfile,'w') 
    #     file.write(" ncdata  = '"+init_dir+"hp_built_for_wh_1.9x2.5_L72_20081014_12Z_ECMWF.cam2.i.2008-10-14-43200_r2.nc' \n") 
    #     file.close() 

    # if case_num in ['48','49'] : 
    #     nfile = case_dir+"user_nl_cam"
    #     file = open(nfile,'w')
    #     file.write(" ncdata  = '"+init_dir+"cami_mam3_Linoz_ne30np4_L70_c160214.nc' \n") 
    #     file.close() 


    #------------------------------------------------
    # update cami file if not equal to "default"
    #------------------------------------------------
    if cami_file != "default" :
        ### copy file to scratch
        CMD = "cp ~/ACME/init_files/"+cami_file+" "+init_dir
        print(CMD)
        os.system(CMD)
        ### write file path to namelist
        nfile = case_dir+"user_nl_cam"
        file = open(nfile,'w')
        file.write(" ncdata  = '"+init_dir+cami_file+"' \n ") 
        file.close() 
    #------------------------------------------------
    # set run-time variables
    #------------------------------------------------
    start_date = "2000-01-01"

    if exp == "AMIP" : start_date = "1990-01-01"
    
    os.system(cdcmd+"./xmlchange --file env_run.xml   --id RUN_STARTDATE  --val "+start_date)

    if host=="titan" :
        # if acct != "cli115" : os.system(cdcmd+"./xmlchange --file env_run.xml --id RUNDIR  --val "+workdir+"/"+acct+"/"+case_name+"/run ")
        if acct == "cli115" : os.system(cdcmd+"./xmlchange --file env_run.xml --id RUNDIR  --val /lustre/atlas1/cli115/scratch/hannah6/"+case_name+"/run ")
        if acct == "csc249" : os.system(cdcmd+"./xmlchange --file env_run.xml --id RUNDIR  --val /lustre/atlas/scratch/hannah6/csc249/" +case_name+"/run ")
        

    if host=="anvil" :
        scratch_root_dir   = "/lcrc/group/acme/whannah/ACME_simulations/"
        short_term_archive = "/lcrc/group/acme/whannah/archive/"+case_name
        
        os.system(cdcmd+"./xmlchange --file env_run.xml --id DOUT_S_ROOT --val "+short_term_archive)
        os.system(cdcmd+"./xmlchange --file env_run.xml --id EXEROOT --val "+scratch_root_dir+case_name+"/bld")
        os.system(cdcmd+"./xmlchange --file env_run.xml --id RUNDIR  --val "+scratch_root_dir+case_name+"/run")
        
        
    if " camrt " in cam_opt :
        # os.system(cdcmd+"./xmlchange --file env_run.xml --id CAM_NML_USE_CASE  --val 2000_cam5_av1c-SP1")
        os.system(cdcmd+"./xmlchange --file env_run.xml --id CAM_NML_USE_CASE  --val 2000_cam5_av1c-SP1_no-linoz")

    #------------------------------------------------
    # copy any modified source code (preserve permissions)
    #------------------------------------------------
    # if cld=="ZM" and case_num=="01" :
        # os.system("cp -rp "+srcmod_dir+"zm_conv_intr.no-CMT.F90  "+case_dir+"SourceMods/src.cam/zm_conv_intr.F90 ")
    #------------------------------------------------
    # Set input data location
    #------------------------------------------------
    # os.system(cdcmd+"./xmlchange -file env_run.xml  DIN_LOC_ROOT='/global/cscratch1/sd/acmedata' ")
    # os.system(cdcmd+"./xmlchange -file env_run.xml   -id DIN_LOC_ROOT       -val '/global/cscratch1/sd/acmedata/inputdata' ")
    #------------------------------------------------
    # Change processor count
    #------------------------------------------------
    if res=="ne4" :
        # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val   96 ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val  866 ")
    if res=="ne16" :
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val 1536 ")
        # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val 3457 ")
    if res=="ne30" :
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val 5400 ")
        # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val 6076 ")
        # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val 10800 ")

    if cld == "ZM" : os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val "+str(num_dyn)+" ")

    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_LND -val "+str(num_dyn)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ICE -val "+str(num_dyn)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_OCN -val "+str(num_dyn)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_CPL -val "+str(num_dyn)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_GLC -val "+str(num_dyn)+" ")
    # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_RTM -val "+str(num_dyn)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_WAV -val "+str(num_dyn)+" ")

    if debug and debug_ddt :
        if res=="ne30" : ntask_debug_ddt = 480 #300
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val "+str(ntask_debug_ddt)+" ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_LND -val "+str(ntask_debug_ddt)+" ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ICE -val "+str(ntask_debug_ddt)+" ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_OCN -val "+str(ntask_debug_ddt)+" ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_CPL -val "+str(ntask_debug_ddt)+" ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_GLC -val "+str(ntask_debug_ddt)+" ")
        # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_RTM -val "+str(ntask_debug_ddt)+" ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_WAV -val "+str(ntask_debug_ddt)+" ")

    ### This might be needed for ne120
    # if res=="ne120" :
    #     os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_ATM -val 1 ")
    #     os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_OCN -val 1 ")
    #     os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_LND -val 1 ")
    #     os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_CPL -val 1 ")
    #     os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_GLC -val 1 ")
    #     os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_ICE -val 1 ")
    #     os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_RTM -val 1 ")
    #     os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_WAV -val 1 ")

    #------------------------------------------------
    # Set the timestep
    #------------------------------------------------
    os.system(cdcmd+"./xmlchange -file env_run.xml -id ATM_NCPL -val "+str(ncpl) )

    #------------------------------------------------
    # for GNU set COMPILER before configure so that Macros file has correct flags
    #------------------------------------------------
    if use_GNU :
        CMD = cdcmd+"./xmlchange --file env_build.xml --id COMPILER --val \"gnu\" "
        print(CMD)
        os.system(CMD)
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
    #os.system(cdcmd+"cp "+srcmod_dir+"* ./SourceMods/src.cam/")    # copy any modified source code

    #----------------------------------------------------------
    # Make sure optimization is set correctly in Macros file
    #----------------------------------------------------------
    macros_file = case_dir+"Macros.make"
    f = open(macros_file, "r")
    contents = f.readlines()
    f.close()
    index = -1
    for num, line in enumerate(contents, 1):
        if "ifeq ($(DEBUG), FALSE) " in line: index = num
    if index > 0 :    
        if drop_opt : 
            contents[index] = "   FFLAGS +=  -O1 \n"
        else :
            contents[index] = "   FFLAGS +=  -O2 \n"
    f = open(macros_file, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()
    #----------------------------------------------------------
    #----------------------------------------------------------


    if "titan"  in host : 
        # os.system(cdcmd+"./xmlchange -file env_build.xml   -id CESMSCRATCHROOT   -val $ENV{MEMBERWORK}/"+acct
        # if acct == "csc249" : os.system(cdcmd+"./xmlchange -file env_build.xml   -id CIME_OUTPUT_ROOT  -val "+workdir+"/"+acct)
        if acct == "cli115" : os.system(cdcmd+"./xmlchange -file env_build.xml   -id CIME_OUTPUT_ROOT  -val /lustre/atlas1/cli115/scratch/hannah6/")
        if acct == "csc249" : os.system(cdcmd+"./xmlchange -file env_build.xml   -id CIME_OUTPUT_ROOT  -val /lustre/atlas/scratch/hannah6/csc249/" )

    if use_GNU :
        CMD = cdcmd+"./xmlchange --file env_build.xml --id COMPILER --val \"gnu\" "
        print(CMD)
        os.system(CMD)

    if debug :
        os.system(cdcmd+"./xmlchange -file env_build.xml   -id DEBUG   -val TRUE")
    else :
        os.system(cdcmd+"./xmlchange -file env_build.xml   -id DEBUG   -val FALSE")

    if os.path.isfile(case_dir+"case.build") :
        if clean : os.system(cdcmd+"./case.build --clean")                  # Clean previous build    
        os.system(cdcmd+"./case.build")
    else :
        os.system(cdcmd+"./"+case_name+".clean_build")
        os.system(cdcmd+"./"+case_name+".build")

#=================================================================================================================================
# Copy init data for branch run
#=================================================================================================================================
# if copyinit == True:
#     print 
#     if case_num=="01" : branch_data = "/glade/p/work/whannah/"+ref_case+"/"+ref_date+"-00000/* "
#     if case_num=="02" : branch_data = "/glade/p/work/whannah/"+ref_case+"/"+ref_date+"-00000/* "
#     os.system("cp "+branch_data+" "+run_dir+case_name+"/run")

# if copyinit == True:
#     if case_num in ['31','32'] : 
#         ref_case = "ACME_SP2_CTL_ne30_03"
#         ref_date = "2000-01-03"
#         os.system(cdcmd+"./xmlchange -file env_run.xml     -id RUN_TYPE    -val hybrid")
#         os.system(cdcmd+"./xmlchange -file env_run.xml     -id GET_REFCASE -val FALSE")
#         os.system(cdcmd+"./xmlchange -file env_run.xml     -id RUN_REFCASE -val "+ref_case)
#         os.system(cdcmd+"./xmlchange -file env_run.xml     -id RUN_REFDATE -val "+ref_date)
#         # branch_data = "/lustre/atlas1/"+acct+"/scratch/hannah6/"+ref_case+"/run/"+ref_date+"-00000/* "
#         branch_data = "/lustre/atlas1/"+acct+"/scratch/hannah6/"+ref_case+"/run/*.r*"+ref_date+"*nc "
#         cmd = "cp "+branch_data+" "+run_dir
#         print
#         print(cmd)
#         print
#         os.system(cmd)

#=================================================================================================================================
# Write the custom namelist options
#=================================================================================================================================
if mk_nml :

    (cam_config_opts, err) = subprocess.Popen(cdcmd+"./xmlquery CAM_CONFIG_OPTS -value", stdout=subprocess.PIPE, shell=True).communicate()
    (compset        , err) = subprocess.Popen(cdcmd+"./xmlquery COMPSET         -value", stdout=subprocess.PIPE, shell=True).communicate()

    nfile = case_dir+"user_nl_cam"
    file = open(nfile,'w') 


    #------------------------------
    # Special test mode 
    #------------------------------
    if test_run :
        file.write(" nhtfrq    = 0,1 \n") 
        file.write(" mfilt     = 1,"+str(nsteps)+" \n") 
        file.write(" fincl2    = 'T','Q','PS','TS','Z3','OMEGA','U','V','QRL','QRS','CLOUD' ")
        file.write(             ",'FLNS','FLNT','FSNS','FSNT','FLUT' ")
        file.write(             ",'FSNTC','FLNTC' ")
        file.write(             ",'LHFLX','SHFLX'")
        file.write(             ",'PRECT','TMQ'")
        file.write(             ",'LWCF','SWCF'")
        # file.write(             ",'QEXCESS' ")
        if "SP" in cld :
            file.write(             ",'SPDT','SPDQ' ")
            # file.write(             ",'CRM_T','CRM_QV','CRM_QC','CRM_QPC','CRM_PREC' ")
            file.write(             ",'SPQPEVP','SPTLS' ")
            file.write(             ",'SPMCUP','SPMCDN','SPMCUUP','SPMCUDN' ")
            file.write(             ",'SPQC','SPQR' ")
            # file.write(             ",'SPQI','SPQS','SPQG' ")
        if "SP_CRM_SPLIT" in cam_config_opts :
            file.write(         ",'SPDT1','SPDQ1','SPDT2','SPDQ2' ")
        file.write("\n")

    #------------------------------
    # Default output
    #------------------------------
    else :
        file.write(" nhtfrq    = 0,-6,-1 \n") 
        file.write(" mfilt     = 1, 4, 120 \n")     # h2 = 1 hourly for 5 days
        # file.write(" nhtfrq    = 0,-6,-3 \n") 
        # file.write(" mfilt     = 1, 4, 80 \n")      # h2 = 3 hourly for 5 days 
        file.write(" fincl2    = 'T','Q','Z3','PS','TS' ")
        file.write(             ",'CLOUD','FLUT' ")
        file.write(             ",'U','V','OMEGA' ")        # velocity components
        file.write(             ",'QRL','QRS' ")            # Full radiative heating profiles
        file.write(             ",'FSNT','FLNT' ")          # Net TOM heating rates
        file.write(             ",'FLNS','FSNS' ")          # Surface rad for total column heating
        file.write(             ",'FSNTC','FLNTC' ")        # clear sky heating rates for CRE
        file.write(             ",'LHFLX','SHFLX'")         # surface fluxes
        if "SP" in cld :
            file.write(         ",'SPDT','SPDQ' ")
            file.write(         ",'SPMCUP','SPMCDN','SPMCUUP','SPMCUDN' ")
            if any(x in cam_config_opts for x in ["SP_ESMT","SP_USE_ESMT","SPMOMTRANS"]) : 
                file.write(",'ZMMTU','ZMMTV','uten_Cu','vten_Cu' ")
            if "SP_USE_ESMT" in cam_config_opts : file.write(",'U_ESMT','V_ESMT' ")
            if "SPMOMTRANS"  in cam_config_opts : file.write(",'UCONVMOM','VCONVMOM' ")
        file.write("\n")
        file.write(" fincl3    = 'PRECT','TMQ' ")
        # file.write(            ",'LHFLX','SHFLX'")
        file.write("\n")


    if cami_file != "default" : file.write(" ncdata  = '"+init_dir+cami_file+"' \n")         
    

    if "SP" in cld : 
        if not flux_avg_omit_list : 
            file.write(" srf_flux_avg = 1 \n")
        else :
            if any(x in case_num for x in flux_avg_omit_list) : 
                file.write(" srf_flux_avg = 0 \n")
            else : 
                file.write(" srf_flux_avg = 1 \n")

    # if exp == "AMIP" and "ZM" in cld and case_num in [] : file.write(" zmconv_tau = 1800 \n")
    
    # if exp == "AMIP" and "ZM" in cld and case_num in [] : 
    #     file.write(" zmconv_c0_lnd = 0.004 \n")
    #     file.write(" zmconv_c0_ocn = 0.007 \n")


    file.write(" dyn_npes = "+str(num_dyn)+" \n")

    #------------------------------
    # Dycore tuning parameters
    #------------------------------

    ### default values
    qsplit            = 1 
    rsplit            = 3 
    se_nsplit         = 2
    hypervis_subcycle = 3

    if inc_remap :
        se_nsplit = 4
    
    ### special cases
    if case_num in ['04a'] : 
        qsplit            = 4
        rsplit            = 8
        se_nsplit         = 8
        hypervis_subcycle = 6

    file.write(" qsplit    = "+str(   qsplit)+" \n") 
    file.write(" rsplit    = "+str(   rsplit)+" \n") 
    file.write(" se_nsplit = "+str(se_nsplit)+" \n")
    file.write(" hypervis_subcycle = "+str(hypervis_subcycle)+" \n") 

    #------------------------------
    # state_debug_checks
    #------------------------------
    if debug :
        file.write(" state_debug_checks = .true. \n")
    else :
        file.write(" state_debug_checks = .false. \n")

    # file.write(" dtime    = "+str(dtime)+" \n")     # probably don't need this as long as ATM_NCPL is set

    file.close() 

    #------------------------------
    # Turn off CICE history files
    #------------------------------
    nfile = case_dir+"user_nl_cice"
    file = open(nfile,'w') 
    file.write(" histfreq = 'x','x','x','x','x' \n")
    file.close()
    
    #------------------------------
    # Specify land timestep - probably don't need this as long as ATM_NCPL is set
    #------------------------------
    # nfile = case_dir+"user_nl_clm"
    # file = open(nfile,'w') 
    # file.write(" dtime    = "+str(dtime)+" \n")     
    # file.close()

    #------------------------------
    # convective gustiness modification
    #------------------------------
    # if exp == "AMIP" and "ZM" in cld and case_num in [] : 
    #     nfile = case_dir+"user_nl_cpl"
    #     file = open(nfile,'w') 
    #     file.write(" gust_fac = 1 \n")
    #     file.close()

    #------------------------------
    # AMIP issuse with land inputs
    #------------------------------
    if exp == "AMIP" : 
        nfile = case_dir+"user_nl_clm"
        file = open(nfile,'w') 
        file.write(" finidat             = '/lustre/atlas1/cli900/world-shared/cesm/inputdata/lnd/clm2/initdata_map/I1850CLM45.ne30_oECv3.edison.intel.36b43c9.clm2.r.0001-01-06-00000_c20171023.nc' \n")
        file.write(" flanduse_timeseries = '/lustre/atlas1/cli900/world-shared/cesm/inputdata/lnd/clm2/surfdata_map/landuse.timeseries_ne30np4_hist_simyr1850_c20171102.nc' \n")
        file.write(" fsurdat             = '/lustre/atlas1/cli900/world-shared/cesm/inputdata/lnd/clm2/surfdata_map/surfdata_ne30np4_simyr1850_2015_c171018.nc' \n")
        file.write(" check_finidat_year_consistency = .false. \n")
        file.close()

    #------------------------------
    # Set ocn domain file for SOM
    #------------------------------
    if "DOCN%SOM" in compset :
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id DOCN_SOM_FILENAME  -val pop_frc.1x1d.090130.nc ")

        nfile = case_dir+"user_nl_docn"
        file = open(nfile,'w') 
        file.write(' domainfile = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/share/domains/domain.ocn.ne30np4_gx1v6_110217.nc"  \n')
        file.close()

#===============================================================================================================================================================
#===============================================================================================================================================================
# Run the simulation
#===============================================================================================================================================================
#===============================================================================================================================================================
if runsim == True:


    CMD = ''
    if acct == "csc249" : CMD = cdcmd+"./xmlchange --file env_batch.xml --id CHARGE_ACCOUNT --val \"CSC249ADSE15\" "
    if acct == "cli115" : CMD = cdcmd+"./xmlchange --file env_batch.xml --id CHARGE_ACCOUNT --val \"CLI115\"  "
    print(CMD)
    if CMD != '' : os.system(CMD)

    # ncdata        = '/lustre/atlas1/"+acct+"/scratch/hannah6/ACME_SP2_CTL_ne30_01/run/cami-mam3_0000-01-01_ne30np4_L30_c130424.modified.nc'
    # os.system(cdcmd+"./xmlchange --file env_run.xml   --id RUN_STARTDATE  --val 0006-01-01")

    # if cld=="SP1" : os.system(cdcmd+"./xmlchange --file env_run.xml --id CAM_NML_USE_CASE  --val 2000_cam5_av1c-SP1")

    runfile = case_dir+"case.run"
    subfile = case_dir+"case.submit"

    ### CIME updates changed the run file name - prependend a "."
    if not os.path.isfile(runfile) : runfile = case_dir+".case.run"

    #------------------------------
    # Change run options
    #------------------------------
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_OPTION  -val ndays ")
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_N       -val "+str(ndays)) 
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id RESUBMIT     -val "+str(resub))
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id CONTINUE_RUN -val "+cflag)

    if debug or test_run :
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_OPTION  -val nsteps ")
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_N       -val "+str(nsteps)) 

    #------------------------------
    # Change the BFB flag for certain runs
    #------------------------------
    if disable_bfb : 
        os.system(cdcmd+"./xmlchange -file env_run.xml -id BFBFLAG -val FALSE")
    else :
        os.system(cdcmd+"./xmlchange -file env_run.xml -id BFBFLAG -val TRUE")

    #------------------------------
    # switch to debug queue
    # but check if a run is already in the dbug queu
    #------------------------------    

    os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val batch")
    # os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val debug")

    # if debug : os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val debug")
    # if test_run : os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val debug")

    if debug :
        ### get user name
        user = subprocess.check_output(["whoami"]).strip()
        ### get data on all jobs 
        out = subprocess.check_output(['qstat','-f'])
        lines = out.split('\n')
        ### build list of jobs for the user, each job is a dictionary
        jobs = []
        for line in lines:
            if "Job Id:" in line:  # new job
                job = {}
                s = line.split(":")
                job_id = s[1].split('.')[0].strip()
                job[s[0].strip()] = job_id
            if '=' in line:
                s = line.split("=")
                job[s[0].strip()] = s[1].strip()
            elif line == '':
                jobs.append(job)
        ### Check current jobs in case one is already in the debug queue
        debug_clear = True
        for job in jobs:
            if job['Job_Owner'].split('@')[0] == user:     
                if job['queue']=="debug" :
                    debug_clear = False
        if debug_clear : 
            os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val debug")
            wall_time = wall_time_debug

    #------------------------------
    # DEBUG LEVEL
    #------------------------------
    if debug :
        # level of debug output, 0=minimum, 1=normal, 2=more, 3=too much
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id INFO_DBUG -val 1")

        # for debug mode, make sure that we will get a core dump file 
        # in the event that we get a segmentation fault
        f = open(runfile, "r")
        contents = f.readlines()
        f.close()

        index = -1
        for num, line in enumerate(contents, 1):
            if "def _main_func(description):" in line: index = num+1
            if "resource.setrlimit" in line: index = -1  # this means the resource limit was already set

        if index > 0 :
            contents.insert(index  , "    import resource \n")
            contents.insert(index+1, "    resource.setrlimit(resource.RLIMIT_CORE, (resource.RLIM_INFINITY, resource.RLIM_INFINITY)) \n")
            contents.insert(index+2, "    \n")

            f = open(runfile, "w")
            contents = "".join(contents)
            f.write(contents)
            f.close()
        else:
            print("\n    WARNING: couldn't find line for resource limit in run file: \n"+runfile+" \n")

        # Make sure that there is not old core file
        # because it won't get overwritten
        core_file = run_dir+"/core"

        if os.path.isfile(core_file) :
            for n in range(1, 99):
                core_file_next = run_dir+"/core_old_" + str(n).zfill(2)
                if not os.path.isfile(core_file_next) :
                    os.system("mv "+core_file+"  "+core_file_next)
                    break


    #------------------------------
    # Set the wall clock limit
    #------------------------------
    # if test_run :
    #     os.system(cdcmd+"./xmlchange -file env_batch.xml -id JOB_WALLCLOCK_TIME -val 00:30:00")
    # else :
    #     os.system(cdcmd+"./xmlchange -file env_batch.xml -id JOB_WALLCLOCK_TIME -val "+wall_time)

    os.system(cdcmd+"./xmlchange -file env_batch.xml -id JOB_WALLCLOCK_TIME -val "+wall_time)

    #------------------------------
    # Submit the run
    #------------------------------
    if "titan"  in host :
        mail_flag = " --mail-user hannah6@llnl.gov  -M end -M fail "
        # os.system(cdcmd+"./xmlchange -file env_batch.xml -id BATCH_COMMAND_FLAGS -val \" "+mail_flag+"\" ")
        os.system(cdcmd+"./xmlchange -file env_batch.xml -id BATCH_COMMAND_FLAGS -val \"\" ")
        if acct == "csc249" :
            os.system(cdcmd+subfile+" -a '-A csc249adse15'   "+mail_flag)
        else :
            os.system(cdcmd+subfile+mail_flag)
    else :
        os.system(cdcmd+subfile)
    
#==================================================================================================
#==================================================================================================
# del case_dir

