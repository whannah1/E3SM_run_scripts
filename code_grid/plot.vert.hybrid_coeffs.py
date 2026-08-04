import os, numpy as np, xarray as xr, ngl
import hapy_common as hc
home = os.getenv('HOME')

vert_file_list,name,clr = [],[],[]

# vert_file_list.append(f'{home}/E3SM/vert_grid_files/L60.nc');     clr.append('green');name.append('L60')
vert_file_list.append(f'{home}/E3SM/vert_grid_files/L72_E3SM.nc');clr.append('black');name.append('L72 E3SM')
# vert_file_list.append(f'{home}/E3SM/vert_grid_files/L50_v2.nc');  clr.append('red');  name.append('L50')

# vert_file_list.append(f'{home}/E3SM/vert_grid_files/L20_test.nc');clr.append('pink');  name.append('L20')
# vert_file_list.append(f'{home}/E3SM/vert_grid_files/L30_test.nc');clr.append('purple');  name.append('L30')
# vert_file_list.append(f'{home}/E3SM/vert_grid_files/L40_test.nc');clr.append('cyan');  name.append('L40')

# vert_file_list.append(f'{home}/E3SM/vert_grid_files/L72_E3SM_pm400.nc'); clr.append('red');   name.append('L72 pm400')
# vert_file_list.append(f'{home}/E3SM/vert_grid_files/L72_E3SM_pm200.nc'); clr.append('green'); name.append('L72 pm200')
# vert_file_list.append(f'{home}/E3SM/vert_grid_files/L72_E3SM_pm100.nc'); clr.append('blue');  name.append('L72 pm100')
# vert_file_list.append(f'{home}/E3SM/vert_grid_files/L72_E3SM_pm50.nc') ; clr.append('purple');name.append('L72 pm50')


fig_type = 'png'
fig_file = os.getenv('HOME')+'/E3SM/figs_grid/vertical_hybrid_coeffs'


#-------------------------------------------------------------------------------
# Set up workstation
#-------------------------------------------------------------------------------
wks = ngl.open_wks(fig_type,fig_file)
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
res.xyLineThicknessF             = 6.

res.xyMarkLineMode = 'MarkLines'
res.xyMarkerSizeF = 0.005
res.xyMarker = 16

# res.xyYStyle = "Log"


#-------------------------------------------------------------------------------
# Load data and create plot
#-------------------------------------------------------------------------------
for f,vert_file in enumerate(vert_file_list):

  ds = xr.open_dataset(vert_file)

  hya = ds['hyai'].values
  hyb = ds['hybi'].values

  lev = hya*1000 + hyb*1000

  #-----------------------------------
  #-----------------------------------

  res.tiXAxisString = 'lev'
  res.tiYAxisString = 'hybrid coeffficient'

  # res.xyLineColor = clr[f]
  # res.xyMarkerColor = clr[f]

  # res.xyDashPattern = 0
  res.xyLineColor = 'red'
  res.xyMarkerColor = res.xyLineColor
  plota = ngl.xy(wks, lev, hya, res)

  # res.xyDashPattern = 1
  res.xyLineColor = 'blue'
  res.xyMarkerColor = res.xyLineColor
  plotb = ngl.xy(wks, lev, hyb, res)
  
  ngl.overlay( plotb, plota )

  if f==0:
    plot.append(plotb)
  else:
    ngl.overlay(plot[0],plotb)

#-------------------------------------------------------------------------------
# Add legend
#-------------------------------------------------------------------------------
lgres = ngl.Resources()
lgres.vpWidthF           = 0.1
lgres.vpHeightF          = 0.1
lgres.lgLabelFontHeightF = 0.012
lgres.lgMonoDashIndex    = True
lgres.lgLineLabelsOn     = False
lgres.lgLineThicknessF   = 8
lgres.lgLabelJust        = 'CenterLeft'
lgres.lgLineColors       = clr#[::-1]

# pid = ngl.legend_ndc(wks, len(name), name, 0.6, 0.3, lgres)

#-------------------------------------------------------------------------------
# Finalize plot
#-------------------------------------------------------------------------------
ngl.panel(wks,plot[0:len(plot)],[1,len(plot)],ngl.Resources()); ngl.end()

# trim white space
hc.trim_png(fig_file.replace(os.getenv('PWD')+'/',''))

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------