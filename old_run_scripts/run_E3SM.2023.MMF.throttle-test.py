#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'
# src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC4' # branch => whannah/scidac-2023
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => master @ Oct 11

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

debug_mode = False

queue = 'regular'  # regular / debug 

arch = 'GNUGPU' # GNUCPU / GNUGPU

# walltime = '8:00:00'
# if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'ndays',1, 0,'0:10:00'
# if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',15,24-1,'8:00:00'
# if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',73,4,'2:00:00'
# if queue=='regular': stop_opt,stop_n,resub,walltime = 'ndays',365,5-1,'6:00:00'

ne,npg,grid = 4,2,'ne4pg2_oQU480'; num_nodes = 1
# ne,npg,grid = 30,2,'ne30pg2_EC30to60E2r2'; num_nodes = 64

# ens_num = '00' # original ensemble
# ens_num = '01' # change wmin to 0 for better mass flux diagnostics - doesn't seem to matter
ens_num = '02' # new runs to overcome issue from perlmutter maintenance - also switch to ne4


compset_list,nx_list,ny_list = [],[],[]
def add_case(compset_in,nx_in,ny_in):
   compset_list.append(compset_in)
   nx_list.append(nx_in)
   ny_list.append(ny_in)

# add_case('F2010-MMF1',  8, 1)
# add_case('F2010-MMF1', 16, 1)
# add_case('F2010-MMF1', 32, 1)
# add_case('F2010-MMF1', 64, 1)
# add_case('F2010-MMF1',128, 1)
# add_case('F2010-MMF1',256, 1)
# add_case('F2010-MMF1',512, 1)
# add_case('F2010-MMF1',  8, 4)
# add_case('F2010-MMF1', 16, 4)
# add_case('F2010-MMF1', 32, 4)
# add_case('F2010-MMF1', 64, 4)
# add_case('F2010-MMF1',128, 4)
# add_case('F2010-MMF1',256, 4)
# add_case('F2010-MMF1',512, 4)
# add_case('F2010-MMF1',  8, 8)
# add_case('F2010-MMF1', 16, 8)
# add_case('F2010-MMF1', 32, 8)
# add_case('F2010-MMF1', 64, 8)
# add_case('F2010-MMF1',128, 8)
# add_case('F2010-MMF1',256, 8)
# add_case('F2010-MMF1',512, 8)

# add_case('F2010-MMF1', 32, 32)

### focused area for resubmitting runs that have been difficult to finish
# add_case('F2010-MMF1',16,1)
# add_case('F2010-MMF1',256,1)
# add_case('F2010-MMF1',64,4)
add_case('F2010-MMF1',512,4)
# add_case('F2010-MMF1',8,8)
add_case('F2010-MMF1',64,8)
# add_case('F2010-MMF1',512,8)
# add_case('F2010-MMF1',32,32)

# add_case('FAQP-MMF1',   8, 1)
# add_case('FAQP-MMF1',  16, 1)
# add_case('FAQP-MMF1',  32, 1)
# add_case('FAQP-MMF1',  64, 1)
# add_case('FAQP-MMF1', 128, 1)
# add_case('FAQP-MMF1', 256, 1)
# add_case('FAQP-MMF1', 512, 1)
# add_case('FAQP-MMF1',   8, 4)
# add_case('FAQP-MMF1',  16, 4)
# add_case('FAQP-MMF1',  32, 4)
# add_case('FAQP-MMF1',  64, 4)
# add_case('FAQP-MMF1', 128, 4)
# add_case('FAQP-MMF1', 256, 4)
# add_case('FAQP-MMF1', 512, 4)
# add_case('FAQP-MMF1',   8, 8)
# add_case('FAQP-MMF1',  16, 8)
# add_case('FAQP-MMF1',  32, 8)
# add_case('FAQP-MMF1',  64, 8)
# add_case('FAQP-MMF1', 128, 8)
# add_case('FAQP-MMF1', 256, 8)
# add_case('FAQP-MMF1', 512, 8)


### old approach

# nx,ny=  8, 1; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny= 16, 1; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny= 32, 1; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}']) 
# nx,ny= 64, 1; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny=128, 1; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny=256, 1; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny=512, 1; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])

# nx,ny=  8, 4; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny= 16, 4; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny= 32, 4; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny= 64, 4; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny=128, 4; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny=256, 4; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny=512, 4; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])

# nx,ny=  8, 8; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny= 16, 8; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny= 32, 8; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny= 64, 8; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
### nx,ny=128, 8; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny=256, 8; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny=512, 8; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])

# nx,ny= 16,16; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny= 32, 8; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny= 64, 4; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])

# nx,ny= 32,32; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny= 64,16; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
# nx,ny=128, 8; case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])

if debug_mode: case += '.debug'

# init_path_lnd = '/global/cfs/cdirs/m4310/whannah/E3SM/init_data'
# init_case_lnd = 'ELM_spinup.ICRUELM.ne30pg2_EC30to60E2r2.20-yr.2010-01-01'
# init_file_lnd = f'{init_path_lnd}/{init_case_lnd}.elm.r.2010-01-01-00000.nc'
# data_path_lnd = '/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map'
# data_file_lnd = f'{data_path_lnd}/surfdata_ne30pg2_simyr2010_c210402.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(compset=None,nx=None,ny=None):
   
   case='.'.join(['E3SM',f'2023-THR-TEST-{ens_num}',grid,compset,f'NXY_{nx}_{ny}'])
   
   print('\n  case : '+case+'\n')

   # print(case); return # use this for printing a sorted list

   if 'CPU' in arch: max_mpi_per_node,atm_nthrds  = 128,1 ; max_task_per_node = 128
   if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   4,8 ; max_task_per_node = 32
   atm_ntasks = max_mpi_per_node*num_nodes

   if 'CPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
   if 'GPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/{case}'

   #---------------------------------------------------------------------------------------------------
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case}'
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --handle-preexisting-dirs u '
      cmd += f' --compset {compset}'
      cmd += f' --res {grid} '
      cmd += f' --project {acct} '
      cmd += f' --walltime {walltime} '
      if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
      if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
      run_cmd(cmd)
      # # Copy this run script into the case directory
      # timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
   #---------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #---------------------------------------------------------------------------------------------------
   if config :
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------
      # if specifying ncdata, do it here to avoid an error message
      if 'init_file_atm' in globals():
         file = open('user_nl_eam','w')
         file.write(f' ncdata = \'{init_file_atm}\' \n')
         file.close()
      #-------------------------------------------------------
      # file=open('user_nl_eam','w');file.write(get_atm_nl_opts(e,c,h));file.close()
      # run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev {nlev} \" ')
      # run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nz {crm_nz} \" ')
      # run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val=\'-cosp\'')
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx {nx} -crm_ny {ny} \" ')
      #-------------------------------------------------------
      # PE layout mods from Noel
      if 'CPU' in arch: cpl_stride = 8; cpl_ntasks = atm_ntasks / cpl_stride
      if 'GPU' in arch: cpl_stride = 4; cpl_ntasks = atm_ntasks / cpl_stride
      run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_CPL="{cpl_ntasks}"')
      run_cmd(f'./xmlchange --file env_mach_pes.xml PSTRID_CPL="{cpl_stride}"')
      run_cmd(f'./xmlchange --file env_mach_pes.xml ROOTPE_CPL="0"')
      #-------------------------------------------------------
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #---------------------------------------------------------------------------------------------------
   if build : 
      run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #---------------------------------------------------------------------------------------------------
   if submit : 
      #-------------------------------------------------------
      # Namelist options
      #-------------------------------------------------------
      nfile = 'user_nl_eam'
      file = open(nfile,'w') 
      #------------------------------
      # Specify history output frequency and variables
      #------------------------------
      file.write(' nhtfrq    = 0,-24 \n')
      file.write(' mfilt     = 1,5 \n')
      file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots
      file.write(          ",'CLDLIQ','CLDICE'")
      file.write(          ",'MMF_QPEVP','MMF_MC','MMF_MCUP','MMF_MCDN','MMF_MCUUP','MMF_MCUDN'")
      file.write('\n')
      file.write(" fincl2 = 'PS','TS','PSL'")
      file.write(          ",'PRECT','TMQ'")
      file.write(          ",'PRECC','PRECL'")
      file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
      file.write(          ",'FSNT','FLNT','FLUT'")        # Net TOM heating rates
      file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
      file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
      file.write(          ",'TGCLDLWP','TGCLDIWP'")       # liq & ice water path
      # file.write(          ",'TUQ','TVQ'")                 # vapor transport for AR tracking
      # variables for tracking stuff like hurricanes
      # file.write(          ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
      # file.write(          ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
      # file.write(          ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
      # file.write(          ",'Z300:I','Z500:I'")
      # file.write(          ",'OMEGA850:I','OMEGA500:I'")
      # file.write(          ",'U200:I','V200:I'")
      # file.write(          ",'MMF_MC','MMF_MCUP','MMF_MCDN','MMF_MCUUP','MMF_MCUDN'")
      file.write('\n')
      # vertically resovled quantities
      # file.write(" fincl3 = 'PS','TS','PSL'")
      # file.write(          ",'T','Q','Z3'")                      # 3D thermodynamic budget components
      # file.write(          ",'U','V','OMEGA'")                    # 3D velocity components
      # file.write(          ",'QRL','QRS'")                        # 3D radiative heating profiles
      # file.write(          ",'CLDLIQ','CLDICE'")                  # 3D cloud fields
      # file.write(          ",'UTGWORO','UTGWSPEC','BUTGWSPEC'")   # gravity wave U tendencies
      file.write('\n')

      # ,'MSKtem','VTH2d','UV2d','UW2d','U2d','V2d','TH2d','W2d' # FV TE terms
      
      #------------------------------
      # Other namelist stuff
      #------------------------------   
      # file.write(f' cosp_lite = .true. \n')
      if 'init_file_atm' in globals(): file.write(f' ncdata = \'{init_file_atm}\' \n')
      # file.write(" inithist = \'ENDOFRUN\' \n")
      file.close()
      #-------------------------------------------------------
      # LND namelist
      #-------------------------------------------------------
      if 'init_file_lnd' in globals() or 'data_file_lnd' in globals():
         nfile = 'user_nl_elm'
         file = open(nfile,'w')
         if 'init_file_lnd' in globals(): file.write(f' finidat = \'{init_file_lnd}\' \n')
         if 'data_file_lnd' in globals(): file.write(f' fsurdat = \'{data_file_lnd}\' \n')
         # file.write(f' check_finidat_fsurdat_consistency = .false. \n')
         file.close()
      #-------------------------------------------------------
      # Set some run-time stuff
      #-------------------------------------------------------
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

      if continue_run :
         run_cmd('./xmlchange CONTINUE_RUN=TRUE')   
      else:
         run_cmd('./xmlchange CONTINUE_RUN=FALSE')
      #-------------------------------------------------------
      # Submit the run
      run_cmd('./case.submit')
      #-------------------------------------------------------
      # Print the case name again
      print(f'\n  case : {case}\n') 

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for c in range(len(compset_list)):
      main( compset=compset_list[c], nx=nx_list[c], ny=ny_list[c] )
#---------------------------------------------------------------------------------------------------
