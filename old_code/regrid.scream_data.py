#!/usr/bin/env python
import os, glob, subprocess as sp
from optparse import OptionParser
hiccup_root = os.getenv('HOME')+'/HICCUP'
# home = os.getenv('HOME')
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
# def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; sp.check_call(cmd,shell=True); return
#-------------------------------------------------------------------------------
# parser = OptionParser()
# parser.add_option('-c',dest='case',default=None,help='')
# (opts, args) = parser.parse_args()
#-------------------------------------------------------------------------------
# Generate grid file:
# GenerateCSMesh --alt --res 1024 --file ~/HICCUP/data_scratch/ne1024.g
# GenerateVolumetricMesh --in ~/HICCUP/data_scratch/ne1024.g --out ~/HICCUP/data_scratch/ne1024pg2.g --np 2 --uniform
# ConvertExodusToSCRIP --in ~/HICCUP/data_scratch/ne1024pg2.g  --out ~/HICCUP/data_scratch/ne1024pg2_scrip.nc
# ConvertMeshToSCRIP --in ~/HICCUP/data_scratch/ne1024pg2.g  --out ~/HICCUP/data_scratch/ne1024pg2_scrip.nc

# Generate map file: 
# ncremap --alg_typ=tempest --src_grd=${HOME}/HICCUP/data_scratch/ne1024pg2_scrip.nc --dst_grd=${HOME}/HICCUP/data_scratch/scrip_180x360_s2n.nc --map_file=${HOME}/HICCUP/data_scratch/map_ne1024pg2_to_180x360.nc --wgt_opt='--in_type fv --in_np 2 --out_type fv --out_np 2 --out_double'
# ncremap -5 --src_grd=${HOME}/HICCUP/data_scratch/ne1024pg2_scrip.nc --dst_grd=${HOME}/HICCUP/data_scratch/scrip_180x360_s2n.nc --map_file=${HOME}/HICCUP/data_scratch/map_ne1024pg2_to_180x360.nc 

# Remap the data: 
# ncremap -m <map file> -i <input file> -o <output file>

# ncap2 -O -v -s 'defdim("plev",9);plev[$plev]={97500,95000,92500,85000,80000,70000,50000,20000,10000};' ${HOME}/E3SM/vert_grid_files/vrt_prs_SCREAM.nc

# ncap2 -O -v -s 'defdim("plev",17);plev[$plev]={};' vrt_prs_ncep_L17.nc

# --vrt_fl=${HOME}/E3SM/vert_grid_files/vrt_prs_SCREAM.nc
#-------------------------------------------------------------------------------
name,case,case_dir,case_sub,case_grid = [],[],[],[],[]
def add_case(case_in,n=None,d=None,s=None,g=None,c=None):
   global name,case,case_dir,case_sub
   tmp_name = case_in if n is None else n
   case.append(case_in); name.append(tmp_name); case_dir.append(d); case_sub.append(s); case_grid.append(g)
#-------------------------------------------------------------------------------

nlat_dst,nlon_dst = 180,360

date = '2013-10-01'
# case_path = '/gpfs/alpine/cli115/proj-shared/donahue/run_cases'
data_path = '/gpfs/alpine/cli115/proj-shared/donahue/e3sm_scratch/'
# case = 'ne1024pg2_ne1024pg2.F2010-SCREAMv1.20221014_production_run.27604ccf3f1aaa88ea3413b774ef3817cad7343a'
case = 'ne1024pg2_ne1024pg2.F2010-SCREAMv1.20221115_dt50.bc9287c699516005d52446b0772f7b2db901386d'

output_path = f'/gpfs/alpine/cli115/proj-shared/hannah6/INCITE2022'

# idir = f'{data_path}/{case}/run'
idir = f'{output_path}/{case}/data'
odir = f'{output_path}/{case}/remap_{nlat_dst}x{nlon_dst}'

num_files = 1

# if not os.path.exists(f'{output_path}/{case}'): os.mkdir(f'{output_path}/{case}')
# if not os.path.exists(odir): os.mkdir(odir)

#-------------------------------------------------------------------------------

src_grid_name = 'ne1024pg2' 

# dst_grid_name = f'{nlat_dst}x{nlon_dst}_s2n'
# dst_grid_file = f'{hiccup_root}/files_grid/scrip_{dst_grid_name}.nc'

map_file = f'{hiccup_root}/data_scratch/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}.nc'

print()
print(f'case  : {clr.CYAN}{case}{clr.END}')
print(f'idir  : {idir}')
print(f'odir  : {odir}')
print(f'map   : {map_file}')
print()

if not os.path.exists(odir): print(); raise OSError('Output directory does not exist!')

# exit()

#-------------------------------------------------------------------------------
file_path = f'{idir}/output.scream.QvT.INSTANT*'
# file_path = f'{idir}/output.scream.HorizWinds.INSTANT*'
#-------------------------------------------------------------------------------
file_list = sorted( glob.glob(file_path) )

if 'num_files' in locals(): file_list = file_list[:num_files]

# print(file_list); exit()


# Check for empty file_list and print turncated list for sanity check
if file_list==[]: raise ValueError('file_list is empty')

# print()
# for f in range(min(len(file_list),5)): print(f'  {file_list[f]}')

#-------------------------------------------------------------------------------
for src_file_name in file_list:

   dst_file_name = src_file_name.replace(idir,odir)

   dst_file_name = dst_file_name.replace('.nc',f'.remap_{nlat_dst}x{nlon_dst}.nc')

   print()
   print(f'src file: {src_file_name}')
   print(f'dst file: {dst_file_name}')
   print()

   # exit()

   #---------------------------------------------------------------------------
   # run_cmd(f'ncremap -a tempest -m {map_file} -i {src_file_name} -o {dst_file_name}  ')
   # run_cmd(f'ncremap -m {map_file} -i {src_file_name} -o {dst_file_name}  ')

   # vrt_file = os.getenv('HOME')+'/E3SM/vert_grid_files/vrt_prs_SCREAM.nc'
   # run_cmd(f'ncremap --vrt_fl={vrt_file} -m {map_file} -i {src_file_name} -o {dst_file_name}  ')

   cmd = 'ncremap'
   # cmd += f' -a tempest'
   # if 'h2' in file_search_str: 
   #     vrt_file = os.getenv('HOME')+'/E3SM/vert_grid_files/vrt_prs_SCREAM.nc'
   #     cmd += f' --vrt_fl={vrt_file}'
   cmd += f' -m {map_file}'
   cmd += f' -i {src_file_name}'
   cmd += f' -o {dst_file_name} '

   run_cmd(cmd)

   exit()

   # run_cmd(f'ncrename -v lat,latitude -v lon,longitude {dst_file_name} ')
   #---------------------------------------------------------------------------
   # print(f'\n\nsrc file: {src_file_name}\ndst file: {dst_file_name}\n')

