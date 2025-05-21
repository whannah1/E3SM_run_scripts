#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, numpy as np, subprocess as sp, datetime
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
case_dir = os.getenv('HOME')+'/E3SM/Cases'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC5' # branch => ???

### flags to control config/build/submit sections
# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',1,0,'1:00:00'
# queue,stop_opt,stop_n,resub,walltime = 'regular','steps',5,0,'1:00:00'
#---------------------------------------------------------------------------------------------------
compset        = 'F2010-MMF1'
arch           = 'CRAYGPU'
ne,npg,grid    = 4,2,'ne4pg2_oQU480'

# gnz,cnz,cnx,cny,rnx,cdx,cdt,gdt_min=276,256,32,32,2,2000,10,20; nnode=12
gnz,cnz,cnx,cny,rnx,cdx,cdt,gdt_min=148,128,16,16,2,2000,1,5; nnode=12


case_list=['E3SM','GB2024-TEST-00',arch,grid,compset]
case_list.append(f'NN_{nnode}')
case_list.append(f'L{gnz}_{cnz}')
case_list.append(f'NXY_{cnx}x{cny}')
case_list.append(f'DXT_{cdx}x{cdt}')
case_list.append(f'GDT_{gdt_min}')
if debug_mode: case_list.append('debug')
case='.'.join(case_list)

print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
hiccup_scratch = '/lustre/orion/cli115/proj-shared/hannah6/HICCUP/data'
init_file_atm = f'{hiccup_scratch}/HICCUP.atm_era5.2023-10-22.ne{ne}np4.L{gnz}.nc'
#---------------------------------------------------------------------------------------------------
dtime = gdt_min*60   # GCM physics time step
num_dyn = ne*ne*6
#---------------------------------------------------------------------------------------------------
if 'CPU' in arch: max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,56,1
if 'GPU' in arch: max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,8,6#7
task_per_node = max_mpi_per_node
if 'nnode' in locals():atm_ntasks = task_per_node*nnode
#---------------------------------------------------------------------------------------------------
if newcase :
   # Check if directory already exists
   if os.path.isdir(f'{case_dir}/{case}'): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd = cmd + f' -compset {compset} -res {grid}'
   if arch=='CRAYCPU':cmd+=f' -mach frontier -compiler crayclang    -pecount {atm_ntasks}x{atm_nthrds} '
   # if arch=='CRAYGPU':cmd+=f' -mach frontier -compiler crayclanggpu -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='CRAYGPU':cmd+=f' -mach frontier-scream-gpu -compiler crayclang-scream -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUCPU' :cmd+=f' -mach frontier -compiler gnu          -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' :cmd+=f' -mach frontier -compiler gnugpu       -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   #-------------------------------------------------------
   os.chdir(f'{case_dir}/{case}/')
   run_cmd(f'./xmlchange --file env_mach_pes.xml --id MAX_TASKS_PER_NODE    --val {max_task_per_node} ')
   run_cmd(f'./xmlchange --file env_mach_pes.xml --id MAX_MPITASKS_PER_NODE --val {max_mpi_per_node} ')
else:
   os.chdir(f'{case_dir}/{case}/')
#---------------------------------------------------------------------------------------------------
if config : 
   #-------------------------------------------------------
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\'\n')
      file.close()
   #-------------------------------------------------------
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev {gnz} -crm_nz {cnz} \" ')
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dt {cdt} -crm_dx {cdx} \" ')
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx {cnx} -crm_ny {cny} \" ')
   rny = rnx if cny>1 else 1
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx_rad {rnx} -crm_ny_rad {rny} \" ')
   #-------------------------------------------------------
   cpp_opt = ' -DMMF_HYPERVISCOSITY -DMMF_SEDIMENTATION'
   if cny>1: cpp_opt += ' -DMMF_MOMENTUM_FEEDBACK'
   cmd  = f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS'
   cmd += f' --val \" -cppdefs \' {cpp_opt} \'  \" '
   run_cmd(cmd)
   #-------------------------------------------------------
   # 64_data format is needed for large output (i.e. high-res grids or CRM data)
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
   # disable MPI support on GPU
   run_cmd('./xmlchange MPICH_GPU_SUPPORT_ENABLED=0 ')
   #-------------------------------------------------------
   # Set tasks for all components
   if ne==4:
      cmd = './xmlchange --file env_mach_pes.xml '
      alt_ntask = max_mpi_per_node
      cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
      cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
      cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
      cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
      run_cmd(cmd)
   #-------------------------------------------------------
   # Run case setup
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   # init_scratch = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata'
   # run_cmd(f'./xmlchange DIN_LOC_ROOT={init_scratch} ')
   #-------------------------------------------------------
   # Query some stuff about the case
   (din_loc_root, err) = sp.Popen('./xmlquery DIN_LOC_ROOT    --value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   (config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS --value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
   ntasks_atm = None
   (ntasks_atm     , err) = sp.Popen('./xmlquery NTASKS_ATM    --value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   ntasks_atm = float(ntasks_atm)
   #-------------------------------------------------------
   # Namelist options
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   file.write(' nhtfrq    = 0,-1 \n') 
   file.write(' mfilt     = 1,24 \n') # 1-day files
   file.write(" fincl1    = 'Z3','CLOUD','CLDLIQ','CLDICE'\n")
   file.write(" fincl2    = 'PS','PSL','TS'")                      # sfc pressure and temperature
   file.write(             ",'PRECT','TMQ'")                       # precip and total column water
   file.write(             ",'LHFLX','SHFLX'")                     # surface fluxes
   file.write(             ",'FSNT','FLNT'")                       # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")                       # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")                     # clear sky heating rates for CRE
   file.write(             ",'FLUT','FSNTOA'")                     # more rad fields
   file.write(             ",'LWCF','SWCF'")                       # cloud radiative foricng
   file.write(             ",'TGCLDLWP','TGCLDIWP'")               # liq/ice water path
   file.write(             ",'CLDTOT','CLDLOW','CLDMED','CLDHGH'") # cloud fraction
   file.write(             ",'QREFHT','TREFHT'")                   # reference temperature and humidity
   file.write(             ",'TUQ','TVQ'")                         # vapor transport
   file.write(             ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   file.write(             ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   file.write(             ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   file.write(             ",'Z300:I','Z500:I'")                   # height surfaces
   file.write(             ",'OMEGA850:I','OMEGA500:I'")           # omega
   file.write(             ",'U200:I','V200:I'")                   # 200mb winds
   file.write('\n')
   if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\'\n')
   # file.write(f' crm_accel_factor = 3 \n')         # CRM acceleration factor (default is 2)
   if  cny>1: file.write(' use_mmf_esmt = .false. \n')
   if 'dyn_npes' in locals(): file.write(f' dyn_npes = {dyn_npes} \n')
   if 'dtime' in locals(): 
      file.write(f'se_tstep            = {dtime/4} \n')
      file.write(f'dt_remap_factor     = 1 \n')
      file.write(f'hypervis_subcycle   = 1 \n')
      file.write(f'dt_tracer_factor    = 4 \n')
      file.write(f'hypervis_subcycle_q = 4 \n')
   # file.write(f'disable_diagnostics = .true. \n')
   file.close()
   #-------------------------------------------------------
   run_cmd('./xmlchange REST_OPTION=never') # Disable restart file write for timing
   if 'dtime' in locals(): ncpl=86400/dtime ; run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   continue_flag = 'TRUE' if continue_run else 'False'
   run_cmd(f'./xmlchange --file env_run.xml CONTINUE_RUN={continue_flag} ')   
   #-------------------------------------------------------
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
