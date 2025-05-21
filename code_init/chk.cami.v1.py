import os
import ngl
import copy
import xarray as xr
import numpy as np

input_data = '/global/cfs/cdirs/e3sm/inputdata/atm/cam/inic/homme'

### full path of input file
input_files = [
              # f'{input_data}/cami_mam3_Linoz_ne30np4_L72_c160214.nc',
              f'/global/cscratch1/sd/whannah/HICCUP/data/HICCUP.cami_mam3_Linoz_ne30np4.L72_alt.nc',
              f'/global/cscratch1/sd/whannah/HICCUP/data/HICCUP.cami_mam3_Linoz_ne4np4.L72_alt.nc',
              # f'{input_data}/cami_mam3_Linoz_ne45np4_L72_c20200611.nc',
              ]

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
class tcolor:
   ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
for i in range(len(input_files)):
   print(f'\n  {input_files[i]}')
   
   # read the data
   ds = xr.open_dataset( input_files[i] )

   # reset the counters
   nan_var_cnt,inf_var_cnt = 0,0
   #----------------------------------------------------------------------------
   # loop through variables in dataset
   #----------------------------------------------------------------------------
   for key in ds.keys():
      
      # print(f'{key:20}  {ds[key].dtype}')
      
      # skip these varaibles
      if key in ['time_bnds','date_written','time_written']: 
         continue

      # check for NaN values
      nan_flag = np.isnan(ds[key].values)
      if np.any(nan_flag):
         nan_cnt = np.sum(nan_flag)
         print(f'    {key:10} {nan_cnt:4} NaNs found!')
         nan_var_cnt += 1

      # check for inf values
      inf_flag = np.isinf(ds[key].values)
      if np.any(inf_flag):
         inf_cnt = np.sum(inf_flag)
         print(f'    {key:10} {inf_cnt:4} Infs found!')
         inf_var_cnt += 1
   
   #----------------------------------------------------------------------------
   # print a summary message
   #----------------------------------------------------------------------------
   if nan_var_cnt==0 and inf_var_cnt==0:
      msg = f'  No NaNs or Infs found\n'
      msg = tcolor.GREEN+msg+tcolor.ENDC
      print(msg)
   else:
      nan_msg = f'  {nan_var_cnt} vars found with NaNs'
      inf_msg = f'  {inf_var_cnt} vars found with Infs'
      if nan_var_cnt>0 : nan_msg = tcolor.RED+nan_msg+tcolor.ENDC
      if inf_var_cnt>0 : inf_msg = tcolor.RED+inf_msg+tcolor.ENDC
      print(f'{nan_msg}\n{inf_msg}\n')

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
