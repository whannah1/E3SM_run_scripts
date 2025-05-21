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

acct = 'e3sm'
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC3' # master @ April 16 2025

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

# queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',1,0,'0:30:00'
# queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',32,0,'1:30:00' # 75 nodes
# queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',73,5*2-1,'4:00:00' # 75 nodes
# queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',365,2-1,'12:00:00' # 75 nodes
# queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',365,0,'7:00:00' # 256 nodes
# queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',73,5-1,'2:00:00' # 256 nodes

stop_opt,stop_n,resub,walltime = 'ndays',32,0,'1:00:00' # LR - 32 nodes
# stop_opt,stop_n,resub,walltime = 'ndays',365,0,'4:00:00' # LR - 32 nodes


# compset ='F20TR'
# grid = f'ne120pg2_r025_RRSwISC6to18E3r5'
# num_nodes = 75

compset='F2010'
grid = f'ne30pg2_r05_IcoswISC30E3r5'
num_nodes = 32

# topo_file = '/global/cfs/cdirs/e3sm/inputdata/atm/cam/topo/USGS-gtopo30_ne120np4pg2_x6t_forOroDrag.c20241019.nc'
# topo_file = '/lcrc/group/e3sm/data/inputdata/atm/cam/topo/USGS-gtopo30_ne120np4pg2_x6t_forOroDrag.c20241019.nc'
topo_file = '/lcrc/group/e3sm/data/inputdata/atm/cam/topo/USGS-gtopo30_ne30np4pg2_x6t-SGH_forOroDrag.c20241001.nc'

# land_init_file = '/pscratch/sd/w/wlin/inputdata/20231130.v3b02-icos_trigrid_top_bgc.IcoswISC30E3r5.chrysalis.fnsp.elm.r.0251-01-01-00000.nc'
# land_init_file = '/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/initdata_map/elmi.CNPRDCTCBCTOP.r025_RRSwISC6to18E3r5.1985.nc'
land_init_file = '/lcrc/group/e3sm/data/inputdata/lnd/clm2/initdata_map/20250119_CBGCv3.r05.chrysalis.I1850WCCNPPHSWFMCROP.rgsp.elm.r.0601-01-01-00000.nc'

# add_case(prefix='2025-v3HR-QBO-00', beres='old', gweff=0.1, cfrac=2.5, hdpth=0.50) # control
# add_case(prefix='2025-v3HR-QBO-00', beres='new', gweff=0.1, cfrac=2.5, hdpth=1.00) # 
# add_case(prefix='2025-v3HR-QBO-00', beres='off' ) # 

# restart with more output to check tendencies
# add_case(prefix='2025-v3HR-QBO-01', beres='old', gweff=0.1, cfrac=2.5, hdpth=0.50) # control
# add_case(prefix='2025-v3HR-QBO-01', beres='off' ) # 
# add_case(prefix='2025-v3HR-QBO-01', beres='off', orogw='off', frontgw='off' )

add_case(prefix='2025-v3HR-QBO-01', orogw='old') # control
add_case(prefix='2025-v3HR-QBO-01', orogw='new') # control

# add_case(prefix='2025-v3HR-QBO-00', beres='new', gweff=0.1, cfrac=2.5, hdpth=1.00) # ???
# add_case(prefix='2025-v3HR-QBO-00', beres='new', gweff=0.1, cfrac=5.0, hdpth=1.00) # ???
# add_case(prefix='2025-v3HR-QBO-00', beres='new', gweff=0.1, cfrac=2.5, hdpth=1.00) # ???

#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
def main(opts):
   global compset, grid, num_nodes

   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix']:
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

   print(f'\n  case : {case}\n')

   #----------------------------------------------------------------------------
   # max_mpi_per_node,atm_nthrds  = 128,1
   max_mpi_per_node,atm_nthrds  = 96,1
   atm_ntasks = max_mpi_per_node*num_nodes
   # case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
   case_root = f'/lcrc/group/e3sm/ac.whannah/scratch/chrys/{case}'
   #------------------------------------------------------------------------------------------------
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      # cmd += f' --mach pm-cpu '
      cmd += f' --pecount {atm_ntasks}x{atm_nthrds} '
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
      #-------------------------------------------------------------------------
      # ice_ntasks = 18 * max_mpi_per_node
      # ocn_ntasks =  6 * max_mpi_per_node
      # lnd_ntasks = atm_ntasks - ice_ntasks
      # ocn_rootpe = atm_ntasks - ocn_ntasks

      # run_cmd(f'./xmlchange NTASKS_ICE="{ice_ntasks}" ')
      # run_cmd(f'./xmlchange NTASKS_OCN="{ocn_ntasks}" ')
      # run_cmd(f'./xmlchange NTASKS_LND="{lnd_ntasks}" ')
      # run_cmd(f'./xmlchange NTASKS_ROF="{lnd_ntasks}" ')

      # run_cmd(f'./xmlchange OCN_ROOTPE="{ocn_rootpe}"')
      # run_cmd(f'./xmlchange LND_ROOTPE="{ice_ntasks}"')
      # run_cmd(f'./xmlchange ROF_ROOTPE="{ice_ntasks}"')
      #-------------------------------------------------------------------------
      # run_cmd('./xmlchange --id CAM_CONFIG_OPTS --append --val=\'-cosp\' ')
      #-------------------------------------------------------------------------
      run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #-------------------------------------------------------------------------
      # use_gw_front  # frontal GWD
      # use_od_bl     # flow-blocking drag
      # use_od_fd     # turbulent orographic form drag
      # use_od_ls     # nonlinear oGWD
      # use_od_ss     # small-scale GWD
      #-------------------------------------------------------------------------
      # Namelist options
      nfile = 'user_nl_eam'
      file = open(nfile,'w') 
      # file.write(v3HR_atm_opts)
      file.write(v3LR_atm_opts)
      if 'beres' in opts.keys():
         if opts['beres']=='old':    file.write(f' use_gw_convect_old           = .true. \n')
         if opts['beres']=='new':    file.write(f' use_gw_convect_old           = .false. \n')
         if opts['beres']=='off':    file.write(f' use_gw_convect               = .false. \n')
      if 'orogw'     in opts.keys():
         if opts['orogw']=='off':
            file.write(f' use_od_bl                  = .false. \n')
            file.write(f' use_od_ls                  = .false. \n')
            file.write(f' use_od_ss                  = .false. \n')
            file.write(f' use_od_fd                  = .false. \n')
            file.write(f' do_tms                     = .true. \n')
         if opts['orogw']=='old':
            file.write(f' use_gw_oro                 = .true. \n')
            file.write(f' do_tms                     = .true. \n')
            file.write(f' use_od_bl                  = .false. \n')
            file.write(f' use_od_ls                  = .false. \n')
            file.write(f' use_od_ss                  = .false. \n')
            file.write(f' use_od_fd                  = .false. \n')
         if opts['orogw']=='new':
            file.write(f' use_gw_oro                 = .false. \n')
            file.write(f' do_tms                     = .false. \n')
            file.write(f' use_od_bl                  = .true. \n')
            file.write(f' use_od_ls                  = .true. \n')
            file.write(f' use_od_ss                  = .true. \n')
            file.write(f' use_od_fd                  = .true. \n')
      if 'frontgw'   in opts.keys(): 
         if opts['frontgw']=='off':  file.write(f' use_gw_front                 = .false. \n')
      if 'gweff'     in opts.keys(): file.write(f' effgw_beres                  = {opts["gweff"]} \n')
      if 'cfrac'     in opts.keys(): file.write(f' gw_convect_hcf               = {opts["cfrac"]} \n')
      if 'hdpth'     in opts.keys(): file.write(f' hdepth_scaling_factor        = {opts["hdpth"]} \n')
      # if 'hdpth_min' in opts.keys(): file.write(f' gw_convect_hdepth_min        = {opts["hdpth_min"]} \n')
      # if 'stspd_min' in opts.keys(): file.write(f' gw_convect_storm_speed_min   = {opts["stspd_min"]} \n')
      # if 'plev_srcw' in opts.keys(): file.write(f' gw_convect_plev_src_wind     = {opts["plev_srcw"]*1e2} \n')
      file.close()
      #-------------------------------------------------------------------------
      file=open('user_nl_elm','w')
      file.write(v3HR_lnd_opts)
      file.close()
      #-------------------------------------------------------------------------
      run_cmd(f'./xmlchange --file env_run.xml RUN_STARTDATE=1985-01-01')
      #-------------------------------------------------------------------------
      ### reset tasks to change number of nodes
      # run_cmd(f'./xmlchange NTASKS_ATM="{atm_ntasks}" ')
      # run_cmd(f'./xmlchange NTASKS_CPL="{atm_ntasks}" ')
      # run_cmd(f'./xmlchange NTASKS_OCN="{atm_ntasks}" ')
      # run_cmd(f'./xmlchange NTASKS_WAV="{atm_ntasks}" ')
      # run_cmd(f'./xmlchange NTASKS_GLC="{atm_ntasks}" ')
      # run_cmd(f'./xmlchange NTASKS_ICE="{atm_ntasks}" ')
      # run_cmd(f'./xmlchange NTASKS_ROF="{atm_ntasks}" ')
      # run_cmd(f'./xmlchange NTASKS_LND="{atm_ntasks}" ')
      # run_cmd(f'./xmlchange NTASKS_ESP="{atm_ntasks}" ')
      # run_cmd(f'./xmlchange NTASKS_IAC="{atm_ntasks}" ')
      # run_cmd(f'./xmlchange BUILD_COMPLETE=TRUE ')
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
'''
          'CLMODIS','FISCCP1_COSP',
          'CLDHGH_CAL','CLDLOW_CAL','CLDMED_CAL','CLD_MISR','CLDTOT_CAL',
          'CLDTOT_ISCCP','MEANCLDALB_ISCCP','MEANPTOP_ISCCP','CLD_CAL',
          'CLDTOT_CAL_LIQ','CLDTOT_CAL_ICE','CLDTOT_CAL_UN',
          'CLDHGH_CAL_LIQ','CLDHGH_CAL_ICE','CLDHGH_CAL_UN',
          'CLDMED_CAL_LIQ','CLDMED_CAL_ICE','CLDMED_CAL_UN',
          'CLDLOW_CAL_LIQ','CLDLOW_CAL_ICE','CLDLOW_CAL_UN',
          'CLWMODIS','CLIMODIS', 
          'CLD_CAL_TMPLIQ','CLD_CAL_TMPICE',
          'O3_2DTDA_trop','O3_2DTDB_trop','O3_2DTDD_trop','O3_2DTDE_trop','O3_2DTDI_trop','O3_2DTDL_trop',
          'O3_2DTDN_trop','O3_2DTDO_trop','O3_2DTDS_trop','O3_2DTDU_trop','O3_2DTRE_trop','O3_2DTRI_trop',
          'O3_SRF','NO_2DTDS','NO_TDLgt','NO2_2DTDD','NO2_2DTDS','NO2_TDAcf','CO_SRF','TROPE3D_P','TROP_P',
          'dst_a1DDF','dst_a3DDF','dst_c1DDF','dst_c3DDF','dst_a1SFWET','dst_a3SFWET','dst_c1SFWET','dst_c3SFWET',
          'dst_a1SF','dst_a3SF',
          'CDNUMC','SFDMS','so4_a1_sfgaex1','so4_a2_sfgaex1','so4_a3_sfgaex1','so4_a5_sfgaex1','soa_a1_sfgaex1',
          'soa_a2_sfgaex1','soa_a3_sfgaex1','GS_soa_a1','GS_soa_a2','GS_soa_a3','AQSO4_H2O2','AQSO4_O3',
          'SFSO2','SO2_CLXF','SO2','DF_SO2','AQ_SO2','GS_SO2','WD_SO2','ABURDENSO4_STR','ABURDENSO4_TRO',
          'ABURDENSO4','ABURDENBC','ABURDENDUST','ABURDENMOM','ABURDENPOM','ABURDENSEASALT',
          'ABURDENSOA','AODSO4_STR','AODSO4_TRO',
          'EXTINCT','AODABS','AODABSBC','Mass_bc_srf',
          'Mass_dst_srf','Mass_mom_srf','Mass_ncl_srf','Mass_pom_srf','Mass_so4_srf','Mass_soa_srf','Mass_bc_850',
          'Mass_dst_850','Mass_mom_850','Mass_ncl_850','Mass_pom_850','Mass_so4_850','Mass_soa_850','Mass_bc_500',
          'Mass_dst_500','Mass_mom_500','Mass_ncl_500','Mass_pom_500','Mass_so4_500','Mass_soa_500','Mass_bc_330',
          'Mass_dst_330','Mass_mom_330','Mass_ncl_330','Mass_pom_330','Mass_so4_330','Mass_soa_330','Mass_bc_200',
          'Mass_dst_200','Mass_mom_200','Mass_ncl_200','Mass_pom_200','Mass_so4_200','Mass_soa_200',
          'O3_2DTDD','O3_2DCIP','O3_2DCIL','CO_2DTDS','CO_2DTDD','CO_2DCEP','CO_2DCEL','NO_2DTDD',
          'SAODVIS',
'''

v3LR_atm_opts = f'''

 empty_htapes = .true.

 avgflag_pertape = 'A','A','A','I','I','I'
 nhtfrq = 0,-24,-6,-3,-1,0
 mfilt  = 1,30,120,240,720,1

 fincl1 = 'AODALL','AODBC','AODDUST','AODPOM','AODSO4','AODSOA','AODSS','AODVIS',
          'CLDLOW','CLDMED','CLDHGH','CLDTOT',
          'FLDS','FLNS','FLNSC','FLNT','FLUT','FLNTC',
          'FLUTC','FSDS','FSDSC','FSNS','FSNSC','FSNT','FSNTOA','FSNTOAC','FSNTC',
          'ICEFRAC','LANDFRAC','LWCF','OCNFRAC','OMEGA','PRECC','PRECL','PRECSC','PRECSL','PS','PSL','Q',
          'QFLX','QREFHT','RELHUM','SCO','SHFLX','LHFLX','SOLIN','SWCF','T','TAUX','TAUY','TCO','O3',
          'TGCLDLWP','TMQ','TREFHT','TREFMNAV','TREFMXAV','TS','U','U10','V','Z3','CLDICE','CLDLIQ','H2OLNZ',
          'PHIS','CLOUD','TGCLDIWP','TGCLDCWP','AREL',
          'PUTEND','FUTGWSPEC','BUTGWSPEC','UTGWORO',
          'Uzm','Vzm','Wzm','THzm','VTHzm','WTHzm','UVzm','UWzm','THphys','PSzm'
 
 phys_grid_ctem_zm_nbas = 120
 phys_grid_ctem_za_nlat = 90
 phys_grid_ctem_nfreq = -1

 bnd_topo='{topo_file}'

 ! Dust emission cap
 dstemislimitswitch = .true.

'''
#---------------------------------------------------------------------------------------------------
v3HR_atm_opts = f'''
 cosp_lite = .true.

 empty_htapes = .true.

 avgflag_pertape = 'A','A','A','I','I','I'
 nhtfrq = 0,-24,-6,-3,-1,0
 mfilt  = 1,30,120,240,720,1

 fincl1 = 'AODALL','AODBC','AODDUST','AODPOM','AODSO4','AODSOA','AODSS','AODVIS',
          'CLDLOW','CLDMED','CLDHGH','CLDTOT',
          'CLDHGH_CAL','CLDLOW_CAL','CLDMED_CAL','CLD_MISR','CLDTOT_CAL',
          'CLMODIS','FISCCP1_COSP','FLDS','FLNS','FLNSC','FLNT','FLUT',
          'FLUTC','FSDS','FSDSC','FSNS','FSNSC','FSNT','FSNTOA','FSNTOAC','FSNTC',
          'ICEFRAC','LANDFRAC','LWCF','OCNFRAC','OMEGA','PRECC','PRECL','PRECSC','PRECSL','PS','PSL','Q',
          'QFLX','QREFHT','RELHUM','SCO','SHFLX','SOLIN','SWCF','T','TAUX','TAUY','TCO',
          'TGCLDLWP','TMQ','TREFHT','TREFMNAV','TREFMXAV','TS','U','U10','V','Z3',
          'dst_a1DDF','dst_a3DDF','dst_c1DDF','dst_c3DDF','dst_a1SFWET','dst_a3SFWET','dst_c1SFWET','dst_c3SFWET',
          'O3','LHFLX',
          'O3_2DTDA_trop','O3_2DTDB_trop','O3_2DTDD_trop','O3_2DTDE_trop','O3_2DTDI_trop','O3_2DTDL_trop',
          'O3_2DTDN_trop','O3_2DTDO_trop','O3_2DTDS_trop','O3_2DTDU_trop','O3_2DTRE_trop','O3_2DTRI_trop',
          'O3_SRF','NO_2DTDS','NO_TDLgt','NO2_2DTDD','NO2_2DTDS','NO2_TDAcf','CO_SRF','TROPE3D_P','TROP_P',
          'CDNUMC','SFDMS','so4_a1_sfgaex1','so4_a2_sfgaex1','so4_a3_sfgaex1','so4_a5_sfgaex1','soa_a1_sfgaex1',
          'soa_a2_sfgaex1','soa_a3_sfgaex1','GS_soa_a1','GS_soa_a2','GS_soa_a3','AQSO4_H2O2','AQSO4_O3',
          'SFSO2','SO2_CLXF','SO2','DF_SO2','AQ_SO2','GS_SO2','WD_SO2','ABURDENSO4_STR','ABURDENSO4_TRO',
          'ABURDENSO4','ABURDENBC','ABURDENDUST','ABURDENMOM','ABURDENPOM','ABURDENSEASALT',
          'ABURDENSOA','AODSO4_STR','AODSO4_TRO',
          'EXTINCT','AODABS','AODABSBC','CLDICE','CLDLIQ','CLD_CAL_TMPLIQ','CLD_CAL_TMPICE','Mass_bc_srf',
          'Mass_dst_srf','Mass_mom_srf','Mass_ncl_srf','Mass_pom_srf','Mass_so4_srf','Mass_soa_srf','Mass_bc_850',
          'Mass_dst_850','Mass_mom_850','Mass_ncl_850','Mass_pom_850','Mass_so4_850','Mass_soa_850','Mass_bc_500',
          'Mass_dst_500','Mass_mom_500','Mass_ncl_500','Mass_pom_500','Mass_so4_500','Mass_soa_500','Mass_bc_330',
          'Mass_dst_330','Mass_mom_330','Mass_ncl_330','Mass_pom_330','Mass_so4_330','Mass_soa_330','Mass_bc_200',
          'Mass_dst_200','Mass_mom_200','Mass_ncl_200','Mass_pom_200','Mass_so4_200','Mass_soa_200',
          'O3_2DTDD','O3_2DCIP','O3_2DCIL','CO_2DTDS','CO_2DTDD','CO_2DCEP','CO_2DCEL','NO_2DTDD',
          'FLNTC','SAODVIS',
          'H2OLNZ',
          'dst_a1SF','dst_a3SF',
          'PHIS','CLOUD','TGCLDIWP','TGCLDCWP','AREL',
          'CLDTOT_ISCCP','MEANCLDALB_ISCCP','MEANPTOP_ISCCP','CLD_CAL',
          'CLDTOT_CAL_LIQ','CLDTOT_CAL_ICE','CLDTOT_CAL_UN',
          'CLDHGH_CAL_LIQ','CLDHGH_CAL_ICE','CLDHGH_CAL_UN',
          'CLDMED_CAL_LIQ','CLDMED_CAL_ICE','CLDMED_CAL_UN',
          'CLDLOW_CAL_LIQ','CLDLOW_CAL_ICE','CLDLOW_CAL_UN',
          'CLWMODIS','CLIMODIS', 
          'PUTEND','FUTGWSPEC','BUTGWSPEC','UTGWORO',
          'Uzm','Vzm','Wzm','THzm','VTHzm','WTHzm','UVzm','UWzm','THphys','PSzm'
 

 ! fincl2 = 'PS', 'FLUT','PRECT','U200','V200','U850','V850','TCO','SCO','TREFHTMN:M','TREFHTMX:X','TREFHT','QREFHT'
 ! fincl3 = 'PS', 'PSL','PRECT','TUQ','TVQ','UBOT','VBOT','TREFHT','FLUT','OMEGA500','TBOT','U850','V850','U200','V200','T200','T500','Z700'
 ! fincl4 = 'PRECT'
 ! fincl5 = 'O3_SRF'
 ! fincl6 = 'CO_2DMSD','NO2_2DMSD','NO_2DMSD','O3_2DMSD','O3_2DMSD_trop'

 phys_grid_ctem_zm_nbas = 120
 phys_grid_ctem_za_nlat = 90
 phys_grid_ctem_nfreq = -1

 ! -- chemUCI settings ------------------
 history_chemdyg_summary = .true.
 history_gaschmbudget_2D = .false.
 history_gaschmbudget_2D_levels = .false.
 history_gaschmbudget_num = 6 !! no impact if  history_gaschmbudget_2D = .false.

 ! -- MAM5 settings ------------------
 is_output_interactive_volc = .true.

 ! Parameter changes for HR

 cld_macmic_num_steps           =  3

 ! gravity wave parameters perturbed
 effgw_oro = 0.25
 !gw_convect_hcf = 2.5
 !effgw_beres = 0.1

 ! Sea salt emissions
  seasalt_emis_scale = 0.72

 ! Raise dust emission from original
 dust_emis_fact = 9.2

 ! Turn off mass flux adjustment
 zmconv_clos_dyn_adj = .false.

 ! lightning NOx emissions
 lght_no_prd_factor = 0.31D0

 !new ORO GWD scheme
 use_gw_oro=.false.
 use_od_ls=.true.
 use_od_bl=.true.
 use_od_ss=.true.
 use_od_fd=.true.
 
 bnd_topo='{topo_file}'

 !Tunings
 od_ls_ncleff = 2
 od_bl_ncd = 3 !(FBD)
 od_ss_sncleff = 1 !(sGWD).

 !New SL transport enhanced trajectory method
 semi_lagrange_trajectory_nsubstep = 3
 semi_lagrange_trajectory_nvelocity = 4
 dt_tracer_factor = 12
 hypervis_subcycle_q = 12
 semi_lagrange_halo = 4

 ! Dust emission cap
 dstemislimitswitch = .true.

 ! Cloud tuning parameter changes
 nucleate_ice_subgrid = 1.40
 !zmconv_tau           = 4200
 !clubb_c8               =  4.8
 !clubb_c1                =  2.7
 p3_embryonic_rain_size = 0.000020D0
 !zmconv_dmpdz    = -0.9e-3

'''
#---------------------------------------------------------------------------------------------------
v3HR_lnd_opts = f'''
 hist_dov2xy = .true.,.true.
 hist_fexcl1 = 'AGWDNPP','ALTMAX_LASTYEAR','AVAIL_RETRANSP','AVAILC','BAF_CROP',
              'BAF_PEATF','BIOCHEM_PMIN_TO_PLANT','CH4_SURF_AERE_SAT','CH4_SURF_AERE_UNSAT','CH4_SURF_DIFF_SAT',
              'CH4_SURF_DIFF_UNSAT','CH4_SURF_EBUL_SAT','CH4_SURF_EBUL_UNSAT','CMASS_BALANCE_ERROR','cn_scalar',
              'COL_PTRUNC','CONC_CH4_SAT','CONC_CH4_UNSAT','CONC_O2_SAT','CONC_O2_UNSAT',
              'cp_scalar','CWDC_HR','CWDC_LOSS','CWDC_TO_LITR2C','CWDC_TO_LITR3C',
              'CWDC_vr','CWDN_TO_LITR2N','CWDN_TO_LITR3N','CWDN_vr','CWDP_TO_LITR2P',
              'CWDP_TO_LITR3P','CWDP_vr','DWT_CONV_CFLUX_DRIBBLED','F_CO2_SOIL','F_CO2_SOIL_vr',
              'F_DENIT_vr','F_N2O_DENIT','F_N2O_NIT','F_NIT_vr','FCH4_DFSAT',
              'FINUNDATED_LAG','FPI_P_vr','FPI_vr','FROOTC_LOSS','HR_vr',
              'LABILEP_TO_SECONDP','LABILEP_vr','LAND_UPTAKE','LEAF_MR','leaf_npimbalance',
              'LEAFC_LOSS','LEAFC_TO_LITTER','LFC2','LITR1_HR','LITR1C_TO_SOIL1C',
              'LITR1C_vr','LITR1N_TNDNCY_VERT_TRANS','LITR1N_TO_SOIL1N','LITR1N_vr','LITR1P_TNDNCY_VERT_TRANS',
              'LITR1P_TO_SOIL1P','LITR1P_vr','LITR2_HR','LITR2C_TO_SOIL2C','LITR2C_vr',
              'LITR2N_TNDNCY_VERT_TRANS','LITR2N_TO_SOIL2N','LITR2N_vr','LITR2P_TNDNCY_VERT_TRANS','LITR2P_TO_SOIL2P',
              'LITR2P_vr','LITR3_HR','LITR3C_TO_SOIL3C','LITR3C_vr','LITR3N_TNDNCY_VERT_TRANS',
              'LITR3N_TO_SOIL3N','LITR3N_vr','LITR3P_TNDNCY_VERT_TRANS','LITR3P_TO_SOIL3P','LITR3P_vr',
              'M_LITR1C_TO_LEACHING','M_LITR2C_TO_LEACHING','M_LITR3C_TO_LEACHING','M_SOIL1C_TO_LEACHING','M_SOIL2C_TO_LEACHING',
              'M_SOIL3C_TO_LEACHING','M_SOIL4C_TO_LEACHING','NDEPLOY','NEM','nlim_m',
              'o2_decomp_depth_unsat','OCCLP_vr','PDEPLOY','PLANT_CALLOC','PLANT_NDEMAND',
              'PLANT_NDEMAND_COL','PLANT_PALLOC','PLANT_PDEMAND','PLANT_PDEMAND_COL','plim_m',
              'POT_F_DENIT','POT_F_NIT','POTENTIAL_IMMOB','POTENTIAL_IMMOB_P','PRIMP_TO_LABILEP',
              'PRIMP_vr','PROD1P_LOSS','QOVER_LAG','RETRANSN_TO_NPOOL','RETRANSP_TO_PPOOL',
              'SCALARAVG_vr','SECONDP_TO_LABILEP','SECONDP_TO_OCCLP','SECONDP_vr','SMIN_NH4_vr',
              'SMIN_NO3_vr','SMINN_TO_SOIL1N_L1','SMINN_TO_SOIL2N_L2','SMINN_TO_SOIL2N_S1','SMINN_TO_SOIL3N_L3',
              'SMINN_TO_SOIL3N_S2','SMINN_TO_SOIL4N_S3','SMINP_TO_SOIL1P_L1','SMINP_TO_SOIL2P_L2','SMINP_TO_SOIL2P_S1',
              'SMINP_TO_SOIL3P_L3','SMINP_TO_SOIL3P_S2','SMINP_TO_SOIL4P_S3','SMINP_vr','SOIL1_HR','SOIL1C_TO_SOIL2C','SOIL1C_vr','SOIL1N_TNDNCY_VERT_TRANS','SOIL1N_TO_SOIL2N','SOIL1N_vr',
              'SOIL1P_TNDNCY_VERT_TRANS','SOIL1P_TO_SOIL2P','SOIL1P_vr','SOIL2_HR','SOIL2C_TO_SOIL3C',
              'SOIL2C_vr','SOIL2N_TNDNCY_VERT_TRANS','SOIL2N_TO_SOIL3N','SOIL2N_vr','SOIL2P_TNDNCY_VERT_TRANS',
              'SOIL2P_TO_SOIL3P','SOIL2P_vr','SOIL3_HR','SOIL3C_TO_SOIL4C','SOIL3C_vr',
              'SOIL3N_TNDNCY_VERT_TRANS','SOIL3N_TO_SOIL4N','SOIL3N_vr','SOIL3P_TNDNCY_VERT_TRANS','SOIL3P_TO_SOIL4P',
              'SOIL3P_vr','SOIL4_HR','SOIL4C_vr','SOIL4N_TNDNCY_VERT_TRANS','SOIL4N_TO_SMINN',
              'SOIL4N_vr','SOIL4P_TNDNCY_VERT_TRANS','SOIL4P_TO_SMINP','SOIL4P_vr','SOLUTIONP_vr',
              'TCS_MONTH_BEGIN','TCS_MONTH_END','TOTCOLCH4','water_scalar','WF',
              'wlim_m','WOODC_LOSS','WTGQ'
 hist_fincl1 = 'SNOWDP','COL_FIRE_CLOSS','NPOOL','PPOOL','TOTPRODC'
 hist_mfilt = 1
 hist_nhtfrq = 0
 hist_avgflag_pertape = 'A'

 check_finidat_year_consistency = .false.
 check_finidat_fsurdat_consistency = .false.

 ! if finidat from a different period is specified
 ! check_finidat_pct_consistency   = .false.

 !--- land BGC spin-up initial conditions ---, pending
 !finidat='{land_init_file}'

'''
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
