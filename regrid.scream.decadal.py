#!/usr/bin/env python3
import sys,os,glob,subprocess as sp
class tcolor: ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
#---------------------------------------------------------------------------------------------------
'''
GRID_ROOT=/lustre/orion/cli115/proj-shared/hannah6/files_grid
MAPS_ROOT=/lustre/orion/cli115/proj-shared/hannah6/files_map

NE=256

GenerateCSMesh --alt --res ${NE} --file ${GRID_ROOT}/ne${NE}.g
GenerateVolumetricMesh --in ${GRID_ROOT}/ne${NE}.g --out ${GRID_ROOT}/ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${GRID_ROOT}/ne${NE}pg2.g --out ${GRID_ROOT}/ne${NE}pg2_scrip.nc

ncremap -G ttl='Equi-Angular grid 1000x2000'#latlon=1000,2000#lat_typ=uni#lon_typ=grn_wst -g ${GRID_ROOT}/1000x2000_scrip.nc

GRID_SRC=${GRID_ROOT}/ne${NE}pg2_scrip.nc
GRID_DST=${GRID_ROOT}/1000x2000_scrip.nc
MAP_FILE=${MAPS_ROOT}/map_ne${NE}pg2_to_1000x2000_traave.nc

ncremap --alg_typ=traave --grd_src=${GRID_SRC} --grd_dst=${GRID_DST} --map=${MAP_FILE}

nohup python -u ./regrid.scream.decadal.py > ./regrid.scream.decadal.out &

'''
#---------------------------------------------------------------------------------------------------
'''
GRID_ROOT=/lustre/orion/cli115/proj-shared/hannah6/files_grid
NE=30
GenerateCSMesh --alt --res ${NE} --file ${GRID_ROOT}/ne${NE}.g
GenerateVolumetricMesh --in ${GRID_ROOT}/ne${NE}.g --out ${GRID_ROOT}/ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${GRID_ROOT}/ne${NE}pg2.g --out ${GRID_ROOT}/ne${NE}pg2_scrip.nc
'''
#---------------------------------------------------------------------------------------------------
home = os.getenv('HOME')
# map_file, dst_grid = f'{home}/maps/map_ne30pg2_to_90x180_aave.nc', '90x180'
map_file, dst_grid = f'{home}/maps/map_ne30pg2_to_90x180_traave.nc', '90x180'
# map_file, dst_grid = f'{home}/maps/map_ne30pg2_to_180x360_traave.20240508.nc', '180x360'

# src_root = '/lustre/orion/cli115/proj-shared/brhillman/e3sm_scratch'
# dst_root = '/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch'
# src_sub_dir,dst_sub_dir = 'run',f'remap_{dst_grid}'
# case = 'decadal-production-run6-20240708.ne1024pg2_ne1024pg2.F20TR-SCREAMv1.pnetcdf'


# src_root = '/pscratch/sd/b/beydoun/e3sm_scratch/pm-gpu/'
src_root = '/global/cfs/cdirs/e3sm/beydoun'
dst_root = '/pscratch/sd/w/whannah/scream_scratch/pm-gpu'
src_sub_dir,dst_sub_dir = 'run',f'remap_{dst_grid}'
case = 'ne256pg2_ne256pg2.F20TR-SCREAMv1.rainfrac1.spanc1000.auto2700.acc150.n0128'
# /pscratch/sd/b/beydoun/e3sm_scratch/pm-gpu/ne256pg2_ne256pg2.F20TR-SCREAMv1.rainfrac1.spanc1000.auto2700.acc150.n0128

overwrite = True

#-------------------------------------------------------------------------------
# htype = 'output.scream.decadal.3hourlyAVG_ne30pg2.AVERAGE.nhours_x3'
# htype = 'output.scream.decadal.3hourlyINST_ne30pg2.INSTANT.nhours_x3'
# htype = 'output.scream.decadal.6hourlyAVG_ne30pg2.AVERAGE.nhours_x6'
# htype = 'output.scream.decadal.6hourlyINST_ne30pg2.INSTANT.nhours_x6'
# htype = 'output.scream.decadal.monthlyAVG_ne30pg2.AVERAGE.nmonths_x1'
htype = '6ha_ne30pg2.AVERAGE.nhours_x6.'
#---------------------------------------------------------------------------------------------------

src_dir = f'{src_root}/{case}/{src_sub_dir}'
dst_dir = f'{dst_root}/{case}/{dst_sub_dir}'

if not os.path.exists(dst_dir):
  print(); print(f'Creating output directory: {dst_dir}'); print()
  os.makedirs(dst_dir)

file_path = f'{src_dir}/*{htype}*'
file_list_all = sorted(glob.glob(file_path))
# if 'first_file' in locals(): file_list = file_list[first_file:]
# if 'num_files' in locals(): file_list = file_list[:num_files]

# screen out files
file_list = []
for f in file_list_all:
  if '~' in f: continue
  # year = int(f[-19:-19+4])
  year = int(f[-19:-19+4])
  # print(year); exit()
  if year in [1995,1996,1997,1998]:
    file_list.append(f)

# for f in file_list[-5:]: print(f)
# print(len(file_list)/365)
# exit()

for src_file_name in file_list:
  dst_file_name = src_file_name.replace(src_dir,dst_dir).replace('.nc',f'.remap_{dst_grid}.nc')
  # skip if file destination exists and overwrite=False
  if os.path.isfile(dst_file_name) :
    if overwrite : os.remove(dst_file_name)
    else: 
      print(f'skipping {dst_file_name}')
      continue
  # do the remapping
  cmd = f'ncremap -P eamxx -m {map_file} -i {src_file_name} -o {dst_file_name}'
  print(tcolor.GREEN + cmd + tcolor.ENDC)

  # exit()
  # continue

  try:
    sp.check_output(cmd,shell=True,universal_newlines=True)
  except sp.CalledProcessError as error:
    print(error.output); exit()

  # exit(f'STOPPING - check out file => {dst_file_name}')

#---------------------------------------------------------------------------------------------------