import os, numpy as np, xarray as xr


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def main():

  # ifile = os.getenv('HOME')+'/CESM/scratch/CESM.f09_g17.FSPCAMS/run/CESM.f09_g17.FSPCAMS.cam.h1.0001-01-01-00000.nc'

  # case = 'CESM.ne30pg2_ne30pg2_mg17.FSPCAMS.CRMNX_64.CRMDX_2000.CRMDT_5.NLEV_32.CRMNZ_30'
  # ifile = os.getenv('HOME')+f'/CESM/scratch/{case}/run/{case}.cam.h1.0001-01-01-00000.nc'

  data_root = os.getenv('SCRATCH')+'/HICCUP/data' # NERSC
  ifile = f'{data_root}/screami_ne30np4L128_20220913.nc'
  ofile = os.getenv('HOME')+f'/E3SM/vert_grid_files/SCREAM_L128.nc'
  
  print()
  print(f'  ifile: {ifile} ')

  ds_in = xr.open_dataset(ifile)

  mlev = ds_in['lev']
  ilev = ds_in['ilev']
  am   = ds_in['hyam']
  bm   = ds_in['hybm']
  ai   = ds_in['hyai']
  bi   = ds_in['hybi']
  # p0   = ds_in['P0']
  p0 = 100000

  num_mlev = len(mlev)

  # ofile = os.getenv('HOME')+f'/E3SM/vert_grid_files/L{num_mlev}_CESM.nc'


  print(f'  ofile: {ofile} ')
  print()

  mlev = xr.DataArray(mlev)
  ilev = xr.DataArray(ilev)

  ds = xr.Dataset()
  ds['lev']  = ('lev', mlev)
  ds['hyam'] = ('lev', am)
  ds['hybm'] = ('lev', bm)
  ds['ilev'] = ('ilev',ilev)
  ds['hyai'] = ('ilev',ai)
  ds['hybi'] = ('ilev',bi)
  ds['P0'] = p0

  ds['lev'].attrs['units']      = 'level'
  ds['lev'].attrs['positive']   = 'down'
  ds['ilev'].attrs['units']     = 'level'
  ds['ilev'].attrs['positive']  = 'down'
  ds['P0'].attrs['units']       = 'Pa'
  ds['P0'].attrs['long_name']   = 'reference pressure'
  ds['hyam'].attrs['long_name'] = 'hybrid A coefficient at layer midpoints'
  ds['hybm'].attrs['long_name'] = 'hybrid B coefficient at layer midpoints'
  ds['hyai'].attrs['long_name'] = 'hybrid A coefficient at layer interfaces'
  ds['hybi'].attrs['long_name'] = 'hybrid B coefficient at layer interfaces'
  
  # print(f'\n{ofile}\n')

  ds.to_netcdf(ofile)

  # print(f'\n{ofile}\n')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if __name__ == '__main__':
  main()

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------