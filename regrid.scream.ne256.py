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

nohup time python -u regrid.scream.ne256.py > regrid.scream.ne256.out &

'''
#---------------------------------------------------------------------------------------------------

dst_grid = '1000x2000'

map_file = '/lustre/orion/cli115/proj-shared/hannah6/files_map/map_ne256pg2_to_1000x2000_traave.nc'

htype = 'output.scream.2D.1hr.ne256pg2.INSTANT.nhours_x1'

case_root = '/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch'
src_sub_dir = 'run'
dst_sub_dir = f'remap_{dst_grid}'

case_list = []
# case_list.append('SCREAM.2025-PC-01.F2010-SCREAMv1-DYAMOND1.ne256pg2.cfr_1')
# case_list.append('SCREAM.2025-PC-00.F2010-SCREAMv1-DYAMOND1.ne256pg2.cfr_1.cfi_0.acc_60.rsc_5.eci_0.1.eri_0.1.mti_7.4e6.acp_100.acq_2.5.acn_1.5.acr_2e-05.isf_1')
case_list.append('SCREAM.2025-PC-00.F2010-SCREAMv1-DYAMOND1.ne256pg2.cfr_1.cfi_0.acc_60.rsc_5.eci_0.1.eri_0.1.mti_7.4e6.acp_100.acq_2.5.acn_1.5.acr_2e-05.isf_0.95')
case_list.append('SCREAM.2025-PC-00.F2010-SCREAMv1-DYAMOND1.ne256pg2.cfr_1.cfi_0.acc_60.rsc_5.eci_0.1.eri_0.1.mti_7.4e6.acp_100.acq_2.5.acn_1.5.acr_2e-05.isf_0.9')

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
    cmd = f'ncremap -P eamxx -m {map_file} -i {src_file_name} -o {dst_file_name}'
    
    print(tcolor.GREEN + cmd + tcolor.ENDC)
    
    # continue

    try:
      sp.check_output(cmd,shell=True,universal_newlines=True)
    except sp.CalledProcessError as error:
      print(error.output); exit()

#---------------------------------------------------------------------------------------------------