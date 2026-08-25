import os
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END); os.system(cmd)
#---------------------------------------------------------------------------------------------------
'''NOTES
source /lcrc/soft/climate/e3sm-unified/load_latest_e3sm_unified_chrysalis.sh

after running this script make sure permissions are correct:
chmod go+r ${DIN_LOC_ROOT}/atm/scream/init_tmp/*
'''
#---------------------------------------------------------------------------------------------------
DIN_LOC_ROOT = '/lcrc/group/acme/public_html/inputdata'

SRC_ROOT = f'{DIN_LOC_ROOT}/atm/scream/init'
DST_ROOT = f'{DIN_LOC_ROOT}/atm/scream/init_tmp'

file_list = []
file_list.append(f'{SRC_ROOT}/screami_ne4np4L128_20241022.nc')
file_list.append(f'{SRC_ROOT}/screami_ne30np4L128_20221004.nc')
file_list.append(f'{SRC_ROOT}/eamxxi_ne32np4L128.v3.LR.amip_0101.eam.i.2000-01-01-00000.20251001.nc')
file_list.append(f'{SRC_ROOT}/eamxxi_ne64np4L128.v3.LR.amip_0101.eam.i.2000-01-01-00000.20251001.nc')
file_list.append(f'{SRC_ROOT}/screami_ne120np4L128_20230215.nc')
file_list.append(f'{SRC_ROOT}/eamxxi_ne128np4L128.v3.LR.amip_0101.eam.i.2000-01-01-00000.20251001.nc')
file_list.append(f'{SRC_ROOT}/screami_ne256np4L128_ifs-20200120_20220914.nc')
file_list.append(f'{SRC_ROOT}/screami_ne256np4L128_era5_aer_c20240929.nc')
file_list.append(f'{SRC_ROOT}/screami_ne512np4L128_20220823.nc')
file_list.append(f'{SRC_ROOT}/screami_ne1024np4L128_era5-20131001-topoadj-16x_20220914.nc')
file_list.append(f'{SRC_ROOT}/screami_mam4xx_ne1024np4L128_20240513.nc')
file_list.append(f'{SRC_ROOT}/screami_ne1024np4L128_ifs-20200120-topoadjx6t_20221011.nc')

DST_VERT = f'{SRC_ROOT}/vertical_coordinates_L128v4_c20260820.nc'

DST_DATESTAMP = '20260825'

#---------------------------------------------------------------------------------------------------
os.makedirs(DST_ROOT,exist_ok=True)
#---------------------------------------------------------------------------------------------------
DST_FILE_LIST = []
for SRC_FILE in file_list:
  if not os.path.exists(SRC_FILE): raise OSError(f'file is missing:\n  {SRC_FILE}\n')
  SRC_DATESTAMP = SRC_FILE[-3-8:-3]
  DST_FILE = SRC_FILE
  DST_FILE = DST_FILE.replace('L128_','L128v4_')
  DST_FILE = DST_FILE.replace(SRC_DATESTAMP,DST_DATESTAMP)
  DST_FILE = DST_FILE.replace(SRC_ROOT,DST_ROOT)
  DST_FILE_LIST.append(DST_FILE)
  print()
  run_cmd(f'ncremap -4 --ps_nm=ps --vrt_fl={DST_VERT} --in_fl={SRC_FILE} --out_fl={DST_FILE}')
  run_cmd(f'ncatted -O -a _FillValue,ps,d,, {DST_FILE} {DST_FILE}.tmp')
  run_cmd(f'ncks -5 {DST_FILE}.tmp {DST_FILE}.tmp.cdf5')
  run_cmd(f'mv {DST_FILE}.tmp.cdf5 {DST_FILE}')
  run_cmd(f'rm {DST_FILE}.tmp')
  print()
  print(f'SRC_FILE: {SRC_FILE}')
  print(f'DST_FILE: {DST_FILE}')
#---------------------------------------------------------------------------------------------------
print()
mx_len = 0
for DST_FILE in DST_FILE_LIST:
  mx_len = max(mx_len,len(DST_FILE))
for DST_FILE in DST_FILE_LIST:
  msg = f'  {DST_FILE:{mx_len}}  '
  if os.path.exists(SRC_FILE):
    msg += f'  {clr.GREEN}OK{clr.END}'
  else:
    msg += f'  {clr.RED}MISSING?{clr.END}'
  print(msg)
#---------------------------------------------------------------------------------------------------
print()
#---------------------------------------------------------------------------------------------------