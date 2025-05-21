import os, numpy as np, xarray as xr, ngl, copy
import hapy_setres as hs
import hapy_common as hc
home = os.getenv('HOME')

grid_file_list,topo_file_list,grid_name = [],[],[]

grid_name.append(f'CARRM')
grid_file_list.append('/global/cfs/cdirs/e3sm/zhang73/grids2/CAne32x32v1/CA_ne32_x32_v1_pg2_scrip.nc')
topo_file_list.append('/global/cfs/cdirs/e3sm/inputdata/atm/cam/topo/USGS-gtopo30_CA_ne32_x32_v1_pg2_16xdel2.nc')


fig_type = 'png'
fig_file = 'figs_grid/grid.CARRM'

region_list = []
dx,dy = 10,8
cy,cx = 36,360-120.; region_list.append([cy-dy, cy+dy, cx-dx, cx+dx]) # California


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
# npix = 4096; wkres.wkWidth,wkres.wkHeight=npix,npix
npix = 1024; wkres.wkWidth,wkres.wkHeight=npix,npix
wks = ngl.open_wks(fig_type,fig_file,wkres)
plot = [None]*( len(region_list) * len(grid_file_list) )
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

res.lbLabelBarOn = False
res.cnFillPalette  = 'OceanLakeLandSnow'
res.cnLevelSelectionMode = 'ExplicitLevels'
# res.cnLevels = np.arange(0,4000+100,100)
res.cnLevels = np.arange(0,3000+50,50)

res.mpGridAndLimbOn       = False

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def set_subtitle(wks, plot, center_sub_string ):
  ttres         = ngl.Resources()
  ttres.nglDraw = False
  ttres.txFontHeightF = 0.015
  ttres.txPerimOn = True
  # ttres.txBackgroundFillColor = (0,0,0,0.2)
  # ttres.txFontColor = (0,0,0,1)
  ttres.txBackgroundFillColor = (0,0,0,0.4)
  ttres.txFontColor = (1,1,1,1)
  # Use plot extent to call ngl.text(), otherwise you will see this error:
  # GKS ERROR NUMBER   51 ISSUED FROM SUBROUTINE GSVP  : --RECTANGLE DEFINITION IS INVALID
  strx = ngl.get_float(plot,"trXMinF")
  stry = ngl.get_float(plot,"trYMinF")
  # Set annotation resources to describe how close text is to be attached to plot
  amres = ngl.Resources()
  if not hasattr(ttres,"amOrthogonalPosF"):
    amres.amOrthogonalPosF = -0.50-0.02   # Top of plot plus a little extra to stay off the border
  else:
    amres.amOrthogonalPosF = ttres.amOrthogonalPosF
  # Add "sub-sub-titles" that sit inside the plot border, below the other subtitles
  sub_dy = -0.50+0.1
  amres.amOrthogonalPosF = -0.50-0.02+0.1
  tx_id_c2 = ngl.text(wks, plot, center_sub_string, strx, stry-sub_dy, ttres)
  amres.amJust,amres.amParallelPosF = "BottomCenter",0.0   # Centered
  amres.amOrthogonalPosF = -0.50-0.02+0.1 + 0.1
  anno_id_c2 = ngl.add_annotation(plot, tx_id_c2, amres)
  return
#-------------------------------------------------------------------------------
# Load data and create plot
#-------------------------------------------------------------------------------
for r,coords in enumerate(region_list):
  
  print(f'r: {r}')

  [lat1,lat2,lon1,lon2] = coords

  if lat1 is not None:
    res.mpLimitMode     = 'LatLon'
    res.mpMinLatF,res.mpMaxLatF = lat1,lat2
    res.mpMinLonF,res.mpMaxLonF = lon1,lon2

  for f,(grid_file,topo_file) in enumerate( zip(grid_file_list,topo_file_list) ):

    print(f'f: {f}')

    ds_grid = xr.open_dataset(grid_file)

    if topo_file is not None:
      ds_topo = xr.open_dataset(topo_file)
      topo = ds_topo['PHIS'].values
      topo = topo / 9.81
      land = ds_topo['LANDFRAC'].values
      topo = np.where(land>0.5,topo,-1e3)
      # if lake_file_list[f] is not None:
      #   ds_lake = xr.open_dataset(lake_file_list[f])
      #   # hc.print_stat(ds_lake['PCT_LAKE'])
      #   lake = ds_lake['PCT_LAKE'].values
      #   topo = np.where(lake<50,topo,-1e3)
    else:
      res.cnFillPalette   = "CBR_wet"
      topo = ds_grid['grid_area'].values

    tres = copy.deepcopy(res)
    tres.sfXArray      = ds_grid['grid_center_lon'].values
    tres.sfYArray      = ds_grid['grid_center_lat'].values
    tres.sfXCellBounds = ds_grid['grid_corner_lon'].values
    tres.sfYCellBounds = ds_grid['grid_corner_lat'].values

    ip = r*len(grid_file_list)+f
    # ip = f*len(region_list)+r

    plot[ip] = ngl.contour_map(wks, topo, tres)

    # hs.set_subtitles(wks, plot[ip], '', grid_name[f], '', font_height=0.02)

    # if r==0:
    #   set_subtitle(wks,plot[ip],grid_name[f])
    
#-------------------------------------------------------------------------------
# Finalize plot
#-------------------------------------------------------------------------------
pres = ngl.Resources()
# pres.nglPanelLabelBar = True
# nglPanelLabelBarLabelFontHeightF
# pres.nglPanelFigureStrings            = ['a','b','c','d','e','f','g','h']
# pres.nglPanelFigureStringsJust        = "TopLeft"
# pres.nglPanelFigureStringsFontHeightF = 0.015
pres.nglPanelYWhiteSpacePercent = 0    
pres.nglPanelXWhiteSpacePercent = 0

# layout = [2,np.ceil(len(plot)/2)]
# layout = [1,len(plot)]

layout = [len(region_list),len(grid_file_list)] 
# layout = [len(grid_file_list),len(region_list)] 

ngl.panel(wks,plot,layout,pres); ngl.end()

# trim white space
fig_file = f'{fig_file}.{fig_type}'
os.system(f'convert -trim +repage {fig_file}   {fig_file}')
print(f'\n{fig_file}\n')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------