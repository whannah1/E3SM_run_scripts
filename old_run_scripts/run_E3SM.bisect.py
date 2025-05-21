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

if "edison" in host : 
    host = "edison"
    acct = "acme"
if "blogin" in host : host = "anvil"
if "titan"  in host : 
    host = "titan"
    acct = "cli115"     # cli115 / csc249

get_src,newcase,config,build,runsim,clean,mk_nml = False,False,False,False,False,False,False
#======================================================================================================================
#======================================================================================================================

# clean = True

# get_src  = True
newcase  = True
config   = True
build    = True
mk_nml   = True
runsim   = True


# git_hashes =["cff9c9a0d76eab54ea3be9ca4be5266aaa0fab09"    # Aug 5 - Some extra cosmetic changes and code clean up (PR #45)
#             ,"20c33a19e3781675a01afb0da38f23b3060d750f"    # Jul 11 - Fix crm presi initialization bug; minor fixes for titan debug build
#             ,"eab2ecfbcec34388b69d293c391962a15cbcaaf8"    # Jul 10 - Merge 'E3SM/master' into ACME-ECP
#             ,"580263c09e6ca69a287f619c28c52c990478d78e"    # Jul 9 - Merge branch 'whannah/new_TKE_code' (PR #42) (right before ESM merge)
#             ,"e8f52d4e555940cec4de094c8b189397d0689a06"    # Jul 3 - New version of tke_full.F90 (CRM
#             ,"440918d775197fa6659feaf20f5fa53d63b681d7"    # Jun 18 - Merge branch 'whannah/crm_bulk_transport' (PR #38)
#             ,"45691649932fa34287dbc62801b882fff0b6bef2"    # Jun 7 - Merge branch whannah/crm_setperturb_bug_fix (PR #39)
#             ]

# git_hashes = ["cff9c9a0d76eab54ea3be9ca4be5266aaa0fab09"    # Aug 5 - Some extra cosmetic changes and code clean up (PR #45)
#              ,"20c33a19e3781675a01afb0da38f23b3060d750f"    # Jul 11 - Fix crm presi initialization bug; minor fixes for titan debug build
#              ,"eab2ecfbcec34388b69d293c391962a15cbcaaf8"    # Jul 10 - Merge 'E3SM/master' into ACME-ECP
#              ,"580263c09e6ca69a287f619c28c52c990478d78e"    # Jul 9 - Merge branch 'whannah/new_TKE_code' (PR #42) (right before ESM merge)
#              ,"e8f52d4e555940cec4de094c8b189397d0689a06"    # Jul 3 - New version of tke_full.F90 (CRM
#              ]
# git_hashes = [""]   # 
git_hashes = ["cff9c9a0d76eab54ea3be9ca4be5266aaa0fab09"]   # Aug 5 - Some extra cosmetic changes and code clean up (PR #45)
# git_hashes = ["45691649932fa34287dbc62801b882fff0b6bef2"]   # Jun 7 - Merge branch whannah/crm_setperturb_bug_fix (PR #39)

#--------------------------------------------------------
#--------------------------------------------------------
# case_num = "00"     # control - all current defaults - 15 min time step
# case_num = "01"     # 00 +  SP_ESMT  SP_USE_ESMT  SP_ORIENT_RAND
# case_num = "02"     # 01 +  srf_flux_avg
# case_num = "03"     # 02 +  30 min timestep
# case_num = "04"     # 03 +  crm_nx_rad 8
# case_num = "05"     # 04 +  crm_dx=1km

# case_num = "06"     # 00 +  crm_dx=1km
# case_num = "07"     # 00 +  30 min timestep + srf_flux_avg
# case_num = "08"     # 00 +  srf_flux_avg
# case_num = "09"     # 00 +  SP_ORIENT_RAND
# case_num = "10"     # 00 +  se_ftype = 0
# case_num = "11"     # 00 +  se_ftype = 1
# case_num = "12"     # 00 +  SP_FLUX_BYPASS
case_num = "13"     # 00 (15-min) + se_nsplit=1

#--------------------------------------------------------
#--------------------------------------------------------

cld = "SP1"    # ZM / SP1 / SP2
exp = "bisect"
res = "ne30"   # ne30 / ne16 / ne4 / 0.9x1.25 / 1.9x2.5

cflag = "FALSE"  # continue flag - Don't forget to set this!!!! 


if "ZM" in cld : ndays,resub = (73),(0)         # 5=1yr
if "SP" in cld : ndays,resub = 5,(6*3-1 )       # 3 months

wall_time = "4:00:00"

crm_nx,crm_ny,mod_str = 64,1,"_4km" # don't change this!

if case_num in ['05','06'] : crm_nx,crm_ny,mod_str = 64,1,"_1km"


#--------------------------------------------------------
# Special Cases
#--------------------------------------------------------

if "ZM" in cld : mod_str = ""

#--------------------------------------------------------
# Set the case name
#--------------------------------------------------------

if "SP" in cld : 
    crmdim = "_"+str(crm_nx)+"x"+str(crm_ny) 
else : 
    crmdim = ""


#===============================================================================================================================================================
#===============================================================================================================================================================
# Begin loop over git hashes
#===============================================================================================================================================================
#===============================================================================================================================================================

for git_hash in git_hashes :

    git_hash_shortname = git_hash[:8]

    case_name = "E3SM_"+exp+"_"+res+"_"+cld+crmdim+mod_str+"_"+case_num+"_"+git_hash_shortname

    #======================================================================================================================
    # Various settings for account / system / directories
    #======================================================================================================================
    top_dir     = home+"/E3SM/"
    srcmod_dir  = top_dir+"mod_src/"
    nmlmod_dir  = top_dir+"mod_nml/"

    scratch_dir = os.getenv("CSCRATCH","")
    if scratch_dir=="" : 
        if host=="titan" :
            if acct == "cli115" : 
                scratch_dir = "/lustre/atlas1/"+acct+"/scratch/hannah6"
            else : 
                scratch_dir = "/lustre/atlas/scratch/hannah6/"+acct+""

    run_dir = scratch_dir+"/"+case_name+"/run"

    if res=="ne4"      : num_dyn = 96
    if res=="ne16"     : num_dyn = 1536
    if res=="ne30"     : num_dyn = 5400
    if res=="0.9x1.25" : num_dyn = 1536
    if res=="1.9x2.5"  : num_dyn = 1536

    dtime = 15*60

    if case_num in ['03','04','05','07'] : 
        dtime = 30*60

    ncpl  = 86400 / dtime

    os.system("cd "+top_dir)
    case_dir  = top_dir+"Cases/"+case_name 
    cdcmd = "cd "+case_dir+" ; "
    
    if len(git_hashes) > 1 : 
        print("============================================================================================================")
    print
    print("  case : "+case_name)
    print

    #======================================================================================================================
    #======================================================================================================================
    # Retrieve the source code
    #======================================================================================================================
    #======================================================================================================================

    src_dir = scratch_dir+"/E3SM_SRC/"+git_hash_shortname

    cd_src = "cd "+src_dir+" ; "

    if get_src :

        if not os.path.isdir(src_dir) : 
            os.mkdir(src_dir)

        CMD = cd_src+"git clone git@github.com:E3SM-Project/ACME-ECP.git "+src_dir
        print(CMD)
        os.system(CMD)

        CMD = cd_src+"git checkout "+git_hash
        print(CMD)
        os.system(CMD)

        # CMD = cd_src+"git submodule sync "
        # print(CMD)
        # os.system(CMD)

        CMD = cd_src+"git submodule update --init "
        print(CMD)
        os.system(CMD)

    #======================================================================================================================
    #======================================================================================================================
    # Create new case
    #======================================================================================================================
    #======================================================================================================================

    compset_opt = " -compset FC5AV1C-L "
    grid_opt    = res+"_"+res
        
    use_SP_compset = False

    # if cld=="SP1" : compset_opt = " -compset FSP1V1 " ; use_SP_compset = True
    # if cld=="SP2" : compset_opt = " -compset FSP2V1 " ; use_SP_compset = True

    if "A_WCYCL" in compset_opt : grid_opt = res+"_oECv3_ICG"

    if newcase == True:

        if host=="titan" : os.system("echo '"+acct+"' > "+home+"/.cesm_proj")         # change project on titan

        newcase_cmd = src_dir+"/cime/scripts/create_newcase"
        cmd = newcase_cmd+" -case "+case_dir+" "+compset_opt+" -res "+grid_opt+" -mach  "+host
        print("\n"+cmd+"\n")
        os.system(cmd)

        if host=="titan" and acct == "csc249" : os.system("echo 'CSC249ADSE15' > "+home+"/.cesm_proj")       # change project name back for csc249

    case_dir = case_dir+"/"

    #======================================================================================================================
    #======================================================================================================================
    # Configure the case
    #======================================================================================================================
    #======================================================================================================================
    if config == True:
        #------------------------------------------------
        # set vertical levels
        #------------------------------------------------
        nlev_gcm = 72
        nlev_crm = 58
        
        crm_adv = "MPDATA"

        crm_dt = 5
        crm_dx = 4000

        if case_num in ['05','06'] : crm_dx = 1000

        #------------------------------------------------
        # set CAM_CONFIG_OPTS
        #------------------------------------------------

        if cld=="ZM" :
            cam_opt = " -rad rrtmg -nlev "+str(nlev_gcm)+"  -clubb_sgs -microphys mg2 "

            chem_opt = " -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates "

            cpp_opt = " -cppdefs ' -DAPPLY_POST_DECK_BUGFIXES "

            cam_crm_rad_opt = ""
        
        if "SP" in cld :

            ### set options common to all SP setups
            cam_opt = " -use_SPCAM  -rad rrtmg  -nlev "+str(nlev_gcm)+"  -crm_nz "+str(nlev_crm)+" -crm_adv "+crm_adv+" "\
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
            if case_num in ['04','05'] : 
                cam_crm_rad_opt = " -crm_nx_rad 8 -crm_ny_rad 1 "
            else :
                cam_crm_rad_opt = " "

            cam_opt = cam_opt+cam_crm_rad_opt

            ### use the same chem and aerosol options for SP1 and SP2
            chem_opt = " -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates "

            ### set default CPP variables
            # cpp_opt = " -cppdefs ' -DAPPLY_POST_DECK_BUGFIXES -DSP_TK_LIM  -DSP_ESMT -DSP_USE_ESMT -DSP_ORIENT_RAND "
            cpp_opt = " -cppdefs ' -DAPPLY_POST_DECK_BUGFIXES -DSP_TK_LIM "

            #-------------------------------
            # Special cases
            #-------------------------------

            if case_num in ['01','02','03','04','05'] : 
                cpp_opt = cpp_opt+" -DSP_ESMT  -DSP_USE_ESMT  "   

            if case_num in ['01','02','03','04','05','09'] : 
                cpp_opt = cpp_opt+"  -DSP_ORIENT_RAND "   


            if case_num in ['12'] : 
                cpp_opt = cpp_opt+"  -DSP_FLUX_BYPASS "

            # if '' in case_num : cpp_opt = cpp_opt+"  -D "
            # if case_num in [''] : cpp_opt = cpp_opt.replace("-D","")    # remove cpp flag
            #-------------------------------
            #-------------------------------


        cam_opt = cam_opt+chem_opt+cpp_opt+" ' "


        if cld=="ZM" or ( "SP" in cld and not use_SP_compset ) : 
            print("------------------------------------------------------------")
            CMD = cdcmd+"./xmlchange --file env_build.xml --id CAM_CONFIG_OPTS --val \""+cam_opt+"\""
            print(CMD)
            os.system(CMD)
            print("------------------------------------------------------------")


        #------------------------------------------------
        # set run-time variables
        #------------------------------------------------
        start_date = "2000-01-01"

        os.system(cdcmd+"./xmlchange --file env_run.xml   --id RUN_STARTDATE  --val "+start_date)

        if host=="titan" :
            if acct == "cli115" : os.system(cdcmd+"./xmlchange --file env_run.xml --id RUNDIR  --val /lustre/atlas1/cli115/scratch/hannah6/"+case_name+"/run ")
            if acct == "csc249" : os.system(cdcmd+"./xmlchange --file env_run.xml --id RUNDIR  --val /lustre/atlas/scratch/hannah6/csc249/" +case_name+"/run ")
        
        #------------------------------------------------
        # Change processor count
        #------------------------------------------------
        if res=="ne4" :
            os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val  866 ")    # 96 / 866
        if res=="ne16" :
            os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val 1536 ")    # 1536 / 3457
        if res=="ne30" :
            os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val 6076 ")    # 5400 / 6076 / 10800

        if cld == "ZM" : os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ATM -val "+str(num_dyn)+" ")

        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_LND -val "+str(num_dyn)+" ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_ICE -val "+str(num_dyn)+" ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_OCN -val "+str(num_dyn)+" ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_CPL -val "+str(num_dyn)+" ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_GLC -val "+str(num_dyn)+" ")
        # os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_RTM -val "+str(num_dyn)+" ")
        os.system(cdcmd+"./xmlchange -file env_mach_pes.xml  -id NTASKS_WAV -val "+str(num_dyn)+" ")

        #------------------------------------------------
        # Set the timestep
        #------------------------------------------------
        os.system(cdcmd+"./xmlchange -file env_run.xml -id ATM_NCPL -val "+str(ncpl) )

        #------------------------------------------------
        # configure the case
        #------------------------------------------------
        if os.path.isfile(case_dir+"case.setup") :
            if clean : os.system(cdcmd+"./case.setup --clean")
            os.system(cdcmd+"./case.setup")
        else :
            os.system(cdcmd+"./cesm_setup")     # older versions

    #======================================================================================================================
    #======================================================================================================================
    # Build the model
    #======================================================================================================================
    #======================================================================================================================
    if build == True:
        
        if "titan"  in host : 
            if acct == "cli115" : os.system(cdcmd+"./xmlchange -file env_build.xml   -id CIME_OUTPUT_ROOT  -val /lustre/atlas1/cli115/scratch/hannah6/")
            if acct == "csc249" : os.system(cdcmd+"./xmlchange -file env_build.xml   -id CIME_OUTPUT_ROOT  -val /lustre/atlas/scratch/hannah6/csc249/" )

        if os.path.isfile(case_dir+"case.build") :
            if clean : os.system(cdcmd+"./case.build --clean")                  # Clean previous build    
            os.system(cdcmd+"./case.build")
        else :
            os.system(cdcmd+"./"+case_name+".clean_build")
            os.system(cdcmd+"./"+case_name+".build")

    #======================================================================================================================
    # Write the custom namelist options
    #======================================================================================================================
    if mk_nml :

        (cam_config_opts, err) = subprocess.Popen(cdcmd+"./xmlquery CAM_CONFIG_OPTS -value", stdout=subprocess.PIPE, shell=True).communicate()
        (compset        , err) = subprocess.Popen(cdcmd+"./xmlquery COMPSET         -value", stdout=subprocess.PIPE, shell=True).communicate()
        (din_loc_root   , err) = subprocess.Popen(cdcmd+"./xmlquery DIN_LOC_ROOT    -value", stdout=subprocess.PIPE, shell=True).communicate()

        ### remove extra spaces to simplify string query
        cam_config_opts = ' '.join(cam_config_opts.split())

        nfile = case_dir+"user_nl_cam"
        file = open(nfile,'w') 

        #------------------------------
        # output variables
        #------------------------------
        
        file.write(" nhtfrq    = 0,-1 \n") 
        file.write(" mfilt     = 1,24 \n")   

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
        file.write(             ",'QEXCESS' ")
        file.write(             ",'PTTEND' ")
        if "chem none" not in cam_config_opts :
            file.write(         ",'AEROD_v','EXTINCT'")         # surface fluxes
        if "SP" in cld :
            file.write(             ",'SPDT','SPDQ' ")
            # file.write(             ",'CRM_T','CRM_QV','CRM_QC','CRM_QPC','CRM_PREC' ")
            file.write(             ",'SPQTFLX','SPQTFLXS'")
            file.write(             ",'SPTLS','SPQTLS' ")
            file.write(             ",'SPQPEVP','SPMC' ")
            file.write(             ",'SPMCUP','SPMCDN','SPMCUUP','SPMCUDN' ")
            # file.write(             ",'SPQC','SPQR' ")
            # file.write(             ",'SPQI','SPQS','SPQG' ")
            file.write(             ",'SPTK','SPTKE','SPTKES' ")
        if "SP_CRM_SPLIT" in cam_config_opts :
            file.write(         ",'SPDT1','SPDQ1','SPDT2','SPDQ2' ")
            file.write(         ",'SPTLS1','SPTLS2' ")
        file.write("\n")

        
        if case_num in ['02','03','04','05','07','08'] :
            file.write(" srf_flux_avg = 1 \n")
        else :
            file.write(" srf_flux_avg = 0 \n")


        if case_num in ['10'] :
            file.write(" se_ftype = 0 \n")
        if case_num in ['11'] :
            file.write(" se_ftype = 1 \n")

        if case_num in ['13'] :
            file.write(" se_nsplit = 1 \n")

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
        # close the atm namelist file
        #------------------------------
        file.close() 

        #------------------------------
        # Land model namelist
        #------------------------------
        # nfile = case_dir+"user_nl_clm"
        # file = open(nfile,'w') 
        # file.write(" hist_nhtfrq = 0,1\n")
        # # file.write(" hist_mfilt  = 1, 30 \n")
        # file.write(" hist_mfilt  = 1,"+str(ncpl)+" \n")
        # file.write(" hist_fincl2 = 'TBOT','QTOPSOIL','RH','RAIN'")
        # file.write(              ",'FGEV','FCEV','FCTR'")
        # file.write(              ",'FSH_V','FSH_G'")
        # file.write("\n")
        # file.close()
        #------------------------------
        # Turn off CICE history files
        #------------------------------
        nfile = case_dir+"user_nl_cice"
        file = open(nfile,'w') 
        file.write(" histfreq = 'x','x','x','x','x' \n")
        file.close()
        

    #======================================================================================================================
    #======================================================================================================================
    # Run the simulation
    #======================================================================================================================
    #======================================================================================================================
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

        #------------------------------
        # Change run options
        #------------------------------
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_OPTION  -val ndays ")
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id STOP_N       -val "+str(ndays)) 
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id RESUBMIT     -val "+str(resub))
        os.system(cdcmd+"./xmlchange -file env_run.xml   -id CONTINUE_RUN -val "+cflag)

        #------------------------------
        # Set the wall clock limit
        #------------------------------
        os.system(cdcmd+"./xmlchange -file env_batch.xml -id JOB_WALLCLOCK_TIME -val "+wall_time)

        #------------------------------
        # Submit the run
        #------------------------------
        if "titan"  in host :
            mail_flag = " --mail-user hannah6@llnl.gov  -M end -M fail "
            os.system(cdcmd+"./xmlchange -file env_batch.xml -id BATCH_COMMAND_FLAGS -val \"\" ")
            os.system(cdcmd+subfile+mail_flag)
        else :
            os.system(cdcmd+subfile)
        

    print("")
    print("  case : "+case_name)
    print("")

#======================================================================================================================
#======================================================================================================================
#======================================================================================================================
#======================================================================================================================