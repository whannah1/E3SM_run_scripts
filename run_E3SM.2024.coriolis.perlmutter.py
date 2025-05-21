#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END); os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
newcase,config,build,clean,submit,continue_run,reset_resub,st_archive = False,False,False,False,False,False,False,False

acct = 'm4310' # m4310 / m3312
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC4' # whannah/2024-coriolis-test

# clean        = True
# newcase      = True
# config       = True
build        = True
submit       = True
# continue_run = True
### reset_resub  = True

# queue = 'batch' # batch / debug

# stop_opt,stop_n,resub,walltime = 'nsteps',4,0,'0:10:00' 
# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00' 
# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'2:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',73,4,'4:00:00'
stop_opt,stop_n,resub,walltime = 'ndays',73,5*4-1,'4:00:00'

### set grid
grid='ne30pg2_EC30to60E2r2';  num_nodes=32
# grid='ne30pg2_oECv3';  num_nodes=32
# grid='ne4pg2_oQU480';  num_nodes=1

# arch = 'GNUCPU' # GNUGPU / GNUCPU

#---------------------------------------------------------------------------------------------------
compset_list = []
GNHS_list,GNCT_list = [],[]
doXU_list,doXW_list,doSU_list,doSW_list = [],[],[],[]
nx_list,ny_list = [],[]
nlev_list = []
def add_case(compset,GNHS=False,GNCT=False,doXU=False,doXW=False,doSU=False,doSW=False,nx=64,ny=1,nlev=None):
   compset_list.append(compset)
   GNHS_list.append(GNHS)
   GNCT_list.append(GNCT)
   doXU_list.append(doXU)
   doXW_list.append(doXW)
   doSU_list.append(doSU)
   doSW_list.append(doSW)
   nx_list.append(nx)
   ny_list.append(ny)
   nlev_list.append(nlev)
#---------------------------------------------------------------------------------------------------

add_case('F2010-MMF1',GNHS=False,GNCT=False) # control
add_case('F2010-MMF1',GNHS=True ,GNCT=False) # test non-hydrostatic effects
add_case('F2010-MMF1',GNHS=True ,GNCT=True ) # enable NCT in HOMME

# add_case('F2010',GNHS=False,GNCT=False) # control
# add_case('F2010',GNHS=True ,GNCT=False) # test non-hydrostatic effects
# add_case('F2010',GNHS=True ,GNCT=True ) # enable NCT in HOMME

# add_case('F2010-MMF1',GNHS=True ,GNCT=True,doXU=False,doXW=False,doSU=False,doS=False)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(compset,GNHS,GNCT,doXU,doXW,doSU,doSW,nx,ny,nlev):

   if 'MMF' in compset:
      arch = 'GNUGPU'
   else:
      arch = 'GNUCPU'
      
   # case_list=['E3SM','2024-coriolis-00',arch,grid,compset] # only use NCT in GCM
   case_list=['E3SM','2024-coriolis-01',arch,grid,compset] # switch to AMIP for QBO diagnosis
   if 'MMF' in compset: case_list.append(f'NXY_{nx}_{ny}')
   case_list.append('NHS-on' if GNHS else 'NHS-off')
   case_list.append('NCT-on' if GNCT else 'NCT-off')
   # case_list.append('XU-on' if doXU else 'XU-off')
   # case_list.append('XW-on' if doXW else 'XW-off')
   # case_list.append('SU-on' if doSU else 'SU-off')
   # case_list.append('SW-on' if doSW else 'SW-off')

   case='.'.join(case_list)

   # print(case); exit()
   #---------------------------------------------------------------------------------------------------
   init_scratch = '/global/cfs/cdirs/m4310/whannah/HICCUP/data/'
   init_file_atm = None
   if 'MMF' in compset:
      arch = 'GNUGPU'
      if nlev==64: init_file_atm = f'{init_scratch}/20220504.v2.LR.bi-grid.amip.chemMZT.chrysalis.eam.i.1985-01-01-00000.L80_c20230629.L64_c20230819.nc'
      if nlev==72: init_file_atm = f'{init_scratch}/20220504.v2.LR.bi-grid.amip.chemMZT.chrysalis.eam.i.1985-01-01-00000.L80_c20230629.L72_c20230819.nc'
   else:
      arch = 'GNUCPU'
      if nlev==72: init_file_atm = f'{init_scratch}/20220504.v2.LR.bi-grid.amip.chemMZT.chrysalis.eam.i.1985-01-01-00000.nc'
      if nlev==80: init_file_atm = f'{init_scratch}/20220504.v2.LR.bi-grid.amip.chemMZT.chrysalis.eam.i.1985-01-01-00000.L80_c20230629.nc'

   init_path_lnd = '/global/cfs/cdirs/m4310/whannah/E3SM/init_data'
   init_case_lnd = 'ELM_spinup.ICRUELM.ne30pg2_EC30to60E2r2.20-yr.2010-01-01'
   init_file_lnd = f'{init_path_lnd}/{init_case_lnd}.elm.r.2010-01-01-00000.nc'
   data_path_lnd = '/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map'
   data_file_lnd = f'{data_path_lnd}/surfdata_ne30pg2_simyr2010_c210402.nc'
   #------------------------------------------------------------------------------------------------
   if 'CPU' in arch: max_mpi_per_node,atm_nthrds  = 128,1 ; max_task_per_node = 128
   if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   4,8 ; max_task_per_node = 32
   atm_ntasks = max_mpi_per_node*num_nodes
   if 'CPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
   if 'GPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/{case}'
   #------------------------------------------------------------------------------------------------
   #------------------------------------------------------------------------------------------------
   print(f'\n  case : {case}\n')
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase : 
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase --case {case}'
      cmd += f' --output-root {case_root} --script-root {case_root}/case_scripts '
      cmd += f' --handle-preexisting-dirs u '
      cmd += f' --compset {compset} --res {grid} '
      cmd += f' --project {acct} --walltime {walltime} '
      if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
      if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   # Configure
   if config :
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------
      # when specifying ncdata, do it here to avoid an error message
      write_atm_nl_opts(compset,GNHS,init_file_atm)
      #-------------------------------------------------------
      if nlev is not None:
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev {nlev} \" ')
      if 'MMF' in compset:
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx {nx} -crm_ny {ny} \" ')
      #-------------------------------------------------------
      cpp_opt = ''
      if GNCT: cpp_opt += f' -DHOMME_DO_NCT'
      if doXU or doXW or doSU or doSW: cpp_opt += f' -DMMF_DO_CORIOLIS'
      if doXU: cpp_opt += f' -DMMF_DO_CORIOLIS_U'
      if doXW: cpp_opt += f' -DMMF_DO_CORIOLIS_W'
      if doSU: cpp_opt += f' -DMMF_DO_CORIOLIS_ESMT'
      if doSW: cpp_opt += f' -DMMF_DO_CORIOLIS_ESMT_W'
      if cpp_opt != '' :
         cmd  = f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS'
         cmd += f' --val \" -cppdefs \' {cpp_opt} \'  \" '
         run_cmd(cmd)
      #-------------------------------------------------------
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   # Build
   if build : 
      #-------------------------------------------------------
      if 'debug-on' in case : run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   # Write the namelist options and submit the run
   if submit : 
      #-------------------------------------------------------
      write_atm_nl_opts(compset,GNHS,init_file_atm)
      write_lnd_nl_opts(init_file_lnd,data_file_lnd)
      #-------------------------------------------------------
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      # if 'resub' in globals() and not continue_run: run_cmd(f'./xmlchange RESUBMIT={resub}')
      # if 'resub' in globals() and reset_resub: run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'resub' in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      #-------------------------------------------------------
      if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
def write_atm_nl_opts(compset,GNHS,init_file_atm):
   nfile = 'user_nl_eam'
   file = open(nfile,'w')
   file.write(' nhtfrq = 0,-3,-6 \n')
   file.write(' mfilt  = 1,8,4 \n')
   file.write('\n')
   file.write(" fincl1 = 'Z3','CLOUD','CLDLIQ','CLDICE'\n")
   file.write(          "'PSzm','Uzm','Vzm','Wzm'")
   file.write(          ",'THzm','VTHzm','WTHzm'")
   file.write(          ",'UVzm','UWzm','THphys'")
   file.write(" fincl2 = 'PS','PSL','TS'")
   file.write(          ",'PRECT','TMQ'")
   file.write(          ",'PRECC','PRECSC'")
   file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(          ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(          ",'TGCLDLWP','TGCLDIWP'")
   file.write(          ",'TBOT','QBOT'")
   file.write('\n')
   # 3D variables
   # file.write(" fincl3 = 'PS'")
   # file.write(          ",'T','Q','Z3'")                       # 3D thermodynamic budget components
   # file.write(          ",'U','V','OMEGA'")                    # 3D velocity components
   # file.write(          ",'QRL','QRS'")                        # 3D radiative heating profiles
   # file.write(          ",'CLDLIQ','CLDICE'")                  # 3D cloud fields
   # file.write('\n')
   file.write(f' phys_grid_ctem_zm_nbas = 120 \n') # Number of basis functions used for TEM
   file.write(f' phys_grid_ctem_za_nlat = 90 \n') # Number of latitude points for TEM
   file.write(f' phys_grid_ctem_nfreq = -6 \n') # Frequency of TEM diagnostic calculations (neg => hours)
   if 'MMF' in compset:
      file.write(f' mmf_orientation_angle = 0 \n') # E/W
   if GNHS:
      file.write(f' theta_hydrostatic_mode = .false. \n')
      file.write(f' tstep_type = 9 \n')
   if init_file_atm is not None:
      file.write(f' ncdata = \'{init_file_atm}\' \n')
   file.close()

#---------------------------------------------------------------------------------------------------
def write_lnd_nl_opts(init_file_lnd,data_file_lnd):
   if init_file_lnd is not None or data_file_lnd is not None:
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      if init_file_lnd is not None: file.write(f' finidat = \'{init_file_lnd}\' \n')
      if data_file_lnd is not None: file.write(f' fsurdat = \'{data_file_lnd}\' \n')
      # file.write(f' check_finidat_fsurdat_consistency = .false. \n')
      file.close()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for n in range(len(compset_list)):
      # print('-'*80)
      main( compset_list[n], \
            GNHS_list[n], GNCT_list[n], \
            doXU_list[n], doXW_list[n], doSU_list[n], doSW_list[n], \
            nx_list[n], ny_list[n], \
            nlev_list[n], \
           )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
