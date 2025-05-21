#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import sys,os,subprocess as sp
from optparse import OptionParser
parser = OptionParser()
parser.add_option('-n',dest='num_file',default=None,help='sets number of files to print')
# parser.add_option('--comp',dest='component',default=None,help='model component history file to search for')
parser.add_option('--vert',action='store_true', dest='vert_pressure_remap', default=False,help='enable vertical interpolation to pressure levels')
(opts, args) = parser.parse_args()
#===============================================================================
#===============================================================================
home = os.getenv('HOME')

# scratch_dir = '/pscratch/sd/w/whannah/e3sm_scratch/perlmutter'      ### Perlmutter scratch space
# scratch_dir = os.getenv('SCRATCH')+'/e3sm_scratch/cori-knl/'        ### Cori scratch space
# scratch_dir = os.getenv('MEMBERWORK')+'/cli115/e3sm_scratch/'       ### OLCF scratch space
scratch_dir = os.getenv('CFS')+'/m1517/dyang/E3SM_MMF/'

if scratch_dir=='' :exit('ERROR: scratch directory not set!')
#===============================================================================
#===============================================================================
do_h0, do_h1, do_h2, do_clm, overwrite = False, False, False, False, False

if len(sys.argv) < 2 :
    print('ERROR: no case name provided!')
    exit()
else :
    cases = sys.argv[1:]

# omit flags from case list
for c in cases: 
    if c[0]=='-': cases.remove(c)

### comment/uncomment to disable/enable
do_h0 = True
do_h1 = True
do_h2 = True
# do_clm = True

execute   = True
overwrite = True
print_cmd = True
write_log = False

nlat_dst,nlon_dst =  90,180
# nlat_dst,nlon_dst = 180,360
# nlat_dst,nlon_dst =  72, 144

# pressure_levels = 1000,975,950,925,900,875,850,825,800,775,750,700,650,600,550,500,450,400,350,300,250,225,200,175,150,125,100

log_file = './regrid.case.out'

class tcolor: ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'

#===============================================================================
#===============================================================================
for case in cases :

    #---------------------------------------------------------------------------
    # Input directory
    #---------------------------------------------------------------------------
    # data_sub = 'run'
    data_sub = 'data_native'
    data_dir = f'{scratch_dir}/{case}/{data_sub}/'
    #---------------------------------------------------------------------------
    # Output directory
    #---------------------------------------------------------------------------
    if opts.vert_pressure_remap: 
        odir_sub = f'data_remap_{nlat_dst}x{nlon_dst}_prs'
    else:
        odir_sub = f'data_remap_{nlat_dst}x{nlon_dst}'
    odir = f'{scratch_dir}/{case}/{odir_sub}'
    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    print(f'case     : {case}')
    print(f'data dir : {data_dir}')
    print(f'out dir  : {odir}')
    print(f'log file : {log_file}')
    print('')

    files = os.listdir(data_dir)

    if 'ne30_'     in case: src_grid_name = 'ne30np4'
    if 'ne30pg2_'  in case: src_grid_name = 'ne30pg2'
    if 'ne30pg2.'  in case: src_grid_name = 'ne30pg2'
    if 'ne45pg2_'  in case: src_grid_name = 'ne45pg2'
    if 'ne120pg2_' in case: src_grid_name = 'ne120pg2'
    if 'ne120pg2.' in case: src_grid_name = 'ne120pg2'

    #---------------------------------------------------------------------------
    # specify map file
    #---------------------------------------------------------------------------
    
    ### CMIP map for E3SM diags
    if 'map_file' not in locals():
        map_file = f'{home}/maps/map_{src_grid_name}_to_cmip6_{nlat_dst}x{nlon_dst}_aave.nc'
        # map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}_aave.nc'

    
    if nlat_dst==721 and nlon_dst==1440:
        if any( pg in case for pg in ['pg2','pg3','pg4'] ):
            map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}_bilin.20201019.nc'
        else:
            map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}.20201019.nc'

    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------

    if not os.path.exists(odir): os.mkdir(odir)

    atm_comp,lnd_comp = 'eam','elm'
    # if 'E3SM.RGMA.' in case: atm_comp,lnd_comp = 'cam','clm'
    if 'E3SM.PI-CPL.v1.' in case: atm_comp,lnd_comp = 'cam','clm'
        

    cnt = 0
    for f_in in files : 
        remap_flag = False
        if do_h0  and f'{atm_comp}.h0' in f_in : remap_flag = True
        if do_h1  and f'{atm_comp}.h1' in f_in : remap_flag = True
        if do_h2  and f'{atm_comp}.h2' in f_in : remap_flag = True
        if do_clm and f'{lnd_comp}2.h' in f_in : remap_flag = True

        if 'htype' in locals():
            if f'{atm_comp}.{htype}.' in f_in : remap_flag = True

        # don't remap already remapped data
        if '.remap_' in f_in : remap_flag = False
        
        if remap_flag :
            cnt += 1
            f_out = f_in.replace('.nc','.remap.nc')

            if os.path.isfile(f_out) :
                if overwrite : os.remove(f_out)
                else : continue

            src_file_name = data_dir+f_in
            dst_file_name = src_file_name.replace('.nc',f'.remap_{nlat_dst}x{nlon_dst}.nc')


            # Change directory
            dst_file_name = dst_file_name.replace(f'/{data_sub}/',f'/{odir_sub}/')

            cmd = f'ncremap -m {map_file} -i {src_file_name} -o {dst_file_name}'

            if opts.vert_pressure_remap:
                cmd += ' --vrt_fl=$HOME/E3SM/vert_grid_files/vrt_prs_CMIP6.nc'

            if print_cmd:
                msg = tcolor.GREEN + cmd + tcolor.ENDC
                print('\n'+msg+'\n')
            else:
                print('    '+f_in+'  >  '+data_dir+f_out)
            if write_log: cmd += ' > '+log_file
            if execute: 
                # os.system(cmd)
                try:
                    sp.check_output(cmd,shell=True,universal_newlines=True)
                except sp.CalledProcessError as error:
                    print(error.output)
                    exit()
#===============================================================================
#===============================================================================
    if cnt==0:
        print(files)
        print()
        print(f'  do_h0    : {do_h0}')
        print(f'  do_h1    : {do_h1}')
        print(f'  do_h2    : {do_h2}')
        print(f'  do_clm   : {do_clm}')
        print(f'  dst_grid : {nlat_dst} x {nlon_dst}')
        print(f'  atm_comp : {atm_comp}')
        print(f'  odir     : {odir}')
        

        print('\nNo files found for remapping...?\n')

#===============================================================================
#===============================================================================
