#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm4310'
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC3' # 2025-scidac-deep-atmos-test => master @ Apr 21 + oksanaguba:og/da 

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

queue = 'regular'

# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',10,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365-32,0,'3:00:00'
stop_opt,stop_n,resub,walltime = 'ndays',365,10-1,'4:00:00'

compset='F20TR'
grid = f'ne30pg2_r05_IcoswISC30E3r5'
num_nodes = 32


# add_case(prefix='2025-SCIDAC-NCT-test-00',grid=grid,compset=compset,NCT='0') # control
# add_case(prefix='2025-SCIDAC-NCT-test-00',grid=grid,compset=compset,NCT='1') # enable deep atmos mode

add_case(prefix='2025-SCIDAC-NCT-test-00',grid=grid,compset=compset,NHS='off',NCT='off')
add_case(prefix='2025-SCIDAC-NCT-test-00',grid=grid,compset=compset,NHS='on', NCT='off')
add_case(prefix='2025-SCIDAC-NCT-test-00',grid=grid,compset=compset,NHS='on', NCT='on')

# print(opt_list[0])
# exit()

# case_list.append('NHS-on' if GNHS else 'NHS-off')
# case_list.append('NCT-on' if GNCT else 'NCT-off')

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(opts):
   global compset, grid, num_nodes

   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix','compset','grid']:
         case_list.append(val)
      # elif key in ['num_nodes']:
      #    continue
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            case_list.append(f'{key}_{val:g}')

   case = '.'.join(case_list)

   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
   #----------------------------------------------------------------------------
   print(f'\n  case : {case}\n')
   #----------------------------------------------------------------------------
   # exit()
   # return
   #----------------------------------------------------------------------------
   max_mpi_per_node,atm_nthrds  = 128,1 
   atm_ntasks = max_mpi_per_node*num_nodes
   case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
   #------------------------------------------------------------------------------------------------
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --mach pm-cpu --pecount {atm_ntasks}x{atm_nthrds} '
      cmd += f' --case {case} --handle-preexisting-dirs u '
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --compset {compset} --res {grid} '
      cmd += f' --project {acct} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config :
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------
      cpp_opt = ''
      # if opts['NCT']=='0': cpp_opt += f' -Dxxx'
      # if opts['NCT']=='1': cpp_opt += f' -DHOMMEDA'
      if opts['NCT']=='on': cpp_opt += f' -DHOMMEDA'
      if cpp_opt != '' :
         cmd  = f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS'
         cmd += f' --val \" -cppdefs \' {cpp_opt} \'  \" '
         run_cmd(cmd)
      #-------------------------------------------------------------------------
      run_cmd('./xmlchange --id CAM_CONFIG_OPTS --append --val=\'-cosp\' ')
      #-------------------------------------------------------------------------
      run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #----------------------------------------------------------------------------
      # Namelist options
      nfile = 'user_nl_eam'
      file = open(nfile,'w')
      if opts['NHS']=='on':
         file.write(f' theta_hydrostatic_mode = .false. \n')
         file.write(f' tstep_type = 9 \n')
      file.write(' nhtfrq    = 0,-3,-3 \n')
      file.write(' mfilt     = 1,8,8 \n')
      # file.write(" avgflag_pertape = 'A','A','I' \n")
      file.write(" fincl1 = 'Z3','CLDLIQ','CLDICE','BUTGWSPEC'")
      file.write(         ",'Uzm','Vzm','Wzm','THzm','VTHzm','WTHzm','UVzm','UWzm','THphys','PSzm'")
      file.write(         ",'CLDHGH_CAL','CLDLOW_CAL','CLDMED_CAL','CLD_MISR','CLDTOT_CAL','CLMODIS'")
      file.write(         ",'CLDTOT_ISCCP','MEANCLDALB_ISCCP','MEANPTOP_ISCCP','CLD_CAL','FISCCP1_COSP'")
      file.write(         ",'CLDTOT_CAL_LIQ','CLDTOT_CAL_ICE','CLDTOT_CAL_UN'")
      file.write(         ",'CLDHGH_CAL_LIQ','CLDHGH_CAL_ICE','CLDHGH_CAL_UN'")
      file.write(         ",'CLDMED_CAL_LIQ','CLDMED_CAL_ICE','CLDMED_CAL_UN'")
      file.write(         ",'CLDLOW_CAL_LIQ','CLDLOW_CAL_ICE','CLDLOW_CAL_UN'")
      file.write(         ",'CLD_CAL_TMPLIQ','CLD_CAL_TMPICE'")
      file.write(         ",'CLWMODIS','CLIMODIS'")
      file.write("\n")
      file.write(" fincl2    = 'PS','TS','PSL'")
      file.write(             ",'PRECT','TMQ'")
      file.write(             ",'LHFLX','SHFLX'")                     # surface fluxes
      file.write(             ",'FSNT','FLNT'")                       # Net TOM heating rates
      file.write(             ",'FLNS','FSNS'")                       # Surface rad for total column heating
      file.write(             ",'FSNTC','FLNTC'")                     # clear sky heating rates for CRE
      file.write(             ",'LWCF','SWCF'")                       # cloud radiative foricng
      file.write(             ",'TGCLDLWP','TGCLDIWP'")               # cloud water path
      file.write(             ",'TUQ','TVQ'")                         # vapor transport
      file.write(             ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model level
      file.write(             ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
      file.write(             ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
      file.write(             ",'Z300:I','Z500:I'")
      file.write(             ",'OMEGA850:I','OMEGA500:I'")
      file.write('\n')
      file.write(f' phys_grid_ctem_zm_nbas = 120 \n') # Number of basis functions used for TEM
      file.write(f' phys_grid_ctem_za_nlat = 90 \n') # Number of latitude points for TEM
      file.write(f' phys_grid_ctem_nfreq = -1 \n') # Frequency of TEM diagnostic calculations (neg => hours)
      # if 'beres' in opts.keys():
      #    if opts['beres']=='old':    file.write(f' use_gw_convect_old           = .true. \n')
      #    if opts['beres']=='new':    file.write(f' use_gw_convect_old           = .false. \n')
      # if 'gweff'     in opts.keys(): file.write(f' effgw_beres                  = {opts["gweff"]} \n')
      # if 'cfrac'     in opts.keys(): file.write(f' gw_convect_hcf               = {opts["cfrac"]} \n')
      # if 'hdpth'     in opts.keys(): file.write(f' hdepth_scaling_factor        = {opts["hdpth"]} \n')
      # if 'hdpth_min' in opts.keys(): file.write(f' gw_convect_hdepth_min        = {opts["hdpth_min"]} \n')
      # if 'stspd_min' in opts.keys(): file.write(f' gw_convect_storm_speed_min   = {opts["stspd_min"]} \n')
      # if 'plev_srcw' in opts.keys(): file.write(f' gw_convect_plev_src_wind     = {opts["plev_srcw"]*1e2} \n')
      file.close()
      #----------------------------------------------------------------------------
      # file=open('user_nl_elm','w')
      # file.write(v3HR_lnd_opts)
      # file.close()
      #-------------------------------------------------------------------------
      if not continue_run: run_cmd(f'./xmlchange --file env_run.xml RUN_STARTDATE=1985-01-01')
      #-------------------------------------------------------------------------
      # Set some run-time stuff
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      #-------------------------------------------------------------------------
      if     continue_run: run_cmd('./xmlchange CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------------------------
      # Submit the run
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
