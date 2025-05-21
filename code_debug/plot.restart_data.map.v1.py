import os, ngl, copy, xarray as xr, numpy as np

### case name for plot title
case_name = 'E3SM'

### full path of input file
scratch_dir = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch'
# case,date = 'E3SM.INCITE2021-CMT.GNUGPU.ne45pg2_r05_oECv3.F-MMFXX.NXY_32x32.BVT.MOMFB.01','0001-02-02'
case,date = 'E3SM.INCITE2021-HC.HC.GNUGPU.ne45pg2_r05_oECv3.F-MMFXX.NXY_32x32.DX_200.L_125_115.DT_5e-1.BVT.2008-10-01','2008-10-02'
input_file_path = f'{scratch_dir}/{case}/run/{case}.eam.r.{date}-00000.nc'

### scrip file for native grid plot
scrip_file_name = '/global/homes/w/whannah/E3SM/data_grid/ne30pg2_scrip.nc'

### list of variables to plot
# var = ['U']
var = ['dpVT_T']

### output figure type and name
fig_file,fig_type = 'restart_data.map.v1','png'

### uncomment to plot a regional subset
# lat1,lat2 = -40,40
# lat1,lat2,lon1,lon2 = 0,40,360-160,360-80     # East Pac

#---------------------------------------------------------------------------------------------------
# Set up plot resources
#---------------------------------------------------------------------------------------------------
num_var = len(var)

### create the plot workstation
wks = ngl.open_wks(fig_type,fig_file)
plot = []

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

if 'lat1' in vars() : res.mpMinLatF = lat1
if 'lat2' in vars() : res.mpMaxLatF = lat2
if 'lon1' in vars() : res.mpMinLonF = lon1
if 'lon2' in vars() : res.mpMaxLonF = lon2

#---------------------------------------------------------------------------------------------------
# method for plotting statistics
#---------------------------------------------------------------------------------------------------
def print_stat(x,name='(no name)',unit='',fmt='f',stat='naxh',indent='',compact=False):
   """ Print min, avg, max, and std deviation of input """
   if fmt=='f' : fmt = '%.6f'
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
   if compact: msg += line#+'\n'
   print(msg)
   return msg
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
   #----------------------------------------------------------------------------
   # read the data
   #----------------------------------------------------------------------------
   ds = xr.open_dataset( input_file_path )
   data = ds[var[v]]

   ### print stats before time averaging
   print_stat(data,name=var[v],stat='naxsh',indent='    ')
   exit()

   ### Calculate time mean
   if 'time' in data.dims: data = data.mean(dim='time')

   ### adjust units
   if var[v] in ['PRECT','PRECC','PRECL'] : data = data*86400.*1e3

   #----------------------------------------------------------------------------
   # Set colors and contour levels
   #----------------------------------------------------------------------------
   tres = copy.deepcopy(res)
   ### use a perceptually uniform colormap
   tres.cnFillPalette = "MPL_viridis"

   ### specify specific contour intervals
   if var[v] in ['PRECT','PRECC']   : tres.cnLevels = np.arange(1,20+1,1)
   if var[v]=='LHFLX'               : tres.cnLevels = np.arange(5,205+5,5)
   if var[v]=="TGCLDLWP"            : tres.cnLevels = np.logspace( -2,-0.2, num=60).round(decimals=2) # better for non-MMF

   if hasattr(tres,'cnLevels') : tres.cnLevelSelectionMode = 'ExplicitLevels'
   #----------------------------------------------------------------------------
   # Set up cell fill attributes using scrip grid file
   #----------------------------------------------------------------------------
   scripfile = xr.open_dataset(scrip_file_name)
   tres.cnFillMode    = 'CellFill'
   tres.sfXArray      = scripfile['grid_center_lon'].rename({'grid_size':'ncol'}).values
   tres.sfYArray      = scripfile['grid_center_lat'].rename({'grid_size':'ncol'}).values
   tres.sfXCellBounds = scripfile['grid_corner_lon'].rename({'grid_size':'ncol'}).values
   tres.sfYCellBounds = scripfile['grid_corner_lat'].rename({'grid_size':'ncol'}).values
   
   #----------------------------------------------------------------------------
   # Create plot
   #----------------------------------------------------------------------------
   plot.append( ngl.contour_map(wks,data.values,tres) )
   set_subtitles(wks, plot[len(plot)-1], case_name, '', var[v], font_height=0.01)

#---------------------------------------------------------------------------------------------------
# Finalize plot
#---------------------------------------------------------------------------------------------------
pres = ngl.Resources()
pres.nglPanelYWhiteSpacePercent = 5
pres.nglPanelXWhiteSpacePercent = 5

layout = [len(plot),1]

ngl.panel(wks,plot[0:len(plot)],layout,pres)
ngl.end()

### trim white space from image using imagemagik
if fig_type == 'png' :
   fig_file = fig_file+'.png'
   os.system( 'convert -trim +repage '+fig_file+'   '+fig_file )
   print('\n'+fig_file+'\n')

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------