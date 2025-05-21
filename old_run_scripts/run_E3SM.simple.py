#!/usr/bin/env python
import os
newcase,config,build,clean,submit,continue_run,debug_queue = False,False,False,False,False,False,False


top_dir  = "/global/homes/w/whannah/E3SM/"
case_dir = top_dir+"Cases/"

# src_dir  = top_dir+"E3SM_SRC1/"
# src_dir  = top_dir+"E3SM_SRC2/"
src_dir  = top_dir+"E3SM_SRC3/"

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True
debug_queue  = True

if debug_queue :
   queue, walltime, stop_opt, stop_n, resub = "debug",  "0:30:00","ndays",1,0
   # stop_opt,stop_n,resub,walltime = 'nsteps',1,0,'0:30:00'
else:
   queue, walltime, stop_opt, stop_n, resub = "regular","3:00:00","ndays",65,0


ne,npg = 4,0
compset = 'F-EAMv1-AQP1'   # FC5AV1C-L / F-EAMv1-AQP1 / FSP1V1 / FSP2V1

res = "ne"+str(ne) if npg==0 else  "ne"+str(ne)+"pg"+str(npg)

case = "E3SM_temp-TEST_"+res+"_"+compset+"_00"  # ?
# case = case+"_debug-on"
# case = case+"_checks-on"

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print("\n  case : "+case+"\n")

num_dyn = ne*ne*6
num_task = str(num_dyn)+"x1"
grid = res+"_"+res
# grid = res+"_oECv3_ICG"
#---------------------------------------------------------------------------------------------------
if newcase :
   cmd = src_dir+"cime/scripts/create_newcase -case "+case_dir+case
   cmd = cmd + " -compset "+compset+" -res "+grid+" --pecount "+num_task
   os.system(cmd)
#---------------------------------------------------------------------------------------------------
# domain_path = "/global/cscratch1/sd/whannah/acme_scratch/init_files/"
# domain_file     = "domain.ocn."+res+"_oQU240.190321.nc"
# domain_file_lnd = "domain.lnd."+res+"_oQU240.190321.nc"
os.chdir(case_dir+case+"/")
if config : 
   #-------------------------------------------------------
   # if ne==4 and npg>0 :
   #    os.system("./xmlchange -file env_run.xml OCN_DOMAIN_PATH=\""+domain_path+"\",ICE_DOMAIN_PATH=\""+domain_path+"\" ")
   #    os.system("./xmlchange -file env_run.xml OCN_DOMAIN_FILE=\""+domain_file+"\",ICE_DOMAIN_FILE=\""+domain_file+"\" ")
   #    if compset=="FC5AV1C-L" :
   #       os.system("./xmlchange -file env_run.xml LND_DOMAIN_PATH=\""+domain_path+"\",LND_DOMAIN_FILE=\""+domain_file_lnd+"\" ")
   #-------------------------------------------------------
   if clean : os.system("./case.setup --clean")
   os.system("./case.setup --reset")
#--------------------------------------------------------------------------------------------------- 
if build : 
   if "debug-on" in case : os.system("./xmlchange -file env_build.xml -id DEBUG -val TRUE ")
   if clean : os.system("./case.build --clean")
   os.system("./case.build")
#---------------------------------------------------------------------------------------------------
if submit : 
   init_path = "/global/cscratch1/sd/whannah/acme_scratch/init_files/"
   #-------------------------------------------------------
   if True: 
      nfile = "user_nl_cam"
      file = open(nfile,'w') 
      file.write(" nhtfrq    = 0,-1 \n") 
      file.write(" mfilt     = 1, 24 \n")
      file.write(" fincl2    = 'PS','PRECT','TMQ'")
      file.write(            ",'LHFLX','SHFLX'")
      # file.write(            ",'FSNT','FLNT','FLNS','FSNS'")
      # file.write(            ",'UBOT','VBOT','QBOT','TBOT'")
      # file.write(            ",'T','Q','U','OMEGA'")
      # file.write(            ",'TBP','QBP','TAP','QAP'")
      # file.write(            ",'PTTEND','PTEQ','TTEND_TOT','DTCOND','DCQ'")
      # if npg>0 : file.write(   ",'DYN_PS','DYN_T','DYN_OMEGA' ")

      file.write("\n")
      if "checks-on" in case : file.write(" state_debug_checks = .true. \n")

      ### Dycor mods
      # nu_val = 1.0e15 * 10.**(1.-ne/30.)
      # if spinup : nu_val = nu_val * 3
      # nu_str = "{0:.2e}".format(nu_val)
      # nu_div = "{0:.2e}".format(nu_val)
      # if compset=="FC5AV1C-L" : nu_div = "{0:.2e}".format( nu_val*2.5 )
      # file.write(" nu      = "+nu_str+" \n")  
      # file.write(" nu_div  = "+nu_str+" \n") 
      # file.write(" nu_p    = "+nu_str+" \n") 

      # hyper_sub = 3
      # # if spinup : hyper_sub = hyper_sub*4
      # file.write(" hypervis_subcycle = "+str(hyper_sub)+" \n")

      # file.write(" inithist = \'ENDOFRUN\' \n")
      # file.write(" phys_loadbalance = -1   \n")
      # file.write(" use_gw_front = .false. \n")

      file.close()
   #-------------------------------------------------------
   # if ne >= 60 : ncpl = 144   # 10 min
   # if ne  < 60 : ncpl = 96    # 15 min
   # if ne  < 46 : ncpl = 48    # 30 min
   # if ne  <  8 : ncpl = 48    # 60 min
   # os.system('./xmlchange -file env_run.xml   ATM_NCPL='          +str(ncpl)   )
   #-------------------------------------------------------
   os.system('./xmlchange -file env_run.xml   STOP_OPTION='       +stop_opt    )
   os.system('./xmlchange -file env_run.xml   STOP_N='            +str(stop_n) )
   os.system('./xmlchange -file env_batch.xml JOB_QUEUE='         +queue       )
   os.system('./xmlchange -file env_batch.xml JOB_WALLCLOCK_TIME='+walltime    )
   os.system('./xmlchange -file env_run.xml   RESUBMIT='          +str(resub)  )

   if continue_run :
      os.system("./xmlchange -file env_run.xml CONTINUE_RUN=TRUE ")
   else:
      os.system("./xmlchange -file env_run.xml CONTINUE_RUN=FALSE ")

   os.system("./case.submit")
   #-------------------------------------------------------

print("\n  case : "+case+"\n")
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
