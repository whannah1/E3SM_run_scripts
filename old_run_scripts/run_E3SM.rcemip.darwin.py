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
newcase,config,build,runsim,debug,clean,mk_nml,quick_test = False,False,False,False,False,False,False, False

# newcase  = True
# clean    = True
# config   = True
build    = True
mk_nml   = True
runsim   = True

quick_test = True     # only run for a few time steps (debug_nsteps)
# debug      = True     # enable debug flags

#--------------------------------------------------------
#--------------------------------------------------------

case_num = "s1_00"     # control - all current defualts  

#--------------------------------------------------------
#--------------------------------------------------------

sst = 300
exp = "RCEMIP_"+str(sst)+"K"

cld = "SP1"    # ZM / SP1 / SP2 / SP2+ECPP
res = "ne4pg1"    # ne4 / ne4pg1 

cflag = "FALSE"

ndays = 1

crm_nx,crm_ny,mod_str = 8,1,"_1km"

debug_nsteps = 5

#==========================================================================================================================================
#==========================================================================================================================================

#--------------------------------------------------------
# Setup the case name
#--------------------------------------------------------

if "ZM" in cld : mod_str,crmdim = "",""
if "SP" in cld : crmdim = "_"+str(crm_nx)+"x"+str(crm_ny) 
    
case_name = "E3SM_"+exp+"_"+cld+"_"+res+crmdim+mod_str+"_"+case_num
# case_name = "E3SM_"+cld+"_"+exp+"_"+res+crmdim+mod_str+"_"+case_num
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
print("\n  case : "+case_name+"\n")
#==========================================================================================================================================
#==========================================================================================================================================
# Create new case
#==========================================================================================================================================
#==========================================================================================================================================

case_obj = E3SM_common.Case( case_name=case_name, res=res, cld=cld, case_dir=case_dir )
case_obj.verbose = True

if "pg1" not in res : 
    grid_opt = res+"_"+res
else:
    grid_opt = res

# compset_opt = " -compset FC5AV1C-L "
if cld=="ZM"  : compset_opt = " -compset FC5AV1C-L-AQUA "
if cld=="SP1" : compset_opt = " -compset SP1V1-AQUA " 

use_SP_compset = False

if newcase == True:
    newcase_cmd = src_dir+"/cime/scripts/create_newcase"
    cmd = newcase_cmd+" -case "+case_dir+" "+compset_opt+" -res "+grid_opt+" -mach "+host
    cmd = cmd+" --mpilib mpich "
    print("\n"+cmd+"\n")
    os.system(cmd)

case_dir = case_dir+"/"

init_dir = home+"/E3SM/init_files/"
# cami_file = "default"

sst_data_filename = "RCEMIP_sst."+str(sst)+"K.nc"
if "ne30" in res : cami_file = "cami_mam3_Linoz_ne30np4_L72_c160214_RCEMIP.nc"
if "ne4"  in res : cami_file = "cami_mam3_Linoz_ne4np4_L72_c160909_RCEMIP.nc"

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

    # crm_nx_rad = crm_nx/2
    crm_nx_rad = 1

    #------------------------------------------------
    # set CAM_CONFIG_OPTS
    #------------------------------------------------
    cam_opt = E3SM_common.get_default_config( cld, nlev_gcm, nlev_crm, crm_nx, crm_ny, crm_nx_rad, crm_dx )

    cpp_opt = " -cppdefs ' -DRCEMIP "

    if "pg1" in res : cpp_opt = cpp_opt+" -DPHYS_GRID_1x1_TEST "

    # if cld=="ZM" : 
    #     cam_opt = " -rad rrtmg -nlev "+str(nlev_gcm)+"  -clubb_sgs -microphys mg2 -chem none "

    
    if "SP" in cld :
        cpp_opt = cpp_opt+" -DSP_ORIENT_RAND "
        # cpp_opt = cpp_opt+" -DAPPLY_POST_DECK_BUGFIXES "
        # cpp_opt = cpp_opt+" -DSP_TK_LIM "
        # cpp_opt = cpp_opt+" -DSP_ESMT -DSP_USE_ESMT "

        #-------------------------------
        # Special SP cases
        #-------------------------------
        # if case_num == "" : cpp_opt = cpp_opt+" -D "

    #-------------------------------
    # Special cases for SP and ZM
    #-------------------------------
    # if res=="ne4pg1" : cpp_opt = cpp_opt+" -DPHYS_GRID_1x1_TEST "

    ### Switch to RRMTGP
    cam_opt = cam_opt.replace("-rad rrtmg","-rad rrtmgp")

    #------------------------------------------------
    #------------------------------------------------

    cam_opt = cam_opt+cpp_opt+" ' "

    if cld=="ZM" or ( "SP" in cld and not use_SP_compset ) : 
        case_obj.xmlchange("env_build.xml", "CAM_CONFIG_OPTS", "\""+cam_opt+"\"" )

    #--------------------------------------------------------
    # Specified SST 
    #--------------------------------------------------------
    case_obj.xmlchange("env_run.xml", "SSTICE_DATA_FILENAME", init_dir+sst_data_filename ) 

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
    case_obj.xmlchange("env_run.xml", "ATM_NCPL", ncpl )

    #------------------------------------------------
    # configure the case
    #------------------------------------------------
    case_obj.setup(clean)

#==========================================================================================================================================
#==========================================================================================================================================
# Build the model
#==========================================================================================================================================
#==========================================================================================================================================
if build == True :

    case_obj.set_debug_mode(debug)
    case_obj.build(clean)

#==========================================================================================================================================
#==========================================================================================================================================
# Write the custom namelist options
#==========================================================================================================================================
#==========================================================================================================================================

### Get local input data directory path
cam_config_opts = case_obj.xmlquery("CAM_CONFIG_OPTS")
compset         = case_obj.xmlquery("COMPSET")
input_data_dir  = case_obj.xmlquery("DIN_LOC_ROOT")

if mk_nml :
    nfile = case_dir+"user_nl_cam"
    file = open(nfile,'w') 

    if debug or quick_test :
        file.write(" nhtfrq    = 0,1,1 \n") 
        file.write(" mfilt     = 1,"+str(debug_nsteps)+","+str(debug_nsteps)+"  \n") 
    else :
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
    # file.write(             ",'dyn_PS','dyn_T' ")
    # file.write(             ",'dyn_U','dyn_V','dyn_OMEGA' ")
    file.write("\n")

    file.write(" fincl3    = 'dyn_PS','dyn_T' \n")
        # file.write(" fincl3    = 'PHIS_SM' \n")

    if cami_file != "default" : file.write(" ncdata  = '"+init_dir+cami_file+"' \n") 

    file.write(" srf_flux_avg = 1 \n")
    
    
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



    #------------------------------
    # RCEMIP namelist settings
    #------------------------------
    
    topo_file = "RCEMIP_topo."+res.replace("pg1","")+".v1.nc"

    file.write(" bnd_topo   = '"+init_dir+topo_file+"' \n")

    # Orbital settings need to end up in drv_in
    nfile = case_dir+"user_nl_cpl"
    drv_file = open(nfile,'w') 
    drv_file.write(" orb_mode           = 'fixed_parameters' \n")
    drv_file.write(" orb_eccen          = 0 \n")
    drv_file.write(" orb_obliq          = 0 \n")
    drv_file.write(" orb_mvelp          = 0 \n")
    drv_file.close()

    file.write(" prescribed_ozone_cycle_yr   = 2000 \n")
    file.write(" prescribed_ozone_type       = 'CYCLICAL' \n")
    file.write(" prescribed_ozone_datapath   = '"+init_dir+"' \n")
    file.write(" prescribed_ozone_file       = 'RCEMIP_ozone.v1.nc' \n")
    file.write(" prescribed_ozone_name       = 'O3' \n")
    # file.write(" prescribed_ozone_type       = 'FIXED' \n")

    #------------------------------
    #------------------------------
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

    # set domain files
    if res=="ne30" :
        domain_ocn_file = "RCEMIP_domain.ocn.ne30np4_gx1v6.v1.nc"
        domain_lnd_file = "RCEMIP_domain.lnd.ne30np4_gx1v6.v1.nc"
    if res=="ne4" :
        domain_ocn_file = "RCEMIP_domain.ocn.ne4np4_oQU240.160614.nc"
        domain_lnd_file = "RCEMIP_domain.lnd.ne4np4_oQU240.160614.nc"
    if res=="ne4pg1"  :
        domain_ocn_file = "RCEMIP_domain.ocn.ne4np1.nc"
        domain_lnd_file = "RCEMIP_domain.lnd.ne4np1.nc"

    ### update xml entries for domain file names and paths
    case_obj.set_domain_file_name_path( init_dir, domain_ocn_file, domain_lnd_file )

    # update xml entry for the SST file
    case_obj.xmlchange("env_run.xml", "SSTICE_DATA_FILENAME", init_dir+sst_data_filename )

#==========================================================================================================================================
#==========================================================================================================================================
# Run the simulation
#==========================================================================================================================================
#==========================================================================================================================================
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
    case_obj.xmlchange("env_run.xml", "ICE_DOMAIN_PATH", " \"\\$DIN_LOC_ROOT/atm/cam/ocnfrac\" " )
    case_obj.xmlchange("env_run.xml", "ICE_DOMAIN_FILE", "domain.camocn.64x128_USGS_070807.nc" )    

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
        # level of debug output, 0=minimum, 1=normal, 2=more, 3=too much
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id INFO_DBUG -val 2")

    #------------------------------
    # Submit the run
    #------------------------------
    os.system(cdcmd+subfile+" --no-batch ")


print("\n  case : "+case_name+"\n")
    
#==========================================================================================================================================
#==========================================================================================================================================