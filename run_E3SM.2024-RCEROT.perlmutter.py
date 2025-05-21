#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END); os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
newcase,config,build,clean,submit,continue_run,st_archive = False,False,False,False,False,False,False

acct = 'm3312'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC4' # branch => whannah/2024-rce-with-rotation

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

disable_bfb = True

debug_mode = False

queue = 'regular'

grid,num_nodes = 'ne30pg2_ne30pg2',64

# stop_opt,stop_n,resub,walltime = 'ndays',10,0,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',90,3,'4:00:00'

#-------------------------------------------------------------------------------
compset_list,msst_list,arch_list = [],[],[]
crm_nx_list, crm_ny_list, crm_dx_list = [],[],[]
mem_list = []
def add_case(compset,mem=None,msst=None,crm_nx=None,crm_ny=1,crm_dx=None):
   compset_list.append(compset); msst_list.append(msst)
   crm_nx_list.append(crm_nx)
   crm_ny_list.append(crm_ny)
   crm_dx_list.append(crm_dx)
   arch_list.append('GNUGPU' if 'MMF' in compset else 'GNUCPU')
   mem_list.append(mem)
#-------------------------------------------------------------------------------
# add_case('FRCEROT',msst=300)
# add_case('FRCEROT',msst=320)

# add_case('FRCEROT-MMF1',msst=300,crm_nx=128,crm_dx=1000)
# add_case('FRCEROT-MMF1',msst=320,crm_nx=128,crm_dx=1000)

# add_case('FRCEROT',         mem='01') 
add_case('FRCEROT-320',     mem='01') # add +20K uniformly
# add_case('FRCEROT-MMF1',    mem='01',crm_nx=128,crm_dx=1000) 
# add_case('FRCEROT-320-MMF1',mem='01',crm_nx=128,crm_dx=1000) # add +20K uniformly

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(compset,mem,msst,arch,crm_nx,crm_ny,crm_dx):

   compset_str = compset if msst is None else f'{compset}_{msst}'

   # case_list = ['E3SM','2024-RCEROT-01',compset_str] # note that 320 is meaningless for AQP pattern
   # case_list = ['E3SM','2024-RCEROT-02',compset_str] # add +20K uniformly
   
   case_list = ['E3SM',f'2024-RCEROT-{mem}',compset_str] 

   if grid!='ne30pg2_ne30pg2': case_list.append(grid)
   if 'MMF' in compset:
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
   # Configure
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
      write_nl_opts(compset)
      #-------------------------------------------------------
      if 'MMF' in compset:
         # rad_nx, rad_ny = 1,1
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dx {crm_dx}  \" ')
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
         # run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev 72 -crm_nz 60 \" ')
      #-------------------------------------------------------
      # Add special CPP flags for MMF options
      cpp_opt = ''
      if msst==320: cpp_opt += ' -DAQP20'
      if cpp_opt != '' :
         cmd  = f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -cppdefs \' {cpp_opt} \'  \" '
         run_cmd(cmd)
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
   # Write the namelist options and submit the run
   if submit : 
      write_nl_opts(compset)
      #-------------------------------------------------------
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      # if 'resub' in globals() and not continue_run: run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'resub' in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'GPU' in arch: run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct}_g,PROJECT={acct}_g')
      #-------------------------------------------------------
      if     disable_bfb: run_cmd('./xmlchange BFBFLAG=FALSE')
      if not disable_bfb: run_cmd('./xmlchange BFBFLAG=TRUE')
      #-------------------------------------------------------
      if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
def write_nl_opts(compset):
   nl_opts = ''
   #----------------------------------------------------------------------------
   if 'MMF' in compset:
      # alt initial condition for new L72 grid for MMF
      init_root = '/global/cfs/cdirs/m4310/whannah/E3SM/init_data'
      if grid=='ne4pg2_ne4pg2':   init_file_atm = f'{init_root}/eam_i_rcemip_ne4np4_L72_c20240716.nc'
      if grid=='ne30pg2_ne30pg2': init_file_atm = f'{init_root}/eam_i_rcemip_ne30np4_L72_c20240716.nc'
      nl_opts += f' ncdata = \'{init_file_atm}\'\n'
   #----------------------------------------------------------------------------
   
   nl_opts += "empty_htapes = .true. \n"
   nl_opts += "avgflag_pertape = 'A','I','I','I' \n"
   nl_opts += "nhtfrq = -240,-1,-6,-6 \n"
   nl_opts += "mfilt  = 1,24,4,4 \n"
   # nl_opts += "fincl1    = 'Z3'\n"
   nl_opts += "fincl1 = 'TS','PSL','PS'"
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
   nl_opts +=         ",'T','Q','Z3','RELHUM'"
   nl_opts +=         ",'CLDLIQ','CLDICE','CLOUD'"
   nl_opts +=         ",'U','V','OMEGA'"
   nl_opts +=         ",'QRS','QRL'"
   nl_opts += "\n"
   # 2D 1 hour instant
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
   # 3D 6 hour instant
   nl_opts += "fincl3 = 'PS','T','Q','Z3','RELHUM'"
   nl_opts +=         ",'CLDLIQ','CLDICE','CLOUD'"
   nl_opts +=         ",'U','V','OMEGA'"
   nl_opts +=         ",'QRS','QRL'"
   nl_opts +=         ",'PS','T','Q','Z3','RELHUM'"
   nl_opts +=         ",'CLDLIQ','CLDICE','CLOUD'"
   nl_opts +=         ",'U','V','OMEGA'"
   nl_opts +=         ",'QRS','QRL'"
   nl_opts +=         ",'QRSC','QRLC'"
   nl_opts +=         ",'DTCOND'"
   # nl_opts +=         ",'CRM_QPC','CRM_QPI'"
   # nl_opts +=         ",'MMF_MCUP'"           # convective mass flux
   nl_opts += "\n"
   # nl_opts += " fincl4    = 'PS','T','Q','Z3'"            # 3D thermodynamic budget components
   # nl_opts +=              ",'U','V','OMEGA'"             # 3D velocity components
   # nl_opts +=              ",'CLDLIQ','CLDICE'"           # 3D cloud fields
   # nl_opts +=              ",'QRL','QRS'"                 # 3D radiative heating profiles
   # 3D 6 hour instant - MSE budget terms
   nl_opts += " fincl4    = 'PS'"            # 3D thermodynamic budget components
   if 'MMF' in compset:
      nl_opts +=         ",'DDSE_TOT','DQLV_TOT'" # Total Eulerian MSE tendencies
      nl_opts +=         ",'DDSE_DYN','DQLV_DYN'" # Dynamics MSE tendencies
      nl_opts +=         ",'DDSE_CRM','DQLV_CRM'" # 
      nl_opts +=         ",'DDSE_QRS','DDSE_QRL'" # 
      nl_opts +=         ",'DDSE_CEF','DQLV_CEF'" # 
      nl_opts +=         ",'DDSE_PBL','DQLV_PBL'" # 
      nl_opts +=         ",'DDSE_GWD'"            # 
      nl_opts +=         ",'DDSE_CRM_ALT','DQLV_CRM_ALT'"
   else:
      nl_opts +=         ",'DDSE_TOT','DQLV_TOT'" # Total Eulerian MSE tendencies
      nl_opts +=         ",'DDSE_DYN','DQLV_DYN'" # Dynamics MSE tendencies
      nl_opts +=         ",'DDSE_CLD','DQLV_CLD'" # convection schemes
      nl_opts +=         ",'DDSE_QRS','DDSE_QRL'" # 
      nl_opts +=         ",'DDSE_CEF','DQLV_CEF'" # 
      nl_opts +=         ",'DDSE_GWD'"            # 
   nl_opts += "\n"
   nl_opts += "inithist = 'NONE' \n"
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
            mem_list[n], 
            msst_list[n], 
            arch_list[n], 
            crm_nx_list[n], 
            crm_ny_list[n], 
            crm_dx_list[n],
          )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
