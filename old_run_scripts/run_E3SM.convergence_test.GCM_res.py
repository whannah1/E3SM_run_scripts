#!/usr/bin/env python
import os
newcase,config,build,clean,submit,continue_run,debug_queue,spinup = False,False,False,False,False,False,False,False
top_dir  = "/global/homes/w/whannah/E3SM/"
src_dir  = top_dir+"E3SM_SRC1/"
case_dir = top_dir+"Cases/"

# clean        = True
# debug_queue  = True
# spinup       = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

ne,npg = 45,2

compset = "F-EAMv1-AQP1"
res = "ne"+str(ne) if npg==0 else  "ne"+str(ne)+"pg"+str(npg)
# case = "E3SM_TEST_"+res+"_"+compset
case = "E3SM_CTEST-H_"+res+"_"+compset+"_00"
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print("\n  case : "+case+"\n")
if newcase :
   cmd = src_dir+"cime/scripts/create_newcase -case "+case_dir+case
   cmd = cmd + " -compset "+compset+" -res "+res+"_"+res+" --pecount "+str(ne*ne*6)+"x1"
   os.system(cmd)
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+"/")
if config : 
   if ne >= 60 : ncpl = 144   # 10 min
   if ne  < 60 : ncpl = 96    # 15 min
   if spinup : ncpl = ncpl*3 #288
   os.system("./xmlchange -file env_run.xml -id ATM_NCPL -val "+str(ncpl)+" ")
   #-------------------------------------------------------
   domain_path = "/global/cscratch1/sd/whannah/acme_scratch/init_files/"
   domain_file     = "domain.ocn."+res+"_oQU240.190321.nc"
   # domain_file_lnd = "domain.lnd."+res+"_oQU240.190321.nc"
   os.system("./xmlchange -file env_run.xml OCN_DOMAIN_PATH=\""+domain_path+"\",ICE_DOMAIN_PATH=\""+domain_path+"\" ")
   os.system("./xmlchange -file env_run.xml OCN_DOMAIN_FILE=\""+domain_file+"\",ICE_DOMAIN_FILE=\""+domain_file+"\" ")
   # os.system("./xmlchange -file env_run.xml LND_DOMAIN_PATH=\""+domain_path+"\",LND_DOMAIN_FILE=\""+domain_file_lnd+"\" ")
   #-------------------------------------------------------
   if clean : os.system("./case.setup --clean")
   os.system("./case.setup --reset")
#---------------------------------------------------------------------------------------------------
if build : 
   # if "debug-on" in case : os.system("./xmlchange -file env_build.xml -id DEBUG -val TRUE ")
   if clean : os.system("./case.build --clean")
   os.system("./case.build")
#---------------------------------------------------------------------------------------------------
if submit : 
   if ne==60  : os.system("./xmlchange -file env_run.xml -id EPS_AGRID -val 2e-12 ")
   if ne==120 : os.system("./xmlchange -file env_run.xml -id EPS_AGRID -val 5e-12 ")
   #-------------------------------------------------------
   init_path = "/global/cscratch1/sd/whannah/acme_scratch/init_files/"
   nfile = "user_nl_cam"
   file = open(nfile,'w') 
   file.write(" nhtfrq    = 0,-1 \n") 
   file.write(" mfilt     = 1, 24 \n")
   file.write(" fincl2    = 'PS','PRECT','TMQ','FLNT','U850'\n")
   file.write(" cubed_sphere_map = 2 \n") 
   file.write(" ncdata = \'"+init_path+"/cami_aquaplanet_ne"+str(ne)+"np4_L72.nc\' \n")
   # Dycor mods
   nu_val = 1.0e15 * 10.**(1.-ne/30.)
   if spinup : nu_val = nu_val * 4
   nu_str = "{0:.2e}".format(nu_val)
   file.write(" nu      = "+nu_str+" \n")  
   file.write(" nu_div  = "+nu_str+" \n") 
   file.write(" nu_p    = "+nu_str+" \n")  
   hyper_sub = 3
   file.write(" hypervis_subcycle = "+str(hyper_sub)+" \n")
   file.close()
   #-------------------------------------------------------
   # queue, walltime, stop_opt, stop_n = "regular","1:00:00","ndays",6
   if ne < 60 : queue, walltime, stop_opt, stop_n = "regular","4:00:00","ndays",40
   if ne== 60 : queue, walltime, stop_opt, stop_n = "regular","4:00:00","ndays",30
   if ne==120 : queue, walltime, stop_opt, stop_n = "regular","5:00:00","ndays",20
   if debug_queue : queue, walltime, stop_opt, stop_n = "debug",  "0:30:00","ndays",2
   os.system("./xmlchange -file env_run.xml   STOP_OPTION="+stop_opt+",STOP_N="+str(stop_n) )
   os.system("./xmlchange -file env_batch.xml JOB_QUEUE="+queue+",JOB_WALLCLOCK_TIME="+walltime )
   if continue_run :
      os.system("./xmlchange -file env_run.xml CONTINUE_RUN=TRUE ")
      os.system("./xmlchange -file env_run.xml RESUBMIT=10 ")
   else:
      os.system("./xmlchange -file env_run.xml CONTINUE_RUN=FALSE ")
      # if spinup : os.system("./xmlchange -file env_run.xml RESUBMIT=10 ")
   os.system("./case.submit")
   #-------------------------------------------------------

print("\n  case : "+case+"\n")
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------