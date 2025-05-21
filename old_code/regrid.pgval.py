#!/usr/bin/env python

### command for making map file
# SRC=ne30np4 ; ncremap --src_grd=$HOME/E3SM/data_grid/${SRC}_scrip.nc --dst_grd=$HOME/HICCUP/files_grid/scrip_90x180_s2n.nc -m $HOME/maps/map_${SRC}_to_90x180_aave.nc
# SRC=ne45pg2; DST=721x1440 ; ncremap --src_grd=$HOME/E3SM/data_grid/${SRC}_scrip.nc --dst_grd=$HOME/E3SM/data_grid/${DST}_gss_scrip.nc -m $HOME/maps/map_${SRC}_to_${DST}.20201019.nc
# SRC=ne30pg2; DST=721x1440 ; ncremap -a bilinear --esmf_typ=nearestidavg --src_grd=$HOME/E3SM/data_grid/${SRC}_scrip.nc --dst_grd=$HOME/E3SM/data_grid/${DST}_gss_scrip.nc -m $HOME/maps/map_${SRC}_to_${DST}_bilin.20201019.nc

### highorder maps for np4 KE spectra
# NE=30; SRC=ne${NE}np4; DST=721x1440 ; GenerateOverlapMesh --b ${HOME}/E3SM/data_grid/ne${NE}.g --a $HOME/E3SM/data_grid/${DST}_gss_scrip.nc  --out ${HOME}/E3SM/data_grid/overlap_mesh.ne${NE}.${DST}_gss.g
# NE=30; SRC=ne${NE}np4; DST=721x1440 ; GenerateOfflineMap --in_mesh ${HOME}/E3SM/data_grid/ne${NE}.g  --out_mesh $HOME/E3SM/data_grid/${DST}_gss_scrip.nc --ov_mesh ${HOME}/E3SM/data_grid/overlap_mesh.ne${NE}.${DST}_gss.g   --in_type cgll --in_np 4 --out_type fv --out_double --out_format Netcdf4 --correct_areas --out_map $HOME/maps/map_${SRC}_to_${DST}.20201019.nc

### map file for CMIP remap method:
# GRID=ne30np4 ; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRID}_scrip.nc 
# --grd_dst=$HOME/E3SM/data_grid/cmip6_180x360_scrip.20181001.nc
# --map=$HOME/maps/map_${GRID}_to_cmip6_180x360_aave.20200624.nc

### grid files for PMP grids
# ncremap -G ttl='Equi-Angular grid 180x360'#latlon=180,360#lat_typ=uni#lon_typ=grn_wst -g $HOME/E3SM/data_grid/pmp_180x360_scrip.nc
# ncremap -G ttl='CAM-FV grid 121x240'#latlon=121,240#lat_typ=fv#lon_typ=grn_ctr -g $HOME/E3SM/data_grid/pmp_121x240_scrip.nc
# ncremap -G ttl='CAM-FV grid  72x144'#latlon=72,144#lat_typ=fv#lon_typ=grn_wst -g $HOME/E3SM/data_grid/pmp_72x144_scrip.nc

### grid for spherical harmonic analysis
# ncremap -G ttl='Gaussian grid 721x1440'#latlon=721,1440#lat_typ=gss#lon_typ=grn_wst -g $HOME/E3SM/data_grid/721x1440_gss_scrip.nc

### PMP map files
# GRID=ne30np4; NLAT=180; NLON=360; DATESTAMP=20200716; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRID}_scrip.nc  --grd_dst=$HOME/E3SM/data_grid/pmp_${NLAT}x${NLON}_scrip.nc --map=$HOME/maps/map_${GRID}_to_pmp_${NLAT}x${NLON}_aave.${DATESTAMP}.nc
# GRID=ne30pg2; NLAT=180; NLON=360; DATESTAMP=20200716; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRID}_scrip.nc  --grd_dst=$HOME/E3SM/data_grid/pmp_${NLAT}x${NLON}_scrip.nc --map=$HOME/maps/map_${GRID}_to_pmp_${NLAT}x${NLON}_aave.${DATESTAMP}.nc
# GRID=ne30pg3; NLAT=180; NLON=360; DATESTAMP=20200716; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRID}_scrip.nc  --grd_dst=$HOME/E3SM/data_grid/pmp_${NLAT}x${NLON}_scrip.nc --map=$HOME/maps/map_${GRID}_to_pmp_${NLAT}x${NLON}_aave.${DATESTAMP}.nc
# GRID=ne30pg4; NLAT=180; NLON=360; DATESTAMP=20200716; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRID}_scrip.nc  --grd_dst=$HOME/E3SM/data_grid/pmp_${NLAT}x${NLON}_scrip.nc --map=$HOME/maps/map_${GRID}_to_pmp_${NLAT}x${NLON}_aave.${DATESTAMP}.nc

# GRID=ne30np4; NLAT=121; NLON=240; DATESTAMP=20200716; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRID}_scrip.nc  --grd_dst=$HOME/E3SM/data_grid/pmp_${NLAT}x${NLON}_scrip.nc --map=$HOME/maps/map_${GRID}_to_pmp_${NLAT}x${NLON}_aave.${DATESTAMP}.nc
# GRID=ne30pg2; NLAT=121; NLON=240; DATESTAMP=20200716; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRID}_scrip.nc  --grd_dst=$HOME/E3SM/data_grid/pmp_${NLAT}x${NLON}_scrip.nc --map=$HOME/maps/map_${GRID}_to_pmp_${NLAT}x${NLON}_aave.${DATESTAMP}.nc
# GRID=ne30pg3; NLAT=121; NLON=240; DATESTAMP=20200716; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRID}_scrip.nc  --grd_dst=$HOME/E3SM/data_grid/pmp_${NLAT}x${NLON}_scrip.nc --map=$HOME/maps/map_${GRID}_to_pmp_${NLAT}x${NLON}_aave.${DATESTAMP}.nc
# GRID=ne30pg4; NLAT=121; NLON=240; DATESTAMP=20200716; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRID}_scrip.nc  --grd_dst=$HOME/E3SM/data_grid/pmp_${NLAT}x${NLON}_scrip.nc --map=$HOME/maps/map_${GRID}_to_pmp_${NLAT}x${NLON}_aave.${DATESTAMP}.nc

# GRID=ne30np4; NLAT=72; NLON=144; DATESTAMP=20200716; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRID}_scrip.nc  --grd_dst=$HOME/E3SM/data_grid/pmp_${NLAT}x${NLON}_scrip.nc --map=$HOME/maps/map_${GRID}_to_pmp_${NLAT}x${NLON}_aave.${DATESTAMP}.nc
# GRID=ne30pg2; NLAT=72; NLON=144; DATESTAMP=20200716; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRID}_scrip.nc  --grd_dst=$HOME/E3SM/data_grid/pmp_${NLAT}x${NLON}_scrip.nc --map=$HOME/maps/map_${GRID}_to_pmp_${NLAT}x${NLON}_aave.${DATESTAMP}.nc
# GRID=ne30pg3; NLAT=72; NLON=144; DATESTAMP=20200716; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRID}_scrip.nc  --grd_dst=$HOME/E3SM/data_grid/pmp_${NLAT}x${NLON}_scrip.nc --map=$HOME/maps/map_${GRID}_to_pmp_${NLAT}x${NLON}_aave.${DATESTAMP}.nc
# GRID=ne30pg4; NLAT=72; NLON=144; DATESTAMP=20200716; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRID}_scrip.nc  --grd_dst=$HOME/E3SM/data_grid/pmp_${NLAT}x${NLON}_scrip.nc --map=$HOME/maps/map_${GRID}_to_pmp_${NLAT}x${NLON}_aave.${DATESTAMP}.nc

# E3SM.PGVAL.ne30_r05_oECv3.F2010SC5-CMIP6.master-cbe53b
# E3SM.PGVAL.ne30pg2_r05_oECv3.F2010SC5-CMIP6.master-cbe53b
# E3SM.PGVAL.ne30pg3_r05_oECv3.F2010SC5-CMIP6.master-cbe53b
# E3SM.PGVAL.ne30pg4_r05_oECv3.F2010SC5-CMIP6.master-cbe53b

# python regrid.case.py E3SM.PGVAL.ne30_r05_oECv3.F2010SC5-CMIP6.master-cbe53b
# python regrid.case.py E3SM.PGVAL.ne30pg2_r05_oECv3.F2010SC5-CMIP6.master-cbe53b
# python regrid.case.py E3SM.PGVAL.ne30pg3_r05_oECv3.F2010SC5-CMIP6.master-cbe53b
# python regrid.case.py E3SM.PGVAL.ne30pg4_r05_oECv3.F2010SC5-CMIP6.master-cbe53b

#===============================================================================
#===============================================================================
import sys,os
import subprocess as sp
from optparse import OptionParser
parser = OptionParser()
parser.add_option('-n',dest='num_file',default=None,help='sets number of files to print')
parser.add_option('--comp',dest='component',default='eam',help='model component history file to search for')
(opts, args) = parser.parse_args()
#===============================================================================
#===============================================================================
home = os.getenv('HOME')

scratch_dir = os.getenv('SCRATCH')+'/e3sm_scratch/cori-knl/'        ### Cori scratch space
# scratch_dir = os.getenv('MEMBERWORK')+'/cli115/e3sm_scratch/'       ### OLCF scratch space

if scratch_dir=='' :exit('ERROR: scratch directory not set!')
#===============================================================================
#===============================================================================
do_h0, do_h1, do_h2, do_clm, overwrite = False, False, False, False, False

# if len(sys.argv) < 2 :
#     print('ERROR: no case name provided!')
#     exit()
# else :
#     cases = sys.argv[1:]

### comment/uncomment to disable/enable
# do_h0 = True    
# do_h1 = True
do_h2 = True
# do_clm = True

execute   = True
overwrite = True
print_cmd = True
write_log = False

cases = ['E3SM.PGVAL-XTRA.ne30_r05_oECv3.F2010SC5-CMIP6.master-32921c']; src_grid_dyn = 'ne30np4'
# cases = ['E3SM.PGVAL-XTRA.ne30pg3_r05_oECv3.F2010SC5-CMIP6.master-6a7c9b','E3SM.PGVAL-XTRA.ne30pg4_r05_oECv3.F2010SC5-CMIP6.master-6a7c9b']

var_list = ['PTTEND','DYN_PTTEND']
# var_list = ['DYN_PTTEND']

# nlat_dst,nlon_dst =  90,180
# nlat_dst,nlon_dst = 180,360
# nlat_dst,nlon_dst =  72, 144
# nlat_dst,nlon_dst = 121, 240
nlat_dst,nlon_dst = 721,1440  # use this for spherical harmonic analysis (KE spectra)

log_file = './regrid.case.out'

class tcolor: ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'

#===============================================================================
#===============================================================================
for case in cases :

    data_dir = scratch_dir+case+'/run/'
    
    print('case     : '+case)
    print('data_dir : '+data_dir)
    print('log file : '+log_file)
    print('')

    files = os.listdir(data_dir)

    if 'ne30_'     in case: src_grid_name = 'ne30np4'
    if 'ne30pg2_'  in case: src_grid_name = 'ne30pg2'
    if 'ne30pg3_'  in case: src_grid_name = 'ne30pg3'
    if 'ne30pg4_'  in case: src_grid_name = 'ne30pg4'
    if 'ne45pg2_'  in case: src_grid_name = 'ne45pg2'
    if 'ne120pg2_' in case: src_grid_name = 'ne120pg2'
    if 'ne120pg2.' in case: src_grid_name = 'ne120pg2'

    if 'conusx4v1_' in case: src_grid_name = 'conusx4v1'
    if 'conusx4v1pg2_' in case: src_grid_name = 'conusx4v1pg2'

    #---------------------------------------------------------------------------
    # specify map file
    #---------------------------------------------------------------------------
    
    ### CMIP map for E3SM diags
    map_file = f'{home}/maps/map_{src_grid_name}_to_cmip6_{nlat_dst}x{nlon_dst}_aave.20200624.nc'

    ### map for spherical harmonic analysis
    if nlat_dst==721 and nlon_dst==1440:
        # if any( pg in case for pg in ['pg2','pg3','pg4'] ):
        map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}_bilin.20201019.nc'

        if 'pg2' in src_grid_name: src_grid_dyn = src_grid_name.replace('pg2','np4')
        if 'pg3' in src_grid_name: src_grid_dyn = src_grid_name.replace('pg3','np4')
        if 'pg4' in src_grid_name: src_grid_dyn = src_grid_name.replace('pg4','np4')
        map_file_dyn = f'{home}/maps/map_{src_grid_dyn}_to_{nlat_dst}x{nlon_dst}.20201019.nc'

    ### PMP maps 
    # map_file = f'{home}/maps/map_{src_grid_name}_to_pmp_{nlat_dst}x{nlon_dst}_aave.20200716.nc'    

    # map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}.nc'
    # map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}_bilin.nc'

    # if 'conusx4v1_' in case or 'conusx4v1pg2_' in case:
    #     nlat_dst,nlon_dst = 180,360
    #     map_file = f'{home}/maps/map_{src_grid_name}_to_cmip6_{nlat_dst}x{nlon_dst}_aave.20200624.nc'

    # if 'np4' in src_grid_name:
    #     map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}_mono.nc'
    # else:
    #     map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}_aave.nc'

    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    odir_sub = f'data_remap_{nlat_dst}x{nlon_dst}'
    odir = f'{scratch_dir}/{case}/{odir_sub}'
    # odir = f'{scratch_dir}/{case}/data_remap_pmp_{nlat_dst}x{nlon_dst}'

    #------------------------------
    #------------------------------
    # print(tcolor.RED )
    # print('\nWARNING! remapping for DYN variables!\n')
    # print(tcolor.ENDC)
    # sub_dir = sub_dir+'_dyn'
    # odir = f'{scratch_dir}/{case}/{sub_dir}'
    # if 'pg2' in src_grid_name: src_grid_name = src_grid_name.replace('pg2','np4')
    # if 'pg3' in src_grid_name: src_grid_name = src_grid_name.replace('pg3','np4')
    # if 'pg4' in src_grid_name: src_grid_name = src_grid_name.replace('pg4','np4')
    # map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}.20201019.nc'
    #------------------------------
    #------------------------------

    if not os.path.exists(odir): os.mkdir(odir)

    atm_comp = opts.component
    lnd_comp = 'elm'

    atm_comp = 'eam'
    # if 'ne45' in case: atm_comp = 'eam'
    # if 'ne30' in case: atm_comp = 'cam'

    cnt = 0
    for f_in in files : 
        remap_flag = False
        if do_h0  and f'{atm_comp}.h0' in f_in : remap_flag = True
        if do_h1  and f'{atm_comp}.h1' in f_in : remap_flag = True
        if do_h2  and f'{atm_comp}.h2' in f_in : remap_flag = True
        if do_clm and f'{lnd_comp}2.h' in f_in : remap_flag = True

        # don't remap already remapped data
        if '.remap_' in f_in : remap_flag = False

        if remap_flag:
            if do_h1  and f'{atm_comp}.h1' in f_in : tmp = f'{atm_comp}.h1'
            if do_h2  and f'{atm_comp}.h2' in f_in : tmp = f'{atm_comp}.h2'

            ### special logic for KE spectra - use bilin for wind data but conservative for PS
            # if do_h1  and f'{atm_comp}.h1' in f_in : map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}.20201019.nc'
            # if do_h2  and f'{atm_comp}.h2' in f_in : map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}_bilin.20201019.nc'
            
            ### This block will focus on a small subset
            # if 'ne45' in case: tyr = 1
            # if 'ne30' in case: tyr = 4
            # date = f_in.replace(f'{case}.{tmp}.','').replace('-00000.nc','')
            # [yr,mn,dy] = date.split('-')
            # if not ( int(yr)==tyr and int(mn) in [1,2,3,4] ): continue

        if '.remap_' in f_in : remap_flag = False
        
        if remap_flag :
            cnt += 1
            f_out = f_in.replace('.nc','.remap.nc')

            if os.path.isfile(f_out) :
                if overwrite : os.remove(f_out)
                else : continue

            for var in var_list:



                src_file_name = data_dir+f_in
                dst_file_name = src_file_name.replace('.nc',f'.remap_{nlat_dst}x{nlon_dst}.{var}.nc')

                # Change directory
                dst_file_name = dst_file_name.replace('/run/',f'/{odir_sub}/')
                # dst_file_name = dst_file_name.replace('/run/',f'/data_remap_pmp_{nlat_dst}x{nlon_dst}/')

                if 'DYN_' in var:
                    tmp_map_file = map_file_dyn
                else:
                    tmp_map_file = map_file

                if '.ne30_' in case: tmp_map_file = map_file_dyn

                cmd = f'ncremap -v {var} -m {tmp_map_file} -i {src_file_name} -o {dst_file_name}'


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
