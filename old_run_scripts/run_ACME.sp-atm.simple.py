#!/usr/bin/env python
#===============================================================================================================================================================
#   This script runs atmosphere only simulations of ACME
#
#    Jan, 2017  Walter Hannah       Lawrence Livermore National Lab
#
#===============================================================================================================================================================
import sys
import os
# import numpy as np
home = os.getenv("HOME")
host = os.getenv("HOST")

if "edison" in host : host = "edison"
if "blogin" in host : host = "anvil"
if "titan"  in host : host = "titan"

#===============================================================================================================================================================
#===============================================================================================================================================================
newcase,config,build,copyinit,mk_nml,runsim,debug,clean,test_run,use_GNU = False,False,False,False,False,False,False,False,False

newcase  = True
# clean    = True
config   = True 
build    = True
mk_nml   = True
runsim   = True

# debug    = True       # enable the ACME's debug mode
# copyinit = True       # only for branch runs
# test_run = True       # special run mode - run a 5 time steps and output every timestep (see below)


case_num = "00"


# wall_time =  "1:00:00"
wall_time =  "2:00:00"


cld = "SP1"    # ZM / SP1 / SP2
exp = "CTL"    # CTL / EXP
res = "ne30"   # ne30 / ne16

cflag = "FALSE"                      # Continue flag - Don't forget to set this!!!! 
# cflag = "TRUE"

ndays = 5
resub = 0

crm_nx = 32
crm_ny = 1


crmdim  = ""
if "SP" in cld :
    crmdim = "_"+str(crm_nx)+"x"+str(crm_ny) 

case_name = "ACME_"+cld+"_"+exp+"_"+res+crmdim+"_"+case_num

#===============================================================================================================================================================
#===============================================================================================================================================================
top_dir     = home+"/ACME/"
srcmod_dir  = top_dir+"mod_src/"
nmlmod_dir  = top_dir+"mod_nml/"

src_dir = "~/ACME/ACME_SRC"

scratch_dir = os.getenv("CSCRATCH","")
if scratch_dir=="" : 
    acct = "cli115"
    # acct = "csc249"
    if host=="titan" :
        if acct == "cli115" : 
            scratch_dir = "/lustre/atlas1/"+acct+"/scratch/hannah6"
        else : 
            scratch_dir = "/lustre/atlas/scratch/hannah6/"+acct+"/"

run_dir = scratch_dir+"/"+case_name+"/run"

if res=="ne4"   : num_dyn = 96
if res=="ne16"  : num_dyn = 1536
if res=="ne30"  : num_dyn = 5400
if res=="ne120" : num_dyn = 86400

#--------------------------------------------------------------------
#--------------------------------------------------------------------
os.system("cd "+top_dir)
case_dir  = top_dir+"Cases/"+case_name #+"/"
cdcmd = "cd "+case_dir+" ; "
print
print "  case : "+case_name
print
#===============================================================================================================================================================
#===============================================================================================================================================================
# Create new case
#===============================================================================================================================================================
#===============================================================================================================================================================
compset_opt = " -compset FC5AV1C-L "
    
if exp == "AMIP" :
    compset_opt = " -compset F20TRC5AV1C-04P2"

use_SP_compset = False
# if case_num in ['s1_00','s1_01'] :
#     if cld=="SP1" : compset_opt = " -compset FSP1V1 "
#     if cld=="SP2" : compset_opt = " -compset FSP2V1 "
#     use_SP_compset = True


if newcase == True:
    
    if host=="titan" and acct == "csc249" : os.system("echo '"+acct+"' > "+home+"/.cesm_proj")         # temporarily change project on titan

    newcase_cmd = src_dir+"/cime/scripts/create_newcase"
    cmd = newcase_cmd+" -case "+case_dir+" "+compset_opt+" -res "+res+"_"+res+" -mach  "+host
    print cmd
    os.system(cmd)

    if host=="titan" and acct == "csc249" : os.system("echo 'CSC249ADSE15' > "+home+"/.cesm_proj")       # change project name back

case_dir = case_dir+"/"

#===============================================================================================================================================================
#===============================================================================================================================================================
# Configure the case
#===============================================================================================================================================================
#===============================================================================================================================================================
if config == True:
    #------------------------------------------------
    # set vertical levels and CRM paramters
    #------------------------------------------------

    nlev_gcm = 72
    nlev_crm = 58

    # if cld=="SP1" :
    #     nlev_gcm = 26
    #     nlev_crm = 24
    # if cld=="SP2" :
    #     nlev_gcm = 30
    #     nlev_crm = 28

    crm_adv = "MPDATA"
    crm_dt = 5
    crm_dx = 1000

    #------------------------------------------------
    # set CAM_CONFIG_OPTS
    #------------------------------------------------
    if cld=="ZM" :
        cam_opt = " -rad rrtmg -nlev "+str(nlev_gcm)+"  -clubb_sgs -microphys mg2 "

        chem_opt = " -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates "

        cpp_opt = " -cppdefs ' "
        # cpp_opt = cpp_opt+"  "
        cpp_opt = cpp_opt+" ' "
            
        cam_opt = cam_opt+chem_opt+cpp_opt 
    
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

        # always reduce rad columns by factor of 8 (new default) - use less for smaller CRM
        cam_opt = cam_opt+" -crm_nx_rad 8 -crm_ny_rad 1 "
        if crm_nx == 16 : cam_opt = cam_opt.replace("-crm_nx_rad 8","-crm_nx_rad 4")

        # use the same chem and aerosol options for SP1 and SP2
        chem_opt = " -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates "

        # set CPP variables
        cpp_opt = "-cppdefs ' -DSP_DIR_NS  -DSP_TK_LIM  "

        #-------------------------------
        # Special cases
        #-------------------------------
        if any(c in case_num for c in ['31']) :
            chem_opt = chem_opt + " -use_ECPP "


        #-------------------------------
        #-------------------------------

        cam_opt = cam_opt+chem_opt+cpp_opt+" ' "


    if not use_SP_compset : 
        print("------------------------------------------------------------")
        CMD = cdcmd+"./xmlchange --file env_build.xml --id CAM_CONFIG_OPTS --val \""+cam_opt+"\""
        print(CMD)
        os.system(CMD)
        print("------------------------------------------------------------")
    
    #------------------------------------------------
    # for FV runs we need to set this here
    # otherwise it will complain about not having a default ncdata
    #------------------------------------------------
    if res=="1.9x2.5" :
        init_dir = "/lustre/atlas1/cli115/scratch/hannah6/init_files/"
        nfile = case_dir+"user_nl_cam"
        file = open(nfile,'w') 
        file.write(" ncdata  = '"+init_dir+"hp_built_for_wh_1.9x2.5_L72_20081014_12Z_ECMWF.cam2.i.2008-10-14-43200_r2.nc' \n") 
        file.close() 
    #------------------------------------------------
    # set run-time variables
    #------------------------------------------------
    start_date = "2000-01-01"
    
    os.system(cdcmd+"./xmlchange --file env_run.xml   --id RUN_STARTDATE  --val "+start_date)

    if host=="titan" :
        if acct != "cli115" : os.system(cdcmd+"./xmlchange --file env_run.xml --id RUNDIR  --val "+workdir+"/"+acct+"/"+case_name+"/run ")

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
    # Copy a custom namelist file
    #------------------------------------------------
    # nml_file = ""
    # nml_file = nmlmod_dir+"user_nl_cam.F."+exp+"."+case_num
    
    # if nml_file != "" :
    #     if not os.path.isfile(nml_file) :
    #         print "ERROR: Modified ATM namelist file does not exist! ("+nml_file+")"
    #         exit()
        
    #     CMD = "cp "+nml_file+"  "+case_dir+"user_nl_cam "
    #     print(CMD)
    #     os.system(CMD)
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

    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_LND -val "+str(num_dyn)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ICE -val "+str(num_dyn)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_OCN -val "+str(num_dyn)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_CPL -val "+str(num_dyn)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_GLC -val "+str(num_dyn)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_RTM -val "+str(num_dyn)+" ")
    os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_WAV -val "+str(num_dyn)+" ")
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
#         # branch_data = "/lustre/atlas1/cli115/scratch/hannah6/"+ref_case+"/run/"+ref_date+"-00000/* "
#         branch_data = "/lustre/atlas1/cli115/scratch/hannah6/"+ref_case+"/run/*.r*"+ref_date+"*nc "
#         cmd = "cp "+branch_data+" "+run_dir
#         print
#         print(cmd)
#         print
#         os.system(cmd)

#=================================================================================================================================
# Write the custom namelist options
#=================================================================================================================================
if mk_nml :
    nfile = case_dir+"user_nl_cam"
    file = open(nfile,'w') 

    file.write(" nhtfrq    = 0,-6,-3 \n") 
    file.write(" mfilt     = 1, 4, 8 \n") 
    file.write(" fincl2    = 'T','Q','PS','TS','Z3','OMEGA','U','V','QRL','QRS','CLOUD' ")
    file.write("\n")
    file.write(" fincl3    = 'TMQ','PRECT','LHFLX','SHFLX','FLNS','FLNT','FSNS','FSNT','FLUT' ")
    file.write("\n")

    if "SP" in cld : file.write(" srf_flux_avg = 1 \n")    

    file.write(" dyn_npes = "+str(num_dyn)+" \n")

    # enforce defaults for the split parameters - in case a previous test run modified them
    # file.write(" qsplit    = 1 \n") 
    # file.write(" rsplit    = 3 \n") 
    # file.write(" se_nsplit = 2 \n") 

    # file.write(" phys_alltoall = 1      \n")
    # file.write(" phys_loadbalance = 2   \n")

    file.close() 

    # Turn off CICE history files
    nfile = case_dir+"user_nl_cice"
    file = open(nfile,'w') 
    file.write(" histfreq = 'x','x','x','x','x' \n")
    file.close()

    ### convective gustiness modification
    # if exp == "AMIP" and "ZM" in cld and case_num in [] : 
    #     nfile = case_dir+"user_nl_cpl"
    #     file = open(nfile,'w') 
    #     file.write(" gust_fac = 1 \n")
    #     file.close()
#===============================================================================================================================================================
#===============================================================================================================================================================
# Run the simulation
#===============================================================================================================================================================
#===============================================================================================================================================================
if runsim == True:

    CMD = ''
    if acct == "csc249" : CMD = cdcmd+"./xmlchange --file env_batch.xml --id CHARGE_ACCOUNT --val \"CSC249ADSE15\" "
    if acct == "cli115" : CMD = cdcmd+"./xmlchange --file env_batch.xml --id CHARGE_ACCOUNT --val \"CLI115\" "
    print(CMD)
    if CMD != '' : os.system(CMD)

    # ncdata        = '/lustre/atlas1/cli115/scratch/hannah6/ACME_SP2_CTL_ne30_01/run/cami-mam3_0000-01-01_ne30np4_L30_c130424.modified.nc'
    # os.system(cdcmd+"./xmlchange --file env_run.xml   --id RUN_STARTDATE  --val 0006-01-01")

    runfile = case_dir+"case.run"
    subfile = case_dir+"case.submit"
    
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_OPTION  -val ndays ")
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_N       -val "+str(ndays)) 
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id RESUBMIT     -val "+str(resub))
    os.system(cdcmd+"./xmlchange -file env_run.xml   -id CONTINUE_RUN -val "+cflag)

    #------------------------------
    #  Set the queue
    #------------------------------
    os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val batch")
    # if test_run : os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val debug")

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
    # special debug mode - only run a few timesteps
    #------------------------------
    if test_run :
        nrun = 5
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_OPTION -val nsteps ")
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_N      -val "+str(nrun) )

        # Write the namelist options instead of copying a pre-written file
        nfile = case_dir+"user_nl_cam"
        file = open(nfile,'w') 
        # init_dir = "/lustre/atlas1/cli115/scratch/hannah6/init_files/"
        # if res=="ne30" : file.write(" ncdata    = '"+init_dir+"cami_mam3_Linoz_ne30np4_L72_c160214.no_ice.nc' \n") 
        # if res=="ne16" : file.write(" ncdata    = '"+init_dir+"cami_mam3_Linoz_ne16np4_L72_c160614.no_ice.nc' \n") 
        file.write(" nhtfrq    = 0,1 \n") 
        file.write(" mfilt     = 1,"+str(nrun)+" \n") 
        file.write(" fincl2    = 'T','Q','LHFLX','SHFLX','FLNT','FSNT','QRL','QRS','HR' ") 
        # file.write(" fincl2    = 'T','Q','PS','Z3','OMEGA','U','V','PRECL','PRECC','LHFLX','SHFLX' ") 
        # file.write(             ",'FLNS','FLNT','FSNS','FSNT','FLUT','TS','QRL','QRS' ")
        # file.write(             ",'CLDICE','NUMICE','CLOUD' ")
        file.write("\n")
        file.write(" srf_flux_avg = 1 \n")
        # file.write(" qsplit    = 1 \n") 
        # file.write(" rsplit    = 3 \n")       # increasing this might help avoid a negative thickness error... or not
        # file.write(" se_nsplit = 2 \n") 

        file.close() 

    #------------------------------
    # Set the wall clock limit
    #------------------------------
    if test_run :
        os.system(cdcmd+"./xmlchange -file env_batch.xml -id JOB_WALLCLOCK_TIME -val 00:30:00")
    else :
        os.system(cdcmd+"./xmlchange -file env_batch.xml -id JOB_WALLCLOCK_TIME -val "+wall_time)
    
    #------------------------------
    # Submit the run
    #------------------------------
    if "titan"  in host :
        mail_flag = " --mail-user hannah6@llnl.gov  -M end -M fail "
        if acct == "csc249" :
            os.system(cdcmd+subfile+" -a '-A csc249adse15'   "+mail_flag)
        else :
            os.system(cdcmd+subfile+"  "+mail_flag)
    else :
        os.system(cdcmd+subfile)
    
#==================================================================================================
#==================================================================================================

