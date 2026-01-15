#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END); os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
newcase,config,build,clean,submit,continue_run,reset_resub,st_archive,cp_branch_data = False,False,False,False,False,False,False,False,False

acct = 'm3312'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC3' # branch => whannah/atm/rcemip-phase-2-update

# clean        = True
# newcase      = True
# config       = True
# build        = True
cp_branch_data = True
# submit       = True
# continue_run = True
### reset_resub  = True

debug_mode = False

queue = 'regular' # debug / regular

grid,num_nodes = 'ne30pg2_ne30pg2',64
# grid,num_nodes = 'ne4pg2_ne4pg2',1

# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',5,0,'3:00:00'
stop_opt,stop_n,resub,walltime = 'ndays',32,0,'3:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',100,0,'4:00:00'

compset_list,msst_list,arch_list = [],[],[]
crm_nx_list, crm_ny_list, crm_dx_list = [],[],[]
def add_case(compset,msst=None,crm_nx=None,crm_ny=1,crm_dx=None):
   compset_list.append(compset); msst_list.append(msst)
   crm_nx_list.append(crm_nx)
   crm_ny_list.append(crm_ny)
   crm_dx_list.append(crm_dx)
   arch_list.append('GNUGPU' if 'MMF' in compset else 'GNUCPU')


# add_case('FRCE-MMF1',msst=300,crm_nx= 32,crm_dx=1000)
# add_case('FRCE-MMF1',msst=300,crm_nx= 64,crm_dx=1000)
# add_case('FRCE-MMF1',msst=300,crm_nx=128,crm_dx=1000)
# add_case('FRCE-MMF1',msst=300,crm_nx=256,crm_dx=1000)

# add_case('FRCE-MMF1',msst=300,crm_nx= 32,crm_dx=4000)
# add_case('FRCE-MMF1',msst=300,crm_nx= 64,crm_dx=4000)
add_case('FRCE-MMF1',msst=300,crm_nx=128,crm_dx=4000)
add_case('FRCE-MMF1',msst=300,crm_nx=256,crm_dx=4000)


# alt initial condition for new L72 grid
init_root = '/global/cfs/cdirs/m4310/whannah/E3SM/init_data'
init_file_atm = None
if grid=='ne4pg2_ne4pg2':   init_file_atm = f'{init_root}/eam_i_rcemip_ne4np4_L72_c20240716.nc'
if grid=='ne30pg2_ne30pg2': init_file_atm = f'{init_root}/eam_i_rcemip_ne30np4_L72_c20240716.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(compset,msst,arch,crm_nx,crm_ny,crm_dx):

   compset_str = compset if msst is None else f'{compset}_{msst}'

   # case_list = ['E3SM','2024-RCEMIP-DOMAIN-TEST',compset_str]
   case_list = ['E3SM','2024-RCEMIP-DOMAIN-TEST-01',compset_str] # short runs w/ alt output

   if grid!='ne30pg2_ne30pg2': case_list.append(grid)
   case_list.append(f'NX_{crm_nx}x{crm_ny}')
   case_list.append(f'DX_{crm_dx}')

   if debug_mode: case_list.append('debug')
   case = '.'.join(case_list)

   #------------------------------------------------------------------------------------------------
   if 'CPU' in arch: max_mpi_per_node,atm_nthrds  = 128,1 ; max_task_per_node = 128
   if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   4,8 ; max_task_per_node = 32
   atm_ntasks = max_mpi_per_node*num_nodes

   if 'CPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
   if 'GPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/{case}'

   #------------------------------------------------------------------------------------------------
   #------------------------------------------------------------------------------------------------
   print('\n  case : '+case+'\n')
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      # Check if directory already exists   
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case}'
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --handle-preexisting-dirs u '
      cmd += f' --compset {compset}'
      cmd += f' --res {grid} '
      if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
      if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
      cmd += f' --project {acct} '
      cmd += f' --walltime {walltime} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config :
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------
      run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node} ')
      run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node} ')
      #-------------------------------------------------------
      if msst is not None:
         run_cmd(f'./xmlchange DOCN_AQPCONST_VALUE={msst}')
      #-------------------------------------------------------
      # when specifying ncdata, do it here to avoid an error message
      write_nl_opts(case,compset)
      #-------------------------------------------------------
      rad_nx, rad_ny = 1,1
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dx {crm_dx}  \" ')
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev 72 -crm_nz 60 \" ')
      #-------------------------------------------------------
      # Add special CPP flags for MMF options
      # cpp_opt = ''
      # if crm_ny>1: cpp_opt += ' -DMMF_MOMENTUM_FEEDBACK'
      # if cpp_opt != '' :
      #    cmd  = f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -cppdefs \' {cpp_opt} \'  \" '
      #    run_cmd(cmd)
      #-------------------------------------------------------
      #-------------------------------------------------------
      run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
      #-------------------------------------------------------
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   # Build
   if build : 
      #-------------------------------------------------------
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if cp_branch_data:
      if '.2024-RCEMIP-DOMAIN-TEST-01.' in case:
         ref_case = case.replace('2024-RCEMIP-DOMAIN-TEST-01.','2024-RCEMIP-DOMAIN-TEST.')
         ref_date = '0001-07-21'
         run_cmd(f'./xmlchange RUN_TYPE=hybrid')
         run_cmd(f'./xmlchange RUN_STARTDATE=0001-01-01,START_TOD=0')
         run_cmd(f'./xmlchange GET_REFCASE=FALSE')
         run_cmd(f'./xmlchange RUN_REFCASE=\'{ref_case}\'')
         run_cmd(f'./xmlchange RUN_REFDATE={ref_date}')
         # copy the initialization data files
         scratch = '/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu'
         run_cmd(f'cp {scratch}/{ref_case}/run/*{ref_date}* {case_root}/run/')
   #------------------------------------------------------------------------------------------------
   # Write the namelist options and submit the run
   if submit : 
      write_nl_opts(case,compset)
      #-------------------------------------------------------
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      # if 'resub' in globals() and not continue_run: run_cmd(f'./xmlchange RESUBMIT={resub}')
      # if 'resub' in globals() and reset_resub: run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'resub' in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'GPU' in arch: run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct}_g,PROJECT={acct}_g')
      #-------------------------------------------------------
      if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
def write_nl_opts(case,compset,init_file_atm=None):
   nl_opts = ''
   if init_file_atm is not None: nl_opts += f' ncdata = \'{init_file_atm}\'\n'
   nl_opts += "empty_htapes = .false. \n"
   nl_opts += "avgflag_pertape = 'A','A','I' \n"
   nl_opts += "nhtfrq = -240,-1,-3 \n"
   nl_opts += "mfilt  = 1,24,8 \n"
   # nl_opts += "nhtfrq = -240,-1,-6 \n"
   # nl_opts += "mfilt  = 1,24,4 \n"
   nl_opts += "fincl1 = 'Z3','CLOUD','CLDLIQ','CLDICE'"
   nl_opts += "\n"
   # 2D 1 hour average
   nl_opts += "fincl2 = 'TS','PSL','PS'"
   nl_opts +=         ",'PRECT','PRECC','SHFLX','LHFLX'"
   nl_opts +=         ",'TMQ','TMQS','TGCLDLWP','TGCLDIWP'"
   nl_opts +=         ",'FLDS','FLNS'"       # sfc LW
   nl_opts +=         ",'FSDS','FSNS'"       # sfc SW
   nl_opts +=         ",'FLDSC','FLNSC'"     # sfc LW clearsky
   nl_opts +=         ",'FSDSC','FSNSC'"     # sfc SW clearsky
   nl_opts +=         ",'FLUTOA','FLNTOA'"   # toa LW
   nl_opts +=         ",'FSUTOA','FSNTOA'"   # toa SW
   nl_opts +=         ",'FLUTOAC','FLNTOAC'" # toa LW clearsky
   nl_opts +=         ",'FSUTOAC','FSNTOAC'" # toa SW clearsky
   nl_opts +=         ",'CLDTOT','CLDLOW','CLDMED','CLDHGH'"
   nl_opts +=         ",'OMEGA500'"
   nl_opts +=         ",'UBOT','VBOT','TBOT','QBOT'"
   nl_opts +=         ",'U10','TREFHT'"
   nl_opts += "\n"
   # # 3D 6 hour average
   # nl_opts += "fincl3 = 'PS','T','Q','Z3','RELHUM'"
   # nl_opts +=         ",'CLDLIQ','CLDICE','CLOUD'"
   # nl_opts +=         ",'U','V','OMEGA'"
   # nl_opts +=         ",'QRS','QRL'"
   # nl_opts +=         ",'PS','T','Q','Z3','RELHUM'"
   # nl_opts +=         ",'CLDLIQ','CLDICE','CLOUD'"
   # nl_opts +=         ",'U','V','OMEGA'"
   # nl_opts +=         ",'QRS','QRL'"
   # nl_opts +=         ",'QRSC','QRLC'"
   # nl_opts +=         ",'DTCOND'"
   # nl_opts +=         ",'CRM_QPC','CRM_QPI'"
   # nl_opts +=         ",'MMF_MCUP'"           # convective mass flux
   # nl_opts += "\n"
   # 3D 3 hour instant
   nl_opts += "fincl3 = 'PS','T','Q','Z3','RELHUM'"
   nl_opts +=         ",'CLDLIQ','CLDICE','CLOUD'"
   nl_opts +=         ",'U','V','OMEGA'"
   nl_opts +=         ",'QRS','QRL'"
   nl_opts +=         ",'PS','T','Q','Z3','RELHUM'"
   nl_opts +=         ",'CLDLIQ','CLDICE','CLOUD'"
   nl_opts +=         ",'U','V','OMEGA'"
   nl_opts +=         ",'QRS','QRL'"
   if '.2024-RCEMIP-DOMAIN-TEST-01.' in case:
      nl_opts +=         ",'MMF_MCUP'"           # convective mass flux
      nl_opts +=         ",'MMF_MCUP2'"          # convective mass flux - no W threshold
   else:
      # nl_opts +=         ",'CRM_U','CRM_W'"
      # nl_opts +=         ",'CRM_T','CRM_QV'"
      nl_opts +=         ",'CRM_QPC','CRM_QPI'"
      nl_opts +=         ",'MMF_MCUP'"           # convective mass flux
   nl_opts += "\n"
   # nl_opts += "inithist = 'NONE' \n"
   nl_opts += "inithist = 'ENDOFRUN' \n"
   # if  crm_ny>1: nl_opts += ' use_mmf_esmt = .false. \n'
   file=open('user_nl_eam','w')
   file.write(nl_opts)
   file.close()
   return 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for n in range(len(compset_list)):
      # print('-'*80)
      main( compset_list[n], 
            msst_list[n], 
            arch_list[n], 
            crm_nx_list[n], 
            crm_ny_list[n], 
            crm_dx_list[n],
          )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
