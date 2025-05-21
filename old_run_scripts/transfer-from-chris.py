#!/usr/bin/env python
#======================================================================================================================
#   Oct, 2018 - Walter Hannah - Lawrence Livermore National Lab
#   transfer and reorganize history files from Chris Jones (PNNL)
#======================================================================================================================
import os
# home = os.getenv("HOME")

case = "ne120_SP1_72L_32x1_1km_nc720"

src_dir = "/lustre/atlas/proj-shared/cli115/crjones/"+case+"/"
# src_sub_dir = "run/hist/"
src_sub_dir = "run/"

dst_dir = "/lustre/atlas/proj-shared/cli115/hannah6/E3SM/"+case+"/"
dst_sub_dir = "atm/"

verbose  = True
show_cmd = False
execute  = True

if verbose:
    print
    print("    case: "+case)
    print
    print("    src:  "+src_dir+src_sub_dir)
    print("    dst:  "+dst_dir+dst_sub_dir)
    print

#----------------------------------------------------
# make sure the destination directory exists
#----------------------------------------------------
if not os.path.isdir(dst_dir) :

    # create project directory for this case
    tdir = dst_dir
    if not os.path.exists(tdir) : os.makedirs(tdir)

    tdir = dst_dir+dst_sub_dir
    if not os.path.exists(tdir) : os.makedirs(tdir)

#----------------------------------------------------
# loop through the files in the source directory
#----------------------------------------------------

files = sorted( os.listdir(src_dir+src_sub_dir) )

for f_in in files : 

    #----------------------------------
    # copy h0
    #----------------------------------
    if case in f_in and "cam.h0" in f_in :
        f_out = f_in

        cmd = "cp " + src_dir+src_sub_dir+f_in +" "+ dst_dir+dst_sub_dir+f_out
        
        if verbose  : print(f_in+"  >  "+f_out)
        if show_cmd : print(cmd)
        if execute  : os.system(cmd)

    #----------------------------------
    # combine h1+h2 into h1
    #----------------------------------
    if case in f_in and "cam.h1" in f_in :
        cmd_stub = ""
        f_out = f_in
        f_in_h2 = f_in.replace("cam.h1","cam.h2")
        
        cmd = "cp " + src_dir+src_sub_dir+f_in +" "+ dst_dir+dst_sub_dir+f_out
        
        if verbose  : print(f_in+"  >  "+f_out)
        if show_cmd : print(cmd)
        if execute  : os.system(cmd)

        cmd = "ncks -A " + src_dir+src_sub_dir+f_in_h2 +" "+ dst_dir+dst_sub_dir+f_out
        
        if verbose  : print(f_in_h2+"  >  "+f_out)
        if show_cmd : print(cmd)
        if execute  : os.system(cmd)

    #----------------------------------
    # copy h3 as h2
    #----------------------------------
    if case in f_in and "cam.h3" in f_in :
        f_out = f_in.replace("cam.h3","cam.h2")
        
        cmd = "cp " + src_dir+src_sub_dir+f_in +" "+ dst_dir+dst_sub_dir+f_out
        
        if verbose  : print(f_in+"  >  "+f_out)
        if show_cmd : print(cmd)
        if execute  : os.system(cmd)

#======================================================================================================================
#======================================================================================================================