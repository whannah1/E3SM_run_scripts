import os, numpy as np, xarray as xr, ngl, copy
import hapy_setres as hs
import hapy_common as hc
home = os.getenv('HOME')

grid_file_list,topo_file_list,name = [],[],[]
scratch_dir = '/global/cfs/cdirs/e3sm/inputdata'
# scratch_dir = '/gpfs/alpine/cli115/scratch/hannah6/inputdata'
topo_dir = f'{scratch_dir}/atm/cam/topo'

grid_file_list.append('/global/cfs/cdirs/e3sm/inputdata/ocn/mpas-o/EC30to60E2r2/EC30to60E2r2.scrip.201005.nc')
name.append('EC30to60E2r2')

# grid_file_list.append(f'{home}/E3SM/data_grid/ne4np4_scrip.nc');      name.append('ne4np4')
# grid_file_list.append(f'{home}/E3SM/data_grid/ne4pg2_scrip.nc');      name.append('ne4pg2')
# topo_file_list.append(f'{topo_dir}/USGS-gtopo30_ne4pg2_16xdel2-PFC-consistentSGH.c20190618.nc')
# topo_file_list.append(None)

# grid_file_list.append(f'{home}/E3SM/data_grid/ne30np4_scrip.nc');      name.append('ne30np4')
# grid_file_list.append(f'{home}/E3SM/data_grid/ne30pg2_scrip.nc');      name.append('ne30pg2'); 
# topo_file_list.append(f'{topo_dir}/USGS-gtopo30_ne30np4pg2_16xdel2.nc')
# topo_file_list.append('/global/cfs/cdirs/e3sm/inputdata/atm/cam/topo/USGS-gtopo30_ne30pg2_16xdel2-PFC-consistentSGH.c20190417.nc')
# grid_file_list.append(f'{home}/E3SM/data_grid/ne30pg3_scrip.nc');      name.append('ne30pg3')
# grid_file_list.append(f'{home}/E3SM/data_grid/ne30pg4_scrip.nc');      name.append('ne30pg4')

# grid_file_list.append(f'{home}/E3SM/data_grid/ne30pg2_scrip.nc');      name.append('ne30pg2')
# grid_file_list.append(f'{home}/E3SM/data_grid/conusx4v1pg2_scrip.nc'); name.append('RRM pg2')

# grid_file_list.append(f'{home}/E3SM/data_grid/ne30pg2_scrip.nc');      name.append('ne30pg2')
# grid_file_list.append(f'{home}/E3SM/data_grid/ne120pg2_scrip.nc');     name.append('ne120pg2')

# grid_file_list.append(f'{home}/E3SM/data_grid/ne0_R30x30_tropicsx4pg2_scrip.nc'); name.append('RRM tropicsx4pg2')
# grid_file_list.append(f'{home}/squadgen/RRM_cubefacex2pg2_scrip.nc'); name.append('RRM cubefacex2pg2')
# grid_file_list.append(f'{home}/squadgen/RRM_cubefacex3pg2_scrip.nc'); name.append('RRM cubefacex3pg2')

# grid_file_list.append(f'{home}/squadgen/RRM_cubeface_gradient_pg2_scrip.nc'); name.append('cubeface_gradient ne30x3') ; topo_file_list.append(None)# ne30x3
# grid_file_list.append(f'{home}/squadgen/RRM_cubeface_gradient_ne4x6_pg2_scrip.nc'); name.append('cubeface_gradient ne4x6')
# grid_file_list.append(f'{home}/squadgen/RRM_cubeface_gradient_ne4x5_pg2_scrip.nc'); name.append('cubeface_gradient ne4x5')

# grid_file_list.append(f'{home}/squadgen/RRM_3xfacex2pg2_scrip.nc'); name.append('3xfacex2pg2')

# grid_file_list.append(f'{home}/squadgen/RRM_cubeface_ne16x3_pg2_scrip.nc'); name.append('cubeface_ne16x3_pg2')
# grid_file_list.append(f'{home}/squadgen/RRM_cubeface_blur_ne16x3_pg2_scrip.nc'); name.append('cubeface_blur_ne16x3_pg2')

# grid_file_list.append(f'{home}/squadgen/RRM_cubeface_gradient_zonal_ne16x3_pg2_scrip.nc'); name.append('cubeface_gradient_zonal_ne16x3_pg2')


# grid_file_list.append(f'{home}/squadgen/RRM_1xland_ne30.nsmooth_0_pg2_scrip.nc'); name.append('RRM_1xland')
# grid_file_list.append(f'{home}/squadgen/RRM_1xland_ne30.nsmooth_2_pg2_scrip.nc'); name.append('RRM_1xland')


#data_path = '/pscratch/sd/w/whannah/e3sm_scratch/perlmutter/ECRP-data'
#name.append('Seattle'); grid_file_list.append(f'{data_path}/ECRP_RRM_v0_seattle_pg2_scrip.nc'); topo_file_list.append(f'{data_path}/ECRP_RRM_v0_seattle_pg2_topo.nc')

# grid_file_list.append(f'{home}/squadgen/'); name.append('3xfacex2pg2')
# grid_file_list.append(f'{home}/squadgen/'); name.append('3xfacex2pg2')
# grid_file_list.append(f'{home}/squadgen/'); name.append('3xfacex2pg2')
# grid_file_list.append(f'{home}/squadgen/'); name.append('3xfacex2pg2')
# grid_file_list.append(f'{home}/squadgen/'); name.append('3xfacex2pg2')

# data_root = '/p/lustre1/hannah6/2024-nimbus-iraq-data/'
# grid_file_list.append(f'{data_root}/files_grid/2024-nimbus-iraq-32x3_pg2_scrip.nc' ); name.append('32x3') ;topo_file_list.append(f'{data_root}/files_topo/USGS-topo_2024-nimbus-iraq-32x3-np4_smoothedx6t_20240618.nc')
# grid_file_list.append(f'{data_root}/files_grid/2024-nimbus-iraq-64x3_pg2_scrip.nc' ); name.append('64x3') ;topo_file_list.append(f'{data_root}/files_topo/USGS-topo_2024-nimbus-iraq-64x3-np4_smoothedx6t_20240618.nc')
# grid_file_list.append(f'{data_root}/files_grid/2024-nimbus-iraq-128x3_pg2_scrip.nc'); name.append('128x3');topo_file_list.append(f'{data_root}/files_topo/USGS-topo_2024-nimbus-iraq-128x3-np4_smoothedx6t_20240618.nc')



# for grid in grid_file_list:
#     found = False
#     if 'ne120np4' in grid: found=True;topo_file_list.append(f'{topo_dir}/USGS-gtopo30_ne120np4_16xdel2-PFC-consistentSGH.nc')
#     if 'ne120pg2' in grid: found=True;topo_file_list.append(f'{topo_dir}/USGS-gtopo30_ne120np4pg2_16xdel2.nc')
#     if 'ne30np4'  in grid: found=True;topo_file_list.append(f'{topo_dir}/USGS-gtopo30_ne30np4_16xdel2-PFC-consistentSGH.nc')
#     if 'ne30pg2'  in grid: found=True;topo_file_list.append(f'{topo_dir}/USGS-gtopo30_ne30np4pg2_16xdel2.c20200108.nc')
#     if 'ne30pg3'  in grid: found=True;topo_file_list.append(f'{topo_dir}/USGS-gtopo30_ne30np4pg3_16xdel2.c20200504.nc')
#     if 'ne30pg4'  in grid: found=True;topo_file_list.append(f'{topo_dir}/USGS-gtopo30_ne30np4pg4_16xdel2.c20200504.nc')
#     if 'x4v1_'    in grid: found=True;topo_file_list.append(f'{topo_dir}/USGS_conusx4v1-tensor12x_consistentSGH_c150924.nc')
#     if 'x4v1pg2_' in grid: found=True;topo_file_list.append(f'{topo_dir}/USGS_conusx4v1pg2_12x_consistentSGH_20200609.nc')
#     if not found:topo_file_list.append(None)

fig_type = 'png'
fig_file = os.getenv('HOME')+'/E3SM/figs_grid/grid.scrip.v1'

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
npix = 1024; wkres.wkWidth,wkres.wkHeight=npix,npix
# npix = 4096; wkres.wkWidth,wkres.wkHeight=npix,npix
wks = ngl.open_wks(fig_type,fig_file,wkres)
plot = []
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
res.mpGridAndLimbOn              = False


res.cnFillMode      = 'CellFill'
# res.cnCellFillEdgeColor = "black"

res.lbLabelBarOn = False
res.cnFillPalette   = "OceanLakeLandSnow"
res.cnLevelSelectionMode = "ExplicitLevels"
# res.cnLevels = np.arange(0,4800+100,100)
res.cnLevels = np.arange(5,4805+105,105)

### use this for no topo data
#res.cnFillPalette   = "CBR_wet"

# res.mpCenterLonF          = 180
res.mpCenterLonF          = 30

# res.mpProjection = 'Robinson'
# res.mpProjection          = "Satellite"
res.mpProjection          = "Orthographic"
#res.mpCenterLonF          = -20
#res.mpCenterLatF          = 40
res.mpOutlineBoundarySets = 'NoBoundaries'
res.mpGridAndLimbOn       = False
res.mpPerimOn             = False
# res.pmTickMarkDisplayMode = "Never"

# res.mpGeophysicalLineColor = 'red'
res.mpGeophysicalLineThicknessF = 6


### turn off color fill
# res.cnFillOpacityF = 0.0

res.mpLimitMode     = 'LatLon'

### for aqua RRM
# res.mpMinLatF,res.mpMaxLatF      =  -40, 40
# res.mpMinLonF,res.mpMaxLonF      =  -90, 90

# CONUS
# res.mpMinLatF,res.mpMaxLatF      =  12, 50
# res.mpMinLonF,res.mpMaxLonF      =  360-130, 360-60

# # zoomed-out CONUS
# res.mpMinLatF,res.mpMaxLatF      =  10, 72
# res.mpMinLonF,res.mpMaxLonF      =  360-160, 360-42
# res.cnLevels = np.arange(0,3000+100,100)

# # zoomed-in CONUS
# res.mpMinLatF,res.mpMaxLatF      =  25, 50
# res.mpMinLonF,res.mpMaxLonF      =  360-125, 360-75
# res.cnLevels = np.arange(0,2500+100,100)

# # Florida
# res.mpMinLatF,res.mpMaxLatF      =  12, 32
# res.mpMinLonF,res.mpMaxLonF      =  360-105, 360-75

# # West CONUS
# res.mpMinLatF,res.mpMaxLatF      =  30, 60
# res.mpMinLonF,res.mpMaxLonF      =  360-150, 360-100

# # Andes
# res.mpMinLatF,res.mpMaxLatF      =  -30, 15
# res.mpMinLonF,res.mpMaxLonF      =  360-90, 360-40

# # Himalayas
# res.mpMinLatF,res.mpMaxLatF      =  5, 45
# res.mpMinLonF,res.mpMaxLonF      =  60, 130
# res.cnLevels = np.arange(0,5000+100,100)


# Arabian Penninsula
res.mpMinLatF,res.mpMaxLatF      =  0, 60
res.mpMinLonF,res.mpMaxLonF      =  0, 90




#-------------------------------------------------------------------------------
# Load data and create plot
#-------------------------------------------------------------------------------
for f,(grid_file,topo_file) in enumerate( zip(grid_file_list,topo_file_list) ):

  ds_grid = xr.open_dataset(grid_file)

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
    ### use the line below to make it all blue 
    # topo = np.random.normal(loc=-1, scale=0.01, size=len( ds_grid['grid_area'].values ))

  tres = copy.deepcopy(res)
  fac = 1.
  if np.max(ds_grid['grid_center_lat'].values)<4: fac = 180./np.pi
  tres.sfXArray      = ds_grid['grid_center_lon'].values * fac
  tres.sfYArray      = ds_grid['grid_center_lat'].values * fac
  tres.sfXCellBounds = ds_grid['grid_corner_lon'].values * fac
  tres.sfYCellBounds = ds_grid['grid_corner_lat'].values * fac

  if topo_file is None:
    tres.cnLevelSelectionMode = "AutomaticLevels"
    tres.cnFillPalette   = "CBR_wet"

  # res.tiXAxisString = 'normalized level index'
  # res.tiYAxisString = 'lev [mb]'

  plot.append( ngl.contour_map(wks, topo, tres) )

  # hs.set_subtitles(wks, plot[len(plot)-1], '', name[f], '', font_height=0.02)
  
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
# pres.nglPanelXWhiteSpacePercent = 5

layout = [len(plot),1]
# layout = layout = [2,np.ceil(len(plot)/2)]
ngl.panel(wks,plot,layout,pres); ngl.end()

# trim white space
fig_file = f'{fig_file}.{fig_type}'
os.system(f'convert -trim +repage {fig_file}   {fig_file}')
fig_file = fig_file.replace(os.getenv('HOME')+'/E3SM/','')
print(f'\n{fig_file}\n')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
