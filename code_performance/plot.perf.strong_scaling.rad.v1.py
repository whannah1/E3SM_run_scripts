#!/usr/bin/env python
import sys, os, fileinput, re, subprocess as sp, glob
import hapy_common as hc, hapy_setres as hs
import ngl, numpy as np, xarray as xr
name,nodes,groups,clr,dsh  = [],[],[],[],[]

fig_file = os.getenv('HOME')+'/E3SM/figs_performance/perf.strong_scaling.rad.v1'

#-------------------------------------------------------------------------------
# Specify groups of runs
#-------------------------------------------------------------------------------
nxrad = 4

# GPU - RRTMGP - w/ threads
group = []
group.append(f'E3SM.RAD-TIMING.GNUGPU.ne30pg2_ne30pg2.F-MMFXX-AQP1.RADNX_{nxrad}.NODES_16.NTHRDS_7.RRTMGP.00')
group.append(f'E3SM.RAD-TIMING.GNUGPU.ne30pg2_ne30pg2.F-MMFXX-AQP1.RADNX_{nxrad}.NODES_32.NTHRDS_7.RRTMGP.00')
group.append(f'E3SM.RAD-TIMING.GNUGPU.ne30pg2_ne30pg2.F-MMFXX-AQP1.RADNX_{nxrad}.NODES_64.NTHRDS_7.RRTMGP.00')
group.append(f'E3SM.RAD-TIMING.GNUGPU.ne30pg2_ne30pg2.F-MMFXX-AQP1.RADNX_{nxrad}.NODES_128.NTHRDS_7.RRTMGP.00')
group.append(f'E3SM.RAD-TIMING.GNUGPU.ne30pg2_ne30pg2.F-MMFXX-AQP1.RADNX_{nxrad}.NODES_256.NTHRDS_7.RRTMGP.00')
groups.append(group); clr.append('black'); dsh.append(0)

# GPU - RRTMGPXX - w/ threads
group = []
group.append(f'E3SM.RAD-TIMING.GNUGPU.ne30pg2_ne30pg2.F-MMFXX-AQP1.RADNX_{nxrad}.NODES_16.NTHRDS_7.RRTMGPXX.00')
group.append(f'E3SM.RAD-TIMING.GNUGPU.ne30pg2_ne30pg2.F-MMFXX-AQP1.RADNX_{nxrad}.NODES_32.NTHRDS_7.RRTMGPXX.00')
group.append(f'E3SM.RAD-TIMING.GNUGPU.ne30pg2_ne30pg2.F-MMFXX-AQP1.RADNX_{nxrad}.NODES_64.NTHRDS_7.RRTMGPXX.00')
group.append(f'E3SM.RAD-TIMING.GNUGPU.ne30pg2_ne30pg2.F-MMFXX-AQP1.RADNX_{nxrad}.NODES_128.NTHRDS_7.RRTMGPXX.00')
group.append(f'E3SM.RAD-TIMING.GNUGPU.ne30pg2_ne30pg2.F-MMFXX-AQP1.RADNX_{nxrad}.NODES_256.NTHRDS_7.RRTMGPXX.00')
groups.append(group); clr.append('green'); dsh.append(0)

# CPU - RRTMGPXX - no threads
group = []
group.append(f'E3SM.RAD-TIMING.GNUCPU.ne30pg2_ne30pg2.F-MMFXX-AQP1.RADNX_{nxrad}.NODES_16.NTHRDS_1.RRTMGPXX.00')
group.append(f'E3SM.RAD-TIMING.GNUCPU.ne30pg2_ne30pg2.F-MMFXX-AQP1.RADNX_{nxrad}.NODES_32.NTHRDS_1.RRTMGPXX.00')
group.append(f'E3SM.RAD-TIMING.GNUCPU.ne30pg2_ne30pg2.F-MMFXX-AQP1.RADNX_{nxrad}.NODES_64.NTHRDS_1.RRTMGPXX.00')
group.append(f'E3SM.RAD-TIMING.GNUCPU.ne30pg2_ne30pg2.F-MMFXX-AQP1.RADNX_{nxrad}.NODES_128.NTHRDS_1.RRTMGPXX.00')
group.append(f'E3SM.RAD-TIMING.GNUCPU.ne30pg2_ne30pg2.F-MMFXX-AQP1.RADNX_{nxrad}.NODES_256.NTHRDS_1.RRTMGPXX.00')
groups.append(group); clr.append('blue'); dsh.append(0)


#-------------------------------------------------------------------------------
# parse case names to determine node count
#-------------------------------------------------------------------------------
node_list_all = []
for case_list in groups:
   for case in case_list:
      params = [p.split('_') for p in case.split('.')]
      for p in params:
         if p[0]=='NODES': node_list_all.append(float(p[1]))

#-------------------------------------------------------------------------------
# Set which parameter to plot
#-------------------------------------------------------------------------------
param_list = []
# param_list.append('Throughput')
# param_list.append('physics_fraction')
# param_list.append('Run Time    :')
# param_list.append('ATM Run Time')
# param_list.append('\"a:crm\"')
# param_list.append('a:CAM_run3')
# param_list.append('a:CAM_run1')
# param_list.append('a:radiation')
# param_list.append('a:rad_rrtmgp_run_sw')
param_list.append('a:rad_fluxes_lw')

#-------------------------------------------------------------------------------
# setup plot stuff
#-------------------------------------------------------------------------------
# num_param = len(param)

if 'dsh' not in vars() or dsh==[]: dsh = np.zeros(num_case)

wkres = ngl.Resources()
npix=1024;wkres.wkWidth,wkres.wkHeight  = npix,npix
wks = ngl.open_wks('png',fig_file,wkres)
plot = []

res = hs.res_xy()
res.vpHeightF = 0.4
res.tmXBMinorOn  = True
res.tmYLMinorOn  = True
res.xyMarkLineMode = 'MarkLines'
res.xyMarker = 16
res.xyMarkerSizeF = 0.008
res.xyLineThicknessF = 12

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

# Set tick mark labels based on unique node counts
num_nodes = []
for n in node_list_all:
   if n not in num_nodes: num_nodes.append(n)

res.tmXBMode = 'Explicit'
res.tmXBValues = num_nodes
res.tmXBLabels = num_nodes


#-------------------------------------------------------------------------------
# make sure all logs are unzipped
#-------------------------------------------------------------------------------
max_case_len = 0
for case_list in groups:
   for case in case_list:
      timing_dir = os.getenv('HOME')+f'/E3SM/Cases/{case}/timing'
      timing_stat_gz_path = f'{timing_dir}/*.gz'
      if len(glob.glob(timing_stat_gz_path))>0: os.system(f'gunzip {timing_stat_gz_path} ')
      # find max char len for case name
      if len(case)>max_case_len: max_case_len = len(case)

      ### copy files to folder for sharing
#       timing_stat_path = f'{timing_dir}/e3sm_timing*'
#       if len(glob.glob(timing_stat_path))>0:
#          # os.system(f'ls -1 {timing_stat_path} ')
#          tfiles = glob.glob(timing_stat_path)
#          for tfile in tfiles:
#             dst_file_name = tfile
#             if 'e3sm_timing_stats' in dst_file_name:
#                dst_file_name = dst_file_name.replace('e3sm_timing_stats',f'e3sm_timing_stats.{case}')
#             dst_file_name = dst_file_name.replace(f'/ccs/home/hannah6/E3SM/Cases/{case}/timing/','')
#             cmd = f'cp {tfile} ~/Research/E3SM/timing_data_for_mark/{dst_file_name}'
#             print(f'\n{hc.tcolor.CYAN}{cmd}{hc.tcolor.ENDC}')
#             os.system(cmd)
# exit()


#-------------------------------------------------------------------------------
# Loop through parameters and cases
#-------------------------------------------------------------------------------
for param in param_list :
   print()
   group_data_list = []
   file_list = []
   for case_list in groups:
      print()
      data_list = []
      for c,case in enumerate(case_list):
         # print()
         timing_dir = os.getenv('HOME')+f'/E3SM/Cases/{case}/timing'

         case_name_fmt = hc.tcolor.CYAN+f'{case:{max_case_len}}'+hc.tcolor.ENDC

         # check that the timing files exist
         timing_file_path = f'{timing_dir}/*'

         # check if files exist
         if len(glob.glob(timing_file_path))==0:
            print(f'    {case_name_fmt}  No files!')
            data_list.append(np.nan)
            continue


         tparam = param
         if param=='physics_fraction': tparam = 'a:CAM_run'
         #-------------------------------------------------------------------------
         # grep for the appendropriate line in the stat files
         cmd = 'grep  \''+tparam+f'\'  {timing_dir}/*'
         proc = sp.Popen(cmd, stdout=sp.PIPE, shell=True, universal_newlines=True)
         (msg, err) = proc.communicate()
         msg = msg.split('\n')

         stat_file = msg[0].split(':')[0]

         #-------------------------------------------------------------------------
         # Clean up message but don't print yet
         for m in range(len(msg)):
            line = msg[m]
            line = line.replace(timing_dir+'/','')
            line = line.replace(f'e3sm_timing.{case}.','e3sm_timing        ')
            line = line.replace('e3sm_timing_stats.'  ,'e3sm_timing_stats  ')
            # Add case name
            if line!='': line = case_name_fmt+' '+line
            line = line.replace(f'e3sm_timing      ','')
            msg[m] = line
         #-------------------------------------------------------------------------
         # print stat file header with indentation
         if 'a:' in tparam :
            head = sp.check_output(['head',stat_file],universal_newlines=True).split('\n')
            for line in head:
               if 'walltotal' in line:
                  indent = len(msg[0].split(':')[0])+1
                  line = ' '*indent+line
                  hline = line
                  # Get rid of some dead space
                  line = line.replace('name        ','name')
                  print(hline)
                  break
         #-------------------------------------------------------------------------
         # set up character indices for color
         if 'a:' in tparam:
            n1 = hline.find('walltotal')    +len('walltotal')
            n2 = hline.find('wallmax')      +len('wallmax')
            n3 = hline.find('wallmax')      +len('wallmax (proc   thrd  )')
            n4 = hline.find('wallmin')      +len('wallmin')
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
            if param=='physics_fraction':
               if frac_cnt==0: print()
               if any([s in line for s in ['a:CAM_run1','a:CAM_run2','a:CAM_run3']]):
                  tot_cost += float(line[n1:n2])
               if any([s in line for s in ['a:CAM_run1','a:CAM_run2']]):
                  phys_cost += float(line[n1:n2])
               frac_cnt += 1
               if frac_cnt==4:
                  data.append( phys_cost / tot_cost )
                  dpos.append(float(c))
                  frac_cnt,phys_cost,tot_cost = 0,0,0
            else:
               data.append(float(line[n1:n2]))
               # dpos.append(float(c))
            if 'a:' in tparam :
               line = line[:n1] \
                    +hc.tcolor.CYAN  +line[n1:n2]+hc.tcolor.CYAN +line[n2:n3] \
                    +hc.tcolor.GREEN +line[n3:n4]+hc.tcolor.ENDC +line[n4:]
               # Get rid of some dead space
               line = line.replace('        ','')
            else:
               line = line[:n1] \
                    +hc.tcolor.GREEN +line[n1:n2]+hc.tcolor.ENDC \
                    +line[n2:]
               # Print conversion to min aand hours for specific params
               offset = len(hc.tcolor.GREEN)
               if tparam=='Run Time    :' and line[n1+offset:n2+offset]!='' :
                  sec = float( line[n1+offset:n2+offset] )
                  line = line+'  ('+hc.tcolor.GREEN+f'{sec/60:.2f}'     +hc.tcolor.ENDC+' min)'
                  line = line+'  ('+hc.tcolor.GREEN+f'{sec/60/60:.2f}'  +hc.tcolor.ENDC+' hour)'
            # print the line
            print('    '+line)

         data = np.array(data)
         avg = np.average(data)

         data_list.append(avg)

         # print(f'average: {hc.tcolor.GREEN}{avg:6.3}{hc.tcolor.ENDC}')

      group_data_list.append(data_list)

      # print()
      # print(group_data_list)
      # print()


   #----------------------------------------------------------------------------
   # plot timing data

   # res.tiXAxisString = xvar
   # res.tiYAxisString = yvar

   group_data_list_flat = [item for sublist in group_data_list for item in sublist]


   # px = xr.DataArray(np.array(dpos_list)).stack().values
   py = xr.DataArray(np.array(group_data_list_flat)).stack().values

   mag = np.max(node_list_all) - np.min(node_list_all)
   res.trXMinF = np.min(node_list_all) - 0.01*mag
   res.trXMaxF = np.max(node_list_all) + 0.1*mag

   tpy = np.ma.masked_invalid(py)
   mag = np.max(tpy) - np.min(tpy)
   res.trYMinF = np.min(tpy)   - 0.1*np.min(tpy)
   res.trYMaxF = np.max(tpy)   + 0.1*np.max(tpy)

   for g,data_list in enumerate(group_data_list):

      case_list = groups[g]

      # figure out node count for each point
      node_list = []
      for case in case_list:
         params = [p.split('_') for p in case.split('.')]
         for p in params:
            if p[0]=='NODES': node_list.append(float(p[1]))

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
         msg+= f'    # nodes: {hc.tcolor.GREEN}{int(px[c]):6}{hc.tcolor.ENDC}'
         msg+= f'    Throughput: {hc.tcolor.GREEN}{    py[c] :6.2f}{hc.tcolor.ENDC}'
         print(msg)
      #-------------------------------------------------
      #-------------------------------------------------

      px = np.where(np.isnan(py), np.nan, px)
      px = np.ma.masked_invalid(np.stack(px))
      py = np.ma.masked_invalid(np.stack(py))

      res.tiXAxisString = '# Nodes'
      # res.tiYAxisString = '[sypd]'

      res.xyMarkerColor = clr[g]
      res.xyLineColor   = clr[g]
      res.xyDashPattern = dsh[g]

      tplot = ngl.xy(wks, px, py, res)

      if g==0:
         plot.append( tplot  )
      else:
         ngl.overlay( plot[len(plot)-1], tplot )

   # # Add horizontal lines
   # ngl.overlay( plot[len(plot)-1], ngl.xy(wks,[0,0],[-1e8,1e8],lres) )
   # ngl.overlay( plot[len(plot)-1], ngl.xy(wks,[-1e8,1e8],[0,0],lres) )

   param_name = ''
   if param=='Throughput':       param_name = 'Overall Model Throughput [sypd]'
   if param=='ATM Run Time':     param_name = 'Atmosphere Model Throughput [sypd]'
   if param=='physics_fraction': param_name = 'Proportional Cost of Physics (excluding I/O)'

   subtitle_font_height = 0.025
   if len(param_list)==2: subtitle_font_height = 0.015
   hs.set_subtitles(wks, plot[len(plot)-1], '', param_name, '', font_height=subtitle_font_height)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
pres = hs.setres_panel()
if len(param_list)>1:
   # pres.nglPanelYWhiteSpacePercent = 5
   # pres.nglPanelXWhiteSpacePercent = 5
   pres.nglPanelFigureStrings            = ['a','b','c','d','e','f','g','h']
   pres.nglPanelFigureStringsJust        = "TopLeft"
   pres.nglPanelFigureStringsFontHeightF = 0.015

layout = [1,len(plot)]
ngl.panel(wks,plot[0:len(plot)],layout,pres)
ngl.end()

hc.trim_png(fig_file.replace(os.getenv('PWD')+'/',''))
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------