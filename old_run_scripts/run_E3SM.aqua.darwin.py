#!/usr/bin/env python
#===============================================================================================================================================================
#  Jan, 2019 - Walter Hannah - Lawrence Livermore National Lab
#  This script runs aqua-planet simulations of E3SM
#===============================================================================================================================================================
import sys
import os
import fileinput
import subprocess
import run_E3SM_common as E3SM_common

home = E3SM_common.get_home_dir()
host = E3SM_common.get_host_name()
acct = E3SM_common.get_host_acct(host)

newcase,config,build,runsim,clean,mk_nml = False,False,False,False,False,False
debug,quick_test,debug_chks = False,False,False
#===============================================================================================================================================================
#===============================================================================================================================================================

# newcase  = True
clean    = True
config   = True
build    = True
# mk_nml   = True
runsim   = True

quick_test = True     # only run for a few time steps (debug_nsteps)
# debug      = True     # enable debug flags
# debug_chks  = True       # enable state_debug_checks (namelist)

#--------------------------------------------------------
#--------------------------------------------------------
case_num = "00"     # control - all current defaults  

#--------------------------------------------------------
#--------------------------------------------------------
cld = "ZM"    # ZM / SP1 / SP2 / SP2+ECPP
exp = "FC5AV1C-L"    # AQP1 / AQP2 / FC5AV1C-L
res = "ne30"   # ne120 / ne30 / ne16 / ne4

cflag = "FALSE"                      # Don't forget to set this!!!! 

ndays,resub,wall_time = 1,0,"0:30:00"

crm_nx,crm_ny,mod_str = 8,1,"_1km"

#--------------------------------------------------------
# Special Cases
#--------------------------------------------------------
debug_wall_time =  "0:30:00"        # special limit for debug queue
debug_nsteps = 10                  # for debug mode use steps instead of days

if debug : resub = 0    # set resubmissions for debug mode

if "ZM" in cld : mod_str = ""     

#--------------------------------------------------------
# Set the case name
#--------------------------------------------------------
crmdim = ""
if "SP" in cld : crmdim = "_"+str(crm_nx)+"x"+str(crm_ny) 
    

case_name = "E3SM_"+exp+"_"+cld+"_"+res+crmdim+mod_str+"_"+case_num


#===============================================================================================================================================================
# Various settings for account / system / directories
#===============================================================================================================================================================
top_dir     = home+"/E3SM/"

src_dir = home+"/E3SM/E3SM_SRC_master"
if "s1"  in case_num : src_dir = home+"/E3SM/E3SM_SRC1"
if "s2"  in case_num : src_dir = home+"/E3SM/E3SM_SRC2"

scratch_dir = E3SM_common.get_scratch_dir(host,acct)

run_dir = scratch_dir+"/"+case_name+"/run"

num_dyn = E3SM_common.get_num_dyn(res)

# dtime = 20*60
# ncpl  = 86400 / dtime

os.system("cd "+top_dir)
case_dir  = top_dir+"Cases/"+case_name 
cdcmd = "cd "+case_dir+" ; "

print("\n  case : "+case_name+"\n")
#===============================================================================================================================================================
#===============================================================================================================================================================
# Create new case
#===============================================================================================================================================================
#===============================================================================================================================================================

case_obj = E3SM_common.Case( case_name=case_name, res=res, cld=cld, case_dir=case_dir )

grid_opt = res+"_"+res
if "pg" in res : grid_opt = res+"_"+res

# compset_opt = " -compset FC5AV1C-L-"+exp+" "
if "AQP" in exp : 
    compset_opt = " -compset F-EAMv1-"+exp+" "
else :
    compset_opt = " -compset "+exp+" "

use_SP_compset = False

if newcase == True:
    newcase_cmd = src_dir+"/cime/scripts/create_newcase"
    cmd = newcase_cmd+" -case "+case_dir+" "+compset_opt+" -res "+grid_opt+" -mach "+host
    cmd = cmd+" --mpilib mpich "
    print("\n"+cmd+"\n")
    os.system(cmd)

case_dir = case_dir+"/"

### set location and file name for initialization
cami_file = "default"
init_dir = "/global/cscratch1/sd/whannah/acme_scratch/init_files/"


if "AQP" in exp :
    if "ne30" in res : cami_file = "aqua_0006-01-01_ne30np4_L72_c190130.nc"
    # if "ne30" in res : cami_file = "cami_mam3_Linoz_ne30np4_L72_c160214_RCEMIP.nc"
    if "ne4" in res  : cami_file = "cami_mam3_Linoz_ne4np4_L72_c160909_RCEMIP.nc"

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
    
    # crm_adv = "MPDATA"
    # if case_num in [''] : crm_adv = "UM5"        

    # crm_dt = 5

    crm_dx = 0
    if mod_str == "_4km"  : crm_dx = 4000
    if mod_str == "_2km"  : crm_dx = 2000
    if mod_str == "_1km"  : crm_dx = 1000
    if mod_str == "_0.5km": crm_dx = 500

    crm_nx_rad = crm_nx/4

    #------------------------------------------------
    # set CAM_CONFIG_OPTS
    #------------------------------------------------

    # cam_opt = E3SM_common.get_default_config( cld, nlev_gcm, nlev_crm, crm_nx, crm_ny, crm_nx_rad, crm_dx )

    # if cld=="ZM" : 
    #     cpp_opt = " -cppdefs ' "
    
    if "SP" in cld :
        
        cam_opt = E3SM_common.get_default_config( cld, nlev_gcm, nlev_crm, crm_nx, crm_ny, crm_nx_rad, crm_dx )

        cpp_opt = " -cppdefs ' -DSP_ORIENT_RAND "

        #-------------------------------
        # Special cases
        #-------------------------------
        # if case_num=='03' : cpp_opt = cpp_opt+" -DSP_USE_DIFF "   # enable normal GCM thermodynamic diffusion

        #-------------------------------
        #-------------------------------

        if "pg1" in res : cpp_opt = cpp_opt+" -DPHYS_GRID_1x1_TEST "

        cam_opt = cam_opt+cpp_opt+" ' "

        case_obj.xmlchange("env_build.xml", "CAM_CONFIG_OPTS", "\""+cam_opt+"\"" )

    # if ( "SP" in cld and not use_SP_compset ) : 
    #     case_obj.xmlchange("env_build.xml", "CAM_CONFIG_OPTS", "\""+cam_opt+"\"" )

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
    # Change processor count
    #------------------------------------------------
    case_obj.set_NTASKS_all(1)
    case_obj.set_NTHRDS_all(1)      # Make sure threading is off
    case_obj.set_ROOTPE_all(0)      # Not sure if we need this or not

    case_obj.xmlchange("env_mach_pes.xml", "NTASKS_ATM", 4 )  
    case_obj.xmlchange("env_mach_pes.xml", "COST_PES",   4 )
    case_obj.xmlchange("env_mach_pes.xml", "TOTALPES",   4 )

    #------------------------------------------------
    # Set the timestep
    #------------------------------------------------
    # case_obj.xmlchange("env_run.xml", "ATM_NCPL", ncpl )

    #------------------------------------------------
    # configure the case
    #------------------------------------------------    
    case_obj.setup(clean)
    
#===============================================================================================================================================================
#===============================================================================================================================================================
# Build the model
#===============================================================================================================================================================
#===============================================================================================================================================================
if build == True:
    case_obj.set_debug_mode(debug)
    case_obj.build(clean)


#=================================================================================================================================
# Write the custom namelist options
#=================================================================================================================================
if mk_nml :

    cam_config_opts = case_obj.xmlquery("CAM_CONFIG_OPTS")
    compset         = case_obj.xmlquery("COMPSET")
    din_loc_root    = case_obj.xmlquery("DIN_LOC_ROOT")

    ### remove extra spaces to simplify string query
    cam_config_opts = ' '.join(cam_config_opts.split())

    nfile = case_dir+"user_nl_cam"
    file = open(nfile,'w') 

    #------------------------------
    #------------------------------
    if debug or quick_test :
        file.write(" nhtfrq    = 0,1,1 \n") 
        file.write(" mfilt     = 1,"+str(debug_nsteps)+","+str(debug_nsteps)+"  \n") 
    else :
        file.write(" nhtfrq    = 0,-1 \n") 
        file.write(" mfilt     = 1,24  \n") 


    file.write(" fincl2    = 'PS','PRECT','TMQ'")
    # file.write(             ",'T','Q','Z3' ")
    # file.write(             ",'OMEGA','U','V' ")
    # file.write(             ",'QRL','QRS'")             # Full radiative heating profiles
    file.write(             ",'FSNT','FLNT'")           # Net TOM heating rates
    file.write(             ",'FLNS','FSNS'")           # Surface rad for total column heating
    file.write(             ",'FSNTC','FLNTC'")         # clear sky heating rates for CRE
    file.write(             ",'LHFLX','SHFLX'")         # surface fluxes
    # file.write(             ",'TAUX','TAUY'")
    # file.write(             ",'LWCF','SWCF'")           # cloud radiative foricng
    file.write(             ",'UBOT','VBOT','QBOT','TBOT'")
    # file.write(             ",'UAP','VAP','QAP','QBP','TAP','TBP','TFIX'")
    file.write(             ",'CLOUD','CLDLIQ','CLDICE' ")
    file.write(             ",'PTTEND','DTCOND','DCQ' ")
    # file.write(             ",'AEROD_v','EXTINCT'")         # surface fluxes
    # file.write(             ",'dyn_PS','dyn_T' ")
    # file.write(             ",'dyn_U','dyn_V','dyn_OMEGA' ")
    file.write("\n")
    #------------------------------
    #------------------------------
    file.write(" dyn_npes = "+str(num_dyn)+" \n")

    if cami_file != "default" : file.write(" ncdata  = '"+init_dir+cami_file+"' \n")         

    if res == "ne120" : file.write(" cld_macmic_num_steps = 3 \n") 

    # if "pg1" in res : file.write(" bnd_topo   = '"+init_dir+topo_file+"' \n")

    #------------------------------
    # Sfc flux smoothing
    #------------------------------
    if "SP" in cld : file.write(" srf_flux_avg = 1 \n")
    
    #------------------------------
    # Prescribed aerosol settings
    #------------------------------
    # if "chem none" in cam_config_opts :
    #     prescribed_aero_path = "/atm/cam/chem/trop_mam/aero"
    #     prescribed_aero_file = "mam4_0.9x1.2_L72_2000clim_c170323.nc"
    #     file.write(" use_hetfrz_classnuc = .false. \n")
    #     file.write(" aerodep_flx_type = 'CYCLICAL' \n")
    #     file.write(" aerodep_flx_datapath = '"+din_loc_root+prescribed_aero_path+"' \n")
    #     file.write(" aerodep_flx_file = '"+prescribed_aero_file+"' \n")
    #     file.write(" aerodep_flx_cycle_yr = 01 \n")
    #     file.write(" prescribed_aero_type = 'CYCLICAL' \n")
    #     file.write(" prescribed_aero_datapath='"+din_loc_root+prescribed_aero_path+"' \n")
    #     file.write(" prescribed_aero_file = '"+prescribed_aero_file+"' \n")
    #     file.write(" prescribed_aero_cycle_yr = 01 \n")

    #------------------------------
    # Prescribed ozone
    #------------------------------
    # file.write(" prescribed_ozone_cycle_yr   = 2000 \n")
    # # file.write(" prescribed_ozone_datapath   = '/project/projectdirs/acme/inputdata/atm/cam/ozone' \n")
    # # file.write(" prescribed_ozone_file       = 'ozone_1.9x2.5_L26_2000clim_c091112.nc' \n")
    # # file.write(" prescribed_ozone_name       = 'O3' \n")
    # file.write(" prescribed_ozone_type       = 'CYCLICAL' \n")

    # file.write(" prescribed_ozone_datapath   = '"+init_dir+"' \n")
    # file.write(" prescribed_ozone_file       = 'RCEMIP_ozone.v1.nc' \n")
    # file.write(" prescribed_ozone_name       = 'O3' \n")
    # # file.write(" prescribed_ozone_type       = 'FIXED' \n")

    # ### update ozone file in case it got scrubbed
    # CMD = "cp -u "+home+"/E3SM/init_files/RCEMIP_ozone.v1.nc "+init_dir
    # print(CMD)
    # os.system(CMD)

    #------------------------------
    # state_debug_checks
    #------------------------------
    if debug_chks :
        file.write(" state_debug_checks = .true. \n")
    else :
        file.write(" state_debug_checks = .false. \n")
    
    #------------------------------
    # close atm_in
    #------------------------------ 
    file.close() 


#===============================================================================================================================================================
#===============================================================================================================================================================
# Run the simulation
#===============================================================================================================================================================
#===============================================================================================================================================================
if runsim == True:

    runfile = case_dir+".case.run"
    subfile = case_dir+"case.submit"

    #------------------------------
    # Turn off restart files
    #------------------------------
    case_obj.xmlchange("env_run.xml", "PIO_TYPENAME", " \"netcdf\" " )
    case_obj.xmlchange("env_run.xml", "REST_N", 30000 )

    #------------------------------
    # Set ICE domain - not sure why this isn't being set correctly
    #------------------------------
    # case_obj.xmlchange("env_run.xml", "ICE_DOMAIN_PATH", " \"\\$DIN_LOC_ROOT/atm/cam/ocnfrac\" " )
    # case_obj.xmlchange("env_run.xml", "ICE_DOMAIN_FILE", "domain.camocn.64x128_USGS_070807.nc" )    

    #------------------------------
    # Change run options
    #------------------------------
    case_obj.xmlchange("env_run.xml", "PIO_REARR_COMM_MAX_PEND_REQ_COMP2IO", 0 )

    case_obj.xmlchange("env_run.xml", "CONTINUE_RUN", cflag )
    case_obj.xmlchange("env_run.xml", "STOP_OPTION" , "ndays" )
    case_obj.xmlchange("env_run.xml", "STOP_N"      , ndays )

    if debug or quick_test :
        case_obj.xmlchange("env_run.xml", "STOP_OPTION" , "nsteps" )
        case_obj.xmlchange("env_run.xml", "STOP_N"      , debug_nsteps )

    #------------------------------
    # DEBUG LEVEL
    #------------------------------
    if debug :
        ### level of debug output, 0=minimum, 1=normal, 2=more, 3=too much
        case_obj.xmlchange("env_run.xml", "INFO_DBUG", 2 )

    #------------------------------
    # Submit the run
    #------------------------------
    os.system(cdcmd+subfile+" --no-batch ")
    

print("\n  case : "+case_name+"\n")

#===============================================================================================================================================================
#===============================================================================================================================================================
#===============================================================================================================================================================
#===============================================================================================================================================================