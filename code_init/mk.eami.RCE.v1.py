'''
The idea here is to create a starting point for RCE runs, by taking the 
global mean of data from [ifile] and use that to overwrite the values 
read in from [cfile] and write the result to [ofile]
'''
#-------------------------------------------------------------------------------
import os, numpy as np, xarray as xr, subprocess as sp

# timestamp = '20230223'
# timestamp = '20230309'
timestamp = '20230310'

dst_nz = 60  # 60 / 72
dst_ne = 16  # 8 / 16 / 32 / 64 / 128 / 256

if dst_nz==60:
  # ifile = f'/gpfs/alpine/cli115/world-shared/e3sm/inputdata/atm/cam/inic/homme/eam_i_rcemip_ne4np4_L60_c20210917.nc'
  ifile = f'/ccs/home/hannah6/E3SM/scratch2/E3SM.RCE-GRID-SENS-SPINUP-01.FRCE-MMF1.ne128pg2/run/E3SM.RCE-GRID-SENS-SPINUP-01.FRCE-MMF1.ne128pg2.eam.i.0001-01-06-00000.nc'
  ofile = f'/gpfs/alpine/scratch/hannah6/cli115/HICCUP/data/eam_i_rce_ne{dst_ne}_L60_c{timestamp}.nc'
  cfile = f'/gpfs/alpine/scratch/hannah6/cli115/HICCUP/data/eam_i_aquaplanet_ne{dst_ne}_L60_c20221212.nc'
  # if dst_ne==128:cfile = f'/gpfs/alpine/scratch/hannah6/cli115/HICCUP/data/eam_i_aquaplanet_ne{dst_ne}_L60_c20221212.nc'
  # if dst_ne== 64:
  # if dst_ne== 32:cfile = f'/gpfs/alpine/scratch/hannah6/cli115/HICCUP/data/eam_i_aquaplanet_ne{dst_ne}_L60_c20221212.nc'
  # if dst_ne== 16:
if dst_nz==72:
  # ifile = f'/gpfs/alpine/cli115/world-shared/e3sm/inputdata/atm/cam/inic/homme/cami_rcemip_ne4np4_L72_c190919.nc'
  ifile = f'/ccs/home/hannah6/E3SM/scratch2/E3SM.RCE-GRID-SENS-SPINUP-01.FRCE.ne128pg2/run/E3SM.RCE-GRID-SENS-SPINUP-01.FRCE.ne128pg2.eam.i.0001-01-06-00000.nc'
  cfile = f'/gpfs/alpine/scratch/hannah6/cli115/HICCUP/data/eam_i_aquaplanet_ne{dst_ne}_L72_c20221212.nc'
  ofile = f'/gpfs/alpine/scratch/hannah6/cli115/HICCUP/data/eam_i_rce_ne{dst_ne}_L72_c{timestamp}.nc'

print()
print(f'  ifile: {ifile}')
print(f'  cfile: {cfile}')
print(f'  ofile: {ofile}')
print()
# exit()

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

ds_copy = xr.open_dataset(cfile, decode_cf=False, engine='netcdf4')
ds      = xr.open_dataset(ifile, decode_cf=False, engine='netcdf4')

for var in ds.variables:
  if var in ['lat','lon','lat_d','lon_d','area','area_d']: continue
  if var in ds_copy.variables:
    if 'ncol'   in ds[var].dims: ds_copy[var] = ds_copy[var]*0 + ds[var].mean(dim='ncol')
    if 'ncol_d' in ds[var].dims: ds_copy[var] = ds_copy[var]*0 + ds[var].mean(dim='ncol_d')
    if var in ['U','V']: ds_copy[var] = ds_copy[var]*0

# remove problematic aerosol fields
for var in ds_copy.variables:
  if var in ['DMS','H2O2','H2SO4','SO2','SOAG',
            'bc_a1','bc_a3','bc_a4','dst_a1','dst_a3',
            'mom_a1','mom_a2','mom_a3','mom_a4','ncl_a1','ncl_a2','ncl_a3'
            ,'num_a1','num_a2','num_a3','num_a4','pom_a1','pom_a3','pom_a4'
            ,'so4_a1','so4_a2','so4_a3','soa_a1','soa_a2','soa_a3'
            ]:
    ds_copy = ds_copy.drop(var)

if 'ncol' in ds.dims and 'ncol_d' not in ds.dims: ds_copy = ds_copy.rename({'ncol':'ncol_d'})

print(); print(f'writing to ofile: {ofile}')

ds_copy.to_netcdf(ofile)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

print()
print('Converting to cdf5...')
cmd=f'ncks -O -5 {ofile} {ofile}.cdf5'; print(cmd); sp.call(cmd.split(' '))
cmd=f'mv {ofile}.cdf5 {ofile}'; print(cmd); sp.call(cmd.split(' '))
# cmd=f'ncpdq -O -a time,lev,ncol_d {ofile}.cdf5 {ofile}'; print(cmd); sp.call(cmd.split(' ')) # no need for this
print('done.')
print()

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------