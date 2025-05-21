#!/usr/bin/env python
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
import os
import subprocess as sp

# local inputdata path
inputdata_path = '/global/project/projectdirs/e3sm/inputdata'

username = 'ac.whannah'
server = 'blues.lcrc.anl.gov'

# Destination path
# dst_dir = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files/PR3568_files/'
dst_top_dir = '/lcrc/group/acme/public_html/inputdata/'

execute = False

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
files = []

# ne45pg2 files
files.append('share/domains/domain.lnd.ne45pg2_oEC60to30v3.200615.nc')
files.append('share/domains/domain.ocn.ne45pg2_oEC60to30v3.200615.nc')
files.append('cpl/gridmaps/ne45pg2/map_ne45pg2_to_oEC60to30v3_mono.200610.nc')
files.append('cpl/gridmaps/ne45pg2/map_ne45pg2_to_oEC60to30v3_bilin.200610.nc')
files.append('cpl/gridmaps/oEC60to30v3/map_oEC60to30v3_to_ne45pg2_mono.200610.nc')
files.append('cpl/gridmaps/ne45pg2/map_ne45pg2_to_r05_mono.200610.nc')
files.append('cpl/gridmaps/ne45pg2/map_ne45pg2_to_r05_bilin.200610.nc')
files.append('cpl/gridmaps/ne45pg2/map_r05_to_ne45pg2_mono.200610.nc')
files.append('atm/cam/inic/homme/cami_mam3_Linoz_ne45np4_L72_c20200611.nc')
files.append('atm/cam/inic/homme/cami_aquaplanet_ne45np4_L72_c20200611.nc')
files.append('atm/cam/topo/USGS-gtopo30_ne45np4pg2_16xdel2.c20200615.nc')
files.append('atm/cam/chem/trop_mam/atmsrf_ne45pg2_200527.nc')


# # ne30pg3 files
# files.append('share/domains/domain.lnd.ne30pg3_oEC60to30v3.200330.nc')
# files.append('share/domains/domain.ocn.ne30pg3_oEC60to30v3.200330.nc')
# files.append('cpl/gridmaps/ne30pg3/map_ne30pg3_to_oEC60to30v3_mono.200331.nc')
# files.append('cpl/gridmaps/ne30pg3/map_ne30pg3_to_oEC60to30v3_bilin.200331.nc')
# files.append('cpl/gridmaps/oEC60to30v3/map_oEC60to30v3_to_ne30pg3_mono.200331.nc')
# files.append('cpl/gridmaps/ne30pg3/map_ne30pg3_to_r05_mono.200331.nc')
# files.append('cpl/gridmaps/ne30pg3/map_ne30pg3_to_r05_bilin.200331.nc')
# files.append('cpl/gridmaps/ne30pg3/map_r05_to_ne30pg3_mono.200331.nc')
# files.append('atm/cam/topo/USGS-gtopo30_ne30np4pg3_16xdel2.c20200504.nc')

# # ne30pg4 files
# files.append('share/domains/domain.lnd.ne30pg4_oEC60to30v3.200330.nc')
# files.append('share/domains/domain.ocn.ne30pg4_oEC60to30v3.200330.nc')
# files.append('cpl/gridmaps/ne30pg4/map_ne30pg4_to_oEC60to30v3_mono.200331.nc')
# files.append('cpl/gridmaps/ne30pg4/map_ne30pg4_to_oEC60to30v3_bilin.200331.nc')
# files.append('cpl/gridmaps/oEC60to30v3/map_oEC60to30v3_to_ne30pg4_mono.200331.nc')
# files.append('cpl/gridmaps/ne30pg4/map_ne30pg4_to_r05_mono.200331.nc')
# files.append('cpl/gridmaps/ne30pg4/map_ne30pg4_to_r05_bilin.200331.nc')
# files.append('cpl/gridmaps/ne30pg4/map_r05_to_ne30pg4_mono.200331.nc')
# files.append('atm/cam/topo/USGS-gtopo30_ne30np4pg4_16xdel2.c20200504.nc')

# # ne120pg2 files
# files.append('share/domains/domain.lnd.ne120pg2_oEC60to30v3.200511.nc')
# files.append('share/domains/domain.ocn.ne120pg2_oEC60to30v3.200511.nc')
# files.append('cpl/gridmaps/ne120pg2/map_ne120pg2_to_oEC60to30v3_mono.200331.nc')
# files.append('cpl/gridmaps/ne120pg2/map_ne120pg2_to_oEC60to30v3_bilin.200331.nc')
# files.append('cpl/gridmaps/oEC60to30v3/map_oEC60to30v3_to_ne120pg2_mono.200331.nc')
# files.append('cpl/gridmaps/ne120pg2/map_ne120pg2_to_r05_mono.200331.nc')
# files.append('cpl/gridmaps/ne120pg2/map_ne120pg2_to_r05_bilin.200331.nc')
# files.append('cpl/gridmaps/ne120pg2/map_r05_to_ne120pg2_mono.200331.nc')
# files.append('atm/cam/topo/USGS-gtopo30_ne120np4pg2_16xdel2.nc')

# # conus np4 files
# files.append('share/domains/domain.lnd.conusx4v1_oEC60to30v3.200518.nc')
# files.append('share/domains/domain.ocn.conusx4v1_oEC60to30v3.200518.nc')
# files.append('cpl/gridmaps/conusx4v1/map_conusx4v1_to_oEC60to30v3_mono.200514.nc')
# files.append('cpl/gridmaps/conusx4v1/map_conusx4v1_to_oEC60to30v3_bilin.200514.nc')
# files.append('cpl/gridmaps/oEC60to30v3/map_oEC60to30v3_to_conusx4v1_monotr.200514.nc')
# files.append('cpl/gridmaps/conusx4v1/map_conusx4v1_to_r05_mono.200514.nc')
# files.append('cpl/gridmaps/conusx4v1/map_conusx4v1_to_r05_bilin.200514.nc')
# files.append('cpl/gridmaps/conusx4v1/map_r05_to_conusx4v1_monotr.200514.nc')
# files.append('cpl/gridmaps/conusx4v1/map_r05_to_conusx4v1_bilin.200514.nc')
# files.append('atm/cam/topo/USGS_conusx4v1-tensor12x_consistentSGH_c150924.nc')
# files.append('atm/cam/chem/trop_mam/atmsrf_conusx4v1.nc')

# # conus pg2 files
# files.append('share/domains/domain.lnd.conusx4v1pg2_oEC60to30v3.200518.nc')
# files.append('share/domains/domain.ocn.conusx4v1pg2_oEC60to30v3.200518.nc')
# files.append('cpl/gridmaps/conusx4v1pg2/map_conusx4v1pg2_to_oEC60to30v3_mono.200514.nc')
# files.append('cpl/gridmaps/conusx4v1pg2/map_conusx4v1pg2_to_oEC60to30v3_bilin.200514.nc')
# files.append('cpl/gridmaps/oEC60to30v3/map_oEC60to30v3_to_conusx4v1pg2_mono.200514.nc')
# files.append('cpl/gridmaps/conusx4v1pg2/map_conusx4v1pg2_to_r05_mono.200514.nc')
# files.append('cpl/gridmaps/conusx4v1pg2/map_conusx4v1pg2_to_r05_bilin.200514.nc')
# files.append('cpl/gridmaps/conusx4v1pg2/map_r05_to_conusx4v1pg2_mono.200514.nc')
# files.append('atm/cam/topo/USGS_conusx4v1pg2_12x_consistentSGH_20200609.nc')
# files.append('atm/cam/chem/trop_mam/atmsrf_conusx4v1pg2_20020609.nc')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

class tcolor:
   ENDC,RED,GREEN,YELLOW,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m'

# files.sort()
# for file in files: print(file)

os.chdir(inputdata_path)

file_list = ''

for file in files:

   file_path = f'{inputdata_path}/{file}'

   # Check that file exists
   found = False
   msg = file_path.ljust(100)
   if os.path.isfile(file_path):
      found = True
      msg += '  '+tcolor.GREEN+'OK'+tcolor.ENDC
      # print(msg)
   else:
      msg += '  '+tcolor.RED+'MISSING'+tcolor.ENDC
      print(msg)


   file_list = file_list+' '+file

   if found:
      ### copy to new directory
      # cmd = f'cp {file_path} {dst_top_dir}'
      # msg = tcolor.GREEN + cmd + tcolor.ENDC
      # print('\n'+msg+'')
      # os.system(cmd)

      sub_path = os.path.dirname(file)

      ### send to blues via scp
      cmd = f'scp {file_path}  {username}@{server}:{dst_top_dir}/{sub_path}/'
      print('\n'+tcolor.GREEN+cmd+tcolor.ENDC+'\n')

      if execute:
         # os.system(cmd)
         try:
            # sp.check_output(cmd,shell=True)
            sp.check_output(cmd,shell=True,stderr=sp.STDOUT)
            # sp.check_output(cmd,shell=True,stderr=sp.PIPE)
         except sp.CalledProcessError as e:
            print(e.output)

      # exit()

print(file_list)

