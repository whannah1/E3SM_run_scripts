#!/usr/bin/env python
#==========================================================================================================================================
# Jan, 2017 - Walter Hannah - Lawrence Livermore National Lab
# This script runs atmosphere-only, single-column simulations of E3SM
# ulimit -c unlimited
#==========================================================================================================================================
import sys
import os
import fileinput
import subprocess
import run_E3SM_common as E3SM_common

home = E3SM_common.get_home_dir()
host = E3SM_common.get_host_name()

opsys = os.getenv("os")

#==========================================================================================================================================
#==========================================================================================================================================
newcase,config,build,runsim,debug,clean,mk_nml = False,False,False,False,False,False,False

newcase  = True
# clean    = True
config   = True
build    = True
mk_nml   = True
runsim   = True

debug    = True       # enable debug flags

# E3SM_SP1_CTL_ne4_48x1_4km_00

#--------------------------------------------------------
#--------------------------------------------------------
case_num = "00"     # control - all current defualts  

#--------------------------------------------------------
#--------------------------------------------------------

cld = "SP1"    # ZM / SP1 / SP2 / SP2+ECPP
exp = "CTL"    # CTL / ???
res = "ne4"    # ne4

ndays = 1
resub = 0

crm_nx,crm_ny,mod_str = 48,1,"_4km"

#==========================================================================================================================================
#==========================================================================================================================================

#--------------------------------------------------------
# Setup the case name
#--------------------------------------------------------

if "ZM" in cld : mod_str,crmdim = "",""
if "SP" in cld : crmdim = "_"+str(crm_nx)+"x"+str(crm_ny) 
    
case_name = "E3SM_"+cld+"_"+exp+"_"+res+crmdim+mod_str+"_"+case_num

# case_name = "E3SM_"+exp+"_"+res+"_"+case_num

#--------------------------------------------------------
# Setup directory names
#--------------------------------------------------------
top_dir     = home+"/E3SM/"
srcmod_dir  = top_dir+"mod_src/"
nmlmod_dir  = top_dir+"mod_nml/"

src_dir = home+"/E3SM/E3SM_SRC_master"
if "s1"  in case_num : src_dir = home+"/E3SM/E3SM_SRC1"
if "s2"  in case_num : src_dir = home+"/E3SM/E3SM_SRC2"

scratch_dir = home+"/Model/E3SM/scratch/"

run_dir = scratch_dir+"/"+case_name+"/run"

#--------------------------------------------------------
# Set the CM physics time step
#--------------------------------------------------------
dtime = 20*60

ncpl  = 86400 / dtime

#===================================================================================
#===================================================================================
os.system("cd "+top_dir)
case_dir  = top_dir+"Cases/"+case_name 
cdcmd = "cd "+case_dir+" ; "
print("")
print("  case : "+case_name)
print("")
#==========================================================================================================================================
#==========================================================================================================================================
# Create new case
#==========================================================================================================================================
#==========================================================================================================================================

case_obj = E3SM_common.Case( case_name=case_name, res=res, cld=cld, case_dir=case_dir )

case_obj.verbose = True

compset_opt = " -compset FC5AV1C-L "

use_SP_compset = False
# if cld=="SP1" : compset_opt = " -compset FSP1V1 " ; use_SP_compset = True

if newcase == True:

    newcase_cmd = src_dir+"/cime/scripts/create_newcase"
    cmd = newcase_cmd+" -case "+case_dir+" "+compset_opt+" -res "+res+"_"+res+" -mach "+host
    cmd = cmd+" --mpilib mpich "
    
    print("")
    print(cmd)
    print("")
    os.system(cmd)

case_dir = case_dir+"/"

#==========================================================================================================================================
#==========================================================================================================================================
# Configure the case
#==========================================================================================================================================
#==========================================================================================================================================
if config == True:
    #------------------------------------------------
    # set vertical levels
    #------------------------------------------------
    nlev_gcm = 72
    nlev_crm = 58
    
    # crm_adv = "MPDATA"
    # if case_num in [''] : crm_adv = "UM5"        

    # crm_dt = 5

    if mod_str == "_4km"  : crm_dx = 4000
    if mod_str == "_2km"  : crm_dx = 2000
    if mod_str == "_1km"  : crm_dx = 1000
    if mod_str == "_0.5km": crm_dx = 500

    #------------------------------------------------
    # set CAM_CONFIG_OPTS
    #------------------------------------------------
    # cam_opt = " -phys cam5 -rad rrtmg -nlev 72  -clubb_sgs -microphys mg2 "

    # chem_opt = " -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates "
    # # chem_opt = " -chem none"

    # # cpp_opt = " -cppdefs ' "
    # # cpp_opt = cpp_opt+" ' "
        
    # cam_opt = cam_opt+chem_opt #+cpp_opt 

    # CMD = cdcmd+"./xmlchange --file env_build.xml --id CAM_CONFIG_OPTS --val \""+cam_opt+"\""
    # print(CMD)
    # os.system(CMD)


    cam_opt = E3SM_common.get_default_config( cld, nlev_gcm, nlev_crm, crm_nx, crm_ny, crm_dx )

    if cld=="ZM" : 
        cam_opt = " -rad rrtmg -nlev "+str(nlev_gcm)+"  -clubb_sgs -microphys mg2 -chem none "
        # cam_opt = " -rad rrtmg -nlev "+str(nlev_gcm)+" -microphys mg1 -chem none "
        
        cpp_opt = " -cppdefs ' -DRCEMIP "

    
    if "SP" in cld :
        # cpp_opt = " -cppdefs ' -DAPPLY_POST_DECK_BUGFIXES -DSP_TK_LIM  -DSP_ESMT -DSP_USE_ESMT -DSP_ORIENT_RAND "
        cpp_opt = " -cppdefs ' -DSP_TK_LIM -DSP_ORIENT_RAND "

        #-------------------------------
        # Special cases
        #-------------------------------

        if case_num=='03' : cpp_opt = cpp_opt+" -DSP_USE_DIFF "   # enable normal GCM thermodynamic diffusion
        
        # if case_num == '' : cpp_opt = cpp_opt+" -DSP_ESMT_PGF "
        # if case_num == '' : cpp_opt = cpp_opt+" -DSP_ESMT  -DSPMOMTRANS  -DSP_USE_ESMT  "
        # if case_num == '' : cpp_opt = cpp_opt+" -DSP_ESMT -DSP_USE_ESMT -DSP_ESMT_PGF "

        if case_num in ['s2_50']  : cpp_opt = cpp_opt+" -DSP_ALT_TPHYSBC "
        if case_num in ['s2_51']  : cpp_opt = cpp_opt+" -DSP_ALT_TPHYSBC -DDIFFUSE_PHYS_TEND "
        if case_num in ['s2_51a'] : cpp_opt = cpp_opt+" -DSP_ALT_TPHYSBC -DDIFFUSE_PHYS_TEND -DSP_DUMMY_HYPERVIS -DSP_DUMMY_HYPERVIS_T "
        if case_num in ['s2_51b'] : cpp_opt = cpp_opt+" -DSP_ALT_TPHYSBC -DDIFFUSE_PHYS_TEND -DSP_DUMMY_HYPERVIS -DSP_DUMMY_HYPERVIS_Q "
        if case_num in ['s2_52']  : cpp_opt = cpp_opt+" -DSP_ALT_TPHYSBC -DDIFFUSE_PHYS_TEND -DPHYS_HYPERVIS_FACTOR_5X5 "
        

        #-------------------------------
        #-------------------------------

    cam_opt = cam_opt+cpp_opt+" ' "


    if cld=="ZM" or ( "SP" in cld and not use_SP_compset ) : 
        print("------------------------------------------------------------")
        CMD = cdcmd+"./xmlchange --file env_build.xml --id CAM_CONFIG_OPTS --val \""+cam_opt+"\""
        print(CMD)
        os.system(CMD)
        print("------------------------------------------------------------")


    #------------------------------------------------
    # Use CLM 4.5
    #------------------------------------------------
    # clm_opt = " -phys clm4_5 "

    # CMD = cdcmd+"./xmlchange --file env_build.xml --id CLM_CONFIG_OPTS --val \""+clm_opt+"\" "
    # print(CMD)
    # os.system(CMD)

    #------------------------------------------------
    # set run-time variables
    #------------------------------------------------
    # os.system(cdcmd+"./xmlchange --file env_run.xml   --id RUN_STARTDATE  --val "+start_date)
    # os.system(cdcmd+"./xmlchange --file env_run.xml   --id START_TOD      --val "+str(start_in_sec))

    #------------------------------------------------
    # Change processor count
    #------------------------------------------------
    ntask = 4

    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val "+str(ntask)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_LND -val "+str(ntask)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ICE -val "+str(ntask)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_OCN -val "+str(ntask)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_CPL -val "+str(ntask)+" ")
    # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_GLC -val "+str(ntask)+" ")
    # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_WAV -val "+str(ntask)+" ")
    # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ROF -val "+str(ntask)+" ")

    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_GLC -val 1 ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_WAV -val 1 ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ROF -val 1 ")

    case_obj.set_NTHRDS_all(1)      # Make sure threading is off

    #------------------------------------------------
    # Set the timestep
    #------------------------------------------------
    os.system(cdcmd+"./xmlchange -file env_run.xml -id ATM_NCPL -val "+str(ncpl) )

    #------------------------------------------------
    # for GNU set COMPILER before configure so that Macros file has correct flags
    #------------------------------------------------
    CMD = cdcmd+"./xmlchange --file env_build.xml --id COMPILER --val \"gnu\" "
    print(CMD)
    os.system(CMD)

    #------------------------------------------------
    # configure the case
    #------------------------------------------------    
    if clean : os.system(cdcmd+"./case.setup --clean")
    os.system(cdcmd+"./case.setup")

#==========================================================================================================================================
#==========================================================================================================================================
# Build the model
#==========================================================================================================================================
#==========================================================================================================================================
if build == True:

    #----------------------------------------------------------
    #----------------------------------------------------------
    ### Don't want to write restarts as this appears to be broken for  CICE model in SCM.  For now set this to a high value to avoid
    # os.system(cdcmd+"./xmlchange PIO_TYPENAME=\"netcdf\" ")
    # os.system(cdcmd+"./xmlchange REST_N=30000 ")

    #----------------------------------------------------------
    #----------------------------------------------------------
    ### Modify some parameters for CICE to make it SCM compatible 
    # os.system(cdcmd+"./xmlchange CICE_AUTO_DECOMP=\"FALSE\" ")
    # os.system(cdcmd+"./xmlchange CICE_DECOMPTYPE=\"blkrobin\" ")
    # os.system(cdcmd+"./xmlchange --id CICE_BLCKX --val 1 ")
    # os.system(cdcmd+"./xmlchange --id CICE_BLCKY --val 1 ")
    # os.system(cdcmd+"./xmlchange --id CICE_MXBLCKS --val 1 ")
    # os.system(cdcmd+"./xmlchange CICE_CONFIG_OPTS=\"-nodecomp -maxblocks 1 -nx 1 -ny 1\" ")

    #----------------------------------------------------------
    #----------------------------------------------------------
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


#==========================================================================================================================================
#==========================================================================================================================================
# Write the custom namelist options
#==========================================================================================================================================
#==========================================================================================================================================

# Get local input data directory path
(cam_config_opts, err) = subprocess.Popen(cdcmd+"./xmlquery CAM_CONFIG_OPTS -value", stdout=subprocess.PIPE, shell=True).communicate()
(compset        , err) = subprocess.Popen(cdcmd+"./xmlquery COMPSET         -value", stdout=subprocess.PIPE, shell=True).communicate()
(din_loc_root   , err) = subprocess.Popen(cdcmd+"./xmlquery DIN_LOC_ROOT    -value", stdout=subprocess.PIPE, shell=True).communicate()
(input_data_dir , err) = subprocess.Popen(cdcmd+"./xmlquery DIN_LOC_ROOT -value", stdout=subprocess.PIPE, shell=True).communicate()

if mk_nml :
    nfile = case_dir+"user_nl_cam"
    file = open(nfile,'w') 

    file.write(" nhtfrq    = 0,-1 \n") 
    file.write(" mfilt     = 1,24  \n") 

    file.write(" fincl2    = ")
    file.write(             "'T','Q','PS','TS','OMEGA','U','V' ")
    file.write(             ",'QRL','QRS'")             # Full radiative heating profiles
    file.write(             ",'FSNT','FLNT'")           # Net TOM heating rates
    file.write(             ",'FLNS','FSNS'")           # Surface rad for total column heating
    file.write(             ",'FSNTC','FLNTC'")         # clear sky heating rates for CRE
    file.write(             ",'LHFLX','SHFLX'")         # surface fluxes
    file.write(             ",'TAUX','TAUY'")
    file.write(             ",'PRECT','TMQ'")
    file.write(             ",'LWCF','SWCF'")           # cloud radiative foricng
    file.write(             ",'UBOT','VBOT','QBOT','TBOT'")
    file.write(             ",'UAP','VAP','QAP','QBP','TAP','TBP','TFIX'")
    file.write(             ",'CLOUD','CLDLIQ','CLDICE' ")
    file.write(             ",'PTTEND','DTCOND','DCQ' ")
    # file.write(             ",'AEROD_v','EXTINCT'")         # surface fluxes
    file.write("\n")

    file.write(" srf_flux_avg = 1 \n")
    
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

    file.close() 

    #------------------------------
    # Turn off CICE history files
    #------------------------------
    nfile = case_dir+"user_nl_cice"
    file = open(nfile,'w') 
    file.write(" histfreq = 'x','x','x','x','x' \n")
    file.close()

#==========================================================================================================================================
#==========================================================================================================================================
# Run the simulation
#==========================================================================================================================================
#==========================================================================================================================================
if runsim == True:

    runfile = case_dir+".case.run"
    subfile = case_dir+"case.submit"

    #------------------------------
    #------------------------------
    # not sure why this isn't being set correctly
    # if opsys == "Darwin" :
        # os.system(cdcmd+"./xmlchange -file env_run.xml   -id ICE_DOMAIN_PATH  -val \"\\$DIN_LOC_ROOT/atm/cam/ocnfrac\" ")
        # if res == "ne30" : os.system(cdcmd+"./xmlchange -file env_run.xml   -id ICE_DOMAIN_FILE  -val domain.camocn.64x128_USGS_070807.nc ")
        # if res == "ne4"  : os.system(cdcmd+"./xmlchange -file env_run.xml   -id ICE_DOMAIN_FILE  -val domain.ocn.ne4np4_oQU240.160614.nc ")
        # if res == "ne4"  : os.system(cdcmd+"./xmlchange -file env_run.xml   -id ICE_DOMAIN_FILE  -val UNSET ")

    #------------------------------
    # Change run options
    #------------------------------
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_OPTION  -val ndays ")
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_N       -val "+str(ndays)) 
    # os.system(cdcmd+"./xmlchange -file env_run.xml   -id RESUBMIT     -val "+str(resub))
    # os.system(cdcmd+"./xmlchange -file env_run.xml   -id CONTINUE_RUN -val "+cflag)
 


    if opsys=="Darwin" and res=="ne4":
        # os.system(cdcmd+"./xmlchange --file env_run.xml   --id PIO_REARR_COMM_MAX_PEND_REQ_COMP2IO  --val 64 ")
        os.system(cdcmd+"./xmlchange --file env_run.xml   --id PIO_REARR_COMM_MAX_PEND_REQ_COMP2IO  --val 4 ")

    # if opsys=="Darwin" and res=="T42":
        # os.system(cdcmd+"./xmlchange --file env_run.xml   --id PIO_REARR_COMM_MAX_PEND_REQ_COMP2IO  --val 0 ")
        # os.system(cdcmd+"./xmlchange --file env_run.xml   --id PIO_REARR_COMM_MAX_PEND_REQ_COMP2IO  --val 1 ")

    #------------------------------
    # switch to debug queue
    #------------------------------    
    if host=="edison" :
        os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val regular")
    #------------------------------
    # DEBUG LEVEL
    #------------------------------
    if debug :
        ### level of debug output, 0=minimum, 1=normal, 2=more, 3=too much
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id INFO_DBUG -val 2")

        ### for debug mode, make sure that we will get a core dump file 
        ### in the event that we get a segmentation fault
        f = open(runfile, "r")
        contents = f.readlines()
        f.close()

        index = -1
        for num, line in enumerate(contents, 1):
            if "def _main_func(description):" in line: index = num+1
            if "resource.setrlimit" in line: index = -1

        if index > 0 :
            contents.insert(index  , "    import resource \n")
            contents.insert(index+1, "    resource.setrlimit(resource.RLIMIT_CORE, (resource.RLIM_INFINITY, resource.RLIM_INFINITY)) \n")
            contents.insert(index+2, "    \n")

            f = open(runfile, "w")
            contents = "".join(contents)
            f.write(contents)
            f.close()

        ### Make sure that there is not old core file, because it won't get overwritten
        core_file = run_dir+"/core"

        if os.path.isfile(core_file) :
            for n in range(1, 99):
                core_file_next = run_dir+"/core_old_" + str(n).zfill(2)
                if not os.path.isfile(core_file_next) :
                    os.system("mv "+core_file+"  "+core_file_next)
                    break

    
    #------------------------------
    # Submit the run
    #------------------------------
    if opsys == "Darwin" :
        os.system(cdcmd+subfile+" --no-batch ")
    elif host == "edison" :
        # mail_flag = " --mail-user=hannah6@llnl.gov  "
        os.system(cdcmd+subfile+mail_flag)
    else :
        os.system(cdcmd+subfile)


print("")
print("  case : "+case_name)
print("")
    
#==========================================================================================================================================
#==========================================================================================================================================
