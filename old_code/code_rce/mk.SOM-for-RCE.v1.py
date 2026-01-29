import os, copy, xarray as xr, numpy as np
#-------------------------------------------------------------------------------
som_file = '/global/cfs/cdirs/e3sm/inputdata/ocn/docn7/SOM/pop_frc.1x1d.090130.nc'

# grd_root = '/global/cfs/cdirs/e3sm/inputdata/ocn/mpas-o'
# grd = 'oQU480';      grd_file = f'{grd_root}/oQU480/ocean.QU.480km.scrip.181106.nc'
# grd = 'oEC60to30v3'; grd_file = f'{grd_root}/oEC60to30v3/ocean.oEC60to30v3.scrip.181106.nc'

grd_root = '/global/cfs/cdirs/e3sm/mapping/grids/'
grd = 'ne4pg2';  grd_file = f'{grd_root}/ne4pg2_scrip_c20191218.nc'
# grd = 'ne30pg2'; grd_file = f'{grd_root}/ne30pg2_scrip_20200209.nc'


# qdp,bld,T_k,S = 50,30,300,34
qdp,bld,T_k,S = 0,30,300,34

# out_path = '/pscratch/sd/w/whannah/e3sm_scratch/init_scratch'
out_root = '/global/cfs/cdirs/e3sm/inputdata/ocn/docn7/SOM'
out_file = f'{out_root}/SOM-RCE.{grd}.qdp_{qdp}.bld_{bld}.T_{T_k}K.S_{S}.20240501.nc'
#-------------------------------------------------------------------------------
print(f'''
  
  input data file: {som_file}
  input grid file: {grd_file}

  output data file: {out_file}

''')
#-------------------------------------------------------------------------------
ds_grd = xr.open_dataset( grd_file )
ds_som = xr.open_dataset( som_file )
ds_out = xr.Dataset()

ntime = len( ds_som['time'])
ncol = len( ds_grd['grid_size'] )

# ds_out['time']  = ds_som['time']
# ds_out['ncol']  = ds_grd['grid_size'].rename(grid_size='ni')
ds_out['yc']    = ds_grd['grid_center_lat'].rename(grid_size='ni').expand_dims(dim='nj')
ds_out['xc']    = ds_grd['grid_center_lon'].rename(grid_size='ni').expand_dims(dim='nj')

# shape = (1,ncol)
# coords = {'nj':,'ni':ds_grd['grid_size'].rename(grid_size='ni')}

ds_out['area']  = ds_grd['grid_area'].rename(grid_size='ni').expand_dims(dim='nj')
ds_out['mask']  = xr.DataArray(np.full((1,ncol),1),dims=('nj','ni'))

shape = (ntime,1,ncol)
coords = {'time':ds_som['time'],'nj':np.arange(1),'ni':ds_grd['grid_size'].rename(grid_size='ni')}

ds_out['U']     = xr.DataArray(np.full(shape,0),coords)
ds_out['V']     = xr.DataArray(np.full(shape,0),coords)
ds_out['S']     = xr.DataArray(np.full(shape,S),coords)
ds_out['T']     = xr.DataArray(np.full(shape,T_k-273.15),coords)
ds_out['dhdx']  = xr.DataArray(np.full(shape,0),coords)
ds_out['dhdy']  = xr.DataArray(np.full(shape,0),coords)
ds_out['hblt']  = xr.DataArray(np.full(shape,bld),coords)
ds_out['qdp']   = xr.DataArray(np.full(shape,qdp),coords)

# print();print();print();print(ds_out)
# print();print();print();print(ds_som)
# print();print();print()
# ds_domain = xr.open_dataset('inputdata/share/domains/domain.ocn.oQU480.151209.nc')
# print(ds_domain)
# exit()

ds_out.to_netcdf(path=out_file,mode='w')
#-------------------------------------------------------------------------------