import os, numpy as np, xarray as xr, ngl, copy
import hapy_setres as hs
import hapy_common as hc
home = os.getenv('HOME')

grid_file_list,topo_file_list,grid_name = [],[],[]
topo_dir = '/global/cfs/cdirs/e3sm/inputdata/atm/cam/topo' # NERSC
# topo_dir = '/gpfs/alpine/cli115/scratch/hannah6/inputdata/atm/cam/topo' #OLCF


# grid_file_list.append(f'{home}/E3SM/data_grid/ne30np4_scrip.nc');  grid_name.append('ne30np4')
grid_file_list.append(f'{home}/E3SM/data_grid/ne30pg2_scrip.nc');  grid_name.append('ne30pg2')
grid_file_list.append(f'{home}/E3SM/data_grid/ne120pg2_scrip.nc'); grid_name.append('ne120pg2')
# grid_file_list.append(f'{home}/HICCUP/data_scratch/ne1024pg2_scrip.nc');grid_name.append('ne1024pg2')

### identify topo data file
for grid in grid_file_list:
  found = False
  if 'ne30np4'   in grid: found=True;topo_file_list.append(f'{topo_dir}/USGS-gtopo30_ne30np4_16xdel2-PFC-consistentSGH.nc')
  if 'ne30pg2'   in grid: found=True;topo_file_list.append(f'{topo_dir}/USGS-gtopo30_ne30np4pg2_16xdel2.c20200108.nc')
  if 'ne120pg2'  in grid: found=True;topo_file_list.append(f'{topo_dir}/USGS-gtopo30_ne120np4pg2_16xdel2.nc')
  if 'ne1024pg2' in grid: found=True;topo_file_list.append(f'{topo_dir}/USGS-gtopo30_ne1024np4pg2_x6t-SGH.nc')
  if not found:topo_file_list.append(None)

fig_type = 'png'
fig_file = os.getenv('HOME')+'/E3SM/figs_grid/grid.scrip.v1'

# lat1,lat2,lon1,lon2 = 32, 44, 360-125, 360-113  # California
lat1,lat2,lon1,lon2 = 15, 35, 360-70, 360-90  # Florida

# NOTE - for high res land dataset make sure to issue this command in the terminal first:
# export PYNGL_RANGS=~/.conda/envs/pyn_env/lib/ncarg/database/rangs
hi_res_land = False


#-------------------------------------------------------------------------------
# debug section - just print stuff and exit
#-------------------------------------------------------------------------------
# for f,grid_file in enumerate(grid_file_list):
#   print()
#   ds_grid = xr.open_dataset(grid_file)
#   hc.print_stat( ds_grid['grid_area']*1e3, name=f'{grid_name[f]:20}', compact=True )
#   # print('  area sum = '+str(np.sum(ds_grid['grid_area'].values)) )
# exit()

#-------------------------------------------------------------------------------
# Set up workstation
#-------------------------------------------------------------------------------
wkres = ngl.Resources()
npix = 4096; wkres.wkWidth,wkres.wkHeight=npix,npix
wks = ngl.open_wks(fig_type,fig_file,wkres)
plot = []
res = ngl.Resources()
res.nglDraw,res.nglFrame         = False,False
res.tmXTOn                       = False
res.tmXBMajorOutwardLengthF      = 0.
res.tmXBMinorOutwardLengthF      = 0.
res.tmYLMajorOutwardLengthF      = 0.
res.tmYLMinorOutwardLengthF      = 0.
res.tmYLLabelFontHeightF         = 0.015
res.tmXBLabelFontHeightF         = 0.015
res.tiXAxisFontHeightF           = 0.015
res.tiYAxisFontHeightF           = 0.015
res.tmXBMinorOn,res.tmYLMinorOn  = False,False
res.tmXBOn,res.tmYLOn            = False,False

res.cnFillOn                     = True
res.cnLinesOn                    = False
res.cnLineLabelsOn               = False
res.cnInfoLabelOn                = False
res.lbOrientation                = 'Horizontal'
res.lbLabelFontHeightF           = 0.008

res.mpOutlineSpecifiers = "conterminous us : states"   # plot state boundaries
if hi_res_land:
  res.mpDataBaseVersion = "HighRes"
else:
  res.mpDataBaseVersion = "MediumRes"

res.cnFillMode      = 'CellFill'
res.cnCellFillEdgeColor = 'black'

res.lbLabelBarOn = True
res.cnFillPalette  = 'OceanLakeLandSnow'
res.cnLevelSelectionMode = 'ExplicitLevels'
res.cnLevels = np.arange(0,4000+100,100)

res.mpGridAndLimbOn       = False

if 'lat1' in locals():
  res.mpLimitMode     = 'LatLon'
  res.mpMinLatF,res.mpMaxLatF = lat1,lat2
  res.mpMinLonF,res.mpMaxLonF = lon1,lon2


#-------------------------------------------------------------------------------
# Load data and create plot
#-------------------------------------------------------------------------------
for f,(grid_file,topo_file) in enumerate( zip(grid_file_list,topo_file_list) ):

  ds_grid = xr.open_dataset(grid_file)

  if topo_file is not None:
    ds_topo = xr.open_dataset(topo_file)
    topo = ds_topo['PHIS'].values
    topo = topo / 9.81
    land = ds_topo['LANDFRAC'].values
    topo = np.where(land>0.5,topo,-1e3)
  else:
    res.cnFillPalette   = "CBR_wet"
    topo = ds_grid['grid_area'].values

  tres = copy.deepcopy(res)
  tres.sfXArray      = ds_grid['grid_center_lon'].values
  tres.sfYArray      = ds_grid['grid_center_lat'].values
  tres.sfXCellBounds = ds_grid['grid_corner_lon'].values
  tres.sfYCellBounds = ds_grid['grid_corner_lat'].values

  plot.append( ngl.contour_map(wks, topo, tres) )

  hs.set_subtitles(wks, plot[len(plot)-1], '', grid_name[f], '', font_height=0.02)
  
#-------------------------------------------------------------------------------
# Finalize plot
#-------------------------------------------------------------------------------
pres = ngl.Resources()
# pres.nglPanelLabelBar = True
# nglPanelLabelBarLabelFontHeightF
# pres.nglPanelFigureStrings            = ['a','b','c','d','e','f','g','h']
# pres.nglPanelFigureStringsJust        = "TopLeft"
# pres.nglPanelFigureStringsFontHeightF = 0.015
pres.nglPanelYWhiteSpacePercent = 5    
pres.nglPanelXWhiteSpacePercent = 5

# layout = [2,np.ceil(len(plot)/2)]
layout = [1,len(plot)]
ngl.panel(wks,plot,layout,pres); ngl.end()

# trim white space
fig_file = f'{fig_file}.{fig_type}'
os.system(f'convert -trim +repage {fig_file}   {fig_file}')
print(f'\n{fig_file}\n')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------