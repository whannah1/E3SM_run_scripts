#!/usr/bin/env python3
import sys,os,glob,subprocess as sp
class tcolor: ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
#---------------------------------------------------------------------------------------------------
'''
GRID_ROOT=/pscratch/sd/w/whannah/files_grid
MAPS_ROOT=/pscratch/sd/w/whannah/files_map

NE=120
GenerateCSMesh --alt --res ${NE} --file ${GRID_ROOT}/exodus_ne${NE}.g
GenerateVolumetricMesh --in ${GRID_ROOT}/exodus_ne${NE}.g --out ${GRID_ROOT}/exodus_ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${GRID_ROOT}/exodus_ne${NE}pg2.g --out ${GRID_ROOT}/scrip_ne${NE}pg2.nc

ncremap -G ttl='Equi-Angular grid 1000x2000'#latlon=1000,2000#lat_typ=uni#lon_typ=grn_wst -g ${GRID_ROOT}/1000x2000_scrip.nc

GRID_SRC=${GRID_ROOT}/scrip_ne120pg2.nc
GRID_DST=${GRID_ROOT}/scrip_ne30pg2.nc
MAP_FILE=${MAPS_ROOT}/map_ne120pg2_to_ne30pg2_traave.nc

ncremap --alg_typ=traave --grd_src=${GRID_SRC} --grd_dst=${GRID_DST} --map=${MAP_FILE}

nohup time python -u regrid.v3HR.py > regrid.v3HR.out &

'''
#---------------------------------------------------------------------------------------------------

dst_grid = 'ne30pg2'

map_file = '/pscratch/sd/w/whannah/files_map/map_ne120pg2_to_ne30pg2_traave.nc'

htype = 'eam.h0.'

case_root = '/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu'
src_sub_dir = 'run'
dst_sub_dir = f'remap_{dst_grid}'

case_list = []
# case_list.append('E3SM.v3HR.QBO-tuning-00.F20TR.fgfc_2E-14.tsps_2.pm-cpu')
# case_list.append('E3SM.v3HR.QBO-tuning-00.F20TR.fgfc_5E-14.tsps_2.pm-cpu')
# case_list.append('E3SM.v3HR.QBO-tuning-00.F20TR.fgfc_2E-14.tsps_5.pm-cpu')
case_list.append('E3SM.v3HR.QBO-tuning-00.F20TR.fgfc_5E-14.tsps_5.pm-cpu')


overwrite = True

#---------------------------------------------------------------------------------------------------
for case in case_list:

  src_dir = f'{case_root}/{case}/{src_sub_dir}'
  dst_dir = f'{case_root}/{case}/{dst_sub_dir}'

  if not os.path.exists(dst_dir):
    print(); print(f'Creating output directory: {dst_dir}'); print()
    os.mkdir(dst_dir)

  file_path = f'{src_dir}/*{htype}*'
  file_list = sorted(glob.glob(file_path))
  if 'first_file' in locals(): file_list = file_list[first_file:]
  if 'num_files' in locals(): file_list = file_list[:num_files]

  for src_file_name in file_list:
    dst_file_name = src_file_name.replace(src_dir,dst_dir).replace('.nc',f'.remap_{dst_grid}.nc')
    # skip if file destination exists and overwrite=False
    if os.path.isfile(dst_file_name): 
      if overwrite:
        print(f'{tcolor.RED}overwriting {dst_file_name}{tcolor.ENDC}')
        os.remove(dst_file_name)
      else:
        print(f'{tcolor.CYAN}skipping {dst_file_name}{tcolor.ENDC}')
        continue

    # do the remapping
    # cmd = f'ncremap -P eamxx -m {map_file} -i {src_file_name} -o {dst_file_name}'
    cmd = f'ncremap -m {map_file} -i {src_file_name} -o {dst_file_name}'
    
    print(tcolor.GREEN + cmd + tcolor.ENDC)
    
    # continue

    try:
      sp.check_output(cmd,shell=True,universal_newlines=True)
    except sp.CalledProcessError as error:
      print(error.output); exit()

#---------------------------------------------------------------------------------------------------