import os
import ngl 
import numpy as np
import hapy_common as hc
import numba
import xarray as xr
# import matplotlib.pyplot as plt
home = os.getenv("HOME")

grid = "ne30pg2"

num_neighbors  = 16
max_neighbors  = 64
find_neighbors = False

make_plot = True
fig_type = "png"
fig_file = home+"/E3SM/figs_init/smooth_topo."+grid+".num_neighbors_"+str(num_neighbors)

ifile = "/global/cscratch1/sd/whannah/acme_scratch/init_files/USGS_"+grid+"_unsmoothed_20190409.nc"
ofile = "/global/cscratch1/sd/whannah/acme_scratch/init_files/USGS_"+grid+"_smoothed_20190409.nc"

# Define temporary file to hold neighbor ids and distances
neighbor_file_name = home+"/E3SM/data_neighbors/"+grid+"_nearest-neighbors_"+str(max_neighbors).zfill(2)+".nc"

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
infile = xr.open_dataset(ifile)
phis = infile.variables['PHIS'].values
lat  = infile.variables['lat'].values
lon  = infile.variables['lon'].values
ncol = len(lat)

# print(infile)

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
   neighbor_dist = neighbor_ds.variables['neighbor_dist'].values

#-------------------------------------------------------------------------------
# Define function for smoothing
#-------------------------------------------------------------------------------
def smooth(X,area,dist,neighbor_id):
   X_b = np.empty(X.shape,dtype=X.dtype)
   for n in range(0,ncol) :
      nb_id = neighbor_id[:num_neighbors,n]
      X_b[n] = sum( X[nb_id] * area[nb_id] / np.sum(area[nb_id]) )
      # X_b[n] = sum( X[nb_id] * area[nb_id] / np.sum(area[nb_id]) / dist[:num_neighbors,n] )
   return X_b

#-------------------------------------------------------------------------------
# Smooth by averaging nearest neighbors
#-------------------------------------------------------------------------------

phis_smooth = phis

print("Smoothing...")
phis_smooth = smooth(phis_smooth,area,neighbor_dist,neighbor_id)
print("done.")

phis_diff = np.absolute( phis - phis_smooth )
hc.printMAM(phis,name_str="PHIS before: ")
hc.printMAM(phis_smooth,name_str="PHIS after: ")
hc.printMAM(phis_diff,name_str="absolute difference: ")

#-------------------------------------------------------------------------------
# Plot topo map
#-------------------------------------------------------------------------------
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
res.cnFillPalette    = "WhiteBlueGreenYellowRed"
dc = 4000
res.cnLevels = np.arange(0,52000+dc,dc)
if hasattr(res,'cnLevels') : res.cnLevelSelectionMode = "ExplicitLevels"
plot = []
plot.append( ngl.contour_map(wks,phis,res) )
plot.append( ngl.contour_map(wks,phis_smooth,res) )
layout = [len(plot),1]
ngl.panel(wks,plot[0:len(plot)],layout)
ngl.end()
# Crop white space from png image
hc.trim_png(fig_file)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

output_ds = xr.Dataset()
output_ds['PHIS'] = (('ncol'), phis_smooth)
output_ds['lat'] = infile.variables['lat']
output_ds['lon'] = infile.variables['lon']
output_ds['LANDFRAC'] = infile.variables['LANDFRAC']
output_ds['LANDM_COSLAT'] = infile.variables['LANDM_COSLAT']

# print(output_ds)

output_ds.to_netcdf(path=ofile,mode='w')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------