#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
unified_env = '/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh'
def print_line():print(' '*2+'-'*80)
def run_cmd(cmd): 
   print('\n'+clr.GREEN+cmd+clr.END);
   os.system(cmd); 
   return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, glob, datetime
import warnings; warnings.simplefilter(action='ignore', category=FutureWarning) # supress FutureWarning from pandas
import xarray as xr, numpy as np, pandas as pd
st_archive,lt_archive_create,lt_archive_update,cp_post_to_cfs = False,False,False,False
remap_h1, calc_TEM_6hour, calc_TEM_month = False, False, False
delete_data = False

# remap_h1             = True
# calc_TEM_6hour       = True
# calc_TEM_month       = True
# st_archive           = True
# lt_archive_create    = True
# lt_archive_update    = True
delete_data       = True

zstash_log_root = '/global/homes/w/whannah/E3SM/zstash_logs'


scratch_root_cpu = '/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu'
scratch_root_gpu = '/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu'

hpss_root = 'E3SM/2024-SCIDAC-PCOMP'

dst_nlat,dst_nlon = 90, 180
map_file = '/global/homes/w/whannah/maps/map_ne30pg2_to_90x180_traave.nc'
prs_lvl_file = os.getenv('HOME')+'/E3SM/vert_grid_files/vrt_prs_ERA5.nc'

#---------------------------------------------------------------------------------------------------
compset = 'F20TR'
grid    = 'ne30pg2_r05_IcoswISC30E3r5'
# ens_id  = '2024-SCIDAC-PCOMP-TEST' # initial test to work out logistical issues
ens_id = '2024-SCIDAC-PCOMP-TEST-01' # second test with alternate land/river configuration
#---------------------------------------------------------------------------------------------------
case_list = []
def add_case(e,c,h,d):
   case = '.'.join(['E3SM',ens_id,grid,f'EF_{e:0.2f}',f'CF_{c:02.0f}',f'HD_{h:0.2f}',f'{d}'])
   case_list.append( case )
#---------------------------------------------------------------------------------------------------
# tmp_date_list = []
# # v2
# # tmp_date_list.append('1983-01-01') # phase 1 - pi*1/4
# # tmp_date_list.append('1993-04-01')
# # tmp_date_list.append('2004-05-01')
# # tmp_date_list.append('2022-10-01')
# # tmp_date_list.append('1985-11-01') # phase 2 - pi*3/4
# # tmp_date_list.append('1991-04-01')
# # tmp_date_list.append('2000-01-01')
# # tmp_date_list.append('2011-07-01')
# tmp_date_list.append('1984-01-01') # phase 3 - pi*5/4
# tmp_date_list.append('2001-04-01')
# tmp_date_list.append('2005-07-01')
# # tmp_date_list.append('2021-11-01')
# # tmp_date_list.append('1987-07-01') # phase 4 - pi*7/4
# # tmp_date_list.append('1994-10-01')
# # tmp_date_list.append('2008-01-01')
# # tmp_date_list.append('2015-04-01')


case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-01.ne30pg2_r05_IcoswISC30E3r5.EF_0.09.CF_20.HD_0.25.1984-01-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-01.ne30pg2_r05_IcoswISC30E3r5.EF_0.09.CF_20.HD_0.25.1985-11-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-01.ne30pg2_r05_IcoswISC30E3r5.EF_0.09.CF_20.HD_0.25.2001-04-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-01.ne30pg2_r05_IcoswISC30E3r5.EF_0.09.CF_20.HD_0.25.2004-05-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-01.ne30pg2_r05_IcoswISC30E3r5.EF_0.09.CF_20.HD_0.25.2005-07-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-01.ne30pg2_r05_IcoswISC30E3r5.EF_0.09.CF_20.HD_0.25.2021-11-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-01.ne30pg2_r05_IcoswISC30E3r5.EF_0.35.CF_10.HD_0.50.1984-01-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-01.ne30pg2_r05_IcoswISC30E3r5.EF_0.35.CF_10.HD_0.50.1985-11-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-01.ne30pg2_r05_IcoswISC30E3r5.EF_0.35.CF_10.HD_0.50.2001-04-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-01.ne30pg2_r05_IcoswISC30E3r5.EF_0.35.CF_10.HD_0.50.2004-05-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-01.ne30pg2_r05_IcoswISC30E3r5.EF_0.35.CF_10.HD_0.50.2005-07-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-01.ne30pg2_r05_IcoswISC30E3r5.EF_0.35.CF_10.HD_0.50.2021-11-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-01.ne30pg2_r05_IcoswISC30E3r5.EF_0.70.CF_21.HD_0.31.1984-01-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-01.ne30pg2_r05_IcoswISC30E3r5.EF_0.70.CF_21.HD_0.31.1985-11-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-01.ne30pg2_r05_IcoswISC30E3r5.EF_0.70.CF_21.HD_0.31.2001-04-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-01.ne30pg2_r05_IcoswISC30E3r5.EF_0.70.CF_21.HD_0.31.2004-05-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-01.ne30pg2_r05_IcoswISC30E3r5.EF_0.70.CF_21.HD_0.31.2005-07-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-01.ne30pg2_r05_IcoswISC30E3r5.EF_0.70.CF_21.HD_0.31.2021-11-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-02.ne30pg2_r05_IcoswISC30E3r5.EF_0.09.CF_20.HD_0.25.1984-01-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-02.ne30pg2_r05_IcoswISC30E3r5.EF_0.12.CF_16.HD_0.48.1984-01-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-02.ne30pg2_r05_IcoswISC30E3r5.EF_0.35.CF_10.HD_0.50.1984-01-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST-02.ne30pg2_r05_IcoswISC30E3r5.EF_0.70.CF_21.HD_0.31.1984-01-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST.ne30pg2_r05_IcoswISC30E3r5.EF_0.12.CF_16.HD_0.48.1983-01-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST.ne30pg2_r05_IcoswISC30E3r5.EF_0.12.CF_16.HD_0.48.1993-04-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST.ne30pg2_r05_IcoswISC30E3r5.EF_0.35.CF_10.HD_0.50.1983-01-01' )
case_list.append( 'E3SM.2024-SCIDAC-PCOMP-TEST.ne30pg2_r05_IcoswISC30E3r5.EF_0.35.CF_10.HD_0.50.1993-04-01' )

#---------------------------------------------------------------------------------------------------
# for date in tmp_date_list:
#    add_case(e=0.35,c=10,h=0.50,d=date) #  <<< v3 default
#    # add_case(e=0.12,c=16,h=0.48,d=date) # prev surrogate optimum
#    add_case(e=0.09,c=20,h=0.25,d=date) # no QBO at all
#    add_case(e=0.70,c=21,h=0.31,d=date) # QBO is too fast
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(case):
   if case is None: exit(' case argument not provided?')
   # if root is None: exit(' root argument not provided?')

   root = '/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/'

   case_root = f'{root}/{case}'

   # print(case); return

   #------------------------------------------------------------------------------------------------
   #------------------------------------------------------------------------------------------------
   print_line()
   print(f'  case : {clr.BOLD}{case}{clr.END} \n')
   #------------------------------------------------------------------------------------------------
   remap_src_sub  = 'run'
   # remap_src_sub  = 'archive/atm/hist'
   remap_dst_sub  = f'data_remap_{dst_nlat}x{dst_nlon}'
   remap_src_root = f'{case_root}/{remap_src_sub}'
   remap_dst_root = f'{case_root}/{remap_dst_sub}'
   if not os.path.exists(remap_dst_root): os.mkdir(remap_dst_root)
   #------------------------------------------------------------------------------------------------
   if remap_h1:
      htype = 'h1'
      src_file_list = sorted( glob.glob(f'{remap_src_root}/{case}.eam.{htype}.*'))
      for src_file in src_file_list:
         dst_file = src_file.replace('.nc',f'.remap_{dst_nlat}x{dst_nlon}.nc')
         dst_file = dst_file.replace(remap_src_root,remap_dst_root)
         run_cmd(f'ncremap -m {map_file} -i {src_file} -o {dst_file} --vrt_fl={prs_lvl_file}')
   #------------------------------------------------------------------------------------------------
   if calc_TEM_6hour:
      idir = f'{root}/{case}/data_remap_90x180'
      odir = f'{root}/{case}/data_remap_90x180_tem'
      if not os.path.exists(odir): os.mkdir(odir)
      file_list = sorted( glob.glob(f'{idir}/*eam.h1.*') )
      file_list.remove(file_list[-1]) # last file is empty, so remove it
      # loop through files to calculate TEM terms 
      for src_file in file_list: 
         dst_file = src_file.replace(f'.h1.',f'.h1.tem.').replace(idir,odir)
         calc_TEM(src_file,dst_file)
   #------------------------------------------------------------------------------------------------
   if calc_TEM_month:
      htype = 'h1.tem'
      file_path = f'{case_root}/data_remap_90x180_tem/*.eam.{htype}.*'
      file_list = sorted(glob.glob(file_path))
      if file_list==[]: print(); print(file_path); exit('ERROR - calc_TEM_month: no files found!')
      # find bounds for loop over years
      yr_pos = file_list[0].find(htype) + len(htype) + 1
      yr1 = int(file_list[ 0][yr_pos:yr_pos+4])
      yr2 = int(file_list[-1][yr_pos:yr_pos+4])
      for y in range(yr1,yr2+1):
         for m in range(1,12+1):
            file_path = f'{case_root}/data_remap_90x180_tem/*.eam.{htype}.{y:04}-{m:02}*'
            file_list = sorted( glob.glob(file_path) )
            #-------------------------------------------------------------------
            # print()
            # for f in file_list: print(f)
            # days_in_month = pd.Period(f'{y}-{m}-01').days_in_month
            # print(f'days_in_month: {days_in_month}')
            #-------------------------------------------------------------------
            days_in_month = pd.Period(f'{y}-{m}-01').days_in_month
            if days_in_month==29: days_in_month=28
            if len(file_list) != days_in_month: continue
            #-------------------------------------------------------------------
            dst_file = file_list[0][:file_list[0].find(htype)]+f'h0.tem.{y:04}-{m:02}.remap_90x180.nc'
            print(); print(' '*4+f'yr/mn: {y} / {m}   dst_file: {clr.CYAN}{dst_file}{clr.END}')
            #-------------------------------------------------------------------
            ds = xr.open_mfdataset(file_list).load()
            # residual calculation
            ds['dudt'] = ds['u'].differentiate(coord='time',datetime_unit='s')
            ds['residual'] =  ds['dudt'] - ds['utendvtem'] - ds['utendwtem']-ds['utendepfd']
            # monthly average of entire dataset
            ds_out = ds.mean('time')
            # add dummy time coordinate
            time_da = xr.DataArray([0], [('time', [0])])
            time_da.attrs['long_name'] = 'time'
            time_da.attrs['units']     = f'days since {y}-{m}-01 00:00:00'
            ds_out = ds_out.expand_dims(time=time_da)

            # # TEST # TEST # TEST # TEST # TEST #
            # # skip the first days
            # n_skip = 10
            # print(); print(f'{clr.RED}WARNING - omitting first {n_skip} days - WARNING{clr.END}'); print()
            # ds_out = ds.isel(time=slice(n_skip*4,32*4)).mean('time')
            # # TEST # TEST # TEST # TEST # TEST #

            ds_out.to_netcdf(path=dst_file,mode='w')
   #------------------------------------------------------------------------------------------------
   if st_archive:
      os.chdir(f'{case_root}/case_scripts')
      run_cmd(f'./xmlchange DOUT_S_ROOT={case_root}/archive ')
      run_cmd('./case.st_archive')
   #------------------------------------------------------------------------------------------------
   if lt_archive_create:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Create the HPSS archive
      run_cmd(f'source {unified_env}; zstash create --hpss={hpss_root}/{case} . 2>&1 | tee {zstash_log_root}/zstash_2024-SCIDAC-PCOMP_create_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if lt_archive_update:
      print(f'\n{clr.GREEN}cd {case_root}{clr.END}');
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      run_cmd(f'source {unified_env}; zstash update --hpss={hpss_root}/{case}  2>&1 | tee {zstash_log_root}/zstash_2024-SCIDAC-PCOMP_update_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if delete_data:
      file_list = []
      file_list += glob.glob(f'{case_root}/archive/*/hist/*.nc')
      file_list += glob.glob(f'{case_root}/archive/rest/*/*.nc')
      file_list += glob.glob(f'{case_root}/run/*.nc')
      file_list += glob.glob(f'{case_root}/data_remap_90x180/*.nc')
      file_list += glob.glob(f'{case_root}/data_remap_90x180_tem/*.nc')
      file_list += glob.glob(f'{case_root}/data_remap_90x180_prs/*.nc')
      
      if len(file_list)>0: 
         print(f'  {clr.RED}deleting {(len(file_list))} files{clr.END}')
         for f in file_list:
            os.remove(f)
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {clr.BOLD}{case}{clr.END} ')
#---------------------------------------------------------------------------------------------------
# constants
H     = 7e3          # m         assumed mean scale heightof the atmosphere
P0    = 101325       # Pa        surface pressure
Rd    = 287.058      # J/kg/K    gas constant for dry air
cp    = 1004.64      # J/kg/K    specific heat for dry air
g     = 9.80665      # m/s       global average of gravity at MSLP
a     = 6.37123e6    # m         Earth's radius
omega = 7.29212e-5   # 1/s       Earth's rotation rate
pi    = 3.14159
#---------------------------------------------------------------------------------------------------
def calc_TEM(src_file,dst_file):
   #----------------------------------------------------------------------------
   ds = xr.open_dataset(src_file)
   #----------------------------------------------------------------------------
   nlat, nlev = len(ds[ 'lat'].values), len(ds['plev'].values)
   dlat = ds['lat']
   rlat = np.deg2rad(dlat)
   rlat['lat'] = rlat
   cos_lat = np.cos(rlat)
   fcor = 2*omega*np.sin(rlat)
   #----------------------------------------------------------------------------
   # basic zonal means and anomalies
   TH   = ds['T'] * np.power( P0/ds['plev'], Rd/cp )
   TH_b = TH.mean(dim='lon')
   U_b  = ds['U'].mean(dim='lon')
   V_b  = ds['V'].mean(dim='lon')
   W_b  = ds['OMEGA'].mean(dim='lon')
   TH_p = TH          - TH_b
   U_p  = ds['U']     - U_b
   V_p  = ds['V']     - V_b
   W_p  = ds['OMEGA'] - W_b
   # make sure coordinate data is lat in radians for da.differentiate()
   TH_b['lat'], U_b ['lat'], V_b ['lat'], W_b ['lat'] = rlat, rlat, rlat, rlat
   TH_p['lat'], U_p ['lat'], V_p ['lat'], W_p ['lat'] = rlat, rlat, rlat, rlat
   #----------------------------------------------------------------------------
   # EP flux vectors
   dTHdp = TH_b.differentiate('plev')
   dUdp  =  U_b.differentiate('plev')
   dUdy  = (U_b*cos_lat).differentiate('lat') / (a*cos_lat)
   # eddy stream function
   gamma = (V_p*TH_p).mean(dim='lon') / dTHdp
   # original version based on Gerber and Manzini
   F_y = a*cos_lat * (       dUdp *gamma - (U_p*V_p).mean(dim='lon') )
   F_z = a*cos_lat * ( (fcor-dUdy)*gamma - (U_p*W_p).mean(dim='lon') )
   F_y = F_y.transpose('time','plev','lat')
   F_z = F_z.transpose('time','plev','lat')
   #----------------------------------------------------------------------------
   # EP flux divergence
   dFydy = (F_y*cos_lat).differentiate('lat') / (a*cos_lat)
   dFzdp = F_z.differentiate('plev')
   EP_div = ( dFydy + dFzdp ) / (a*cos_lat)
   #----------------------------------------------------------------------------
   # TEM meridional and vertical  velocities
   dgamma_dy = (gamma*cos_lat).differentiate('lat') / (a*cos_lat)
   dgamma_dp = gamma.differentiate('plev')
   V_star = V_b - dgamma_dp
   W_star = W_b - dgamma_dy
   #----------------------------------------------------------------------------
   # TEM mass stream function
   dp_int = xr.full_like(ds['plev'],np.nan)
   for k in range(1,nlev-1):
      pint1 = ( ds['plev'][k-1] + ds['plev'][k-0] ) / 2.
      pint2 = ( ds['plev'][k-0] + ds['plev'][k+1] ) / 2.
      dp_int[k] =  pint1 - pint2
   gamma_mass = xr.full_like(U_b,np.nan)
   for k in range(1,nlev-1):
      tmp_integral = xr.full_like(U_b.mean(dim='plev'),0)
      for kk in range(1,k):
         tmp_integral[:,:] = tmp_integral[:,:] + ( V_b[:,kk,:]*dp_int[kk] - gamma[:,kk,] )
      gamma_mass[:,k,:] = ( (2*pi*a*cos_lat[:]/g) * tmp_integral[:,:] ).transpose('time','lat')
   #----------------------------------------------------------------------------
   # TEM northward and upward advection
   dUdt_y = V_star * ( fcor - dUdy )
   dUdt_z = -1 * W_star * dUdp
   #----------------------------------------------------------------------------
   # Create output datset and add variables      
   ds_out = xr.Dataset()
   ds_out['vtem']         = V_star
   ds_out['wtem']         = W_star
   ds_out['psitem']       = gamma_mass 
   ds_out['utendepfd']    = EP_div
   ds_out['utendvtem']    = dUdt_y
   ds_out['utendwtem']    = dUdt_z
   ds_out['lat'] = dlat # use latitude in degrees for output
   ds_out['u']            = ds['U' ].mean(dim='lon')
   ds_out['z']            = ds['Z3'].mean(dim='lon')
   #----------------------------------------------------------------------------
   # add variable long names
   ds_out['vtem']        .attrs['long_name'] = 'Transformed Eulerian mean northward wind'
   ds_out['wtem']        .attrs['long_name'] = 'Transformed Eulerian mean upward wind'
   ds_out['psitem']      .attrs['long_name'] = 'Transformed Eulerian mean mass stream function'
   ds_out['utendepfd']   .attrs['long_name'] = 'Tendency of eastward wind due to TEM Eliassen-Palm flux divergence'
   ds_out['utendvtem']   .attrs['long_name'] = 'Tendency of eastward wind due to TEM northward wind advection and coriolis'
   ds_out['utendwtem']   .attrs['long_name'] = 'Tendency of eastward wind due to TEM upward wind advection'
   ds_out['u']           .attrs['long_name'] = 'Zonal mean eastward wind'
   ds_out['z']           .attrs['long_name'] = 'Geopotential Height'
   #----------------------------------------------------------------------------
   # add variable units
   ds_out['vtem']        .attrs['units'] = 'm/s'
   ds_out['wtem']        .attrs['units'] = 'm/2'
   ds_out['psitem']      .attrs['units'] = 'kg/s'
   ds_out['utendepfd']   .attrs['units'] = 'm/s2'
   ds_out['utendvtem']   .attrs['units'] = 'm/s2'
   ds_out['utendwtem']   .attrs['units'] = 'm/s2'
   ds_out['u']           .attrs['units'] = 'm/s'
   ds_out['z']           .attrs['units'] = 'm'
   #----------------------------------------------------------------------------
   # write to file
   print(' '*4+f'writing to file: {dst_file}')
   ds_out.to_netcdf(path=dst_file,mode='w')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for n in range(len(case_list)):
      print('-'*80)
      main( case=case_list[n] )
   print_line()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
