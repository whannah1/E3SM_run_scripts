#!/usr/bin/env python
#===================================================================================================
#   This script is used to regrid individual E3SM output files
#    Mar, 2017  Walter Hannah       Lawrence Livermore National Lab
# 
# To generate new map file:
# ESMF_RegridWeightGen  -s ~/E3SM/data_grid/ne4pg2_scrip.nc 
#                       -d /project/projectdirs/e3sm/mapping/grids/96x144_SCRIP.20160301.nc
#                       -w ~/maps/map_ne4pg2_to_fv96x144_aave.20201120.nc --method conserve
#===================================================================================================
import sys
import os
import subprocess
opsys = os.getenv("os")
home = os.getenv("HOME")
if opsys=="Darwin" :
   host = "mac"
else:
   host = subprocess.check_output(["dnsdomainname"],shell=True, universal_newlines=True).strip()
if host==None : host = os.getenv("host")
if host==None : host = os.getenv("HOST")
if "cori"   in host : host = "cori"
if "blogin" in host : host = "anvil"
if "titan"  in host : host = "titan"
if "rhea"   in host : host = "rhea"
if "summit" in host : host = "summit"

if len(sys.argv) < 2 :
   print("ERROR: no file name provided!")
   exit()
else :
   files = sys.argv[1:]

overwrite = True
log_file = "./regrid.file.out"
#===================================================================================================
#===================================================================================================
for f_in in files : 
   
   remap_flag = True

   if ".remap." in f_in : remap_flag = False
   
   if remap_flag :
      f_out = f_in.replace(".nc",".remap.nc")

      if os.path.isfile(f_out) :
         if overwrite : os.remove(f_out)
         else : continue

      # print("    "+f_in+"  >  "+f_out)

      map_file = ""
      if "ne120" in f_in : map_file = "/project/projectdirs/acme/mapping/maps/map_ne120np4_to_fv800x1600_bilin.20160301.nc"
      if "_ne30"  in f_in : map_file = home+"/maps/map_ne30np4_to_fv128x256_aave.20160301.nc"
      if "_ne16"  in f_in : map_file = home+"/maps/map_ne16np4_to_fv91x180_aave.20170401.nc"
      if "_ne4"   in f_in : map_file = home+"/maps/map_ne4np4_to_fv25x48_aave.20170401.nc"
      if "_ne45pg2" in f_in or ".ne45pg2" in f_in : map_file = home+"/maps/map_ne45pg2_to_cmip6_180x360_aave.20200624.nc"
      # if "_ne30pg2" in f_in or ".ne30pg2" in f_in : map_file = home+"/maps/map_ne30pg2_to_fv128x256_aave.20160301.nc"
      if "_ne30pg2" in f_in or ".ne30pg2" in f_in : map_file = home+"/maps/map_ne30pg2_to_180x360.nc"

      cmd = "ncremap -m "+map_file+" -i "+f_in+" -o "+f_out
      print(cmd+"\n")
      os.system(cmd+" > "+log_file)
      print()
      
#===================================================================================================
#===================================================================================================
