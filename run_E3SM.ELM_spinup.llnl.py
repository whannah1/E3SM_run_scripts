#!/usr/bin/env python3

## commands for creating ROF map files
'''
scp whannah@dtn01.nersc.gov:/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids/SCRIPgrid_0.125x0.125_nomask_c170126.nc /usr/gdata/e3sm/ccsm3data/inputdata/lnd/clm2/mappingdata/grids/

GRID_ROOT=/p/lustre1/hannah6/2024-nimbus-iraq-data/files_grid
MAP_ROOT=/p/lustre1/hannah6/2024-nimbus-iraq-data/files_map
# ROF_GRID=/usr/gdata/e3sm/ccsm3data/inputdata/lnd/clm2/mappingdata/grids/SCRIPgrid_0.125x0.125_nomask_c170126.nc
ROF_GRID=${GRID_ROOT}/SCRIPgrid_0.125x0.125_nomask_c20240701.nc

ncremap -g ${ROF_GRID} -G latlon=1440,2880#lat_typ=uni#lon_typ=180_wst # "r0125" ELM/MOSART 0.125x0.125 1/8 degree uniform grid

ncremap -a traave --src_grd=${GRID_ROOT}/2024-nimbus-iraq-32x3_pg2_scrip.nc  --dst_grd=${ROF_GRID} --map_file=${MAP_ROOT}/map_2024-nimbus-iraq-32x3_to_r0125_traave.20240701.nc
ncremap -a traave --src_grd=${GRID_ROOT}/2024-nimbus-iraq-64x3_pg2_scrip.nc  --dst_grd=${ROF_GRID} --map_file=${MAP_ROOT}/map_2024-nimbus-iraq-64x3_to_r0125_traave.20240701.nc
ncremap -a traave --src_grd=${GRID_ROOT}/2024-nimbus-iraq-128x3_pg2_scrip.nc --dst_grd=${ROF_GRID} --map_file=${MAP_ROOT}/map_2024-nimbus-iraq-128x3_to_r0125_traave.20240701.nc

ncremap -a traave --src_grd=${ROF_GRID} --dst_grd=${GRID_ROOT}/2024-nimbus-iraq-32x3_pg2_scrip.nc  --map_file=${MAP_ROOT}/map_r0125_to_2024-nimbus-iraq-32x3_traave.20240701.nc
ncremap -a traave --src_grd=${ROF_GRID} --dst_grd=${GRID_ROOT}/2024-nimbus-iraq-64x3_pg2_scrip.nc  --map_file=${MAP_ROOT}/map_r0125_to_2024-nimbus-iraq-64x3_traave.20240701.nc
ncremap -a traave --src_grd=${ROF_GRID} --dst_grd=${GRID_ROOT}/2024-nimbus-iraq-128x3_pg2_scrip.nc --map_file=${MAP_ROOT}/map_r0125_to_2024-nimbus-iraq-128x3_traave.20240701.nc
'''
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
'''
DATA_ROOT=/p/lustre1/hannah6/2024-nimbus-iraq-data
ncdump -h ${DATA_ROOT}/files_fsurdat_ne32/surfdata_2024-nimbus-iraq-32x3-pg2_simyr2010_c240701.nc   | grep "gridcell =" 
ncdump -h ${DATA_ROOT}/files_fsurdat_ne64/surfdata_2024-nimbus-iraq-64x3-pg2_simyr2010_c240701.nc   | grep "gridcell =" 
ncdump -h ${DATA_ROOT}/files_fsurdat_ne128/surfdata_2024-nimbus-iraq-128x3-pg2_simyr2010_c240701.nc | grep "gridcell =" 
32     74112  
64    261024  
128   993744  
print( 74112/(112*8))       82.7
print(261024/(112*16))     145.6

print(993744/(112*64))     138.6
print(993744/(112*128))     69.3
print(993744/(112*256))     34.6
'''
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, datetime
newcase,config,build,clean,submit,continue_run,debug = False,False,False,False,False,False,False

acct = 'nhclilab'

src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # branch => whannah/2024-nimbus-iraq

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

debug = False


# stop_opt,stop_n,resub,walltime = 'nyears',5, 0,'2:00:00'
# stop_opt,stop_n,resub,walltime = 'nyears',1, 0, '4:00:00'
# stop_opt,stop_n,resub,walltime = 'nyears',1, 20-1,'4:00:00'
# stop_opt,stop_n,resub,walltime = 'nyears',2, 10-1,'4:00:00'
# stop_opt,stop_n,resub,walltime = 'nyears',1, 0,'2:00:00'

walltime = '8:00:00'

compset = 'ICRUELM'
# compset = 'IGSWELM'


# bne=32;  num_nodes=8; dtime=30*60
# bne=64;  num_nodes=16; dtime=30*60 #; resub = resub-8
bne=128; num_nodes=128; dtime=30*60


grid=f'ne0np4-2024-nimbus-iraq-{bne}x3-pg2'; 
data_root = '/p/lustre1/hannah6/2024-nimbus-iraq-data'
fsurdat_path     = f'{data_root}/files_fsurdat_ne{bne}/surfdata_2024-nimbus-iraq-{bne}x3-pg2_simyr2010_c240701.nc'
map_file_lnd2rof = f'{data_root}/files_map/map_2024-nimbus-iraq-{bne}x3_to_r0125_traave.20240701.nc'
map_file_rof2lnd = f'{data_root}/files_map/map_r0125_to_2024-nimbus-iraq-{bne}x3_traave.20240701.nc'

#  74112 /  8 =   9264   / 112 =  82.7
# 993744 / 32 =  31054.5 / 112 = 277.3
# 993744 / 64 = 15527.25 / 112 = 138.6

num_years = 20
stop_date = datetime.datetime(2015, 10, 1)
start_date = datetime.datetime(stop_date.year-num_years, stop_date.month, stop_date.day)
stop_date_str = stop_date.strftime("%Y-%m-%d")
start_date_str = start_date.strftime("%Y-%m-%d")
rest_opt,rest_n = 'nyears',1


case = f'ELM_spinup.{compset}.{grid}.{num_years}-yr.{stop_date_str}'

if debug: case += '.debug'

#-------------------------------------------------------------------------------
def write_namelist_atm():
   # nfile = ''
   # nfile = 'user_nl_datm'
   # file = open(nfile,'w') 
   # file.write(' empty_htapes = .true. \n') 
   return
#-------------------------------------------------------------------------------
def write_namelist_lnd():
   nfile = ''
   nfile = 'user_nl_elm'
   file = open(nfile,'w') 
   file.write(f' fsurdat = \'{fsurdat_path}\' \n')
   file.close()
   return
#-------------------------------------------------------------------------------
def write_namelist_all():
   write_namelist_atm()
   write_namelist_lnd()
   return
#-------------------------------------------------------------------------------
def xml_check_and_set(file_name,var_name,value):
   if var_name in open(file_name).read(): 
      run_cmd('./xmlchange --file '+file_name+' '+var_name+'='+str(value) )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

max_mpi_per_node = 112
atm_ntasks,atm_nthrds = num_nodes*max_mpi_per_node,2

case_root = f'/p/lustre2/hannah6/e3sm_scratch/{case}'

#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase '
   cmd += f' --case {case}'
   cmd += f' --output-root {case_root} '
   cmd += f' --script-root {case_root}/case_scripts '
   cmd += f' --handle-preexisting-dirs u '
   cmd += f' --compset {compset} --res {grid} '
   cmd += f' --project {acct} '
   # cmd += f' --walltime {walltime} '
   cmd += f' -mach dane -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)

   os.chdir(f'{case_root}/case_scripts')
   run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
   run_cmd(f'./xmlchange RUNDIR={case_root}/run ')

   run_cmd(f'./xmlchange --file env_run.xml LND2ROF_FMAPNAME={map_file_lnd2rof}' )
   run_cmd(f'./xmlchange --file env_run.xml ROF2LND_FMAPNAME={map_file_rof2lnd}' )
   run_cmd(f'./xmlchange --file env_run.xml ATM2ROF_FMAPNAME={map_file_lnd2rof}' )
   run_cmd(f'./xmlchange --file env_run.xml ATM2ROF_SMAPNAME={map_file_lnd2rof}' )
   
#------------------------------------------------------------------------------------------------
os.chdir(f'{case_root}/case_scripts')
#---------------------------------------------------------------------------------------------------
if config : 
   write_namelist_all()
   #----------------------------------------------------------------------------   
   clm_opt = ' -bgc sp -clm_start_type arb_ic'
   run_cmd(f'./xmlchange --append --file env_run.xml --id ELM_BLDNML_OPTS  --val  \"{clm_opt}\"' )
   #----------------------------------------------------------------------------
   # Set tasks for non-land components   
   cmd = './xmlchange --file env_mach_pes.xml '
   alt_ntask = max_mpi_per_node*1
   cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
   cmd += f',NTASKS_ATM={alt_ntask},NTASKS_CPL={alt_ntask}'
   cmd += f',NTASKS_ROF={max_mpi_per_node},NTASKS_WAV={max_mpi_per_node}'
   cmd += f',NTASKS_GLC={max_mpi_per_node},NTASKS_ESP=1,NTASKS_IAC=1'
   run_cmd(cmd)
   #----------------------------------------------------------------------------
   # Set threads for non-land components
   cmd = './xmlchange --file env_mach_pes.xml '
   alt_nthrds = 1
   cmd += f'NTHRDS_OCN={alt_nthrds},NTHRDS_ICE={alt_nthrds}'
   cmd += f',NTHRDS_ATM={alt_nthrds},NTHRDS_CPL={alt_nthrds}'
   cmd += f',NTHRDS_ROF=1,NTHRDS_WAV=1,NTASKS_GLC=1'
   cmd += f',NTHRDS_ESP=1,NTHRDS_IAC=1'
   run_cmd(cmd)
   #----------------------------------------------------------------------------
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
   #----------------------------------------------------------------------------
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   if debug: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   inputdata_root = '/p/lustre1/hannah6/inputdata'
   run_cmd(f'./xmlchange DIN_LOC_ROOT=\'{inputdata_root}\' ')
   run_cmd(f'./xmlchange DIN_LOC_ROOT_CLMFORC=\'{inputdata_root}/atm/datm7\' ')
   #-------------------------------------------------------
   write_namelist_all()
   #-------------------------------------------------------
   # Set some run-time stuff
   if 'dtime' in locals(): 
      ncpl = 86400/dtime
      run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   # if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   
   # Restart Frequency
   run_cmd(f'./xmlchange --file env_run.xml  REST_OPTION={rest_opt}')
   run_cmd(f'./xmlchange --file env_run.xml  REST_N={rest_n}')

   xml_check_and_set('env_workflow.xml','CHARGE_ACCOUNT',acct)
   xml_check_and_set('env_workflow.xml','PROJECT',acct)

   # An alternate grid checking threshold is needed for ne120pg2 (still not sure why...)
   # if ne==120 and npg==2 : run_cmd('./xmlchange --file env_run.xml  EPS_AGRID=1e-11' )
   # run_cmd('./xmlchange --file env_run.xml EPS_FRAC=3e-2' ) # default=1e-2

   if continue_run :
      run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
   else:
      run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
   #-------------------------------------------------------
   # Submit the run
   if 'walltime' in globals(): 
      run_cmd(f'./case.submit -a="-t {walltime}" ')
   else:
      run_cmd(f'./case.submit')

#---------------------------------------------------------------------------------------------------
# Print the case name again
print('\n  case : '+case+'\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
