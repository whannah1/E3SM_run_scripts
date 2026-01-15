#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END); os.system(cmd); return
#---------------------------------------------------------------------------------------------------
# NOTE: The branch (whannah/scidac-2023) started 
# with master @ Aug 7 w/ v3atm/eam/master_MAM5_wetaero_chemdyg:
#     commit 915e929b5118243bc2f15b90c4ca911352985524
#     Merge: 855bd01e21 b3454bb277
#     Author: Wuyin Lin <wlin@bnl.gov>
#     Date:   Mon Aug 7 07:47:35 2023 -0700
# but also includes commits to add the hdepth_scaling_factor namelist parameter
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
create_exe,newcase,config,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm4310'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC2' # branch => whannah/scidac-2024

# create_exe   = True
# newcase      = True
# config       = True
submit       = True
# continue_run = True

num_nodes    = 22
grid         = 'ne30pg2_r05_IcoswISC30E3r5'

# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',64,0,'2:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,0,'4:00:00'
stop_opt,stop_n,resub,walltime = 'ndays',73,5-1,'4:00:00'

# ens_id = '2024-SCIDAC-PCOMP-TEST' # initial test to work out logistical issues
# ens_id = '2024-SCIDAC-PCOMP-TEST-01' # second test with alternate land/river configuration
ens_id = '2024-SCIDAC-PCOMP-TEST-02' # run cases for a year to see how QBO signal decays

#---------------------------------------------------------------------------------------------------
tmp_date_list = []
# v1
# tmp_date_list.append('1983-01-01') # phase 1 - pi*1/4
# tmp_date_list.append('1993-04-01')
# tmp_date_list.append('2002-07-01')
# tmp_date_list.append('2022-10-01')
# tmp_date_list.append('1986-10-01') # phase 2 - pi*3/4
# tmp_date_list.append('1995-07-01')
# tmp_date_list.append('2000-04-01')
# tmp_date_list.append('2009-01-01')
# tmp_date_list.append('1982-01-01') # phase 3 - pi*5/4
# tmp_date_list.append('1987-04-01')
# tmp_date_list.append('2014-07-01')
# tmp_date_list.append('2021-10-01')
# tmp_date_list.append('1984-10-01') # phase 4 - pi*7/4
# tmp_date_list.append('1994-07-01')
# tmp_date_list.append('2006-04-01')
# tmp_date_list.append('2013-01-01')
# v2
# tmp_date_list.append('1983-01-01') # phase 1 - pi*1/4
# tmp_date_list.append('1993-04-01')
# tmp_date_list.append('2004-05-01')
# tmp_date_list.append('2022-10-01')
# tmp_date_list.append('1985-11-01') # phase 2 - pi*3/4
# tmp_date_list.append('1991-04-01')
# tmp_date_list.append('2000-01-01')
# tmp_date_list.append('2011-07-01')
tmp_date_list.append('1984-01-01') # phase 3 - pi*5/4
# tmp_date_list.append('2001-04-01')
# tmp_date_list.append('2005-07-01')
# tmp_date_list.append('2021-11-01')
# tmp_date_list.append('1987-07-01') # phase 4 - pi*7/4
# tmp_date_list.append('1994-10-01')
# tmp_date_list.append('2008-01-01')
# tmp_date_list.append('2015-04-01')
#---------------------------------------------------------------------------------------------------
gweff_list, cfrac_list, hdpth_list = [],[],[]
start_date_list = []
def add_case(e,c,h,d):
   gweff_list.append(e)
   cfrac_list.append(c)
   hdpth_list.append(h)
   start_date_list.append(d)
#---------------------------------------------------------------------------------------------------
# tdate = '1983-01-01'
# add_case(e=0.35,c=10,h=0.50,d=tdate) #  <<< v3 default
# add_case(e=0.12,c=16,h=0.48,d=tdate) # prev surrogate optimum
# tdate = '1993-04-01'
# add_case(e=0.35,c=10,h=0.50,d=tdate) #  <<< v3 default
# add_case(e=0.12,c=16,h=0.48,d=tdate) # prev surrogate optimum
#---------------------------------------------------------------------------------------------------
for date in tmp_date_list:
   add_case(e=0.35,c=10,h=0.50,d=date) #  <<< v3 default
   add_case(e=0.12,c=16,h=0.48,d=date) # prev surrogate optimum
   add_case(e=0.09,c=20,h=0.25,d=date) # no QBO at all
   add_case(e=0.70,c=21,h=0.31,d=date) # QBO is too fast
#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
def get_case_root(case): return f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
#---------------------------------------------------------------------------------------------------
def get_ntasks(): return num_nodes*128
def get_nthrds(): return 1
#---------------------------------------------------------------------------------------------------
def get_compset():
   # return 'F20TR' # this is problematic due to BGC and MOSART being on by default
   return '20TR_EAM%CMIP6_ELM%SPBCTOP_MPASSI%PRES_DOCN%DOM_SROF_SGLC_SWAV_SIAC_SESP'
#---------------------------------------------------------------------------------------------------
def get_exe_case_name(): 
   return '.'.join(['E3SM',ens_id,grid,'EXE'])
#---------------------------------------------------------------------------------------------------
def get_case_name(start_date,e,c,h): 
   return '.'.join(['E3SM',ens_id,grid,f'EF_{e:0.2f}',f'CF_{c:02.0f}',f'HD_{h:0.2f}',f'{start_date}'])
#---------------------------------------------------------------------------------------------------
def create_ens_exe():
   case = get_exe_case_name()
   # print(case); exit()
   case_root = get_case_root(case)
   #----------------------------------------------------------------------------
   print('\n  case : '+case+'\n')
   #----------------------------------------------------------------------------
   # Check if directory already exists   
   if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase'
   cmd += f' --case {case}'
   cmd += f' --output-root {case_root} '
   cmd += f' --script-root {case_root}/case_scripts '
   cmd += f' --handle-preexisting-dirs u '
   cmd += f' --compset {get_compset()}'
   cmd += f' --res {grid} '
   cmd += f' --machine pm-cpu '
   cmd += f' --pecount {get_ntasks()}x{get_nthrds()} '
   cmd += f' --project {acct} '
   run_cmd(cmd)
   #----------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #----------------------------------------------------------------------------
   run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
   run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
   run_cmd('./case.setup --reset')
   #----------------------------------------------------------------------------
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
   #----------------------------------------------------------------------------
   return
#---------------------------------------------------------------------------------------------------
def create_ens_member(start_date=None,e=None,c=None,h=None):
   if start_date is None or h is None or c is None or e is None: exit(' one or more arguments not provided?')

   # case = '.'.join(['E3SM',ens_id,grid,f'EF_{e:0.2f}',f'CF_{c:02.0f}',f'HD_{h:0.2f}',f'{start_date}'])

   case_name = get_case_name(start_date,e,c,h)
   case_root = get_case_root(case_name)

   # print(case); return
   
   #----------------------------------------------------------------------------
   print('\n  case : '+case_name+'\n')
   #----------------------------------------------------------------------------
   if newcase:
      # Check if directory already exists   
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case_name}'
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --handle-preexisting-dirs u '
      cmd += f' --compset {get_compset()}'
      cmd += f' --res {grid} '
      cmd += f' --machine pm-cpu '
      cmd += f' --pecount {get_ntasks()}x{get_nthrds()} '
      cmd += f' --project {acct} '
      run_cmd(cmd)
   #----------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #----------------------------------------------------------------------------
   if config:
      exe_root = get_case_root( get_exe_case_name() )
      run_cmd(f'./xmlchange EXEROOT={exe_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      run_cmd('./case.setup --reset')
      run_cmd(f'./xmlchange BUILD_COMPLETE=TRUE ')
   #----------------------------------------------------------------------------
   if submit : 
      write_atm_nl(start_date,e,c,h)
      write_lnd_nl(start_date)
      run_cmd(f'./xmlchange RUN_STARTDATE={start_date}')
      #-------------------------------------------------------
      sst_data_root = '/global/cfs/projectdirs/m4310/whannah/2024-QBO-PCOMP/files_init_sst'
      sst_data_file = f'{sst_data_root}/HICCUP.sst_noaa.{start_date}.nc'
      sst_data_year = int(start_date.split('-')[0])
      din_loc_root  = '/global/cfs/cdirs/e3sm/inputdata'
      # sst_grid_file = f'{din_loc_root}/ocn/docn7/domain.ocn.360x720.201027.nc'
      sst_grid_file = f'{din_loc_root}/ocn/docn7/domain.ocn.1x1.111007.nc'
      run_cmd(f'./xmlchange --file env_run.xml  SSTICE_DATA_FILENAME={sst_data_file}')
      run_cmd(f'./xmlchange --file env_run.xml  SSTICE_YEAR_ALIGN={sst_data_year}')
      run_cmd(f'./xmlchange --file env_run.xml  SSTICE_YEAR_START={sst_data_year}')
      run_cmd(f'./xmlchange --file env_run.xml  SSTICE_YEAR_END={(sst_data_year+1)}')
      run_cmd(f'./xmlchange --file env_run.xml  SSTICE_GRID_FILENAME={sst_grid_file}')
      #-------------------------------------------------------
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      #-------------------------------------------------------
      if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------
      run_cmd('./case.submit')
   #----------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case_name}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def write_atm_nl(start_date,gweff,cfrac,hdpth):
   atm_init_root = '/global/cfs/projectdirs/m4310/whannah/2024-QBO-PCOMP/files_init_atm'
   atm_init_file = f'{atm_init_root}/HICCUP.atm_era5.{start_date}.ne30np4.L80.nc'
   file=open('user_nl_eam','w')
   file.write(f" ncdata = '{atm_init_file}' \n")
   file.write(f" effgw_beres           = {gweff} \n")
   file.write(f" gw_convect_hcf        = {cfrac} \n")
   file.write(f" hdepth_scaling_factor = {hdpth} \n")
   file.write(" inithist = 'NONE' \n")
   # file.write(" cosp_lite = .true.")
   file.write(" empty_htapes = .true. \n")
   file.write(" avgflag_pertape = 'A','A','I','A' \n")
   file.write(" nhtfrq = 0,-6,-6 \n")
   file.write(" mfilt  = 1,4,4 \n")
   file.write(" fincl1 = 'AODALL', 'AODDUST', 'AODVIS'")
   # file.write(         ",'CLDHGH_CAL', 'CLDLOW_CAL', 'CLDMED_CAL'")
   # file.write(         ",'CLD_MISR', 'CLDTOT_CAL', 'CLMODIS', 'FISCCP1_COSP'")
   file.write(         ",'FLDS', 'FLNS', 'FLNSC', 'FLNT', 'FLUT'")
   file.write(         ",'FLUTC', 'FSDS', 'FSDSC', 'FSNS', 'FSNSC', 'FSNT', 'FSNTOA', 'FSNTOAC'")
   file.write(         ",'ICEFRAC', 'LANDFRAC', 'OCNFRAC'")
   file.write(         ",'PS','U','V','OMEGA','Z3','T','Q','BUTGWSPEC'")
   file.write(         ",'PRECC','PRECL','PRECSC','PRECSL'")
   file.write(         ",'QFLX','SCO','SHFLX','SOLIN','SWCF','LWCF'")
   file.write(         ",'TAUX','TAUY','TCO','TGCLDLWP','TGCLDIWP','TMQ'")
   file.write(         ",'TS', 'TREFHT', 'TREFMNAV', 'TREFMXAV'")
   file.write("\n")
   file.write(" fincl2 = 'PS:A','U:A','V:A','OMEGA:A','Z3:A','T:A','Q:A','BUTGWSPEC:A' \n")
   file.write(" fincl3 = 'PS:I','U:I','V:I','OMEGA:I','Z3:I','T:I','Q:I','BUTGWSPEC:I' \n")
   file.write(" fincl4 = 'Uzm','Vzm','Wzm','THzm','VTHzm','WTHzm','UVzm','UWzm','THphys','PSzm' \n")
   file.write(f' phys_grid_ctem_zm_nbas = 120 \n') # Number of basis functions used for TEM
   file.write(f' phys_grid_ctem_za_nlat = 90 \n') # Number of latitude points for TEM
   file.write(f' phys_grid_ctem_nfreq = -1 \n') # Frequency of TEM diagnostic calculations (neg => hours)
   file.close()
   return
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def write_lnd_nl(start_date):
   din_loc_root = '/global/cfs/cdirs/e3sm/inputdata'
   lnd_data_root = f'{din_loc_root}/lnd/clm2/surfdata_map'
   lnd_data_file = f'{lnd_data_root}/surfdata_0.5x0.5_simyr1850_c200609_with_TOP.nc'
   # lnd_spinup_case = 'ELM_spinup.2024-SCIDAC.ICRUELM.ne30pg2_r05_IcoswISC30E3r5.44-yr.2024-01-01'
   lnd_spinup_case = 'ELM_spinup.2024-SCIDAC.ICRUELM-SP.ne30pg2_r05_IcoswISC30E3r5.44-yr.2024-01-01'
   lnd_init_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{lnd_spinup_case}/run' # <<< temporary
   # lnd_init_root = '/global/cfs/projectdirs/m4310/whannah/2024-QBO-PCOMP/files_init_lnd'
   # lnd_init_file = f'{lnd_init_root}/{lnd_spinup_case}.elm.r.{start_date}-00000.nc'
   #----------------------------------------------------------------------------
   # use "adjusted" start date for land IC due to lack of restart files for all months
   lnd_start_date = start_date
   if '-02-01' in start_date: lnd_start_date = lnd_start_date.replace('-02-01','-01-01')
   if '-05-01' in start_date: lnd_start_date = lnd_start_date.replace('-05-01','-04-01')
   if '-08-01' in start_date: lnd_start_date = lnd_start_date.replace('-08-01','-07-01')
   if '-11-01' in start_date: lnd_start_date = lnd_start_date.replace('-11-01','-10-01')
   lnd_init_file = f'{lnd_init_root}/{lnd_spinup_case}.elm.r.{lnd_start_date}-00000.nc'
   #----------------------------------------------------------------------------
   file=open('user_nl_elm','w')
   file.write(f" fsurdat = \'{lnd_data_file}\' \n")
   file.write(f" finidat = \'{lnd_init_file}\' \n")
   file.close()
   return
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   if create_exe:
      create_ens_exe()

   if any([newcase,config,submit]):
      for n in range(len(start_date_list)):
         print('-'*80)
         create_ens_member( start_date_list[n], e=gweff_list[n], c=cfrac_list[n], h=hdpth_list[n] )   
      
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
