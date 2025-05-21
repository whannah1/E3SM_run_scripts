import xarray as xr, numpy as np
#-------------------------------------------------------------------------------
# inputdata_root = '/gpfs/alpine/cli115/scratch/hannah6/inputdata'
inputdata_root = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata'
init_scratch = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
#-------------------------------------------------------------------------------
# F2010 SST data
sst_file_name = 'sst_ice_CMIP6_DECK_E3SM_1x1_2010_clim_c20190821.nc'
ifile = f'{inputdata_root}/ocn/docn7/SSTDATA/{sst_file_name}'
#-------------------------------------------------------------------------------
sst_pert_list = [1,2,3,4]
for sst_pert in sst_pert_list:
  # read the input file
  ds = xr.open_dataset(ifile,decode_times=False)
  # specify output file
  ofile = f'{init_scratch}/{sst_file_name}'
  ofile = ofile.replace('.nc',f'.SSTPERT_{sst_pert}K.nc')
  # print the file names
  print()
  print(f'ifile: {ifile}')
  print(f'ofile: {ofile}')
  print()
  # add perturbation
  sst_var = 'SST_cpl'
  ds[sst_var] = ds[sst_var] + sst_pert
  ds.compute()
  # create output file
  ds.to_netcdf(path=ofile,mode='w',format='NETCDF3_64BIT')
#-------------------------------------------------------------------------------
