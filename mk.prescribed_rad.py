import os, subprocess as sp, numpy as np, xarray as xr
import hapy_common as hc, hapy_E3SM as he

# case = 'E3SM.GNUGPU.ne30pg2.F-MMFXX-RCEROT.BVT.RADNX_1.03'
case = 'E3SM.GNUCPU.ne30pg2.F-EAM-RCEROT.04'

# htype,first_file,num_files = 'h0',3,0
htype,first_file,num_files = 'h0',12,0


# file_path = os.getenv('SCRATCH')+'/e3sm_scratch/init_files/prescribed_rad'     # cori
file_path = os.getenv('SCRATCH')+'/e3sm_scratch/perlmutter/init_data/prescribed_rad' # perlmutter

file_path = f'{file_path}/{case}.global-mean-QR.nc'

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# case_obj = he.Case( name=case, data_dir='/global/cfs/cdirs/m1517/dyang/E3SM_MMF', data_sub='data_native' )
case_obj = he.Case( name=case, data_dir='/global/homes/w/whannah/E3SM/scratch_pm', data_sub='run' )

area = case_obj.load_data('area',htype=htype)

QRL = case_obj.load_data('QRL', htype=htype,first_file=first_file,num_files=num_files)
QRL_gbl_mean = ( (QRL*area).sum(dim='ncol') / area.sum(dim='ncol') ) 
QRL_gbl_mean = QRL_gbl_mean.mean(dim=('time'))
QRL_gbl_mean.compute()

QRS = case_obj.load_data('QRS', htype=htype,first_file=first_file,num_files=num_files)
QRS_gbl_mean = ( (QRS*area).sum(dim='ncol') / area.sum(dim='ncol') ) 
QRS_gbl_mean = QRS_gbl_mean.mean(dim=('time'))
QRS_gbl_mean.compute()

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# print(); print(QRL_gbl_mean)
# print(); print(QRS_gbl_mean)
# print()

# for k in range(len(QRL_gbl_mean['lev'].values)):
#   lev = QRL_gbl_mean['lev'][k].values
#   val = QRL_gbl_mean[k].values
#   print(f'  {k:4d}    {lev:10.3f}    {val:10.4f}')
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

QRL_gbl_mean.name = 'QRL'
QRS_gbl_mean.name = 'QRS'


# gbl_mean_ds = QRL_gbl_mean.to_dataset()
gbl_mean_ds = xr.Dataset()

gbl_mean_ds['QRL'] = QRL_gbl_mean
gbl_mean_ds['QRS'] = QRS_gbl_mean

gbl_mean_ds['ntime'] = len(QRL['time'].values)

# exit(gbl_mean_ds)

gbl_mean_ds.to_netcdf(path=file_path,mode='w')
print(); print(f'  {file_path}'); print()

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

