#!/usr/bin/env python
#===================================================================================================
#  Feb, 2019 - Walter Hannah - Lawrence Livermore National Lab
#  This script runs atmosphere-only, single-column simulations of E3SM
#===================================================================================================
import sys
import os
import fileinput
import subprocess
import run_E3SM_common as E3SM_common
home = E3SM_common.get_home_dir()
host = E3SM_common.get_host_name()
#===================================================================================================
#===================================================================================================
newcase,config,build,runsim,debug,clean,mk_nml,debug_queue = False,False,False,False,False,False,False,False

newcase  = True
# clean    = True
config   = True
build    = True
mk_nml   = True
runsim   = True

# debug     = True       # enable debug flags
debug_queue = True
#----------------------------------------------------------
#----------------------------------------------------------
case_num = "s1_00"     # control - all current defualts  

cld = "ZM"     # ZM / SP1 / SP2
exp = "GATE"    # GATE / ARM95 / ARM97 / TOGA / TWP / BOMEX / RICO / GCSS_SH / RCE_300 / RCE_295 / RCE_305
res = "ne4"     # ne4 / T42

wall_time =  "0:30:00"

cflag = "FALSE"                      # continue flag - Don't forget to set this!!!! 
# cflag = "TRUE"

crm_nx,crm_ny,mod_str =  64,1,"_1km" 
#===================================================================================================
#===================================================================================================

#----------------------------------------------------------
# Set the case name
#----------------------------------------------------------
if "SP" in cld :
    crmdim = "_"+str(crm_nx)+"x"+str(crm_ny) 
else :
    crmdim  = ""
    mod_str = ""

case_name = "E3SM_SCM_"+exp+"_"+cld+"_"+res+crmdim+mod_str+"_"+case_num

#----------------------------------------------------------
# Setup directory names
#----------------------------------------------------------
top_dir     = home+"/E3SM/"
srcmod_dir  = top_dir+"mod_src/"
nmlmod_dir  = top_dir+"mod_nml/"

src_dir = home+"/E3SM/E3SM_SRC_master"
if "s1"  in case_num : src_dir = home+"/E3SM/E3SM_SRC1"
if "s2"  in case_num : src_dir = home+"/E3SM/E3SM_SRC2"

scratch_dir = os.getenv("CSCRATCH","")
run_dir = scratch_dir+"/"+case_name+"/run"

#----------------------------------------------------------
# Set the physics time step
#----------------------------------------------------------
dtime = 20*60
ncpl  = 86400 / dtime

#===================================================================================================
#===================================================================================================
# Aerosol specification
#  1) cons_droplet  (sets cloud liquid and ice concentration to a constant)
#  2) prescribed    (uses climatologically prescribed aerosol concentration)
#  3) observed      ()
init_aero_type = "cons_droplet"

# Location of IOP file
iop_path = "atm/cam/scam/iop"

# Prescribed aerosol file path and name
presc_aero_path = "atm/cam/chem/trop_mam/aero"
presc_aero_file = "mam4_0.9x1.2_L72_2000clim_c170323.nc"

#----------------------------------------------------------
# RCE Cases
#----------------------------------------------------------

if "RCE" in exp :
    scmlat = 0.0
    scmlon = 0.0
    do_iop_srf_prop   = ".false."       # Use surface fluxes in IOP file?
    do_scm_relaxation = ".false."       # Relax case to observations?
    do_turnoff_swrad  = ".true."       # Turn off SW calculation
    do_turnoff_lwrad  = ".false."       # Turn off LW calculation
    micro_nccons_val  = "100.0D6"       # cons_droplet value for liquid
    micro_nicons_val  = "0.0001D6"      # cons_droplet value for ice
    # micro_nicons_val  = "1D5"           # cons_droplet value for ice
    start_date        = "0000-01-01"    # Start date in IOP file
    start_in_sec      = 0               # start time in seconds in IOP file
    stop_option       = "ndays"
    stop_n            = 100

    if exp=="RCE_295" : iop_file = "RCE_iopfile.SST_295K.nc"
    if exp=="RCE_300" : iop_file = "RCE_iopfile.SST_300K.nc"
    if exp=="RCE_305" : iop_file = "RCE_iopfile.SST_305K.nc"


#----------------------------------------------------------
# Deep Convection Cases
#----------------------------------------------------------

if exp=="GATE" :
    scmlat = 9.00
    scmlon = 336.0
    do_iop_srf_prop   = ".false."       # Use surface fluxes in IOP file?
    do_scm_relaxation = ".false."       # Relax case to observations?
    do_turnoff_swrad  = ".false."       # Turn off SW calculation
    do_turnoff_lwrad  = ".false."       # Turn off LW calculation
    micro_nccons_val  = "70.0D6"        # cons_droplet value for liquid
    micro_nicons_val  = "0.0001D6"      # cons_droplet value for ice
    start_date        = "1974-08-30"    # Start date in IOP file
    start_in_sec      = 0               # start time in seconds in IOP file
    # stop_option       = "nsteps"
    # stop_n            = 10
    stop_option       = "ndays"
    stop_n            = 1 #30
    iop_file          = "GATEIII_iopfile_4scam.nc" 

if exp=="ARM95" :
    scmlat = 36.6
    scmlon = 262.5
    do_iop_srf_prop   = ".true."       # Use surface fluxes in IOP file?
    do_scm_relaxation = ".false."       # Relax case to observations?
    do_turnoff_swrad  = ".false."       # Turn off SW calculation
    do_turnoff_lwrad  = ".false."       # Turn off LW calculation
    micro_nccons_val  = "100.0D6"        # cons_droplet value for liquid
    micro_nicons_val  = "0.0001D6"      # cons_droplet value for ice
    start_date        = "1995-07-18"    # Start date in IOP file
    start_in_sec      = 19800               # start time in seconds in IOP file
    stop_option       = "ndays"
    stop_n            = 17
    iop_file          = "ARM95_iopfile_4scam.nc"

if exp=="ARM97" :
    scmlat = 36.6
    scmlon = 262.5
    do_iop_srf_prop   = ".true."       # Use surface fluxes in IOP file?
    do_scm_relaxation = ".false."       # Relax case to observations?
    do_turnoff_swrad  = ".false."       # Turn off SW calculation
    do_turnoff_lwrad  = ".false."       # Turn off LW calculation
    micro_nccons_val  = "100.0D6"        # cons_droplet value for liquid
    micro_nicons_val  = "0.0001D6"      # cons_droplet value for ice
    start_date        = "1997-06-19"    # Start date in IOP file
    start_in_sec      = 84585               # start time in seconds in IOP file
    stop_option       = "ndays"
    stop_n            = 26
    iop_file          = "ARM97_iopfile_4scam.nc"

if exp=="TOGA" :
    scmlat = -2.10
    scmlon = 154.69
    do_iop_srf_prop   = ".true."       # Use surface fluxes in IOP file?
    do_scm_relaxation = ".false."       # Relax case to observations?
    do_turnoff_swrad  = ".false."       # Turn off SW calculation
    do_turnoff_lwrad  = ".false."       # Turn off LW calculation
    micro_nccons_val  = "70.0D6"        # cons_droplet value for liquid
    micro_nicons_val  = "0.0001D6"      # cons_droplet value for ice
    start_date        = "1992-12-18"    # Start date in IOP file
    start_in_sec      = 64800               # start time in seconds in IOP file
    stop_option       = "nsteps"
    stop_n            = 1512
    # stop_option       = "ndays"
    # stop_n            = 2
    iop_file          = "TOGAII_iopfile_4scam.nc"  

if exp=="TWP" :
    scmlat = -12.43
    scmlon = 130.89
    do_iop_srf_prop   = ".true."        # Use surface fluxes in IOP file?
    do_scm_relaxation = ".false."       # Relax case to observations?
    do_turnoff_swrad  = ".false."       # Turn off SW calculation
    do_turnoff_lwrad  = ".false."       # Turn off LW calculation
    micro_nccons_val  = "70.0D6"        # cons_droplet value for liquid
    micro_nicons_val  = "0.0001D6"      # cons_droplet value for ice
    start_date        = "2006-01-17"    # Start date in IOP file
    start_in_sec      = 10800               # start time in seconds in IOP file
    stop_option       = "nsteps"
    stop_n            = 1926
    # stop_option       = "ndays"
    # stop_n            = 2
    iop_file          = "TWP06_iopfile_4scam.nc"

#----------------------------------------------------------
# Shallow Convection Cases
#----------------------------------------------------------

if exp=="BOMEX" :
    scmlat = 15.0
    scmlon = 300.0
    do_iop_srf_prop   = ".true."        # Use surface fluxes in IOP file?
    do_scm_relaxation = ".false."       # Relax case to observations?
    do_turnoff_swrad  = ".true."        # Turn off SW calculation
    do_turnoff_lwrad  = ".true."        # Turn off LW calculation
    micro_nccons_val  = "70.0D6"        # cons_droplet value for liquid
    micro_nicons_val  = "0.0001D6"      # cons_droplet value for ice
    start_date        = "1969-06-25"    # Start date in IOP file
    start_in_sec      = 0               # start time in seconds in IOP file
    stop_option       = "ndays"
    stop_n            = 5
    iop_file          = "BOMEX_iopfile_4scam.nc"

if exp=="RICO" :
    scmlat = 17.97
    scmlon = 298.54
    do_iop_srf_prop   = ".false."       # Use surface fluxes in IOP file?
    do_scm_relaxation = ".false."       # Relax case to observations?
    do_turnoff_swrad  = ".true."        # Turn off SW calculation
    do_turnoff_lwrad  = ".true."        # Turn off LW calculation
    micro_nccons_val  = "70.0D6"        # cons_droplet value for liquid
    micro_nicons_val  = "0.0001D6"      # cons_droplet value for ice
    start_date        = "2004-12-16"    # Start date in IOP file
    start_in_sec      = 0               # start time in seconds in IOP file
    stop_option       = "ndays"
    stop_n            = 1
    iop_file          = "RICO_iopfile_4scam.nc"

if exp=="GCSS_SH" :
    scmlat = 36.0
    scmlon = 262.5
    do_iop_srf_prop   = ".true."        # Use surface fluxes in IOP file?
    do_scm_relaxation = ".false."       # Relax case to observations?
    do_turnoff_swrad  = ".false."       # Turn off SW calculation
    do_turnoff_lwrad  = ".false."       # Turn off LW calculation
    micro_nccons_val  = "50.0D6"        # cons_droplet value for liquid
    micro_nicons_val  = "0.0001D6"      # cons_droplet value for ice
    start_date        = "1997-06-21"    # Start date in IOP file
    start_in_sec      = 0               # start time in seconds in IOP file
    stop_option       = "nsteps"
    stop_n            = 43
    iop_file          = "ARM_shallow_iopfile_4scam.nc"


#===================================================================================
#===================================================================================
os.system("cd "+top_dir)
case_dir  = top_dir+"Cases/"+case_name 
cdcmd = "cd "+case_dir+" ; "

print("\n  case : "+case_name+"\n")
#===================================================================================================
#===================================================================================================
# Create new case
#===================================================================================================
#===================================================================================================
case_obj = E3SM_common.Case( case_name=case_name, res=res, cld=cld, case_dir=case_dir )
use_SP_compset = False
compset_opt = " -compset F_SCAM5 "
if newcase == True:
    newcase_cmd = src_dir+"/cime/scripts/create_newcase"
    cmd = newcase_cmd+" -case "+case_dir+" "+compset_opt+" -res "+res+"_"+res+" -mach "+host
    print("\n"+cmd+"\n")
    os.system(cmd)
case_dir = case_dir+"/"
#===================================================================================================
#===================================================================================================
# Write custom namelist options
#===================================================================================================
#===================================================================================================

# Get local input data directory path
(input_data_dir, err) = subprocess.Popen(cdcmd+"./xmlquery DIN_LOC_ROOT -value", stdout=subprocess.PIPE, shell=True).communicate()

#----------------------------------------------------------
# Copy RCE iop into input directory
#----------------------------------------------------------
if "RCE" in exp :
    print("")
    print("Copying RCE iop file to input direcotry")
    dest_file = input_data_dir+"/"+iop_path+"/"+iop_file
    # if os.path.isfile(dest_file) :
    ### always overwrite just in case file has been updated
    # CMD = "cp -rp "+home+"/E3SM/init_files/"+iop_file+"  "+dest_file
    # print("")
    # print(CMD)
    # os.system(CMD)
    # print("")
#----------------------------------------------------------
#----------------------------------------------------------

if mk_nml :
    nfile = case_dir+"user_nl_cam"
    file = open(nfile,'w') 

    file.write(" nhtfrq    = 0,1 \n") 
    file.write(" mfilt     = 1,5000  \n") 

    if "RCE" in exp :
        file.write(" nhtfrq    = 0,-1 \n") 
        file.write(" mfilt     = 1,5000  \n") 

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
    # file.write(             ",'UBOT','VBOT','QBOT','TBOT'")
    # file.write(             ",'UAP','VAP','QAP','QBP','TAP','TBP','TFIX'")
    file.write(             ",'CLOUD','CLDLIQ','CLDICE' ")
    # file.write(             ",'QEXCESS' ")
    # file.write(             ",'PTTEND','DTCOND','DCQ' ")
    # file.write(             ",'AEROD_v','EXTINCT'")         # surface fluxes
    if "SP" in cld :
        file.write(         ",'SPDT','SPDQ' ")
        file.write(         ",'CLOUDTOP' ")
        # file.write(         ",'CRM_T','CRM_QV','CRM_QC','CRM_QPC','CRM_PREC' ")
        file.write(         ",'MU_CRM','MD_CRM','EU_CRM','DU_CRM','ED_CRM' ")
        file.write(         ",'SPQTFLX','SPQTFLXS'")
        file.write(         ",'SPTLS','SPQTLS' ")
        file.write(         ",'SPQPEVP','SPMC' ")
        file.write(         ",'SPMCUP','SPMCDN','SPMCUUP','SPMCUDN' ")
        # file.write(         ",'SPQC','SPQR' ")
        # file.write(         ",'SPQI','SPQS','SPQG' ")
        # file.write(         ",'ZMMTU','ZMMTV','U_ESMT','V_ESMT','U_ESMT_PGF','V_ESMT_PGF' ")
    # if "SP_CRM_SPLIT" in cam_config_opts :
    #     file.write(         ",'SPDT1','SPDQ1','SPDT2','SPDQ2' ")
    #     file.write(         ",'SPTLS1','SPTLS2' ")
    file.write("\n")

    
    if "SP" in cld : 
        file.write(" cld_macmic_num_steps = 1 \n") 
    else:
        if res == "T42" : file.write(" cld_macmic_num_steps = 8 \n")   # only for CLUBB?
        if res == "ne4" : file.write(" cld_macmic_num_steps = 6 \n")   # only for CLUBB?
    file.write(" cosp_lite = .true. \n") 
    file.write(" use_gw_front = .true. \n") 
    file.write(" iopfile = '"+input_data_dir+"/"+iop_path+"/"+iop_file+"' \n") 
    file.write(" scm_iop_srf_prop = "+do_iop_srf_prop+"  \n") 
    file.write(" scm_relaxation   = "+do_scm_relaxation+" \n") 
    file.write(" iradlw = 1 \n") 
    file.write(" iradsw = 1 \n") 
    file.write(" swrad_off = "+do_turnoff_swrad+"  \n") 
    file.write(" lwrad_off = "+do_turnoff_lwrad+" \n") 
    file.write(" scmlat = "+str(scmlat)+" \n") 
    file.write(" scmlon = "+str(scmlon)+" \n") 

    if "SP" in cld : file.write(" srf_flux_avg = 1 \n")

    if init_aero_type == "cons_droplet" :
        file.write(" micro_do_nccons = .true. \n")
        file.write(" micro_do_nicons = .true. \n")
        file.write(" micro_nccons = "+micro_nccons_val+" \n")
        file.write(" micro_nicons = "+micro_nicons_val+" \n")

    
    if init_aero_type == "prescribed" :
        file.write(" use_hetfrz_classnuc = .false. \n")
        file.write(" aerodep_flx_type = 'CYCLICAL' \n")
        file.write(" aerodep_flx_datapath = '"+input_data_dir+"/"+presc_aero_path+"'  \n")
        file.write(" aerodep_flx_file = '"+presc_aero_file+"' \n")
        file.write(" aerodep_flx_cycle_yr = 01 \n")
        file.write(" prescribed_aero_type = 'CYCLICAL' \n")
        file.write(" prescribed_aero_datapath='"+input_data_dir+"/"+presc_aero_path+"' \n")
        file.write(" prescribed_aero_file='"+presc_aero_file+"' \n")
        file.write(" prescribed_aero_cycle_yr = 01 \n")

    # if observed aerosols then set flag
    if init_aero_type == "observed" : 
        file.write(" scm_observed_aero = .true. \n")


    file.close() 

    # Turn off CICE history files
    nfile = case_dir+"user_nl_cice"
    file = open(nfile,'w') 
    file.write(" histfreq = 'x','x','x','x','x' \n")
    file.close()

    ### convective gustiness modification
    # nfile = case_dir+"user_nl_cpl"
    # file = open(nfile,'w') 
    # file.write(" gust_fac = 1 \n")
    # file.close()

    if res == "T42" :
        nfile = case_dir+"user_nl_cam"
        file = open(nfile,'a') 
        file.write(" fsurdat = '"+input_data_dir+"/lnd/clm2/surfdata_map/surfdata_64x128_simyr2000_c170111.nc' \n")
        file.close()
#===================================================================================================
#===================================================================================================
# Configure the case
#===================================================================================================
#===================================================================================================
if config == True:
    #----------------------------------------------------------
    # set vertical levels and CRM domain parameters
    #----------------------------------------------------------
    nlev_gcm = 72
    nlev_crm = 58
    # crm_adv = "MPDATA"        # default is set in get_default_config()
    # crm_dt = 5                # default is set in get_default_config()
    crm_dx = 1000
    if mod_str == "_8km"  : crm_dx = 8000
    if mod_str == "_4km"  : crm_dx = 4000
    if mod_str == "_2km"  : crm_dx = 2000
    if mod_str == "_1km"  : crm_dx = 1000
    if mod_str == "_0.5km": crm_dx = 500
    crm_nx_rad = crm_nx/2
    #----------------------------------------------------------
    # set CAM_CONFIG_OPTS
    #----------------------------------------------------------
    cam_opt = E3SM_common.get_default_config( cld, nlev_gcm, nlev_crm, crm_nx, crm_ny, crm_nx_rad, crm_dx )
    # cpp_opt = " -cppdefs ' -DRCEMIP "
    cpp_opt = " -cppdefs '  "
    if "SP" in cld :
        cpp_opt = cpp_opt+" -DSP_ORIENT_RAND "
        cpp_opt = cpp_opt+" -DAPPLY_POST_DECK_BUGFIXES "
        # cpp_opt = cpp_opt+" -DSP_TK_LIM "
        # cpp_opt = cpp_opt+" -DSP_ESMT -DSP_USE_ESMT "
        #-------------------------------
        # Special cases
        #-------------------------------
        # if case_num=='03' : cpp_opt = cpp_opt+" -DSP_USE_DIFF "   # enable normal GCM thermodynamic diffusion        
        # if case_num == '' : cpp_opt = cpp_opt+" -DSP_ESMT_PGF "
        # if case_num == '' : cpp_opt = cpp_opt+" -DSP_ESMT  -DSPMOMTRANS  -DSP_USE_ESMT  "
        # if case_num == '' : cpp_opt = cpp_opt+" -DSP_ESMT -DSP_USE_ESMT -DSP_ESMT_PGF "
        #-------------------------------
        #-------------------------------
    # Close the cppdef string
    cam_opt = cam_opt+cpp_opt+" ' "
    # Make sure "-phys cam5" is in config opts
    if "-phys cam5" not in cam_opt : cam_opt = " -phys cam5 " +cam_opt
    # Set configure options
    case_obj.xmlchange("env_build.xml", "CAM_CONFIG_OPTS", "\""+cam_opt+"\"" )
    #----------------------------------------------------------
    #----------------------------------------------------------
    case_obj.xmlchange("env_run.xml", "PTS_MODE", "TRUE" )
    case_obj.xmlchange("env_run.xml", "PTS_LAT", scmlat )
    case_obj.xmlchange("env_run.xml", "PTS_LON", scmlon )
    case_obj.xmlchange("env_build.xml", "MASK_GRID", "USGS" )
    #----------------------------------------------------------
    # Use CLM 4.5
    #----------------------------------------------------------
    # case_obj.xmlchange("env_build.xml", "CLM_CONFIG_OPTS", "\" -phys clm4_5 \"" )
    #----------------------------------------------------------
    # set run-time variables
    #----------------------------------------------------------
    case_obj.xmlchange("env_run.xml", "RUN_STARTDATE", start_date )
    case_obj.xmlchange("env_run.xml", "START_TOD",      start_in_sec ) 
    #----------------------------------------------------------
    # Change processor/thread count
    #----------------------------------------------------------
    case_obj.xmlchange("env_mach_pes.xml", "TOTALPES", 1 )
    case_obj.set_NTASKS_all(1)
    case_obj.set_ROOTPE_all(0)
    case_obj.set_NTHRDS_all(1)      # Make sure threading is off
    #----------------------------------------------------------
    # Set the timestep
    #----------------------------------------------------------
    case_obj.xmlchange("env_run.xml", "ATM_NCPL", ncpl )
    #----------------------------------------------------------
    # configure the case
    #----------------------------------------------------------    
    case_obj.setup(clean)
#===================================================================================================
#===================================================================================================
# Build the model
#===================================================================================================
#===================================================================================================
if build == True:
    
    case_obj.xmlchange("env_run.xml", "PIO_TYPENAME",   "\"netcdf\"" )

    # Don't want to write restarts as this appears to be broken for  
    # CICE model in SCM.  For now set this to a high value to avoid    
    case_obj.xmlchange("env_run.xml", "REST_N", 30000 )
    #----------------------------------------------------------
    # Modify some parameters for CICE to make it SCM compatible 
    case_obj.xmlchange("env_build.xml", "CICE_AUTO_DECOMP", "\"FALSE\"" )
    case_obj.xmlchange("env_build.xml", "CICE_DECOMPTYPE",  "\"blkrobin\"" )
    case_obj.xmlchange("env_build.xml", "CICE_CONFIG_OPTS", "\"-nodecomp -maxblocks 1 -nx 1 -ny 1\"" )
    case_obj.xmlchange("env_build.xml", "CICE_BLCKX",   1 )
    case_obj.xmlchange("env_build.xml", "CICE_BLCKY",   1 )
    case_obj.xmlchange("env_build.xml", "CICE_MXBLCKS", 1 )
    #----------------------------------------------------------
    case_obj.set_debug_mode(debug)
    case_obj.build(clean)
#===================================================================================================
#===================================================================================================
# Run the simulation
#===================================================================================================
#===================================================================================================
if runsim == True:
    runfile = case_dir+".case.run"
    subfile = case_dir+"case.submit"
    #----------------------------------------------------------
    # Change run options
    #----------------------------------------------------------
    case_obj.xmlchange("env_run.xml", "CONTINUE_RUN", cflag )
    case_obj.xmlchange("env_run.xml", "STOP_OPTION" , stop_option )
    case_obj.xmlchange("env_run.xml", "STOP_N"      , stop_n )
    case_obj.xmlchange("env_batch.xml", "JOB_WALLCLOCK_TIME", wall_time )
    #----------------------------------------------------------
    # set the queue
    #----------------------------------------------------------    
    if debug_queue : 
        case_obj.xmlchange("env_batch.xml", "JOB_QUEUE", "debug" )
    else :
        case_obj.xmlchange("env_batch.xml", "JOB_QUEUE", "regular" )
    #----------------------------------------------------------
    # DEBUG LEVEL
    #----------------------------------------------------------
    if debug :
        # level of debug output, 0=minimum, 1=normal, 2=more, 3=too much
        case_obj.xmlchange("env_run.xml", "INFO_DBUG", 2 )
        # for debug mode, make sure that we will get a core dump file 
        # in the event that we get a segmentation fault
        f = open(runfile, "r")
        contents = f.readlines()
        f.close()
        # Find the line to add the resource statement
        index = -1
        for num, line in enumerate(contents, 1):
            if "def _main_func(description):" in line: index = num+1
            if "resource.setrlimit" in line: index = -1
        # If found and not already modified then add the resource statement
        if index > 0 :
            contents.insert(index  , "    import resource \n")
            contents.insert(index+1, "    resource.setrlimit(resource.RLIMIT_CORE, (resource.RLIM_INFINITY, resource.RLIM_INFINITY)) \n")
            contents.insert(index+2, "    \n")
            f = open(runfile, "w")
            contents = "".join(contents)
            f.write(contents)
            f.close()
    #----------------------------------------------------------
    # Submit the run
    #----------------------------------------------------------
    case_obj.submit()

print("\n  case : "+case_name+"\n")
#===================================================================================================
#===================================================================================================
