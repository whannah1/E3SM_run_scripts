#!/usr/bin/env python
#===============================================================================================================================================================
#   Jan, 2017 - Walter Hannah - Lawrence Livermore National Lab
#   This script transfers data from scratch space (14 day purge) to project work space (90 purge)
#   re-gridding is also done if needed
#   The modification time is used to make sure the most recent file is transferred
#===============================================================================================================================================================
import sys
import os
# import numpy as np
home = os.getenv("HOME")
host = os.getenv("HOST")

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--old",action="store_true", dest="use_old_scratch", default=False,help="switch to alternate source scratch directory")
(opts, args) = parser.parse_args()

if "edison" in host : host = "edison"
if "blogin" in host : host = "anvil"
if "titan"  in host : host = "titan"

scratch_dir = ""
project_dir = ""
if host == "titan"  : 
    # scratch_dir = "/lustre/atlas/proj-shared/csc249/hannah6/E3SM/"
    if opts.use_old_scratch :
        scratch_dir = "/lustre/atlas/scratch/hannah6/csc249/"
    else :
        scratch_dir = "/lustre/atlas1/cli115/scratch/hannah6/"
     

    # project_dir = "/lustre/atlas/proj-shared/csc249/hannah6/E3SM/"
    project_dir = "/lustre/atlas/proj-shared/cli115/hannah6/E3SM/"


if scratch_dir=="" :
    print("ERROR: scratch directory not set!")
    exit()
if project_dir=="" :
    print("ERROR: project directory not set!")
    exit()
#===============================================================================================================================================================
#===============================================================================================================================================================
do_atm_h0, do_atm_h1, do_atm_h2 = False,False,False
do_lnd_h0, do_lnd_h1 =  False,False
do_rest, overwrite = False,False


# comment/uncomment to disable/enable
do_atm_h0  = True
do_atm_h1  = True
do_atm_h2  = True
do_lnd_h0  = True
do_lnd_h1  = True
do_rest    = True

mv_orig = True      # move original data files?
mv_regr = False     # move regridded data files?
 
# overwrite = True


log_file = "./transfer.out"

# cmd_stub = "mv "
cmd_stub = "cp "


if len(sys.argv) < 2 :
    cases = ["default"]
    print("ERROR: no case name provided!")
    exit()

    # cases = ["E3SM_ZM_AMIP_ne16_00","E3SM_ZM_AMIP_ne30_13"]
    # cases = ["E3SM_ZM_CTL_ne30_00"]
    
    # get all AMIP cases
    # cases = [ item for item in os.listdir(scratch_dir) if os.path.isdir(os.path.join(scratch_dir, item)) and "AMIP" in item ]
    # print cases

else :
    # cases = sys.argv[1:]
    cases = args




#===============================================================================================================================================================
#===============================================================================================================================================================
# num_c = len(cases)
for case in cases :

    # data_dir = home+"/E3SM/scratch/"+case+"/run/"
    # src_dir = scratch_dir+case+"/run/"
    if "proj-shared" in scratch_dir :
        src_dir = scratch_dir+case+"/atm/"
    else :
        src_dir = scratch_dir+case+"/run/"
    
    dst_dir = project_dir+case+"/atm/"
    rst_dir = project_dir+case+"/rest/"

    files = sorted( os.listdir(src_dir) )

    #----------------------------------------------------
    # find the appropriate map for regridding 
    #----------------------------------------------------
    map_file = ""
    if "_ne30" in case : map_file = home+"/maps/map_ne30np4_to_fv128x256_aave.20160301.nc"
    if "_ne16" in case : map_file = home+"/maps/map_ne16np4_to_fv91x180_aave.20170401.nc"
    if "_ne4"  in case : map_file = home+"/maps/map_ne4np4_to_fv25x48_aave.20170401.nc"
    
    #----------------------------------------------------
    # print some info
    #----------------------------------------------------
    print("")
    print("case     : "+case)
    print("src_dir  : "+src_dir)
    print("dst_dir  : "+dst_dir)
    print("map      : "+map_file)
    print("log file : "+log_file)
    print("")

    #----------------------------------------------------
    # make sure the destination directory exists
    #----------------------------------------------------
    if not os.path.isdir(dst_dir) :

        # create project directory for this case
        tdir = project_dir+case
        if not os.path.exists(tdir) : os.makedirs(tdir)

        # directory for atm data
        tdir = project_dir+case+"/atm/"     
        if not os.path.exists(tdir) : os.makedirs(tdir)        

        # directory for vertically interpolated and derived data files - create here for convenience
        tdir = project_dir+case+"/data/"    
        if not os.path.exists(tdir) : os.makedirs(tdir)

    # directory for restart files
    if not os.path.exists(rst_dir) : os.makedirs(rst_dir)

    #----------------------------------------------------
    # find last modification time of restart files
    #----------------------------------------------------
    rest_stub = ['cam.rs.','cam.rh0.','cpl.r.','cam.r.','clm2.r.','cice.r.','clm2.rh0.','cam.rh0.','.bin','rpointer']
    rest_mod_time = []
    rest_max_time = []
    if do_rest :
        
        for f_in in files :
            if (rest_stub[0] in f_in) and ("0.nc" in f_in) : 
                rest_mod_time.append(os.path.getmtime(src_dir+f_in))
        
        if rest_mod_time : 
            rest_max_time = max(rest_mod_time)
        # else :
            # rest_mod_time is empty

    #----------------------------------------------------
    # build list of history file stubs
    #----------------------------------------------------
    hist_stub = []
    if do_atm_h0 : hist_stub.append("cam.h0")
    if do_atm_h1 : hist_stub.append("cam.h1")
    if do_atm_h2 : hist_stub.append("cam.h2")
    if do_lnd_h0 : hist_stub.append("clm2.h0")
    if do_lnd_h1 : hist_stub.append("clm2.h1")

    #----------------------------------------------------
    # loop through the files in the source directory
    #----------------------------------------------------
    for f_in in files : 

        if do_rest and rest_max_time :
            if any(stub in f_in for stub in rest_stub) and ("0.nc" in f_in) :

                ftime = os.path.getmtime(src_dir+f_in)
                time_diff = ftime - rest_max_time

                if abs(time_diff) < 5e3 :
                    f_out = f_in
                    print("  copying : "+src_dir+f_out)
                    cmd = cmd_stub+src_dir+f_out+" "+rst_dir+f_out
                    # print(cmd)
                    os.system(cmd+" > "+log_file)
                    # os.system("chmod 644 "+dst_dir+f_out+"/*/*/*")
                    os.system("chmod 644 "+rst_dir+f_out)

        # check if the file is an atm history file
        # if any(stub in f_in for stub in hist_stub) and ("0.nc" in f_in) :
        if any(stub in f_in for stub in hist_stub) :

            #----------------------------------------------------
            # move regridded data files
            #----------------------------------------------------
            if mv_regr :
                f_out = f_in.replace(".nc",".remap.nc")
                # regrid data if not already done
                if not os.path.isfile(src_dir+f_out) : 
                    print("  regridding : "+f_in+"  >  "+src_dir+f_out)
                    cmd = "ncremap -m "+map_file+" -i "+src_dir+f_in+" -o "+src_dir+f_out
                    os.system(cmd+" > "+log_file)

                # move regridded files
                print("  moving  : "+src_dir+f_out)
                cmd = cmd_stub+src_dir+f_out+" "+dst_dir+f_out
                # print(cmd)
                os.system(cmd+" > "+log_file)
                # os.system("chmod 644 "+dst_dir+f_out+"/*/*/*")
            #----------------------------------------------------
            # move original data files
            # use file size to overwirte partial files
            #----------------------------------------------------
            if mv_orig :
                f_out = f_in
                proceed = False
                if os.path.isfile(dst_dir+f_out) and (os.stat(src_dir+f_in).st_size > os.stat(dst_dir+f_in).st_size) : proceed = True
                if not os.path.isfile(dst_dir+f_out) : proceed = True
                if proceed :
                    print("  copying : "+dst_dir+f_out)
                    cmd = cmd_stub+src_dir+f_in+" "+dst_dir+f_out
                    # print(cmd)
                    os.system(cmd+" > "+log_file)
                    #os.system("chmod 644 "+dst_dir+f_out+"/*/*/*")
                    # exit()

            # print
    #----------------------------------------------------
    #----------------------------------------------------

    # os.system("chmod 644 "+project_dir+"/*/*/*")
    os.system("chmod 644 "+rst_dir+"*")
    
    print("")
    print("-------------------------------------------------------------------------------------------")

#===============================================================================================================================================================
#===============================================================================================================================================================
