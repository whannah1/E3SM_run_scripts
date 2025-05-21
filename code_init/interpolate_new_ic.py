#!/usr/bin/env python
import os

execute = False

tempest_path = "~/Tempest/tempestgecore/bin/"

ne = 30
npg = 3

# date_str = "190321"

if npg==0 :
   grid_name = "ne"+str(ne)
else:
   grid_name = "ne"+str(ne)+"pg"+str(npg)

mesh_path = "~/Tempest/files_exodus/"
src_mesh_file = mesh_path+"ne30.g"
# src_mesh_file = mesh_path+"ne30pg2.g"
dst_mesh_file = mesh_path+grid_name+".g"

# dst_name = "ne4x2pg2"
# dst_mesh_file = mesh_path+dst_name+".g"

input_root  = "/project/projectdirs/acme/inputdata/atm/cam/inic/homme/"
output_root = "/global/cscratch1/sd/whannah/acme_scratch/init_files/"
# input_root = output_root

map_path = "~/Tempest/files_map/"
overlap_file = map_path+"tmp_overlap_mesh.nc"
mapping_file = map_path+"tmp_mapping_weights.nc "

src_initial_condition = input_root +"cami_aquaplanet_ne30np4_L72_c190215.nc"
dst_initial_condition = output_root+"cami_aquaplanet_"+grid_name+"_L72.nc"


# src_initial_condition = input_root +"cami_mam3_Linoz_ne30np4_L72_c160214.nc"
# src_initial_condition = input_root +"cami_mam3_Linoz_ne30pg2_L72_c160214.nc"
# dst_initial_condition = output_root+"cami_mam3_Linoz_"+grid_name+"_L72_c160214.smoothed.nc"

#---------------------------------------------------------------------------------------------------
# Generate overlap mesh
cmd = tempest_path+"GenerateOverlapMesh "
cmd = cmd+" --a "+src_mesh_file
cmd = cmd+" --b "+dst_mesh_file
cmd = cmd+" --out "+overlap_file
print("\n"+cmd+"\n")
if execute: os.system(cmd)


#---------------------------------------------------------------------------------------------------  
# Generate mapping weights
cmd = tempest_path+"GenerateOfflineMap "
cmd = cmd+" --in_mesh  "+src_mesh_file
cmd = cmd+" --out_mesh "+dst_mesh_file
cmd = cmd+" --ov_mesh "+overlap_file
if npg>0 :
   # cmd = cmd + " --in_type fv  --in_np 1 "
   cmd = cmd + " --in_type cgll  --in_np 4 "
   cmd = cmd + " --out_type fv --out_np 1 "
   cmd = cmd + " --out_double --mono  "
   # cmd = cmd + " --volumetric "
else :
   cmd = cmd + " --in_type cgll  --in_np 4 "
   # cmd = cmd + " --in_type fv  --in_np 1 "
   cmd = cmd + " --out_type cgll --out_np 4 "
   # cmd = cmd + " --out_type fv  --out_np 1 "
   cmd = cmd + " --out_double --mono  "
cmd = cmd+"--out_map "+mapping_file
print("\n"+cmd+"\n")
if execute: os.system(cmd)

#---------------------------------------------------------------------------------------------------
# Apply mapping weights
if npg==0 : grid_name = "ne"+str(ne)+"np4"

cmd = "ncremap -4 -m "+mapping_file+" "+src_initial_condition+" "+dst_initial_condition
print("\n"+cmd+"\n")
if execute: os.system(cmd)
