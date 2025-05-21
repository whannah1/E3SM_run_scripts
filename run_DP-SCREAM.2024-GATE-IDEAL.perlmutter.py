#!/usr/bin/env python
import os, datetime, subprocess as sp
#---------------------------------------------------------------------------------------------------
class tcolor: END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
#---------------------------------------------------------------------------------------------------
def run_cmd(cmd,suppress_output=False):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.END ; print(f'\n{msg}')
   os.system(cmd); return
#---------------------------------------------------------------------------------------------------
def xmlquery(xmlvar):
   ( value, err) = sp.Popen(f'./xmlquery {xmlvar} --value', stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   return value
#---------------------------------------------------------------------------------------------------
'''
components/eamxx/cime_config/namelist_defaults_scream.xml

     <!-- P3 microphysics -->
     <p3 inherit="atm_proc_base">
+      <fix_cld_frac_r>false</fix_cld_frac_r>
+      <fix_cld_frac_i>false</fix_cld_frac_i>
+      <fix_cld_frac_l>false</fix_cld_frac_l>

components/eamxx/src/physics/p3/eamxx_p3_run.cpp

+  if (m_params.get<bool>("fix_cld_frac_l", false)) {
+    auto& cld_frac_l = p3_preproc.cld_frac_l;
+    Kokkos::deep_copy(cld_frac_l,1.0);
+  }
+
+  if (m_params.get<bool>("fix_cld_frac_r", false)) {
+    auto& cld_frac_r = p3_preproc.cld_frac_r;
+    Kokkos::deep_copy(cld_frac_r,1.0);
+  }
+
+  if (m_params.get<bool>("fix_cld_frac_i", false)) {
+    auto& cld_frac_i = p3_preproc.cld_frac_i;
+    Kokkos::deep_copy(cld_frac_i,1.0);
+  }
+
   // Update the variables in the p3 input structures with local values.

   infrastructure.dt = dt;
'''
#---------------------------------------------------------------------------------------------------
prefix_list = []
ne_list, domain_len_list, dt_list = [],[],[]
# autoconvr_list = []
# accretion_list = []
vgrid_name_list = []
vgrid_file_list = []
vgrid_nlev_list = []
init_file_list = []
mod_str_list = []
acp_list = []
acr_list = []
acq_list = []
acn_list = []
acc_list = []
rsc_list = []
eci_list = []
eri_list = []
no_ice_list = []
def add_case(  prefix,ne,domain_len,dt, \
               # autoconvr=None,accretion=None, \
               no_ice=False,
               acp=None, acr=None, acq=None, acn=None, acc=None, rsc=None, \
               eci=None, eri=None,
               vgrid_name=None,vgrid_file=None,vgrid_nlev=None, \
               init_file=None,mod_str=None):
   prefix_list.append(prefix)
   ne_list.append(ne)
   domain_len_list.append(domain_len)
   dt_list.append(dt)
   # autoconvr_list.append(autoconvr)
   # accretion_list.append(accretion)
   no_ice_list.append(no_ice)
   acp_list.append(acp)
   acr_list.append(acr)
   acq_list.append(acq)
   acn_list.append(acn)
   acc_list.append(acc)
   rsc_list.append(rsc)
   eci_list.append(eci)
   eri_list.append(eri)
   vgrid_name_list.append(vgrid_name)
   vgrid_file_list.append(vgrid_file)
   vgrid_nlev_list.append(vgrid_nlev)
   init_file_list.append(init_file)
   mod_str_list.append(mod_str)
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC0'
# src_dir  = os.getenv('HOME')+'/SCREAM/SCREAM_SRC0'
# src_dir  = os.getenv('SCRATCH')+'/tmp_scream_src'

# clean        = True
# newcase      = True
# config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

# queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',10,0,'6:00:00'
# queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',30,0,'12:00:00'
# queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',60,0,'6:00:00'
# queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',1,0,'0:30:00'
queue,stop_opt,stop_n,resub,walltime = 'debug','ndays',1,0,'0:30:00'

arch = 'GPU'

compset = 'FIOP-SCREAMv1-DP'

dp_cpl_tight = False

vgrid_root = '/global/cfs/projectdirs/e3sm/whannah/vert_grid_files'
init_root  = '/global/cfs/projectdirs/e3sm/whannah/HICCUP'

#---------------------------------------------------------------------------------------------------
# build list of cases to run

# add_case(prefix='2024-GATE-IDEAL-00', ne=88, domain_len=800e3, dt=60)
# add_case(prefix='2024-GATE-IDEAL-00', ne=88, domain_len=800e3, dt=60, mod_str='FCFR')
# add_case(prefix='2024-GATE-IDEAL-00', ne=88, domain_len=800e3, dt=60, mod_str='FCFI')
# add_case(prefix='2024-GATE-IDEAL-00', ne=88, domain_len=800e3, dt=60, mod_str='FCFL')
# add_case(prefix='2024-GATE-IDEAL-00', ne=88, domain_len=800e3, dt=60, mod_str='FCFL_FCFR_FCFI')

# add_case(prefix='2024-GATE-IDEAL-01', ne=88, domain_len=800e3, dt=60, mod_str='FCFL_FCFR_FCFI') # test alternate code for namelist flags
# add_case(prefix='2024-GATE-IDEAL-01a', ne=88, domain_len=800e3, dt=60, mod_str='FCFL_FCFR_FCFI') # test alternate code for namelist flags

add_case(prefix='2024-GATE-IDEAL-02', ne=88, domain_len=800e3, dt=60, mod_str='FCFL_FCFR_FCFI') # test alternate ice melt strategy

#---------------------------------------------------------------------------------------------------
# old runs - moved to /pscratch/sd/w/whannah/scream_scratch/pm-gpu/old_DP-GATE/

# add_case(prefix='2024-GATE-IDEAL-02', ne= 88, domain_len= 800e3, dt=60, mod_str='FCFR', accretion=40)

# add_case(prefix='2024-GATE-IDEAL-02', ne= 88, domain_len= 800e3, dt=60, mod_str='FCFR', eci=0.1) # default eci = 0.5
# add_case(prefix='2024-GATE-IDEAL-02', ne= 88, domain_len= 800e3, dt=60, mod_str='FCFR', eri=0.25) # default eri = 1.0

# add_case(prefix='2024-GATE-IDEAL-02', ne= 44, domain_len= 400e3, dt=60, mod_str='FCFR') # control + P3 cld_frac_r = 1 
# add_case(prefix='2024-GATE-IDEAL-02', ne= 44, domain_len= 400e3, dt=60, mod_str='FCFI')
# add_case(prefix='2024-GATE-IDEAL-02', ne= 44, domain_len= 400e3, dt=60, mod_str='FCFR_FCFI')

# add_case(prefix='2024-GATE-IDEAL-02', ne= 44, domain_len= 400e3, dt=60, accretion= 1)
# add_case(prefix='2024-GATE-IDEAL-02', ne= 44, domain_len= 400e3, dt=60, accretion=10)
# add_case(prefix='2024-GATE-IDEAL-02', ne= 44, domain_len= 400e3, dt=60, accretion=20)
# add_case(prefix='2024-GATE-IDEAL-02', ne= 44, domain_len= 400e3, dt=60, accretion=40)

# add_case(prefix='2024-GATE-IDEAL-02', ne= 44, domain_len= 400e3, dt=60, accretion= 1, mod_str='FCFR')
# add_case(prefix='2024-GATE-IDEAL-02', ne= 44, domain_len= 400e3, dt=60, accretion=10, mod_str='FCFR')
# add_case(prefix='2024-GATE-IDEAL-02', ne= 44, domain_len= 400e3, dt=60, accretion=20, mod_str='FCFR')
# add_case(prefix='2024-GATE-IDEAL-02', ne= 44, domain_len= 400e3, dt=60, accretion=40, mod_str='FCFR')

# add_case(prefix='2024-GATE-IDEAL-02', ne= 44, domain_len= 400e3, dt=60) # new control - w/ nu_top tests
#---------------------------------------------------------------------------------------------------
# 03 => update branch and explore pieces of minimal recipe

# add_case(prefix='2024-GATE-IDEAL-03',ne=88,domain_len=800e3,dt=60,mod_str='FCFR') # new control - always use maximal rain fraction
# add_case(prefix='2024-GATE-IDEAL-03',ne=88,domain_len=800e3,dt=60,mod_str='FCFR',no_ice=True,acp=0.0005555555,acr=0.0001,acq=1.0,acn=0.0,acc=0.0,rsc=0.0) # minimal recipe v1 (mistake)

# add_case(prefix='2024-GATE-IDEAL-03',ne=88,domain_len=800e3,dt=60,mod_str='FCFR',no_ice=True) # minimal recipe components
# add_case(prefix='2024-GATE-IDEAL-03',ne=88,domain_len=800e3,dt=60,mod_str='FCFR',acp=0.0005555555) # minimal recipe components
# add_case(prefix='2024-GATE-IDEAL-03',ne=88,domain_len=800e3,dt=60,mod_str='FCFR',acr=0.0001) # minimal recipe components
# add_case(prefix='2024-GATE-IDEAL-03',ne=88,domain_len=800e3,dt=60,mod_str='FCFR',acq=1.0) # minimal recipe components
# add_case(prefix='2024-GATE-IDEAL-03',ne=88,domain_len=800e3,dt=60,mod_str='FCFR',acn=0.0) # minimal recipe components
# add_case(prefix='2024-GATE-IDEAL-03',ne=88,domain_len=800e3,dt=60,mod_str='FCFR',acc=0.0) # minimal recipe components
# add_case(prefix='2024-GATE-IDEAL-03',ne=88,domain_len=800e3,dt=60,mod_str='FCFR',rsc=0.0) # minimal recipe components

# add_case(prefix='2024-GATE-IDEAL-03',ne=88,domain_len=800e3,dt=60,mod_str='FCFR',no_ice=True,acr=100e-6, acq=1.0) # minimal recipe components
# add_case(prefix='2024-GATE-IDEAL-03',ne=88,domain_len=800e3,dt=60,mod_str='FCFR',no_ice=True,acc=0.0) # minimal recipe components
# add_case(prefix='2024-GATE-IDEAL-03',ne=88,domain_len=800e3,dt=60,mod_str='FCFR',no_ice=True,rsc=0.0) # minimal recipe components
# add_case(prefix='2024-GATE-IDEAL-03',ne=88,domain_len=800e3,dt=60,mod_str='FCFR',acr=100e-6, acq=1.0) # minimal recipe components

# add_case(prefix='2024-GATE-IDEAL-03',ne=88,domain_len=800e3,dt=60,mod_str='FCFR',acr=100e-6, acq=1.0, rsc=0.0) # minimal recipe components

# no need to specify FCFR anymore - it's always on - also omit domain and time step from case name
# add_case(prefix='2024-GATE-IDEAL-04',ne=88,domain_len=800e3,dt=60, rsc=4.0, eci=0.4 ) # ?
# add_case(prefix='2024-GATE-IDEAL-04',ne=88,domain_len=800e3,dt=60, rsc=3.0, eci=0.3 ) # ?
# add_case(prefix='2024-GATE-IDEAL-04',ne=88,domain_len=800e3,dt=60, rsc=2.0, eci=0.2 ) # ?
# add_case(prefix='2024-GATE-IDEAL-04',ne=88,domain_len=800e3,dt=60, rsc=1.0, eci=0.1 ) # ?


# acp => autoconversion_prefactor         0.0      1350.0
# acr => autoconversion_radius            100e-6   25.0e-6
# acq => autoconversion_qc_exponent       1.0      2.47
# acn => autoconversion_nc_exponent       0.0      1.79
# acc => accretion_prefactor              0.0      67.0
# rsc => rain_selfcollection_prefactor    0.0      5.78
# eci => cldliq_to_ice_collection_factor           0.5
# eri => rain_to_ice_collection_factor             1.0

#---------------------------------------------------------------------------------------------------
''' Notes
add defaults for new namelist parameters here:
components/eamxx/cime_config/namelist_defaults_scream.xml

P3 input cld frac modified here: components/eamxx/src/physics/p3/eamxx_p3_process_interface.cpp
various defaults:
p3_k_accretion = 67
'''
#---------------------------------------------------------------------------------------------------
# Case specific information
iop_path                = 'atm/cam/scam/iop'
# iop_file                = 'GATEIDEAL_iopfile_4scam.nc'
iop_file                = 'GATEIDEAL_iopfile_4scam_extended.nc'
lat                     =   9.0      # latitude
lon                     = 336.0      # longitude
do_iop_srf_prop         = 'false'    # Use surface fluxes in IOP file?
do_iop_nudge_tq         = 'false'    # Relax T&Q to observations?
do_iop_nudge_uv         = 'true'     # Relax U&V to observations?
do_iop_nudge_coriolis   = 'false'    # Nudge to geostrophic winds?
do_iop_subsidence       = 'false'    # compute LS vertical transport?
startdate               = '1974-08-30' # Start date in IOP file
start_in_sec            = 0            # start time in seconds in IOP file
do_turnoff_swrad        = True

num_nodes = 1
# max_mpi_per_node,atm_nthrds  = 8,1
max_mpi_per_node,atm_nthrds  = 4,1
max_task_per_node = max_mpi_per_node*atm_nthrds
atm_ntasks = max_mpi_per_node*num_nodes

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(prefix,ne,domain_len,dtime, \
         # autoconvr,accretion, \
         no_ice,\
         acp,acr,acq,acn,acc,rsc, \
         eci,eri,\
         vgrid_name,vgrid_file,vgrid_nlev,init_file,
         mod_str):

   domain_len_km = int( domain_len / 1e3 )

   case_list = ['DPSCREAM',prefix]

   # case_list.append(f'ne{ne}')
   # case_list.append(f'len_{domain_len_km}km')
   # case_list.append(f'DT_{dtime}')

   # case_list.append('nutop_2e4')

   if dp_cpl_tight: case_list.append('TCPL')
   # if autoconvr  is not None: case_list.append(f'acn_{autoconvr}')
   # if accretion  is not None: case_list.append(f'acc_{accretion}')
   if no_ice                : case_list.append(f'no_ice')
   if acp        is not None: case_list.append(f'acp_{acp}')
   if acr        is not None: case_list.append(f'acr_{acr}')
   if acq        is not None: case_list.append(f'acq_{acq}')
   if acn        is not None: case_list.append(f'acn_{acn}')
   if acc        is not None: case_list.append(f'acc_{acc}')
   if rsc        is not None: case_list.append(f'rsc_{rsc}')
   if eci        is not None: case_list.append(f'eci_{eci}')
   if eri        is not None: case_list.append(f'eri_{eri}')
   if vgrid_file is not None: case_list.append(f'vgrid_{vgrid_name}')
   if mod_str    is not None: case_list.append(mod_str)
   case = '.'.join(case_list)

   print('\n  case : '+case+'\n')

   if arch=='GPU': case_root = os.getenv('SCRATCH')+f'/scream_scratch/pm-gpu/{case}'
   if arch=='CPU': case_root = os.getenv('SCRATCH')+f'/scream_scratch/pm-cpu/{case}'

   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{tcolor.RED}This case already exists!{tcolor.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case}'
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --handle-preexisting-dirs u '
      cmd += f' --compset {compset}'
      cmd += f' --res ne30pg2_ne30pg2 '
      cmd += f' --project {acct} '
      # cmd += f' --queue {queue} --walltime {wallt} '
      # cmd += f' -mach frontier-scream-gpu -compiler crayclang-scream  '
      if arch=='GPU': cmd += f' -mach pm-gpu -compiler gnugpu '
      if arch=='CPU': cmd += f' -mach pm-cpu -compiler gnu '
      cmd += f' -pecount {atm_ntasks}x{atm_nthrds} '
      run_cmd(cmd)
      # cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case}'
      # cmd += f' -compiler gnu -compset {compset} -res ne30_ne30 --pecount {ntasks}x1'
      # run_cmd(cmd)
      # # Copy this run script into the case directory
      # timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config : 
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------------------------
      run_cmd(f'./xmlchange RUN_STARTDATE="{startdate}",START_TOD="{start_in_sec}"')
      run_cmd(f'./xmlchange PTS_MULTCOLS_MODE="TRUE",PTS_MODE="TRUE",PTS_LAT="{lat}",PTS_LON="{lon}"')
      #-------------------------------------------------------------------------
      # num_col = ne*ne*(4-1)**2 # number of columns needed for component model initialization
      num_col = ne*ne*4 # number of columns needed for component model initialization
      run_cmd(f'./xmlchange MASK_GRID="USGS",PTS_NX="{num_col}",PTS_NY=1')
      run_cmd(f'./xmlchange ICE_NX="{num_col}",ICE_NY=1')
      run_cmd(f'./xmlchange CALENDAR="GREGORIAN"')
      run_cmd(f'./xmlchange PIO_TYPENAME="netcdf"')
      #-------------------------------------------------------------------------
      din_loc_root = xmlquery('DIN_LOC_ROOT')
      cmake_opts   = xmlquery('SCREAM_CMAKE_OPTIONS')
      #-------------------------------------------------------------------------
      # change vertical levels
      if vgrid_nlev is not None: vgrid_nlev_loc = vgrid_nlev
      if vgrid_nlev is     None: vgrid_nlev_loc = 128
      opt_list = cmake_opts.split()
      for i,opt in enumerate(opt_list):
         if opt=='SCREAM_NUM_VERTICAL_LEV': opt_list[i+1] = f'{vgrid_nlev_loc}'
      cmake_opts = ' '.join(opt_list)
      run_cmd(f'./xmlchange SCREAM_CMAKE_OPTIONS="{cmake_opts}"')
      #-------------------------------------------------------------------------
      # if init_file is not None: run_cmd(f'./atmchange initial_conditions::Filename=\"{init_file}\"')
      #-------------------------------------------------------------------------
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
      #-------------------------------------------------------------------------
      # Set relevant namelist modifications  
      run_cmd(f'./atmchange target_latitude={lat} ')
      run_cmd(f'./atmchange target_longitude={lon} ')
      run_cmd(f'./atmchange se_ne_x={ne} ')
      run_cmd(f'./atmchange se_ne_y={ne} ')
      run_cmd(f'./atmchange se_lx={domain_len} ')
      run_cmd(f'./atmchange se_ly={domain_len} ')
      run_cmd(f'./atmchange cubed_sphere_map=2 ')
      run_cmd(f'./atmchange iop_file={din_loc_root}/{iop_path}/{iop_file} ')
      run_cmd(f'./atmchange nu=0.216784 ')
      # run_cmd(f'./atmchange nu_top=1e3 ') # ok
      run_cmd(f'./atmchange nu_top=1e4 ') # default
      # run_cmd(f'./atmchange nu_top=2e4 ') # ?
      # run_cmd(f'./atmchange nu_top=5e4 ') # bad
      # run_cmd(f'./atmchange nu_top=1e5 ') # bad
      # run_cmd(f'./atmchange nu_top=1e6 ') # bad
      # run_cmd(f'./atmchange nu_top=1e8 ') # bad
      run_cmd(f'./atmchange se_ftype=2 ')
      if dp_cpl_tight:
         run_cmd(f'./atmchange se_tstep={dtime} ')
         run_cmd(f'./atmchange dt_remap_factor=1 ')
         run_cmd(f'./atmchange dt_tracer_factor=1 ')
         run_cmd(f'./atmchange hypervis_subcycle_q=1 ')
      else:
         run_cmd(f'./atmchange dt_remap_factor=1 ')
         run_cmd(f'./atmchange se_tstep={(dtime/6)} ')
      run_cmd(f'./atmchange rad_frequency=1 ')
      run_cmd(f'./atmchange iop_srf_prop={do_iop_srf_prop} ')
      run_cmd(f'./atmchange iop_nudge_uv={do_iop_nudge_uv} ')
      run_cmd(f'./atmchange iop_nudge_tq={do_iop_nudge_tq} ')
      run_cmd(f'./atmchange iop_coriolis={do_iop_nudge_coriolis} ')
      run_cmd(f'./atmchange iop_dosubsidence={do_iop_subsidence} ')
      # # Allow for the computation of tendencies for output purposes
      # run_cmd(f'./atmchange physics::mac_aero_mic::shoc::compute_tendencies=T_mid,qv')
      # run_cmd(f'./atmchange physics::mac_aero_mic::p3::compute_tendencies=T_mid,qv')
      # run_cmd(f'./atmchange physics::rrtmgp::compute_tendencies=T_mid')
      # run_cmd(f'./atmchange homme::compute_tendencies=T_mid,qv')
      #-------------------------------------------------------------------------
      # parameters for popcorn testing
      # if autoconvr  is not None: run_cmd(f'./atmchange p3_autoconversion_prefactor={autoconvr} ')
      # if accretion  is not None: run_cmd(f'./atmchange p3_k_accretion={accretion} ')
      if vgrid_file is not None: run_cmd(f'./atmchange vertical_coordinate_filename={vgrid_file} ')
      # if eci        is not None: run_cmd(f'./atmchange p3_eci={eci}') # default = 0.5
      # if eri        is not None: run_cmd(f'./atmchange p3_eri={eri}') # default = 1.0
      if acp is not None: run_cmd(f'./atmchange autoconversion_prefactor={acp} ')
      if acr is not None: run_cmd(f'./atmchange autoconversion_radius={acr} ')
      if acq is not None: run_cmd(f'./atmchange autoconversion_qc_exponent={acq} ')
      if acn is not None: run_cmd(f'./atmchange autoconversion_nc_exponent={acn} ')
      if acc is not None: run_cmd(f'./atmchange accretion_prefactor={acc} ')
      if rsc is not None: run_cmd(f'./atmchange rain_selfcollection_prefactor={rsc} ')
      if eci is not None: run_cmd(f'./atmchange cldliq_to_ice_collection_factor={eci}') # default = 0.5
      if eri is not None: run_cmd(f'./atmchange rain_to_ice_collection_factor={eri}') # default = 1.0
      if no_ice: run_cmd(f'./atmchange do_ice_production=false ')
      #-------------------------------------------------------------------------
      # p3_eci => cldliq_to_ice_collection_factor
      # p3_eri => rain_to_ice_collection_factor
   #------------------------------------------------------------------------------------------------
   if build : 
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit : 
      #-------------------------------------------------------------------------
      # # special flags for enabling modified code blocks
      # run_cmd(f'./atmchange p3::fix_cld_frac_r=true ')

      if mod_str is not None:
         mod_list = mod_str.split('_')
         if 'FCFL' in mod_list: run_cmd(f'./atmchange p3::set_cld_frac_l_to_one=true ')
         if 'FCFR' in mod_list: run_cmd(f'./atmchange p3::set_cld_frac_r_to_one=true ')
         if 'FCFI' in mod_list: run_cmd(f'./atmchange p3::set_cld_frac_i_to_one=true ')
         # if 'FCFR' not in mod_list: run_cmd(f'./atmchange p3::fix_cld_frac_r=false ')
      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
      add_hist_file('scream_output_1D_1hr_mean.yaml',hist_opts_1D_1hr)
      add_hist_file('scream_output_2D_1hr_mean.yaml',hist_opts_2D_1hr)
      # add_hist_file('scream_output_3D_6hr_mean.yaml',hist_opts_3D_6hr)
      # add_hist_file('scream_output_2D_5min_mean.yaml',hist_opts_2D_5min)
      # add_hist_file('scream_output_3D_5min_mean.yaml',hist_opts_3D_5min)
      hist_file_list_str = ','.join(hist_file_list)
      run_cmd(f'./atmchange Scorpio::output_yaml_files="{hist_file_list_str}"')
      #-------------------------------------------------------------------------
      if init_file is not None: 
         run_cmd(f'./atmchange initial_conditions::Filename=\"{init_file}\"')
      #-------------------------------------------------------------------------
      # write_atm_namelist(ne,domain_len,dtime)
      #-------------------------------------------------------------------------
      # avoid writing monthly cice file
      file = open('user_nl_cice','w') 
      file.write(f"histfreq='y','x','x','x','x' \n")
      file.close()

      constant_zenith_deg = 180 if do_turnoff_swrad else -1

      file = open('user_nl_cpl','w') 
      file.write(f' constant_zenith_deg = {constant_zenith_deg} \n')
      file.write(f' ocn_surface_flux_scheme = 2 \n')
      file.close()

      # ELM output is temporarily broken for DP-SCREAM so turn it off
      file = open('user_nl_elm','w') 
      file.write(f"hist_empty_htapes = .true. \n")
      file.close()

      #-------------------------------------------------------------------------
      # Set some run-time stuff
      run_cmd(f'./xmlchange ATM_NCPL={int(86400/dtime)}')
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
      if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------------------------
      # Submit the run
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
field_txt_2D = '''
      - ps
      - precip_total_surf_mass_flux
      - VapWaterPath
      - LiqWaterPath
      - IceWaterPath
      - surf_sens_flux
      - surf_evap
      - surface_upward_latent_heat_flux
      - surf_mom_flux
      - wind_speed_10m
      - horiz_winds_at_model_bot
      - SW_flux_dn_at_model_bot
      - SW_flux_up_at_model_bot
      - LW_flux_dn_at_model_bot
      - LW_flux_up_at_model_bot
      - SW_flux_up_at_model_top
      - SW_flux_dn_at_model_top
      - LW_flux_up_at_model_top
'''

# field_txt_3D = '''
#       - ps
#       - omega
#       - horiz_winds
#       - qv
#       - qc
#       - qr
#       - qi
#       - qm
#       - nc
#       - nr
#       - ni
#       - bm
#       - T_mid
#       - z_mid
#       - RelativeHumidity
#       - rad_heating_pdel
#       - P3_qr2qv_evap
# '''

field_txt_1D = '''
      - ps
      - omega
      - horiz_winds
      - qv
      - qc
      - qr
      - qi
      - qm
      - nc
      - nr
      - ni
      - bm
      - T_mid
      - z_mid
      - RelativeHumidity
      - rad_heating_pdel
'''

hist_opts_2D_1hr = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D.1hr
Averaging Type: Average
Max Snapshots Per File: 24
Fields:
   Physics PG2:
      Field Names:{field_txt_2D}
output_control:
   Frequency: 1
   frequency_units: nhours
   MPI Ranks in Filename: false
Restart:
   force_new_file: true
'''

hist_opts_1D_1hr = f'''
%YAML 1.1
---
filename_prefix: output.scream.1D.1hr
Averaging Type: Average
Max Snapshots Per File: 24
horiz_remap_file: /global/homes/w/whannah/maps/map_dpxx_x800000m_y800000m_nex88_ney88_to_1x1.20241213.nc
Fields:
   Physics PG2:
      Field Names:{field_txt_1D}
output_control:
   Frequency: 1
   frequency_units: nhours
   MPI Ranks in Filename: false
Restart:
   force_new_file: true
'''

# hist_opts_3D_6hr = f'''
# %YAML 1.1
# ---
# filename_prefix: output.scream.3D.6hr
# Averaging Type: Average
# Max Snapshots Per File: 4
# Fields:
#    Physics PG2:
#       Field Names:{field_txt_3D}
# output_control:
#    Frequency: 1
#    frequency_units: nhours
#    MPI Ranks in Filename: false
# Restart:
#    force_new_file: true
# '''

# hist_opts_2D_5min = f'''
# %YAML 1.1
# ---
# filename_prefix: output.scream.2D.5min
# Averaging Type: Average
# Max Snapshots Per File: 72
# Fields:
#    Physics PG2:
#       Field Names:{field_txt_2D}
# output_control:
#    Frequency: 5
#    frequency_units: nmins
#    MPI Ranks in Filename: false
# Restart:
#    force_new_file: true
# '''

# hist_opts_3D_5min = f'''
# %YAML 1.1
# ---
# filename_prefix: output.scream.3D.5min
# Averaging Type: Average
# Max Snapshots Per File: 72
# Fields:
#    Physics PG2:
#       Field Names:{field_txt_3D}
# output_control:
#    Frequency: 5
#    frequency_units: nmins
#    MPI Ranks in Filename: false
# Restart:
#    force_new_file: true
# '''
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(ne_list)):
      main( prefix_list[n], \
            ne_list[n], \
            domain_len_list[n], \
            dt_list[n], \
            # autoconvr_list[n], \
            # accretion_list[n], \
            no_ice_list[n], \
            acp_list[n], \
            acr_list[n], \
            acq_list[n], \
            acn_list[n], \
            acc_list[n], \
            rsc_list[n], \
            eci_list[n], \
            eri_list[n], \
            vgrid_name_list[n], \
            vgrid_file_list[n], \
            vgrid_nlev_list[n], \
            init_file_list[n], \
            mod_str_list[n], \
          )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
