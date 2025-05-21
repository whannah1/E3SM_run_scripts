#!/usr/bin/env python
import os

home = os.getenv("HOME")

# GenerateVolumetricMesh --in ne4.g --out ne4pg2.g --np 2 --uniform --reverse

# dst_name = "ne4np4_alt"
# src_name = "oQU240"

# atm_grid_file=ne4.g
# ocn_grid_file=ocean.QU.240km.scrip.151209.nc

# atm_res=ne4pg2;  ocn_grid_file=ocean.QU.240km.scrip.151209.nc; atm_grid_file=$atm_res"_scrip.nc"; ncremap -P mwf -s $ocn_grid_file -g $atm_grid_file --nm_src=oQU240 --nm_dst=$atm_res --dt_sng=20190314 --dbg_lvl=2


# atm_res=ne32pg2; ncremap --alg_typ=aave --grd_src=ocean.QU.240km.scrip.151209.nc --grd_dst=${atm_res}_scrip.nc --map=/global/homes/w/whannah/E3SM/init_scratch/map_oQU240_to_${atm_res}_aave.20190312.nc

# gen_domain=~/E3SM/E3SM_SRC2/cime/tools/mapping/gen_domain_files/gen_domain
# atm_grid_name=ne8pg2; ocn_grid_name=oQU240; ${gen_domain} -m map_${ocn_grid_name}_to_${atm_res}_aave.20190312.nc -o ${ocn_grid_name} -l ${atm_grid_name}



# e3sm_root=~/E3SM/E3SM_SRC2 ; interp_root=${e3sm_root}/components/cam/tools/interpic_new ; template_file=${interp_root}/template.nc

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

build   = False
execute = True
suppress_output = True

ne,npg = 30,2

if npg==0 : atm_grid_name = "ne"+str(ne)
if npg>0  : atm_grid_name = "ne"+str(ne)+"pg"+str(npg)


ocn_grid_name = "oEC60to30v3"
# ocn_grid_name = "oQU240"
# ocn_grid_name = "oECv3"

gen_domain_root = home+'/E3SM/E3SM_SRC3/cime/tools/mapping/gen_domain_files'

tempest_top   = home+"/Tempest"
tempest_root  = home+"/Tempest/tempestgecore/bin/"
mapping_dir   = "/global/cscratch1/sd/whannah/Tempest/files_maps"
overlap_mesh  = mapping_dir+"/ncremap_tmp_msh_ovr_tempest.g"
transpose_map = mapping_dir+"/ncremap_tmp_map_trn_tempest.nc"
output_map    = mapping_dir+"/map_"+ocn_grid_name+"_to_"+atm_grid_name+"_monotr.nc"


atm_grid_file = tempest_top+"/files_exodus/"+atm_grid_name+".g"

if ocn_grid_name=="oQU240": ocn_grid_file = tempest_top+"/files_scrip/ocean.QU.240km.scrip.151209.nc"
if ocn_grid_name=="oECv3" : ocn_grid_file = "/project/projectdirs/acme/inputdata/ocn/mpas-o/oEC60to30v3/ocean.oEC60to30v3.scrip.181106.nc"
#-------------------------------------------------------------------------------
# source environment and build
#-------------------------------------------------------------------------------
# source /global/project/projectdirs/acme/software/anaconda_envs/load_latest_e3sm_unified.sh

#-------------------------------------------------------------------------------
# Build the gen_domain tool
#-------------------------------------------------------------------------------
if build: 

   os.chdir(gen_domain_root+'/src')

   cmd = '../../../configure --macros-format Makefile --mpilib mpi-serial'
   print("\n"+cmd+"\n")
   os.system(cmd)

   # cmd = 'source '+gen_domain_root+'/src'+'/env_mach_specific.xml ; gmake'
   cmd = 'gmake'
   print("\n"+cmd+"\n")
   os.system(cmd)

#-------------------------------------------------------------------------------
# Create domain file
#-------------------------------------------------------------------------------
# os.chdir(home+'/E3SM')
os.chdir('/global/cscratch1/sd/whannah/acme_scratch/init_files/')

fminval = 0.001 # default
if ne==30 and npg==2 : fminval = 0.1

cmd = gen_domain_root+'/gen_domain'
cmd = cmd + ' -m '+output_map
cmd = cmd + ' -o '+ocn_grid_name
cmd = cmd + ' -l '+atm_grid_name
cmd = cmd + ' --fminval '+str(fminval)
# if suppress_output : cmd = cmd + " > /dev/null"
print("\n"+cmd+"\n")
if execute: os.system(cmd)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
