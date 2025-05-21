#!/usr/bin/env python
#===================================================================================================
#  Jan, 2018 - Walter Hannah - Lawrence Livermore National Lab
#  This script runs atmosphere only simulations of E3SM on OLCF machines (Titan, Summit, etc)
#===================================================================================================
import sys
import os
import fileinput
import subprocess
import run_E3SM_common as E3SM_common

home = E3SM_common.get_home_dir()
host = E3SM_common.get_host_name()
acct = E3SM_common.get_host_acct(host)

newcase,config,build,runsim,continue_run,clean,mk_nml = False,False,False,False,False,False,False
debug,test_run,debug_queue,inc_remap,debug_chks,disable_bfb = False,False,False,False,False,False
#===================================================================================================
#===================================================================================================

# newcase      = True
# clean        = True
# config       = True
# build        = True
mk_nml       = True
runsim       = True
# continue_run = True

# test_run    = True       # hourly output only (no h2)
debug       = True       # enable debug mode
debug_queue = True       # use debug queue + use debug_nsteps

# debug_chks  = True       # enable state_debug_checks (namelist)
# inc_remap   = True       # Increase vertical remap parameter to reduce timestep via atm namelist
# disable_bfb = True       # Use this to get past a random crash (slightly alters the weather of the restart)

use_memcheck = False

#--------------------------------------------------------
#--------------------------------------------------------
# case_num = "00"     # control - all current defaults  

# case_num = "02a"     # CRM orientation sensitivity - SP_ORIENT_RAND
# case_num = "02b"     # CRM orientation sensitivity - SP_DIR_NS
# case_num = "02c"     # CRM orientation sensitivity - east-west
# case_num = "02d"     # CRM orientation sensitivity - SP_ORIENT_RAND + SP_ORIENT_RAND_LIMIT
# case_num = "02e"     # CRM orientation sensitivity - SP_ORIENT_FLIPFLOP

### SRC1 runs
case_num = "s1_00"    # ???

### SRC2 runs 
# case_num = "s2_50a"   # SP_ALT_TPHYSBC
# case_num = "s2_50b"   # SP_ALT_TPHYSBC + DIFFUSE_PHYS_TEND
# case_num = "s2_50c"   # SP_ALT_TPHYSBC + DIFFUSE_PHYS_TEND + PHYS_HYPERVIS_FACTOR_5X5

#--------------------------------------------------------
#--------------------------------------------------------
arch = "CPU"   # GPU / CPU

cld = "SP1"    # ZM / SP1 / SP2 / SP2+ECPP
exp = "ESMT-TEST"    # CTL / EXP / AMIP / BRANCH / TEST / TIMING_TEST 
res = "ne4"   # ne120 / ne30 / ne16 / ne4 / 0.9x1.25 / 1.9x2.5

if "ZM" in cld : ndays,resub = (73*2),1 #(5)       # 5=2yr, 15=6yr, 25=10yr
# if "SP" in cld : ndays,resub = 25,15
if "SP" in cld : ndays,resub = 1,0

# num_nodes,crm_nx,crm_ny,crm_dx = 15,64,1,4000
# num_nodes,crm_nx,crm_ny,crm_dx = 15,64,1,1000

if res=="ne4": num_nodes,crm_nx,crm_ny,crm_dx = 1,64,1,1000
if res=="ne30": num_nodes,crm_nx,crm_ny,crm_dx = 15,64,1,1000


if num_nodes>= 1 : wall_time =  "2:00:00"
if num_nodes>=46 : wall_time =  "6:00:00"
if num_nodes>=92 : wall_time = "12:00:00"
if num_nodes>=922: wall_time = "24:00:00"

#--------------------------------------------------------
# Special Cases
#--------------------------------------------------------
debug_wall_time =  "1:00:00"  # special limit for debug queue
debug_nsteps = 20              # for debug mode use steps instead of days

if debug       : resub = 0    # set resubmissions for debug mode
if debug_queue : resub = 0 

# start_date = "2000-01-01"
# if exp == "AMIP" : start_date = "1990-01-01"

### list of cases to not set surface flux averaging
flux_avg_omit_list = []

#--------------------------------------------------------
# Set the case name
#--------------------------------------------------------
if "SP" in cld : 
    crmdim = "_"+str(crm_nx)+"x"+str(crm_ny) 
    mod_str = "_{0:.2f}".format(crm_dx/1e3).rstrip('0').rstrip('.')+"km"
else : 
    crmdim = ""
    mod_str = ""

# case_name = "E3SM_"+arch+"_"+cld+"_"+exp+"_"+res+crmdim+mod_str+"_"+case_num
case_name = "E3SM_"+exp+"_"+arch+"_"+cld+"_"+res+crmdim+mod_str+"_"+case_num

#===================================================================================================
# Various settings for account / system / directories
#===================================================================================================
top_dir     = home+"/E3SM/"
srcmod_dir  = top_dir+"mod_src/"
nmlmod_dir  = top_dir+"mod_nml/"

src_dir = home+"/E3SM/E3SM_SRC_master"
if "s1"  in case_num : src_dir = home+"/E3SM/E3SM_SRC1"
if "s2"  in case_num : src_dir = home+"/E3SM/E3SM_SRC2"

scratch_dir = E3SM_common.get_scratch_dir(host,acct)
run_dir     = scratch_dir+"/"+case_name+"/run"
num_dyn     = E3SM_common.get_num_dyn(res)

### Set the physics time step
dtime = 20*60
if res=="ne120" : dtime = 6*60
ncpl  = 86400 / dtime

os.system("cd "+top_dir)
case_dir  = top_dir+"Cases/"+case_name 

print("\n  case : "+case_name+"\n")

#===================================================================================================
#===================================================================================================
# Create new case
#===================================================================================================
#===================================================================================================
case_obj = E3SM_common.Case( case_name=case_name, res=res, cld=cld, case_dir=case_dir )

compset_opt = " -compset FC5AV1C-L "

grid_opt = res+"_"+res
if "pg" in res : grid_opt = res+"_"+res
    
# if exp == "AMIP" : 
#     compset_opt = " -compset F20TRC5AV1C-L"
#     if res=="ne30" : grid_opt = "ne30_oECv3"

use_SP_compset = False
# if cld=="SP1" : compset_opt = " -compset FSP1V1 " ; use_SP_compset = True
# if cld=="SP2" : compset_opt = " -compset FSP2V1 " ; use_SP_compset = True

    
if res == "ne120" : compset_opt = " -compset FC5AV1C-H01A "

if newcase == True:
    newcase_cmd = src_dir+"/cime/scripts/create_newcase"
    cmd = newcase_cmd+" -case "+case_dir+" "+compset_opt+" -res "+grid_opt

    if host=="summit" :
        if arch=="CPU" : cmd = cmd + " -mach summit-cpu -compiler pgi    -pecount "+str(num_nodes*84)+"x1 "
        if arch=="GPU" : cmd = cmd + " -mach summit     -compiler pgigpu -pecount "+str(num_nodes*36)+"x1 "
    else:
        cmd = cmd + " -mach "+host

    print("\n"+cmd+"\n")
    os.system(cmd)


case_dir = case_dir+"/"

### set location and file name for initialization
if host=="titan" : init_dir = "/lustre/atlas/scratch/hannah6/"+acct+"/init_files/"
cami_file = "default"

#===================================================================================================
#===================================================================================================
# Configure the case
#===================================================================================================
#===================================================================================================
if config == True:
    ### set vertical levels and CRM stuff
    nlev_gcm = 72
    nlev_crm = 58
    crm_adv = "MPDATA" 
    crm_dt = 5

    crm_nx_rad = 4
    if crm_nx==256 : crm_nx_rad = 16
    if crm_nx==256 and '02' in case_num : crm_nx_rad = 4

    #------------------------------------------------
    # set CAM_CONFIG_OPTS
    #------------------------------------------------
    cam_opt = E3SM_common.get_default_config( cld, nlev_gcm, nlev_crm, crm_nx, crm_ny, crm_nx_rad, crm_dx )

    if cld=="ZM" : 
        cpp_opt = " -cppdefs ' "
    
    if "SP" in cld :
        # cpp_opt = " -cppdefs ' -DAPPLY_POST_DECK_BUGFIXES -DSP_TK_LIM  -DSP_ESMT -DSP_USE_ESMT -DSP_ORIENT_RAND "
        # cpp_opt = " -cppdefs ' -DSP_TK_LIM -DSP_ORIENT_RAND "

        cpp_opt = " -cppdefs '  "
        cpp_opt = cpp_opt + " -DSP_DIR_NS "
        cpp_opt = cpp_opt + " -DSP_MCICA_RAD "

        if exp=='ESMT-TEST': 
            cpp_opt = cpp_opt + " -DSP_ESMT -DSP_USE_ESMT "
            cpp_opt = cpp_opt + " -DSP_ESMT_PGF "

        #-------------------------------
        # Special cases
        #-------------------------------
        if case_num=='02b' : cpp_opt = cpp_opt.replace("-DSP_ORIENT_RAND","-DSP_DIR_NS")
        if case_num=='02c' : cpp_opt = cpp_opt.replace("-DSP_ORIENT_RAND","")
        if case_num=='02d' : cpp_opt = cpp_opt + " -DSP_ORIENT_RAND_LIMIT "
        if case_num=='02e' : cpp_opt = cpp_opt.replace("-DSP_ORIENT_RAND","-DSP_ORIENT_FLIPFLOP")
        
        # if case_num == 's1_61' : cpp_opt = cpp_opt+" -DSP_ESMT -DSP_USE_ESMT -DSP_ESMT_PGF "
        # if case_num == '00b' : cpp_opt = cpp_opt+" -DSP_ALT_PERTURBATION "

    ### Switch to RRMTGP
    # cam_opt = cam_opt.replace("-rad rrtmg","-rad rrtmgp")

    if host=="summit" and arch=="GPU" : cam_opt = cam_opt + " -pcols 256 "

    cam_opt = cam_opt+cpp_opt+" ' "

    if cld=="ZM" or ( "SP" in cld and not use_SP_compset ) : 
        case_obj.xmlchange("env_build.xml", "CAM_CONFIG_OPTS", "\""+cam_opt+"\"" )

    #------------------------------------------------
    #------------------------------------------------
    ### update cami file if not equal to "default"
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
    ### set run-time variables
    # case_obj.xmlchange("env_run.xml", "RUN_STARTDATE", start_date ) 
    if host=="titan" and acct=="cli115" : 
        case_obj.xmlchange("env_run.xml", "RUNDIR", "/lustre/atlas1/cli115/scratch/hannah6/"+case_name+"/run" )
    if host=="summit" : 
        tdir = "/gpfs/alpine/scratch/hannah6/cli115/"
        case_obj.xmlchange("env_run.xml", "RUNDIR", tdir+case_name+"/run" )
        # case_obj.xmlchange("env_build.xml", "CIME_OUTPUT_ROOT", tdir )
        
    ### change use-case for CAMRT
    if " camrt " in cam_opt : case_obj.xmlchange("env_run.xml", "CAM_NML_USE_CASE", " 2000_cam5_av1c-SP1_no-linoz " )

    ### Set the timestep
    case_obj.xmlchange("env_run.xml", "ATM_NCPL", ncpl )

    ### set CUDA memcheck
    if use_memcheck: case_obj.xmlchange("env_mach_specific.xml", "run_exe", "\"cuda-memcheck \$EXEROOT/e3sm.exe\"" )

    ### configure the case
    case_obj.setup(clean)
    
#===================================================================================================
#===================================================================================================
# Build the model
#===================================================================================================
#===================================================================================================
if build == True:
    if host=="titan" and acct=="cli115" : 
        case_obj.xmlchange("env_build.xml", "CIME_OUTPUT_ROOT", "/lustre/atlas1/cli115/scratch/hannah6/" )
    case_obj.set_debug_mode(debug)
    case_obj.build(clean)

#===================================================================================================
# Write the custom namelist options
#===================================================================================================
if mk_nml :

    cam_config_opts = case_obj.xmlquery("CAM_CONFIG_OPTS")
    compset         = case_obj.xmlquery("COMPSET")
    din_loc_root    = case_obj.xmlquery("DIN_LOC_ROOT")

    ### remove extra spaces to simplify string query
    cam_config_opts = ' '.join(cam_config_opts.split())

    nfile = case_dir+"user_nl_cam"
    file = open(nfile,'w') 

    #------------------------------
    # Special test mode 
    #------------------------------
    if test_run :
        # file.write(" nhtfrq    = 0,-1 \n") 
        # file.write(" mfilt     = 1,24 \n")  

        if "02" in case_num :
            nday_hist = 5
            if "SP_ORIENT_RAND" in cam_config_opts :
                file.write(" nhtfrq    = 0,-3,1 \n") 
                file.write(" mfilt     = 1,"+str(8*nday_hist)+","+str(ncpl*nday_hist)+" \n")  
            else:
                file.write(" nhtfrq    = 0,-3 \n") 
                file.write(" mfilt     = 1,"+str(8*nday_hist)+" \n")  


        file.write(" fincl2    = 'PS','TS'")
        file.write(             ",'PRECT','TMQ'")
        file.write(             ",'T','Q','Z3' ")           # full 3d thermodynamic fields
        file.write(             ",'OMEGA','U','V' ")        # full 3d momentum fields
        file.write(             ",'QRL','QRS'")             # full 3d radiative heating profiles
        file.write(             ",'FSNT','FLNT'")           # Net TOM heating rates
        file.write(             ",'FLNS','FSNS'")           # Surface rad for total column heating
        file.write(             ",'FSNTC','FLNTC'")         # clear sky heating rates for CRE
        file.write(             ",'LHFLX','SHFLX'")         # surface fluxes
        # file.write(             ",'TAUX','TAUY'")           # surface stress
        # file.write(             ",'LWCF','SWCF'")           # cloud radiative foricng
        # file.write(             ",'UBOT','VBOT','QBOT','TBOT'")
        # file.write(             ",'U850','U200','V850','V200','OMEGA500' ")
        file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT' ")
        file.write(             ",'CLOUD','CLDLIQ','CLDICE' ")
        # file.write(             ",'UAP','VAP','QAP','QBP','TAP','TBP','TFIX'")
        # file.write(             ",'QEXCESS' ")
        # file.write(             ",'PTTEND' ")
        # if "chem none" not in cam_config_opts :
        #     file.write(         ",'AEROD_v','EXTINCT'")         # surface fluxes
        # if "SP" in cld :
            # file.write(             ",'SPDT','SPDQ' ")
            # file.write(             ",'SPTLS','SPQTLS' ")
            # file.write(             ",'CRM_T','CRM_QV','CRM_QC','CRM_QPC','CRM_PREC' ")
            # file.write(             ",'SPQTFLX','SPQTFLXS'")
            # file.write(             ",'SPQPEVP','SPMC' ")
            # file.write(             ",'SPMCUP','SPMCDN','SPMCUUP','SPMCUDN' ")
            # file.write(             ",'SPQC','SPQR' ")
            # file.write(             ",'SPQI','SPQS','SPQG' ")
            # file.write(             ",'SPTK','SPTKE','SPTKES' ")

        if "02" in case_num :
            if "SP_ORIENT_RAND" in cam_config_opts :
                file.write(           ",'CRM_ANGLE' ")

        file.write("\n")

        if "02" in case_num :
            if "SP_ORIENT_RAND" in cam_config_opts :
                file.write(" fincl3    = 'CRM_ANGLE','PRECT' \n ")

    #------------------------------
    # Default output
    #------------------------------
    else :
        file.write(" nhtfrq    = 0,-6,-1 \n") 
        file.write(" mfilt     = 1, 4, 120 \n")     # h2 = 1 hourly for 5 days
        # file.write(" nhtfrq    = 0,-6,-3 \n") 
        # file.write(" mfilt     = 1, 4, 80 \n")      # h2 = 3 hourly for 5 days 
        file.write(" fincl2    = 'PS','TS'")
        file.write(             ",'T','Q','Z3' ")               # thermodynamic budget components
        file.write(             ",'U','V','OMEGA'")             # velocity components
        file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
        file.write(             ",'QRL','QRS'")                 # Full radiative heating profiles
        file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
        file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
        file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
        file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
        # file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
        file.write(             ",'TAUX','TAUY'")               # surface stress
        if "SP" in cld :
            file.write(         ",'SPDT','SPDQ'")               # CRM heating/moistening tendencies
            file.write(         ",'SPTLS','SPQTLS' ")           # CRM large-scale forcing
            file.write(         ",'SPQPEVP','SPMC'")            # CRM rain evap and total mass flux
            file.write(         ",'SPMCUP','SPMCDN'")           # CRM saturated mass fluxes
            file.write(         ",'SPMCUUP','SPMCUDN'")         # CRM unsaturated mass fluxes
            # if any(x in cam_config_opts for x in ["SP_ESMT","SP_USE_ESMT","SPMOMTRANS"]) : 
            #     file.write(",'ZMMTU','ZMMTV','uten_Cu','vten_Cu' ")
            # if "SP_USE_ESMT" in cam_config_opts : file.write(",'U_ESMT','V_ESMT'")
            # if "SPMOMTRANS"  in cam_config_opts : file.write(",'UCONVMOM','VCONVMOM'")
        file.write("\n")
        file.write(" fincl3    = 'PRECT','TMQ' ")
        file.write(            ",'LHFLX','SHFLX'")
        file.write("\n")
    #------------------------------
    #------------------------------

    if cami_file != "default" : file.write(" ncdata  = '"+init_dir+cami_file+"' \n")         
    
    
    file.write(" srf_flux_avg = 1 \n")

    # crm mean-state acceleration
    # file.write(" crm_accel_factor = 4.     \n")
    file.write(" use_crm_accel    = .false. \n")
    file.write(" crm_accel_uv     = .false. \n")

    # if not flux_avg_omit_list :
    #     file.write(" srf_flux_avg = 1 \n")
    # else :
    #     if any(x in case_num for x in flux_avg_omit_list) :
    #         file.write(" srf_flux_avg = 0 \n")
    #     else :
    #         file.write(" srf_flux_avg = 1 \n")

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

    if res == "ne120" : file.write(" cld_macmic_num_steps = 3 \n") 

    #------------------------------
    # Dycore tuning parameters
    #------------------------------
    
    ### default values
    # qsplit            = 1 
    rsplit            = 3 
    se_nsplit         = 2
    # hypervis_subcycle   = 3
    # hypervis_subcycle_q = 1

    ### special cases
    if res == "ne30" :
        if dtime <= 20*60 : se_nsplit,rsplit = 2,2
        if dtime <= 10*60 : se_nsplit,rsplit = 2,1
        if dtime <=  5*60 : se_nsplit,rsplit = 1,1

    if res == "ne120" :
        if dtime <= 10*60 : se_nsplit,rsplit = 2,2
        if dtime <=  5*60 : se_nsplit,rsplit = 2,1

    if inc_remap : se_nsplit = se_nsplit*2

    # file.write(" qsplit    = "+str(   qsplit)+" \n") 
    file.write(" rsplit    = "+str(   rsplit)+" \n") 
    file.write(" se_nsplit = "+str(se_nsplit)+" \n")
    # if res != "ne120" : 
    #     file.write(" hypervis_subcycle = "+str(hypervis_subcycle)+" \n") 

    #------------------------------
    # state_debug_checks
    #------------------------------
    if debug_chks :
        file.write(" state_debug_checks = .true. \n")
    else :
        file.write(" state_debug_checks = .false. \n")

    #------------------------------
    # Close user_nl_cam
    #------------------------------
    file.close() 

    #------------------------------
    # Land model namelist
    #------------------------------
    # if test_run :
    #     nfile = case_dir+"user_nl_clm"
    #     file = open(nfile,'w') 
    #     file.write(" hist_nhtfrq = 0,-1 \n")
    #     file.write(" hist_mfilt  = 1,24 \n")
    #     file.write(" hist_mfilt  = 1,"+str(ncpl)+" \n")
    #     file.write(" hist_fincl2 = 'TBOT','QTOPSOIL','RH','RAIN'")
    #     file.write(              ",'FGEV','FCEV','FCTR','Rnet'")
    #     file.write(              ",'FSH_V','FSH_G','TLAI','ZWT','ZWT_PERCH'")
    #     file.write(              ",'QSOIL','QVEGT','QCHARGE'")
    #     file.write("\n")
    #     file.close()

    ### new land initial condition file (not in inputdata yet)    
    nfile = case_dir+"user_nl_clm"
    file = open(nfile,'w') 
    if res=="ne30" : file.write(" finidat = '/gpfs/alpine/scratch/hannah6/cli115/init_files/clmi.ICLM45BC.ne30_ne30.d0241119c.clm2.r.nc' \n")
    ### This causes error - 1D variable eflx_dynbal_amt_to_dribblewith unknown subgrid dimension - clm/src/main/initInterp.F90 at line 392
    # file.write(" finidat_interp_source = '/gpfs/alpine/scratch/hannah6/cli115/init_files/clmi.ICLM45BC.ne30_ne30.d0241119c.clm2.r.nc' \n")
    file.close()

    #------------------------------
    # Turn off CICE history files
    #------------------------------
    nfile = case_dir+"user_nl_cice"
    file = open(nfile,'w') 
    file.write(" histfreq = 'x','x','x','x','x' \n")
    file.close()

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
    # if exp == "AMIP" : 
    #     nfile = case_dir+"user_nl_clm"
    #     file = open(nfile,'w') 
    #     file.write(" finidat             = '/lustre/atlas1/cli900/world-shared/cesm/inputdata/lnd/clm2/initdata_map/I1850CLM45.ne30_oECv3.edison.intel.36b43c9.clm2.r.0001-01-06-00000_c20171023.nc' \n")
    #     file.write(" flanduse_timeseries = '/lustre/atlas1/cli900/world-shared/cesm/inputdata/lnd/clm2/surfdata_map/landuse.timeseries_ne30np4_hist_simyr1850_c20171102.nc' \n")
    #     file.write(" fsurdat             = '/lustre/atlas1/cli900/world-shared/cesm/inputdata/lnd/clm2/surfdata_map/surfdata_ne30np4_simyr1850_2015_c171018.nc' \n")
    #     file.write(" check_finidat_year_consistency = .false. \n")
    #     file.close()

#===================================================================================================
#===================================================================================================
# Run the simulation
#===================================================================================================
#===================================================================================================
if runsim == True:

    # if acct=="cli115" : case_obj.xmlchange("env_batch.xml", "CHARGE_ACCOUNT", "\"CLI115\"" )

    runfile = case_dir+"case.run"
    subfile = case_dir+"case.submit"

    ### CIME updates changed the run file name - prependend a "."
    if not os.path.isfile(runfile) : runfile = case_dir+".case.run"

    #------------------------------
    # Change run options
    #------------------------------
    if continue_run:
        case_obj.xmlchange("env_run.xml", "CONTINUE_RUN", "TRUE" )
    else:
        case_obj.xmlchange("env_run.xml", "CONTINUE_RUN", "FALSE" )
    case_obj.xmlchange("env_run.xml", "STOP_OPTION" , "ndays" )
    case_obj.xmlchange("env_run.xml", "STOP_N"      , ndays )
    case_obj.xmlchange("env_run.xml", "RESUBMIT"    , resub )

    if debug or debug_queue :
        case_obj.xmlchange("env_run.xml", "STOP_OPTION" , "nsteps" )
        case_obj.xmlchange("env_run.xml", "STOP_N"      , debug_nsteps )

    ### disable restart files for ne120
    if res=="ne120" : case_obj.xmlchange("env_run.xml", "REST_OPTION", "never" )

    #------------------------------
    # Change the BFB flag for certain runs
    #------------------------------
    if disable_bfb : 
        case_obj.xmlchange("env_run.xml", "BFBFLAG", "FALSE" )
    else :
        case_obj.xmlchange("env_run.xml", "BFBFLAG", "TRUE" )

    #------------------------------
    # switch to debug queue if it is clear
    #------------------------------    
    case_obj.xmlchange("env_batch.xml", "JOB_QUEUE", "batch" )

    if debug_queue and host=="titan" :
        ### get user name
        user = subprocess.check_output(["whoami"],universal_newlines=True).strip()
        ### get data on all jobs 
        out = subprocess.check_output(['qstat','-f'],universal_newlines=True)
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
            case_obj.xmlchange("env_batch.xml", "JOB_QUEUE", "debug" )
            wall_time = debug_wall_time

    #------------------------------
    # DEBUG LEVEL
    #------------------------------
    if debug :
        ### level of debug output, 0=minimum, 1=normal, 2=more, 3=too much
        case_obj.xmlchange("env_run.xml", "INFO_DBUG", 2 )

        ### for debug mode, make sure the core will be dumped to file in the event of a seg fault
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

        ### Make sure that there is not old core file because it won't get overwritten
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
    case_obj.xmlchange("env_batch.xml", "JOB_WALLCLOCK_TIME", wall_time )

    #------------------------------
    # Submit the run
    #------------------------------
    case_obj.submit()
    

print("\n  case : "+case_name+"\n")

#===================================================================================================
#===================================================================================================
#===================================================================================================
#===================================================================================================
