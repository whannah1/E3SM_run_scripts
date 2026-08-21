#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np, hashlib
from shutil import copy2
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
''' Notes
# defaults from case => 
# /pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/E3SM.2025-MF-test-00.ne30pg2.F20TR.NN_32/run/atm_in
  effgw_beres               =  0.35
  gw_convect_hcf            =  10.0
  hdepth_scaling_factor     =  0.50
  gw_convect_hdepth_min     = 2.5
  gw_convect_plev_src_wind  = 70000
  frontgfc                  = 1.25D-15  =>  7.4925 = 1.25e-15 * (360*111/(30*4*2)) * 3600e10
  effgw_cm                  = 1.D0
  taubgnd                   = 2.5D-3
  effgw_oro                 = 0.375

# Initial conditions - use HICCUP script: 
~/HICCUP/user_scripts/2025-SciDAC-multifidelity-create_EAM_IC_from_EAM.horz_only.py

# run this script
nohup python -u ~/E3SM/run_E3SM.2025.scidac.MF-ensemble.pilot.py > ~/E3SM/run_E3SM.2025.scidac.MF-ensemble.pilot.out &
'''
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm4310'
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # branch => whannah/scidac-2025-multifidelity

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

# disable_bfb = True

queue = 'regular' # regular / debug

# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,  0,  '2:00:00' #  1 year
stop_opt,stop_n,resub,walltime = 'ndays',365*5,1,'10:00:00' # 10 years

#---------------------------------------------------------------------------------------------------
compset        = 'F20TR'
din_loc_root   = '/global/cfs/cdirs/e3sm/inputdata'
init_root      = '/global/cfs/cdirs/m4310/whannah/E3SM/init_data/v3.LR.amip_0101/archive/rest/2000-01-01-00000'
lnd_init_file  = f'{init_root}/v3.LR.amip_0101.elm.r.2000-01-01-00000.nc'
lnd_data_root  = f'{din_loc_root}/lnd/clm2/surfdata_map'
lnd_data_file  = f'{lnd_data_root}/surfdata_0.5x0.5_simyr1850_c200609_with_TOP.nc'
lnd_luse_file  = f'{lnd_data_root}/landuse.timeseries_0.5x0.5_hist_simyr1850-2015_c240308.nc'
RUN_START_DATE = '1995-01-01'
# atm_init_file  = f'{init_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000.nc'
#---------------------------------------------------------------------------------------------------

kwargs = {'prefix':'E3SM.2025-MF0','g':'ne30'}


add_case(**kwargs,EF=0.350, CF=10.00, HD=0.500, HM=2.500, PS=700.0, FT= 7.4925, FE=1.000, OB=0.002500, OE=0.375) # v3 defaults

# add_case(**kwargs,EF=0.258, CF= 7.96, HD=1.013, HM=2.327, PS=893.9, FT=24.0591, FE=0.477, OB=0.004277, OE=0.502)
# add_case(**kwargs,EF=0.104, CF= 9.01, HD=1.449, HM=2.970, PS=617.5, FT=37.4295, FE=0.098, OB=0.005117, OE=0.267)


#---------------------------------------------------------------------------------------------------
def get_grid_stuff(opts):
   grid_short = opts['g']
   grid,num_nodes,ne = None,None,None
   if grid_short=='ne18': grid = 'ne18pg2_r05_IcoswISC30E3r5'; num_nodes=12; ne=18
   if grid_short=='ne22': grid = 'ne22pg2_r05_IcoswISC30E3r5'; num_nodes=18; ne=22
   if grid_short=='ne26': grid = 'ne26pg2_r05_IcoswISC30E3r5'; num_nodes=24; ne=26
   if grid_short=='ne30': grid = 'ne30pg2_r05_IcoswISC30E3r5'; num_nodes=32; ne=30
   if grid is None: raise ValueError(f'no valid grid details for opts[\'g\']: {opts['g']}')
   return grid_short,grid,num_nodes,ne
#---------------------------------------------------------------------------------------------------
def get_atm_init_file(opts):
   grid_short,grid,num_nodes,ne = get_grid_stuff(opts)
   alt_init_root = '/global/cfs/cdirs/m4310/whannah/files_init'
   atm_init_file = None
   if grid_short=='ne18': atm_init_file  = f'{alt_init_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000.ne18np4.20251001.nc'
   if grid_short=='ne22': atm_init_file  = f'{alt_init_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000.ne22np4.20251001.nc'
   if grid_short=='ne26': atm_init_file  = f'{alt_init_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000.ne26np4.20251001.nc'
   if grid_short=='ne30': atm_init_file  = f'{    init_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000.nc'
   if atm_init_file is None: raise ValueError('no valid atm_init_file found')
   return atm_init_file
#---------------------------------------------------------------------------------------------------
def main(opts):
   global debug_mode, compset, din_loc_root, init_root, lnd_init_file, lnd_data_root, lnd_data_file, lnd_luse_file, RUN_START_DATE

   grid_short,grid,num_nodes,ne = get_grid_stuff(opts)
   #----------------------------------------------------------------------------
   case_list = []
   for key,val in opts.items(): 
      if key in ['prefix']:
         case_list.append(val)
      # elif key in ['num_nodes']:
      #    case_list.append(f'NN_{val}')
      elif key in ['g']:
         case_list.append(grid_short)
      elif key in ['debug']:
         case_list.append('debug')
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            fmt = 'g'
            if key in ['EF','CF','HD','HM','PS','FT','FE','OB','OE']: fmt = '0.3f'
            if key=='CF':fmt='05.2f'
            if key=='PS':fmt='05.1f'
            if key=='FT':fmt='07.4f'
            if key=='OB':fmt='0.6f'
            case_list.append(f'{key}_{val:{fmt}}')

   #----------------------------------------------------------------------------
   case = '.'.join(case_list)
   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
   #----------------------------------------------------------------------------
   opts['dx'] = 360*111/(ne*4*2)
   opts['atm_init_file'] = get_atm_init_file(opts)
   #----------------------------------------------------------------------------
   print(f'\n  case : {case}\n')
   #----------------------------------------------------------------------------
   return
   #----------------------------------------------------------------------------
   max_mpi_per_node,atm_nthrds  = 128,1 
   atm_ntasks = max_mpi_per_node*num_nodes
   case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
   #------------------------------------------------------------------------------------------------
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --mach pm-cpu --pecount {atm_ntasks}x{atm_nthrds} '
      cmd += f' --case {case} --handle-preexisting-dirs u '
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --compset {compset} --res {grid} '
      cmd += f' --project {acct} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config :
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------------------------
      # when specifying ncdata, do it here to avoid an error message
      write_atm_nl_opts(opts)
      #-------------------------------------------------------------------------
      # run_cmd('./xmlchange --id CAM_CONFIG_OPTS --append --val=\'-cosp\' ')
      #-------------------------------------------------------------------------
      run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build :
      if 'debug' in opts:
         if opts['debug']: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #-------------------------------------------------------
      write_atm_nl_opts(opts)
      write_lnd_nl_opts()
      #-------------------------------------------------------------------------
      if not continue_run: run_cmd(f'./xmlchange --file env_run.xml RUN_STARTDATE={RUN_START_DATE}')
      #-------------------------------------------------------------------------
      # Set some run-time stuff
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      #-------------------------------------------------------------------------
      if 'disable_bfb' in globals() and     disable_bfb: run_cmd('./xmlchange BFBFLAG=FALSE')
      if 'disable_bfb' in globals() and not disable_bfb: run_cmd('./xmlchange BFBFLAG=TRUE')
      #-------------------------------------------------------------------------
      if     continue_run: run_cmd('./xmlchange CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------------------------
      # Submit the run
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def get_atm_nl_opts(opts):
   return f'''
 ncdata = \'{opts["atm_init_file"]}\'
 use_gw_convect_old       = .false.
 effgw_beres              = { opts["EF"]}
 gw_convect_hcf           = { opts["CF"]}
 hdepth_scaling_factor    = { opts["HD"]}
 gw_convect_hdepth_min    = { opts["HM"]}
 gw_convect_plev_src_wind = {(opts["PS"]*1e2)}
 frontgfc                 = {(opts["FT"]/(opts["dx"]*3600e10))}
 effgw_cm                 = { opts["FE"]}
 taubgnd                  = { opts["OB"]}
 effgw_oro                = { opts["OE"]}

 cosp_lite = .false.
 inithist = 'NONE'

 tropopause_output_all = .true.

 empty_htapes = .true.
 fincl1 = 'AODALL', 'AODDUST', 'AODVIS'
         ,'FLDS', 'FLNS', 'FLNSC', 'FLNT', 'FLUT'
         ,'FLUTC', 'FSDS', 'FSDSC', 'FSNS', 'FSNSC', 'FSNT', 'FSNTOA', 'FSNTOAC'
         ,'ICEFRAC', 'LANDFRAC', 'OCNFRAC'
         ,'PSL', 'PS', 'OMEGA', 'U', 'V', 'Z3', 'T', 'Q', 'RELHUM', 'O3'
         ,'TROP_Z', 'TROP_P', 'TROP_T'
         ,'TROPF_Z', 'TROPF_P', 'TROPF_T'
         ,'TROPE3D_Z', 'TROPE3D_P', 'TROPE3D_T'
         ,'PRECC', 'PRECL', 'PRECSC', 'PRECSL'
         ,'QFLX', 'SCO', 'SHFLX', 'SOLIN', 'SWCF', 'LWCF'
         ,'TAUX', 'TAUY', 'TCO', 'TGCLDLWP', 'TGCLDIWP', 'TMQ'
         ,'TS', 'TREFHT', 'TREFMNAV', 'TREFMXAV'
         ,'HDEPTH', 'MAXQ0', 'UTGWSPEC', 'BUTGWSPEC', 'UTGWORO'
         ,'PSzm','Uzm','Vzm','Wzm','THzm','VTHzm','WTHzm','UVzm','UWzm'

 phys_grid_ctem_zm_nbas = 120 ! num basis functions for TEM
 phys_grid_ctem_za_nlat =  90 ! num latitude points for TEM
 phys_grid_ctem_nfreq   =  -6 ! frequency of TEM diags (neg => hours)

'''
def write_atm_nl_opts(opts):
   file=open('user_nl_eam','w')
   file.write(get_atm_nl_opts(opts))
   file.close()
   return
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def get_lnd_nl_opts():
   global lnd_luse_file, lnd_data_file, lnd_init_file
   return f'''
 flanduse_timeseries = \'{lnd_luse_file}\'
 fsurdat = \'{lnd_data_file}\'
 finidat = \'{lnd_init_file}\'
 ! -- Reduce the size of land outputs since we dont need them --
 hist_fincl1 = 'SNOWDP'
 hist_mfilt = 1
 hist_nhtfrq = 0
 hist_avgflag_pertape = 'A'

'''
# check_dynpft_consistency = .false.
# check_finidat_year_consistency = .false.
def write_lnd_nl_opts():
   file=open('user_nl_elm','w')
   file.write(get_lnd_nl_opts())
   file.close()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
