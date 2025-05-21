#!/usr/bin/env python
import sys, os, fileinput, re, subprocess as sp, glob, copy
import hapy_common as hc, hapy_setres as hs
import numpy as np, xarray as xr, ngl
# Set up terminal colors
class bcolor:
   ENDC    = '\033[0m';  BLACK  = '\033[30m'; RED   = '\033[31m'  
   GREEN   = '\033[32m'; YELLOW = '\033[33m'; BLUE  = '\033[34m'
   MAGENTA = '\033[35m'; CYAN   = '\033[36m'; WHITE = '\033[37m'
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
name,nodes,groups,group_name,clr,dsh  = [],[],[],[],[],[]
subdir_list = []
sbase,sgroup = [],[]
#-------------------------------------------------------------------------------
# updated Summit timing
#-------------------------------------------------------------------------------

node_cnt_str = 'NODES'

group_list = []
# group_list.append({'arch':'CPU','clr':'red', 'dsh':0,'crm':'32x1','ver':'00','sbase':True})
group_list.append({'arch':'GPU','clr':'blue','dsh':0,'crm':'32x1','ver':'00','sbase':False})
group_list.append({'arch':'GPU','clr':'red', 'dsh':0,'crm':'32x32','ver':'00','sbase':False})

# group_list.append({'arch':'CPU','clr':'red', 'dsh':1,'grid':'ne30_ne30','ver':'01a','subdir':'Cases',     'sbase':False})
# group_list.append({'arch':'GPU','clr':'blue','dsh':1,'grid':'ne30_ne30','ver':'01a','subdir':'Cases',     'sbase':False})
# group_list.append({'arch':'CPU','clr':'red', 'dsh':1,'grid':'ne30_ne30','subdir':'Cases_olcf','sbase':True})
# group_list.append({'arch':'GPU','clr':'blue','dsh':1,'grid':'ne30_ne30','subdir':'Cases_olcf','sbase':False})
# group_list.append({'arch':'GPU','clr':'blue','dsh':1,'grid':'ne120_ne120','sbase':False})

for g in group_list:
   group = []
   # grid = g['grid']
   grid = 'ne120pg2_r05_oECv3'
   a,c,d,v = g['arch'],g['clr'],g['dsh'],g['ver']
   crm = g['crm']
   sb = g['sbase']
   node_list = [250,500,1000,2000]
   # node_list = [500,1000]
   for n in node_list:
      group.append(f'E3SM.INCITE2023-TIMING-{v}.GNU{a}.{grid}.F2010-MMF1.NODES_{n}.NXY_{crm}')
   groups.append(group); clr.append(c); dsh.append(d); sbase.append(sb)
   subdir_list.append('Cases')
   crm_rank = '2D'
   if 'x1' not in crm: crm_rank = '3D'
   group_name.append(f' {crm_rank} CRM ({crm})')
   

run_length_nday = 5

convert_sypd  = True
plot_speedup  = False
common_y_axis = True
ideal_scaling = False

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

node_list_all = []
for case_list in groups:
   for case in case_list:
      params = [p.split('_') for p in case.split('.')]
      for p in params:
         if p[0]==node_cnt_str: node_list_all.append(float(p[1]))

param_list = []
param_list.append('CPL:ATM_RUN')
param_list.append('a:crm_physics_tend')
param_list.append('a:dyn_run')
param_list.append('a:radiation')
# param_list.append('')
# param_list.append('')
# param_list.append('')

# ATM Other   'CPL:ATM_RUN' - sum (above)
# Remaining Model   'CPL:RUN_LOOP' - 'CPL:ATM_RUN'

num_plot_col = 2

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def print_plot_values(px,py):
   str_px,str_py = '',''
   for i in range(len(px)): 
      str_px += f'{px[i]:6.0f},' if np.isfinite(px[i]) else f'--,'
      str_py += f'{py[i]:6.1f},' if np.isfinite(py[i]) else f'--,'
   print('\n'+f'    px: [{str_px}]')
   print(     f'    py: [{str_py}]\n')
#-------------------------------------------------------------------------------
# setup plot stuff
#-------------------------------------------------------------------------------
# num_param = len(param)

if 'dsh' not in vars() or dsh==[]: dsh = np.zeros(num_case)

fig_file = os.getenv('HOME')+'/E3SM/figs_performance/perf.scaling.incite2023'

wks = ngl.open_wks('png',fig_file)
plot = [None]*len(param_list)
if plot_speedup: plot = [None]*len(param_list)*2
res = hs.res_xy()
res.vpHeightF = 0.4
res.tmXBMinorOn  = True
res.tmYLMinorOn  = True
res.xyMarkLineMode = 'MarkLines'
res.xyMarker = 16
res.xyMarkerSizeF = 0.008

res.xyLineThicknessF = 6

res.tmXMajorGrid = True
res.tmYMajorGrid = True
res.tmXMinorGrid = True
res.tmYMinorGrid = True

res.tmXMajorGridLineColor = 'gray'
res.tmYMajorGridLineColor = 'gray'
res.tmXMinorGridLineColor = 'gray'
res.tmYMinorGridLineColor = 'gray'

res.tmXMajorGridThicknessF = 4
res.tmYMajorGridThicknessF = 4
res.tmXMinorGridThicknessF = 1
res.tmYMinorGridThicknessF = 1

# res.tmXMajorGridLineDashPattern = 0

res.xyXStyle = 'Log'
res.xyYStyle = 'Log'

lres = copy.deepcopy(res)
lres.xyLineThicknessF = 3
lres.xyMarkLineMode = 'Lines'
lres.xyLineColor   = 'gray'
lres.xyDashPattern = 2

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def is_stat_param(param):
   if 'a:'   in param: return True
   if 'a_i:' in param: return True
   if 'CPL:' in param: return True
   return False
#-------------------------------------------------------------------------------
# make sure all logs are unzipped and find max case name length
#-------------------------------------------------------------------------------
max_case_len = 0
for g,case_list in enumerate(groups):
   for c,case in enumerate(case_list):
      timing_dir = os.getenv('HOME')+f'/E3SM/{subdir_list[g]}/{case}/timing'
      timing_stat_gz_path = f'{timing_dir}/*.gz'
      if len(glob.glob(timing_stat_gz_path))>0: os.system(f'gunzip {timing_stat_gz_path} ')
      # find max char len for case name
      if len(case)>max_case_len: max_case_len = len(case)

max_case_len = max_case_len+4

#-------------------------------------------------------------------------------
# Loop through parameters and cases
#-------------------------------------------------------------------------------
group_data_list_list = []
for param_ind,param in enumerate(param_list) :
   print()
   group_data_list = []
   file_list = []

   tparam = param
   # if param=='physics_fraction': tparam = 'a:CAM_run'

   for g,case_list in enumerate(groups):
      print()
      data_list = []
      for c,case in enumerate(case_list):
         # print('')
         if case=='':
            print('')
            continue

         timing_dir = os.getenv('HOME')+f'/E3SM/{subdir_list[g]}/{case}/timing'
         case_name_fmt = bcolor.CYAN+f'{case:{max_case_len}}'+bcolor.ENDC

         # check that the timing files exist
         timing_file_path = f'{timing_dir}/e3sm_timing*'
         if len(glob.glob(timing_file_path))==0: 
            if not os.path.isdir(os.getenv('HOME')+f'/E3SM/{subdir_list[g]}/{case}'):
               print(f'    {case_name_fmt}   '+bcolor.RED+'case doesn\'t exist!'+bcolor.ENDC)
            else:
               print(' '*4+f'{case_name_fmt}  No files!')
            data_list.append(np.nan)
            continue


         #-------------------------------------------------------------------------
         # grep for the apropriate line in the stat files

         stat_file = f'{timing_dir}/e3sm_timing*'
         if 'CPL:' in tparam: stat_file = stat_file.replace('*','_stats*')
         cmd = f'grep  --with-filename \'{tparam}\'  {stat_file}'
         proc = sp.Popen(cmd, stdout=sp.PIPE, shell=True, universal_newlines=True)
         (msg, err) = proc.communicate()
         msg = msg.split('\n')
         stat_file = msg[0].split(':')[0]

         #-------------------------------------------------------------------------
         # Clean up message but don't print yet

         for m in range(len(msg)): 
            line = msg[m]
            # remove path to timing file in line
            line = line[line.find('e3sm_timing_stats'):]
            # remove file name, which is always 40 characters long
            if 'e3sm_timing_stats' in line: line = line[40:]
            # Add case name
            if line!='': line = case_name_fmt+line
            # line = line.replace(f'e3sm_timing      ','')
            msg[m] = line
            
         #-------------------------------------------------------------------------
         # print stat file header with indentation
         if is_stat_param(tparam):
            head = sp.check_output(['head',stat_file],universal_newlines=True).split('\n')
            for line in head: 
               if 'walltotal' in line:
                  hline = ' '*max_case_len+line
                  if c==0: print(' '*4+hline)
                  break
                  
         #-------------------------------------------------------------------------
         # set up character indices for color
         if is_stat_param(tparam):
            n1 = hline.find('walltotal')+len('walltotal')
            # n1 = hline.find('wallmax')
            n2 = hline.find('(proc   thrd  )   wallmin')
            n3 = hline.find('wallmin')
            n4 = n3+len('wallmin')
            offset = len(bcolor.GREEN)*2-1
            n1 += offset
            n2 += offset
            n3 += offset
            n4 += offset
         elif 'ATM Run Time' in tparam:
            line = msg[0]
            n1 = line.replace(':','', 1).find(':')+2
            num_in_list = re.findall(r'\d+\.\d+', line[n1:])
            n1 = line.find(num_in_list[2])
            n2 = line.find(num_in_list[2])+len(num_in_list[2])
         else:
            line = msg[0]
            n1 = line.replace(':','', 1).find(':')+2
            num_in_list = re.findall(r'\d+\.\d+', line[n1:])
            n2 = line.find(num_in_list[0])+len(num_in_list[0])

         #-------------------------------------------------------------------------
         # print the timing data
         num_file = -len(msg)
         data,dpos = [],[]
         frac_cnt,phys_cost,tot_cost = 0,0,0
         for line in msg[num_file:] : 
            if line=='': continue
            if is_stat_param(tparam):
               wallmax = float(line[n1:n2])
               if convert_sypd:
                  wallmax_sypd = ( run_length_nday / 365. ) / ( wallmax / 86400. )
                  data.append(wallmax_sypd)
               else:
                  data.append(wallmax)
               # dpos.append(float(c))
               line = line[:n1] +bcolor.GREEN  +line[n1:n2]+bcolor.ENDC +line[n2:]
            else:
               data.append(float(line[n1:n2]))
               line = line[:n1] +bcolor.GREEN  +line[n1:n2]+bcolor.ENDC +line[n2:]
               # Print conversion to min aand hours for specific params
               offset = len(bcolor.GREEN)
               if tparam=='Run Time    :' and line[n1+offset:n2+offset]!='' :
                  sec = float( line[n1+offset:n2+offset] )
                  line = line+'  ('+bcolor.GREEN+f'{sec/60:.2f}'     +bcolor.ENDC+' min)'
                  line = line+'  ('+bcolor.GREEN+f'{sec/60/60:.2f}'  +bcolor.ENDC+' hour)'
            # print the line
            print(' '*4+line)

         data = np.array(data)
         avg = np.average(data)

         data_list.append(avg)

         # print(f'average: {bcolor.GREEN}{avg:6.3}{bcolor.ENDC}')

      group_data_list.append(data_list)

      # print()
      # print(group_data_list)
      # print()

   group_data_list_list.append(group_data_list)


#-------------------------------------------------------------------------------
# set common Y-axis limits
#-------------------------------------------------------------------------------
data_list_all = []
if common_y_axis:
   data_min,data_max = 1e3,0
   for param_ind,param in enumerate(param_list) :   
      group_data_list = group_data_list_list[param_ind]
      for g,data_list in enumerate(group_data_list):
         data_min = np.min([data_min,np.nanmin(np.array(data_list))])
         data_max = np.max([data_max,np.nanmax(np.array(data_list))])
         for d in data_list: data_list_all.append(d)
   
   data_std = np.nanstd(np.array(data_list_all))

   print(f'\n  Common Y-axis limts: {data_min}  --  {data_max}  (std: {data_std})\n')
   # exit()

#-------------------------------------------------------------------------------
# restart parameter loop to make the plots
#-------------------------------------------------------------------------------
for param_ind,param in enumerate(param_list) :
   group_data_list = group_data_list_list[param_ind]
   #----------------------------------------------------------------------------
   # set plot limits
   
   mag = np.max(node_list_all) - np.min(node_list_all)
   res.trXMinF = np.min(node_list_all)/2 #- 0.01*mag
   res.trXMaxF = np.max(node_list_all)*2 #+ 0.1*mag

   if common_y_axis:
      mag = np.nanmax(data_list_all) - np.nanmin(data_list_all)
      res.trYMinF = data_min/2
      res.trYMaxF = data_max*2 #+ 0.1*mag

   else:
      group_data_list_flat = [item for sublist in group_data_list for item in sublist]

      # px = xr.DataArray(np.array(dpos_list)).stack().values
      py = xr.DataArray(np.array(group_data_list_flat)).stack().values
      
      tpy = np.ma.masked_invalid(py)
      mag = np.max(tpy) - np.min(tpy)
      res.trYMinF = np.min(tpy)   - 0.1*np.min(tpy)
      res.trYMaxF = np.max(tpy)   + 0.1*np.max(tpy)

      ### apply some sensible limits to the X axis for clarity
      # if res.trXMinF > 1e0 and res.trXMinF < 1e1: res.trXMinF = 1e0
      # if res.trXMinF > 1e1 and res.trXMinF < 1e2: res.trXMinF = 1e1
      # if res.trXMinF > 1e2 and res.trXMinF < 1e3: res.trXMinF = 1e2

      # if res.trXMaxF > 1e1 and res.trXMaxF < 1e2: res.trXMaxF = 1e2
      # if res.trXMaxF > 1e2 and res.trXMaxF < 1e3: res.trXMaxF = 1e3
      # if res.trXMaxF > 1e3 and res.trXMaxF < 1e4: res.trXMaxF = 1e4

      ### apply some sensible limits to the Y axis for clarity
      # if res.trYMinF > 1e1 and res.trYMinF < 1e2: res.trYMinF = 1e1
      # if res.trYMinF > 1e2 and res.trYMinF < 1e3: res.trYMinF = 1e2
      # if res.trYMinF > 1e3 and res.trYMinF < 1e4: res.trYMinF = 1e3

      # if res.trYMaxF > 1e1 and res.trYMaxF < 1e2: res.trYMaxF = 1e2
      # if res.trYMaxF > 1e2 and res.trYMaxF < 1e3: res.trYMaxF = 1e3
      # if res.trYMaxF > 1e3 and res.trYMaxF < 1e4: res.trYMaxF = 1e4

   #----------------------------------------------------------------------------
   # calculate bounds for speedup plot
   if plot_speedup:
      smin_grp = np.full(len(group_data_list),np.nan)
      smax_grp = np.full(len(group_data_list),np.nan)
      for g,data_list in enumerate(group_data_list):
         py = np.array(data_list)
         if sbase[g]:
            baseline = py
         else:
            smin_grp[g] = np.nanmin(py/baseline)
            smax_grp[g] = np.nanmax(py/baseline)
            # print(f'   {(py/baseline)}')
      smin_grp = np.ma.masked_invalid(np.array(smin_grp))
      smax_grp = np.ma.masked_invalid(np.array(smax_grp))
      smin = np.nanmin(smin_grp) - 0.1*np.nanmin(smin_grp)
      smax = np.nanmax(smax_grp) + 0.1*np.nanmax(smax_grp)

   # print()
   # print(f'smin_grp: {smin_grp}')
   # print(f'smax_grp: {smax_grp}')
   # print()
   # print(f'smin: {smin}')
   # print(f'smax: {smax}')     
   # exit()

   #----------------------------------------------------------------------------
   # plot timing data

   # res.tiXAxisString = xvar
   # res.tiYAxisString = yvar

   for g,data_list in enumerate(group_data_list):

      case_list = groups[g]

      # figure out node count for each point
      node_list = []
      for case in case_list:
         params = [p.split('_') for p in case.split('.')]
         for p in params:
            if p[0]==node_cnt_str: node_list.append(float(p[1]))

      px = xr.DataArray(np.array(node_list)).stack().values
      py = xr.DataArray(np.array(data_list)).stack().values

      #-------------------------------------------------
      #-------------------------------------------------
      # print data that will go on the plot
      print()
      for c,case in enumerate(case_list):
         if np.isnan(py[c]) : continue
         if 'GPU' in case: arch = 'GPU'
         if 'CPU' in case: arch = 'CPU'
         msg = f'    {arch}'
         msg+= f'    # nodes: {bcolor.GREEN}{int(px[c]):6}{bcolor.ENDC}'
         msg+= f'    Throughput: {bcolor.GREEN}{    py[c] :6.2f}{bcolor.ENDC} sypd'
         print(msg)
      #-------------------------------------------------
      #-------------------------------------------------

      px = np.where(np.isnan(py), np.nan, px)
      px = np.ma.masked_invalid(np.stack(px))
      py = np.ma.masked_invalid(np.stack(py))

      # print_plot_values(px,py)

      res.tiXAxisString = '# Nodes'
      res.tiYAxisString = 'sim year / day'

      res.xyMarkerColor = clr[g]
      res.xyLineColor   = clr[g]
      res.xyDashPattern = dsh[g]

      if ideal_scaling and g==0 :
         res.trYMinF = 1e-3
         res.trYMaxF = 1e6
         res.trXMinF = 1e-3
         res.trXMaxF = 1e6

      tplot = ngl.xy(wks, px, py, res)

      if ideal_scaling and g==0 :
         # for p in range(2):
            y0 = np.nanmedian(data_list)
            x0 = node_list[ np.where(data_list == y0)[0][0] ]
            # if p==0: lx = np.array([ ( 1e1  - y0 ) + x0 , np.nanmax(node_list) ])
            # if p==0: lx = np.array([ ( 1e-1 - y0 ) + x0 , ( 1e1 - y0 ) + x0 ])
            # if p==1: lx = np.array([ ( 1e-3 - y0 ) + x0 , ( 1e3 - y0 ) + x0 ])
            ly = np.array([1e-3,1e-2,1e-1,1e0,1e1,1e2,1e3,1e4,1e5])
            lx = np.empty(len(ly))
            for i,ty in enumerate(ly):
               lx[i] = ( ty - y0 ) + x0
            # ly = ( lx - x0 ) + y0
            print(); print(f'x0 / y0 : {x0} / {y0}'); print(f'lx / ly : {lx} / {ly}')
            # m = (ly-y0) / (lx-x0)
            # b = -x0*m + y0
            # print(f'slope     : {m}')
            # print(f'intercept : {b}')
            # if np.any(ly<=0) or np.any(np.isnan(ly)):
            #    print(); print(f'x0 / y0 : {x0} / {y0}'); print(f'lx / ly : {lx} / {ly}')
            #    exit('ERROR: ideal line values are invalid!')
            ngl.overlay( tplot, ngl.xy(wks,lx,ly,lres) )

            ngl.overlay(tplot,ngl.xy(wks, np.array([1e2,1e3]), np.array([1e2,1e3]), lres))
            ngl.overlay(tplot,ngl.xy(wks, np.array([1e2,1e3]), np.array([1e2,1e3])-50, lres))
            ngl.overlay(tplot,ngl.xy(wks, np.array([1e2,1e3]), np.array([1e2,1e3])-99, lres))
         

      ip = param_ind
      if plot_speedup: ip = param_ind*2

      if plot[ip] is None:
         plot[ip] = tplot
      else:
         ngl.overlay( plot[ip], tplot )
      del tplot

      #-------------------------------------------------
      # plot speedup
      #-------------------------------------------------
      if plot_speedup:
         if sbase[g]:
            baseline = py
         else:
            sx,sy = px,py/baseline
            sres = copy.deepcopy(res)
            sres.trYMinF = smin 
            sres.trYMaxF = smax 
            sres.xyYStyle = 'Linear'
            splot = ngl.xy(wks, sx, sy, sres)

         if 'splot' in locals():
            if plot[ip+1] is None:
               plot[ip+1] = splot
            else:
               ngl.overlay( plot[ip+1], splot )
            del splot
         
      #-------------------------------------------------
      #-------------------------------------------------

   # # Add horizontal lines
   # ngl.overlay( plot[len(plot)-1], ngl.xy(wks,[0,0],[-1e8,1e8],lres) )
   # ngl.overlay( plot[len(plot)-1], ngl.xy(wks,[-1e8,1e8],[0,0],lres) )

   param_name = param
   if param=='Throughput':       param_name = 'Overall Model Throughput [sypd]'
   if param=='ATM Run Time':     param_name = 'Atmosphere Model Throughput [sypd]'
   # if param=='physics_fraction': param_name = 'Proportional Cost of Physics (excluding I/O)'
   
   subtitle_font_height = 0.015
   if len(param_list)==2: subtitle_font_height = 0.015
   hs.set_subtitles(wks, plot[ip], '', param_name, '', font_height=subtitle_font_height)

   # if len(plot)==2:
   if plot_speedup:
      hs.set_subtitles(wks, plot[ip+1], '', 'GPU speedup', '', font_height=subtitle_font_height)
    
#-------------------------------------------------------------------------------
# Add legend
#-------------------------------------------------------------------------------
lx,ly,vpx = 0.6,0.4,0.1
if plot_speedup: lx,ly,vpx = 0.2,0.5,0.05

lgres = ngl.Resources()
lgres.vpWidthF           = vpx
lgres.vpHeightF          = vpx
lgres.lgLabelFontHeightF = 0.012
lgres.lgLineLabelsOn     = False
lgres.lgLineThicknessF   = 8
lgres.lgLabelJust        = 'CenterLeft'
# lgres.lgMonoDashIndex    = True
lgres.lgDashIndexes      = dsh
lgres.lgLineColors       = clr

pid = ngl.legend_ndc(wks, len(group_name), group_name, lx, ly, lgres)  
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
pres = hs.setres_panel()
if len(param_list)>1:
   # pres.nglPanelYWhiteSpacePercent = 5
   # pres.nglPanelXWhiteSpacePercent = 5
   pres.nglPanelFigureStrings            = ['a','b','c','d','e','f','g','h']
   pres.nglPanelFigureStringsJust        = "TopLeft"
   pres.nglPanelFigureStringsFontHeightF = 0.015

if plot_speedup:
   layout = [len(param_list),2]
else:
   layout = [int(np.ceil(len(plot)/float(num_plot_col))),num_plot_col]

ngl.panel(wks,plot[0:len(plot)],layout,pres)
ngl.end()

hc.trim_png(fig_file)
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
