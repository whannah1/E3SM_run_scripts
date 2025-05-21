#!/usr/bin/env python
#====================================================================================================================================================
#  Jan, 2018 - Walter Hannah - Lawrence Livermore National Lab
#  This script runs atmosphere only simulations of E3SM for RCEMIP
#====================================================================================================================================================
import sys
import os
import fileinput
import subprocess
import run_E3SM_common as E3SM_common

home = E3SM_common.get_home_dir()
host = E3SM_common.get_host_name()
acct = E3SM_common.get_host_acct(host)

newcase,config,build,runsim,clean,mk_nml,copyinit,use_GNU,use_intel,drop_opt,lower_dt = False,False,False,False,False,False,False,False,False,False,False
debug,debug_w_opt,debug_log,debug_ddt,test_run,debug_queue,inc_remap,debug_chks,disable_bfb = False,False,False,False,False,False,False,False,False
#====================================================================================================================================================
#====================================================================================================================================================

newcase  = True
# clean    = True
config   = True
build    = True
mk_nml   = True
runsim   = True

# use_GNU     = True       # use the GNU compiler (override the default)
use_intel   = True       # use the intel compiler (override the default)
# copyinit    = True       # copy new initialization files for branch run
# test_run    = True       # special output mode 
# debug       = True       # enable debug mode
# debug_w_opt = True       # enable debug mode - retain O2 optimization - use with debug = True
# debug_queue = True       # use debug queue
# debug_log   = True       # enable debug output in log files (adds WH_DEBUG flag)
# debug_ddt   = True       # also change ntask for running DDT - only works with debug 
# drop_opt    = True       # Reduce optimization in Macros file                 requires rebuild
# lower_dt    = True       # Reduce timestep by half (from 20 to 10 minutes)    requires re-config

# debug_chks  = True       # enable state_debug_checks (namelist)
# inc_remap   = True       # Increase vertical remap parameter to reduce timestep via atm namelist
# disable_bfb = True       # Use this to get past a random crash (slightly alters the weather of the restart)

#--------------------------------------------------------
#--------------------------------------------------------
# case_num = "00"     # control - all current defaults  
# case_num = "01"     # use RCEMIP to set coszrs in cam/src/utils/orbit.F90 + solar_const=551.58
# case_num = "02"     # ???

case_num = "s1_00"    # testing Ben's RRTMGP branch - rotation enabled?
# case_num = "s1_01"    # testing Ben's RRTMGP branch - no rotation

# case_num = "s1_50"    # control
# case_num = "s1_51"    # PHYS_GRID_REDUCED_TEST
# case_num = "s1_52"    # PHYS_GRID_1x1_TEST
# case_num = "s1_53"    # PHYS_GRID_1x1_TEST w/ less cores

#--------------------------------------------------------
#--------------------------------------------------------

sst = 300
exp = "RCEMIP_"+str(sst)+"K"

cld = "SP1"     # ZM / SP1 / SP2
res = "ne30"    # ne30 / ne16 / ne4 
# res = "ne4pg1"
# res = "ne30pg1"


cflag = "FALSE"                      # Don't forget to set this!!!! 
# cflag = "TRUE"

# if "ZM" in cld : ndays,resub = (73*2),1 #(5)       # 5=2yr, 15=6yr, 25=10yr
if "ZM" in cld : ndays,resub = 73,0
# if "SP" in cld : ndays,resub = 5,(6*1-1 )       # 3 months
# if "SP" in cld : ndays,resub = 10,3
if "SP" in cld and res=="ne30"    : ndays,resub =  5,1
if "SP" in cld and res=="ne30pg1" : ndays,resub = 10,0


wall_time = "4:00:00"
# wall_time = "0:30:00"

# crm_nx,crm_ny,mod_str = 48,1,"_4km"
crm_nx,crm_ny,mod_str = 64,1,"_1km"
# crm_nx,crm_ny,mod_str = 128,1,"_1km"

#--------------------------------------------------------
# Special Cases
#--------------------------------------------------------

debug_wall_time =  "0:30:00"        # special limit for debug queue
if "SP" in cld : debug_nsteps = 10  # for debug mode use steps instead of days
if "ZM" in cld : debug_nsteps = 72  

if debug : resub = 1                # set resubmissions for debug mode

if "ZM" in cld : mod_str = ""

#--------------------------------------------------------
# Set the case name
#--------------------------------------------------------

if "SP" in cld : 
    crmdim = "_"+str(crm_nx)+"x"+str(crm_ny) 
else : 
    crmdim = ""

case_name = "E3SM_"+exp+"_"+res+"_"+cld+crmdim+mod_str+"_"+case_num

#====================================================================================================================================================
# Various settings for account / system / directories
#====================================================================================================================================================
top_dir     = home+"/E3SM/"
srcmod_dir  = top_dir+"mod_src/"
nmlmod_dir  = top_dir+"mod_nml/"

src_dir = home+"/E3SM/E3SM_SRC_master"
if "s1"  in case_num : src_dir = home+"/E3SM/E3SM_SRC1"
if "s2"  in case_num : src_dir = home+"/E3SM/E3SM_SRC2"

scratch_dir = E3SM_common.get_scratch_dir(host,acct)

run_dir = scratch_dir+"/"+case_name+"/run"

num_dyn = E3SM_common.get_num_dyn(res)

dtime = 20*60

if lower_dt : dtime = 5*60

ncpl  = 86400 / dtime

os.system("cd "+top_dir)
case_dir  = top_dir+"Cases/"+case_name 
cdcmd = "cd "+case_dir+" ; "
print
print("  case : "+case_name)
print
#====================================================================================================================================================
#====================================================================================================================================================
# Create new case
#====================================================================================================================================================
#====================================================================================================================================================

case_obj = E3SM_common.Case( case_name=case_name, res=res, cld=cld, case_dir=case_dir )

compset_opt = " -compset FC5AV1C-L "
if res=="ne30"or res=="ne16" or res=="ne4" : 
    grid_opt = res+"_"+res
else:
    grid_opt = res
    

use_SP_compset = False
# if cld=="SP1" : compset_opt = " -compset FSP1V1 " ; use_SP_compset = True
# if cld=="SP2" : compset_opt = " -compset FSP2V1 " ; use_SP_compset = True
    
if "RCEMIP" in exp :
    if cld=="ZM"  : compset_opt = " -compset FC5AV1C-L-AQUA "
    if cld=="SP1" : compset_opt = " -compset SP1V1-AQUA "  


if newcase == True:

    if host=="titan" : os.system("echo '"+acct+"' > "+home+"/.cesm_proj")         # change project on titan

    newcase_cmd = src_dir+"/cime/scripts/create_newcase"
    cmd = newcase_cmd+" -case "+case_dir+" "+compset_opt+" -res "+grid_opt+" -mach  "+host
    if use_GNU   : cmd = cmd + " -compiler gnu "
    if use_intel : cmd = cmd + " -compiler intel "
    print("\n"+cmd+"\n")
    os.system(cmd)

    if host=="titan" and acct == "csc249" : os.system("echo 'CSC249ADSE15' > "+home+"/.cesm_proj")       # change project name back for csc249


case_dir = case_dir+"/"

### set location and file name for initialization
if host=="titan" :
    init_dir = "/lustre/atlas/scratch/hannah6/"+acct+"/init_files/"
    if acct == "cli115" :  init_dir = "/lustre/atlas1/cli115/scratch/hannah6/init_files/"
    cami_file = "default"
if host=="edison" or host=="cori-knl" :
    init_dir = "/global/cscratch1/sd/whannah/acme_scratch/init_files/"
    cami_file = "default"


if "RCEMIP" in exp :
    # sst_data_filename = "RCEMIP_sst."+res+"."+str(sst)+"K.nc"
    sst_data_filename = "RCEMIP_sst."+str(sst)+"K.nc"
    if "ne30" in res : cami_file = "cami_mam3_Linoz_ne30np4_L72_c160214_RCEMIP.nc"
    if "ne4" in res  : cami_file = "cami_mam3_Linoz_ne4np4_L72_c160909_RCEMIP.nc"

    if res=="ne16np8" : cami_file = "cami_ne16np8_L72_RCEMIP.nc"

#====================================================================================================================================================
#====================================================================================================================================================
# Configure the case
#====================================================================================================================================================
#====================================================================================================================================================
if config == True:
    #------------------------------------------------
    # set vertical levels
    #------------------------------------------------
    nlev_gcm = 72
    nlev_crm = 58
    
    crm_adv = "MPDATA"

    crm_dt = 5

    crm_dx = -1
    if mod_str == "_4km"  : crm_dx = 4000
    if mod_str == "_2km"  : crm_dx = 2000
    if mod_str == "_1km"  : crm_dx = 1000
    if mod_str == "_0.5km": crm_dx = 500

    #------------------------------------------------
    # set CAM_CONFIG_OPTS
    #------------------------------------------------

    cam_opt = E3SM_common.get_default_config( cld, nlev_gcm, nlev_crm, crm_nx, crm_ny, crm_dx )

    if cld=="ZM" : 
        cam_opt = " -rad rrtmg -nlev "+str(nlev_gcm)+"  -clubb_sgs -microphys mg2 -chem none "
        # cam_opt = " -rad rrtmg -nlev "+str(nlev_gcm)+" -microphys mg1 -chem none "
        
        cpp_opt = " -cppdefs ' -DRCEMIP "

    
    if "SP" in cld :
        # cpp_opt = " -cppdefs ' -DAPPLY_POST_DECK_BUGFIXES -DSP_TK_LIM  -DSP_ESMT -DSP_USE_ESMT -DSP_ORIENT_RAND "
        cpp_opt = " -cppdefs ' -DSP_ORIENT_RAND -DRCEMIP "

        #-------------------------------
        # Special cases
        #-------------------------------


        #-------------------------------
        #-------------------------------

    # if cld=="ZM" :
    #     cam_opt = " -rad rrtmg -nlev "+str(nlev_gcm)+"  -clubb_sgs -microphys mg2 "
    #     # chem_opt = " -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates "
    #     ### use prescribed aerosols
    #     chem_opt = " -chem none "
    #     # cpp_opt = ""
    #     cpp_opt = " -cppdefs ' -DAPPLY_POST_DECK_BUGFIXES -DRCEMIP "
    #     cam_crm_rad_opt = ""
    # if "SP" in cld :
    #     ### set options common to all SP setups
    #     cam_opt = " -phys cam5 -use_SPCAM  -rad rrtmg  -nlev "+str(nlev_gcm)+"  -crm_nz "+str(nlev_crm)+" -crm_adv "+crm_adv+" "\
    #              +" -crm_nx "+str(crm_nx)+" -crm_ny "+str(crm_ny)+" -crm_dx "+str(crm_dx)+" -crm_dt "+str(crm_dt)
    #     ### 1-moment microphysics
    #     if cld=="SP1" : cam_opt = cam_opt + " -SPCAM_microp_scheme sam1mom   " 
    #     ### 2-moment microphysics
    #     if cld=="SP2" : cam_opt = cam_opt + " -SPCAM_microp_scheme m2005  " 
    #     #-------------------------------
    #     #-------------------------------
    #     ### Use mg2 since mg1 isn't supported anymore
    #     cam_opt = cam_opt + " -microphys mg2 "
    #     ### reduce rad columns by factor of 8
    #     # cam_crm_rad_opt = " -crm_nx_rad 8 -crm_ny_rad 1 "
    #     cam_crm_rad_opt = " "
    #     cam_opt = cam_opt+cam_crm_rad_opt
    #     ### use prescribed aerosols
    #     chem_opt = " -chem none "
    #     ### set default CPP variables
    #     # cpp_opt = " -cppdefs ' -DAPPLY_POST_DECK_BUGFIXES -DSP_TK_LIM  -DSP_ESMT -DSP_USE_ESMT -DSP_ORIENT_RAND "
    #     cpp_opt = " -cppdefs ' -DSP_ORIENT_RAND -DRCEMIP "
    #     # cpp_opt = cpp_opt+" -DSPMOMTRANS "
    #     #-------------------------------
    #     # Special cases
    #     #-------------------------------
    #     # if case_num in ['00d'] : cpp_opt = cpp_opt+"  -DSP_AERO_BUG_FX "
    #     # if case_num=='03' : cpp_opt = cpp_opt+" -DSP_USE_DIFF "   # enable normal GCM thermodynamic diffusion
    #     # if case_num=='05' : cpp_opt = cpp_opt+" -DSP_FLUX_BYPASS  "
    #     # if cld=="SP1" and any(c in case_num for c in ['']) :
    #     #     cam_opt = cam_opt.replace("-microphys mg2"," ")          # CAMRT doesn't play nice with MG2, so remove it - revert to default RK
    #     #     cam_opt = cam_opt.replace("-rad rrtmg","-rad camrt")
    #     #     chem_opt = " -chem none"
    #     #-------------------------------
    #     #-------------------------------
    #     ### use all columns for radiation with CAMRT
    #     if " camrt " in cam_opt : cam_opt = cam_opt.replace(cam_crm_rad_opt,"")
    # cam_opt = cam_opt+chem_opt+cpp_opt+" ' "

    ### Switch to RRMTGP
    if "RCEMIP" in exp : cam_opt = cam_opt.replace("-rad rrtmg","-rad rrtmgp")
    # if case_num == "s1_00" : cam_opt = cam_opt.replace("-rad rrtmg","-rad rrtmgp")
    # if case_num == "s1_01" : cam_opt = cam_opt.replace("-rad rrtmg","-rad rrtmgp")

    #-------------------------------
    # Special cases
    #-------------------------------
    # if case_num == "s1_51" : cpp_opt = cpp_opt+" -DPHYS_GRID_REDUCED_TEST "
    # if case_num == "s1_52" : cpp_opt = cpp_opt+" -DPHYS_GRID_1x1_TEST "
    # if case_num == "s1_53" : cpp_opt = cpp_opt+" -DPHYS_GRID_1x1_TEST "

    if "pg1" in res : cpp_opt = cpp_opt+" -DPHYS_GRID_1x1_TEST "


    #-------------------------------
    #-------------------------------

    cam_opt = cam_opt+cpp_opt+" ' "


    if cld=="ZM" or ( "SP" in cld and not use_SP_compset ) : 
        print("------------------------------------------------------------")
        CMD = cdcmd+"./xmlchange --file env_build.xml --id CAM_CONFIG_OPTS --val \""+cam_opt+"\""
        print(CMD)
        os.system(CMD)
        print("------------------------------------------------------------")

    #--------------------------------------------------------
    # Specified SST 
    #--------------------------------------------------------
    if "RCEMIP" in exp :
        os.system(cdcmd+"./xmlchange -file env_run.xml -id SSTICE_DATA_FILENAME -val "+init_dir+sst_data_filename)

    #------------------------------------------------
    # update cami file if not equal to "default"
    #------------------------------------------------
    if cami_file != "default" :
        ### copy file to scratch
        CMD = "cp ~/E3SM/init_files/"+cami_file+" "+init_dir
        print(CMD)
        os.system(CMD)
        ### write file path to namelist
        # nfile = case_dir+"user_nl_cam"
        # file = open(nfile,'w')
        # file.write(" ncdata  = '"+init_dir+cami_file+"' \n ") 
        # file.close() 
    #------------------------------------------------
    # set run-time variables
    #------------------------------------------------
    # start_date = "0000-01-01"
    # os.system(cdcmd+"./xmlchange --file env_run.xml   --id RUN_STARTDATE  --val "+start_date)

    if host=="titan" :
        # if acct != "cli115" : os.system(cdcmd+"./xmlchange --file env_run.xml --id RUNDIR  --val "+workdir+"/"+acct+"/"+case_name+"/run ")
        if acct == "cli115" : os.system(cdcmd+"./xmlchange --file env_run.xml --id RUNDIR  --val /lustre/atlas1/cli115/scratch/hannah6/"+case_name+"/run ")
        if acct == "csc249" : os.system(cdcmd+"./xmlchange --file env_run.xml --id RUNDIR  --val /lustre/atlas/scratch/hannah6/csc249/" +case_name+"/run ")
        

    if host=="anvil" :
        scratch_root_dir   = "/lcrc/group/acme/whannah/E3SM_simulations/"
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

    if "cori" in host :
        ### Don't explicitly set NTASKS for other components on cori
        case_obj.xmlchange("env_mach_pes.xml", "NTASKS_ATM",  num_dyn )
        if res=="ne16np8"  : 
            case_obj.xmlchange("env_mach_pes.xml", "NTASKS_ATM",  1536 )
            case_obj.xmlchange("env_mach_pes.xml", "NTASKS_OCN",  1536 )
            case_obj.xmlchange("env_mach_pes.xml", "NTASKS_ICE",  1536 )
            case_obj.xmlchange("env_mach_pes.xml", "NTASKS_ROF",  1536 )
        if "pg1" in res :
            case_obj.set_NTASKS_all(1)
            case_obj.xmlchange("env_mach_pes.xml", "NTASKS_CPL", num_dyn )
            case_obj.xmlchange("env_mach_pes.xml", "NTASKS_ATM", num_dyn )
            case_obj.xmlchange("env_mach_pes.xml", "NTASKS_OCN", num_dyn )

            if case_num == "s1_53" :
                case_obj.xmlchange("env_mach_pes.xml", "NTASKS_CPL", num_dyn/2 )
                case_obj.xmlchange("env_mach_pes.xml", "NTASKS_ATM", num_dyn/2 )
                case_obj.xmlchange("env_mach_pes.xml", "NTASKS_OCN", num_dyn/2 )
        
    elif "edison" in host :
        case_obj.set_NTASKS_all(num_dyn)
        case_obj.xmlchange("env_mach_pes.xml", "NTASKS_ATM",  num_dyn )
        

    ### Make sure threading is off for SP
    if "SP" in cld : case_obj.set_NTHRDS_all(1)

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
    if use_intel :
        CMD = cdcmd+"./xmlchange --file env_build.xml --id COMPILER --val \"intel\" "
        print(CMD)
        os.system(CMD)
    #------------------------------------------------
    #------------------------------------------------
    if "pg1" in res :
        case_obj.xmlchange("env_build.xml", "ATM_NX", num_dyn )
        case_obj.xmlchange("env_build.xml", "OCN_NX", num_dyn )
        case_obj.xmlchange("env_build.xml", "ICE_NX", num_dyn )
    #------------------------------------------------
    # configure the case
    #------------------------------------------------
    if os.path.isfile(case_dir+"case.setup") :
        if clean : os.system(cdcmd+"./case.setup --clean")
        os.system(cdcmd+"./case.setup")
    else :
        os.system(cdcmd+"./cesm_setup")     # older versions
    
#====================================================================================================================================================
#====================================================================================================================================================
# Build the model
#====================================================================================================================================================
#====================================================================================================================================================
if build == True:
    #os.system(cdcmd+"cp "+srcmod_dir+"* ./SourceMods/src.cam/")    # copy any modified source code

    #----------------------------------------------------------
    # Make sure optimization is set correctly in Macros file
    #----------------------------------------------------------
    # macros_file = case_dir+"Macros.make"
    # f = open(macros_file, "r")
    # contents = f.readlines()
    # f.close()
    # index_debug_n = -1
    # index_debug_y = -1
    # # Find lines for compiler optimization settings for both debug and non-debug modes
    # for num, line in enumerate(contents, 1):
    #     if "ifeq ($(DEBUG), FALSE)" in line: index_debug_n = num
    #     if "ifeq ($(DEBUG), TRUE)"  in line: index_debug_y = num
    # # modify setting for standard non-debug mode
    # if index_debug_n > 0 :    
    #     if drop_opt : 
    #         contents[index_debug_n] = "   FFLAGS +=  -O0 \n"
    #     else :
    #         contents[index_debug_n] = "   FFLAGS +=  -O2 \n"
    # # modify setting for standard debug mode
    # if index_debug_y > 0 :    
    #     if debug_w_opt : 
    #         contents[index_debug_y] = "   FFLAGS +=  -O2 \n"
    #     else :
    #         contents[index_debug_y] = "   FFLAGS +=  -O0 \n"
    # f = open(macros_file, "w")
    # contents = "".join(contents)
    # f.write(contents)
    # f.close()
    #----------------------------------------------------------
    #----------------------------------------------------------

    if use_GNU   : case_obj.xmlchange("env_build.xml", "COMPILER", " \"gnu\" " )
    if use_intel : case_obj.xmlchange("env_build.xml", "COMPILER", " \"intel\" " )

    if debug :
        case_obj.xmlchange("env_build.xml", "DEBUG", "TRUE" )
        # os.system(cdcmd+"./xmlchange -file env_build.xml   -id DEBUG   -val TRUE")
    else :
        case_obj.xmlchange("env_build.xml", "DEBUG", "FALSE" )
        # os.system(cdcmd+"./xmlchange -file env_build.xml   -id DEBUG   -val FALSE")

    if os.path.isfile(case_dir+"case.build") :
        if clean : os.system(cdcmd+"./case.build --clean")                  # Clean previous build    
        os.system(cdcmd+"./case.build")
    else :
        os.system(cdcmd+"./"+case_name+".clean_build")
        os.system(cdcmd+"./"+case_name+".build")


    # if "titan"  in host : 
    #     # os.system(cdcmd+"./xmlchange -file env_build.xml   -id CESMSCRATCHROOT   -val $ENV{MEMBERWORK}/"+acct
    #     # if acct == "csc249" : os.system(cdcmd+"./xmlchange -file env_build.xml   -id CIME_OUTPUT_ROOT  -val "+workdir+"/"+acct)
    #     if acct == "cli115" : os.system(cdcmd+"./xmlchange -file env_build.xml   -id CIME_OUTPUT_ROOT  -val /lustre/atlas1/cli115/scratch/hannah6/")
    #     if acct == "csc249" : os.system(cdcmd+"./xmlchange -file env_build.xml   -id CIME_OUTPUT_ROOT  -val /lustre/atlas/scratch/hannah6/csc249/" )

    # if use_GNU :
    #     CMD = cdcmd+"./xmlchange --file env_build.xml --id COMPILER --val \"gnu\" "
    #     print(CMD)
    #     os.system(CMD)

    # if debug :
    #     os.system(cdcmd+"./xmlchange -file env_build.xml   -id DEBUG   -val TRUE")
    # else :
    #     os.system(cdcmd+"./xmlchange -file env_build.xml   -id DEBUG   -val FALSE")

    # if os.path.isfile(case_dir+"case.build") :
    #     if clean : os.system(cdcmd+"./case.build --clean")                  # Clean previous build    
    #     os.system(cdcmd+"./case.build")
    # else :
    #     os.system(cdcmd+"./"+case_name+".clean_build")
    #     os.system(cdcmd+"./"+case_name+".build")

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
#         ref_case = "E3SM_SP2_CTL_ne30_03"
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



# if copyinit == True:
#     if exp == "ERS" and case_num in ['01'] : 
#         # ref_case = "E3SM_SP1_ERS_ne30_64x1_4km_00"
#         ref_case = "E3SM_"+cld+"_"+exp+"_"+res+crmdim+mod_str+"_00" 
#         ref_date = "2000-01-05"
#         os.system(cdcmd+"./xmlchange -file env_run.xml     -id RUN_TYPE    -val branch")
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
    (din_loc_root   , err) = subprocess.Popen(cdcmd+"./xmlquery DIN_LOC_ROOT    -value", stdout=subprocess.PIPE, shell=True).communicate()

    ### remove extra spaces to simplify string query
    cam_config_opts = ' '.join(cam_config_opts.split())

    nfile = case_dir+"user_nl_cam"
    file = open(nfile,'w') 

    #------------------------------
    # Special test mode 
    #------------------------------
    if test_run :
        file.write(" nhtfrq    = 0,-1 \n") 
        file.write(" mfilt     = 1,"+str(ncpl)+" \n")   # make sure each file has 1-day worth of data
        # file.write(" nhtfrq    = 0,-1 \n") 
        # file.write(" mfilt     = 1,24 \n")   

        file.write(" fincl2    = 'PS','TS'")
        file.write(             ",'T','Q','Z3'")            # thermodynamic components
        file.write(             ",'U','V','OMEGA'")         # velocity components
        file.write(             ",'QRL','QRS'")             # Full radiative heating profiles
        file.write(             ",'FDS','FUS','FDL','FUL'") # Full radiative flux profiles
        file.write(             ",'FSNT','FLNT'")           # Net TOM heating rates
        file.write(             ",'FLNS','FSNS','SOLIN' ")  # Surface rad for total column heating
        file.write(             ",'FSNTC','FLNTC'")         # clear sky heating rates for CRE
        file.write(             ",'LHFLX','SHFLX'")         # surface fluxes
        # file.write(             ",'TAUX','TAUY'")
        file.write(             ",'SOLIN' ")                # solar insolation (pobably not accurate)
        file.write(             ",'PRECT','TMQ'")
        file.write(             ",'LWCF','SWCF'")           # cloud radiative foricng
        # file.write(             ",'COSZRS'")
        file.write(             ",'UBOT','VBOT','QBOT','TBOT'")
        # file.write(             ",'UAP','VAP','QAP','QBP','TAP','TBP','TFIX'")
        file.write(             ",'CLOUD','CLDLIQ','CLDICE' ")
        # file.write(             ",'QEXCESS' ")
        # file.write(             ",'PTTEND' ")
        # file.write(             ",'O3','LINOZ_DO3','LINOZ_O3COL' ")
        # file.write(             ",'Mass_bc','Mass_dst','Mass_ncl','Mass_so4','Mass_pom','Mass_soa','Mass_mom' ")
        if "SP" in cld :
            file.write(             ",'SPDT','SPDQ' ")
            # file.write(             ",'CRM_T','CRM_QV','CRM_QC','CRM_QPC','CRM_PREC' ")
            # file.write(             ",'SPQTFLX','SPQTFLXS'")
            file.write(             ",'SPTLS','SPQTLS' ")
            # file.write(             ",'SPQPEVP','SPMC' ")
            file.write(             ",'SPMCUP','SPMCDN','SPMCUUP','SPMCUDN' ")
            # file.write(             ",'SPTK','SPTKE','SPTKES' ")
            # file.write(             ",'SPQC','SPQR','SPQI','SPQS','SPQG' ")
        file.write("\n")

    #------------------------------
    # Default output
    #------------------------------
    else :
        if cld == "ZM" :
            # Don't waste time with high-freq output for now
            file.write(" nhtfrq    = 0 \n") 
            file.write(" mfilt     = 1 \n")     # h2 = 1 hourly for 5 days
        else:
            file.write(" nhtfrq    = 0,-6,-1 \n") 
            file.write(" mfilt     = 1, 4, 120 \n")     # h2 = 1 hourly for 5 days
            # file.write(" nhtfrq    = 0,-6,-3 \n") 
            # file.write(" mfilt     = 1, 4, 80 \n")      # h2 = 3 hourly for 5 days 
            file.write(" fincl2    = 'PS'") # ,'TS'
            file.write(             ",'T','Q','Z3'")            # thermodynamic components
            file.write(             ",'U','V','OMEGA'")         # velocity components
            file.write(             ",'CLOUD','CLDLIQ','CLDICE'")
            file.write(             ",'QRL','QRS'")             # Full radiative heating profiles
            # file.write(             ",'FDS','FUS','FDL','FUL'") # Full radiative flux profiles (only for h0?)
            file.write(             ",'FSNT','FLNT','FLUT'")    # Net TOM heating rates
            file.write(             ",'FLNS','FSNS'")           # Surface rad for total column heating
            file.write(             ",'FSNTC','FLNTC'")         # clear sky heating rates for CRE
            file.write(             ",'LHFLX','SHFLX'")         # surface fluxes
            file.write(             ",'LWCF','SWCF'")           # cloud radiative foricng
            # file.write(             ",'Mass_bc','Mass_dst','Mass_ncl','Mass_so4','Mass_pom','Mass_soa','Mass_mom' ")
            if "SP" in cld :
                file.write(         ",'SPDT','SPDQ'")
                file.write(         ",'SPQPEVP','SPMC'")
                file.write(         ",'SPMCUP','SPMCDN','SPMCUUP','SPMCUDN'")
                # if any(x in cam_config_opts for x in ["SP_ESMT","SP_USE_ESMT","SPMOMTRANS"]) : 
                #     file.write(",'ZMMTU','ZMMTV','uten_Cu','vten_Cu' ")
                if "SP_USE_ESMT" in cam_config_opts : file.write(",'U_ESMT','V_ESMT'")
                if "SPMOMTRANS"  in cam_config_opts : file.write(",'UCONVMOM','VCONVMOM'")
            file.write("\n")
            file.write(" fincl3    = 'PRECT','TMQ' ")
            # file.write(            ",'LHFLX','SHFLX'")
            
            file.write("\n")


    if cami_file != "default" : file.write(" ncdata  = '"+init_dir+cami_file+"' \n")         
    
    file.write(" srf_flux_avg = 1 \n")

    # if any(c in case_num for c in ['00o','00p']) :
    #     file.write(" srf_flux_avg = 1 \n")
    # else:
    #     file.write(" srf_flux_avg = 0 \n")


    file.write(" dyn_npes = "+str(num_dyn)+" \n")


    # if "chem none" in cam_config_opts :
    #     # prescribed_aero_path = din_loc_root+"/atm/cam/chem/trop_mam/aero"
    #     # prescribed_aero_file = "mam4_0.9x1.2_L72_2000clim_c170323.nc"
    #     prescribed_aero_path = init_dir
    #     prescribed_aero_file = "RCEMIP_aero.v1.nc"
    #     file.write(" use_hetfrz_classnuc = .false. \n")
    #     file.write(" aerodep_flx_type = 'CYCLICAL' \n")
    #     file.write(" aerodep_flx_datapath = '"+prescribed_aero_path+"' \n")
    #     file.write(" aerodep_flx_file = '"+prescribed_aero_file+"' \n")
    #     file.write(" aerodep_flx_cycle_yr = 01 \n")
    #     file.write(" prescribed_aero_type = 'CYCLICAL' \n")
    #     file.write(" prescribed_aero_datapath='"+prescribed_aero_path+"' \n")
    #     file.write(" prescribed_aero_file = '"+prescribed_aero_file+"' \n")
    #     file.write(" prescribed_aero_cycle_yr = 01 \n")

    prescribed_aero_path = init_dir
    prescribed_aero_file = "RCEMIP_aero.v1.nc"
    file.write(" use_hetfrz_classnuc = .false. \n")
    file.write(" aerodep_flx_type = 'CYCLICAL' \n")
    file.write(" aerodep_flx_datapath = '"+prescribed_aero_path+"' \n")
    file.write(" aerodep_flx_file = '"+prescribed_aero_file+"' \n")
    file.write(" aerodep_flx_cycle_yr = 01 \n")
    file.write(" prescribed_aero_type = 'CYCLICAL' \n")
    file.write(" prescribed_aero_datapath='"+prescribed_aero_path+"' \n")
    file.write(" prescribed_aero_file = '"+prescribed_aero_file+"' \n")
    file.write(" prescribed_aero_cycle_yr = 01 \n")


    if cld=="ZM" :
        file.write(" micro_do_nccons = .true. \n")
        file.write(" micro_do_nicons = .true. \n")
        micro_nccons_val  = "70.0D6"        # cons_droplet value for liquid
        micro_nicons_val  = "0.0001D6"      # cons_droplet value for ice
        file.write(" micro_nccons = "+micro_nccons_val+" \n")
        file.write(" micro_nicons = "+micro_nicons_val+" \n")
        

    #------------------------------
    # Dycore tuning parameters
    #------------------------------

    ### default values
    if res=="ne30" :
        # hyper_nu          = 1.0e15
        # hyper_nu_p        = 1.0e15
        # hyper_nu_div      = 2.5e15
        # hyper_nu_q        = -1.0
        # hyper_nu_top      = 2.5e5
        qsplit            = 1 
        rsplit            = 3 
        se_nsplit         = 2
        hypervis_subcycle = 3

    ### reduce rsplit to maintain 5 min dynamics step
    if dtime == (20*60) : rsplit = 2

    if res=="ne16np8" :
        hyper_nu          = 5.0e14
        hyper_nu_p        = hyper_nu
        hyper_nu_div      = hyper_nu
        qsplit            = 1 
        rsplit            = 5 
        se_nsplit         = 5
        hypervis_subcycle = 3


    ### inc_remap affects the vert remap frequency (also decreases dynamics timestep)
    if inc_remap : se_nsplit = 4


    if 'hyper_nu'          in vars() : file.write(" nu        = "+str(hyper_nu)+" \n") 
    if 'hyper_nu_p'        in vars() : file.write(" nu_p      = "+str(hyper_nu_p)+" \n") 
    if 'hyper_nu_div'      in vars() : file.write(" nu_div    = "+str(hyper_nu_div)+" \n") 
    if 'qsplit'            in vars() : file.write(" qsplit    = "+str(   qsplit)+" \n") 
    if 'rsplit'            in vars() : file.write(" rsplit    = "+str(   rsplit)+" \n") 
    if 'se_nsplit'         in vars() : file.write(" se_nsplit = "+str(se_nsplit)+" \n")
    if 'hypervis_subcycle' in vars() : file.write(" hypervis_subcycle = "+str(hypervis_subcycle)+" \n") 

    #------------------------------
    # RCEMIP namelist settings
    #------------------------------
    if "RCEMIP" in exp :
        topo_file = "RCEMIP_topo."+res+".v1.nc"
        if "pg1" in res : topo_file = "RCEMIP_topo."+res.replace("pg1","")+".v1.nc"

        file.write(" bnd_topo   = '"+init_dir+topo_file+"' \n")

        # file.write(" rad_climate = 'A:Q:H2O', 'N:O2:O2', 'N:CO2:CO2', 'N:ozone:O3', 'N:N2O:N2O', 'N:CH4:CH4' \n")
        # file.write(" prescribed_aero_specifier = '' \n")

        # file.write(" solar_const = 551.58 \n")
        # file.write(" solar_htng_spctrl_scl = .false. \n")

        # Orbital settings need to end up in drv_in
        nfile = case_dir+"user_nl_cpl"
        drv_file = open(nfile,'w') 
        drv_file.write(" orb_mode           = 'fixed_parameters' \n")
        drv_file.write(" orb_eccen          = 0 \n")
        drv_file.write(" orb_obliq          = 0 \n")
        drv_file.write(" orb_mvelp          = 0 \n")
        drv_file.close()

        # file.write(" datvarnames  = 'ice_cov' \n")

        file.write(" prescribed_ozone_cycle_yr   = 2000 \n")
        # file.write(" prescribed_ozone_datapath   = '/project/projectdirs/acme/inputdata/atm/cam/ozone' \n")
        # file.write(" prescribed_ozone_file       = 'ozone_1.9x2.5_L26_2000clim_c091112.nc' \n")
        # file.write(" prescribed_ozone_name       = 'O3' \n")
        file.write(" prescribed_ozone_type       = 'CYCLICAL' \n")

        file.write(" prescribed_ozone_datapath   = '"+init_dir+"' \n")
        file.write(" prescribed_ozone_file       = 'RCEMIP_ozone.v1.nc' \n")
        file.write(" prescribed_ozone_name       = 'O3' \n")
        # file.write(" prescribed_ozone_type       = 'FIXED' \n")

    #------------------------------
    # state_debug_checks
    #------------------------------
    if debug_chks :
        file.write(" state_debug_checks = .true. \n")
    else :
        file.write(" state_debug_checks = .false. \n")

    # file.write(" state_debug_checks = .false. \n")

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
    # Set input and domain files
    #------------------------------
    if "RCEMIP" in exp :

        # update ozone file in case it got scrubbed
        CMD = "cp -u "+home+"/E3SM/init_files/RCEMIP_ozone.v1.nc "+init_dir
        print(CMD)
        os.system(CMD)

        # update aerosol file in case it got scrubbed
        CMD = "cp -u "+home+"/E3SM/init_files/RCEMIP_aero.v1.nc "+init_dir
        print(CMD)
        os.system(CMD)

        # update topo file in case it got scrubbed
        CMD = "cp -u "+home+"/E3SM/init_files/"+topo_file+" "+init_dir
        print(CMD)
        os.system(CMD)

        # update domain files in case they got scrubbed
        if res=="ne30" :
            domain_ocn_file = "RCEMIP_domain.ocn.ne30np4_gx1v6.v1.nc"
            domain_lnd_file = "RCEMIP_domain.lnd.ne30np4_gx1v6.v1.nc"
        if res=="ne4" :
            domain_ocn_file = "RCEMIP_domain.ocn.ne4np4_oQU240.160614.nc"
            domain_lnd_file = "RCEMIP_domain.lnd.ne4np4_oQU240.160614.nc"
        if res=="ne16np8" :
            domain_ocn_file = "RCEMIP_domain.ocn.ne16np8.nc"
            domain_lnd_file = "RCEMIP_domain.lnd.ne16np8.nc"
        
        if res=="ne4pg1"  :
            domain_ocn_file = "RCEMIP_domain.ocn.ne4np1.nc"
            domain_lnd_file = "RCEMIP_domain.lnd.ne4np1.nc"
        if res=="ne30pg1"  :
            domain_ocn_file = "RCEMIP_domain.ocn.ne30np1.nc"
            domain_lnd_file = "RCEMIP_domain.lnd.ne30np1.nc"

        CMD = "cp -u "+home+"/E3SM/init_files/"+domain_ocn_file+" "+init_dir
        print(CMD)
        os.system(CMD)

        CMD = "cp -u "+home+"/E3SM/init_files/"+domain_lnd_file+" "+init_dir
        print(CMD)
        os.system(CMD)

        # update xml entries for domain file names and paths
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id ATM_DOMAIN_PATH  -val "+init_dir)
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id OCN_DOMAIN_PATH  -val "+init_dir)
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id ICE_DOMAIN_PATH  -val "+init_dir)
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id LND_DOMAIN_PATH  -val "+init_dir)

        os.system(cdcmd+"./xmlchange -file env_run.xml   -id ATM_DOMAIN_FILE  -val "+domain_ocn_file)
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id OCN_DOMAIN_FILE  -val "+domain_ocn_file)
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id ICE_DOMAIN_FILE  -val "+domain_ocn_file)
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id LND_DOMAIN_FILE  -val "+domain_lnd_file)
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id LND_DOMAIN_FILE  -val UNSET ")
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id ROF_DOMAIN_FILE  -val UNSET ")
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id WAV_DOMAIN_FILE  -val UNSET ")
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id GLC_DOMAIN_FILE  -val UNSET ")
        

        # update sst data file in case it got scrubbed
        CMD = "cp -u "+home+"/E3SM/init_files/"+sst_data_filename+" "+init_dir
        print(CMD)
        os.system(CMD)

        # update xml entry for the SST file
        os.system(cdcmd+"./xmlchange -file env_run.xml -id SSTICE_DATA_FILENAME -val "+init_dir+sst_data_filename)

#====================================================================================================================================================
#====================================================================================================================================================
# Run the simulation
#====================================================================================================================================================
#====================================================================================================================================================
if runsim == True:

    CMD = ''
    if acct == "csc249" : CMD = cdcmd+"./xmlchange --file env_batch.xml --id CHARGE_ACCOUNT --val \"CSC249ADSE15\" "
    if acct == "cli115" : CMD = cdcmd+"./xmlchange --file env_batch.xml --id CHARGE_ACCOUNT --val \"CLI115\"  "
    print(CMD)
    if CMD != '' : os.system(CMD)

    runfile = case_dir+"case.run"
    subfile = case_dir+"case.submit"

    ### CIME updates changed the run file name - prependend a "."
    if not os.path.isfile(runfile) : runfile = case_dir+".case.run"

    #------------------------------------------------
    # make sure cami file is up to date
    #------------------------------------------------
    if cami_file != "default" :
        ### copy file to scratch
        CMD = "cp ~/E3SM/init_files/"+cami_file+" "+init_dir
        print(CMD)
        os.system(CMD)

    #------------------------------
    # Change run options
    #------------------------------
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_OPTION  -val ndays ")
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_N       -val "+str(ndays)) 
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id RESUBMIT     -val "+str(resub))
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id CONTINUE_RUN -val "+cflag)

    if debug :
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_OPTION  -val nsteps ")
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_N       -val "+str(debug_nsteps)) 

    #------------------------------
    # Change the BFB flag for certain runs
    #------------------------------
    if disable_bfb : 
        os.system(cdcmd+"./xmlchange -file env_run.xml -id BFBFLAG -val FALSE")
    else :
        os.system(cdcmd+"./xmlchange -file env_run.xml -id BFBFLAG -val TRUE")

    #------------------------------
    # switch to debug queue
    # but check if a run is already in the dbug queue
    #------------------------------    
    if host=="titan"  : os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val batch")
    # if host=="edison" : os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val normal")

    if host=="edison" or host=="cori-knl" :
        if debug_queue :
            os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val debug")
            wall_time = debug_wall_time
        else :
            os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val regular")

    if debug_queue and host=="titan" :
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
            wall_time = debug_wall_time

    #------------------------------
    # DEBUG LEVEL
    #------------------------------
    if debug :
        # level of debug output, 0=minimum, 1=normal, 2=more, 3=too much
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id INFO_DBUG -val 2")

        # for debug mode, make sure that we will get a core dump file 
        # in the event that we get a segmentation fault
        f = open(runfile, "r")
        contents = f.readlines()
        f.close()

        index = -1
        print
        for num, line in enumerate(contents, 1):
            if "def _main_func(description):" in line :
                index = num+1
                print("DEBUG MODE: found line in run file!  "+str(index))
            if "resource.setrlimit" in line: 
                index = -1  # this means the resource limit was already set
                print("DEBUG MODE: core dump resource already set in run file!")

        print("DEBUG MODE: run file index = "+str(index) )
        print

        if index > 0 :
            contents.insert(index  , "    import resource \n")
            contents.insert(index+1, "    resource.setrlimit(resource.RLIMIT_CORE, (resource.RLIM_INFINITY, resource.RLIM_INFINITY)) \n")
            contents.insert(index+2, "    \n")

            f = open(runfile, "w")
            contents = "".join(contents)
            f.write(contents)
            f.close()
        # else:
            # print("\n    WARNING: couldn't find line for resource limit in run file: \n"+runfile+" \n")
            # print("\n    ERROR: couldn't find line for resource limit in run file: \n"+runfile+" \n")
            # exit()

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
    os.system(cdcmd+"./xmlchange -file env_batch.xml -id JOB_WALLCLOCK_TIME -val "+wall_time)

    #------------------------------
    # Submit the run
    #------------------------------
    if "titan"  in host :
        # mail_flag = ""
        mail_flag = " --mail-user hannah6@llnl.gov  -M end -M fail "
        # os.system(cdcmd+"./xmlchange -file env_batch.xml -id BATCH_COMMAND_FLAGS -val \" "+mail_flag+"\" ")
        os.system(cdcmd+"./xmlchange -file env_batch.xml -id BATCH_COMMAND_FLAGS -val \"\" ")
        if acct == "csc249" :
            os.system(cdcmd+subfile+" -a '-A csc249adse15'   "+mail_flag)
        else :
            os.system(cdcmd+subfile+mail_flag)
    else :
        os.system(cdcmd+subfile)
    

print("")
print("  case : "+case_name)
print("")

#====================================================================================================================================================
#====================================================================================================================================================
#====================================================================================================================================================
#====================================================================================================================================================
