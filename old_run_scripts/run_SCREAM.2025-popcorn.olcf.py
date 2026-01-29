#!/usr/bin/env python3
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
Make sure to use:
<command name="load">libfabric/1.20.1</command>
in E3SM_SRC0/cime_config/machines/config_machines.xml
'''
#---------------------------------------------------------------------------------------------------
'''
Hassan's new recipe:

./atmchange autoconversion_prefactor=0.0011111

./atmchange autoconversion_qc_exponent=1.0
./atmchange autoconversion_nc_exponent=0.0
./atmchange accretion_prefactor=10.0
./atmchange rain_selfcollection_prefactor=0.0

./atmchange cldliq_to_ice_collection_factor=0.00001
./atmchange rain_to_ice_collection_factor=0.00001
./atmchange max_total_ni=74000000
'''
#---------------------------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli200'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => whannah/emaxx/add-p3-cld-frac-flags-merge

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

# queue,stop_opt,stop_n,resub,walltime = 'batch','ndays',40,0,'1:45:00'
queue,stop_opt,stop_n,resub,walltime = 'batch','ndays',5,0,'4:00:00'
# queue,stop_opt,stop_n,resub,walltime = 'batch','ndays',1,0,'0:30:00'

arch = 'GPU'

#---------------------------------------------------------------------------------------------------
# build list of cases to run

recipe01 = {'cfr':True,'acc':10.0,'rsc':0.0,'eci':1e-5,'eri':1e-5,'mti':int(74e6),'acp':1e-3,'acq':1.0,'acn':0.0,} # didn't work
recipe02 = {'cfr':True,'acc':10.0,'rsc':0.0,'eci':1e-5,'eri':1e-5,'mti':int(74e6)}

recipe03 = {'cfr':True,'acc':10.0,'rsc':0.0,'eci':1e-5,'eri':1e-5,'mti':int(74e6), 'acp':1,   'acq':2.0,'acn':2.0,'acr': 1e-6} # fails check: qr within interval [0, 0.1]

recipe04 = {'cfr':True,'acc':10.0,'rsc':1e-2,'eci':1e-2,'eri':1e-2,'mti':int(74e6),'acp':1,   'acq':3.0,'acn':3.0,'acr':10e-6} # way too much LWP
recipe05 = {'cfr':True,'acc':10.0,'rsc':1e-2,'eci':1e-2,'eri':1e-2,'mti':int(74e6),'acp':0.5, 'acq':2.0,'acn':2.0,'acr':10e-6} # way too much LWP

recipe06 = {'cfr':True,'acc':10.0,'rsc':1e-5,'eci':1e-5,'eri':1e-5,'mti':int(74e6),'acp':0.5, 'acq':2.0,'acn':2.0,'acr':10e-6} # similar to recipe05 with higher rain water
recipe07 = {'cfr':True,'acc':10.0,'rsc':1e-5,'eci':1e-5,'eri':1e-5,'mti':int(74e6),'acp':0.5, 'acq':2.0,'acn':2.0,'acr':10e-6,'isf':0.95}

recipe08 = {'cfr':True,'acc':10.0,'rsc':1e-5,'eci':1e-5,'eri':1e-5,'mti':int(74e6),'acp':10, 'acq':3.0,'acn':2.0,'acr':5e-6}
recipe09 = {'cfr':True,'acc':10.0,'rsc':1e-5,'eci':1e-5,'eri':1e-5,'mti':int(74e6),'acp':10, 'acq':3.0,'acn':2.0,'acr':5e-6,'isf':0.99}
recipe10 = {'cfr':True,'acc':10.0,'rsc':1e-5,'eci':1e-5,'eri':1e-5,'mti':int(74e6),'acp':10, 'acq':3.0,'acn':2.0,'acr':5e-6,'isf':1.01}

# Too much rain!
# recipe11 = {'cfr':True,'acc':10.0,'rsc':1,'eci':1e-5,'eri':1e-5,'mti':int(74e6),'acp':500, 'acq':3.0,'acn':2.0,'acr':5e-6,'isf':0.95}
# recipe12 = {'cfr':True,'acc':10.0,'rsc':1,'eci':1e-5,'eri':1e-5,'mti':int(74e6),'acp':500, 'acq':3.0,'acn':2.0,'acr':5e-6,'isf':1.00}
# recipe13 = {'cfr':True,'acc':10.0,'rsc':1,'eci':1e-5,'eri':1e-5,'mti':int(74e6),'acp':500, 'acq':3.0,'acn':2.0,'acr':5e-6,'isf':1.05}

# recipe11 = {'cfr':True,'acc':60,'rsc':5,'eci':1e-1,'eri':1e-1,'mti':int(740e4),'acp':100, 'acq':2.5,'acn':1.5,'acr':5e-6,'isf':0.95}
# recipe12 = {'cfr':True,'acc':60,'rsc':5,'eci':1e-1,'eri':1e-1,'mti':int(740e4),'acp':100, 'acq':2.5,'acn':1.5,'acr':5e-6,'isf':1.00}
# recipe13 = {'cfr':True,'acc':60,'rsc':5,'eci':1e-1,'eri':1e-1,'mti':int(740e4),'acp':100, 'acq':2.5,'acn':1.5,'acr':5e-6,'isf':1.05}

recipe14 = {'cfr':True,'cfi':False,'acc':60,'rsc':5,'eci':1e-1,'eri':1e-1,'mti':int(740e4),'acp':100, 'acq':2.5,'acn':1.5,'acr':20e-6,'isf':1.00}
recipe15 = {'cfr':True,'cfi':False,'acc':60,'rsc':5,'eci':1e-1,'eri':1e-1,'mti':int(740e4),'acp':100, 'acq':2.5,'acn':1.5,'acr':20e-6,'isf':0.95}
recipe16 = {'cfr':True,'cfi':True, 'acc':60,'rsc':5,'eci':1e-1,'eri':1e-1,'mti':int(740e4),'acp':100, 'acq':2.5,'acn':1.5,'acr':20e-6,'isf':0.95}
recipe17 = {'cfr':True,'cfi':False,'acc':60,'rsc':5,'eci':1e-1,'eri':1e-1,'mti':int(740e4),'acp':100, 'acq':2.5,'acn':1.5,'acr':20e-6,'isf':0.90}
recipe18 = {'cfr':True,'cfi':True ,'acc':60,'rsc':5,'eci':1e-1,'eri':1e-1,'mti':int(740e4),'acp':100, 'acq':2.5,'acn':1.5,'acr':20e-6,'isf':0.90}

compset = 'F2010-SCREAMv1-DYAMOND1'
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192)
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, cfr=True)
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, **recipe02)
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, **recipe03) # fails check: qr within interval [0, 0.1]
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, **recipe04)
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, **recipe05)
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, **recipe06)
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, **recipe07)

# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, **recipe08)
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, **recipe09)
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, **recipe10)

# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, **recipe11)
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, **recipe12)
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, **recipe13)

# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, **recipe14)
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, **recipe15)
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, **recipe16)
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, **recipe17)
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, **recipe18)

# add_case(prefix='2025-PC-01', compset=compset, grid='ne256pg2', num_nodes=192, cfr=True) # rerun to fix output file names

add_case(prefix='2025-PC-01', compset='F2010-SCREAMv1-DYAMOND1', grid='ne1024pg2', num_nodes=2048)
add_case(prefix='2025-PC-01', compset='F2010-SCREAMv1-DYAMOND1', grid='ne1024pg2', num_nodes=2048, cfr=True)
add_case(prefix='2025-PC-01', compset='F2010-SCREAMv1-DYAMOND1', grid='ne1024pg2', num_nodes=2048, **recipe14)

compset = 'F2010-SCREAMv1'
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192)
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, cfr=True)
# add_case(prefix='2025-PC-00', compset=compset, grid='ne256pg2', num_nodes=192, **recipe1)

native_res = 'ne256pg2'
remap_res  = 'ne30pg2'
hist_map   = '/lustre/orion/cli115/world-shared/e3sm/inputdata/atm/scream/maps/map_ne256pg2_to_ne30pg2_traave.20240206.cdf5.nc'


#---------------------------------------------------------------------------------------------------
''' Notes
add defaults for new namelist parameters here:
components/eamxx/cime_config/namelist_defaults_scream.xml

P3 input cld frac modified here: components/eamxx/src/physics/p3/eamxx_p3_process_interface.cpp
various defaults:
p3_k_accretion = 67
                                        default    minimal
acp => autoconversion_prefactor         1350.0     0.0
acr => autoconversion_radius            25.0e-6    100e-6
acq => autoconversion_qc_exponent       2.47       1.0
acn => autoconversion_nc_exponent       1.79       0.0
acc => accretion_prefactor              67.0       0.0
rsc => rain_selfcollection_prefactor    5.78       0.0
eci => cldliq_to_ice_collection_factor  0.5        ???
eri => rain_to_ice_collection_factor    1.0        ???
mti => max_total_ni                     740.0e3    ???
isf => ice_sedimentation_factor         1.0        ???

scontrol update jobid=34627970 ExcNodeList="nid003193,nid001464,nid001465"
scontrol update jobid=34627964 ExcNodeList="nid003193,nid001464,nid001465"

'''
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(opts):

   case_list = ['SCREAM']
   for key,val in opts.items(): 
      if key in ['prefix','grid','compset']:
         case_list.append(val)
      elif key in ['num_nodes']:
         continue
      else:
         case_list.append(f'{key}_{val:g}')
         # case_list.append(f'{key}_{val}')
   case = '.'.join(case_list)

   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')

   print(f'\n  case : {case}\n')

   # exit()

   #------------------------------------------------------------------------------------------------
   case_root = f'/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch/{case}'

   num_nodes = opts['num_nodes']
   # if arch=='CPU': max_mpi_per_node,atm_nthrds  = 128,1 ; max_task_per_node = 128
   # if arch=='GPU': max_mpi_per_node,atm_nthrds  =   4,8 ; max_task_per_node = 32
   if arch=='CPU': max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,56,1
   if arch=='GPU': max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,8,1
   atm_ntasks = max_mpi_per_node*num_nodes

   grid    = opts['grid']+'_'+opts['grid']
   compset = opts['compset']
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
      cmd += f' --res {grid} '
      cmd += f' --project {acct} '
      if arch=='CPU': cmd+=f' -mach frontier -compiler crayclang'
      # if arch=='GPU': cmd+=f' -mach frontier-scream-gpu -compiler crayclang-scream'
      if arch=='GPU': cmd+=f' -mach frontier -compiler craycray-mphipcc'
      cmd += f' -pecount {atm_ntasks}x{atm_nthrds} '
      run_cmd(cmd)
      #----------------------------------------------------------------------------
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
      # if init_file is not None: run_cmd(f'./atmchange initial_conditions::Filename=\"{init_file}\"')
      #-------------------------------------------------------------------------
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
      #-------------------------------------------------------------------------
      # parameters for addressing popcorn
      if 'acp' in opts.keys():run_cmd(f'./atmchange autoconversion_prefactor'        +f'={opts["acp"]}')
      if 'acr' in opts.keys():run_cmd(f'./atmchange autoconversion_radius'           +f'={opts["acr"]}')
      if 'acq' in opts.keys():run_cmd(f'./atmchange autoconversion_qc_exponent'      +f'={opts["acq"]}')
      if 'acn' in opts.keys():run_cmd(f'./atmchange autoconversion_nc_exponent'      +f'={opts["acn"]}')
      if 'acc' in opts.keys():run_cmd(f'./atmchange accretion_prefactor'             +f'={opts["acc"]}')
      if 'rsc' in opts.keys():run_cmd(f'./atmchange rain_selfcollection_prefactor'   +f'={opts["rsc"]}')
      if 'eci' in opts.keys():run_cmd(f'./atmchange cldliq_to_ice_collection_factor' +f'={opts["eci"]}')
      if 'eri' in opts.keys():run_cmd(f'./atmchange rain_to_ice_collection_factor'   +f'={opts["eri"]}')
      if 'mti' in opts.keys():run_cmd(f'./atmchange max_total_ni'                    +f'={opts["mti"]}')
      if 'cfl' in opts.keys():run_cmd(f'./atmchange p3::set_cld_frac_l_to_one'       +f'=true ')
      if 'cfr' in opts.keys():run_cmd(f'./atmchange p3::set_cld_frac_r_to_one'       +f'=true ')
      if 'cfi' in opts.keys():run_cmd(f'./atmchange p3::set_cld_frac_i_to_one'       +f'=true ')
      if 'isf' in opts.keys():run_cmd(f'./atmchange p3::ice_sedimentation_factor'    +f'={opts["isf"]}')
   #------------------------------------------------------------------------------------------------
   if build : 
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit : 
      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
      add_hist_file('scream_output_2D_1hr_inst_native.yaml',hist_opts_2D_1hr_inst)
      add_hist_file('scream_output_3D_1dy_mean_native.yaml',hist_opts_3D_1dy_mean)
      # add_hist_file('scream_output_2D_1hr_inst_remap.yaml', hist_opts_2D_1hr_inst_remap)
      # add_hist_file('scream_output_3D_1dy_mean_remap.yaml', hist_opts_3D_1dy_mean_remap)
      hist_file_list_str = ','.join(hist_file_list)
      run_cmd(f'./atmchange Scorpio::output_yaml_files="{hist_file_list_str}"')
      #-----------------------------------------------------------------------------
      if compset == 'F2010-SCREAMv1-DYAMOND1':
         start_date = '2016-08-01'
         start_year = int(start_date.split('-')[0])
         run_cmd(f'./xmlchange --file env_run.xml RUN_STARTDATE={start_date}')
         run_cmd(f'./atmchange orbital_year={start_year}')
      #-------------------------------------------------------------------------
      # if init_file is not None: 
      #    run_cmd(f'./atmchange initial_conditions::Filename=\"{init_file}\"')
      #-------------------------------------------------------------------------
      # Set some run-time stuff
      # run_cmd(f'./xmlchange ATM_NCPL={int(86400/dtime)}')
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
      run_cmd(f'./case.submit -a=" -x frontier08656 " ')
      # run_cmd('./case.submit')
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

field_txt_3D = '''
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

# the P3 process tendency fields were not available in this branch
# P3_qr2qv_evap

hist_opts_2D_1hr_inst = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D.1hr.{native_res}
Averaging Type: Instant
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

hist_opts_2D_1hr_inst_remap = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D.1hr.{remap_res}
Averaging Type: Instant
Max Snapshots Per File: 24
horiz_remap_file: {hist_map}
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

hist_opts_3D_1dy_mean = f'''
%YAML 1.1
---
filename_prefix: output.scream.3D.1dy.{native_res}
Averaging Type: Average
Max Snapshots Per File: 1
Fields:
   Physics PG2:
      Field Names:{field_txt_3D}
output_control:
   Frequency: 1
   frequency_units: ndays
   MPI Ranks in Filename: false
Restart:
   force_new_file: true
'''



hist_opts_3D_1dy_mean_remap = f'''
%YAML 1.1
---
filename_prefix: output.scream.3D.1dy.{remap_res}
Averaging Type: Average
Max Snapshots Per File: 1
horiz_remap_file: {hist_map}
Fields:
   Physics PG2:
      Field Names:{field_txt_3D}
output_control:
   Frequency: 1
   frequency_units: ndays
   MPI Ranks in Filename: false
Restart:
   force_new_file: true
'''
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
