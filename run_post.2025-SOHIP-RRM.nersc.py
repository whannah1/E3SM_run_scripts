#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
'''
ssh whannah@dtn02.nersc.gov
screen -r
bash
source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh
nohup python -u ~/E3SM/run_post.2025-SOHIP-RRM.nersc.py > ~/E3SM/run_post.2025-SOHIP-RRM.nersc.py.lt_archive_create.out &

screen -list
screen -d 3359648.pts-44.dtn02

lt_archive_create for x2 runs- started dec 23 2025
lt_archive_create for ptgnia x3 run - started jan 07 2026
'''
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, glob, datetime, sys
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
unified_env = '/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh'
def print_line():print(' '*2+'-'*80)
def run_cmd(cmd): 
   print('\n  '+clr.GREEN+cmd+clr.END);
   os.system(cmd); 
   return
#---------------------------------------------------------------------------------------------------
chk_files,cp_post_to_cfs = False,False
lt_archive_create,lt_archive_check,lt_archive_ls,lt_archive_update = False,False,False,False

acct = 'm4842'

# chk_files         = True
# cp_post_to_cfs    = True
lt_archive_create = True
# lt_archive_check  = True
# lt_archive_ls     = True; zstash_ls_str = 'archive/atm/hist/*eam.h0.2004-12.nc'
# lt_archive_update = True
# delete_data       = True

zstash_log_root = '/global/homes/w/whannah/E3SM/zstash_logs'
# scratch_root = '/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu'
scratch_root = '/pscratch/sd/w/whannah/scream_scratch/pm-gpu'
# cfs_root = '/global/cfs/cdirs/???'
hpss_root = '/home/w/whannah/E3SM/2025-SOHIP-RRM'

#---------------------------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------

# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x2-ptgnia-v1', init_date='2023-06-13', init_hour='19' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x2-sw-ind-v1', init_date='2023-06-12', init_hour='06' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x2-se-pac-v1', init_date='2023-06-12', init_hour='16' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x2-sc-pac-v1', init_date='2023-06-14', init_hour='15' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x2-eq-ind-v1', init_date='2023-06-19', init_hour='09', num_nodes=420 )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x2-eq-ind-v1', init_date='2023-06-21', init_hour='02', num_nodes=420 )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x2-sc-ind-v1', init_date='2023-06-21', init_hour='09' )

add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x3-ptgnia-v1', init_date='2023-06-13', init_hour='19' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x3-sw-ind-v1', init_date='2023-06-12', init_hour='06' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x3-se-pac-v1', init_date='2023-06-12', init_hour='16' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x3-sc-pac-v1', init_date='2023-06-14', init_hour='15' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x3-eq-ind-v1', init_date='2023-06-19', init_hour='09' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x3-eq-ind-v1', init_date='2023-06-21', init_hour='02' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x3-sc-ind-v1', init_date='2023-06-21', init_hour='09' )
#---------------------------------------------------------------------------------------------------
def get_grid_name(opts):
   grid_name = opts['grid'].replace('2025-sohip-','')
   return grid_name
#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   case_list = []
   for key,val in opts.items(): 
      if   key in ['prefix']:    case_list.append(val)
      elif key in ['compset']:   case_list.append(val)
      elif key in ['grid']:      case_list.append(get_grid_name(opts))
      elif key in ['init_date']: case_list.append(val)
      elif key in ['init_hour']: case_list.append(val)
      elif key in ['num_nodes']: case_list.append(f'NN_{val}')
      else:
         if isinstance(val,str): case_list.append(f'{key}_{val}')
         else:                   case_list.append(f'{key}_{val:g}')
   case = '.'.join(case_list)
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}') # clean up the exponential numbers
   return case
#---------------------------------------------------------------------------------------------------
def get_case_root(opts):
   case = get_case_name(opts)
   root = f'{scratch_root}/{case}'
   return root
#---------------------------------------------------------------------------------------------------
def get_cfs_case_root(opts):
   case = get_case_name(opts)
   root = f'{cfs_root}/{case}'
   return root
#---------------------------------------------------------------------------------------------------
def main(opts):
   #------------------------------------------------------------------------------------------------
   if 'g' in opts:
      grid_short = opts['g']
      if grid_short=='ne18': grid = 'ne18pg2_r05_IcoswISC30E3r5'; num_nodes=12; ne=18
      if grid_short=='ne22': grid = 'ne22pg2_r05_IcoswISC30E3r5'; num_nodes=18; ne=22
      if grid_short=='ne26': grid = 'ne26pg2_r05_IcoswISC30E3r5'; num_nodes=24; ne=26
      if grid_short=='ne30': grid = 'ne30pg2_r05_IcoswISC30E3r5'; num_nodes=32; ne=30
   #----------------------------------------------------------------------------
   case = get_case_name(opts)
   case_root = get_case_root(opts)
   #------------------------------------------------------------------------------------------------
   print_line()
   print(f'  case_name : {clr.BOLD}{case}{clr.END}')
   print(f'  case_root : {clr.BOLD}{case_root}{clr.END}')
   #------------------------------------------------------------------------------------------------
   # return
   #------------------------------------------------------------------------------------------------
   if lt_archive_create:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Create the HPSS archive
      run_cmd(f'source {unified_env}; zstash create --hpss={hpss_root}/{case} . 2>&1 | tee {zstash_log_root}/zstash_{case}_create_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if lt_archive_check:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Check the HPSS archive
      run_cmd(f'source {unified_env}; zstash check --hpss={hpss_root}/{case} 2>&1 | tee {zstash_log_root}/zstash_{case}_check_{timestamp}.log ')
   #------------------------------------------------------------------------------------------------
   if lt_archive_ls:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Check the HPSS archive
      run_cmd(f'source {unified_env}; zstash ls --hpss={hpss_root}/{case} "{zstash_ls_str}" ')
   #------------------------------------------------------------------------------------------------
   if lt_archive_update:
      print(f'\n{clr.GREEN}cd {case_root}{clr.END}');
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      run_cmd(f'source {unified_env}; zstash update --hpss={hpss_root}/{case}  2>&1 | tee {zstash_log_root}/zstash_{case}_update_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   # if cp_post_to_cfs:
   #    # os.umask(511)
   #    dst_dir = get_cfs_case_root(opts)
   #    if not os.path.exists(cfs_root): os.mkdir(cfs_root)
   #    if not os.path.exists(dst_dir):  os.mkdir(dst_dir)
   #    src_dir = f'{case_root}/post/atm/90x180/ts/monthly/{nyr}yr'
   #    run_cmd(f'cp {src_dir}/U_* {dst_dir}/')
   #    src_dir = f'{case_root}/post/atm/90x180/clim/{nyr}yr/'
   #    run_cmd(f'cp {src_dir}/{case}_ANN_199501_199912_climo.nc {dst_dir}/')
   #    # run_cmd(f'cp {case_root}/{case}.hovmoller.nc {dst_dir}/')
   #------------------------------------------------------------------------------------------------
   # if delete_data:
   #    file_list = []
   #    # file_list += glob.glob(f'{case_root}/post/atm/180x360/ts/monthly/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/post/atm/180x360/clim/monthly/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/post/atm/180x360/clim/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/post/atm/90x180/ts/monthly/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/post/atm/90x180/clim/monthly/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/post/atm/90x180/clim/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/post/atm/glb/ts/monthly/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/archive/*/hist/*.nc')
   #    file_list += glob.glob(f'{case_root}/archive/lnd/hist/*.nc')
   #    # file_list += glob.glob(f'{case_root}/archive/rest/*/*.nc')
   #    # file_list += glob.glob(f'{case_root}/run/*.nc')
   #    #-------------------------------------------------------------------------
   #    # if len(file_list)>10:
   #    #    print()
   #    #    for f in file_list[:10]: print(f)
   #    #    print()
   #    #    exit()
   #    #-------------------------------------------------------------------------
   #    # if len(file_list)>0: 
   #    #    print(f'  {clr.RED}deleting {(len(file_list))} files{clr.END}')
   #    #    for f in file_list:
   #    #       os.remove(f)
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {clr.BOLD}{case}{clr.END} ')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   
   if chk_files:
      for n in range(len(opt_list)):
         opts = opt_list[n]
         case_name = get_case_name(opts)
         case_root = get_case_root(opts)
         hist_file_list = sorted(glob.glob(f'{case_root}/run/*.eam.h0.*'))
         last_file = hist_file_list[-1].replace(f'{case_root}/run/','')
         num_files = len(hist_file_list)
         print(f'  {(n+1):3}  {case_name}  num_files: {num_files:5}  {clr.GREEN}{last_file}{clr.END}')
      exit()

   for n in range(len(opt_list)):
      main( opt_list[n] )

   # for n in range(len(case_list)):
   #    # print_line()
   #    main( case=case_list[n], nyr=nyr_list[n], 
   #          gweff=gweff_list[n], 
   #          cfrac=cfrac_list[n], 
   #          hdpth=hdpth_list[n], 
   #          hdpth_min=hdpth_min_list[n], 
   #          stspd_min=stspd_min_list[n], 
   #          plev_srcw=plev_srcw_list[n], 
   #        )
   print_line()
   
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
