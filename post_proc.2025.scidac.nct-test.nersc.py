#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
unified_env = '/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh'
def print_line():print(' '*2+'-'*80)
def run_cmd(cmd):  print('\n'+clr.GREEN+cmd+clr.END); os.system(cmd);  return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, glob, datetime
# import xarray as xr
st_archive,copy_to_cfs = False,False
lt_archive_create,lt_archive_update,lt_archive_check = False,False,False
remap_h0, remap_h1, remap_h2 = False, False, False
mv_cfs,reduce_h2 = False,False
delete_all_data = False

acct = 'm4310'

# st_archive           = True
# lt_archive_create    = True
# lt_archive_update    = True
lt_archive_check  = True
# remap_h0             = True
# remap_h1             = True
# remap_h2             = True
# copy_to_cfs          = True
### mv_cfs               = True # separate h0/h1/h2 files
# reduce_h2            = True # reduce 2 size by removing CRM data
# delete_all_data          = True

zstash_log_root = '/global/homes/w/whannah/E3SM/zstash_logs'

'''
nohup time python run_post.2024-RCE-DOMAIN-TEST.perlmutter.py > RCE-DOMAIN-TEST.post.out &
'''

#-------------------------------------------------------------------------------
# case_list,root_list = [],[]
# def add_case(case,root):
#    case_list.append(case); root_list.append(root)
#-------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#-------------------------------------------------------------------------------

scratch_root_cpu = '/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu'
scratch_root_gpu = '/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu'


add_case(prefix='2025-SCIDAC-NCT-test-00',grid='ne30pg2_r05_IcoswISC30E3r5',compset='F20TR',NHS='off',NCT='off')
add_case(prefix='2025-SCIDAC-NCT-test-00',grid='ne30pg2_r05_IcoswISC30E3r5',compset='F20TR',NHS='on', NCT='off')
add_case(prefix='2025-SCIDAC-NCT-test-00',grid='ne30pg2_r05_IcoswISC30E3r5',compset='F20TR',NHS='on', NCT='on')

hpss_root = 'E3SM/2025-SCIDAC-NCT'

dst_nlat =  90
dst_nlon = 180
map_file = '/global/homes/w/whannah/maps/map_ne30pg2_to_90x180_traave.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(opts):
   root = scratch_root_cpu
   #----------------------------------------------------------------------------
   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix','compset','grid']:
         case_list.append(val)
      # elif key in ['num_nodes']:
      #    continue
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            case_list.append(f'{key}_{val:g}')

   case = '.'.join(case_list)
   case_root = f'{root}/{case}'

   # print(case); return

   #------------------------------------------------------------------------------------------------
   #------------------------------------------------------------------------------------------------
   print_line()
   print(f'  case : {clr.BOLD}{case}{clr.END} \n')
   #------------------------------------------------------------------------------------------------
   if st_archive:
      os.chdir(f'{case_root}/case_scripts')
      run_cmd(f'./xmlchange DOUT_S_ROOT={case_root}/archive ')
      run_cmd('./case.st_archive')
   #------------------------------------------------------------------------------------------------
   if lt_archive_create:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Create the HPSS archive
      run_cmd(f'source {unified_env}; zstash create --hpss={hpss_root}/{case} . 2>&1 | tee {zstash_log_root}/zstash_create_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if lt_archive_update:
      print(f'\n{clr.GREEN}cd {case_root}{clr.END}');
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      run_cmd(f'source {unified_env}; zstash update --hpss={hpss_root}/{case}  2>&1 | tee {zstash_log_root}/zstash_update_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if lt_archive_check:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Check the HPSS archive
      run_cmd(f'source {unified_env}; zstash check --hpss={hpss_root}/{case} 2>&1 | tee {zstash_log_root}/zstash_check_{case}_{timestamp}.log ')
   #------------------------------------------------------------------------------------------------
   # remap_src_sub  = 'archive/atm/hist'
   # remap_dst_sub  = f'data_remap_{dst_nlat}x{dst_nlon}'
   # remap_src_root = f'{root}/{case}/{remap_src_sub}'
   # remap_dst_root = f'{root}/{case}/{remap_dst_sub}'
   # if not os.path.exists(remap_dst_root): os.mkdir(remap_dst_root)
   # #------------------------------------------------------------------------------------------------
   # if remap_h0: remap_data( case, remap_src_root, map_file, remap_dst_root, 'h0', dst_nlat, dst_nlon )
   # if remap_h1: remap_data( case, remap_src_root, map_file, remap_dst_root, 'h1', dst_nlat, dst_nlon )
   # if remap_h2: remap_data( case, remap_src_root, map_file, remap_dst_root, 'h2', dst_nlat, dst_nlon )
   #------------------------------------------------------------------------------------------------
   # # new version with seperate folders for each history type
   # if copy_to_cfs:
   #    cfs_root = '/global/cfs/cdirs/m3312/whannah/2024-RCEMIP-DOMAIN-TEST'
   #    src_dir = f'{case_root}/archive/atm/hist'
   #    dst_root = f'{cfs_root}/{case}'
   #    if not os.path.exists(cfs_root): os.mkdir(cfs_root)
   #    if not os.path.exists(dst_root): os.mkdir(dst_root)
   #    for htype in ['h0','h1','h2']:
   #       dst_dir = f'{dst_root}/data_{htype}'
   #       if not os.path.exists(dst_dir): os.mkdir(dst_dir)
   #       run_cmd(f'cp {src_dir}/*eam.{htype}.* {dst_dir}/')
   #------------------------------------------------------------------------------------------------
   # reduce 2 size by copying and excluding CRM data
   if reduce_h2:
      cfs_root = '/global/cfs/cdirs/m3312/whannah/2024-RCEMIP-DOMAIN-TEST'
      src_dir = f'{cfs_root}/{case}/data_h2'
      dst_dir = f'{cfs_root}/{case}/data_h2_mod'
      if not os.path.exists(dst_dir):  os.mkdir(dst_dir)
      src_file_list = sorted( glob.glob(f'{src_dir}/{case}.eam.h2.*'))
      for src_file in src_file_list:
         dst_file = src_file.replace(src_dir,dst_dir)
         run_cmd(f'ncks --overwrite -x -v CRM_QPC,CRM_QPI {src_file} {dst_file}')
   # #------------------------------------------------------------------------------------------------
   # # old version
   # if copy_to_cfs:
   #    dst_root = '/global/cfs/cdirs/m3312/whannah/2024-RCEMIP-DOMAIN-TEST'
   #    src_dir = f'{case_root}/archive/atm/hist'
   #    dst_dir = f'{dst_root}/{case}'
   #    if not os.path.exists(dst_root): os.mkdir(dst_root)
   #    if not os.path.exists(dst_dir):  os.mkdir(dst_dir)
   #    run_cmd(f'cp {src_dir}/*eam.h* {dst_dir}/')
   # #------------------------------------------------------------------------------------------------
   # if mv_cfs:
   #    dst_root = '/global/cfs/cdirs/m3312/whannah/2024-RCEMIP-DOMAIN-TEST'
   #    for htype in ['h0','h1','h2']:
   #       src_dir = f'{dst_root}/{case}'
   #       dst_dir = f'{dst_root}/{case}/data_{htype}'
   #       if not os.path.exists(dst_dir): os.mkdir(dst_dir)
   #       run_cmd(f'mv {src_dir}/*eam.{htype}.* {dst_dir}/')
   #------------------------------------------------------------------------------------------------
   # # if 'delete_all_data' not in globals(): delete_all_data = False
   # if delete_all_data:
   #    file_list = []
   #    # file_list += glob.glob(f'{case_root}/post/atm/180x360/ts/monthly/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/post/atm/180x360/clim/monthly/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/post/atm/180x360/clim/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/post/atm/90x180/ts/monthly/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/post/atm/90x180/clim/monthly/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/post/atm/90x180/clim/10yr/*.nc')
   #    # file_list += glob.glob(f'{case_root}/post/atm/glb/ts/monthly/10yr/*.nc')
   #    file_list += glob.glob(f'{case_root}/archive/*/hist/*.nc')
   #    file_list += glob.glob(f'{case_root}/archive/rest/*/*.nc')
   #    file_list += glob.glob(f'{case_root}/run/*.nc')
   #    file_list += glob.glob(f'{case_root}/data_remap_90x180/*.nc')
   #    file_list += glob.glob(f'{case_root}/data_final/*_2D_*.nc')
   #    file_list += glob.glob(f'{case_root}/data_final/*_3D_*.nc')
   #    # if len(file_list)>10:
   #    #    print()
   #    #    for f in file_list: print(f)
   #    #    print()
   #    #    exit()
   #    if len(file_list)>0: 
   #       print(f'  {clr.RED}deleting {(len(file_list))} files{clr.END}')
   #       for f in file_list:
   #          os.remove(f)
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {clr.BOLD}{case}{clr.END} ')
#---------------------------------------------------------------------------------------------------
def remap_data(case,remap_src_root,map_file, remap_dst_root,htype,dst_nlat,dst_nlon):
   src_file_list = sorted( glob.glob(f'{remap_src_root}/{case}.eam.{htype}.*'))
   for src_file in src_file_list:
      dst_file = src_file.replace('.nc',f'.remap_{dst_nlat}x{dst_nlon}.nc')
      dst_file = dst_file.replace(remap_src_root,remap_dst_root)
      run_cmd(f'ncremap -m {map_file} -i {src_file} -o {dst_file}')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for n in range(len(opt_list)):
      print('-'*80)
      main( opt_list[n] )
   print_line()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
