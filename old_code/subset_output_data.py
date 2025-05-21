#!/usr/bin/env python
#===============================================================================================================================================================
#   This script is used to automate subsetting of E3SM output data
#
#    Jul, 2017  Walter Hannah       Lawrence Livermore National Lab
#
#===============================================================================================================================================================
import sys
import os
import glob
home = os.getenv("HOME")
host = os.getenv("HOST")

if "edison" in host : host = "edison"
if "cori"   in host : host = "cori"
if "blogin" in host : host = "anvil"
if "titan"  in host : host = "titan"

scratch_dir = ""
if host == "titan"  : scratch_dir = "/lustre/atlas1/cli115/scratch/hannah6/"
if host == "edison" : scratch_dir = "/global/cscratch1/sd/whannah/"
if host == "cori"   : scratch_dir = "/global/cscratch1/sd/whannah/"

if scratch_dir=="" :
	print("ERROR: scratch directory not set!  (host="+host+")")
	exit()
#===============================================================================================================================================================
#===============================================================================================================================================================

case = "20161118.beta0.F20TRCOSP.ne30_ne30.edison"

idir = "/global/cscratch1/sd/tang30/E3SM_simulations/"+case+"/run/"

odir = scratch_dir+case+"/"


yr1 = 1997
yr2 = 1997


# files = os.listdir(idir)
files = glob.glob(idir+"*cam.h0*")

for f_in in files : 
	for yr in range(yr1,yr2+1) :
		if str(yr) in f_in :
			print(f_in.replace(idir,""))

			cmd = "cdo   -select,name=time,lev,ncol,lat,lon,nbdate,TAUX,FSNS,FLNS,LHFLX,SHFLX "+f_in+" "+f_in.replace(idir,odir)
			print(cmd)
			os.system(cmd)

			# exit()