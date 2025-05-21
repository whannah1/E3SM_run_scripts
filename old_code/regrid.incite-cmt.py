#!/usr/bin/env python

### command to create map file for CMIP remap method:
# GRID=ne30np4 ; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRID}_scrip.nc 
# --grd_dst=$HOME/E3SM/data_grid/cmip6_180x360_scrip.20181001.nc
# --map=$HOME/maps/map_${GRID}_to_cmip6_180x360_aave.20200624.nc


#===============================================================================
#===============================================================================
import sys,os
import subprocess as sp
from optparse import OptionParser
parser = OptionParser()
parser.add_option('-n',dest='num_file',default=None,help='sets number of files to print')
# parser.add_option('--comp',dest='component',default=None,help='model component history file to search for')
(opts, args) = parser.parse_args()
#===============================================================================
#===============================================================================
home = os.getenv('HOME')

# scratch_dir = os.getenv('SCRATCH')+'/e3sm_scratch/cori-knl'         ### Cori scratch space
# scratch_dir = os.getenv('MEMBERWORK')+'/cli115/e3sm_scratch'        ### OLCF scratch space
# scratch_dir = '/gpfs/alpine/cli115/proj-shared/hannah6/INCITE2021'   ### OLCF project space

# if scratch_dir=='' :exit('ERROR: scratch directory not set!')
#===============================================================================
#===============================================================================
do_h0, do_h1, do_h2, do_lnd, overwrite = False, False, False, False, False



cases = []
# cases.append('E3SM.INCITE2021-CMT.GNUGPU.ne45pg2_r05_oECv3.F-MMFXX.NXY_32x1.BVT.02')
cases.append('E3SM.INCITE2021-CMT.GNUGPU.ne45pg2_r05_oECv3.F-MMFXX.NXY_32x1.BVT.MOMFB.02')
# cases.append('E3SM.INCITE2021-CMT.GNUGPU.ne45pg2_r05_oECv3.F-MMFXX.NXY_32x32.BVT.02')
cases.append('E3SM.INCITE2021-CMT.GNUGPU.ne45pg2_r05_oECv3.F-MMFXX.NXY_32x32.BVT.MOMFB.02')

### comment/uncomment to disable/enable
do_h0 = True
do_h1 = True
do_h2 = True
# do_lnd = True

execute   = True
overwrite = False
print_cmd = True


nlat_dst,nlon_dst,map_file = 180,360,'/ccs/home/hannah6/maps/map_ne45pg2_to_cmip6_180x360_aave.20200624.nc'


src_top_dir,src_sub_dir = os.getenv('MEMBERWORK')+'/cli115/e3sm_scratch','run'
dst_top_dir,dst_sub_dir = '/gpfs/alpine/cli115/proj-shared/hannah6/INCITE2021',f'data_remap_{nlat_dst}x{nlon_dst}'

#===============================================================================
#===============================================================================
class tcolor: ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd,print_cmd=True,suppress_output=False):
    if suppress_output : 
        cmd = cmd + ' > /dev/null'
    if print_cmd: 
        msg = tcolor.GREEN + cmd + tcolor.ENDC
        print(f'{msg}')
    if execute:
        # os.system(cmd)
        try:
            sp.check_output(cmd,shell=True,universal_newlines=True)
        except sp.CalledProcessError as error:
            print(error.output)
            exit()
    return       
#===============================================================================
#===============================================================================
for case in cases :

    #---------------------------------------------------------------------------
    # Input directory
    #---------------------------------------------------------------------------
    src_dir = f'{src_top_dir}/{case}/{src_sub_dir}'
    dst_dir = f'{dst_top_dir}/{case}/{dst_sub_dir}'
    # Create output directory if it doesn't exist
    if not os.path.exists(dst_dir): os.mkdir(dst_dir)
    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    print(f'case    : {case}')
    print(f'src_dir : {src_dir}')
    print(f'dst_dir : {dst_dir}')
    print('')

    atm_comp,lnd_comp = 'eam','elm'
    #---------------------------------------------------------------------------
    # Loop over all files
    #---------------------------------------------------------------------------
    files = os.listdir(src_dir)
    cnt = 0
    for f_in in files : 
        remap_flag = False
        if do_h0  and f'{atm_comp}.h0' in f_in : remap_flag = True
        if do_h1  and f'{atm_comp}.h1' in f_in : remap_flag = True
        if do_h2  and f'{atm_comp}.h2' in f_in : remap_flag = True
        if do_lnd and f'{lnd_comp}.h'  in f_in : remap_flag = True

        # don't regrid data that's already been regridded
        if '.remap_' in f_in : remap_flag = False

        if remap_flag :
            cnt += 1
            
            src_file_name = f'{src_dir}/{f_in}'
            dst_file_name = src_file_name.replace('.nc',f'.remap_{nlat_dst}x{nlon_dst}.nc')

            if os.path.isfile(dst_file_name) :
                if overwrite : os.remove(dst_file_name)
                else : continue

            # Change path of output file
            dst_file_name = dst_file_name.replace(src_dir,dst_dir)

            cmd = f'ncremap -m {map_file} -i {src_file_name} -o {dst_file_name}'

            run_cmd(cmd)

#===============================================================================
#===============================================================================
    if cnt==0:
        print(files)
        print()
        print(f'  do_h0    : {do_h0}')
        print(f'  do_h1    : {do_h1}')
        print(f'  do_h2    : {do_h2}')
        print(f'  do_lnd   : {do_lnd}')
        print(f'  dst_grid : {nlat_dst} x {nlon_dst}')
        print(f'  atm_comp : {atm_comp}')

        print('\nNo files found for remapping...?\n')

#===============================================================================
#===============================================================================
