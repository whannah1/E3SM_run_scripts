import os, numpy as np, xarray as xr, ngl, copy
import hapy_setres as hs
import hapy_common as hc
home = os.getenv('HOME')
#---------------------------------------------------------------------------------------------------
scratch_dir = '/global/cfs/cdirs/e3sm/inputdata'
# scratch_dir = '/gpfs/alpine/cli115/scratch/hannah6/inputdata'
topo_dir = f'{scratch_dir}/atm/cam/topo'
#---------------------------------------------------------------------------------------------------
grid_file_list = []
grid_name_list = []
topo_file_list = []
clat_list,clon_list = [],[]
slat_list,slon_list = [],[]
xlat_list,xlon_list = [],[]
def add_grid(file,name,topo=None,clat=0,clon=0,slat=None, slon=None, xlat=None, xlon=None):
  grid_file_list.append(file)
  grid_name_list.append(name)
  topo_file_list.append(topo)
  clat_list.append(clat); clon_list.append(clon)
  slat_list.append(slat); slon_list.append(slon)
  xlat_list.append(xlat); xlon_list.append(xlon)
#---------------------------------------------------------------------------------------------------

sohip_grid_root = '/global/cfs/cdirs/m4842/whannah/files_grid'

# 2025 SOHIP RRM grids

# add_grid(f'{sohip_grid_root}/2025-sohip-128x3_falkland_v1_pg2_scrip.nc','128x3_falkland_v1',clat=-50,clon=-60)
# add_grid(f'{sohip_grid_root}/2025-sohip-128x3_falkland_v2_pg2_scrip.nc','128x3_falkland_v2',clat=-50,clon=-60)
# add_grid(f'{sohip_grid_root}/2025-sohip-256x3-falkland-v3-pg2_scrip.nc','256x3_falkland_v3',clat=-50,clon=-60)
# add_grid(f'{sohip_grid_root}/2025-sohip-256x3-falkland-v4-pg2_scrip.nc','256x3_falkland_v4',clat=-50,clon=-60)

# add_grid(f'{sohip_grid_root}/2025-sohip-256x3-patagonia-pg2_scrip.nc','patagonia',clat=-60,clon= -50, slat=-49.46, slon=-60.24, xlat=None, xlon=None)
# add_grid(f'{sohip_grid_root}/2025-sohip-256x3-se-pac-pg2_scrip.nc',   'se-pac',   clat=-50,clon= -95, slat=-49.60, slon=-94.45, xlat=None, xlon=None)
# add_grid(f'{sohip_grid_root}/2025-sohip-256x3-sc-pac-pg2_scrip.nc',   'sc-pac',   clat=-35,clon=-135, slat=-34.73, slon=-136.73, xlat=None, xlon=None)
# add_grid(f'{sohip_grid_root}/2025-sohip-256x3-sw-ind-pg2_scrip.nc',   'sw-ind',   clat=-50,clon=  45, slat=-49.61, slon= 45.20, xlat=None, xlon=None)
# add_grid(f'{sohip_grid_root}/2025-sohip-256x3-eq-ind-pg2_scrip.nc',   'eq-ind',   clat=-5, clon=  80, slat=[-6.99,-3.05], slon=[84.74,75.97], xlat=None, xlon=None)
# add_grid(f'{sohip_grid_root}/2025-sohip-256x3-sc-ind-pg2_scrip.nc',   'sc-ind',   clat=-50,clon=  80, slat=-52.49, slon=67.04, xlat=None, xlon=None)


add_grid(f'{sohip_grid_root}/2025-sohip-256x3-eq-ind-pg2_scrip.nc',   'eq-ind',   clat=-5, clon=  80, slat=[-6.99,-3.05], slon=[84.74,75.97], xlat=None, xlon=None)
add_grid(f'{sohip_grid_root}/2025-sohip-256x3-eq-ind-v2-pg2_scrip.nc','eq-ind-v2',clat=-5, clon=  80, slat=[-6.99,-3.05], slon=[84.74,75.97], xlat=None, xlon=None)

# grid_root = '/global/cfs/cdirs/m4310/whannah/files_grid'
# topo_root = '/global/cfs/cdirs/m4310/whannah/files_topo'
# add_grid(f'{grid_root}/ne18pg2_scrip.nc','ne18',topo=f'{topo_root}/USGS-topo_ne18np4_smoothedx6t_20250513.nc',clat=30,clon=-75)
# add_grid(f'{grid_root}/ne22pg2_scrip.nc','ne22',topo=f'{topo_root}/USGS-topo_ne22np4_smoothedx6t_20250513.nc',clat=30,clon=-75)
# add_grid(f'{grid_root}/ne26pg2_scrip.nc','ne26',topo=f'{topo_root}/USGS-topo_ne26np4_smoothedx6t_20250513.nc',clat=30,clon=-75)
# add_grid(f'{grid_root}/ne30pg2_scrip.nc','ne30',topo=f'{topo_root}/USGS-topo_ne30np4_smoothedx6t_20250513.nc',clat=30,clon=-75)


fig_file,fig_type = f'{home}/E3SM/figs_grid/grid.scrip.v2','png'

num_grid = len(grid_file_list)

num_plot_col = 3
# num_plot_col = num_grid

#---------------------------------------------------------------------------------------------------
# debug section - just print stuff and exit
for f,grid_file in enumerate(grid_file_list):
  ds_grid = xr.open_dataset(grid_file)
  hc.print_stat( ds_grid['grid_area']*1e3, name=f'{grid_name_list[f]:20}', compact=True )
  # print('  area sum = '+str(np.sum(ds_grid['grid_area'].values)) )

#---------------------------------------------------------------------------------------------------
# Set up workstation
wkres = ngl.Resources()
npix = 2048; wkres.wkWidth,wkres.wkHeight=npix,npix # 1024 / 2048 / 4096
wks = ngl.open_wks(fig_type,fig_file,wkres)
plot = [None]*num_grid
res = ngl.Resources()
res.nglDraw,res.nglFrame         = False,False
res.tmXTOn                       = False
res.tmYROn                       = False
res.tmXBMajorOutwardLengthF      = 0.
res.tmXBMinorOutwardLengthF      = 0.
res.tmYLMajorOutwardLengthF      = 0.
res.tmYLMinorOutwardLengthF      = 0.
res.tmYLLabelFontHeightF         = 0.015
res.tmXBLabelFontHeightF         = 0.015
res.tiXAxisFontHeightF           = 0.015
res.tiYAxisFontHeightF           = 0.015

res.tmXBMinorOn,res.tmYLMinorOn  = False,False
res.tmXBOn,res.tmYLOn  = False,False

res.cnFillOn                     = True
res.cnLinesOn                    = False
res.cnLineLabelsOn               = False
res.cnInfoLabelOn                = False
res.lbOrientation                = "Horizontal"
res.lbLabelFontHeightF           = 0.008

res.mpGridAndLimbOn              = True

res.cnFillMode      = 'CellFill'
# res.cnCellFillEdgeColor = 'black'

res.lbLabelBarOn = False

### use this for no topo data
#res.cnFillPalette   = "CBR_wet"

# res.mpCenterLonF          = 180
# res.mpCenterLonF          = 30

# res.mpProjection          = 'Robinson'
# res.mpProjection          = "Satellite"
res.mpProjection          = "Orthographic"
# res.mpOutlineBoundarySets = 'NoBoundaries'
res.mpPerimOn             = False
res.pmTickMarkDisplayMode = "Never"

res.mpGeophysicalLineColor = 'white'
res.mpGeophysicalLineThicknessF = 6

### turn off color fill
# res.cnFillOpacityF = 0.0

# res.mpLimitMode     = 'LatLon'

# # Arabian Penninsula
# res.mpMinLatF,res.mpMaxLatF      =  0, 60
# res.mpMinLonF,res.mpMaxLonF      =  0, 90

mres = ngl.Resources()
mres.nglDraw,mres.nglFrame         = False,False
mres.xyMarkLineMode = 'Markers'
mres.xyMarkerColor = 'red'
mres.xyMarkerSizeF = 0.008

#---------------------------------------------------------------------------------------------------
# Load data and create plot

# for f,(grid_file,topo_file) in enumerate( zip(grid_file_list,topo_file_list) ):

grid_data_list = []
topo_data_list = []

for f in range(num_grid):
  grid_file = grid_file_list[f]
  topo_file = topo_file_list[f]
  ds_grid = xr.open_dataset(grid_file)
  #-----------------------------------------------------------------------------
  if topo_file is not None:
    ds_topo = xr.open_dataset(topo_file)
    if 'PHIS' in ds_topo.variables:
      topo = ds_topo['PHIS'].values
      topo = topo / 9.81
    else:
      topo = ds_topo['terr'].values
    # land = ds_topo['LANDFRAC'].values
    # topo = np.where(land>0.5,topo,-1e3)
  else:
    topo = ds_grid['grid_area'].values
  
  topo_data_list.append(topo) 
#---------------------------------------------------------------------------------------------------
area_min = 12
area_max = 0
for f in range(num_grid):
  if topo_file_list[f] is None:
    area_min = np.min([area_min,np.nanmin(topo_data_list[f])])
    area_max = np.max([area_max,np.nanmax(topo_data_list[f])])
(cmin,cmax,cint) = ngl.nice_cntr_levels(area_min, area_max, outside=False, cint=None, max_steps=11, aboutZero=False )

# print(cmin)
# print(cmax)
# print(np.log10(cmin))
# print(np.log10(cmax))
# exit()
#---------------------------------------------------------------------------------------------------
for f in range(num_grid):
  grid_file = grid_file_list[f]
  topo_file = topo_file_list[f]
  ds_grid = xr.open_dataset(grid_file)
  topo = topo_data_list[f]
  #-----------------------------------------------------------------------------
  tres = copy.deepcopy(res)
  fac = 1.
  # if np.max(ds_grid['grid_center_lat'].values)<4: fac = 180./np.pi
  tres.sfXArray      = ds_grid['grid_center_lon'].values * fac
  tres.sfYArray      = ds_grid['grid_center_lat'].values * fac
  tres.sfXCellBounds = ds_grid['grid_corner_lon'].values * fac
  tres.sfYCellBounds = ds_grid['grid_corner_lat'].values * fac

  if topo_file is not None:
    tres.cnFillPalette   = "OceanLakeLandSnow"
    tres.cnLevelSelectionMode = "ExplicitLevels"
    tres.cnLevels = np.arange(5,4805+105,105)
  else:
    tres.cnFillPalette   = "MPL_viridis"
    tres.cnLevelSelectionMode = "ExplicitLevels"
    # tres.cnLevels = np.linspace(cmin,cmax,num=21)
    tres.cnLevels = np.logspace(np.log10(cmin),np.log10(cmax),num=30)
    tres.cnLevelSelectionMode = 'ExplicitLevels'

  tres.mpCenterLonF = clon_list[f]
  tres.mpCenterLatF = clat_list[f]
  
  # res.tiXAxisString = 'normalized level index'
  # res.tiYAxisString = 'lev [mb]'

  # hc.print_stat(topo)

  plot[f] = ngl.contour_map(wks, topo, tres)

  #-----------------------------------------------------------------------------
  if slat_list[f] is not None and slon_list[f] is not None:
    mres.xyMarker = 16
    if isinstance(slat_list[f], list):
      xx = np.array([slon_list[f]])
      yy = np.array([slat_list[f]])
    else:
      xx = np.array([1,1])*slon_list[f]
      yy = np.array([1,1])*slat_list[f]
    ngl.overlay(plot[f], ngl.xy(wks, xx, yy, mres) )
  #-----------------------------------------------------------------------------
  if xlat_list[f] is not None and xlon_list[f] is not None:
    mres.xyMarker = 5
    xx = [1,1]*xlon_list[f]
    yy = [1,1]*xlat_list[f]
    ngl.overlay(plot[f], ngl.xy(wks, xx, yy, mres) )
  #-----------------------------------------------------------------------------
  hs.set_subtitles(wks, plot[f], '', grid_name_list[f], '', font_height=0.015)
  
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
# pres.nglPanelXWhiteSpacePercent = 5

# layout = [num_grid,1]

layout = [int(np.ceil(len(plot)/float(num_plot_col))),num_plot_col]

ngl.panel(wks,plot,layout,pres); ngl.end()

# trim white space
fig_file = f'{fig_file}.{fig_type}'
os.system(f'convert -trim +repage {fig_file}   {fig_file}')
fig_file = fig_file.replace(os.getenv('HOME')+'/E3SM/','')
print(f'\n{fig_file}\n')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
