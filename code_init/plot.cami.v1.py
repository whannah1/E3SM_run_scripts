import os
import ngl
import copy
import xarray as xr
import numpy as np

input_data = '/global/cfs/cdirs/e3sm/inputdata/atm/cam/inic/homme'

### full path of input file
input_files = [
              f'{input_data}/cami_mam3_Linoz_ne30np4_L72_c160214.nc',
              f'/global/cscratch1/sd/whannah/HICCUP/data/HICCUP.cami_mam3_Linoz_ne30np4.L72_alt.nc',
              # f'{input_data}/cami_mam3_Linoz_ne45np4_L72_c20200611.nc',
              ]

grid_name = [None]*len(input_files)
scrip_file = [None]*len(input_files)
for i,file in enumerate(input_files):
   if 'ne30np4' in file : grid_name[i] = 'ne30np4'
   if grid_name[i] is not None: scrip_file[i] = os.getenv('HOME')+f'/E3SM/data_grid/{grid_name[i]}_scrip.nc'

### list of variables to plot
# var = ['PS']
var = ['T']

### output figure type and name
fig_type = 'png'
fig_file = 'cami.v1'

### uncomment to plot a regional subset
# lat1,lat2,lon1,lon2 = 0,40,360-160,360-80     # East Pac

#---------------------------------------------------------------------------------------------------
# Set up plot resources
#---------------------------------------------------------------------------------------------------
if any(s is None for s in scrip_file): 
   print(scrip_file)
   exit('ERROR: scrip_file cannot be None')

num_var = len(var)
num_file = len(input_files)

### create the plot workstation
wks = ngl.open_wks(fig_type,fig_file)
plot = [None]*(num_var*num_file)

### set oup the plot resources
res = ngl.Resources()
res.nglDraw                      = False
res.nglFrame                     = False
res.tmXTOn                       = False
res.tmXBMajorOutwardLengthF      = 0.
res.tmXBMinorOutwardLengthF      = 0.
res.tmYLMajorOutwardLengthF      = 0.
res.tmYLMinorOutwardLengthF      = 0.
res.tmYLLabelFontHeightF         = 0.015
res.tmXBLabelFontHeightF         = 0.015
res.tiXAxisFontHeightF           = 0.015
res.tiYAxisFontHeightF           = 0.015
res.tmXBMinorOn                  = False
res.tmYLMinorOn                  = False
res.tmYLLabelFontHeightF         = 0.008
res.tmXBLabelFontHeightF         = 0.008
res.lbLabelFontHeightF           = 0.012
res.cnFillOn                     = True
res.cnLinesOn                    = False
res.cnLineLabelsOn               = False
res.cnInfoLabelOn                = False
res.lbOrientation                = "Horizontal"
res.lbLabelFontHeightF           = 0.008
res.mpGridAndLimbOn              = False
res.mpCenterLonF                 = 180
res.mpLimitMode                  = "LatLon" 
# if 'lat1' in vars() : res.mpMinLatF = lat1
# if 'lat2' in vars() : res.mpMaxLatF = lat2
# if 'lon1' in vars() : res.mpMinLonF = lon1
# if 'lon2' in vars() : res.mpMaxLonF = lon2

#---------------------------------------------------------------------------------------------------
# define function to add subtitles to the top of plot
#---------------------------------------------------------------------------------------------------
def set_subtitles(wks, plot, left_string='', center_string='', right_string='', font_height=0.01):
   ttres         = ngl.Resources()
   ttres.nglDraw = False

   ### Use plot extent to call ngl.text(), otherwise you will see this error: 
   ### GKS ERROR NUMBER   51 ISSUED FROM SUBROUTINE GSVP  : --RECTANGLE DEFINITION IS INVALID
   strx = ngl.get_float(plot,'trXMinF')
   stry = ngl.get_float(plot,'trYMinF')
   ttres.txFontHeightF = font_height

   ### Set annotation resources to describe how close text is to be attached to plot
   amres = ngl.Resources()
   if not hasattr(ttres,'amOrthogonalPosF'):
      amres.amOrthogonalPosF = -0.52   # Top of plot plus a little extra to stay off the border
   else:
      amres.amOrthogonalPosF = ttres.amOrthogonalPosF

   ### Add left string
   amres.amJust,amres.amParallelPosF = 'BottomLeft', -0.5   # Left-justified
   tx_id_l   = ngl.text(wks, plot, left_string, strx, stry, ttres)
   anno_id_l = ngl.add_annotation(plot, tx_id_l, amres)
   # Add center string
   amres.amJust,amres.amParallelPosF = 'BottomCenter', 0.0   # Centered
   tx_id_c   = ngl.text(wks, plot, center_string, strx, stry, ttres)
   anno_id_c = ngl.add_annotation(plot, tx_id_c, amres)
   # Add right string
   amres.amJust,amres.amParallelPosF = 'BottomRight', 0.5   # Right-justified
   tx_id_r   = ngl.text(wks, plot, right_string, strx, stry, ttres)
   anno_id_r = ngl.add_annotation(plot, tx_id_r, amres)

   return
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
for v in range(num_var):
   print('  var: '+var[v])
   for i in range(len(input_files)):
      print('    input_file: '+input_files[i])
      #----------------------------------------------------------------------------
      # read the data
      #----------------------------------------------------------------------------
      ds = xr.open_dataset( input_files[i] )

      print(ds.keys())
      exit()

      # ncol = ds['ncol']
      # mask = xr.DataArray( np.ones([len(ncol)],dtype=bool), coords=[('ncol', ncol)], dims='ncol' )
      # if 'lat1' in vars(): mask = mask & (ds['lat']>=lat1)
      # if 'lat2' in vars(): mask = mask & (ds['lat']<=lat2)
      # if 'lon1' in vars(): mask = mask & (ds['lon']>=lon1)
      # if 'lon2' in vars(): mask = mask & (ds['lon']<=lon2)
      # data = ds[var[v]].isel(time=time_slice).where(mask,drop=True)

      data = ds[var[v]]
      ### Calculate time mean
      if 'time' in data.dims : data = data.isel(time=0)

      nan_flag = np.isnan(data.values)
      print(nan_flag)
      if np.any(nan_flag):
         print(np.sum(nan_flag))
      else:
         print(f'no NaNs...?')
      exit()

      if 'lev' in data.dims : data = data.isel(lev=-1)

      ### Calculate area-weighted global mean
      # area = ds['area'].where( mask,drop=True)
      # gbl_mean = ( (data*area).sum() / area.sum() ).values 
      # print('\n      Area Weighted Global Mean : '+'%f'%gbl_mean+'\n')

      #----------------------------------------------------------------------------
      # Set colors and contour levels
      #----------------------------------------------------------------------------
      tres = copy.deepcopy(res)
      if i==0:
         cmin,cmax,cint,clev = ngl.nice_cntr_levels(data.min().values, data.max().values,       \
                                                    cint=None, max_steps=21,              \
                                                    returnLevels=True, aboutZero=False )
         clev = np.linspace(cmin,cmax,num=21)
      
      tres.cnLevels = clev
      #----------------------------------------------------------------------------
      # Set up cell fill attributes using scrip grid file
      #----------------------------------------------------------------------------
      ds_scrip = xr.open_dataset(scrip_file[i])
      print(ds_scrip)
      tres.cnFillMode    = 'CellFill'
      tres.sfXArray      = ds_scrip['grid_center_lon'].rename({'grid_size':'ncol'}).values
      tres.sfYArray      = ds_scrip['grid_center_lat'].rename({'grid_size':'ncol'}).values
      tres.sfXCellBounds = ds_scrip['grid_corner_lon'].rename({'grid_size':'ncol'}).values 
      tres.sfYCellBounds = ds_scrip['grid_corner_lat'].rename({'grid_size':'ncol'}).values
      
      #----------------------------------------------------------------------------
      # Create plot
      #----------------------------------------------------------------------------
      ip = i*num_var+v
      plot[ip] = ngl.contour_map(wks,data.values,tres) 
      set_subtitles(wks, plot[ip], grid_name[i], '', var[v], font_height=0.01)

#---------------------------------------------------------------------------------------------------
# Finalize plot
#---------------------------------------------------------------------------------------------------
pres = ngl.Resources()
pres.nglPanelYWhiteSpacePercent = 5
pres.nglPanelXWhiteSpacePercent = 5
layout = [num_file,num_var]
ngl.panel(wks,plot[0:len(plot)],layout,pres)
ngl.end()

### trim white space from image using imagemagik
if fig_type == 'png' :
   fig_file = fig_file+'.png'
   os.system( 'convert -trim +repage '+fig_file+'   '+fig_file )
   print('\n'+fig_file+'\n')

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
