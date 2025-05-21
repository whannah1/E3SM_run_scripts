import os, numpy as np, xarray as xr, ngl
import hapy_common as hc
home = os.getenv('HOME')

vert_file_list,name,clr = [],[],[]

vert_file_list.append(f'{home}/E3SM/vert_grid_files/L72_E3SM.nc');                clr.append('red'); name.append('L72 old')
vert_file_list.append(f'{home}/E3SM/vert_grid_files/L72_E3SM_new.nsmooth_20.nc'); clr.append('blue'); name.append('L72 new')

vert_file_list.append(f'{home}/E3SM/vert_grid_files/L60.nc');     clr.append('green');name.append('L60')
# vert_file_list.append(f'{home}/E3SM/vert_grid_files/L100.nc');    clr.append('green');name.append('L100')
# vert_file_list.append(f'{home}/E3SM/vert_grid_files/L72_E3SM.nc');clr.append('black');name.append('L72 E3SM')
# vert_file_list.append(f'{home}/E3SM/vert_grid_files/L50_v2.nc');  clr.append('red');  name.append('L50')

# vert_file_list.append(f'{home}/E3SM/vert_grid_files/L20_test.nc');clr.append('pink');  name.append('L20')
# vert_file_list.append(f'{home}/E3SM/vert_grid_files/L30_test.nc');clr.append('purple');  name.append('L30')
# vert_file_list.append(f'{home}/E3SM/vert_grid_files/L40_test.nc');clr.append('cyan');  name.append('L40')



fig_type = 'png'
fig_file = os.getenv('HOME')+'/E3SM/figs_grid/vertical_grid'


zoom_in = False
print_table = False

cutoff_top = False
cutoff_pressure = 800.


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
# print stuff
#-------------------------------------------------------------------------------
if print_table:

  mlev_list, zlev_list = [],[]
  for f,vert_file in enumerate(vert_file_list):
    ds = xr.open_dataset(vert_file)
    # mlev = ds['hyam'].values*1000 + ds['hybm'].values*1000
    mlev = ds['hyai'].values*1000 + ds['hybi'].values*1000
    # zlev = ???
    mlev_list.append(mlev)
    # zlev_list.append(zlev)

  max_len = 0
  for mlev in mlev_list: 
    if len(mlev)>max_len: max_len = len(mlev)

  for k in range(max_len):
    msg = f'{k:3}  '
    # k2 = max_len-k-1
    # msg = f'{k:3}  ({k2:3})'
    for mlev in mlev_list: 
      if k < len(mlev):
        k2 = len(mlev)-k#-1
        msg += f'    ({k2:3})    {mlev[k]:8.1f}'
      else:
        msg += ' '*(12+4+5)
    print(msg)

  # exit()

#-------------------------------------------------------------------------------
# Load data and create plot
#-------------------------------------------------------------------------------
for f,vert_file in enumerate(vert_file_list):

  ds = xr.open_dataset(vert_file)

  # mlev = ds['hyam'].values*1000 + ds['hybm'].values*1000
  mlev = ds['hyai'].values*1000 + ds['hybi'].values*1000

  hc.print_stat(mlev,name=name[f],stat='naxsh',indent='    ',compact=True)

  #-----------------------------------
  #-----------------------------------
  if cutoff_top:
    cutoff_index = 0
    for m,l in reversed(list(enumerate(mlev))):
      # print(f'  {m}  {l}')
      if l < cutoff_pressure:
        cutoff_index = m+1
        break
    mlev = mlev[cutoff_index:]
    
    for m in mlev: print(m)
    print()
    # print(cutoff_index)
    # exit()

  #-----------------------------------
  # Normalized coordinate for X-axis
  #-----------------------------------

  ### basic normalized vertical coord - [0,1] for each grid
  # klev = np.arange(0,len(mlev)) / (len(mlev)-1)

  ### relative normalization - only [0,1] for first grid
  # if f==0: nlev_first = len(mlev)
  # klev = (np.arange(0,len(mlev)) -len(mlev)+nlev_first) / (nlev_first-1)

  ### relative normalization - 
  # if f==0: 
  #   mlev_min_first = np.min(mlev)
  #   slope = 1e3 #- mlev_min_first
  #   intercept = mlev_min_first
  # # kmin = ( np.min(mlev) - intercept ) / slope
  # kmin = np.min(mlev) / 1e3
  # klev = np.linspace(kmin,1.,len(mlev))

  ### just find k of first grid that's closest to min lev
  if f==0: 
    mlev_first = mlev
    klev_first = np.arange(0,len(mlev)) / (len(mlev)-1)
  # mlev_min = np.min(mlev)
  # mlev_min_diff = np.zeros(len(mlev_first))
  # for k,lev in enumerate(mlev_first):
  #   mlev_min_diff[k] = mlev_min - mlev_first[k]
  kmin = np.argmin(np.absolute(np.min(mlev) - mlev_first))
  klev = np.linspace(klev_first[kmin],1.,len(mlev))


  # print(f'  kmin: {kmin}'); print()
  print(klev); print()

  #-----------------------------------
  ### zoom in on the layers near the surface
  #-----------------------------------
  # mlev = mlev[-15:]
  # klev = klev[-15:]
  # res.trYMaxF = 1000
  if zoom_in:
    if f==0:
      ### zoom in on surface layers
      # res.trYMinF = np.min(mlev[-20:])
      # res.trYMaxF = np.max(mlev[-20:])
      # res.trXMinF = np.min(klev[-20:])
      # res.trXMaxF = np.max(klev[-20:])

      ### zoom in on top layers
      res.trYMinF = np.min(mlev[:20])
      res.trYMaxF = np.max(mlev[:20])
      res.trXMinF = np.min(klev[:20])
      res.trXMaxF = np.max(klev[:20])
  
  # res.trXMinF = 0.4
  # res.trYMinF = 600

  # res.trXMinF = 0.6
  # res.trYMinF = 700

  # res.trXMaxF = 0.2
  # res.trYMaxF = 100
  #-----------------------------------
  #-----------------------------------

  res.tiXAxisString = 'normalized level index'
  res.tiYAxisString = 'lev [mb]'

  res.xyLineColor = clr[f]
  res.xyMarkerColor = clr[f]

  # res.xyMarkerSizeF = 0.005+0.004*f
  # res.xyMarkerSizeF = 0.010-0.005*f

  # plot.append( ngl.xy(wks, klev, mlev, res) )
  tplot1 = ngl.xy(wks, klev, mlev, res)
  # tplot2 = ngl.xy(wks, ds['hyai'].values, mlev, res)
  # tplot3 = ngl.xy(wks, ds['hybi'].values, mlev, res)
  
  if f==0:
    if 'tplot1' in locals(): plot.append(tplot1)
    if 'tplot2' in locals(): plot.append(tplot2)
    if 'tplot3' in locals(): plot.append(tplot3)
  else:
    if 'tplot1' in locals(): ngl.overlay(plot[0],tplot1)
    if 'tplot2' in locals(): ngl.overlay(plot[1],tplot2)
    if 'tplot3' in locals(): ngl.overlay(plot[2],tplot3)

  nlev = len(ds['hyam'])

  # name.append(f'L{nlev}')


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

pid = ngl.legend_ndc(wks, len(name), name, 0.6, 0.3, lgres)

#-------------------------------------------------------------------------------
# Finalize plot
#-------------------------------------------------------------------------------
ngl.panel(wks,plot[0:len(plot)],[1,len(plot)],ngl.Resources()); ngl.end()

# trim white space
fig_file = f'{fig_file}.{fig_type}'
os.system(f'convert -trim +repage {fig_file}   {fig_file}')
print(f'\n{fig_file}\n')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------