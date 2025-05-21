#!/usr/bin/env python
import os

execute = True

tempest_path = "~/Tempest/tempestgecore/bin/"

# ne = 64

date_str = "190319"

mesh_path = "~/Tempest/"
src_mesh_file = mesh_path+"ne30.g"
# dst_mesh_file = mesh_path+"ne"+str(ne)+".g"

dst_name = "ne30pg2"
dst_mesh_file = mesh_path+dst_name+".g"

# input_root  = "/project/projectdirs/acme/inputdata/atm/cam/inic/homme/"
input_root  = "/global/cscratch1/sd/whannah/acme_scratch/init_files/"
output_root = "/global/cscratch1/sd/whannah/acme_scratch/init_files/"

overlap_file = mesh_path+"overlap_mesh.nc"
mapping_file = mesh_path+"mapping_weights.nc "

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

# GenerateCSMesh --alt --res 120 --file ${source_mesh_file}
  
# Generate overlap mesh
cmd = tempest_path+"GenerateOverlapMesh --a "+src_mesh_file+" --b "+dst_mesh_file+" --out "+overlap_file
print("\n"+cmd+"\n")
if execute: os.system(cmd)
  
# Generate mapping weights
cmd = tempest_path+"GenerateOfflineMap "
cmd = cmd+" --in_mesh  "+src_mesh_file
cmd = cmd+" --out_mesh "+dst_mesh_file
cmd = cmd+" --ov_mesh "+overlap_file
cmd = cmd+" --in_np 4 --out_np 4 --in_type cgll --out_type cgll "
cmd = cmd+"--out_map "+mapping_file
print("\n"+cmd+"\n")
if execute: os.system(cmd)
  
# Apply mapping weights
# src_initial_condition = input_root +"atmsrf_ne32np4.nc"
# dst_initial_condition = output_root+"atmsrf_"+dst_name+".nc"

# src_file = "/project/projectdirs/acme/inputdata/share/domains/domain.lnd.ne30np4_gx1v6.110905.nc"
# dst_file = output_root+""
# cmd = "ApplyOfflineMap"+" --map "+mapping_file+" --in_data  "+src_file+" --out_data "+dst_file
# print("\n"+cmd+"\n")
# if execute: os.system(cmd)

src_file = "/project/projectdirs/acme/inputdata/lnd/clm2/?????"
dst_file = ""
cmd = "ApplyOfflineMap"+" --map "+mapping_file+" --in_data  "+src_file+" --out_data "+dst_file
print("\n"+cmd+"\n")
if execute: os.system(cmd)

# cmd = "ncremap -4 -m "+mapping_file+" "+src_initial_condition+" "+dst_initial_condition
# print("\n"+cmd+"\n")
# if execute: os.system(cmd)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------