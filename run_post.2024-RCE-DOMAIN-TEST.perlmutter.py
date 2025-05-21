#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
'''
Below are commands to create grid and map files. 
copying and pasting all this into the terminal should work if
 - the directories ~/grids and ~/maps exist
 - NCO is installed in your path or conda environment

source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh

NE=30
SRC_GRID=ne${NE}pg2
DST_NY=180
DST_NX=360
DST_GRID=${DST_NY}x${DST_NX}

GRID_FILE_PATH=~/grids
SRC_GRID_FILE=${GRID_FILE_PATH}/${SRC_GRID}_scrip.nc
DST_GRID_FILE=${GRID_FILE_PATH}/${DST_GRID}_scrip.nc
MAP_FILE=~/maps/map_${SRC_GRID}_to_${DST_GRID}_aave.nc

# generate model grid file
GenerateCSMesh --alt --res ${NE} --file ${GRID_FILE_PATH}/ne${NE}.g
GenerateVolumetricMesh --in ${GRID_FILE_PATH}/ne${NE}.g --out ${GRID_FILE_PATH}/ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${GRID_FILE_PATH}/ne${NE}pg2.g --out ${GRID_FILE_PATH}/ne${NE}pg2_scrip.nc

# generate lat/lon grid file
ncremap -g ${DST_GRID_FILE} -G ttl="Equi-Angular grid, dimensions ${DST_GRID}, cell edges on Poles/Equator and Prime Meridian/Date Line"#latlon=${DST_NY},${DST_NX}#lat_typ=uni#lon_typ=grn_wst

# generate map file
ncremap -6 --alg_typ=aave --grd_src=$SRC_GRID_FILE --grd_dst=$DST_GRID_FILE --map=$MAP_FILE

'''
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
unified_env = '/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh'
def print_line():print(' '*2+'-'*80)
def run_cmd(cmd): 
   print('\n'+clr.GREEN+cmd+clr.END);
   os.system(cmd); 
   return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, glob, datetime
# import xarray as xr
st_archive,copy_to_cfs = False,False
lt_archive_create,lt_archive_update,lt_archive_check = False,False,False
remap_h0, remap_h1, remap_h2 = False, False, False
mv_cfs,reduce_h2 = False,False
delete_all_data = False

acct = 'm3312'

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
case_list,root_list = [],[]
def add_case(case,root):
   case_list.append(case); root_list.append(root)
#-------------------------------------------------------------------------------

scratch_root_cpu = '/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu'
scratch_root_gpu = '/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu'

# add_case('E3SM.2024-RCEMIP-DOMAIN-TEST.FRCE-MMF1_300.NX_32x1.DX_1000',  scratch_root_gpu )
add_case('E3SM.2024-RCEMIP-DOMAIN-TEST.FRCE-MMF1_300.NX_64x1.DX_1000',  scratch_root_gpu )
add_case('E3SM.2024-RCEMIP-DOMAIN-TEST.FRCE-MMF1_300.NX_128x1.DX_1000', scratch_root_gpu )
add_case('E3SM.2024-RCEMIP-DOMAIN-TEST.FRCE-MMF1_300.NX_256x1.DX_1000', scratch_root_gpu )
add_case('E3SM.2024-RCEMIP-DOMAIN-TEST.FRCE-MMF1_300.NX_32x1.DX_4000',  scratch_root_gpu )
add_case('E3SM.2024-RCEMIP-DOMAIN-TEST.FRCE-MMF1_300.NX_64x1.DX_4000',  scratch_root_gpu )
add_case('E3SM.2024-RCEMIP-DOMAIN-TEST.FRCE-MMF1_300.NX_128x1.DX_4000', scratch_root_gpu )
add_case('E3SM.2024-RCEMIP-DOMAIN-TEST.FRCE-MMF1_300.NX_256x1.DX_4000', scratch_root_gpu )


add_case('E3SM.2024-RCEMIP-DOMAIN-TEST-01.FRCE-MMF1_300.NX_32x1.DX_4000', scratch_root_gpu )
add_case('E3SM.2024-RCEMIP-DOMAIN-TEST-01.FRCE-MMF1_300.NX_64x1.DX_4000', scratch_root_gpu )
add_case('E3SM.2024-RCEMIP-DOMAIN-TEST-01.FRCE-MMF1_300.NX_128x1.DX_4000', scratch_root_gpu )
add_case('E3SM.2024-RCEMIP-DOMAIN-TEST-01.FRCE-MMF1_300.NX_256x1.DX_4000', scratch_root_gpu )

hpss_root = 'E3SM/2024-RCEMIP-DOMAIN-TEST'

dst_nlat =  90
dst_nlon = 180
map_file = '/global/homes/w/whannah/maps/map_ne30pg2_to_90x180_traave.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(case,root):
   if case is None: exit(' case argument not provided?')
   if root is None: exit(' root argument not provided?')

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
   remap_src_sub  = 'archive/atm/hist'
   remap_dst_sub  = f'data_remap_{dst_nlat}x{dst_nlon}'
   remap_src_root = f'{root}/{case}/{remap_src_sub}'
   remap_dst_root = f'{root}/{case}/{remap_dst_sub}'
   if not os.path.exists(remap_dst_root): os.mkdir(remap_dst_root)
   #------------------------------------------------------------------------------------------------
   if remap_h0: remap_data( case, remap_src_root, map_file, remap_dst_root, 'h0', dst_nlat, dst_nlon )
   if remap_h1: remap_data( case, remap_src_root, map_file, remap_dst_root, 'h1', dst_nlat, dst_nlon )
   if remap_h2: remap_data( case, remap_src_root, map_file, remap_dst_root, 'h2', dst_nlat, dst_nlon )
   #------------------------------------------------------------------------------------------------
   # new version with seperate folders for each history type
   if copy_to_cfs:
      cfs_root = '/global/cfs/cdirs/m3312/whannah/2024-RCEMIP-DOMAIN-TEST'
      src_dir = f'{case_root}/archive/atm/hist'
      dst_root = f'{cfs_root}/{case}'
      if not os.path.exists(cfs_root): os.mkdir(cfs_root)
      if not os.path.exists(dst_root): os.mkdir(dst_root)
      for htype in ['h0','h1','h2']:
         dst_dir = f'{dst_root}/data_{htype}'
         if not os.path.exists(dst_dir): os.mkdir(dst_dir)
         run_cmd(f'cp {src_dir}/*eam.{htype}.* {dst_dir}/')
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
   # if 'delete_all_data' not in globals(): delete_all_data = False
   if delete_all_data:
      file_list = []
      # file_list += glob.glob(f'{case_root}/post/atm/180x360/ts/monthly/10yr/*.nc')
      # file_list += glob.glob(f'{case_root}/post/atm/180x360/clim/monthly/10yr/*.nc')
      # file_list += glob.glob(f'{case_root}/post/atm/180x360/clim/10yr/*.nc')
      # file_list += glob.glob(f'{case_root}/post/atm/90x180/ts/monthly/10yr/*.nc')
      # file_list += glob.glob(f'{case_root}/post/atm/90x180/clim/monthly/10yr/*.nc')
      # file_list += glob.glob(f'{case_root}/post/atm/90x180/clim/10yr/*.nc')
      # file_list += glob.glob(f'{case_root}/post/atm/glb/ts/monthly/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/archive/*/hist/*.nc')
      file_list += glob.glob(f'{case_root}/archive/rest/*/*.nc')
      file_list += glob.glob(f'{case_root}/run/*.nc')
      file_list += glob.glob(f'{case_root}/data_remap_90x180/*.nc')
      file_list += glob.glob(f'{case_root}/data_final/*_2D_*.nc')
      file_list += glob.glob(f'{case_root}/data_final/*_3D_*.nc')
      # if len(file_list)>10:
      #    print()
      #    for f in file_list: print(f)
      #    print()
      #    exit()
      if len(file_list)>0: 
         print(f'  {clr.RED}deleting {(len(file_list))} files{clr.END}')
         for f in file_list:
            os.remove(f)
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

   for n in range(len(case_list)):
      print('-'*80)
      main( case=case_list[n], root=root_list[n] )
   print_line()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
