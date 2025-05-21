#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'
case_dir = os.getenv('HOME')+'/E3SM/Cases'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # branch => whannah/mmf/2023-coupled-historical

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

# queue = 'batch' # batch / debug


# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'2:00:00'
stop_opt,stop_n,resub,walltime = 'ndays',32*3,6,'3:00:00'

compset,num_nodes,arch = 'FAQP-MMF1',32,'GNUGPU'

ne = 30; grid = f'ne{ne}pg2_oECv3'

# mmf_orientation_angle = 90 # N/S = control 
mmf_orientation_angle = 0 # E/W
# mmf_orientation_angle = -1 # RANDOM

case = '.'.join(['E3SM','2023-ORIENT-00',arch,grid,compset,f'OA_{mmf_orientation_angle:02}'])

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 64,1 ; max_task_per_node = 64
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  =  4,8 ; max_task_per_node = 32
atm_ntasks = max_mpi_per_node*num_nodes

#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd = cmd + f' -compset {compset} -res {grid}  '
   if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
os.chdir(f'{case_dir}/{case}/')
if newcase :
   if 'max_mpi_per_node'  in locals(): run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node} ')
   if 'max_task_per_node' in locals(): run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node} ')
#---------------------------------------------------------------------------------------------------
if config :
   #----------------------------------------------------------------------------
   # cpp_opt = ''
   # cpp_opt += f' -D'
   # if cpp_opt != '' :
   #    cmd  = f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS'
   #    cmd += f' --val \" -cppdefs \' {cpp_opt} \'  \" '
   #    run_cmd(cmd)
   #-------------------------------------------------------
   # PE layout mods from Noel
   cpl_stride = 8; cpl_ntasks = atm_ntasks / cpl_stride
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_CPL="{cpl_ntasks}"')
   run_cmd(f'./xmlchange --file env_mach_pes.xml PSTRID_CPL="{cpl_stride}"')
   run_cmd(f'./xmlchange --file env_mach_pes.xml ROOTPE_CPL="0"')
   #----------------------------------------------------------------------------
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   if 'debug-on' in case : run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   #----------------------------------------------------------------------------
   # ATM namelist
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   file.write(' nhtfrq = 0,-3,-3 \n')
   file.write(' mfilt  = 1,8,8 \n')
   file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots   
   file.write(         ",'CLOUD','CLDLIQ','CLDICE'")
   file.write('\n')
   file.write(" fincl2 = 'PS','TS','PSL'")
   file.write(          ",'PRECT','TMQ'")
   file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(          ",'FSNT','FLNT','FLUT'")        # TOM heating rates
   file.write(          ",'FLNS','FSNS'")               # SFC rad for total column heating
   file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(          ",'TGCLDLWP','TGCLDIWP'")       # liq/ice water path
   file.write(          ",'TAUX','TAUY'")               # surface stress
   file.write(          ",'TUQ','TVQ'")                 # vapor transport
   file.write('\n')
   file.write(" fincl3 =  'PS','PSL'")
   file.write(          ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   file.write(          ",'U','V','OMEGA'")             # 3D velocity components
   file.write(          ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   file.write(          ",'QRL','QRS'")                 # 3D radiative heating profiles
   file.write(          ",'MMF_DT','MMF_DQ'")
   file.write(          ",'MMF_DQC','MMF_DQI'")
   file.write(          ",'MMF_DU','MMF_DV'")
   file.write(          ",'MMF_TLS','MMF_QTLS'")
   file.write('\n')

   file.write(f' mmf_orientation_angle = {mmf_orientation_angle} \n')

   file.close()
   #----------------------------------------------------------------------------
   # ELM namelist
   nfile = 'user_nl_elm'
   file = open(nfile,'w')
   if 'land_data_file' in locals(): file.write(f' fsurdat = \'{land_data_path}/{land_data_file}\' \n')
   if 'land_init_file' in locals(): file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
   file.close()
   #----------------------------------------------------------------------------
   # Set some run-time stuff
   if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
   if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
   #----------------------------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')
#-------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n')
#-------------------------------------------------------------------------------

