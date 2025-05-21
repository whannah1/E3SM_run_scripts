import os, numpy as np, xarray as xr, ngl, copy, numba
import hapy_setres as hs, hapy_common as hc
home = os.getenv('HOME')
#-------------------------------------------------------------------------------
''' Generate grid file:
NE=30
GRIDPATH=~/E3SM/data_grid
GRIDPATH=
echo GenerateCSMesh --alt --res ${NE} --file ${GRIDPATH}/ne${NE}.g
echo GenerateVolumetricMesh --in ${GRIDPATH}/ne${NE}.g --out ${GRIDPATH}/ne${NE}pg2.g --np 2 --uniform
echo ConvertMeshToSCRIP --in ${GRIDPATH}/ne${NE}pg2.g --out ${GRIDPATH}/ne${NE}pg2_scrip.nc
echo; echo ${GRIDPATH}/ne${NE}pg2_scrip.nc ; echo 
'''
#-------------------------------------------------------------------------------
grid_file_list,topo_file_list,name = [],[],[]
scratch_dir = '/global/cfs/cdirs/e3sm/inputdata'
# scratch_dir = '/gpfs/alpine/cli115/scratch/hannah6/inputdata'
topo_dir = f'{scratch_dir}/atm/cam/topo'



# grid_file_list.append(f'{home}/E3SM/data_grid/ne2pg2_scrip.nc');      name.append('ne4')
# grid_file_list.append(f'{home}/E3SM/data_grid/ne4pg2_scrip.nc');      name.append('ne4')
grid_file_list.append('/gpfs/alpine/scratch/hannah6/cli115/ECRP-data/ECRP_RRM_v0_demo_pg2_scrip.nc');      name.append('ne4')

fig_type = 'png'
fig_file = os.getenv('HOME')+'/E3SM/figs_grid/grid.np4_vs_pg2.v1'

#-------------------------------------------------------------------------------
# debug section - just print stuff and exit
#-------------------------------------------------------------------------------
for f,grid_file in enumerate(grid_file_list):
  print()
  ds_grid = xr.open_dataset(grid_file)
  hc.print_stat( ds_grid['grid_area']*1e3, name=f'{name[f]:20}', compact=True )
  # print('  area sum = '+str(np.sum(ds_grid['grid_area'].values)) )

# exit()

#-------------------------------------------------------------------------------
# Set up workstation
#-------------------------------------------------------------------------------
wkres = ngl.Resources()
# npix = 1024*2; wkres.wkWidth,wkres.wkHeight=npix,npix
npix = 4096; wkres.wkWidth,wkres.wkHeight=npix,npix
wkres.wkBackgroundColor = 'black'
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
res.tmXBOn,res.tmYLOn  = False,False

res.cnFillOn                     = True
res.cnLinesOn                    = False
res.cnLineLabelsOn               = False
res.cnInfoLabelOn                = False
res.lbOrientation                = "Horizontal"
res.lbLabelFontHeightF           = 0.008
res.mpGridAndLimbOn              = False


res.cnFillMode      = 'CellFill'
res.cnCellFillEdgeColor = "black"

res.lbLabelBarOn = False
res.cnFillPalette   = "OceanLakeLandSnow"
res.cnLevelSelectionMode = "ExplicitLevels"
res.cnLevels = np.arange(0,4800+100,100)

### use this for no topo data
res.cnFillPalette   = "CBR_wet"

# res.mpCenterLonF          = 180

# res.mpProjection          = "Satellite"
res.mpProjection          = "Orthographic"
# res.mpCenterLonF          = 180-20
res.mpCenterLonF          = -20
# res.mpCenterLatF          = 40
res.mpOutlineBoundarySets = "NoBoundaries"
res.mpGridAndLimbOn       = False
res.mpPerimOn             = False
# res.pmTickMarkDisplayMode = "Never"

# res.mpGeophysicalLineColor = 'red'
# res.mpGeophysicalLineThicknessF = 6


### turn off color fill
# res.cnFillOpacityF = 0.0

res.mpLimitMode     = 'LatLon'


lres = ngl.Resources()
lres.gsLineColor       = "red" 
lres.gsLineThicknessF  = 10.0
lres.gsLineDashPattern = 1

# mres = ngl.Resources()
# res.nglDraw,res.nglFrame = False,False
# mres.xyMarkLineMode      = 'Markers'
# mres.xyMarkerSizeF       = 0.005
# mres.xyMarker            = 16

pmres  = ngl.Resources()
pmres.gsMarkerSizeF       = 0.002
pmres.gsMarkerColor       = 'red'
pmres.gsMarkerIndex       = 16
# pmres.gsMarkerThicknessF  = 2

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def get_adjusted_grid_corners(ds_grid):
  # straighten out the lines around the poles to avoid the clover thing
  ncol = len(ds_grid['grid_center_lon'].values)
  xbound = np.zeros([ncol,5])
  ybound = np.zeros([ncol,5])
  xbound[:,:4] = ds_grid['grid_corner_lon'].values
  ybound[:,:4] = ds_grid['grid_corner_lat'].values
  ncol = len(ds_grid['grid_center_lon'].values)
  dummy = [None]*ncol
  for i in range(ncol):
    if 90 in ybound[i,:] or -90 in ybound[i,:]:
      tmp_x = xbound[i,:4]
      tmp_y = ybound[i,:4]
      for ind,lat in enumerate(tmp_y):
        if np.abs(lat)==90:
          tmp_x[ind] = tmp_x[(ind+4+1)%4]
          tmp_x = np.insert(tmp_x, ind, tmp_x[(ind+4-1)%4])
        if lat== 90: tmp_y = np.insert(tmp_y, ind, 90)
        if lat==-90: tmp_y = np.insert(tmp_y, ind,-90)
      xbound[i,:] = tmp_x[:]
      ybound[i,:] = tmp_y[:]
    else:
      xbound[i,-1] = xbound[i,0]
      ybound[i,-1] = ybound[i,0]
  return (xbound,ybound)

deg_to_rad = np.pi/180.
rad_to_deg = 180./np.pi

# @numba.njit
def calc_great_circle_distance(lat1,lat2,lon1,lon2):
   ''' input should be in degrees '''
   dlon = lon2 - lon1
   cos_dist = np.sin(lat1*deg_to_rad)*np.sin(lat2*deg_to_rad) + \
              np.cos(lat1*deg_to_rad)*np.cos(lat2*deg_to_rad)*np.cos(dlon*deg_to_rad)
   cos_dist = np.where(cos_dist> 1.0, 1.0,cos_dist)
   cos_dist = np.where(cos_dist<-1.0,-1.0,cos_dist)
   dist = np.arccos( cos_dist )
   return dist

# @numba.njit()
def align_pg_corners(xbound,ybound,gll_clon,gll_clat):
  npgc = len(xbound[:,0])
  ngll = len(gll_clon)
  dist = np.zeros(ngll)
  for i in range(npgc):
    for c in range(5):
      if abs(ybound[i,c])!=90:
        for ii in range(ngll):
          dist[ii] = calc_great_circle_distance( ybound[i,c], gll_clat[ii], xbound[i,c], gll_clon[ii])
        # identify index of minimum distance and use this to adjust pg2 corners
        min_ind = np.argsort(dist[:])[0]
        ybound[i,c] = gll_clat[min_ind]
        xbound[i,c] = gll_clon[min_ind]
  return


#-------------------------------------------------------------------------------
# Load data and create plot
#-------------------------------------------------------------------------------
# for f,(grid_file,topo_file) in enumerate( zip(grid_file_list,topo_file_list) ):
topo_file = None
for f,grid_file in enumerate( grid_file_list ):

  ds_grid = xr.open_dataset(grid_file)

  if topo_file is not None:
    ds_topo = xr.open_dataset(topo_file)
    if 'PHIS' in ds_topo.variables:
      topo = ds_topo['PHIS'].values
      topo = topo / 9.81
    else:
      topo = ds_topo['terr'].values
    land = ds_topo['LANDFRAC'].values
    topo = np.where(land>0.5,topo,-1e3)
  else:
    topo = ds_grid['grid_area'].values

  (xbound,ybound) = get_adjusted_grid_corners(ds_grid)

  if 'ne2pg2' in grid_file:
    ds_np4 = xr.open_dataset(f'{home}/E3SM/inputdata/grids/ne4np4-pentagons_c100308.nc')
    gll_clon = ds_np4['grid_center_lon'].values
    gll_clat = ds_np4['grid_center_lat'].values
    align_pg_corners(xbound,ybound,gll_clon,gll_clat)


  tres = copy.deepcopy(res)
  tres.sfXArray      = ds_grid['grid_center_lon'].values
  tres.sfYArray      = ds_grid['grid_center_lat'].values
  tres.sfXCellBounds = xbound#ds_grid['grid_corner_lon'].values
  tres.sfYCellBounds = ybound#ds_grid['grid_corner_lat'].values

  # res.tiXAxisString = 'normalized level index'
  # res.tiYAxisString = 'lev [mb]'

  plot.append( ngl.contour_map(wks, topo, tres) )

  # hs.set_subtitles(wks, plot[len(plot)-1], '', name[f], '', font_height=0.02)

  #-----------------------------------------------------------------------------
  if 'ne2pg2' in grid_file:
    # ds_np4 = xr.open_dataset(f'{home}/E3SM/inputdata/grids/ne4np4-pentagons_c100308.nc')
    # gll_clon = ds_np4['grid_center_lon'].values
    # gll_clat = ds_np4['grid_center_lat'].values
    ngl.add_polymarker(wks, plot[len(plot)-1], gll_clon, gll_clat, pmres)

  # # the two grids don't line up... so this doens't work
  # if 'ne4pg2' in grid_file:
  #   ds_elem = xr.open_dataset(f'{home}/E3SM/data_grid/ne2pg2_scrip.nc')
  #   (elem_clon,elem_clat) = get_adjusted_grid_corners(ds_elem)
  #   ncol = len(elem_clat); dummy = [None]*ncol
  #   for i in range(ncol):
  #     dummy[i] = ngl.add_polyline(wks,plot[len(plot)-1],elem_clon[i,:],elem_clat[i,:],lres)
  #-----------------------------------------------------------------------------
  # plot individual grid lines

  # xbound = ds_grid['grid_corner_lon'].values
  # ybound = ds_grid['grid_corner_lat'].values
  # ncol = len(ds_grid['grid_center_lon'].values)
  # dummy = [None]*ncol
  # for i in range(ncol):
  #   for y,lat in enumerate(ybound[i,:]):
  #     if lat==90: 
  #       print()
  #       print(f'{xbound[i,:]}    {ybound[i,:]}')
  #       xbound[i,y] = xbound[i,(y+4-1)%4]
  #       print()
  #       print(f'{xbound[i,:]}    {ybound[i,:]}')
  #       print()
  #   xtmp,ytmp = [],[]
  #   for n in range(5): xtmp.append(xbound[i,(n+1)%4]); ytmp.append(ybound[i,(n+1)%4])
  #   # dummy[i] = ngl.add_polyline(wks,plot[0],xbound[i,:],ybound[i,:],lres)
  #   dummy[i] = ngl.add_polyline(wks,plot[0],np.array(xtmp),np.array(ytmp),lres)

  # xbound = ds_grid['grid_corner_lon'].values
  # ybound = ds_grid['grid_corner_lat'].values
  # ncol = len(ds_grid['grid_center_lon'].values)
  # dummy = [None]*ncol
  # for i in range(ncol):
  #   xtmp,ytmp = [],[]
  #   for n in range(4):
  #     x1,x2 = xbound[i,n],xbound[i,(n+1)%4]
  #     y1,y2 = ybound[i,n],ybound[i,(n+1)%4]
  #     # add first point of segment
  #     xtmp.append(x1)
  #     ytmp.append(y1)
  #     # add mid point
  #     # Bx = np.cos(np.deg2rad(y2)) * np.cos(np.deg2rad(x2-x1))
  #     # By = np.cos(np.deg2rad(y2)) * np.sin(np.deg2rad(x2-x1))
  #     # a1 = np.sin(np.deg2rad(y1)) + np.sin(np.deg2rad(y2))
  #     # a2 = np.sqrt( (np.cos(np.deg2rad(y1))+Bx)*(np.cos(np.deg2rad(y1))+Bx) + By*By )
  #     # ymid = np.arctan2( a1, a2 );
  #     # xmid = x1 + np.arctan2(By, np.cos(y1) + Bx);
  #     # xtmp.append(xmid); ytmp.append(ymid)
  #     # add last point
  #     xtmp.append(x1); ytmp.append(y1)      
  #   dummy[i] = ngl.add_polyline(wks,plot[0],np.array(xtmp),np.array(ytmp),lres)
    
#-------------------------------------------------------------------------------
# Finalize plot
#-------------------------------------------------------------------------------
pres = ngl.Resources()
# pres.nglPanelLabelBar = True
# nglPanelLabelBarLabelFontHeightF
# pres.nglPanelFigureStrings            = ['a','b','c','d','e','f','g','h']
# pres.nglPanelFigureStringsJust        = "TopLeft"
# pres.nglPanelFigureStringsFontHeightF = 0.015
# pres.nglPanelYWhiteSpacePercent = 10    
pres.nglPanelXWhiteSpacePercent = 5

layout = [1,len(plot)]
# layout = layout = [2,np.ceil(len(plot)/2)]
ngl.panel(wks,plot,layout,pres); ngl.end()

# trim white space
fig_file = f'{fig_file}.{fig_type}'
os.system(f'convert -trim +repage {fig_file}   {fig_file}')
fig_file = fig_file.replace(os.getenv('HOME')+'/E3SM/','')
print(f'\n{fig_file}\n')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
