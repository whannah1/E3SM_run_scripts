#!/usr/bin/env python
#===============================================================================================================================================================
#  Jan, 2017 - Walter Hannah - Lawrence Livermore National Lab
#  This script runs atmosphere-only, single-column simulations of E3SM
#===============================================================================================================================================================
import sys
import os
import fileinput
import subprocess
home = os.getenv("HOME")
host = os.getenv("host")
if host==None : host = os.getenv("HOST")
opsys = os.getenv("os")

if "edison" in host : host,acct = "edison"  ,""
if "cori"   in host : host,acct = "cori-knl","m2861"
if "titan"  in host : host,acct = "titan"   ,"cli115"

# if opsys=="Darwin" : host = "mac"
#===============================================================================================================================================================
#===============================================================================================================================================================
newcase,config,build,runsim,debug,clean,mk_nml = False,False,False,False,False,False,False

newcase  = True
# clean    = True
config   = True
build    = True
# mk_nml   = True
# runsim   = True

debug    = True       # enable debug flags

#--------------------------------------------------------
#--------------------------------------------------------
case_num = "00"     # control - all current defualts  

exp = "GATE"    # GATE / ARM95 / ARM97 / TOGA / TWP / BOMEX / RICO / GCSS_SH
res = "ne4"     # ne4 / T42

wall_time =  "0:30:00"

#===============================================================================================================================================================
#===============================================================================================================================================================

#--------------------------------------------------------
# Setup the case name
#--------------------------------------------------------

case_name = "E3SM_SCM_"+exp+"_"+res+"_"+case_num

#--------------------------------------------------------
# Setup directory names
#--------------------------------------------------------
top_dir     = home+"/E3SM/"
srcmod_dir  = top_dir+"mod_src/"
nmlmod_dir  = top_dir+"mod_nml/"

src_dir = home+"/E3SM/E3SM_SRC_master"

scratch_dir = os.getenv("CSCRATCH","")
if scratch_dir=="" : 
    if opsys=="Darwin" : 
        scratch_dir = home+"/Model/ACME/scratch/"

run_dir = scratch_dir+"/"+case_name+"/run"

#===================================================================================
#===================================================================================

### Aerosol specification
#  1) cons_droplet  (sets cloud liquid and ice concentration to a constant)
#  2) prescribed    (uses climatologically prescribed aerosol concentration)
#  3) observed      ()
init_aero_type = "cons_droplet"

### Location of IOP file
iop_path = "atm/cam/scam/iop"

### Prescribed aerosol file path and name
presc_aero_path = "atm/cam/chem/trop_mam/aero"
presc_aero_file = "mam4_0.9x1.2_L72_2000clim_c170323.nc"

#----------------------------------------------------
# Deep Convection Cases
#----------------------------------------------------
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

#----------------------------------------------------
# Shallow Convection Cases
#----------------------------------------------------
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
print("")
print("  case : "+case_name)
print("")
#===============================================================================================================================================================
#===============================================================================================================================================================
# Create new case
#===============================================================================================================================================================
#===============================================================================================================================================================

compset_opt = " -compset F_SCAM5 "

if newcase == True:

    newcase_cmd = src_dir+"/cime/scripts/create_newcase"
    cmd = newcase_cmd+" -case "+case_dir+" "+compset_opt+" -res "+res+"_"+res+" -mach "+host
    if res == "T42" : cmd = cmd+" --mpilib mpi-serial "
    if res == "ne4" : cmd = cmd+" --mpilib mpich "
    # if res == "ne4" : cmd = cmd+" --mpilib open-mpi "
    if host=="edison" : cmd = cmd+" -q normal "
    print("")
    print(cmd)
    print("")
    os.system(cmd)

case_dir = case_dir+"/"

#=================================================================================================================================
# Write the custom namelist options
#=================================================================================================================================

# Get local input data directory path
(input_data_dir, err) = subprocess.Popen(cdcmd+"./xmlquery DIN_LOC_ROOT -value", stdout=subprocess.PIPE, shell=True).communicate()

if mk_nml :
    nfile = case_dir+"user_nl_cam"
    file = open(nfile,'w') 

    file.write(" nhtfrq    = 0,1 \n") 
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
    file.write(             ",'UBOT','VBOT','QBOT','TBOT'")
    file.write(             ",'UAP','VAP','QAP','QBP','TAP','TBP','TFIX'")
    file.write(             ",'CLOUD','CLDLIQ','CLDICE' ")
    file.write(             ",'PTTEND','DTCOND','DCQ' ")
    file.write(             ",'AEROD_v','EXTINCT'")         # surface fluxes
    file.write("\n")

    
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
    # nfile = case_dir+"user_nl_cice"
    # file = open(nfile,'w') 
    # file.write(" histfreq = 'x','x','x','x','x' \n")
    # file.close()

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

#===============================================================================================================================================================
#===============================================================================================================================================================
# Configure the case
#===============================================================================================================================================================
#===============================================================================================================================================================
if config == True:
    #------------------------------------------------
    # set custom CAM_CONFIG_OPTS
    #------------------------------------------------
    cam_opt = " -scam -phys cam5 -rad rrtmg -nlev 72  -clubb_sgs -microphys mg2 "

    if res == "T42" : cam_opt = cam_opt + " -nospmd -nosmp "

    if init_aero_type == "cons_droplet" : chem_opt = " -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates "
    if init_aero_type == "prescribed"   : chem_opt = " -chem none"

    # cpp_opt = " -cppdefs ' "
    # cpp_opt = cpp_opt+" ' "
        
    cam_opt = cam_opt+chem_opt #+cpp_opt 

    CMD = cdcmd+"./xmlchange --file env_build.xml --id CAM_CONFIG_OPTS --val \""+cam_opt+"\""
    print(CMD)
    os.system(CMD)

    #------------------------------------------------
    #------------------------------------------------
    CMD = cdcmd+"./xmlchange PTS_MODE=\"TRUE\",PTS_LAT=\""+str(scmlat)+"\",PTS_LON=\""+str(scmlon)+"\""
    print(CMD)
    os.system(CMD)
    
    CMD = cdcmd+"./xmlchange MASK_GRID=\"USGS\" "
    print(CMD)
    os.system(CMD)

    #------------------------------------------------
    # Use CLM 4.5
    #------------------------------------------------
    clm_opt = " -phys clm4_5 "

    CMD = cdcmd+"./xmlchange --file env_build.xml --id CLM_CONFIG_OPTS --val \""+clm_opt+"\" "
    print(CMD)
    os.system(CMD)

    #------------------------------------------------
    # set run-time variables
    #------------------------------------------------
    os.system(cdcmd+"./xmlchange --file env_run.xml   --id RUN_STARTDATE  --val "+start_date)
    os.system(cdcmd+"./xmlchange --file env_run.xml   --id START_TOD      --val "+str(start_in_sec))

    #------------------------------------------------
    # Change processor count
    #------------------------------------------------
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val 1 ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_LND -val 1 ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ICE -val 1 ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_OCN -val 1 ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_CPL -val 1 ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_GLC -val 1 ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_WAV -val 1 ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ROF -val 1 ")

    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_ATM -val 1 ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_LND -val 1 ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_OCN -val 1 ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_ICE -val 1 ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_CPL -val 1 ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_GLC -val 1 ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_WAV -val 1 ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTHRDS_ROF -val 1 ") 

    if res == "ne4" :
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id ROOTPE_ATM -val 0 ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id ROOTPE_LND -val 0 ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id ROOTPE_OCN -val 0 ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id ROOTPE_ICE -val 0 ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id ROOTPE_CPL -val 0 ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id ROOTPE_GLC -val 0 ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id ROOTPE_WAV -val 0 ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id ROOTPE_ROF -val 0 ")

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

    #----------------------------------------------------------
    #----------------------------------------------------------
    # Don't want to write restarts as this appears to be broken for  CICE model in SCM.  For now set this to a high value to avoid
    os.system(cdcmd+"./xmlchange PIO_TYPENAME=\"netcdf\" ")
    os.system(cdcmd+"./xmlchange REST_N=30000 ")

    #----------------------------------------------------------
    #----------------------------------------------------------
    # Modify some parameters for CICE to make it SCM compatible 
    os.system(cdcmd+"./xmlchange CICE_AUTO_DECOMP=\"FALSE\" ")
    os.system(cdcmd+"./xmlchange CICE_DECOMPTYPE=\"blkrobin\" ")
    os.system(cdcmd+"./xmlchange --id CICE_BLCKX --val 1 ")
    os.system(cdcmd+"./xmlchange --id CICE_BLCKY --val 1 ")
    os.system(cdcmd+"./xmlchange --id CICE_MXBLCKS --val 1 ")
    os.system(cdcmd+"./xmlchange CICE_CONFIG_OPTS=\"-nodecomp -maxblocks 1 -nx 1 -ny 1\" ")

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


#===============================================================================================================================================================
#===============================================================================================================================================================
# Run the simulation
#===============================================================================================================================================================
#===============================================================================================================================================================
if runsim == True:

    runfile = case_dir+".case.run"
    subfile = case_dir+"case.submit"

    #------------------------------
    #------------------------------
    # not sure why this isn't being set correctly
    if opsys == "Darwin" :
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id ICE_DOMAIN_PATH  -val \"\\$DIN_LOC_ROOT/atm/cam/ocnfrac\" ")
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id ICE_DOMAIN_FILE  -val domain.camocn.64x128_USGS_070807.nc ")

    #------------------------------
    # Change run options
    #------------------------------
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_OPTION  -val "+stop_option)
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_N       -val "+str(stop_n)) 

    # if opsys=="Darwin" and res=="ne4":
    #     os.system(cdcmd+"./xmlchange --file env_run.xml   --id PIO_REARR_COMM_MAX_PEND_REQ_COMP2IO  --val 64 ")

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
    # Set the wall clock limit
    #------------------------------
    os.system(cdcmd+"./xmlchange -file env_batch.xml -id JOB_WALLCLOCK_TIME -val "+wall_time)
    
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
    
#===============================================================================================================================================================
#===============================================================================================================================================================
