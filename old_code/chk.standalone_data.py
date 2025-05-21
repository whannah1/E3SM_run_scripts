import xarray as xr, numpy as np
class tcolor: ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def print_stat(x,name='(no name)',unit='',fmt='f',stat='naxh',indent='',compact=False):
   """ Print min, avg, max, and std deviation of input """
   if fmt=='f' : fmt = '%.4f'
   if fmt=='e' : fmt = '%e'
   if unit!='' : unit = f'[{unit}]'
   name_len = 12 if compact else len(name)
   msg = ''
   line = f'{indent}{name:{name_len}} {unit}'
   # if not compact: print(line)
   if not compact: msg += line+'\n'
   for c in list(stat):
      if not compact: line = indent
      if c=='h' : line += '   shp: '+str(x.shape)
      if c=='a' : line += '   avg: '+fmt%x.mean()
      if c=='n' : line += '   min: '+fmt%x.min()
      if c=='x' : line += '   max: '+fmt%x.max()
      if c=='s' : line += '   std: '+fmt%x.std()
      # if not compact: print(line)
      if not compact: msg += line+'\n'
   # if compact: print(line)
   if compact: msg += line+'\n'
   print(msg)
   return msg
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

ds = xr.open_dataset('/gpfs/alpine/cli115/proj-shared/hannah6/crm_standalone_data/crmdata_3d_bug_combined.nc')

print(ds['in_zmid'].isel(unlim=5))
print(ds['in_zint'].isel(unlim=5))

# print_stat(ds['in_zmid'])
# print_stat(ds['in_zint'])

# for k,key in enumerate(ds.keys()): 

  # found = False
  # msg = f'  {key:30}'

  # da = ds[key].stack(x=ds[key].dims)
  
  # if any(da.isnull().values):  found=True; msg+= tcolor.RED    +'  Null values found!'+tcolor.ENDC
  # if any(np.isnan(da.values)): found=True; msg+= tcolor.MAGENTA+'  NaN found!'+tcolor.ENDC
  # if any(np.isinf(da.values)): found=True; msg+= tcolor.MAGENTA+'  Inf found!'+tcolor.ENDC
  
  # if not found: msg+= tcolor.GREEN+'  OK'+tcolor.ENDC

  # print(msg)
  