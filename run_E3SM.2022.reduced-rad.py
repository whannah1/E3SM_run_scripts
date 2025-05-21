#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
from optparse import OptionParser
parser = OptionParser()
parser.add_option('--radnx',dest='radnx',default=None,help='sets number of rad columns')
(opts, args) = parser.parse_args()
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli145' # cli115 / cli145
case_dir = os.getenv('HOME')+'/E3SM/Cases'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1'

print_commands_only = False

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

queue = 'batch' # batch / debug

disable_bfb = False

compset,num_nodes,arch = 'F2010-MMF1',128,'GNUGPU'

stop_opt,stop_n,resub,walltime = 'ndays',11,0,'4:00' 

rad_arch_list,rad_nx_list,rad_sort_flag = [],[],[]
# rad_nx_list.append(128) ; stop_n,resub,walltime = 11,1,'4:00'; rad_sort_flag.append(False)
# rad_nx_list.append( 64) ; stop_n,resub,walltime = 11,1,'4:00'; rad_sort_flag.append(False)
# rad_nx_list.append( 32) ; stop_n,resub,walltime = 22,0,'4:00'; rad_sort_flag.append(False)
# rad_nx_list.append( 16) ; stop_n,resub,walltime = 22,0,'4:00'; rad_sort_flag.append(False)
# rad_nx_list.append(  8) ; stop_n,resub,walltime = 22,0,'4:00'; rad_sort_flag.append(False)
# rad_nx_list.append(  4) ; stop_n,resub,walltime = 22,0,'4:00'; rad_sort_flag.append(False)
# rad_nx_list.append(  2) ; stop_n,resub,walltime = 22,0,'4:00'; rad_sort_flag.append(False)
# rad_nx_list.append(  1) ; stop_n,resub,walltime = 22,0,'4:00'; rad_sort_flag.append(False)

rad_nx_list.append(128) ; stop_n,resub,walltime = 11,2,'4:00'; rad_sort_flag.append(True)
# rad_nx_list.append(  8) ; stop_n,resub,walltime = 11,0,'4:00'; rad_sort_flag.append(True)



#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(rad_nx=None,rad_arch='gpu',use_rad_sort=False):

   if rad_nx is None: exit('rad_nx argument not provided?')

   ne,npg         = 30,2
   use_momfb      = True
   use_vt         = True
   crm_dx         = 1000
   crm_nx,crm_ny  = 128,1

   res=f'ne{ne}' if npg==0 else f'ne{ne}pg{npg}'; grid = f'{res}_oECv3' # f'{res}_r05_oECv3' / f'{res}_{res}'

   #############################################
   # override for testing lagrangian rad
   # ne,npg = 4,2; grid = 'ne4pg2_ne4pg2'; crm_nx,crm_ny,crm_dx=32,1,2000
   #############################################

   case_list = ['E3SM','RAD-SENS',arch,grid,compset,f'NXY_{crm_nx}x{crm_ny}',f'RNX_{rad_nx}']
   if use_rad_sort: case_list.append('RAD_SORT')

   ### batch/version number
   batch_num = '00' # initial runs
   # batch_num = '01' # ???

   case_list.append(batch_num)
   case = '.'.join(case_list)

   # case = case+'.debug-on'

   ### specify land initial condition file
   land_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
   if grid=='ne30pg2_r05_oECv3':land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_r05_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
   if grid=='ne30pg2_oECv3':    land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
   #------------------------------------------------------------------------------------------------
   # Impose wall limits for Summit
   #------------------------------------------------------------------------------------------------
   if 'walltime' not in locals():
      if num_nodes>=  1: walltime =  '2:00'
      if num_nodes>= 46: walltime =  '6:00'
      if num_nodes>= 92: walltime = '12:00'
      if num_nodes>=922: walltime = '24:00'
   #------------------------------------------------------------------------------------------------
   #------------------------------------------------------------------------------------------------
   print('\n  case : '+case+'\n')

   max_task_per_node = 42
   if 'CPU' in arch : max_mpi_per_node,tmp_atm_nthrds  = 42,1
   if 'GPU' in arch : max_mpi_per_node,tmp_atm_nthrds  = 6,4
   if 'atm_nthrds' not in locals(): atm_nthrds = tmp_atm_nthrds
   task_per_node = max_mpi_per_node
   atm_ntasks = task_per_node*num_nodes
   #-------------------------------------------------------------------------------
   # Define run command
   #-------------------------------------------------------------------------------
   class tcolor: ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
   def run_cmd(cmd,suppress_output=False,execute=True):
      if suppress_output : cmd = cmd + ' > /dev/null'
      msg = tcolor.GREEN + cmd + tcolor.ENDC
      if not print_commands_only: msg = f'\n{msg}'
      if print_commands_only: execute = True
      print(msg)
      if execute: os.system(cmd)
      return
   #------------------------------------------------------------------------------------------------
   # Create new case
   #------------------------------------------------------------------------------------------------
   if newcase :
      # Check if directory already exists
      if not print_commands_only:
         if os.path.isdir(f'{case_dir}/{case}'): 
            exit(tcolor.RED+"\nThis case already exists!\n"+tcolor.ENDC)
      cmd = f'{src_dir}/cime/scripts/create_newcase -mach summit -case {case_dir}/{case}'
      cmd = cmd + f' -compset {compset} -res {grid}  '
      if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
      if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
      run_cmd(cmd)
      #-------------------------------------------------------
      # Change run directory to be next to bld directory
      #-------------------------------------------------------
      if not print_commands_only: 
         os.chdir(f'{case_dir}/{case}/')
      else:
         print(tcolor.GREEN+f'cd {case_dir}/{case}/'+tcolor.ENDC)
      # run_cmd('./xmlchange -file env_run.xml RUNDIR=\'$CIME_OUTPUT_ROOT/$CASE/run\' ' )
      run_cmd('./xmlchange -file env_run.xml RUNDIR=\'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/$CASE/run\' ' )

      run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_TASKS_PER_NODE    -val {max_task_per_node} ')
      run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val {max_mpi_per_node} ')
   else:
      if not print_commands_only: 
         os.chdir(f'{case_dir}/{case}/')
      else:
         print(tcolor.GREEN+f'cd {case_dir}/{case}/'+tcolor.ENDC)
   #------------------------------------------------------------------------------------------------
   # Configure
   #------------------------------------------------------------------------------------------------
   if config :
      #-------------------------------------------------------
      # Set some non-default stuff for all MMF experiments here
      if 'MMF' in compset:
         rad_ny = rad_nx if crm_ny>1 else 1
         # run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dt {crm_dt} \" ')
         run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dx {crm_dx}  \" ')
         run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
         run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
         if use_vt: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')
      #-------------------------------------------------------
      # Add special MMF options based on case name
      cpp_opt = ''
      if 'debug-on' in case : cpp_opt += ' -DYAKL_DEBUG'

      # if  crm_ny==1: cpp_opt += ' -DMMF_DIR_NS' # no longer needed
      if crm_ny==1 and use_momfb: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
      if crm_ny>1  and use_momfb: cpp_opt += ' -DMMF_MOMENTUM_FEEDBACK'

      if use_rad_sort: cpp_opt += ' -DMMF_LAGRANGIAN_RAD'

      if cpp_opt != '' :
         cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
         cmd += f' -val \" -cppdefs \' {cpp_opt} \'  \" '
         run_cmd(cmd)
      #-------------------------------------------------------
      # Set tasks for all components
      if ne>=30:
         cmd = './xmlchange -file env_mach_pes.xml '
         alt_ntask = 600; cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
         alt_ntask = 675; cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
         alt_ntask = max_mpi_per_node
         cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
         cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
         run_cmd(cmd)
      #-------------------------------------------------------
      # 64_data format is needed for large numbers of columns (GCM or CRM)
      run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
      #-------------------------------------------------------
      # Run case setup
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   # Build
   #------------------------------------------------------------------------------------------------
   if build : 
      if 'debug-on' in case : run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   # Write the namelist options and submit the run
   #------------------------------------------------------------------------------------------------
   if submit : 
      #-------------------------------------------------------
      # Set some run-time stuff
      #-------------------------------------------------------
      # if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
      run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
      run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
      run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

      # init_scratch = '/gpfs/alpine/cli115/scratch/hannah6/inputdata'
      init_scratch = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata'

      if     continue_run: run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------
      # ATM namelist
      #-------------------------------------------------------
      if not print_commands_only: 
         ### Change inputdata from default due to permissions issue
         # run_cmd('./xmlchange DIN_LOC_ROOT=/gpfs/alpine/cli115/scratch/hannah6/inputdata ')
         # run_cmd('./xmlchange DIN_LOC_ROOT=/gpfs/alpine/cli115/world-shared/e3sm/inputdata ')
         if 'init_scratch' in locals(): run_cmd(f'./xmlchange DIN_LOC_ROOT={init_scratch} ')
         #------------------------------
         # Namelist options
         #------------------------------
         nfile = 'user_nl_eam'
         file = open(nfile,'w') 
         #------------------------------
         # history output variables
         #------------------------------
         if batch_num=='00':
            if grid=='ne4pg2_ne4pg2':
               file.write(' nhtfrq = 0,-1,-24 \n')
               file.write(' mfilt  = 1,24,1 \n')
            else:
               file.write(' nhtfrq = 0,-3,-24 \n')
               file.write(' mfilt  = 1, 8,1 \n')
            file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots   
            file.write(         ",'CLOUD','CLDLIQ','CLDICE'")
            file.write('\n')
            file.write(" fincl2 = 'PS','TS','PSL'")
            file.write(          ",'PRECT','TMQ'")
            file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
            file.write(          ",'FSNT','FLNT'")               # Net TOM heating rates
            file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
            file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
            file.write(          ",'TGCLDLWP','TGCLDIWP'")
            file.write(          ",'TAUX','TAUY'")               # surface stress
            file.write(          ",'TUQ','TVQ'")                         # vapor transport
            file.write(          ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
            file.write(          ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
            file.write(          ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
            file.write(          ",'Z300:I','Z500:I'")
            file.write(          ",'OMEGA850:I','OMEGA500:I'")
            file.write('\n')
            if grid=='ne4pg2_ne4pg2':
               file.write(" fincl3 =  'PS','PSL'")
               file.write(          ",'T','Q','Z3' ")               # 3D thermodynamic budget components
               file.write(          ",'U','V','OMEGA'")             # 3D velocity components
               file.write(          ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
               file.write(          ",'QRL','QRS'")                 # 3D radiative heating profiles
               file.write('\n')
         #------------------------------
         # Other namelist stuff
         #------------------------------
         ### limit dynamics tasks
         # num_dyn = ne*ne*6
         # ntask_dyn = int( num_dyn / atm_nthrds )
         # file.write(f' dyn_npes = {ntask_dyn} \n')
         # file.write(" inithist = \'ENDOFRUN\' \n") # ENDOFRUN / NONE
         file.close()
      #-------------------------------------------------------
      # CLM namelist
      #-------------------------------------------------------
      if not print_commands_only: 
         nfile = 'user_nl_elm'
         file = open(nfile,'w')
         if ne==30 and npg==2: file.write(f' fsurdat = \'{init_scratch}/lnd/clm2/surfdata_map/surfdata_ne30pg2_simyr2010_c210402.nc\' \n')
         if 'land_init_file' in locals(): file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
         file.close()
      #-------------------------------------------------------
      # Submit the run
      #-------------------------------------------------------
      if not print_commands_only: 
         if     disable_bfb: run_cmd('./xmlchange BFBFLAG=FALSE')
         if not disable_bfb: run_cmd('./xmlchange BFBFLAG=TRUE')
         run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   #------------------------------------------------------------------------------------------------
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for n in range(len(rad_nx_list)):
      print('-'*80)
      main(rad_nx=rad_nx_list[n],use_rad_sort=rad_sort_flag[n])

