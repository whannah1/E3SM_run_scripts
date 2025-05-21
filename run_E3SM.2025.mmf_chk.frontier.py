#!/usr/bin/env python3
import os, datetime, subprocess as sp
#---------------------------------------------------------------------------------------------------
class tcolor: END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
#---------------------------------------------------------------------------------------------------
def run_cmd(cmd,suppress_output=False):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.END ; print(f'\n{msg}')
   os.system(cmd); return
#---------------------------------------------------------------------------------------------------
def xmlquery(xmlvar):
   ( value, err) = sp.Popen(f'./xmlquery {xmlvar} --value', stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   return value
#---------------------------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli200'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => <updates YAKL>

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

debug_mode = False

queue,stop_opt,stop_n,resub,walltime = 'batch','ndays',1,0,'0:30:00'

# arch = 'CPU'

#---------------------------------------------------------------------------------------------------
# build list of cases to run

add_case(prefix='2025-MMF-CHK-00', compset='F2010-MMF1', grid='ne4pg2_oQU480', arch='cpu', num_nodes=1)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(opts):

   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix','compset']:
         case_list.append(val)
      elif key in ['num_nodes']:
         continue
      # elif key in ['grid'] and 'FSCM' in opts['compset']:
      #    continue
      else:
         # case_list.append(f'{key}_{val:g}')
         case_list.append(f'{key}_{val}')
   case = '.'.join(case_list)

   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')

   print(f'\n  case : {case}\n')

   # exit()

   if 'FSCM' in opts['compset']: opts['grid'] = 'ne4_ne4'

   #------------------------------------------------------------------------------------------------
   case_root = f'/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch/{case}'

   num_nodes = opts['num_nodes']
   if opts['arch']=='cpu': max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,56,1
   if opts['arch']=='gpu': max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,8,1
   atm_ntasks = max_mpi_per_node*num_nodes

   grid    = opts['grid']#+'_'+opts['grid']
   compset = opts['compset']
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{tcolor.RED}This case already exists!{tcolor.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case}'
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --handle-preexisting-dirs u '
      cmd += f' --compset {compset}'
      cmd += f' --res {grid} '
      cmd += f' --project {acct} '
      if opts['arch']=='cpu': cmd+=f' -mach frontier -compiler craygnu'
      if opts['arch']=='gpu': cmd+=f' -mach frontier -compiler craycray-mphipcc'
      cmd += f' -pecount {atm_ntasks}x{atm_nthrds} '
      run_cmd(cmd)
      #----------------------------------------------------------------------------
      # # Copy this run script into the case directory
      # timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config : 
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------------------------
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #-------------------------------------------------------
      # atmos namelist options
      nfile = 'user_nl_eam'
      file = open(nfile,'w') 
      #-------------------------------------------------------
      # atmos history output
      file.write(' nhtfrq    = 0,-1,-24 \n')
      file.write(' mfilt     = 1,24,1 \n')
      ### add some monthly variables to the default
      file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots   
      file.write(         ",'CLOUD','CLDLIQ','CLDICE'")
      file.write('\n')
      ### hourly 2D variables
      # file.write(" fincl2    = 'PS','TS','PSL'")
      # file.write(             ",'PRECT','TMQ'")
      # file.write(             ",'PRECC','PRECSC'")
      # file.write(             ",'PRECL','PRECSL'")
      # file.write(             ",'LHFLX','SHFLX'")                    # surface fluxes
      # file.write(             ",'FSNT','FLNT'")                      # Net TOM heating rates
      # file.write(             ",'FLNS','FSNS'")                      # Surface rad for total column heating
      # file.write(             ",'FSNTC','FLNTC'")                    # clear sky heating rates for CRE
      # file.write(             ",'LWCF','SWCF'")                      # cloud radiative foricng
      # file.write(             ",'TGCLDLWP','TGCLDIWP'")              # cloud water path
      # file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT'")
      # file.write(             ",'TUQ','TVQ'")                         # vapor transport
      # file.write(             ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
      # file.write(             ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
      # file.write(             ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
      # file.write(             ",'Z300:I','Z500:I'")
      # file.write(             ",'OMEGA850:I','OMEGA500:I'")
      # file.write('\n')

      if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\' \n')

      file.close() # close atm namelist file
      #-------------------------------------------------------------------------
      # Set some run-time stuff
      # run_cmd(f'./xmlchange ATM_NCPL={int(86400/dtime)}')
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
      if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------------------------
      # Submit the run
      # run_cmd(f'./case.submit -a=" -x frontier08656 " ')
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
