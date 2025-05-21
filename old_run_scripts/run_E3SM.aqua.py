#!/usr/bin/env python
#===============================================================================================================================================================
#  Jan, 2018 - Walter Hannah - Lawrence Livermore National Lab
#  This script runs atmosphere only simulations of E3SM
#===============================================================================================================================================================
import sys
import os
import fileinput
import subprocess

home = os.getenv("HOME")
host = os.getenv("HOST")

if "edison" in host : host,acct = "edison"  ,""
if "cori"   in host : host,acct = "cori-knl","m2861"
if "titan"  in host : host,acct = "titan"   ,"cli115"

newcase,config,build,runsim,clean,mk_nml,copyinit,use_GNU,drop_opt,lower_dt = False,False,False,False,False,False,False,False,False,False
debug,debug_w_opt,debug_log,debug_ddt,test_run,debug_queue,inc_remap,debug_chks,disable_bfb = False,False,False,False,False,False,False,False,False
#===============================================================================================================================================================
#===============================================================================================================================================================

# newcase  = True
# clean    = True
# config   = True
# build    = True
mk_nml   = True
runsim   = True

# use_GNU     = True       # use the GNU compiler instead of the default
# copyinit    = True       # copy new initialization files for branch run
test_run    = True       # hourly output only (no h2)
# debug       = True       # enable debug mode
# debug_w_opt = True       # enable debug mode - retain O2 optimization - use with debug = True
# debug_queue = True       # use debug queue
# debug_log   = True       # enable debug output in log files (adds WH_DEBUG flag)
# debug_ddt   = True       # also change ntask for running DDT - only works with debug 
# drop_opt    = True       # Reduce optimization in Macros file                 requires rebuild
# lower_dt    = True       # Reduce timestep by half (from 30 to 15 minutes)    requires re-config

# debug_chks  = True       # enable state_debug_checks (namelist)
# inc_remap   = True       # Increase vertical remap parameter to reduce timestep via atm namelist
# disable_bfb = True       # Use this to get past a random crash (slightly alters the weather of the restart)

#--------------------------------------------------------
#--------------------------------------------------------
# case_num = "00"     # control - all current defaults  


#--------------------------------------------------------
#--------------------------------------------------------
cld = "SP1"    # ZM / SP1 / SP2 / SP2+ECPP
exp = "AQUA"    # CTL / EXP / SOM / AQUA / AQUAP
res = "ne30"   # ne30 / ne16 / ne4 / 0.9x1.25 / 1.9x2.5

cflag = "FALSE"                      # Don't forget to set this!!!! 
# cflag = "TRUE"

if "ZM" in cld : ndays,resub = (73*2),1 #(5)       # 5=2yr, 15=6yr, 25=10yr
if "SP" in cld : ndays,resub = 5,(6*3)      # 3 months

wall_time = "4:00:00"

crm_nx,crm_ny,mod_str = 64,1,"_1km"

#--------------------------------------------------------
# Special Cases
#--------------------------------------------------------
debug_wall_time =  "1:00:00"        # special limit for debug queue
debug_nsteps = 48                  # for debug mode use steps instead of days

if debug : resub = 0    # set resubmissions for debug mode

flux_avg_omit_list = [""]             # list of cases to not set surface flux averaging 

if "ZM" in cld : mod_str = ""

#--------------------------------------------------------
# Special aqua-planet settings
#--------------------------------------------------------
if exp == "AQUA":
    amp = 3
    xc  = 6
    yc  = 4
    if amp == 0 : xc = 0 ; yc = 0

    sst_clat = 0
    wp_clat  = 0
    sst_exp  = "4.0"
    sst_yc   = "1.8"

    mod_str = mod_str+"_wp"+str(amp)+str(xc)+str(yc)

#--------------------------------------------------------
# Set the case name
#--------------------------------------------------------

if "SP" in cld : 
    crmdim = "_"+str(crm_nx)+"x"+str(crm_ny) 
else : 
    crmdim = ""

case_name = "E3SM_"+cld+"_"+exp+"_"+res+crmdim+mod_str+"_"+case_num


#===============================================================================================================================================================
# Various settings for account / system / directories
#===============================================================================================================================================================
top_dir     = home+"/E3SM/"
srcmod_dir  = top_dir+"mod_src/"
nmlmod_dir  = top_dir+"mod_nml/"

src_dir = home+"/E3SM/E3SM_SRC_master"
if "s1"  in case_num : src_dir = home+"/E3SM/E3SM_SRC1"
if "s2"  in case_num : src_dir = home+"/E3SM/E3SM_SRC2"

scratch_dir = os.getenv("CSCRATCH","")
if scratch_dir=="" : 
    if host=="titan" :
        if acct == "cli115" : 
            scratch_dir = "/lustre/atlas1/"+acct+"/scratch/hannah6/"
        else : 
            scratch_dir = "/lustre/atlas/scratch/hannah6/"+acct+"/"

run_dir = scratch_dir+"/"+case_name+"/run"

if res=="ne4"      : num_dyn = 96
if res=="ne16"     : num_dyn = 1536
if res=="ne30"     : num_dyn = 5400

dtime = 20*60

if lower_dt : dtime = 10*60

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
    if res=="ne30" : grid_opt = "ne30_oECv3"

use_SP_compset = False
# if cld=="SP1" : compset_opt = " -compset FSP1V1 " ; use_SP_compset = True
# if cld=="SP2" : compset_opt = " -compset FSP2V1 " ; use_SP_compset = True


if exp == "SOM" :
    if cld=="SP1" : compset_opt = " -compset ESP1V1 "  # SOM compset
    # use_SP_compset = True

if exp == "CPL" :
    if cld=="SP1" : compset_opt = " -compset A_WCYCL1850S_SP1 " # Fully coupled
    use_SP_compset = True

if exp == "AQUA" :
    if cld=="ZM"  : compset_opt = " -compset FC5AV1C-L-AQUA "
    if cld=="SP1" : compset_opt = " -compset SP1V1-AQUA "  
if exp == "AQUAP" :
    if cld=="ZM"  : compset_opt = " -compset FC5AV1C-L-AQUAP " 
    if cld=="SP1" : compset_opt = " -compset SP1V1-AQUAP "  
    use_SP_compset = True
    

if "A_WCYCL" in compset_opt : grid_opt = res+"_oECv3_ICG"


if newcase == True:

    if host=="titan" : os.system("echo '"+acct+"' > "+home+"/.cesm_proj")         # change project on titan

    newcase_cmd = src_dir+"/cime/scripts/create_newcase"
    cmd = newcase_cmd+" -case "+case_dir+" "+compset_opt+" -res "+grid_opt+" -mach  "+host
    if use_GNU : cmd + " -compiler gnu "
    print("\n"+cmd+"\n")
    os.system(cmd)

    if host=="titan" and acct == "csc249" : os.system("echo 'CSC249ADSE15' > "+home+"/.cesm_proj")       # change project name back for csc249


case_dir = case_dir+"/"

### set location and file name for initialization
init_dir = "/lustre/atlas/scratch/hannah6/"+acct+"/init_files/"
if acct == "cli115" :  init_dir = "/lustre/atlas1/cli115/scratch/hannah6/init_files/"
cami_file = "default"

# if case_num in [''] : cami_file = "cami_mam3_Linoz_ne30np4_L64_c160214.nc"


if exp == "AQUA":
    sst_clat_str = str(sst_clat).zfill(2)
    wp_clat_str  = str( wp_clat).zfill(2)
    if sst_clat < 0 : sst_clat_str = str(sst_clat).zfill(3)
    if  wp_clat < 0 :  wp_clat_str = str( wp_clat).zfill(3)

    # data_filename = home+"/E3SM/init_files/sst_aqua_ideal.v1"
    data_filename = "sst_aqua_ideal.v1"
    data_filename = data_filename+".sst_yc_"+sst_yc
    data_filename = data_filename+".sst_exp_"+sst_exp
    data_filename = data_filename+".amp_"+str(amp)+".0.xc_"+str(xc)+".0.yc_"+str(yc)+".0"
    data_filename = data_filename+".wp_clat_"+wp_clat_str+".sst_clat_"+sst_clat_str
    data_filename = data_filename+".nc"

    cami_file = "E3SM_SP1_AQUA_ne30_64x1_4km_wp364_s2_00.cam.i.2000-01-02-36000.nc"

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

    # if case_num in [''] : 
    #     nlev_gcm = 64
    #     nlev_crm = 50

    crm_adv = "MPDATA"
    # if case_num in [''] : crm_adv = "UM5"        

    crm_dt = 5
    crm_dx = 1000

    if case_num == '04c' : crm_dt = 5
    if case_num == '04d' : crm_dt = 10
    if case_num == '04e' : crm_dt = 20
    if case_num == '04f' : crm_dt = 5
    if case_num == '04g' : crm_dt = 10
    if case_num == '04h' : crm_dt = 20
    if case_num == '04w' : crm_dt = 10

    if mod_str == "_4km"  : crm_dx = 4000
    if mod_str == "_2km"  : crm_dx = 2000
    if mod_str == "_0.5km": crm_dx = 500

    #------------------------------------------------
    # set CAM_CONFIG_OPTS
    #------------------------------------------------

    if cld=="ZM" :
        cam_opt = " -rad rrtmg -nlev "+str(nlev_gcm)+"  -clubb_sgs -microphys mg2 "

        chem_opt = " -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates "

        # cpp_opt = ""
        cpp_opt = " -cppdefs ' "

        cam_crm_rad_opt = ""
    
    if "SP" in cld :

        ### set options common to all SP setups
        cam_opt = " -phys cam5 -use_SPCAM  -rad rrtmg  -nlev "+str(nlev_gcm)+"  -crm_nz "+str(nlev_crm)+" -crm_adv "+crm_adv+" "\
                 +" -crm_nx "+str(crm_nx)+" -crm_ny "+str(crm_ny)+" -crm_dx "+str(crm_dx)+" -crm_dt "+str(crm_dt)

        ### 1-moment microphysics
        if cld=="SP1" : cam_opt = cam_opt + " -SPCAM_microp_scheme sam1mom   " 
            
        ### 2-moment microphysics
        if cld=="SP2" : cam_opt = cam_opt + " -SPCAM_microp_scheme m2005  " 

        #-------------------------------
        #-------------------------------

        ### Use mg2 since mg1 isn't supported anymore
        cam_opt = cam_opt + " -microphys mg2 "

        ### reduce rad columns by factor of 8
        # cam_crm_rad_opt = " -crm_nx_rad 8 -crm_ny_rad 1 "
        cam_crm_rad_opt = " "

        cam_opt = cam_opt+cam_crm_rad_opt

        ### chemistry and aerosols settings
        # chem_opt = " -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates "
        if cld=="SP1" :
            chem_opt = " -chem none"
        
        if cld=="SP2" :
            chem_opt = " -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates "
        
        if cld=="SP2+ECPP" :
            chem_opt = " -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates -use_ECPP  "

        ### set default CPP variables
        # cpp_opt = " -cppdefs ' -DSP_TK_LIM -DSP_ORIENT_RAND  -DSP_ESMT -DSP_USE_ESMT  "
        cpp_opt = " -cppdefs ' -DSP_TK_LIM -DSP_ORIENT_RAND "

        # cpp_opt = cpp_opt+" -DSPMOMTRANS "

        #-------------------------------
        # Special cases
        #-------------------------------

        # if case_num=='' : cpp_opt = cpp_opt+" -DSP_USE_DIFF "   # enable normal GCM thermodynamic diffusion
        # if case_num=='' : cpp_opt = cpp_opt+" -DSP_FLUX_BYPASS "
        # if case_num=='' : cpp_opt = cpp_opt+" -DSP_CRM_SFC_FLUX "
        
        # if case_num == '' : cpp_opt = cpp_opt+" -DSP_ESMT_PGF "
        # if case_num == '' : cpp_opt = cpp_opt+" -DSP_ESMT  -DSPMOMTRANS  -DSP_USE_ESMT  "

        #-------------------------------
        #-------------------------------

        ### use all columns for radiation with CAMRT
        # if " camrt " in cam_opt : cam_opt = cam_opt.replace(cam_crm_rad_opt,"")

    cam_opt = cam_opt+chem_opt+cpp_opt+" ' "


    if cld=="ZM" or ( "SP" in cld and not use_SP_compset ) : 
        print("------------------------------------------------------------")
        CMD = cdcmd+"./xmlchange --file env_build.xml --id CAM_CONFIG_OPTS --val \""+cam_opt+"\""
        print(CMD)
        os.system(CMD)
        print("------------------------------------------------------------")

    #--------------------------------------------------------
    # Aqua-planet specific config setting
    #--------------------------------------------------------
    if exp == "AQUA":
        start_date = "0000-01-01"
        os.system(cdcmd+"./xmlchange -file env_run.xml -id SSTICE_DATA_FILENAME -val "+init_dir+data_filename)

    #------------------------------------------------
    # update cami file if not equal to "default"
    #------------------------------------------------
    if cami_file != "default" :
        ### copy file to scratch
        CMD = "cp ~/E3SM/init_files/"+cami_file+" "+init_dir
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
    
    os.system(cdcmd+"./xmlchange --file env_run.xml   --id RUN_STARTDATE  --val "+start_date)

    if host=="titan" :
        if acct == "cli115" : os.system(cdcmd+"./xmlchange --file env_run.xml --id RUNDIR  --val /lustre/atlas1/cli115/scratch/hannah6/"+case_name+"/run ")
        if acct == "csc249" : os.system(cdcmd+"./xmlchange --file env_run.xml --id RUNDIR  --val /lustre/atlas/scratch/hannah6/csc249/" +case_name+"/run ")
        
        
    if " camrt " in cam_opt :
        os.system(cdcmd+"./xmlchange --file env_run.xml --id CAM_NML_USE_CASE  --val 2000_cam5_av1c-SP1_no-linoz")

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
        # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val 5400 ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val 6076 ")
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
    if clean : os.system(cdcmd+"./case.setup --clean")
    os.system(cdcmd+"./case.setup")
    

#===============================================================================================================================================================
#===============================================================================================================================================================
# Build the model
#===============================================================================================================================================================
#===============================================================================================================================================================
if build == True:
    #os.system(cdcmd+"cp "+srcmod_dir+"* ./SourceMods/src.cam/")    # copy any modified source code

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
#     if case_num in ['80a','80b'] : 
#         ref_case = "E3SM_SP1_CTL_ne30_64x1_1km_80"
#         if case_num == '80a' : ref_date = "2000-01-11"
#         if case_num == '80b' : ref_date = "2000-01-21"
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

#         ### create rpointer files
#         file = open(run_dir+"/rpointer.atm",'w') 
#         file.write("E3SM_SP1_CTL_ne30_64x1_1km_80.cam.r."+ref_date+"-00000.nc \n")
#         file.close()

#         file = open(run_dir+"/rpointer.drv",'w') 
#         file.write("E3SM_SP1_CTL_ne30_64x1_1km_80.cpl.r."+ref_date+"-00000.nc \n")
#         file.close()

#         file = open(run_dir+"/rpointer.ice",'w') 
#         file.write("E3SM_SP1_CTL_ne30_64x1_1km_80.cice.r."+ref_date+"-00000.nc \n")
#         file.close()

#         file = open(run_dir+"/rpointer.lnd",'w') 
#         file.write("E3SM_SP1_CTL_ne30_64x1_1km_80.clm2.r."+ref_date+"-00000.nc \n")
#         file.close()

#         file = open(run_dir+"/rpointer.ocn",'w') 
#         file.write("E3SM_SP1_CTL_ne30_64x1_1km_80.docn.r."+ref_date+"-00000.nc \n \n")
#         file.write("E3SM_SP1_CTL_ne30_64x1_1km_80.docn.rs1."+ref_date+"-00000.bin \n")
#         file.close()


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
        # file.write(" nhtfrq    = 0,1 \n") 
        # file.write(" mfilt     = 1,"+str(ncpl)+" \n")   # make sure each file has 1-day worth of data
        file.write(" nhtfrq    = 0,-1 \n") 
        file.write(" mfilt     = 1,24 \n")  

        # file.write(" nhtfrq    = 0,1,1 \n") 
        # file.write(" mfilt     = 1,5,5 \n")   

        file.write(" fincl2    = 'PS','TS'")
        file.write(             ",'T','Q','Z3','OMEGA','U','V' ")
        file.write(             ",'QRL','QRS'")             # Full radiative heating profiles
        file.write(             ",'FSNT','FLNT'")           # Net TOM heating rates
        file.write(             ",'FLNS','FSNS'")           # Surface rad for total column heating
        file.write(             ",'FSNTC','FLNTC'")         # clear sky heating rates for CRE
        file.write(             ",'LHFLX','SHFLX'")         # surface fluxes
        file.write(             ",'TAUX','TAUY'")
        file.write(             ",'PRECT','TMQ'")
        # file.write(             ",'LWCF','SWCF'")           # cloud radiative foricng
        # file.write(             ",'UBOT','VBOT','QBOT','TBOT'")
        # file.write(             ",'UAP','VAP','QAP','QBP','TAP','TBP','TFIX'")
        file.write(             ",'CLOUD','CLDLIQ','CLDICE' ")
        # file.write(             ",'QEXCESS' ")
        # file.write(             ",'PTTEND' ")
        # if "chem none" not in cam_config_opts :
        #     file.write(         ",'AEROD_v','EXTINCT'")         # surface fluxes
        if "SP" in cld :
            file.write(             ",'SPDT','SPDQ' ")
            # file.write(             ",'CRM_T','CRM_QV','CRM_QC','CRM_QPC','CRM_PREC' ")
            # file.write(             ",'SPQTFLX','SPQTFLXS'")
            file.write(             ",'SPTLS','SPQTLS' ")
            # file.write(             ",'SPQPEVP','SPMC' ")
            # file.write(             ",'SPMCUP','SPMCDN','SPMCUUP','SPMCUDN' ")
            # file.write(             ",'SPQC','SPQR' ")
            # file.write(             ",'SPQI','SPQS','SPQG' ")
            # file.write(             ",'SPTK','SPTKE','SPTKES' ")
        if "SP_CRM_SPLIT" in cam_config_opts :
            file.write(         ",'SPDT1','SPDQ1','SPDT2','SPDQ2' ")
            file.write(         ",'SPTLS1','SPTLS2' ")
        file.write("\n")


    #------------------------------
    # Default output
    #------------------------------
    else :
        file.write(" nhtfrq    = 0,-6,-1 \n") 
        file.write(" mfilt     = 1, 4, 120 \n")     # h2 = 1 hourly for 5 days
        # file.write(" nhtfrq    = 0,-6,-3 \n") 
        # file.write(" mfilt     = 1, 4, 80 \n")      # h2 = 3 hourly for 5 days 
        file.write(" fincl2    = 'T','Q','Z3','PS','TS','FLUT'")
        file.write(             ",'CLOUD','CLDLIQ','CLDICE'")
        file.write(             ",'U','V','OMEGA'")         # velocity components
        file.write(             ",'QRL','QRS'")             # Full radiative heating profiles
        file.write(             ",'FSNT','FLNT'")           # Net TOM heating rates
        file.write(             ",'FLNS','FSNS'")           # Surface rad for total column heating
        file.write(             ",'FSNTC','FLNTC'")         # clear sky heating rates for CRE
        file.write(             ",'LHFLX','SHFLX'")         # surface fluxes
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
        if exp == "SOM" :
            file.write(        ",'TS','LHFLX','SHFLX'")
        
        file.write("\n")


    if cami_file != "default" : file.write(" ncdata  = '"+init_dir+cami_file+"' \n")         
    
    
    file.write(" srf_flux_avg = 0 \n")
    # if any(c == case_num for c in ['']) :
    #     file.write(" srf_flux_avg = 1 \n")
    # else:
    #     file.write(" srf_flux_avg = 0 \n")


    file.write(" dyn_npes = "+str(num_dyn)+" \n")


    if "chem none" in cam_config_opts :
        prescribed_aero_path = "/atm/cam/chem/trop_mam/aero"
        prescribed_aero_file = "mam4_0.9x1.2_L72_2000clim_c170323.nc"
        file.write(" use_hetfrz_classnuc = .false. \n")
        file.write(" aerodep_flx_type = 'CYCLICAL' \n")
        file.write(" aerodep_flx_datapath = '"+din_loc_root+prescribed_aero_path+"' \n")
        file.write(" aerodep_flx_file = '"+prescribed_aero_file+"' \n")
        file.write(" aerodep_flx_cycle_yr = 01 \n")
        file.write(" prescribed_aero_type = 'CYCLICAL' \n")
        file.write(" prescribed_aero_datapath='"+din_loc_root+prescribed_aero_path+"' \n")
        file.write(" prescribed_aero_file = '"+prescribed_aero_file+"' \n")
        file.write(" prescribed_aero_cycle_yr = 01 \n")

    #------------------------------
    # Dycore tuning parameters
    #------------------------------

    ### default values
    qsplit            = 1 
    rsplit            = 3 
    se_nsplit         = 2
    hypervis_subcycle   = 3
    hypervis_subcycle_q = 1

    if inc_remap :
        se_nsplit = 4
    
    ### special cases

    # if exp == "AQUA" : 
    #     qsplit            = 20
    #     rsplit            = 20
    #     se_nsplit         = 20
    #     hypervis_subcycle = 20

    file.write(" qsplit    = "+str(   qsplit)+" \n") 
    file.write(" rsplit    = "+str(   rsplit)+" \n") 
    file.write(" se_nsplit = "+str(se_nsplit)+" \n")
    file.write(" hypervis_subcycle = "+str(hypervis_subcycle)+" \n") 

    #------------------------------
    # Aqua-planet namelist settings
    #------------------------------
    if exp == "AQUA" :
        file.write(" bnd_topo   = '"+init_dir+"aqua_topo.v1.nc' \n")
        # file.write(" clim_modal_aero_top_press = 0 \n")
        # file.write(" srf_emis_specifier = '' \n")
        # file.write(" ext_frc_specifier  = '' \n")

    if "AQUA" in exp :
        file.write(" orb_mode           = 'fixed_parameters' \n")
        file.write(" orb_eccen          = 0 \n")
        file.write(" orb_obliq          = 0 \n")
        file.write(" orb_mvelp          = 0 \n")
        # file.write(" datvarnames  = 'ice_cov' \n")

    #------------------------------
    # state_debug_checks
    #------------------------------
    if debug_chks :
        file.write(" state_debug_checks = .true. \n")
    else :
        file.write(" state_debug_checks = .false. \n")

    #------------------------------
    # close the atm namelist file
    #------------------------------
    file.close() 

    #------------------------------
    # Land model namelist
    #------------------------------
    if test_run :
        nfile = case_dir+"user_nl_clm"
        file = open(nfile,'w') 
        file.write(" hist_nhtfrq = 0,-1 \n")
        file.write(" hist_mfilt  = 1,24 \n")
        file.write(" hist_mfilt  = 1,"+str(ncpl)+" \n")
        file.write(" hist_fincl2 = 'TBOT','QTOPSOIL','RH','RAIN'")
        file.write(              ",'FGEV','FCEV','FCTR','Rnet'")
        file.write(              ",'FSH_V','FSH_G','TLAI','ZWT','ZWT_PERCH'")
        file.write(              ",'QSOIL','QVEGT','QCHARGE'")
        file.write("\n")
        file.close()
    #------------------------------
    # Turn off CICE history files
    #------------------------------
    nfile = case_dir+"user_nl_cice"
    file = open(nfile,'w') 
    file.write(" histfreq = 'x','x','x','x','x' \n")
    file.close()
    

    #------------------------------
    # Land sensitivity tests
    #------------------------------
    if case_num == "90":
        lnd_data_filename = "surfdata_ne30np4_simyr2000_c180306_no-vegetation.nc"
        CMD = "cp -u "+home+"/E3SM/init_files/"+lnd_data_filename+" "+init_dir
        print(CMD)
        os.system(CMD)

        nfile = case_dir+"user_nl_clm"
        file = open(nfile,'w') 
        file.write(" fsurdat = \'"+init_dir+lnd_data_filename+"\' \n")
        file.close()


    #------------------------------
    # Set ocn domain file for SOM
    #------------------------------
    if exp == "SOM" :
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id DOCN_SOM_FILENAME  -val pop_frc.1x1d.090130.nc ")

        nfile = case_dir+"user_nl_docn"
        file = open(nfile,'w') 
        file.write(' domainfile = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/share/domains/domain.ocn.ne30np4_gx1v6_110217.nc"  \n')
        file.close()

    #------------------------------
    # Set input and domain files for AQUA
    #------------------------------
    if exp == "AQUA" : 

        # update topo file in case it got scrubbed
        CMD = "cp -u "+home+"/E3SM/init_files/aqua_topo.v1.nc "+init_dir
        print(CMD)
        os.system(CMD)

        # update domain files in case they got scrubbed
        aqua_domain_ocn_file = "aqua_domain.ocn.ne30np4_gx1v6.v1.nc"
        aqua_domain_lnd_file = "aqua_domain.lnd.ne30np4_gx1v6.v1.nc"

        CMD = "cp -u "+home+"/E3SM/init_files/"+aqua_domain_ocn_file+" "+init_dir
        print(CMD)
        os.system(CMD)

        CMD = "cp -u "+home+"/E3SM/init_files/"+aqua_domain_lnd_file+" "+init_dir
        print(CMD)
        os.system(CMD)

        # update xml entries for domain file names and paths
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id ATM_DOMAIN_PATH  -val "+init_dir)
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id OCN_DOMAIN_PATH  -val "+init_dir)
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id ICE_DOMAIN_PATH  -val "+init_dir)
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id LND_DOMAIN_PATH  -val "+init_dir)

        os.system(cdcmd+"./xmlchange -file env_run.xml   -id ATM_DOMAIN_FILE  -val "+aqua_domain_lnd_file)
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id OCN_DOMAIN_FILE  -val "+aqua_domain_ocn_file)
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id ICE_DOMAIN_FILE  -val "+aqua_domain_ocn_file)
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id LND_DOMAIN_FILE  -val "+aqua_domain_lnd_file)
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id LND_DOMAIN_FILE  -val UNSET ")
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id ROF_DOMAIN_FILE  -val UNSET ")
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id WAV_DOMAIN_FILE  -val UNSET ")
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id GLC_DOMAIN_FILE  -val UNSET ")
        

        # update sst data file in case it got scrubbed
        CMD = "cp -u "+home+"/E3SM/init_files/"+data_filename+" "+init_dir
        print(CMD)
        os.system(CMD)

        # update xml entry for the SST file
        os.system(cdcmd+"./xmlchange -file env_run.xml -id SSTICE_DATA_FILENAME -val "+init_dir+data_filename)

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

    # ncdata        = '/lustre/atlas1/"+acct+"/scratch/hannah6/E3SM_SP2_CTL_ne30_01/run/cami-mam3_0000-01-01_ne30np4_L30_c130424.modified.nc'
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
    # but check if a run is already in the dbug queu
    #------------------------------    

    os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val batch")
    # os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val debug")

    # if debug : os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val debug")
    # if test_run : os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val debug")

    # if debug and debug_queue :
    if debug_queue :
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
                    if job['job_state'] != 'C' :
                        debug_clear = False
        if debug_clear : 
            os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val debug")
            wall_time = debug_wall_time

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

#===============================================================================================================================================================
#===============================================================================================================================================================
#===============================================================================================================================================================
#===============================================================================================================================================================