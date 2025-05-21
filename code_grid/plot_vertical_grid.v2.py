import os, numpy as np, xarray as xr, ngl
home = os.getenv('HOME')

vert_file_list,name,clr = [],[],[]
# vert_file_list.append(f'{home}/E3SM/vert_grid_files/L72_E3SM.nc'); clr.append('black'); name.append('L72')
# vert_file_list.append(f'{home}/E3SM/vert_grid_files/L50_v2.nc');  clr.append('red');  name.append('L50')
# vert_file_list.append(f'{home}/E3SM/vert_grid_files/L60.nc');  clr.append('green');  name.append('L60')

vert_file_list.append(f'{home}/E3SM/vert_grid_files/L72_E3SM.nc');                clr.append('red'); name.append('L72 old')
vert_file_list.append(f'{home}/E3SM/vert_grid_files/L72_E3SM_new.nsmooth_20.nc'); clr.append('blue'); name.append('L72 new')


fig_type = 'png'
fig_file = os.getenv('HOME')+'/E3SM/figs_grid/vertical_grid.v2'



#-------------------------------------------------------------------------------
# Set up workstation
#-------------------------------------------------------------------------------
wkres = ngl.Resources()
# npix = 2048; wkres.wkWidth,wkres.wkHeight=npix,npix
wks = ngl.open_wks(fig_type,fig_file,wkres)
plot = [None]*2
res = ngl.Resources()
res.vpWidthF = 0.3
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
res.xyLineThicknessF             = 8.

# res.xyMarkLineMode = 'MarkLines'
# res.xyMarkerSizeF = 0.005
# res.xyMarker = 16

res.trYReverse = True

res.trXMinF = 0
res.trXMaxF = len(vert_file_list)+1
res.trYMinF = 0.05
res.trYMaxF = 1e3

res.tiXAxisString = ''
res.tiYAxisString = 'lev [mb]'

res.tmXBMode = 'Explicit'
res.tmXBValues = np.arange(1,len(name)+1)
res.tmXBLabels = name

lres = ngl.Resources()
lres.gsLineThicknessF = 4.

#-------------------------------------------------------------------------------
# Load data and create plot
#-------------------------------------------------------------------------------
for f,vert_file in enumerate(vert_file_list):

  ds = xr.open_dataset(vert_file)

  mlev = ds['hyam'].values*1000 + ds['hybm'].values*1000
  ilev = ds['hyai'].values*1000 + ds['hybi'].values*1000

  res.xyLineColor = clr[f]
  lres.gsLineColor = clr[f]
  # res.xyMarkerColor = clr[f]

  for p in range(2):

    if p==0: res.xyYStyle = "Linear"
    if p==1: res.xyYStyle = "Log"

    tplot = ngl.xy(wks, np.ones(len(mlev)) + f, ilev, res)

    dplot = [None]*len(ilev)
    for k,lev in enumerate(ilev):
      xx = np.array([f+1-0.25,f+1+0.25])
      yy = np.array([lev,lev])
      # dplot[k] = ngl.xy(wks, xx, yy, res)
      # ngl.overlay(tplot,dplot[k])
      dummy = ngl.add_polyline(wks, tplot, xx, yy, lres)

    if f==0:
      plot[p] = tplot
    else:
      ngl.overlay(plot[p],tplot)


#-------------------------------------------------------------------------------
# Add legend
#-------------------------------------------------------------------------------
# lgres = ngl.Resources()
# lgres.vpWidthF           = 0.1
# lgres.vpHeightF          = 0.1
# lgres.lgLabelFontHeightF = 0.012
# lgres.lgMonoDashIndex    = True
# lgres.lgLineLabelsOn     = False
# lgres.lgLineThicknessF   = 8
# lgres.lgLabelJust        = 'CenterLeft'
# lgres.lgLineColors       = clr#[::-1]

# pid = ngl.legend_ndc(wks, len(name), name, 0.6, 0.3, lgres)

#-------------------------------------------------------------------------------
# Finalize plot
#-------------------------------------------------------------------------------
ngl.panel(wks,plot[0:len(plot)],[1,len(plot)],ngl.Resources()); ngl.end()

# fig_file = fig_file.replace(os.getenv('HOME')+'/Research/E3SM/','')
fig_file = fig_file.replace(os.getenv('PWD')+'/','')

# trim white space
fig_file = f'{fig_file}.{fig_type}'
os.system(f'convert -trim +repage {fig_file}   {fig_file}')
print(f'  \n{fig_file}\n')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------