#!/usr/bin/env python
#===============================================================================
'''
commands to create grid and map files:

GRID_ROOT=~/E3SM/data_grid
MAPS_ROOT=~/maps

NE=26
SRC_GRID=ne${NE}pg2

#DST_NY=90
#DST_NX=180

DST_NY=73
DST_NX=144

DST_GRID=${DST_NY}x${DST_NX}

SRC_GRID_FILE=${GRID_ROOT}/${SRC_GRID}_scrip.nc
DST_GRID_FILE=${GRID_ROOT}/${DST_GRID}_scrip.nc
MAP_FILE=${MAPS_ROOT}/map_${SRC_GRID}_to_${DST_GRID}_traave.nc

echo SRC_GRID_FILE : $SRC_GRID_FILE ; echo DST_GRID_FILE : $DST_GRID_FILE ; echo MAP_FILE      : $MAP_FILE

### generation source grid file
# GenerateCSMesh --alt --res ${NE} --file ${GRID_ROOT}/ne${NE}.g
# GenerateVolumetricMesh --in ${GRID_ROOT}/ne${NE}.g    --out ${GRID_ROOT}/ne${NE}pg2.g --np 2 --uniform
# ConvertMeshToSCRIP     --in ${GRID_ROOT}/ne${NE}pg2.g --out ${GRID_ROOT}/ne${NE}pg2_scrip.nc

### generate destination lat/lon grid file
# ncremap -g ${DST_GRID_FILE} -G ttl="Equi-Angular grid, dimensions ${DST_GRID}, cell edges on Poles/Equator and Prime Meridian/Date Line"#latlon=${DST_NY},${DST_NX}#lat_typ=uni#lon_typ=grn_wst
# ncremap -G ttl='FV grid 73x144'#latlon=73,144#lat_typ=fv#lon_typ=grn_ctr -g $HOME/E3SM/data_grid/73x144_scrip.nc

# generate map file
ncremap -6 --alg_typ=traave --grd_src=$SRC_GRID_FILE --grd_dst=$DST_GRID_FILE --map=$MAP_FILE

# command to create CMIP6 HighResMIP vertical pressure coordinate file
# ncap2 -O -v -s 'defdim("plev",27);plev[$plev]={100000,97500,95000,92500,90000,87500,85000,82500,80000,77500,75000,70000,65000,60000,55000,50000,45000,40000,35000,30000,25000,22500,20000,17500,15000,12500,10000};' ~/E3SM/vert_grid_files/vrt_prs_CMIP6.nc
ncap2 -O -v -s 'defdim("plev",4);plev[$plev]={85000,10000,7000,2000};' ${HOME}/E3SM/vert_grid_files/vrt_prs_850-100-70-20.nc


'''
#===============================================================================
#===============================================================================
import sys, os, subprocess as sp, glob
#===============================================================================
#-------------------------------------------------------------------------------
case_list = []
src_top_dir_list,src_sub_dir_list = [],[]
dst_top_dir_list,dst_sub_dir_list = [],[]
map_file_list = []
def add_case(case_in,src_dir_in,src_sub_in,dst_dir_in,dst_sub_in,map_file=None):
   global case_list,src_top_dir_list,src_sub_dir_list
   case_list.append(case_in)
   src_top_dir_list.append(src_dir_in); src_sub_dir_list.append(src_sub_in)
   dst_top_dir_list.append(dst_dir_in); dst_sub_dir_list.append(dst_sub_in)
   map_file_list.append(map_file)
#-------------------------------------------------------------------------------
#===============================================================================
home = os.getenv('HOME')
do_atm_h0, do_atm_h1, do_atm_h2, do_lnd_h0, overwrite = False, False, False, False, False

# nlat_dst,nlon_dst = 90,180
nlat_dst,nlon_dst = 73,144
# nlat_dst,nlon_dst,map_file =  90,180,f'{home}/maps/map_ne30pg2_to_90x180_aave.nc'
# nlat_dst,nlon_dst,map_file =  90,180,f'{home}/maps/map_ne30pg2_to_cmip6_90x180_aave.nc'

# add_case(case_in='v3.LR.amip_0101.QBObenchmark.20241008',\
#          src_dir_in='/global/cfs/cdirs/m4310/data/sims',\
#          src_sub_in='archive/atm/hist',\
#          dst_dir_in='/global/cfs/cdirs/m4310/data/sims',\
#          dst_sub_in=f'data_remap_{nlat_dst}x{nlon_dst}')

map_root=f'{home}/maps/'
src_dir,src_sub = '/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu','run'
dst_dir,dst_sub = '/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu',f'remap_{nlat_dst}x{nlon_dst}'
add_case(case_in='E3SM.2025-MF-test-00.ne18pg2.F20TR.NN_12',src_dir_in=src_dir,src_sub_in=src_sub,dst_dir_in=dst_dir,dst_sub_in=dst_sub,map_file=f'{map_root}/map_ne18pg2_to_{nlat_dst}x{nlon_dst}_traave.nc')
add_case(case_in='E3SM.2025-MF-test-00.ne22pg2.F20TR.NN_18',src_dir_in=src_dir,src_sub_in=src_sub,dst_dir_in=dst_dir,dst_sub_in=dst_sub,map_file=f'{map_root}/map_ne22pg2_to_{nlat_dst}x{nlon_dst}_traave.nc')
add_case(case_in='E3SM.2025-MF-test-00.ne26pg2.F20TR.NN_24',src_dir_in=src_dir,src_sub_in=src_sub,dst_dir_in=dst_dir,dst_sub_in=dst_sub,map_file=f'{map_root}/map_ne26pg2_to_{nlat_dst}x{nlon_dst}_traave.nc')
add_case(case_in='E3SM.2025-MF-test-00.ne30pg2.F20TR.NN_32',src_dir_in=src_dir,src_sub_in=src_sub,dst_dir_in=dst_dir,dst_sub_in=dst_sub,map_file=f'{map_root}/map_ne30pg2_to_{nlat_dst}x{nlon_dst}_traave.nc')

### comment/uncomment to disable/enable
# do_atm_h0 = True
do_atm_h1 = True
# do_atm_h2 = True
# do_lnd_h0 = True

h0_vars_arg = ' --var_lst=T,U,V '
h1_vars_arg = ' --var_lst=FLUT,PRECT,U850,U200 '
h2_vars_arg = ' --var_lst=T,U,V '

hx_vert_arg = ''
# hx_vert_arg = f' --vrt_fl={home}/E3SM/vert_grid_files/vrt_prs_100-70.nc'
# hx_vert_arg = f' --vrt_fl={home}/E3SM/vert_grid_files/vrt_prs_850-100-70-20.nc'

execute   = True
overwrite = True
print_cmd = True

# yr1,yr2 = 1978,1978
# yr1,yr2 = 1978,2021
# yr1,yr2 = 1985,1989
# yr1,yr2 = 1985,1990
yr1,yr2 = 1985,1994

#===============================================================================
class tcolor: ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd,print_cmd=True,suppress_output=False):
    if suppress_output : cmd = cmd + ' > /dev/null'
    if print_cmd: print(tcolor.GREEN + cmd + tcolor.ENDC)
    if execute:
        try:
            sp.check_output(cmd,shell=True,universal_newlines=True)
        except sp.CalledProcessError as error:
            print(error.output)
            exit()
    return
#===============================================================================
def check_path_and_create(path_in):
    if not os.path.exists(path_in): os.mkdir(path_in)
    return       
#===============================================================================
for c,case in enumerate(case_list) :
    src_top_dir, src_sub_dir = src_top_dir_list[c], src_sub_dir_list[c]
    dst_top_dir, dst_sub_dir = dst_top_dir_list[c], dst_sub_dir_list[c]
    map_file = map_file_list[c]
    #---------------------------------------------------------------------------
    # Set in/out paths and create output directory if it doesn't exist
    src_dir = f'{src_top_dir}/{case}/{src_sub_dir}'
    dst_dir = f'{dst_top_dir}/{case}/{dst_sub_dir}'
    if not os.path.exists(dst_dir):
        print(); print(f'Creating output directory: {dst_dir}'); print()
        check_path_and_create(f'{dst_top_dir}')
        check_path_and_create(f'{dst_top_dir}/{case}')
        check_path_and_create(f'{dst_top_dir}/{case}/{dst_sub_dir}')
    #---------------------------------------------------------------------------
    print(f'case    : {case}')
    print(f'src_dir : {src_dir}')
    print(f'dst_dir : {dst_dir}')
    print(f'map_file: {map_file}')
    print('')
    # exit()
    atm_comp,lnd_comp = 'eam','elm'
    #---------------------------------------------------------------------------
    # get list of all files to loop over
    files = sorted( glob.glob(f'{src_dir}/{case}.{atm_comp}.h*.nc') )
    # files = sorted( os.listdir(src_dir) )
    #---------------------------------------------------------------------------
    # for f in files[:5]: print(' '+f)
    # print('  ...')
    # for f in files[-5:]: print(' '+f)
    # exit()
    #---------------------------------------------------------------------------
    if 'yr1' in locals() \
    or 'yr2' in locals():
        yr_list = []
        for f,f_in in enumerate(files):
            yr = f_in
            yr = yr.replace(f'{src_dir}/','')
            for htype in ['h0','h1','h2','h3','h4','h5','h6','h7','h8','h9']:
                yr = yr.replace(f'{case}.{atm_comp}.{htype}.','')
                # yr = yr.replace(f'{case}.{lnd_comp}.{htype}.','')
            yr = yr.replace(f'.nc','')
            yr = int(yr.split('-')[0])
            yr_list.append(yr)
    #---------------------------------------------------------------------------
    cnt = 0
    for f,f_in in enumerate(files):
        remap_flag = False
        if do_atm_h0 and f'{atm_comp}.h0' in f_in : remap_flag = True
        if do_atm_h1 and f'{atm_comp}.h1' in f_in : remap_flag = True
        if do_atm_h2 and f'{atm_comp}.h2' in f_in : remap_flag = True
        if do_lnd_h0 and f'{lnd_comp}.h0' in f_in : remap_flag = True

        # don't regrid data that's already been regridded
        if '.remap_' in f_in : remap_flag = False

        if 'yr1' in locals() and yr_list[f]<yr1: remap_flag = False
        if 'yr2' in locals() and yr_list[f]>yr2: remap_flag = False

        if remap_flag :
            cnt += 1

            src_file_name = f_in # f'{src_dir}/{f_in}'
            dst_file_name = src_file_name.replace('.nc',f'.remap_{nlat_dst}x{nlon_dst}.nc')

            if os.path.isfile(dst_file_name) :
                if overwrite : os.remove(dst_file_name)
                else : continue

            # Change path of output file
            dst_file_name = dst_file_name.replace(src_dir,dst_dir)

            cmd = f'ncremap -m {map_file} -i {src_file_name} -o {dst_file_name} '

            if f'{atm_comp}.h0' in src_file_name : cmd += h0_vars_arg
            if f'{atm_comp}.h1' in src_file_name : cmd += h1_vars_arg
            if f'{atm_comp}.h2' in src_file_name : cmd += h2_vars_arg
            
            if f'{atm_comp}.h0' in src_file_name : cmd += hx_vert_arg
            if f'{atm_comp}.h2' in src_file_name : cmd += hx_vert_arg

            run_cmd(cmd)
#===============================================================================
    if cnt==0:
        print(files)
        print()
        print(f'  do_atm_h0: {do_atm_h0}')
        print(f'  do_atm_h1: {do_atm_h1}')
        print(f'  do_atm_h2: {do_atm_h2}')
        print(f'  do_lnd_h0: {do_lnd_h0}')
        print(f'  dst_grid : {nlat_dst} x {nlon_dst}')
        print(f'  atm_comp : {atm_comp}')
        print('\nNo files found for remapping...?\n')
#===============================================================================
print('Done.')

