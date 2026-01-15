#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
### command for making map file
# SRC=ne30np4 ; ncremap --src_grd=$HOME/E3SM/data_grid/${SRC}_scrip.nc --dst_grd=$HOME/HICCUP/files_grid/scrip_90x180_s2n.nc -m $HOME/maps/map_${SRC}_to_90x180_aave.nc

#---------------------------------------------------------------------------------------------------
### grid and maps for spherical harmonic analysis
# ncremap -G ttl='Gaussian grid 721x1440'#latlon=721,1440#lat_typ=gss#lon_typ=grn_wst -g $HOME/E3SM/data_grid/721x1440_gss_scrip.nc

# SRC=ne45pg2; DST=721x1440 ; ncremap --src_grd=$HOME/E3SM/data_grid/${SRC}_scrip.nc --dst_grd=$HOME/E3SM/data_grid/${DST}_gss_scrip.nc -m $HOME/maps/map_${SRC}_to_${DST}.20201019.nc
# SRC=ne45pg2; DST=721x1440 ; ncremap -a bilinear --esmf_typ=nearestidavg --src_grd=$HOME/E3SM/data_
# grid/${SRC}_scrip.nc --dst_grd=$HOME/E3SM/data_grid/${DST}_gss_scrip.nc -m $HOME/maps/map_${SRC}_to_${DST}_bilin.20201019.nc

#---------------------------------------------------------------------------------------------------
### highorder maps for np4 KE spectra
# NE=30; SRC=ne${NE}np4; DST=721x1440 ; GenerateOverlapMesh --b ${HOME}/E3SM/data_grid/ne${NE}.g --a $HOME/E3SM/data_grid/${DST}_gss_scrip.nc  --out ${HOME}/E3SM/data_grid/overlap_mesh.ne${NE}.${DST}_gss.g
# NE=30; SRC=ne${NE}np4; DST=721x1440 ; GenerateOfflineMap --in_mesh ${HOME}/E3SM/data_grid/ne${NE}.g  --out_mesh $HOME/E3SM/data_grid/${DST}_gss_scrip.nc --ov_mesh ${HOME}/E3SM/data_grid/overlap_mesh.ne${NE}.${DST}_gss.g   --in_type cgll --in_np 4 --out_type fv --out_double --out_format Netcdf4 --correct_areas --out_map $HOME/maps/map_${SRC}_to_${DST}.20201019.nc

#---------------------------------------------------------------------------------------------------
### map file for CMIP remap method:
# GRIDIN=ne30pg2; GRIDOUT=90x180 ; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRIDIN}_scrip.nc --grd_dst=$HOME/E3SM/data_grid/cmip6_${GRIDOUT}_scrip.20181001.nc --map=$HOME/maps/map_${GRID}_to_cmip6_180x360_aave.nc

# GRIDIN=ne30pg2; GRIDOUT=90x180 ; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRIDIN}_scrip.nc --grd_dst=$HOME/E3SM/data_grid/${GRIDOUT}_scrip.nc --map=$HOME/maps/map_${GRID}_to_${GRIDOUT}_aave.nc

#---------------------------------------------------------------------------------------------------
### grid files for PMP grids
# ncremap -G ttl='Equi-Angular grid 180x360'#latlon=180,360#lat_typ=uni#lon_typ=grn_wst -g $HOME/E3SM/data_grid/pmp_180x360_scrip.nc
# ncremap -G ttl='CAM-FV grid 121x240'#latlon=121,240#lat_typ=fv#lon_typ=grn_ctr -g $HOME/E3SM/data_grid/pmp_121x240_scrip.nc
# ncremap -G ttl='CAM-FV grid  72x144'#latlon=72,144#lat_typ=fv#lon_typ=grn_wst -g $HOME/E3SM/data_grid/pmp_72x144_scrip.nc

#---------------------------------------------------------------------------------------------------
### map files

# GRID=ne30pg2; NLAT=180; NLON=360; DATESTAMP=20240508; ncremap -6 --alg_typ=traave --grd_src=$HOME/E3SM/data_grid/${GRID}_scrip.nc  --grd_dst=$HOME/E3SM/data_grid/${NLAT}x${NLON}_scrip.nc --map=$HOME/maps/map_${GRID}_to_${NLAT}x${NLON}_traave.${DATESTAMP}.nc

# GRID=ne30pg2; NLAT=180; NLON=360; DATESTAMP=20200716; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRID}_scrip.nc  --grd_dst=$HOME/E3SM/data_grid/pmp_${NLAT}x${NLON}_scrip.nc --map=$HOME/maps/map_${GRID}_to_pmp_${NLAT}x${NLON}_aave.${DATESTAMP}.nc
# GRID=ne30pg2; NLAT=121; NLON=240; DATESTAMP=20200716; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRID}_scrip.nc  --grd_dst=$HOME/E3SM/data_grid/pmp_${NLAT}x${NLON}_scrip.nc --map=$HOME/maps/map_${GRID}_to_pmp_${NLAT}x${NLON}_aave.${DATESTAMP}.nc
# GRID=ne30pg2; NLAT=72;  NLON=144; DATESTAMP=20200716; ncremap -6 --alg_typ=aave --grd_src=$HOME/E3SM/data_grid/${GRID}_scrip.nc  --grd_dst=$HOME/E3SM/data_grid/pmp_${NLAT}x${NLON}_scrip.nc --map=$HOME/maps/map_${GRID}_to_pmp_${NLAT}x${NLON}_aave.${DATESTAMP}.nc

#---------------------------------------------------------------------------------------------------
# command to create CMIP6 HighResMIP vertical pressure coordinate file
# ncap2 -O -v -s 'defdim("plev",27);plev[$plev]={100000,97500,95000,92500,90000,87500,85000,82500,80000,77500,75000,70000,65000,60000,55000,50000,45000,40000,35000,30000,25000,22500,20000,17500,15000,12500,10000};' ~/E3SM/vert_grid_files/vrt_prs_CMIP6.nc

#---------------------------------------------------------------------------------------------------
'''
./regrid.case.py --scratch=/gpfs/alpine2/atm146/proj-shared/hannah6/e3sm_scratch/  E3SM.2024-PAM-CHK-04.ne30pg2_oECv3.F2010-MMF2

python ~/E3SM/regrid.case.py --map=~/maps/map_ne30pg2_to_90x180_traave.nc --scratch=/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu --sub=run --case=E3SM.2024-coriolis-00.GNUGPU.ne30pg2_oECv3.F2010-MMF1.NXY_64_1.NHS-off.NCT-off
python ~/E3SM/regrid.case.py --map=~/maps/map_ne30pg2_to_90x180_traave.nc --scratch=/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu --sub=run --case=E3SM.2024-coriolis-00.GNUGPU.ne30pg2_oECv3.F2010-MMF1.NXY_64_1.NHS-on.NCT-off
python ~/E3SM/regrid.case.py --map=~/maps/map_ne30pg2_to_90x180_traave.nc --scratch=/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu --sub=run --case=E3SM.2024-coriolis-00.GNUGPU.ne30pg2_oECv3.F2010-MMF1.NXY_64_1.NHS-on.NCT-on

2024 Rotating RCE runs
nohup time python ~/E3SM/regrid.case.py --map=~/maps/map_ne30pg2_to_90x180_traave.nc --scratch=/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu --sub=run --case=E3SM.2024-RCEROT-01.FRCEROT                              > remap.RCEROT.EAM.300.out &
nohup time python ~/E3SM/regrid.case.py --map=~/maps/map_ne30pg2_to_90x180_traave.nc --scratch=/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu --sub=run --case=E3SM.2024-RCEROT-01.FRCEROT-320                          > remap.RCEROT.EAM.320.out & 
nohup time python ~/E3SM/regrid.case.py --map=~/maps/map_ne30pg2_to_90x180_traave.nc --scratch=/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu --sub=run --case=E3SM.2024-RCEROT-01.FRCEROT-MMF1.NX_128x1.DX_1000        > remap.RCEROT.MMF.300.out &
nohup time python ~/E3SM/regrid.case.py --map=~/maps/map_ne30pg2_to_90x180_traave.nc --scratch=/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu --sub=run --case=E3SM.2024-RCEROT-01.FRCEROT-320-MMF1.NX_128x1.DX_1000    > remap.RCEROT.MMF.320.out & 
 

2024-02-25
login27 & login09

'''
#---------------------------------------------------------------------------------------------------
home = os.getenv('HOME')

# scratch_dir = opts.scratch

# scratch_dir = '/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu'              ### Perlmutter scratch space
# scratch_dir = '/gpfs/alpine2/atm146/proj-shared/hannah6/e3sm_scratch/'  ### OLCF Summit scratch space
# scratch_dir = '/lcrc/group/e3sm/ac.whannah/E3SMv3_dev'                  ### Chrysalis scratch space

if scratch_dir=='' :exit('ERROR: scratch directory not set!')
#---------------------------------------------------------------------------------------------------
do_h0, do_h1, do_h2, do_clm, overwrite = False, False, False, False, False

# if len(sys.argv) < 2 :
#     print('ERROR: no case name provided!')
#     exit()
# else :
#     cases = sys.argv[1:]

# # omit flags from case list
# for c in cases: 
#     if c[0]=='-': cases.remove(c)


# if cases==['RGMA']:
#     cases = []
#     cases.append('E3SM.RGMA.ne120pg2_r05_oECv3.FC5AV1C-H01A.00')
#     cases.append('E3SM.RGMA.ne30pg2_r05_oECv3.F-MMF1.CRMNX_64.CRMDX_2000.RADNX_4.00')
#     cases.append('E3SM.RGMA.ne30pg2_r05_oECv3.FC5AV1C-L.00')


### comment/uncomment to disable/enable
do_h0 = True
do_h1 = True
do_h2 = True
# do_clm = True

# htype = 'hb_mse'      # comment to disable

execute   = True
overwrite = True
print_cmd = True
# write_log = False

nlat_dst,nlon_dst =  90,180
# nlat_dst,nlon_dst = 180,360
# nlat_dst,nlon_dst =  72, 144
# nlat_dst,nlon_dst = 121, 240
# nlat_dst,nlon_dst = 721,1440  # use this for spherical harmonic analysis (KE spectra)

map_file = opts.map_file

# pressure_levels = 1000,975,950,925,900,875,850,825,800,775,750,700,650,600,550,500,450,400,350,300,250,225,200,175,150,125,100

# log_file = './regrid.case.out'

class tcolor: ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'

#===============================================================================
#===============================================================================
# for case in cases :
if True:

    case = opts.case

    #---------------------------------------------------------------------------
    # Input directory
    #---------------------------------------------------------------------------
    # data_sub = 'run'
    data_sub = opts.data_sub
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
    # print(f'log file : {log_file}')
    print('')
    # exit()

    files = os.listdir(data_dir)

    if 'ne30_'     in case: src_grid_name = 'ne30np4'
    if 'ne30pg2_'  in case: src_grid_name = 'ne30pg2'
    if 'ne30pg2.'  in case: src_grid_name = 'ne30pg2'
    if 'ne30pg3_'  in case: src_grid_name = 'ne30pg3'
    if 'ne30pg4_'  in case: src_grid_name = 'ne30pg4'
    if 'ne45pg2_'  in case: src_grid_name = 'ne45pg2'
    if 'ne120pg2_' in case: src_grid_name = 'ne120pg2'
    if 'ne120pg2.' in case: src_grid_name = 'ne120pg2'

    if 'conusx4v1_'    in case: src_grid_name = 'conusx4v1'
    if 'conusx4v1pg2_' in case: src_grid_name = 'conusx4v1pg2'

    # if 'AQUA-RRM-TEST' in case: 
    #     nlat_dst,nlon_dst = 180,360
    #     src_grid_name = 'RRM_cubeface_grad_ne30x3pg2'
    #     map_file = f'{home}/maps/map_{src_grid_name}_to_cmip6_{nlat_dst}x{nlon_dst}_aave.20210913.nc'

    if 'E3SM.PI-CPL.v1.' in case: src_grid_name = 'ne30np4'
    if 'E3SM.PI-CPL.v2.' in case: src_grid_name = 'ne30pg2'

    #---------------------------------------------------------------------------
    # specify map file
    #---------------------------------------------------------------------------
    
    ### CMIP map for E3SM diags
    # if 'map_file' not in locals():
        #map_file = f'{home}/maps/map_{src_grid_name}_to_cmip6_{nlat_dst}x{nlon_dst}_aave.nc'
        # map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}_aave.nc'

    # if 'map_file' not in locals() and nlat_dst==180 and nlon_dst==360:
    #     map_file = f'{home}/maps/map_{src_grid_name}_to_cmip6_{nlat_dst}x{nlon_dst}_aave.20200624.nc'

    ### map for spherical harmonic analysis
    # print(tcolor.RED )
    # print('----------------------------------------------------------------------------------------')
    # print('WARNING - mapping a SUBSET to a high-res grid for spherical harmonic analysis')
    # print('----------------------------------------------------------------------------------------')
    # print(tcolor.ENDC)

    # if nlat_dst==721 and nlon_dst==1440:
    #     if any( pg in case for pg in ['pg2','pg3','pg4'] ):
    #         map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}_bilin.20201019.nc'
    #     else:
    #         map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}.20201019.nc'

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

    # if 'INCITE2019' in case: map_file = f'$HOME/maps/map_ne120pg2_to_{nlat_dst}x{nlon_dst}_aave.nc'

    ### map file for np4 > pg2 (not sure how to do this...)
    # if 'map_file' not in locals():
    #     if 'pg2' in 
    #     map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}_aave.nc'

    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------

    if not os.path.exists(odir): os.mkdir(odir)

    atm_comp,lnd_comp = 'eam','elm'
    # if 'E3SM.PI-CPL.v1.' in case: atm_comp,lnd_comp = 'cam','clm'
        

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

        # if remap_flag:
            # if do_h1  and f'{atm_comp}.h1' in f_in : tmp = f'{atm_comp}.h1'
            # if do_h2  and f'{atm_comp}.h2' in f_in : tmp = f'{atm_comp}.h2'

            # if 'htype' in locals():
            #     if f'{atm_comp}.{htype}.' in f_in : tmp = f'{atm_comp}.{htype}'

            ### special logic for KE spectra - use bilin for wind data but conservative for PS
            # if do_h1  and f'{atm_comp}.h1' in f_in : map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}.20201019.nc'
            # if do_h2  and f'{atm_comp}.h2' in f_in : map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}_bilin.20201019.nc'
        
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
    # if 'E3SM.RGMA.' in case: atm_comp,lnd_comp = 'cam','clm'
        

        print('\nNo files found for remapping...?\n')

#===============================================================================
#===============================================================================
