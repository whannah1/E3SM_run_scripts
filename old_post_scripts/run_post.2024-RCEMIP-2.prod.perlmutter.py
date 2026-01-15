#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
'''
Below are commands to create grid and map files. 
copying and pasting all this into the terminal should work if
 - the directories ~/grids and ~/maps exist
 - NCO is installed in your path or conda environment

source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh

NE=30
SRC_GRID=ne${NE}pg2
DST_NY=180
DST_NX=360
DST_GRID=${DST_NY}x${DST_NX}

GRID_FILE_PATH=~/grids
SRC_GRID_FILE=${GRID_FILE_PATH}/${SRC_GRID}_scrip.nc
DST_GRID_FILE=${GRID_FILE_PATH}/${DST_GRID}_scrip.nc
MAP_FILE=~/maps/map_${SRC_GRID}_to_${DST_GRID}_aave.nc

# generate model grid file
GenerateCSMesh --alt --res ${NE} --file ${GRID_FILE_PATH}/ne${NE}.g
GenerateVolumetricMesh --in ${GRID_FILE_PATH}/ne${NE}.g --out ${GRID_FILE_PATH}/ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${GRID_FILE_PATH}/ne${NE}pg2.g --out ${GRID_FILE_PATH}/ne${NE}pg2_scrip.nc

# generate lat/lon grid file
ncremap -g ${DST_GRID_FILE} -G ttl="Equi-Angular grid, dimensions ${DST_GRID}, cell edges on Poles/Equator and Prime Meridian/Date Line"#latlon=${DST_NY},${DST_NX}#lat_typ=uni#lon_typ=grn_wst

# generate map file
ncremap -6 --alg_typ=aave --grd_src=$SRC_GRID_FILE --grd_dst=$DST_GRID_FILE --map=$MAP_FILE

'''
#---------------------------------------------------------------------------------------------------
'''
make sure to active the env and source the file with authorization:
conda activate swift_env
source ~/.swiftenv
'''
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
unified_env = '/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh'
def print_line():print(' '*2+'-'*80)
def run_cmd(cmd): 
   print('\n'+clr.GREEN+cmd+clr.END);
   os.system(cmd); 
   return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, glob, datetime, time
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning) # supress FutureWarning from pandas
import xarray as xr, numpy as np, pandas
#---------------------------------------------------------------------------------------------------
# set all flags to False by default - uncomment below to enable
st_archive,lt_archive_create,lt_archive_update,cp_post_to_cfs = False,False,False,False
delete_h1,delete_h3,delete_h3_remap = False,False,False
calc_global_mean_h0, calc_global_mean_h1, cmorization = False, False, False
remap_h0, remap_h1, remap_h2, remap_h3 = False, False, False, False
DKRZ_upload,DKRZ_upload_docs = False,False
delete_all_data = False
lt_archive_extract_3D = False
#---------------------------------------------------------------------------------------------------

acct = 'm3312'

# st_archive           = True
# lt_archive_create    = True
# lt_archive_update    = True
lt_archive_check  = True

# calc_global_mean_h0  = True
# calc_global_mean_h1  = True
### delete_h1          = True
### delete_h3          = True
### delete_h3_remap    = True
# remap_h0             = True
# remap_h2             = True
# remap_h3             = True
# cmorization          = True
# DKRZ_upload          = True # make sure to check env and "dim_list"
# DKRZ_upload_docs     = True
delete_all_data          = True
# lt_archive_extract_3D    = True

# extra flags for cmorization section
cmor_do_table_1 = True
cmor_do_table_2 = True
cmor_do_table_3 = True
cmor_do_table_4 = True

#-------------------------------------------------------------------------------
case_list,root_list = [],[]
mdl_list,exp_list = [],[]
def add_case(case,root,mdl,exp):
   case_list.append(case); root_list.append(root)
   mdl_list.append(mdl); exp_list.append(exp)
#-------------------------------------------------------------------------------

scratch_root_cpu = '/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu'
scratch_root_gpu = '/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu'

add_case( 'E3SM.2024-RCEMIP2.FRCE_295'                 ,scratch_root_cpu,'E3SM',    '295' )
add_case( 'E3SM.2024-RCEMIP2.FRCE_300'                 ,scratch_root_cpu,'E3SM',    '300' )
add_case( 'E3SM.2024-RCEMIP2.FRCE_305'                 ,scratch_root_cpu,'E3SM',    '305' )
add_case( 'E3SM.2024-RCEMIP2.FRCE-MW_295dT1p25'        ,scratch_root_cpu,'E3SM',    'MW_295dT1p25' )
add_case( 'E3SM.2024-RCEMIP2.FRCE-MW_300dT0p625'       ,scratch_root_cpu,'E3SM',    'MW_300dT0p625' )
add_case( 'E3SM.2024-RCEMIP2.FRCE-MW_300dT1p25'        ,scratch_root_cpu,'E3SM',    'MW_300dT1p25' )
add_case( 'E3SM.2024-RCEMIP2.FRCE-MW_300dT2p5'         ,scratch_root_cpu,'E3SM',    'MW_300dT2p5' )
add_case( 'E3SM.2024-RCEMIP2.FRCE-MW_305dT1p25'        ,scratch_root_cpu,'E3SM',    'MW_305dT1p25' )   ### corrupted archive :(
add_case( 'E3SM.2024-RCEMIP2.FRCE-MMF1_295'            ,scratch_root_gpu,'E3SM-MMF','295' )
add_case( 'E3SM.2024-RCEMIP2.FRCE-MMF1_300'            ,scratch_root_gpu,'E3SM-MMF','300' )
add_case( 'E3SM.2024-RCEMIP2.FRCE-MMF1_305'            ,scratch_root_gpu,'E3SM-MMF','305' )            ### corrupted archive :(
add_case( 'E3SM.2024-RCEMIP2.FRCE-MW-MMF1_295dT1p25'   ,scratch_root_gpu,'E3SM-MMF','MW_295dT1p25' )   ### corrupted archive :(
add_case( 'E3SM.2024-RCEMIP2.FRCE-MW-MMF1_300dT0p625'  ,scratch_root_gpu,'E3SM-MMF','MW_300dT0p625' )  ### corrupted archive :(
add_case( 'E3SM.2024-RCEMIP2.FRCE-MW-MMF1_300dT1p25'   ,scratch_root_gpu,'E3SM-MMF','MW_300dT1p25' )   ### corrupted archive :(
add_case( 'E3SM.2024-RCEMIP2.FRCE-MW-MMF1_300dT2p5'    ,scratch_root_gpu,'E3SM-MMF','MW_300dT2p5' )
add_case( 'E3SM.2024-RCEMIP2.FRCE-MW-MMF1_305dT1p25'   ,scratch_root_gpu,'E3SM-MMF','MW_305dT1p25' )   ### corrupted archive :(

'''
source /global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh

# bad archive data?
E3SM.2024-RCEMIP2.FRCE-MW_305dT1p25
E3SM.2024-RCEMIP2.FRCE-MMF1_305
E3SM.2024-RCEMIP2.FRCE-MW-MMF1_295dT1p25
E3SM.2024-RCEMIP2.FRCE-MW-MMF1_300dT0p625
E3SM.2024-RCEMIP2.FRCE-MW-MMF1_300dT1p25
E3SM.2024-RCEMIP2.FRCE-MW-MMF1_305dT1p25

cd /pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/E3SM.2024-RCEMIP2.FRCE-MW_305dT1p25
zstash extract --hpss=E3SM/2024-RCEMIP2/E3SM.2024-RCEMIP2.FRCE-MW_305dT1p25 "data_final/E3SM_MW_305dT1p25_3D_cldfrac.nc  data_final/E3SM_MW_305dT1p25_3D_cli.nc  data_final/E3SM_MW_305dT1p25_3D_clisccp.nc  data_final/E3SM_MW_305dT1p25_3D_clw.nc  data_final/E3SM_MW_305dT1p25_3D_hus.nc  data_final/E3SM_MW_305dT1p25_3D_mc.nc  data_final/E3SM_MW_305dT1p25_3D_ta.nc  data_final/E3SM_MW_305dT1p25_3D_tntc.nc  data_final/E3SM_MW_305dT1p25_3D_tntrl.nc  data_final/E3SM_MW_305dT1p25_3D_tntrlcs.nc  data_final/E3SM_MW_305dT1p25_3D_tntrs.nc "
zstash extract --hpss=E3SM/2024-RCEMIP2/E3SM.2024-RCEMIP2.FRCE-MW_305dT1p25 "data_final/E3SM_MW_305dT1p25_3D_cldfrac.nc"

hsi get /home/w/whannah/E3SM/2024-RCEMIP2/E3SM.2024-RCEMIP2.FRCE-MW_305dT1p25/00000a.tar

> tar -tf 00000a.tar
zstash_create_E3SM.2024-RCEMIP2.FRCE-MW_305dT1p25_2024-08-03.061940.log
zstash_update_E3SM.2024-RCEMIP2.FRCE-MW_305dT1p25_2024-09-04.012718.log
tar: Skipping to next header
tar: Exiting with failure status due to previous errors

cpio --list 00000a.tar
cpio -ivd -H ustar < 00000a.tar

'''


'''
nohup time python -u run_post.2024-RCEMIP-2.prod.perlmutter.py > rcemip.prod.FRCE_all.out &
nohup time python -u run_post.2024-RCEMIP-2.prod.perlmutter.py > rcemip.prod.FRCE_mmf.out &
nohup time python -u run_post.2024-RCEMIP-2.prod.perlmutter.py > rcemip.prod.FRCE_mmf_295.out &
nohup time python -u run_post.2024-RCEMIP-2.prod.perlmutter.py > rcemip.prod.FRCE_mmf_300.out &
nohup time python -u run_post.2024-RCEMIP-2.prod.perlmutter.py > rcemip.prod.FRCE_mmf_all.out &
nohup time python -u run_post.2024-RCEMIP-2.prod.perlmutter.py > rcemip.prod.lt_archive_update.out &
nohup time python -u run_post.2024-RCEMIP-2.prod.perlmutter.py > rcemip.prod.DKRZ_upload.out & 
'''

hpss_root = 'E3SM/2024-RCEMIP2'

dst_nlat =  90
dst_nlon = 180
map_file = '/global/homes/w/whannah/maps/map_ne30pg2_to_90x180_traave.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(case,root,mdl,exp):
   if case is None: exit(' case argument not provided?')
   if root is None: exit(' root argument not provided?')
   case_root = f'{root}/{case}'
   # print(case); return
   #------------------------------------------------------------------------------------------------
   print_line()
   print(f'  case : {clr.BOLD}{case}{clr.END} \n')
   #------------------------------------------------------------------------------------------------
   if st_archive:
      os.chdir(f'{case_root}/case_scripts')
      run_cmd(f'./xmlchange DOUT_S_ROOT={case_root}/archive ')
      run_cmd('./case.st_archive')
   #------------------------------------------------------------------------------------------------
   '''
   CASE=E3SM.2024-RCEMIP2.FRCE-MW-MMF1_295dT1p25;zstash ls --hpss=E3SM/2024-RCEMIP2/${CASE} "data_final/*3D*"
   '''
   #------------------------------------------------------------------------------------------------
   if lt_archive_create:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Create the HPSS archive
      run_cmd(f'source {unified_env}; zstash create --hpss={hpss_root}/{case} . 2>&1 | tee zstash_create_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if lt_archive_update:
      print(f'\n{clr.GREEN}cd {case_root}{clr.END}');
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      run_cmd(f'source {unified_env}; zstash update --hpss={hpss_root}/{case}  2>&1 | tee zstash_update_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if lt_archive_extract_3D:
      print(f'\n{clr.GREEN}cd {case_root}{clr.END}');
      os.chdir(f'{case_root}')
      run_cmd(f'source {unified_env}; zstash extract --hpss={hpss_root}/{case} "data_final/*3D*" ')
   #------------------------------------------------------------------------------------------------
   if calc_global_mean_h0:
      htype = 'h0'
      file_list = sorted(glob.glob(f'{case_root}/archive/atm/hist/{case}.eam.{htype}.*'))
      for f in range(len(file_list)):
         ifile = file_list[f] ; ofile = ifile.replace(f'.eam.{htype}.',f'.eam.{htype}g.')
         print('\n'+f'    ifile: {ifile}')
         print(     f'    ofile: {ofile}')
         ds_out = calc_global_mean( xr.open_mfdataset(ifile) )
         ds_out.to_netcdf(path=ofile,mode='w')
   #------------------------------------------------------------------------------------------------
   if calc_global_mean_h1:
      htype = 'h1'
      file_list = sorted(glob.glob(f'{case_root}/archive/atm/hist/{case}.eam.{htype}.*'))
      for f in range(len(file_list)):
         ifile = file_list[f] ; ofile = ifile.replace(f'.eam.{htype}.',f'.eam.{htype}g.')
         print('\n'+f'    ifile: {ifile}')
         print(     f'    ofile: {ofile}')
         ds_out = calc_global_mean( xr.open_mfdataset(ifile) )
         ds_out.to_netcdf(path=ofile,mode='w')
   #------------------------------------------------------------------------------------------------
   if delete_h1:
      htype = 'h1'
      print(' '*2+f'{clr.RED}WARNING - DELETEING {htype} FILES!{clr.END}');
      time.sleep(4) # give the user a few seconds to reconsider
      file_list = sorted(glob.glob(f'{case_root}/archive/atm/hist/{case}.eam.{htype}.*'))
      for f in file_list:
         print(' '*4+f'Deleting file: {clr.CYAN}{f}{clr.END}');
         os.remove(f)
   #------------------------------------------------------------------------------------------------
   if delete_h3:
      htype = 'h3'
      print(' '*2+f'{clr.RED}WARNING - DELETEING {htype} FILES!{clr.END}');
      time.sleep(4) # give the user a few seconds to reconsider
      file_list = sorted(glob.glob(f'{case_root}/archive/atm/hist/{case}.eam.{htype}.*'))
      for f in file_list:
         print(' '*4+f'Deleting file: {clr.CYAN}{f}{clr.END}');
         os.remove(f)
   #------------------------------------------------------------------------------------------------
   if delete_h3_remap:
      htype = 'h3'
      print(' '*2+f'{clr.RED}WARNING - DELETEING {htype} FILES!{clr.END}');
      time.sleep(4) # give the user a few seconds to reconsider
      file_list = sorted(glob.glob(f'{case_root}/data_remap_90x180/{case}.eam.{htype}.*'))
      for f in file_list:
         print(' '*4+f'Deleting file: {clr.CYAN}{f}{clr.END}');
         os.remove(f)
   #------------------------------------------------------------------------------------------------
   remap_src_sub  = 'archive/atm/hist'
   remap_dst_sub  = f'data_remap_{dst_nlat}x{dst_nlon}'
   remap_src_root = f'{root}/{case}/{remap_src_sub}'
   remap_dst_root = f'{root}/{case}/{remap_dst_sub}'
   if not os.path.exists(remap_dst_root): os.mkdir(remap_dst_root)
   #------------------------------------------------------------------------------------------------
   def remap_batch(htype,map_file,remap_src_root,remap_dst_root):
      indent = ' '*4
      print(indent+f'{clr.MAGENTA}Begin remapping {htype} data{clr.END}')
      src_file_list = sorted( glob.glob(f'{remap_src_root}/{case}.eam.{htype}.*'))
      if len(src_file_list)==0:
         print(indent+f'  {clr.RED}No {htype} files found? Skipping.{clr.END}')
      for src_file in src_file_list:
         dst_file = src_file.replace('.nc',f'.remap_{dst_nlat}x{dst_nlon}.nc')
         dst_file = dst_file.replace(remap_src_root,remap_dst_root)
         run_cmd(f'ncremap -m {map_file} -i {src_file} -o {dst_file}')
   #------------------------------------------------------------------------------------------------
   if remap_h0: remap_batch('h0',map_file,remap_src_root,remap_dst_root)
   if remap_h2: remap_batch('h2',map_file,remap_src_root,remap_dst_root)
   if remap_h3: remap_batch('h3',map_file,remap_src_root,remap_dst_root)
   #------------------------------------------------------------------------------------------------
   # if remap_h0:
   #    htype = 'h0'
   #    print(indent+f'{clr.MAGENTA}Begin remapping {htype} data{clr.END}')
   #    src_file_list = sorted( glob.glob(f'{remap_src_root}/{case}.eam.{htype}.*'))
   #    for src_file in src_file_list:
   #       dst_file = src_file.replace('.nc',f'.remap_{dst_nlat}x{dst_nlon}.nc')
   #       dst_file = dst_file.replace(remap_src_root,remap_dst_root)
   #       run_cmd(f'ncremap -m {map_file} -i {src_file} -o {dst_file}')
   # #------------------------------------------------------------------------------------------------
   # if remap_h2:
   #    htype = 'h2'
   #    print(indent+f'{clr.MAGENTA}Begin remapping {htype} data{clr.END}')
   #    src_file_list = sorted( glob.glob(f'{remap_src_root}/{case}.eam.{htype}.*'))
   #    for src_file in src_file_list:
   #       dst_file = src_file.replace('.nc',f'.remap_{dst_nlat}x{dst_nlon}.nc')
   #       dst_file = dst_file.replace(remap_src_root,remap_dst_root)
   #       run_cmd(f'ncremap -m {map_file} -i {src_file} -o {dst_file}')
   # #------------------------------------------------------------------------------------------------
   # if remap_h3:
   #    htype = 'h3'
   #    print(indent+f'{clr.MAGENTA}Begin remapping {htype} data{clr.END}')
   #    src_file_list = sorted( glob.glob(f'{remap_src_root}/{case}.eam.{htype}.*'))
   #    for src_file in src_file_list:
   #       dst_file = src_file.replace('.nc',f'.remap_{dst_nlat}x{dst_nlon}.nc')
   #       dst_file = dst_file.replace(remap_src_root,remap_dst_root)
   #       run_cmd(f'ncremap -m {map_file} -i {src_file} -o {dst_file}')
   #------------------------------------------------------------------------------------------------
   if cmorization:
      dst_root = f'{root}/{case}/data_final'
      if not os.path.exists(dst_root): os.mkdir(dst_root)
      indent = ' '*4
      #-------------------------------------------------------------------------
      if 'cmor_do_table_1' not in globals(): global cmor_do_table_1
      if 'cmor_do_table_2' not in globals(): global cmor_do_table_2
      if 'cmor_do_table_3' not in globals(): global cmor_do_table_3
      if 'cmor_do_table_4' not in globals(): global cmor_do_table_4
      if 'cmor_do_table_1' not in globals(): cmor_do_table_1 = False
      if 'cmor_do_table_2' not in globals(): cmor_do_table_2 = False
      if 'cmor_do_table_3' not in globals(): cmor_do_table_3 = False
      if 'cmor_do_table_4' not in globals(): cmor_do_table_4 = False
      #-------------------------------------------------------------------------
      # TA1 - 0D (t)    1-hr  h0
      if cmor_do_table_1:
         print(indent+f'{clr.MAGENTA}Begin CMORization of 0D data{clr.END}')
         htype, dim, src_root = 'h0g', '0D', f'{root}/{case}/archive/atm/hist'
         create_cmor( mdl, exp, dim, src_root, dst_root, htype, 'pr_avg',     'kg m−2 s−1', 'domain avg. suface precipitation rate' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'hfls_avg',   'Wm−2',       'domain avg. surface upward latent heat flux' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'hfss_avg',   'Wm−2',       'domain avg. surface upward sensible heat flux' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'prw_avg',    'kg m−2',     'domain avg. water vapor path' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'sprw_avg',   'kg m−2',     'domain avg. saturated water vapor path' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'clwvi_avg',  'kg m−2',     'domain avg. condensed water path (cloud ice + cloud liquid)' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'clivi_avg',  'kg m−2',     'domain avg. ice water path (cloud ice)' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rlds_avg',   'Wm−2',       'domain avg. surface downwelling longwave flux' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rlus_avg',   'Wm−2',       'domain avg. surface upwelling longwave flux' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rsds_avg',   'Wm−2',       'domain avg. surface downwelling shortwave flux' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rsus_avg',   'Wm−2',       'domain avg. surface upwelling shortwave flux' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rsdscs_avg', 'Wm−2',       'domain avg. surface downwelling shortwave flux - clear sky' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rsuscs_avg', 'Wm−2',       'domain avg. surface upwelling shortwave flux - clear sky' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rldscs_avg', 'Wm−2',       'domain avg. surface downwelling longwave flux - clear sky' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rluscs_avg', 'Wm−2',       'domain avg. surface upwelling longwave flux - clear sky' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rsdt_avg',   'Wm−2',       'domain avg. TOA incoming shortwave flux' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rsut_avg',   'Wm−2',       'domain avg. TOA outgoing shortwave flux' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rlut_avg',   'Wm−2',       'domain avg. TOA outgoing longwave flux' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rsutcs_avg', 'Wm−2',       'domain avg. TOA outgoing shortwave flux - clear sky' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rlutcs_avg', 'Wm−2',       'domain avg. TOA outgoing longwave flux - clear sky' )
      #-------------------------------------------------------------------------
      # TA2 - 1D (z,t)     1-hr  h1
      if cmor_do_table_2:
         print(indent+f'{clr.MAGENTA}Begin CMORization of 1D data{clr.END}')
         htype, dim, src_root = 'h1g', '1D', f'{root}/{case}/archive/atm/hist'
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'ta_avg',      'K',     'domain avg. air temperaure profile' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'ua_avg',      'm s−1', 'domain avg. eastward wind profile' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'va_avg',      'm s−1', 'domain avg. northward wind profile' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'hus_avg',     'kg/kg', 'domain avg. specific humidity profile' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'hur_avg',     '%',     'domain avg. relative humidity profile' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'clw_avg',     'kg/kg', 'domain avg. mass fraction of cloud liquid water profile' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'cli_avg',     'kg/kg', 'domain avg. mass fraction of cloud ice profile' )
         # create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'plw_avg',     'kg/kg', 'domain avg. mass fraction of precipitating liquid water profile' )
         # create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'pli_avg',     'kg/kg', 'domain avg. mass fraction of precipitating ice profile' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'theta_avg',   'K',     'domain avg. potential temperature profile' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'thetae_avg',  'K',     'domain avg. equivalent potential temperature profile' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'tntrs_avg',   'K s−1', 'domain avg. shortwave radiative heating rate profile' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'tntrl_avg',   'K s−1', 'domain avg. longwave radiative heating rate profile ' )
         # create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'tntrscs_avg', 'K s−1', 'domain avg. shortwave radiative heating rate profile- clear sky ' )
         # create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'tntrlcs_avg', 'K s−1', 'domain avg. longwave radiative heating rate profile- clear sky ' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'cldfrac_avg', '',      'global cloud fraction profile' )
      #-------------------------------------------------------------------------
      # TA3 - 2D (x,y,t)   1-hr  h0+h2
      if cmor_do_table_3:
         print(indent+f'{clr.MAGENTA}Begin CMORization of 2D data{clr.END}')
         htype, dim, src_root = 'h0', '2D', f'{root}/{case}/data_remap_{dst_nlat}x{dst_nlon}'
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'pr',       'kg m−2 s−1', 'surface precipitation rate'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'hfls',     'W m−2',      'surface upward latent heat flux'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'hfss',     'W m−2',      'surface upward sensible heat flux'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rlds',     'W m−2',      'surface downwelling longwave flux'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rlus',     'W m−2',      'surface upwelling longwave flux'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rsds',     'W m−2',      'surface downwelling shortwave flux'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rsus',     'W m−2',      'surface upwelling shortwave flux'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rsdscs',   'W m−2',      'surface downwelling shortwave flux-clearsky'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rsuscs',   'W m−2',      'surface upwelling shortwave flux-clearsky'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rldscs',   'W m−2',      'surface downwelling longwave flux-clearsky'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rluscs',   'W m−2',      'surface upwelling longwave flux-clearsky'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rsdt',     'W m−2',      'TOA incoming shortwave flux'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rsut',     'W m−2',      'TOA outgoing shortwave flux'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rlut',     'W m−2',      'TOA outgoing longwave flux'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rsutcs',   'W m−2',      'TOA outgoing shortwave flux-clearsky'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'rlutcs',   'W m−2',      'TOA outgoing longwave flux-clearsky'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'prw',      'kg m−2',     'water vapor path'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'sprw',     'kg m−2',     'saturated water vapor path'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'clwvi',    'kg m−2',     'condensed water path (cloudice + cloud liquid)'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'clivi',    'kg m−2',     'ice water path(cloudice)'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'psl',      'Pa',         'sea level pressure'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'tas',      'K',          '2m air temperature'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'tabot',    'K',          'air temperature at lowest model level'  )
         # create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'uas',      'm s−1',      '10m eastward wind'  )
         # create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'vas',      'm s−1',      '10m northward wind'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'uabot',    'm s−1',      'eastward wind at lowest model level'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'vabot',    'm s−1',      'northward wind at lowest model level'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'wap500',   'Pa s−1',     'omegaat500hPa'  )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'cl',       '',           'total cloud fraction of grid column' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'pr_conv',  'kg m−2 s−1', 'surface convective precipitation rate'  )
         if 'MMF' not in mdl:
            htype, src_root = 'h2', f'{root}/{case}/data_remap_{dst_nlat}x{dst_nlon}'
            create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'albisccp', '',           'ISCCP mean cloud albedo' )
            create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'cltisccp', '%',          'ISCCP total cloud cover' )
            create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'pctisccp', 'Pa',         'ISCCP mean cloud top pressure' )
      #-------------------------------------------------------------------------
      # TA4 - 3D (x,y,z,t) 6-hr  h3
      if cmor_do_table_4:
         print(indent+f'{clr.MAGENTA}Begin CMORization of 3D data{clr.END}')
         htype, dim, src_root = 'h3', '3D', f'{root}/{case}/data_remap_{dst_nlat}x{dst_nlon}'
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'clw',      'g/g',         'mass fraction of cloud liquid water' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'cli',      'g/g',         'mass fraction of cloud ice' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'plw',      'g/g',         'mass fraction of precipitating liquid water' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'pli',      'g/g',         'mass fraction of precipitating ice' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'ta',       'K',           'air temperature' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'ua',       'ms−1',        'eastward wind' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'va',       'ms−1',        'northward wind' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'hus',      'g/g',         'specific humidity' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'wap',      'Pa s−1',      'omega' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'zg',       'm',           'geopotenial height' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'tntrs',    'Ks−1',        'tendency of air temperature due to shortwave radiative heating' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'tntrl',    'Ks−1 ',       'tendency of air temperature due to longwave radiative heating' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'tntrscs',  'K s−1',       'tendency of air temperature due to shortwave radiative heating- clear sky' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'tntrlcs',  'Ks−1',        'tendency of air temperature due to longwave radiative heating- clear sky' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'cldfrac',  '',            'cloud fraction' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'mc',       'kg m−2 s−1',  'convective mass flux' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'tntc',     'Ks−1',        'tendency of air temperature due to moist convection' )
         create_cmor( mdl,exp,dim, src_root, dst_root, htype, 'clisccp',  '%',           'ISCCP cloud area percentage in optical depth and pressure bins' )
      #-------------------------------------------------------------------------
      print()
   #------------------------------------------------------------------------------------------------
   if DKRZ_upload:
      ''' make sure to active the env and source the file with authorization:
      conda activate swift_env
      source ~/.swiftenv
      '''
      #-------------------------------------------------------------------------
      dim_list = []
      # dim_list.append('0D')
      # dim_list.append('1D')
      # dim_list.append('2D')
      dim_list.append('3D')
      #-------------------------------------------------------------------------
      data_final_root = f'{root}/{case}/data_final'
      print(f'\n{clr.GREEN}cd {data_final_root}{clr.END}');
      os.chdir(f'{data_final_root}')
      #-------------------------------------------------------------------------
      container = None
      if '-MW' not in case: container = 'RCEMIP'
      if '-MW'     in case: container = 'RCEMIP-II'
      if container is None: raise ValueError('container cannot be None - something is wrong!')
      for dim in dim_list:
         file_list = sorted( glob.glob(f'*_{dim}_*.nc') )
         file_list_str = ' '.join(file_list)
         cmd = f'swift upload {container}/{mdl}/{exp}/{dim}'
         if dim=='3D':cmd+=f' --segment-size 1000000000'
         cmd+=f' {file_list_str}'
         run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   if DKRZ_upload_docs:
      ''' make sure to active the env and source the file with authorization:
      conda activate swift_env
      source ~/.swiftenv
      '''
      #-------------------------------------------------------------------------
      print(f'\n{clr.GREEN}cd {root}/{case} {clr.END}');
      os.chdir(f'{root}/{case}')
      doc_file = f'rcemip_modeldoc_form_{mdl}_{exp}.pdf'
      #-------------------------------------------------------------------------
      container = None
      if '-MW' not in case: container = 'RCEMIP'
      if '-MW'     in case: container = 'RCEMIP-II'
      if container is None: raise ValueError('container cannot be None - something is wrong!')
      run_cmd(f'swift upload {container}/{mdl}/{exp}/ {doc_file}')
   #------------------------------------------------------------------------------------------------
   # if 'delete_all_data' not in globals(): delete_all_data = False
   if delete_all_data:
      file_list = []
      file_list += glob.glob(f'{case_root}/post/atm/180x360/ts/monthly/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/post/atm/180x360/clim/monthly/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/post/atm/180x360/clim/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/post/atm/90x180/ts/monthly/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/post/atm/90x180/clim/monthly/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/post/atm/90x180/clim/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/post/atm/glb/ts/monthly/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/archive/*/hist/*.nc')
      file_list += glob.glob(f'{case_root}/archive/rest/*/*.nc')
      file_list += glob.glob(f'{case_root}/run/*.nc')
      file_list += glob.glob(f'{case_root}/data_remap_90x180/*.nc')
      file_list += glob.glob(f'{case_root}/data_final/*_2D_*.nc')
      file_list += glob.glob(f'{case_root}/data_final/*_3D_*.nc')
      # if len(file_list)>10:
      #    print()
      #    for f in file_list: print(f)
      #    print()
      #    exit()
      if len(file_list)>0: 
         print(f'  {clr.RED}deleting {(len(file_list))} files{clr.END}')
         for f in file_list:
            os.remove(f)
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {clr.BOLD}{case}{clr.END} ')
#---------------------------------------------------------------------------------------------------
def calc_global_mean(ds):
   area = ds['area']
   ds_out = ds.copy(deep=True)
   for var in ds.variables:
      if var in ['lat','lon','area']: 
         continue
      if 'ncol' in ds[var].dims:
         ds_out[var] = (ds[var]*area).sum(dim='ncol') / area.sum(dim='ncol')
         ds_out[var].attrs = ds[var].attrs
      else:
         ds_out[var] = ds[var]
   return ds_out
#---------------------------------------------------------------------------------------------------
# constants
cpd     = 1004.         # J / (kg K)       specific heat capacity of air at constant pressure
cpv     = 1850.         # J / (kg K)       specific heat capacity of air at constant volume
cpl     = 4186.         # J / (kg K)        specific heat capacity of liquid water
Tf      = 273.15        # K                freezing temperature of water
g       = 9.81          # m / s^2          acceleration due to gravity
Lv      = 2.5104e6      # J / kg           latent heat of vaporization / evaporation
Lf      = 0.3336e6      # J / kg           latent heat of freezing / melting
Ls      = 2.8440e6      # J / kg           latent heat of sublimation
Rd      = 287.04        # J / (kg K)       gas constant for dry air
#---------------------------------------------------------------------------------------------------
def get_pressure(ds):
   a,b,p0,ps = ds['hyam'], ds['hybm'], ds['P0'], ds['PS']
   pressure = a * p0 + b * ps
   pressure.attrs['units'] = 'Pa'
   return pressure
#---------------------------------------------------------------------------------------------------
def get_cmor_data( src_var_name, src_ds, is_case_MMF=False ):
   #-------------------------------------------------------------------------
   # TA1 - 0D (t)    1-hr  h0
   if src_var_name=='pr_avg'     : return src_ds['PRECT']                        # sfc precipitation rate
   if src_var_name=='hfls_avg'   : return src_ds['LHFLX']                        # sfc upward latent heat flux
   if src_var_name=='hfss_avg'   : return src_ds['SHFLX']                        # sfc upward sensible heat flux
   if src_var_name=='prw_avg'    : return src_ds['TMQ']                          # water vapor path
   if src_var_name=='sprw_avg'   : return src_ds['TMQS']                         # saturated water vapor path
   if src_var_name=='clwvi_avg'  : return src_ds['TGCLDLWP']+src_ds['TGCLDIWP']  # condensed water path (cloud ice + cloud liquid)
   if src_var_name=='clivi_avg'  : return src_ds['TGCLDIWP']                     # ice water path (cloud ice)
   if src_var_name=='rlds_avg'   : return src_ds['FLDS']                         # sfc downwelling longwave flux
   if src_var_name=='rlus_avg'   : return src_ds['FLNS']-src_ds['FLDS']          # sfc upwelling longwave flux
   if src_var_name=='rsds_avg'   : return src_ds['FSDS']                         # sfc downwelling shortwave flux
   if src_var_name=='rsus_avg'   : return src_ds['FSNS']-src_ds['FSDS']          # sfc upwelling shortwave flux
   if src_var_name=='rsdscs_avg' : return src_ds['FSDSC']                        # sfc downwelling shortwave flux - clear sky
   if src_var_name=='rsuscs_avg' : return src_ds['FSNSC']-src_ds['FSDSC']        # sfc upwelling shortwave flux - clear sky
   if src_var_name=='rldscs_avg' : return src_ds['FLDSC']                        # sfc downwelling longwave flux - clear sky
   if src_var_name=='rluscs_avg' : return src_ds['FLNSC']-src_ds['FLDSC']        # sfc upwelling longwave flux - clear sky
   if src_var_name=='rsdt_avg'   : return src_ds['FSNTOA']-src_ds['FSUTOA']      # TOA incoming shortwave flux
   if src_var_name=='rsut_avg'   : return src_ds['FSUTOA']                       # TOA outgoing shortwave flux
   if src_var_name=='rlut_avg'   : return src_ds['FLUTOA']                       # TOA outgoing longwave flux
   if src_var_name=='rsutcs_avg' : return src_ds['FSUTOAC']                      # TOA outgoing shortwave flux - clear sky
   if src_var_name=='rlutcs_avg' : return src_ds['FLUTOAC']                      # TOA outgoing longwave flux - clear sky
   #-------------------------------------------------------------------------
   # TA2 - 1D (z,t)     1-hr  h1 - globally averaged
   if src_var_name=='ta_avg'     : return src_ds['T']                            # air temperaure profile'
   if src_var_name=='ua_avg'     : return src_ds['U']                            # eastward wind profile'
   if src_var_name=='va_avg'     : return src_ds['V']                            # northward wind profile'
   if src_var_name=='hus_avg'    : return src_ds['Q']                            # specific humidity profile'
   if src_var_name=='hur_avg'    : return src_ds['RELHUM']                       # relative humidity profile'
   if src_var_name=='clw_avg'    : return src_ds['CLDLIQ']                       # mass fraction of cloud liquid water profile'
   if src_var_name=='cli_avg'    : return src_ds['CLDICE']                       # mass fraction of cloud ice profile'
   if src_var_name=='plw_avg'    : return None                                   # mass fraction of precipitating liquid water profile'
   if src_var_name=='pli_avg'    : return None                                   # mass fraction of precipitating ice profile'
   if src_var_name=='theta_avg'  :                                               # potential temperature profile'
      P = get_pressure(src_ds)
      return src_ds['T'] * ( src_ds['P0']/P )**(Rd/cpd)
   if src_var_name=='thetae_avg' :                                               # equivalent potential temperature profile'
      qv,qc,qi = src_ds['Q'], src_ds['CLDLIQ'], src_ds['CLDICE']
      qt = qv + qc + qi ; rt = qt/(1-qt) ; rv = qv/(1-qv)
      P = get_pressure(src_ds)
      return src_ds['T'] * ( src_ds['P0']/P )**(Rd/(cpd+rt*cpl)) * np.exp( Lv*rv / ( src_ds['T']*(cpd+rt*cpl) ) )
   if src_var_name=='tntrs_avg'  : return src_ds['QRS']                          # shortwave radiative heating rate profile'
   if src_var_name=='tntrl_avg'  : return src_ds['QRL']                          # longwave radiative heating rate profile '
   if src_var_name=='tntrscs_avg': return src_ds['QRSC']                         # shortwave radiative heating rate profile- clear sky '
   if src_var_name=='tntrlcs_avg': return src_ds['QRLC']                         # longwave radiative heating rate profile- clear sky '
   if src_var_name=='cldfrac_avg': return src_ds['CLOUD']                        # cloud fraction profile'
   #-------------------------------------------------------------------------
   # TA3 - 2D (x,y,t)   1-hr  h0+h2
   if src_var_name=='pr'         : return src_ds['PRECT']                        # sfc precipitation rate
   if src_var_name=='hfls'       : return src_ds['LHFLX']                        # sfc upward latent heat flux
   if src_var_name=='hfss'       : return src_ds['SHFLX']                        # sfc upward sensible heat flux
   if src_var_name=='rlds'       : return src_ds['FLDS']                         # sfc downwelling longwave flux
   if src_var_name=='rlus'       : return src_ds['FLNS']-src_ds['FLDS']          # sfc upwelling longwave flux
   if src_var_name=='rsds'       : return src_ds['FSDS']                         # sfc downwelling shortwave flux
   if src_var_name=='rsus'       : return src_ds['FSNS']-src_ds['FSDS']          # sfc upwelling shortwave flux
   if src_var_name=='rsdscs'     : return src_ds['FSNS']-src_ds['FSDS']          # sfc downwelling shortwave flux-clearsky
   if src_var_name=='rsuscs'     : return src_ds['FSDSC']                        # sfc upwelling shortwave flux-clearsky
   if src_var_name=='rldscs'     : return src_ds['FLDSC']                        # sfc downwelling longwave flux-clearsky
   if src_var_name=='rluscs'     : return src_ds['FLNSC']-src_ds['FLDSC']        # surface upwelling longwave flux-clearsky
   if src_var_name=='rsdt'       : return src_ds['FSNTOA']-src_ds['FSUTOA']      # TOA incoming shortwave flux
   if src_var_name=='rsut'       : return src_ds['FSUTOA']                       # TOA outgoing shortwave flux
   if src_var_name=='rlut'       : return src_ds['FLUTOA']                       # TOA outgoing longwave flux
   if src_var_name=='rsutcs'     : return src_ds['FSUTOAC']                      # TOA outgoing shortwave flux - clear sky
   if src_var_name=='rlutcs'     : return src_ds['FLUTOAC']                      # TOA outgoing longwave flux - clear sky
   if src_var_name=='prw'        : return src_ds['TMQ']                          # water vapor path
   if src_var_name=='sprw'       : return src_ds['TMQS']                         # saturated water vapor path
   if src_var_name=='clwvi'      : return src_ds['TGCLDLWP']+src_ds['TGCLDIWP']  # condensed water path (cloudice + cloud liquid
   if src_var_name=='clivi'      : return src_ds['TGCLDIWP']                     # ice water path(cloudice
   if src_var_name=='psl'        : return src_ds['PSL']                          # sea level pressure
   if src_var_name=='tas'        : return src_ds['TREFHT']                       # 2m air temperature
   if src_var_name=='tabot'      : return src_ds['TBOT']                         # air temperature at lowest model level
   if src_var_name=='uas'        : return None                                   # 10m eastward wind
   if src_var_name=='vas'        : return None                                   # 10m northward wind
   if src_var_name=='uabot'      : return src_ds['UBOT']                         # eastward wind at lowest model level
   if src_var_name=='vabot'      : return src_ds['VBOT']                         # northward wind at lowest model level
   if src_var_name=='wap500'     : return src_ds['OMEGA500']                     # omegaat500hPa
   if src_var_name=='cl'         : return src_ds['CLDTOT']                       # total cloud fraction of grid column
   if src_var_name=='pr_conv'    : return src_ds['PRECC']                        # surface convective precipitation rate
   if is_case_MMF:
      if src_var_name=='albisccp'   : return None                                # ISCCP mean cloud albedo
      if src_var_name=='cltisccp'   : return None                                # ISCCP total cloud cover
      if src_var_name=='pctisccp'   : return None                                # ISCCP mean cloud top pressure
   else:
      if src_var_name=='albisccp'   : return src_ds['MEANCLDALB_ISCCP']          # ISCCP mean cloud albedo
      if src_var_name=='cltisccp'   : return src_ds['CLDTOT_ISCCP']              # ISCCP total cloud cover
      if src_var_name=='pctisccp'   : return src_ds['MEANPTOP_ISCCP']            # ISCCP mean cloud top pressure
   #-------------------------------------------------------------------------
   # TA4 - 3D (x,y,z,t) 6-hr  h3
   if src_var_name=='clw'        : return src_ds['CLDLIQ']                       # mass fraction of cloud liquid water
   if src_var_name=='cli'        : return src_ds['CLDICE']                       # mass fraction of cloud ice
   if src_var_name=='ta'         : return src_ds['T']                            # air temperature
   if src_var_name=='ua'         : return src_ds['U']                            # eastward wind
   if src_var_name=='va'         : return src_ds['V']                            # northward wind
   if src_var_name=='hus'        : return src_ds['Q']                            # specific humidity
   if src_var_name=='wap'        : return src_ds['OMEGA']                        # omega
   if src_var_name=='paorzg'     : return src_ds['Z3']                           # geopotenial height
   if src_var_name=='tntrs'      : return src_ds['QRS']                          # tendency of air temperature due to shortwave radiative heating
   if src_var_name=='tntrl'      : return src_ds['QRL']                          # tendency of air temperature due to longwave radiative heating
   if src_var_name=='tntrscs'    : return src_ds['QRSC']                         # tendency of air temperature due to shortwave radiative heating- clear sky
   if src_var_name=='tntrlcs'    : return src_ds['QRLC']                         # tendency of air temperature due to longwave radiative heating- clear sky
   if src_var_name=='cldfrac'    : return src_ds['CLOUD']                        # cloud fraction
   if src_var_name=='tntc'       : return src_ds['DTCOND']                       # tendency of air temperature due to moist convection
   if src_var_name=='plw'        : return None                                   # mass fraction of precipitating liquid water
   if src_var_name=='pli'        : return None                                   # mass fraction of precipitating ice
   if is_case_MMF:
      # if src_var_name=='plw'        : return src_ds['CRM_QPC']                   # mass fraction of precipitating liquid water
      # if src_var_name=='pli'        : return src_ds['CRM_QPI']                   # mass fraction of precipitating ice
      if src_var_name=='mc'         : return src_ds['MMF_MCUP']                  # convective mass flux
      if src_var_name=='clisccp'    : return None                                # ISCCP cloud area percentage in optical depth and pressure bins
   else:
      # if src_var_name=='plw'        : return None                                # mass fraction of precipitating liquid water
      # if src_var_name=='pli'        : return None                                # mass fraction of precipitating ice
      if src_var_name=='mc'         : return src_ds['CMFMCDZM']                  # convective mass flux
      if src_var_name=='clisccp'    : return src_ds['FISCCP1_COSP']              # ISCCP cloud area percentage in optical depth and pressure bins
   #-------------------------------------------------------------------------
   return None
#---------------------------------------------------------------------------------------------------
license_txt = 'Data produced by E3SM-Project is licensed under a Creative Commons'
license_txt+= ' Attribution 4.0 International License (https://creativecommons.org/licenses/by/4.0/).'
license_txt+= ' Consult https://pcmdi.llnl.gov/CMIP6/TermsOfUse for terms of use governing CMIP6 output,'
license_txt+= ' including citation requirements and proper acknowledgment.'
license_txt+= ' The data producers and data providers make no warranty,'
license_txt+= ' either express or implied, including, but not limited to,'
license_txt+= ' warranties of merchantability and fitness for a particular purpose.'
license_txt+= ' All liabilities arising from the supply of the information'
license_txt+= ' (including any liability arising in negligence)'
license_txt+= ' are excluded to the fullest extent permitted by law.'
#---------------------------------------------------------------------------------------------------
def set_global_atts(dst_ds):
   dst_ds = dst_ds.assign_attrs(activity_id         = 'RCEMIP')
   dst_ds = dst_ds.assign_attrs(experiment_id       = 'RCEMIP')
   dst_ds = dst_ds.assign_attrs(sub_experiment_id   = 'none')
   dst_ds = dst_ds.assign_attrs(institution_id      = 'E3SM-Project')
   dst_ds = dst_ds.assign_attrs(calendar            = 'noleap')
   dst_ds = dst_ds.assign_attrs(source_id           = 'E3SM-2-0')
   dst_ds = dst_ds.assign_attrs(author_name         = 'Walter Hannah')
   dst_ds = dst_ds.assign_attrs(author_institution  = 'Lawrence Livermore National Laboratory')
   dst_ds = dst_ds.assign_attrs(license             = license_txt)
   return dst_ds
#---------------------------------------------------------------------------------------------------
def create_cmor( mdl, exp, dim, src_root, dst_root, htype, dst_var_name, dst_var_unit, dst_var_long ):
   indent = ' '*6
   dst_file = f'{dst_root}/{mdl}_{exp}_{dim}_{dst_var_name}.nc'
   print(indent+f'dst_var_name: {clr.GREEN}{dst_var_name:12}{clr.END}  dst_file: {clr.CYAN}{dst_file}{clr.END}')
   #----------------------------------------------------------------------------
   file_list = sorted( glob.glob(f'{src_root}/*.eam.{htype}.*') )
   src_ds = xr.open_mfdataset(file_list)
   dst_da = get_cmor_data( dst_var_name, src_ds, is_case_MMF=(True if 'MMF' in mdl else False) )
   #----------------------------------------------------------------------------
   if dst_da is None: 
      print()
      print(indent+f'WARNING - variable not found by get_cmor_data()')
      print(indent+f'WARNING - dst_var_name     : {dst_var_name}')
      print(indent+f'WARNING - mdl-exp-dim      : {mdl}-{exp}-{dim}')
      print(indent+f'WARNING - src_root/*htype* : {src_root}/*{htype}*')
      print()
      return
   #----------------------------------------------------------------------------
   dst_ds = xr.Dataset()
   dst_ds[dst_var_name] = dst_da
   dst_ds[dst_var_name].assign_attrs(units = dst_var_unit)
   dst_ds[dst_var_name].assign_attrs(description = dst_var_long)
   dst_ds = set_global_atts(dst_ds)
   dst_ds.to_netcdf(path=dst_file,mode='w')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for n in range(len(case_list)):
      print('-'*100)
      main( case=case_list[n], root=root_list[n], mdl=mdl_list[n], exp=exp_list[n] )
   print_line()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
