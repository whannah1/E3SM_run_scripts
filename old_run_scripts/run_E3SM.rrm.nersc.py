#!/usr/bin/env python
import os
newcase,config,build,clean,submit,continue_run,debug_queue = False,False,False,False,False,False, False

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

debug_queue = True

top_dir  = "/global/homes/w/whannah/E3SM/"
src_dir  = top_dir+"E3SM_SRC1/"
case_dir = top_dir+"Cases/"

compset = "F-EAMv1-AQP1"


npg = 2

if npg==0 : 
   res = "ne0np4-aqua"
else:
   res = "ne0np4-aqua.pg"+str(npg)

# res = "ne"+str(ne) if npg==0 else  "ne"+str(ne)+"pg"+str(npg)

case = "E3SM_TEST_"+res+"_"+compset
# case = case+"_debug-on_checks-on"
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print("\n  case : "+case+"\n")

# num_dyn = ne*ne*6
# num_task = str(num_dyn)+"x1"
grid = res#+"_"+res

if newcase :
   cmd = src_dir+"cime/scripts/create_newcase -case "+case_dir+case
   cmd = cmd + " -compset "+compset+" -res "+grid
   # cmd = cmd + " --pecount "+num_task
   os.system(cmd)

os.chdir(case_dir+case+"/")
if config : 
   domain_path = "/global/cscratch1/sd/whannah/acme_scratch/init_files/"
   os.system("./xmlchange -file env_run.xml -id OCN_DOMAIN_PATH -val \""+domain_path+"\" ")
   os.system("./xmlchange -file env_run.xml -id ICE_DOMAIN_PATH -val \""+domain_path+"\" ")
   if npg==0 : dfile = "domain.ocn.ne4x2_oQU240.190319.nc"
   if npg==2 : dfile = "domain.ocn.ne4x2pg2_oQU240.190319.nc"
   os.system("./xmlchange -file env_run.xml -id OCN_DOMAIN_FILE -val \""+dfile+"\" ")
   os.system("./xmlchange -file env_run.xml -id ICE_DOMAIN_FILE -val \""+dfile+"\" ")
   #-------------------------------------------------------
   if clean : os.system("./case.setup --clean")
   os.system("./case.setup --reset")
   
if build : 
   if "debug-on" in case : os.system("./xmlchange -file env_build.xml -id DEBUG -val TRUE ")
   if clean : os.system("./case.build --clean")
   os.system("./case.build")

if submit : 
   #-------------------------------------------------------
   nfile = "user_nl_cam"
   file = open(nfile,'w') 
   file.write(" nhtfrq    = 0,-1 \n") 
   file.write(" mfilt     = 1, 24 \n")
   file.write(" fincl2    = 'PS','PRECT','TMQ','FLNT','U850'\n")
   file.write(" cubed_sphere_map = 2 \n") 
   init_path = "/global/cscratch1/sd/whannah/acme_scratch/init_files/"
   file.write(" ncdata = \'"+init_path+"/cami_aquaplanet_ne4x2_L72_c190319.nc\' \n")
   file.write(" drydep_srf_file = \'"+init_path+"/atmsrf_ne4x2.nc\' \n")

   # Defaults
   # file.write(" nu      =  1.0e15 \n")
   # file.write(" nu_div  =  2.5e15 \n")
   # file.write(" nu_p    =  1.0e15 \n")
   # file.write(" hypervis_subcycle = 3 \n")
   # stronger smoothing
   file.write(" nu      =  1.0e16 \n")
   file.write(" nu_div  =  1.0e16 \n")
   file.write(" nu_p    =  1.0e16 \n")
   file.write(" hypervis_subcycle = 8 \n")
   # file.write(" nu      =  1.0e16 \n")
   # file.write(" nu_div  =  2.5e16 \n")
   # file.write(" nu_p    =  1.0e16 \n")

   file.write("mesh_file = \'"+init_path+"/ne4x2.g\' \n")

   if "checks-on" in case : file.write(" state_debug_checks = .true. \n")
   file.close()
   #-------------------------------------------------------
   if debug_queue :
      queue, walltime, stop_opt, stop_n = "debug",  "0:30:00","ndays",10
   else:
      queue, walltime, stop_opt, stop_n = "regular","3:00:00","ndays",65

   # if debug_queue and continue_run : stop_n = 5
   
   # if ne>=45 and queue=="regular" : walltime = "5:00:00"

   os.system("./xmlchange -file env_run.xml   STOP_OPTION="+stop_opt+",STOP_N="+str(stop_n) )
   os.system("./xmlchange -file env_batch.xml JOB_QUEUE="+queue+",JOB_WALLCLOCK_TIME="+walltime )

   if continue_run :
      os.system("./xmlchange -file env_run.xml CONTINUE_RUN=TRUE ")
      os.system("./xmlchange -file env_run.xml RESUBMIT=6 ")
   else:
      os.system("./xmlchange -file env_run.xml CONTINUE_RUN=FALSE ")
   

   os.system("./case.submit")
   #-------------------------------------------------------

print("\n  case : "+case+"\n")
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------