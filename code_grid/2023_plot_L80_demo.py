import os, numpy as np, xarray as xr, ngl, copy
import hapy_common as hc
home = os.getenv('HOME')

vert_file_list,name,clr,dsh = [],[],[],[]


def add_grid(grid_in,n=None,d=0,c='black'):
   global vert_file_list,name,clr,dsh
   vert_file_list.append(grid_in); name.append(n); dsh.append(d); clr.append(c)



### new vert grid test for studying QBO in MMF (SciDAC)
grid_path = f'{home}/E3SM/vert_grid_files'

# add_grid(f'{grid_path}/L72_E3SM.nc',    n='L72', c='black', d=1)
# add_grid(f'{grid_path}/L80_demo_00.nc',    n='L80_00',    c='black')
# add_grid(f'{grid_path}/L80_demo_01.nc',    n='L80_01',    c='black')
# add_grid(f'{grid_path}/L80_demo_02.01.nc', n='L80_02.01', c='black')
# add_grid(f'{grid_path}/L80_demo_02.02.nc', n='L80_02.02', c='black')
# add_grid(f'{grid_path}/L80_demo_02.03.nc', n='L80_02.03', c='black')
# add_grid(f'{grid_path}/L80_demo_02.04.nc', n='L80_02.04', c='black')
# add_grid(f'{grid_path}/L80_demo_02.05.nc', n='L80_02.05', c='black')
# add_grid(f'{grid_path}/L80_demo_03.nc',    n='L80_03',    c='black')
# add_grid(f'{grid_path}/L80_demo_04.nc',    n='L80_04',    c='black')

add_grid(f'{grid_path}/L72_E3SM.nc',       n='L72',       c='black',d=1)
add_grid(f'{grid_path}/L80_demo_03.nc',    n='L80_03',    c='red'  ,d=0)
add_grid(f'{grid_path}/L80_demo_04.nc',    n='L80_04',    c='blue' ,d=0)



fig_file,fig_type = os.getenv('HOME')+'/E3SM/figs_grid/2023_L80_demo','png'

print_table = False
use_height = False # for Y-axis, or else use pressure
add_refine_box = False

#-------------------------------------------------------------------------------
# Set up workstation
#-------------------------------------------------------------------------------
wks = ngl.open_wks(fig_type,fig_file)
# plot = []
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
  mlevz = np.log(mlev/1e3) * -6740.

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


for f,vert_file in enumerate(vert_file_list):

  # tmp_fig_file = os.getenv('HOME')+f'/E3SM/figs_grid/2023_L80_demo_{name[f]}'
  # print(tmp_fig_file)
  # exit()

  # wks = ngl.open_wks(fig_type,tmp_fig_file)
  # plot = []

  # mlev = mlev_list[f]
  # dlev = dlev_list[f]

  # dlev_min = np.min([np.nanmin(d) for d in dlev_list[f-1:f+1]])
  # dlev_max = np.max([np.nanmax(d) for d in dlev_list[f-1:f+1]])

  tres = copy.deepcopy(res)

  if use_height:
    tres.xyYStyle = "Linear"
    tres.tiXAxisString = 'Grid Spacing [m]'
    tres.tiYAxisString = 'Approx. Height [m]'
  else:
    tres.xyYStyle = "Log"
    tres.tiXAxisString = 'Grid Spacing [m]'
    tres.tiYAxisString = 'Approx. Pressure [hPa]'

  tres.trXMinF = dlev_min
  tres.trXMaxF = dlev_max + (dlev_max-dlev_min)*0.05
  tres.trYMinF = mlev_min - mlev_min/2
  tres.trYMaxF = 1e3 #mlev_max

  # if f==0: continue
  # tres.xyDashPattern = 0
  # tres.xyLineColor   = 'red'
  # tres.xyMarkerColor = 'red'
  # plot =            ngl.xy(wks, dlev_list[f-1], mlev_list[f-1], tres)
  # tres.xyDashPattern = 0
  # tres.xyLineColor   = 'blue'
  # tres.xyMarkerColor = 'blue'
  # ngl.overlay(plot, ngl.xy(wks, dlev_list[f],   mlev_list[f], tres))

  tres.xyDashPattern = dsh[f]
  tres.xyLineColor   = clr[f]
  tres.xyMarkerColor = clr[f]

  print(clr[f])

  tplot = ngl.xy(wks, dlev_list[f],   mlev_list[f], tres)

  if f==0:
    plot = tplot
  else:
    ngl.overlay(plot,tplot)

ngl.draw(plot)
ngl.frame(wks)
ngl.destroy(wks)

# trim white space
tmp_fig_file = fig_file
tmp_fig_file = f'{tmp_fig_file}.{fig_type}'
os.system(f'convert -trim +repage {tmp_fig_file}   {tmp_fig_file}')
tmp_fig_file = tmp_fig_file.replace(f'{home}/E3SM/','')
print(f'\n{tmp_fig_file}\n')


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------