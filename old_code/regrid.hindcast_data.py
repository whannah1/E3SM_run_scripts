#!/usr/bin/env python
import os, glob, subprocess as sp
from optparse import OptionParser
hiccup_root = os.getenv('HOME')+'/HICCUP/'
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
# def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; sp.check_call(cmd,shell=True); return
#-------------------------------------------------------------------------------
# parser = OptionParser()
# parser.add_option('-c',dest='case',default=None,help='')
# (opts, args) = parser.parse_args()
#-------------------------------------------------------------------------------
# Generate map file for E3SM ne30np4: 
# ncremap --alg_typ=tempest --src_grd=./grid_files/exodus_ne30.g --dst_grd=./grid_files/scrip_90x180_s2n.nc --map_file=/global/homes/w/whannah/maps/map_ne30np4_to_90x180.nc --wgt_opt='--in_type cgll --in_np 4 --out_type fv --out_np 2 --out_double'

# Generate map file for E3SM ne30pg2: 
# ncremap --alg_typ=tempest --src_grd=./grid_files/exodus_ne30pg2.nc --dst_grd=./grid_files/scrip_90x180_s2n.nc --map_file=/global/homes/w/whannah/maps/map_ne30pg2_to_90x180.nc --wgt_opt='--in_type fv --in_np 2 --out_type fv --out_np 2 --out_double'

# Remap the data: ncremap -m <map file> -i <input file> -o <output file>
# obs example: FILE=data_scratch/ERA5_validation.Z.2016-08-01 ; ncremap -m ./map_files/map_721x1440_n2s_to_90x180_s2n.nc -i $FILE.nc -o $FILE.remap_90x180.nc
# hindcast example:
# export MSCRATCH=/global/cscratch1/sd/whannah/e3sm_scratch/cori-knl/
# CASE=E3SM_HINDCAST-TEST_2016-08-01_ne30_FC5AV1C-L_00 ; FILE=$MSCRATCH/$CASE/run/$CASE.cam.h1.2016-08-01-00000 ; ncremap -m $HOME/maps/map_ne30np4_to_90x180.nc -i $FILE.nc -o $FILE.remap_90x180.nc
# CASE=E3SM_HINDCAST-TEST_2016-08-01_ne30pg2_FC5AV1C-L_00 ; FILE=$MSCRATCH/$CASE/run/$CASE.cam.h1.2016-08-01-00000 ; ncremap -m $HOME/maps/map_ne30pg2_to_90x180.nc -i $FILE.nc -o $FILE.remap_90x180.nc
#-------------------------------------------------------------------------------
# name,case_list,case_dir,case_sub,case_grid = [],[],[],[],[]
# def add_case(case_in,n=None,d=None,s=None,g=None,c=None):
#    global name,case,case_dir,case_sub
#    tmp_name = case_in if n is None else n
#    case.append(case_in); name.append(tmp_name); case_dir.append(d); case_sub.append(s); case_grid.append(g)
#-------------------------------------------------------------------------------

case_list = []
case_list.append('E3SM.2022-SCREAMv1-COMP.F2010-MMF1.ne30pg2_oECv3.2013-10-01')

# file_search_str = 'eam.h1.'
file_search_str = 'eam.h2.'

# nlat_dst,nlon_dst = 90,180
nlat_dst,nlon_dst = 180,360

src_grid_name = 'ne30pg2'

dst_grid_name = f'{nlat_dst}x{nlon_dst}_s2n'
dst_grid_file = f'{hiccup_root}/files_grid/scrip_{dst_grid_name}.nc'

date = '2013-10-01'

# scratch_path = '/global/cscratch1/sd/whannah/e3sm_scratch/cori-knl/' ### NERSC
# scratch_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/' ### OLCF
scratch_path = '/gpfs/alpine/cli115/proj-shared/hannah6/e3sm_scratch/' ### OLCF


# map_file = f'{hiccup_root}/map_files/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}.nc'
map_file = os.getenv('HOME')+f'/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}.nc'

#-------------------------------------------------------------------------------
for case in case_list:

    print(f'\ncase: {clr.CYAN}{case}{clr.END}')

    idir = f'{scratch_path}/{case}/run'
    odir = f'{scratch_path}/{case}/remap_{nlat_dst}x{nlon_dst}'

    if not os.path.exists(odir): os.mkdir(odir)
    #---------------------------------------------------------------------------

    file_path = f'{scratch_path}/{case}/run/{case}.{file_search_str}*.nc'
    # file_path = f'{scratch_path}/{case}/run/{case}.eam.h2.*-00000.nc'

    file_list = sorted( glob.glob(file_path) )

    ### truncate the file list for debugging
    # file_list = file_list[0:1]

    ### Check for empty file_list and print turncated list for sanity check
    if file_list==[]: raise ValueError('file_list is empty')
    
    # print()
    # for f in range(min(len(file_list),5)): print(f'  {file_list[f]}')

    #---------------------------------------------------------------------------
    for src_file_name in file_list:

        dst_file_name = src_file_name.replace(idir,odir)

        dst_file_name = dst_file_name.replace('.nc',f'.remap_{nlat_dst}x{nlon_dst}.nc')

        # dst_file_name = src_file_name.replace('.nc',f'.remap_{nlat_dst}x{nlon_dst}.nc')

        print()
        print(f'src file: {src_file_name}')
        print(f'dst file: {dst_file_name}')
        print()

        # exit()

        #-----------------------------------------------------------------------
        cmd = 'ncremap'
        cmd += f' -a tempest'
        if 'h2' in file_search_str: 
            vrt_file = os.getenv('HOME')+'/E3SM/vert_grid_files/vrt_prs_SCREAM.nc'
            cmd += f' --vrt_fl={vrt_file}'
        cmd += f' -m {map_file}'
        cmd += f' -i {src_file_name}'
        cmd += f' -o {dst_file_name} '
        
        run_cmd(cmd)

        # vrt_file = os.getenv('HOME')+'/E3SM/vert_grid_files/vrt_prs_SCREAM.nc'
        # run_cmd(f'ncremap --vrt_fl={vrt_file} -m {map_file} -i {src_file_name} -o {dst_file_name}  ')

        # exit()

        # run_cmd(f'ncrename -v lat,latitude -v lon,longitude {dst_file_name} ')
        #---------------------------------------------------------------------------
        # print(f'\n\nsrc file: {src_file_name}\ndst file: {dst_file_name}\n')

