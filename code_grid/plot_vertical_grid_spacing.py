import os, numpy as np, xarray as xr, ngl, copy
import hapy_common as hc
home = os.getenv('HOME')

vert_file_list,name,clr,dsh = [],[],[],[]


def add_grid(grid_in,n=None,d=0,c='black'):
   global vert_file_list,name,clr,dsh
   vert_file_list.append(grid_in); name.append(n); dsh.append(d); clr.append(c)



grid_path = f'{home}/E3SM/vert_grid_files'

# add_grid(f'{grid_path}/L72_E3SM.nc',       n='L72', d=0,c='red' )
# add_grid(f'{grid_path}/L80_for_E3SMv3.nc', n='L80', d=0,c='blue')
# add_grid(f'{grid_path}/L80_for_E3SMv3_test.nc', n='L80 test', d=1,c='green')

# add_grid(f'{grid_path}/L80_for_E3SMv3.nc',                                       n='L80',           c='black', d=0)
# add_grid(f'{grid_path}/2024_L80_refine_test.rlev_08.nsmth_04.zbot_18.ztop_25.nc',n='L80+08 ztop_25',c='red', d=0)
# add_grid(f'{grid_path}/2024_L80_refine_test.rlev_08.nsmth_04.zbot_18.ztop_30.nc',n='L80+08 18-30',c='green', d=0)
# add_grid(f'{grid_path}/2024_L80_refine_test.rlev_12.nsmth_04.zbot_18.ztop_30.nc',n='L80+12 18-30',c='cyan', d=0)
# add_grid(f'{grid_path}/2024_L80_refine_test.rlev_16.nsmth_04.zbot_15.ztop_30.nc',n='L80+16 15-30',c='orange', d=0)
# add_grid(f'{grid_path}/2024_L80_refine_test.rlev_16.nsmth_06.zbot_15.ztop_30.nc',n='L80+16 15-30',c='red', d=0)
# add_grid(f'{grid_path}/2024_L80_refine_test.rlev_16.nsmth_10.zbot_15.ztop_28.nc',n='L80+16 15-28',c='green', d=0)
# add_grid(f'{grid_path}/2024_L80_refine_test.rlev_24.nsmth_10.zbot_15.ztop_28.nc',n='L80+20 15-28',c='cyan', d=0)
# add_grid(f'{grid_path}/2024_L80_refine_test.rlev_32.nsmth_10.zbot_15.ztop_28.nc',n='L80+32 15-28',c='magenta', d=0)

# add_grid(f'{grid_path}/2024_L80_refine_test.rlev_16.nsmth_10.zbot_20.ztop_30.nc',n='L80+16 20-30',c='red', d=0)
# add_grid(f'{grid_path}/2024_L80_refine_test.rlev_16.nsmth_10.zbot_10.ztop_35.nc',n='L80+16 10-35',c='blue', d=0)

# ### new vert grid test for studying QBO in MMF (SciDAC)
# add_grid(f'{grid_path}/L60_MMF_c20230819.nc',                                n='L60', c='green')
# add_grid(f'{grid_path}/L64_MMF_c20230819.nc',                                n='L64', c='blue')
# add_grid(f'{grid_path}/L72_MMF_c20230819.nc',                                n='L72', c='magenta')

# add_grid(f'{grid_path}/L72_E3SM.nc',                                         n='L72', c='red', d=0)
# add_grid(f'{grid_path}/L72_E3SM_refine+smooth.nsmooth_40.upper_lev_only.nc', n='L80', c='blue',  d=0)
# add_grid(f'{grid_path}/old/L72_E3SM_refine-addmax+smooth.nsmooth_40.upper_lev_only.nc', n='L128', c='red',  d=1)

### new vert grid test for studying QBO in MMF (SciDAC)
# grid_path = f'{home}/E3SM/vert_grid_files'
# add_grid(f'{grid_path}/L60_MMF_c20230819.nc',                                n='L60', c='green')
# add_grid(f'{grid_path}/L64_MMF_c20230819.nc',                                n='L64', c='blue')
# add_grid(f'{grid_path}/L72_MMF_c20230819.nc',                                n='L72', c='magenta')
# add_grid(f'{grid_path}/L80_MMF_c20230819.nc',                                n='LXX', c='pink')

# add_grid(f'{grid_path}/L72_MMF_c20231023.nc',                                n='L64+8', c='green',d=2)
# add_grid(f'{grid_path}/L80_MMF_c20231023.nc',                                n='L72+8', c='darkgreen',d=2)

# add_grid(f'{grid_path}/L64_MMF_c20230821.nc',                                n='L64', c='red')
# add_grid(f'{grid_path}/L70_MMF_c20230821.nc',                                n='L72', c='orange')
# add_grid(f'{grid_path}/L76_MMF_c20230821.nc',                                n='LXX', c='orangered')

# add_grid(f'{grid_path}/L72_E3SM.nc',                                         n='L72', c='black', d=0)
# add_grid(f'{grid_path}/L72_E3SM_refine+smooth.nsmooth_40.upper_lev_only.nc', n='L80', c='gray',  d=0)
# add_grid(f'{grid_path}/L72_E3SM_refine-addmax+smooth.nsmooth_40.upper_lev_only.nc', n='L128', c='red',  d=1)

### smoothed and refined grids for QBO (SciDAC)
# grid_path = f'{home}/E3SM/vert_grid_files'
# add_grid(f'{grid_path}/L72_E3SM.nc',                                         n='L72',         c='black')
# add_grid(f'{grid_path}/L72_E3SM_smooth.nsmooth_40.upper_lev_only.nc',        n='L72 smoothed',c='red')
# add_grid(f'{grid_path}/L72_E3SM_refine+smooth.nsmooth_40.upper_lev_only.nc', n='L72 refined', c='blue')
# add_grid(f'{grid_path}/L72_E3SM_refine-trim+smooth.nsmooth_40.upper_lev_only.nc', n='L72 refined', c='blue')
# add_grid(f'{grid_path}/L72_E3SM_refine-limit.nc',                            n='L72 limit dzdz',c='pink')
# add_grid(f'{grid_path}/L72_E3SM_refine-scale.nc',                            n='L72 scaled',    c='purple')


# add_grid(f'{home}/E3SM/vert_grid_files/L72_E3SM.nc',                  n='L72',     c='black')
add_grid(f'{home}/HICCUP/files_vert/vert_coord_E3SM_L128.nc',         n='L128v1.0',d=0,c='red'  )
# add_grid(f'{home}/E3SM/vert_grid_files/SCREAM_L128_v2.1_c20230216.nc',n='L128v2.1',d=0,c='green')
add_grid(f'{home}/E3SM/vert_grid_files/SCREAM_L128_v2.2_c20230216.nc',n='L128v2.2',d=1,c='blue' )
# add_grid(f'{home}/E3SM/vert_grid_files/SCREAM_L276_v1.1_c20240905.nc',n='L276v1.1',d=0,c='magenta' )
# add_grid(f'{home}/E3SM/vert_grid_files/SCREAM_L256_v1.1_c20240905.nc',n='L256v1.1',d=0,c='cyan' )

add_grid(f'{home}/E3SM/vert_grid_files/SOHIP_L192_v1_c20250414.nc',n='L192v1',d=2,c='magenta' )
add_grid(f'{home}/E3SM/vert_grid_files/SOHIP_L192_v2_c20250414.nc',n='L192v2',d=2,c='cyan' )
add_grid(f'{home}/E3SM/vert_grid_files/SOHIP_L256_v3_c20250414.nc',n='L256v2',d=1,c='green' )

# add_grid(f'{home}/E3SM/vert_grid_files/L72_E3SM.nc',         n='L72',  c='blue')
# add_grid(f'{home}/HICCUP/files_vert/vert_coord_E3SM_L128.nc',n='L128', c='red')
# add_grid('/gpfs/alpine/cli115/world-shared/e3sm/inputdata/atm/scream/init/vertical_coordinates_L128_20220927.nc',n='L128', c='red')

# 470156/9.8

### high-res grid for Gordon Bell 2024
# grid_path = f'{home}/HICCUP/files_vert'
# add_grid(f'{grid_path}/L80_for_E3SMv3.nc'         ,c='blue',n='L80')
# add_grid(f'{grid_path}/L148_GB2024.nsmooth_100.nc',c='pink',n='L148')
# add_grid(f'{grid_path}/L276_GB2024.nsmooth_100.nc',c='purple',n='L276')
# add_grid(f'{home}/E3SM/vert_grid_files/L60.nc'               , c='green',  n='L60')
# add_grid(f'{home}/E3SM/vert_grid_files/L72_E3SM.nc',                  c='black',     n='L72')
# add_grid(f'{home}/HICCUP/files_vert/vert_coord_E3SM_L128.nc',         c='blue',      n='L128v1 (SCREAM)')
# add_grid(f'{home}/E3SM/vert_grid_files/SCREAM_L128_v2.2_c20230216.nc',c='darkgreen', n='L128v2.2',)
# add_grid(f'{home}/HICCUP/files_vert/UP_L125.nc',                      c='red',       n='L125 (UP)')
# add_grid(f'{grid_path}/L276_v1.nsmooth_100.nc',                       c='green',     n='L276 GB2023')
# add_grid(f'{home}/E3SM/vert_grid_files/L276_GB2024.nsmooth_100.nc',   c='magenta',   n='L256+20 GB2024')
# add_grid(f'{home}/E3SM/vert_grid_files/L148_GB2024.nsmooth_100.nc',   c='cyan',      n='L128+20 GB2024')

# # SP-CAM tests for Wayne Chuang (LEAP)
# grid_path = f'{home}/E3SM/vert_grid_files'
# add_grid(f'{grid_path}/L60_MMF_c20230819.nc',    c='green', d=0, n='L60')
# add_grid(f'{grid_path}/L60_spcam.nsmooth_20.nc', c='blue',  d=0, n='L60')

# add_grid(f'{home}/E3SM/vert_grid_files/Lxx_for_E3SMv3_QBOi.nc', n='Lxx',  c='green')
# add_grid(f'{home}/E3SM/vert_grid_files/L80_for_E3SMv3.nc',      n='L80',  c='blue')



fig_type = 'png'
fig_file = os.getenv('HOME')+'/E3SM/figs_grid/vertical_grid_spacing'

print_table     = False
use_height      = True # for Y-axis, or else use pressure
add_zoomed_plot = False
add_refine_box  = False

# set limits for second plot zoomed in on lower levels
# zoom_top_idx = -10
zoom_top_idx = -30

#-------------------------------------------------------------------------------
# Set up workstation
#-------------------------------------------------------------------------------
wks = ngl.open_wks(fig_type,fig_file)
plot = []
res = ngl.Resources()
res.vpWidthF = 0.5
res.nglDraw,res.nglFrame         = False,False
res.tmXTOn                       = False
res.tmXBMajorOutwardLengthF      = 0.
# res.tmXBMinorOutwardLengthF      = 0.
res.tmYLMajorOutwardLengthF      = 0.
res.tmYLMinorOutwardLengthF      = 0.
res.tmYLLabelFontHeightF         = 0.015
res.tmXBLabelFontHeightF         = 0.015
res.tiXAxisFontHeightF           = 0.015
res.tiYAxisFontHeightF           = 0.015
res.tmXBMinorOn,res.tmYLMinorOn  = True,False

res.xyLineThicknessF             = 6.

res.xyMarkLineMode = 'MarkLines'
res.xyMarkerSizeF = 0.005
res.xyMarker = 16

if use_height:
  res.trYReverse = False
else:
  res.trYReverse = True

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
    zlev = np.log(mlev/1e3) * -6740.
    mlev_list.append(mlev)
    zlev_list.append(zlev)

  max_len = 0
  for mlev in mlev_list: 
    if len(mlev)>max_len: max_len = len(mlev)

  for k in range(max_len):
    k2 = max_len-k-1
    msg = f'{k:3}  ({k2:3}) '
    # k2 = max_len-k-1
    # msg = f'{k:3}  ({k2:3})'
    for g in range(len(mlev_list)): 
      # if k < len(mlev_list[g]):
      #   k2 = len(mlev_list[g])-k#-1
      #   msg += f'    ({k2:3})    {mlev_list[g][k]:8.3f} mb  {zlev_list[g][k]:8.3f} m'
      # else:
      #   msg += ' '*(12+4+5)
      if k < len(mlev_list[g]): 
        msg += f'     {mlev_list[g][k]:8.2f} mb   {zlev_list[g][k]:8.1f} m'
    print(msg)

  # exit()

#-------------------------------------------------------------------------------
# Load data
#-------------------------------------------------------------------------------
mlev_list = []
dlev_list = []
for f,vert_file in enumerate(vert_file_list):

  ds = xr.open_dataset(vert_file)

  mlev = ds['hyam'].values*1000 + ds['hybm'].values*1000
  ilev = ds['hyai'].values*1000 + ds['hybi'].values*1000

  # rough estimate of height from pressure
  ilevz = np.log(ilev/1e3) * -6740.
  mlevz = np.log(mlev/1e3) * -6740. / 1e3

  print()
  hc.print_stat(mlev, name=name[f]+' mlev',stat='nxh',indent='    ',compact=True)
  hc.print_stat(mlevz,name=name[f]+' zlev',stat='nxh',indent='    ',compact=True)

  
  dlevz = mlevz*0.
  for k in range(len(mlev)): dlevz[k] = ilevz[k] - ilevz[k+1]

  if use_height:
    mlev_list.append(mlevz)
    dlev_list.append(dlevz)
  else:
    mlev_list.append(mlev)
    dlev_list.append(dlevz)

#-------------------------------------------------------------------------------
# Create plot
#-------------------------------------------------------------------------------
dlev_min = np.min([np.nanmin(d) for d in dlev_list])
dlev_max = np.max([np.nanmax(d) for d in dlev_list])

mlev_min = np.min([np.nanmin(d) for d in mlev_list])
mlev_max = np.max([np.nanmax(d) for d in mlev_list])

# set limits for second plot w/ linear scale
dlev_min_2 = np.min([np.nanmin(d[zoom_top_idx:]) for d in dlev_list])
dlev_max_2 = np.max([np.nanmax(d[zoom_top_idx:]) for d in dlev_list])
mlev_min_2 = np.min([np.nanmin(d[zoom_top_idx:]) for d in mlev_list])
mlev_max_2 = np.max([np.nanmax(d[zoom_top_idx:]) for d in mlev_list])


for f,vert_file in enumerate(vert_file_list):

  mlev = mlev_list[f]
  dlev = dlev_list[f]

  if use_height:
    res.tiXAxisString = 'Grid Spacing [m]'
    res.tiYAxisString = 'Approx. Height [km]'
  else:
    res.tiXAxisString = 'Grid Spacing [m]'
    res.tiYAxisString = 'Approx. Pressure [hPa]'

  res.xyDashPattern = dsh[f]
  res.xyLineColor = clr[f]
  res.xyMarkerColor = clr[f]

  tres1 = copy.deepcopy(res)
  tres2 = copy.deepcopy(res)

  tres1.trXMinF = dlev_min
  tres1.trXMaxF = dlev_max + (dlev_max-dlev_min)*0.05
  if use_height:
    tres1.trYMinF = mlev_min# - mlev_min/2
    tres1.trYMaxF = mlev_max + (mlev_max-mlev_min)*0.05
  else:
    tres1.trYMinF = mlev_min - mlev_min/2
    tres1.trYMaxF = 1e3 #mlev_max

  #print('-'*80)
  #print('-'*80)
  #print(f'WARNING - using custom axis bounds')
  #print('-'*80)
  #print('-'*80)
  #tres1.trXMaxF = 1e3
  #tres1.trYMinF = 10

  tres2.trXMinF = 0 # dlev_min_2
  tres2.trXMaxF = dlev_max_2 + (dlev_max_2-dlev_min_2)*0.05
  tres2.trYMinF = mlev_min_2 #- mlev_min_2/2
  tres2.trYMaxF = 1e3 #mlev_max_2

  # temporary override to highlight new grid
  #tres1.trXMaxF = 800
  #tres2.trXMaxF = 100

  if use_height: 
    tres1.xyYStyle = "Linear"
    tres2.xyYStyle = "Linear"
  else:
    tres1.xyYStyle = "Log"
    tres2.xyYStyle = "Linear"

  tplot1 = ngl.xy(wks, dlev, mlev, tres1)
  
  ### add plot zoomed in on lowest levels
  if add_zoomed_plot: 
    tplot2 = ngl.xy(wks, dlev, mlev, tres2)

  if f==0:
    plot.append(tplot1)
    if add_zoomed_plot: plot.append(tplot2)
  else:
    ngl.overlay(plot[0],tplot1)
    # if len(plot)>=2: ngl.overlay(plot[1],tplot2)
    if add_zoomed_plot: ngl.overlay(plot[1],tplot2)

#-------------------------------------------------------------------------------
# add lines to visually see how grids line up with first case (i.e. control/default)
#-------------------------------------------------------------------------------
# if len(plot)>1:
#   tres3 = copy.deepcopy(tres2)
#   tres3.xyDashPattern = 1
#   tres3.xyLineColor = 'black'
#   tres3.xyLineThicknessF = 1.
#   mlev = mlev_list[0]
#   for k in range(10):
#     kk = len(mlev)-1-k
#     xx = np.array([ -1e5, 1e5 ])
#     yy = np.array([ mlev[kk], mlev[kk] ])
#     ngl.overlay(plot[1], ngl.xy(wks, xx, yy, tres3) )

#-------------------------------------------------------------------------------
# indicate refinement levels
#-------------------------------------------------------------------------------
# if add_refine_box:
#   pgres = ngl.Resources()
#   pgres.nglDraw                = False
#   pgres.nglFrame               = False
#   pgres.gsLineColor            = 'black'
#   pgres.gsLineThicknessF       = 10.0
#   pgres.gsFillIndex            = 0
#   pgres.gsFillColor            = 'red'
#   pgres.gsFillOpacityF         = 0.3

#   rx1,rx2 = 0,1e6
#   rx = [rx1,rx2,rx2,rx1,rx1]

#   rz1,rz2 = 10e3,45e3
#   if use_height: 
#     rk1,rk2 = rz1,rz2
#   else:
#     rk1,rk2 = rp1,rp2
#   ry = [rk1,rk1,rk2,rk2,rk1]

#   pdum = ngl.add_polygon(wks, plot[0], rx, ry, pgres)

#-------------------------------------------------------------------------------
# Add legend
#-------------------------------------------------------------------------------
lgres = ngl.Resources()
lgres.vpWidthF           = 0.1
lgres.vpHeightF          = 0.13
lgres.lgLabelFontHeightF = 0.012
lgres.lgMonoDashIndex    = True
lgres.lgLineLabelsOn     = False
lgres.lgLineThicknessF   = 20
lgres.lgLabelJust        = 'CenterLeft'
lgres.lgLineColors       = clr[::-1]

for n in range(len(name)): name[n] = ' '+name[n]

if add_zoomed_plot:
  lpx, lpy = 0.26, 0.45
  # lpx, lpy = 0.8, 0.45
else:
  lpx, lpy = 0.6, 0.3

pid = ngl.legend_ndc(wks, len(name), name[::-1], lpx, lpy, lgres)

#-------------------------------------------------------------------------------
# Finalize plot
#-------------------------------------------------------------------------------
pnl_res = ngl.Resources()
pnl_res.nglPanelXWhiteSpacePercent = 5
pnl_res.nglPanelYWhiteSpacePercent = 5
ngl.panel(wks,plot[0:len(plot)],[1,len(plot)],pnl_res); ngl.end()

# trim white space
fig_file = f'{fig_file}.{fig_type}'
os.system(f'convert -trim +repage {fig_file}   {fig_file}')
fig_file = fig_file.replace(f'{home}/E3SM/','')
print(f'\n{fig_file}\n')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
