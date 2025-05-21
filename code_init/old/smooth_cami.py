import os
import ngl 
import numpy as np
import hapy_common as hc
import numba
import xarray as xr
# import matplotlib.pyplot as plt
home = os.getenv("HOME")

grid = "ne30np4"

num_neighbors  = 16
max_neighbors  = 64
find_neighbors = False

make_plot = True
fig_type = "png"
fig_file = home+"/E3SM/figs_init/smooth_cami."+grid+".num_neighbors_"+str(num_neighbors)

ifile = "/project/projectdirs/acme/inputdata/atm/cam/inic/homme/cami_mam3_Linoz_"+grid+"_L72_c160214.nc"
ofile = "/global/cscratch1/sd/whannah/acme_scratch/init_files/cami_mam3_Linoz_"+grid+"_L72_c160214.smoothed.nc"

# Define temporary file to hold neighbor ids and distances
neighbor_file_name = home+"/E3SM/data_neighbors/"+grid+"_nearest-neighbors_"+str(max_neighbors).zfill(2)+".nc"

var_list = ['PS','T','Q','U','V']
# var_list = ['PS']

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
print()
print("input topo file   : "+ifile)
print("output topo file  : "+ofile)
print("tmp neighbor file : "+neighbor_file_name)
print()
#-------------------------------------------------------------------------------
# Load topo data
#-------------------------------------------------------------------------------
ids = xr.open_dataset(ifile)
lat  = ids.variables['lat'].values
lon  = ids.variables['lon'].values
ncol = len(lat)

# Create output dataset
ods = ids.copy()

#-------------------------------------------------------------------------------
# Get grid cell areas from scrip file
#-------------------------------------------------------------------------------
sfile = home+'/E3SM/data_grid/'+grid+'_scrip.nc'
if not os.path.isfile(sfile) : sfile = home+'/Research/E3SM/data_grid/'+grid+'_scrip.nc'
scripfile = xr.open_dataset(sfile)
area = scripfile.variables['grid_area'].values

#-------------------------------------------------------------------------------
# Define function
#-------------------------------------------------------------------------------
def find_nearest_neighbors_on_sphere(lat,lon,num_neighbors) :
   ncol = len(lat)
   neighbor_id    = np.empty([num_neighbors+1,ncol], dtype=np.int32)
   neighbor_dist  = np.empty([num_neighbors+1,ncol], dtype=np.float32)
   for n in range(0,ncol):
      dist = hc.calc_great_circle_distance(lat[n],lat[:],lon[n],lon[:])
      p_vector = np.argsort(dist,kind='mergesort')
      neighbor_id[:,n]   = p_vector[0:num_neighbors+1]     # include current point
      neighbor_dist[:,n] = dist[p_vector[0:num_neighbors+1]]
   # return neighbor_id
   neighbor_ds = xr.Dataset()
   neighbor_ds['neighbor_id']   = (('ncol','neighbors'), neighbor_id)
   neighbor_ds['neighbor_dist'] = (('ncol','neighbors'), neighbor_dist)
   return neighbor_ds
#-------------------------------------------------------------------------------
# Find neighbors
#-------------------------------------------------------------------------------
if not os.path.isfile(neighbor_file_name) : find_neighbors = True

if find_neighbors:
   
   neighbor_ds = find_nearest_neighbors_on_sphere(lat,lon,max_neighbors)

   neighbor_id   = neighbor_ds.variables['neighbor_id'].values
   neighbor_dist = neighbor_ds.variables['neighbor_dist'].values
   
   # Write neighbor ids and distances to file
   neighbor_ds.to_netcdf(path=neighbor_file_name,mode='w')

else:
   # Load previously identified neighbor ids
   neighbor_ds   = xr.open_dataset(neighbor_file_name)
   neighbor_id   = neighbor_ds.variables['neighbor_id'].values
   # neighbor_dist = neighbor_ds.variables['neighbor_dist'].values

#-------------------------------------------------------------------------------
# Define function for smoothing
#-------------------------------------------------------------------------------
def smooth(X,area,neighbor_id):
   X_b = np.empty(X.shape,dtype=X.dtype)
   for n in range(X.shape[-1]):
      nb_id = neighbor_id[:num_neighbors,n]
      wgt = area[nb_id] / np.sum(area[nb_id])
      X_b[...,n] = np.average( X[...,nb_id] ,axis=-1,weights=wgt )
   return X_b

#-------------------------------------------------------------------------------
# Smooth by averaging nearest neighbors
#-------------------------------------------------------------------------------

print("\nSmoothing...\n")

for key, var in ods.variables.items():
   if key in var_list:
      print("  "+key)
      ods[key].values = smooth( ods[key].values ,area,neighbor_id) 
      # var[0,:].values = smooth( var[0,:].values ,area,neighbor_id) 
      # ods[key][0,:].values = ods[key][0,:].values * 0.

print("\ndone.\n")

### Debugging check
if key in var_list:
   print("\n"+key+":\n")
   diff = ods.variables[key].values - ids.variables[key].values
   hc.printMAM( ids.variables[key].values ,name_str="before: ")
   hc.printMAM( ods.variables[key].values ,name_str="after-before: ")
   hc.printMAM(diff,name_str="after: ")
   print()
# exit()

#-------------------------------------------------------------------------------
# Plot topo map
#-------------------------------------------------------------------------------
if make_plot:
   wks = ngl.open_wks(fig_type,fig_file)
   res = ngl.Resources()
   res.nglDraw  = False
   res.nglFrame = False
   res.cnFillOn         = True
   res.cnLinesOn        = False
   res.cnLineLabelsOn   = False
   res.lbOrientation    = "horizontal"
   res.mpGridAndLimbOn  = False
   res.mpPerimOn        = False
   res.cnFillMode       = "CellFill"
   res.sfXArray         = scripfile.variables['grid_center_lon'].values
   res.sfYArray         = scripfile.variables['grid_center_lat'].values
   res.sfXCellBounds    = scripfile.variables['grid_corner_lon'].values
   res.sfYCellBounds    = scripfile.variables['grid_corner_lat'].values
   # res.cnFillPalette    = "WhiteBlueGreenYellowRed"
   # dc = 4000
   # res.cnLevels = np.arange(0,52000+dc,dc)
   # if hasattr(res,'cnLevels') : res.cnLevelSelectionMode = "ExplicitLevels"
   plot = []
   plot.append( ngl.contour_map(wks,ids['PS'][0,:].values,res) )
   plot.append( ngl.contour_map(wks,ods['PS'][0,:].values,res) )
   layout = [len(plot),1]
   ngl.panel(wks,plot[0:len(plot)],layout)
   ngl.end()
   # Crop white space from png image
   hc.trim_png(fig_file)

   # exit()

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

ods.to_netcdf(path=ofile,mode='w')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------