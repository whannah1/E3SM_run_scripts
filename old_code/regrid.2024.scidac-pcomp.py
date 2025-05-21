#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
### map file for CMIP remap method:
# GRIDIN=ne30pg2; GRIDOUT=180x360 ; ncremap -6 --alg_typ=aave --grd_src=grid_files/${GRIDIN}_scrip.nc --grd_dst=grid_files/cmip6_${GRIDOUT}_scrip.20181001.nc --map=map_files/map_${GRID}_to_cmip6_${GRIDOUT}_aave.nc
# GRIDIN=ne30pg2; GRIDOUT=90x180 ; ncremap -6 --alg_typ=aave --grd_src=grid_files/${GRIDIN}_scrip.nc --grd_dst=grid_files/cmip6_${GRIDOUT}_scrip.20181001.nc --map=map_files/map_${GRID}_to_cmip6_${GRIDOUT}_aave.nc

#---------------------------------------------------------------------------------------------------
# command to create CMIP6 HighResMIP vertical pressure coordinate file
# ncap2 -O -v -s 'defdim("plev",27);plev[$plev]={100000,97500,95000,92500,90000,87500,85000,82500,80000,77500,75000,70000,65000,60000,55000,50000,45000,40000,35000,30000,25000,22500,20000,17500,15000,12500,10000};' ~/E3SM/vert_grid_files/vrt_prs_CMIP6.nc

# ERA5 vertical pressure coordinate
# ncap2 -O -v -s 'defdim("plev",37);plev[$plev]={100000,97500,95000,92500,90000,87500,85000,82500,80000,77500,75000,70000,65000,60000,55000,50000,45000,40000,35000,30000,25000,22500,20000,17500,15000,12500,10000,7000,5000,3000,2000,1000,700,500,300,200,100};' grid_files/vrt_prs_ERA5.nc
#---------------------------------------------------------------------------------------------------
'''
source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh
nohup python -u  regrid.2024.scidac-pcomp.py > regrid.2024.scidac-pcomp.out &
'''
#---------------------------------------------------------------------------------------------------
import sys,os,subprocess as sp
class tcolor: ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'

do_h0, do_h1, do_h2, do_cl, = False, False, False, False
execute, overwrite, print_cmd =  False, False, False

# scratch_dir = '/global/cfs/cdirs/m4310/whannah/E3SM'
# scratch_dir = '/global/homes/w/whannah/E3SM/cfs_m4310/E3SM'
scratch_dir = '/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu'
data_sub = 'run' # 'archive/atm/hist'
atm_comp = 'eam'

### comment/uncomment to disable/enable
# do_h0 = True
do_h1 = True
# do_h2 = True
# do_clm = True

execute   = True
overwrite = True
print_cmd = True
# write_log = False

#---------------------------------------------------------------------------------------------------

vert_pressure_remap = True
pressure_level_file = os.getenv('HOME')+'/E3SM/vert_grid_files/vrt_prs_ERA5.nc'

nlat_dst,nlon_dst =  90,180
# nlat_dst,nlon_dst = 180,360

src_grid_name = 'ne30pg2'
map_file = os.getenv('HOME')+f'/maps/map_{src_grid_name}_to_cmip6_{nlat_dst}x{nlon_dst}_aave.nc'

# log_file = './regrid.case.out'

#---------------------------------------------------------------------------------------------------
tmp_date_list = []
# tmp_date_list.append('1983-01-01') # phase 1 - pi*1/4
# tmp_date_list.append('1993-04-01')
# tmp_date_list.append('2002-07-01')
# tmp_date_list.append('2022-10-01')
# tmp_date_list.append('1986-10-01') # phase 1 - pi*3/4
# tmp_date_list.append('1995-07-01')
# tmp_date_list.append('2000-04-01')
# tmp_date_list.append('2009-01-01')
# tmp_date_list.append('1982-01-01') # phase 1 - pi*5/4
# tmp_date_list.append('1987-04-01')
# tmp_date_list.append('2014-07-01')
# tmp_date_list.append('2021-10-01')
# tmp_date_list.append('1984-10-01') # phase 1 - pi*7/4
# tmp_date_list.append('1994-07-01')
# tmp_date_list.append('2006-04-01')
# tmp_date_list.append('2013-01-01')

# second test ensemble
tmp_date_list.append('2004-05-01')
tmp_date_list.append('1985-11-01')
# tmp_date_list.append('1984-01-01')
# tmp_date_list.append('1987-07-01')
#---------------------------------------------------------------------------------------------------
compset = 'F20TR'
grid    = 'ne30pg2_r05_IcoswISC30E3r5'
# ens_id  = '2024-SCIDAC-PCOMP-TEST' # initial test to work out logistical issues
ens_id = '2024-SCIDAC-PCOMP-TEST-01' # second test with alternate land/river configuration
def get_case_name(e,c,h,d): return'.'.join(['E3SM',ens_id,grid,f'EF_{e:0.2f}',f'CF_{c:02.0f}',f'HD_{h:0.2f}',f'{d}'])
#---------------------------------------------------------------------------------------------------
case_list = []
gweff_list, cfrac_list, hdpth_list = [],[],[]
start_date_list = []
def add_case(e,c,h,d):
   gweff_list.append(e)
   cfrac_list.append(c)
   hdpth_list.append(h)
   start_date_list.append(d)
   case_list.append( get_case_name(e,c,h,d) )
#---------------------------------------------------------------------------------------------------
# build list of cases with all dates
for date in tmp_date_list:
   add_case(e=0.35,c=10,h=0.50,d=date) #  <<< v3 default
   # add_case(e=0.12,c=16,h=0.48,d=date) # prev surrogate optimum
   add_case(e=0.09,c=20,h=0.25,d=date) # no QBO at all
   add_case(e=0.70,c=21,h=0.31,d=date) # QBO is too fast

#---------------------------------------------------------------------------------------------------
# for case in case_list:
#     print(case)
# exit()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
for case in case_list :
    #---------------------------------------------------------------------------
    # Input directory
    data_dir = f'{scratch_dir}/{case}/{data_sub}/'
    #---------------------------------------------------------------------------
    # Output directory
    if vert_pressure_remap: 
        odir_sub = f'data_remap_{nlat_dst}x{nlon_dst}_prs'
    else:
        odir_sub = f'data_remap_{nlat_dst}x{nlon_dst}'
    odir = f'{scratch_dir}/{case}/{odir_sub}'
    if not os.path.exists(odir): os.mkdir(odir)
    #---------------------------------------------------------------------------
    print(f'case     : {case}')
    print(f'data dir : {data_dir}')
    print(f'out dir  : {odir}')
    print(f'map file : {map_file}')
    # print(f'log file : {log_file}')
    print('')
    # exit()
    #---------------------------------------------------------------------------
    files = os.listdir(data_dir)
    cnt = 0 
    for f_in in files : 
        remap_flag = False
        if do_h0  and f'{atm_comp}.h0' in f_in : remap_flag = True
        if do_h1  and f'{atm_comp}.h1' in f_in : remap_flag = True
        if do_h2  and f'{atm_comp}.h2' in f_in : remap_flag = True
        # don't remap already remapped data
        if '.remap_' in f_in : remap_flag = False
        if remap_flag :
            cnt += 1
            f_out = f_in.replace('.nc','.remap.nc')
            if os.path.isfile(f_out) :
                if overwrite : os.remove(f_out)
                else : continue
            src_file_name = data_dir+f_in
            #-------------------------------------------------------------------
            dst_file_name = src_file_name.replace('.nc',f'.remap_{nlat_dst}x{nlon_dst}.nc')
            # Change directory
            dst_file_name = dst_file_name.replace(f'/{data_sub}/',f'/{odir_sub}/')
            #-------------------------------------------------------------------
            cmd = f'ncremap -m {map_file} -i {src_file_name} -o {dst_file_name}'
            if vert_pressure_remap: cmd += f' --vrt_fl={pressure_level_file}'
            if print_cmd:
                print(f'\n{tcolor.GREEN}{cmd}{tcolor.ENDC}\n')
            else:
                print('    '+f_in+'  >  '+data_dir+f_out)
            # if write_log: cmd += ' > '+log_file
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
    else:
        print(); print('done.'); print()
#===============================================================================
#===============================================================================
