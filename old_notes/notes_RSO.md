
--------------------------------------------------------------------------------
```shell
/global/cfs/cdirs/e3sm/inputdata/ocn/docn7/SSTDATA/sst_ice_CMIP6_DECK_E3SM_1x1_2010_clim_c20190821.nc
/global/cfs/cdirs/e3sm/inputdata/ocn/docn7/RSO/pop_frc.1x1d.090130.nc
```
--------------------------------------------------------------------------------
# copy defualt SST data file and add old MLD for SOM for testing

```shell
SRC_ROOT=/global/cfs/cdirs/e3sm/inputdata/ocn/docn7/SSTDATA
DST_ROOT=/global/cfs/cdirs/e3sm/inputdata/ocn/docn7/RSO
SRC_FILE=${SRC_ROOT}/sst_ice_CMIP6_DECK_E3SM_1x1_2010_clim_c20190821.nc
DST_FILE=${DST_ROOT}/sst_ice_CMIP6_DECK_E3SM_1x1_2010_clim_c20190821_w-MLD.nc
MLD_FILE=${DST_ROOT}/pop_frc.1x1d.090130.nc
cp ${SRC_FILE} ${DST_FILE} 
ncks -5 -A -v hblt,xc,yc ${MLD_FILE} ${DST_FILE} 
```
--------------------------------------------------------------------------------
# commands for evaluating differnce in SST field

ncdump -h /global/cfs/cdirs/e3sm/inputdata/ocn/docn7/SSTDATA/sst_ice_CMIP6_DECK_E3SM_1x1_2010_clim_c20190821.nc | grep "float" 
ncdump -h /global/cfs/cdirs/e3sm/inputdata/ocn/docn7/RSO/pop_frc.1x1d.090130.nc | grep "float" 

ncks -v T /global/cfs/cdirs/e3sm/inputdata/ocn/docn7/RSO/pop_frc.1x1d.090130.nc /global/cfs/cdirs/e3sm/inputdata/ocn/docn7/RSO/pop_frc.1x1d.090130.alt.nc


ncrename -v T,SST_cpl /global/cfs/cdirs/e3sm/inputdata/ocn/docn7/RSO/pop_frc.1x1d.090130.alt.nc /global/cfs/cdirs/e3sm/inputdata/ocn/docn7/RSO/pop_frc.1x1d.090130.alt.nc


ncdiff -v SST_cpl /global/cfs/cdirs/e3sm/inputdata/ocn/docn7/SSTDATA/sst_ice_CMIP6_DECK_E3SM_1x1_2010_clim_c20190821.nc /global/cfs/cdirs/e3sm/inputdata/ocn/docn7/RSO/pop_frc.1x1d.090130.alt.nc  /global/cfs/cdirs/e3sm/inputdata/ocn/docn7/RSO/pop_frc.1x1d.090130.diff.nc

ncks -A -v time,time_bnds,lat,lon/global/cfs/cdirs/e3sm/inputdata/ocn/docn7/SSTDATA/sst_ice_CMIP6_DECK_E3SM_1x1_2010_clim_c20190821.nc /global/cfs/cdirs/e3sm/inputdata/ocn/docn7/RSO/pop_frc.1x1d.090130.diff.nc

--------------------------------------------------------------------------------
```python
import xarray as xr, numpy as np
file_path = '/global/cfs/cdirs/e3sm/inputdata/ocn/docn7/RSO/sst_ice_CMIP6_DECK_E3SM_1x1_2010_clim_c20190821_w-MLD.nc'
ds = xr.open_dataset(file_path)
# print(ds.hblt)
ds['hblt'] = xr.where(np.isnan(ds['hblt'].values),10,ds['hblt'])
# print(ds.hblt)
ds.load()
ds.to_netcdf(file_path)
```
--------------------------------------------------------------------------------
