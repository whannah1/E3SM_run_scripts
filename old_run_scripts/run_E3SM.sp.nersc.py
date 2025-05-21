#!/usr/bin/env python2
#===============================================================================================================================================================
#  Jan, 2018 - Walter Hannah - Lawrence Livermore National Lab
#  This script runs atmosphere only simulations of E3SM
#===============================================================================================================================================================
import sys
import os
import fileinput
import subprocess
import run_E3SM_common as E3SM_common

home = E3SM_common.get_home_dir()
host = E3SM_common.get_host_name()
acct = E3SM_common.get_host_acct(host)

newcase,config,build,runsim,continue_run,clean,mk_nml,copyinit,use_GNU,use_intel,drop_opt,lower_dt = False,False,False,False,False,False,False,False,False,False,False,False
debug,debug_w_opt,debug_log,debug_ddt,test_run,debug_queue,inc_remap,debug_chks,disable_bfb = False,False,False,False,False,False,False,False,False
#===============================================================================================================================================================
#===============================================================================================================================================================

# clean        = True
newcase      = True
config       = True
build        = True
mk_nml       = True
runsim       = True
# continue_run = True

# use_GNU     = True       # use the GNU compiler   (overrides the default)
# use_intel   = True       # use the intel compiler (overrides the default)
# copyinit    = True       # copy new initialization files for branch run
test_run    = True       # special output mode 
# debug       = True       # enable debug mode
# debug_w_opt = True       # enable debug mode - retain O2 optimization - use with debug = True
debug_queue = True       # use debug queue + use debug_nsteps
# debug_log   = True       # enable debug output in log files (adds WH_DEBUG flag)
# debug_ddt   = True       # also change ntask for running DDT - only works with debug 
# drop_opt    = True       # Reduce optimization in Macros file                 requires rebuild
# lower_dt    = True       # Reduce timestep by half (from 30 to 15 minutes)    requires re-config

# debug_chks  = True       # enable state_debug_checks (namelist)
# inc_remap   = True       # Increase vertical remap parameter to reduce timestep via atm namelist
# disable_bfb = True       # Use this to get past a random crash (slightly alters the weather of the restart)

#--------------------------------------------------------
#--------------------------------------------------------
# case_num = '00'     # control - all current defaults  

### SRC1 runs
# case_num = 's1_00'    # 

### SRC2 runs 
case_num = 's2_00'   # 
# case_num = 's2_01'   # SP pg2 tests - map only T as tendency
# case_num = 's2_02'   # SP pg2 tests - map only Q as tendency

# case_num = 's2_50'   # SP_ALT_TPHYSBC
# case_num = 's2_51'   # SP_ALT_TPHYSBC + DIFFUSE_PHYS_TEND
# case_num = 's2_51a'   # SP_ALT_TPHYSBC + DIFFUSE_PHYS_TEND + SP_DUMMY_HYPERVIS_T + SP_DUMMY_HYPERVIS_T
# case_num = 's2_51b'   # SP_ALT_TPHYSBC + DIFFUSE_PHYS_TEND + SP_DUMMY_HYPERVIS_T + SP_DUMMY_HYPERVIS_Q
# case_num = 's2_52'   # SP_ALT_TPHYSBC + DIFFUSE_PHYS_TEND + PHYS_HYPERVIS_FACTOR_5X5

#--------------------------------------------------------
#--------------------------------------------------------
cld = 'SP1'    # ZM / SP1 / SP2 / SP2+ECPP
exp = 'ESMT-TEST'    # CTL / EXP / AMIP / BRANCH / TEST / AQP[1-10]
# exp = 'TEST'

ne,npg = 4,0

# if 'ZM' in cld : ndays,resub = (73*2),1 #(5)       # 5=2yr, 15=6yr, 25=10yr
# if 'SP' in cld and res=='ne30' : ndays,resub,wall_time = 5,0,'4:00:00'
if 'ZM' in cld : ndays,resub,wall_time = 32,0,'2:00:00'
if 'SP' in cld : ndays,resub,wall_time = 10,0,'4:00:00'

crm_nx,crm_ny,crm_dx = 64,1,1000


#--------------------------------------------------------
# Special Cases
#--------------------------------------------------------
debug_wall_time =  '0:30:00'        # special limit for debug queue
debug_nsteps = 72                  # for debug mode use steps instead of days

if debug : resub = 0    # set resubmissions for debug mode


start_date = '2000-01-01'
if exp == 'AMIP' : start_date = '1990-01-01'

### list of cases to not set surface flux averaging
flux_avg_omit_list = []             

#--------------------------------------------------------
# Set the case name
#--------------------------------------------------------
res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)

crmdim = ''
if 'SP' in cld : crmdim = '_'+str(crm_nx)+'x'+str(crm_ny)+'_{0:}km'.format((crm_dx/1e3))
    
case_name = 'E3SM_'+cld+'_'+exp+'_'+res+crmdim+'_'+case_num


#===============================================================================================================================================================
# Various settings for account / system / directories
#===============================================================================================================================================================
top_dir     = home+'/E3SM/'

src_dir = home+'/E3SM/E3SM_SRC_master'
if 's1'  in case_num : src_dir = home+'/E3SM/E3SM_SRC1'
if 's2'  in case_num : src_dir = home+'/E3SM/E3SM_SRC2'

scratch_dir = E3SM_common.get_scratch_dir(host,acct)

run_dir = scratch_dir+'/'+case_name+'/run'

num_dyn = E3SM_common.get_num_dyn(res)

dtime = 20*60

if lower_dt : dtime = dtime/2

ncpl  = 86400 / dtime

os.system('cd '+top_dir)
case_dir  = top_dir+'Cases/'+case_name 
cdcmd = 'cd '+case_dir+' ; '

print('\n  case : '+case_name+'\n')
#===============================================================================================================================================================
#===============================================================================================================================================================
# Create new case
#===============================================================================================================================================================
#===============================================================================================================================================================

case_obj = E3SM_common.Case( case_name=case_name, res=res, cld=cld, case_dir=case_dir )

compset_opt = " -compset FC5AV1C-L "

if 'AQP' in exp : compset_opt = " -compset F-EAMv1-"+exp+" "

grid_opt = res+"_"+res

if exp == "AMIP" : 
    compset_opt = " -compset F20TRC5AV1C-L"
    if res=="ne30" : grid_opt = "ne30_oECv3"

use_SP_compset = False
# if cld=="SP1" : compset_opt = " -compset FSP1V1 " ; use_SP_compset = True
# if cld=="SP2" : compset_opt = " -compset FSP2V1 " ; use_SP_compset = True

if exp == "CPL" :
    if cld=="SP1" : compset_opt = " -compset A_WCYCL1850S_SP1 " # Fully coupled
    use_SP_compset = True

if "A_WCYCL" in compset_opt : grid_opt = res+"_oECv3_ICG"
    
if res == "ne120" : compset_opt = " -compset FC5AV1C-H01A "

if newcase == True:
    newcase_cmd = src_dir+"/cime/scripts/create_newcase"
    cmd = newcase_cmd+" -case "+case_dir+" "+compset_opt+" -res "+grid_opt+" -mach  "+host
    if use_GNU   : cmd = cmd + " -compiler gnu "
    if use_intel : cmd = cmd + " -compiler intel "
    print("\n"+cmd+"\n")
    os.system(cmd)


case_dir = case_dir+"/"


### set location and file name for initialization
cami_file = "default"
init_dir = "/global/cscratch1/sd/whannah/acme_scratch/init_files/"

#===============================================================================================================================================================
#===============================================================================================================================================================
# Configure the case
#===============================================================================================================================================================
#===============================================================================================================================================================
if config == True:
    #------------------------------------------------
    # set CAM_CONFIG_OPTS
    #------------------------------------------------
    crm_nx_rad = crm_nx/4

    cam_opt = E3SM_common.get_default_config( cld=cld, crm_nx=crm_nx, crm_ny=crm_ny, \
                                              crm_dx=crm_dx, crm_nx_rad=crm_nx_rad )

    # if cld=='ZM' : 
    #     cpp_opt = ' -cppdefs \' '
    
    if 'SP' in cld :
        cpp_opt = ' -cppdefs \' -DSP_DIR_NS -DSP_MCICA_RAD '
        # cpp_opt = ' -cppdefs ' -DAPPLY_POST_DECK_BUGFIXES -DSP_TK_LIM  '
        # cpp_opt = cpp_opt+' -DSP_ESMT -DSP_USE_ESMT  '
        # cpp_opt = cpp_opt+' -DSP_ORIENT_RAND '
        
        #-------------------------------
        # Special cases
        #-------------------------------

        # if case_num=='03' : cpp_opt = cpp_opt+' -DSP_USE_DIFF '   # enable normal GCM thermodynamic diffusion
        
        if 'ESMT-TEST' in exp : 
            cpp_opt = cpp_opt+' -DSP_ESMT '
            if '-FB' in exp : cpp_opt = cpp_opt+' -DSP_USE_ESMT '
            if '-PG' in exp : cpp_opt = cpp_opt+' -DSP_ESMT_PGF '
            # cpp_opt = cpp_opt+' -DSPMOMTRANS '
        
        # if case_num == '' : cpp_opt = cpp_opt+' -DSP_ESMT -DSP_USE_ESMT -DSP_ESMT_PGF '

        if case_num in ['s2_50']  : cpp_opt = cpp_opt+' -DSP_ALT_TPHYSBC '
        if case_num in ['s2_51']  : cpp_opt = cpp_opt+' -DSP_ALT_TPHYSBC -DDIFFUSE_PHYS_TEND '
        if case_num in ['s2_51a'] : cpp_opt = cpp_opt+' -DSP_ALT_TPHYSBC -DDIFFUSE_PHYS_TEND -DSP_DUMMY_HYPERVIS -DSP_DUMMY_HYPERVIS_T '
        if case_num in ['s2_51b'] : cpp_opt = cpp_opt+' -DSP_ALT_TPHYSBC -DDIFFUSE_PHYS_TEND -DSP_DUMMY_HYPERVIS -DSP_DUMMY_HYPERVIS_Q '
        if case_num in ['s2_52']  : cpp_opt = cpp_opt+' -DSP_ALT_TPHYSBC -DDIFFUSE_PHYS_TEND -DPHYS_HYPERVIS_FACTOR_5X5 '
        #-------------------------------
        #-------------------------------

    if 'SP' in cld : cam_opt = cam_opt+cpp_opt+' \' '

    if 'AQP' in exp : cam_opt = cam_opt+' -aquaplanet '


    if cld=='ZM' or ( 'SP' in cld and not use_SP_compset ) : 
        case_obj.xmlchange('env_build.xml', 'CAM_CONFIG_OPTS', '\"'+cam_opt+'\"' )

    #------------------------------------------------
    # update cami file if not equal to 'default'
    #------------------------------------------------
    if cami_file != 'default' :
        ### copy file to scratch
        CMD = 'cp ~/E3SM/init_files/'+cami_file+' '+init_dir
        print(CMD)
        os.system(CMD)
        ### write file path to namelist
        nfile = case_dir+'user_nl_cam'
        file = open(nfile,'w')
        file.write(' ncdata  = ''+init_dir+cami_file+'' \n ') 
        file.close() 
    #------------------------------------------------
    # set run-time variables
    #------------------------------------------------    
    case_obj.xmlchange('env_run.xml', 'RUN_STARTDATE', start_date ) 
    
    ### change use-case for CAMRT
    if ' camrt ' in cam_opt : case_obj.xmlchange('env_run.xml', 'CAM_NML_USE_CASE', ' 2000_cam5_av1c-SP1_no-linoz ' )

    #------------------------------------------------
    # Change processor count
    #------------------------------------------------
    if 'cori' in host :
        ### Don't explicitly set NTASKS for other components on cori
        case_obj.xmlchange('env_mach_pes.xml', 'NTASKS_ATM',  num_dyn )

    # if debug and debug_ddt :
    #     if res=='ne30' : case_obj.set_NTASKS_all(480)
    
    ### Make sure threading is off for SP
    if 'SP' in cld : case_obj.set_NTHRDS_all(1)
    #------------------------------------------------
    # Set the timestep
    #------------------------------------------------
    case_obj.xmlchange('env_run.xml', 'ATM_NCPL', ncpl )

    #------------------------------------------------
    # for GNU set COMPILER before configure so that Macros file has correct flags
    #------------------------------------------------
    if use_intel : case_obj.xmlchange('env_build.xml', 'COMPILER',   '\'intel\'' )
    if use_GNU   : case_obj.xmlchange('env_build.xml', 'COMPILER',   '\'gnu\'' )
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
    #----------------------------------------------------------
    #----------------------------------------------------------
    if use_GNU   : case_obj.xmlchange("env_build.xml", "COMPILER", " \"gnu\" " )
    if use_intel : case_obj.xmlchange("env_build.xml", "COMPILER", " \"intel\" " )

    case_obj.set_debug_mode(debug)
    case_obj.build(clean)

#=================================================================================================================================
# Write the custom namelist options
#=================================================================================================================================
if mk_nml :

    (cam_config_opts, err) = subprocess.Popen(cdcmd+"./xmlquery CAM_CONFIG_OPTS -value", stdout=subprocess.PIPE, shell=True).communicate()
    (compset        , err) = subprocess.Popen(cdcmd+"./xmlquery COMPSET         -value", stdout=subprocess.PIPE, shell=True).communicate()
    (din_loc_root   , err) = subprocess.Popen(cdcmd+"./xmlquery DIN_LOC_ROOT    -value", stdout=subprocess.PIPE, shell=True).communicate()

    # (cam_config_opts, err) = case_obj.xmlquery_value("CAM_CONFIG_OPTS")
    # (compset        , err) = case_obj.xmlquery_value("COMPSET")
    # (din_loc_root   , err) = case_obj.xmlquery_value("DIN_LOC_ROOT")

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
        # file.write(             ",'CLOUD','CLDLIQ','CLDICE' ")
        # file.write(             ",'UAP','VAP','QAP','QBP','TAP','TBP'")
        # file.write(             ",'QEXCESS' ")
        # file.write(             ",'PTTEND' ")
        # if npg>0 : file.write(   ",'DYN_OMEGA','DYN_T','DYN_Q','DYN_PS'")
        # if "chem none" not in cam_config_opts :
        #     file.write(         ",'AEROD_v','EXTINCT'")         # aerosol optical depth and extinction
        if "SP" in cld :
            # if 's2' in case_num : 
            #     file.write(         ",'SPTA','SPQV'")               # CRM mean Tabs and qv
            file.write(             ",'SPDT','SPDT' ")
            file.write(             ",'SPTLS','SPQTLS' ")
            # file.write(             ",'CRM_T','CRM_QV','CRM_QC','CRM_QPC','CRM_PREC' ")
            # file.write(             ",'SPQTFLX','SPQTFLXS'")
            # file.write(             ",'SPQPEVP','SPMC' ")
            # file.write(             ",'SPMCUP','SPMCDN','SPMCUUP','SPMCUDN' ")
            # file.write(             ",'SPQC','SPQR' ")
            # file.write(             ",'SPQI','SPQS','SPQG' ")
            # file.write(             ",'SPTK','SPTKE','SPTKES' ")
        file.write("\n")

    #------------------------------
    # Default output
    #------------------------------
    else :
        file.write(" nhtfrq    = 0,-3 \n") 
        file.write(" mfilt     = 1,80 \n")     
        # file.write(" nhtfrq    = 0,-6,-3 \n") 
        # file.write(" mfilt     = 1, 4, 80 \n")      # h2 = 3 hourly for 5 days 
        file.write(" fincl2    = 'PS','TS'")
        file.write(             ",'PRECT','TMQ'")
        file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
        file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
        file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
        file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
        file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
        file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT' ")
        # file.write(             ",'TAUX','TAUY'")               # surface stress
        file.write(             ",'T','Q','Z3' ")               # 3D thermodynamic budget components
        file.write(             ",'U','V','OMEGA'")             # 3D velocity components
        file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
        # file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
        if npg>0 : file.write(   ",'DYN_OMEGA'")
        # if "SP" in cld :
            # if 's2' in case_num : 
            #     file.write(     ",'SPTA','SPQV'")               # CRM mean Tabs and qv
            # file.write(         ",'SPDT','SPDQ'")               # CRM heating/moistening tendencies
            # file.write(         ",'SPTLS','SPQTLS' ")           # CRM large-scale forcing
            # file.write(         ",'SPQPEVP','SPMC'")            # CRM rain evap and total mass flux
            # file.write(         ",'SPMCUP','SPMCDN'")           # CRM saturated mass fluxes
            # file.write(         ",'SPMCUUP','SPMCUDN'")         # CRM unsaturated mass fluxes
            # if any(x in cam_config_opts for x in ["SP_ESMT","SP_USE_ESMT","SPMOMTRANS"]) : 
            #     file.write(",'ZMMTU','ZMMTV','uten_Cu','vten_Cu' ")
            # if "SP_USE_ESMT" in cam_config_opts : file.write(",'U_ESMT','V_ESMT'")
            # if "SPMOMTRANS"  in cam_config_opts : file.write(",'UCONVMOM','VCONVMOM'")
        file.write("\n")
        # file.write(" fincl3    = 'PRECT','TMQ' ")
        # file.write(            ",'LHFLX','SHFLX'")
        # file.write("\n")
    #------------------------------
    #------------------------------
    file.write(" dyn_npes = "+str(num_dyn)+" \n")
    # if npg>0: file.write(" se_ftype = 0 \n")
    # if npg>0: file.write(" phys_loadbalance = -1 ")

    if cami_file != "default" : file.write(" ncdata  = '"+init_dir+cami_file+"' \n") 

    if res == "ne120" : file.write(" cld_macmic_num_steps = 3 \n") 

    # if "pg1" in res : file.write(" bnd_topo   = '"+init_dir+topo_file+"' \n")

    #------------------------------
    # Sfc flux smoothing
    #------------------------------
    # if not flux_avg_omit_list :
    #     file.write(" srf_flux_avg = 1 \n")
    # else :
    #     if any(x in case_num for x in flux_avg_omit_list) :
    #         file.write(" srf_flux_avg = 0 \n")
    #     else :
    #         file.write(" srf_flux_avg = 1 \n")

    #------------------------------
    # Prescribed aerosol settings
    #------------------------------
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
    # qsplit              = 1 
    rsplit              = 3 
    se_nsplit           = 2
    hypervis_subcycle   = 3
    # hypervis_subcycle_q = 1

    if dtime == (20*60) : rsplit = 2

    if inc_remap : se_nsplit = se_nsplit*2

    ### special cases

    # file.write(" qsplit    = "+str(   qsplit)+" \n") 
    file.write(" rsplit    = "+str(   rsplit)+" \n") 
    file.write(" se_nsplit = "+str(se_nsplit)+" \n")
    if res != "ne120" : 
        file.write(" hypervis_subcycle = "+str(hypervis_subcycle)+" \n") 

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
    #------------------------------
    # Turn off CICE history files
    #------------------------------
    nfile = case_dir+"user_nl_cice"
    file = open(nfile,'w') 
    file.write(" histfreq = 'x','x','x','x','x' \n")
    file.close()


#===============================================================================================================================================================
#===============================================================================================================================================================
# Run the simulation
#===============================================================================================================================================================
#===============================================================================================================================================================
if runsim == True:

    runfile = case_dir+"case.run"
    subfile = case_dir+"case.submit"

    ### CIME updates changed the run file name - prependend a "."
    if not os.path.isfile(runfile) : runfile = case_dir+".case.run"

    #------------------------------
    # Change run options
    #------------------------------
    if continue_run : 
        case_obj.xmlchange('env_run.xml', 'CONTINUE_RUN', 'TRUE' )
    else:
        case_obj.xmlchange('env_run.xml', 'CONTINUE_RUN', 'FALSE' )

    case_obj.xmlchange('env_run.xml', 'STOP_OPTION' , 'ndays' )
    case_obj.xmlchange('env_run.xml', 'STOP_N'      , ndays )
    case_obj.xmlchange('env_run.xml', 'RESUBMIT'    , resub )

    if debug or debug_queue :
        case_obj.xmlchange('env_run.xml', 'STOP_OPTION' , 'nsteps' )
        case_obj.xmlchange('env_run.xml', 'STOP_N'      , debug_nsteps )

    ### disable restart files for ne120
    if res=='ne120' : case_obj.xmlchange('env_run.xml', 'REST_OPTION', 'never' )

    ### Change the BFB flag for certain runs
    if disable_bfb : 
        case_obj.xmlchange('env_run.xml', 'BFBFLAG', 'FALSE' )
    else :
        case_obj.xmlchange('env_run.xml', 'BFBFLAG', 'TRUE' )

    #------------------------------
    # Queue and batch settings
    #------------------------------        

    ### switch to debug queue if it is clear
    if debug_queue :
        case_obj.xmlchange("env_batch.xml", "JOB_QUEUE", "debug" )
        wall_time = debug_wall_time
    else :
        case_obj.xmlchange("env_batch.xml", "JOB_QUEUE", "regular" )

    ### set the wall clock limit
    case_obj.xmlchange("env_batch.xml", "JOB_WALLCLOCK_TIME", wall_time )

    #------------------------------
    # DEBUG LEVEL
    #------------------------------
    if debug :
        ### level of debug output, 0=minimum, 1=normal, 2=more, 3=too much
        case_obj.xmlchange("env_run.xml", "INFO_DBUG", 2 )

        ### for debug mode, make sure the core will be dumped to file in the event of a seg fault
        # case_obj.enable_core_dump()

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

    #------------------------------
    # Submit the run
    #------------------------------
    os.system(cdcmd+subfile)
    

print("\n  case : "+case_name+"\n")

#===============================================================================================================================================================
#===============================================================================================================================================================
#===============================================================================================================================================================
#===============================================================================================================================================================