import os, copy, ngl, xarray as xr, numpy as np, subprocess as sp
import hapy_common as hc, hapy_E3SM   as he, hapy_setres as hs

case = 'E3SM.MEMLEAK_TEST.ne4pg2_ne4pg2.F-MMF1-AQP1.CRMNX_32.RADNX_32.gnu9.00'
scratch_dir = f'/global/cscratch1/sd/whannah/e3sm_scratch/cori-knl'

file_list,clr = [],[]
file_list.append(f'{scratch_dir}/{case}/run/e3sm.log.47524509.210924-161457');clr.append('black')
# file_list.append(f'{scratch_dir}/{case}/run/e3sm.log.47599361.210927-113116');clr.append('red')
# file_list.append(f'{scratch_dir}/{case}/run/e3sm.log.47604905.210927-115545');clr.append('blue')

task_list = ['10','20','30']

fig_type = 'png'
fig_file = 'memory_leak.v1'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
num_file = len(file_list)
time_list,data_list,clr_list = [],[],[]
for f,file_name in enumerate(file_list):

  for task in task_list:
    cmd = f'grep "{task}:  mem-debug" {file_name} | grep "(final)" '
    (mem_usage, err) = sp.Popen(cmd, stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()

    mem_usage = mem_usage.split('\n')

    cnt = 0
    cnt_list,mem_list = [],[]
    for line in mem_usage: 
      for w,word in enumerate(line.split()):
        if word=='(usage)': 
          mem = float( line.split()[w-2] )
          mem_list.append(mem)
          cnt_list.append(cnt)
          cnt += 1

    mem_list = np.array(mem_list)

    name = file_name.replace(f'{scratch_dir}/{case}/run/','')
    name = name+f'  task {task}'
    hc.print_stat(mem_list,name=name,compact=True,indent='  ')

    clr_list.append( clr[f] )
    data_list.append( mem_list )
    time_list.append( cnt_list )

# exit()

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

wkres = ngl.Resources()
# npix=2048; wkres.wkWidth,wkres.wkHeight=npix,npix
wks = ngl.open_wks(fig_type,fig_file,wkres)

res = hs.res_xy()
# res.vpHeightF = 0.5
# res.vpHeightF = 0.2
res.tmYLLabelFontHeightF         = 0.02
res.tmXBLabelFontHeightF         = 0.02
res.tiXAxisFontHeightF           = 0.02
res.tiYAxisFontHeightF           = 0.02
res.xyLineThicknessF = 10
# res.tiXAxisString = 'Time [days]'
res.trYMinF = np.min([np.nanmin(d) for d in data_list])
res.trYMaxF = np.max([np.nanmax(d) for d in data_list])
res.trXMinF = np.min([np.nanmin(d) for d in time_list])
res.trXMaxF = np.max([np.nanmax(d) for d in time_list])

for d in range(len(data_list)):
  res.xyLineColor = clr_list[d]
  tplot = ngl.xy(wks, time_list[d], data_list[d], res)
  if d==0: 
    plot = tplot
  else:
    ngl.overlay(plot,tplot)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

ngl.draw(plot)
ngl.frame(wks)

# layout = [1,len(plot)]
# ngl.panel(wks,plot,layout,hs.setres_panel())

ngl.end()

hc.trim_png(fig_file)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------