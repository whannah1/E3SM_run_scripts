#!/usr/bin/env python
#===============================================================================================================================================================
#   This script runs an ensemble of ACME simulations
#
#    Jan, 2017  Walter Hannah       Lawrence Livermore National Lab
#
#===============================================================================================================================================================
import sys
import os
import getopt
from optparse import OptionParser
import shutil
import time
from subprocess import Popen, PIPE

# import numpy as np
home = os.getenv("HOME")
host = os.getenv("HOST")

if "edison" in host : host = "edison"
if "blogin" in host : host = "anvil"
if "titan"  in host : host = "titan"

#===============================================================================================================================================================
#===============================================================================================================================================================

overwrite = False

# res = "1.9x2.5"
res = "ne30"
cld = "SP1"
nf  = 1

crm_nx = 64
crm_ny = 1

# crm_nx_rad = [crm_nx,4,1]
crm_nx_rad = [32,1]
# crm_nx_rad = crm_nx
# crm_nx_rad = 4
# crm_nx_rad = 1


# crmdim = "_"+str(crm_nx)+"x"+str(crm_ny)
# crmdim = "_"+str(crm_nx)+"x"+str(crm_ny)+"_nr"+crm_nx_rad
# if "ZM" in cld : crmdim = ""

load_bal	= False
master_flag = False
UM5_flag	= False
# rrtmg_flag  = False

crmdim  = ""
mod_str = ""
if "SP" in cld :
    # crmdim = "_"+str(crm_nx)+"x"+str(crm_ny) 
    # crmdim = "_"+str(crm_nx)+"x"+str(crm_ny)+"_nr"+str(crm_nx_rad)
    if crm_nx==32  : mod_str = mod_str = "_2km"
    if crm_nx==64  : mod_str = mod_str = "_1km"
    if crm_nx==128 : mod_str = mod_str = "_0.5km"

if master_flag : mod_str = mod_str+"_master"
if UM5_flag    : mod_str = mod_str+"_UM5"  
if load_bal    : mod_str = mod_str+"_LB2"  
# if rrtmg_flag  : mod_str = mod_str+"_rrtmg"  

mod_flag = ""
if master_flag : mod_flag = mod_flag+" --master "
if UM5_flag    : mod_flag = mod_flag+" --UM5 "
if load_bal    : mod_flag = mod_flag+" --LB2 "
# if rrtmg_flag  : mod_flag = mod_flag+" --rrtmg "

# ntask = [64,128,256,512,1024,2048]

# if res=="ne4"  : ntask = [16,32,64,128,256,512]
# if res=="ne16" : ntask = [64,128,256,512,1024]

# if res=="ne4"  : ntask = [  24,  48,  96,  192,  384, 768, 1536]
# if res=="ne16" : ntask = [ 384, 768,1536, 3072, 6144]
# if res=="ne30" : ntask = [1350,2700,5400,10800]


if nf==1 :
	if res=="1.9x2.5" : ntask = [ 256 ] 
	
	# if res=="ne4"  : ntask = [  866 ] 
	# if res=="ne4"  : ntask = [  433, 866] 
	if res=="ne4"  : ntask = [  24, 48, 96,  192,  384, 768, 55, 109, 217, 433, 866] 
	# if res=="ne4"  : ntask = [  3072, 6144,12288] 
	# if res=="ne16" : ntask = [ 1729, 3072, 6144, 3457, 6913, 12288, 13826 ]
	if res=="ne16" : ntask = [ 1729 ]
	# if res=="ne16" : ntask = [ 865, 1536, 1729, 3072, 6144, 3457, 6913, 12288, 13826 ]
	# if res=="ne30" : ntask = [ 6076 ]
	if res=="ne30" : ntask = [ 5400 ]
	# if res=="ne30" : ntask = [ 21600, 24301, 43200, 48602 ]
	# if res=="ne30" : ntask = [ 2700, 3038, 5400, 6076, 10800, 12151, 21600, 24301, 43200, 48602]

if nf==4 :
	# start at 4 proc per element
	# if res=="ne4"  : ntask = [  433, 866] 
	# if res=="ne4"  : ntask = [  24,  48,  96, 192, 384]
	# if res=="ne4"  : ntask = [  768, 1536]
	if res=="ne16" : ntask = [ 6913 ]
	# if res=="ne16" : ntask = [ 384, 768,1536, 3072, 6144]
	# if res=="ne16" : ntask = [ 3072, 6144,12288]
	# if res=="ne30" : ntask = [1350,2700,5400,10800]
	if res=="ne30" : ntask = [10800]

# if nf== 2 : if res=="ne30" : ntask = [5400]
# if nf== 6 : if res=="ne30" : ntask = [5400]
# if nf== 8 : if res=="ne30" : ntask = [5400]
# if nf==12 : if res=="ne30" : ntask = [5400]

# if cld=="ZM" and nf==1 and res=="ne16" : ntask = [1536, 3072, 6144 , 3457, 6913, 13826]
# if cld=="ZM" and nf==1 and res=="ne4"  : ntask = [433]
# if cld=="ZM" and nf==1 and res=="ne16" : ntask = [3072, 3457, 6144]
# if cld=="ZM" and nf==1 and res=="ne16" : ntask = [1536]
# if cld=="ZM" and nf==1 and res=="ne30" : ntask = [5400,10800,12151,21600,24301,48602]


# ntask = [384]
n = ntask[0]

# for n in ntask :
for nr in crm_nx_rad :

	crmdim  = ""
	if "SP" in cld :
		crmdim = "_"+str(crm_nx)+"x"+str(crm_ny)+"_nr"+str(nr)

	case_num = str(n)
	nfac = str(nf)

	case_name = "ACME_timing2_"+res+crmdim+"_"+cld+mod_str+"_f"+nfac+"_"+case_num

	#----------------------------------------------------
	# remove directories of previous runs
	#----------------------------------------------------
	if overwrite :
		paths = []
		# paths.append( "/ccs/home/hannah6/acme_scratch/cli115/"+case_name )
		paths.append( "/ccs/home/hannah6/ACME/Cases/"+case_name )
		paths.append( "/lustre/atlas1/cli115/scratch/hannah6/"+case_name )
		# paths.append( "/lustre/atlas/scratch/hannah6/csc249/"+case_name )
		# paths.append( "/ccs/home/hannah6/acme_scratch/csc249/"+case_name )
		
		print("Checking for old directories...")
		rm_flag = False
		for path in paths :
			if os.path.isdir(path) :
				print("  {:<70}".format(path)+"  : -- path exists -- this will be deleted!")
				rm_flag = True
			else :
				print("  {:<70}".format(path)+"  : does not exist ")

		if rm_flag : time.sleep(5) # in case the user changes their mind and wants to abort

		for path in paths :
			if os.path.isdir(path) :
				shutil.rmtree(path)
	#----------------------------------------------------
	#----------------------------------------------------

	log_file = home+"/ACME/ensemble_term_output/"+case_name+".out"

	crm_arg = ""
	if "SP" in cld : 
		crm_arg = "  --crm_nx "+str(crm_nx)+" --crm_ny "+str(crm_ny)
		crm_arg = crm_arg + "  --crm_nx_rad "+str(nr) 

	cmd = "nohup ./run_ACME.timing.py  -g "+res+" -c "+cld+"  -n "+str(n)+"  -f "+str(nf)+crm_arg+"  "+mod_flag+" &>  "+log_file # +" & "
	# cmd_list = cmd.split(' ')
	print(cmd)
	
	print("")
	print("STOPPING - no command is issued.")
	exit()

	proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
	out, err = proc.communicate()
	
	# os.system(cmd)




#===============================================================================================================================================================
#===============================================================================================================================================================
