#!/usr/bin/env python
import os
import subprocess as sp
import glob
from optparse import OptionParser
class tcolor:
   ENDC,RED,GREEN,YELLOW,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m'
#-------------------------------------------------------------------------------
# Set up option parser
#-------------------------------------------------------------------------------
parser = OptionParser()
parser.add_option('-c',dest='case',default='', help='case name to be processed')
parser.add_option('-s',dest='yr1', default='1',help='start year of climatology')
parser.add_option('-e',dest='yr2', default='5',help='last year of climatology')
(opts, args) = parser.parse_args()

if opts.case=='' : exit('ERROR: no case name provided!')

#-------------------------------------------------------------------------------
# Figure out which machine we're on
#-------------------------------------------------------------------------------
# host = sp.check_output(["dnsdomainname"],universal_newlines=True).strip()
# if 'nersc' in host : host = None
# if host==None : host = os.getenv("host")
# if host==None : host = os.getenv("HOST")
# opsys = os.getenv("os")
# if opsys=="Darwin"  : host = "mac"
# if "cori"   in host : host = "cori-knl"
# if "summit" in host : host = "summit" 

#-------------------------------------------------------------------------------
# Set up directory paths and create output dir if it doesn't exist
#-------------------------------------------------------------------------------
# data_top_dir = '~/Data/E3SM/'
# if host=='cori-knl': data_top_dir = '/global/cscratch1/sd/whannah/acme_scratch/cori-knl/'

data_top_dir = '/global/cscratch1/sd/whannah/e3sm_scratch/cori-knl/'

# idir = data_top_dir+'/'+opts.case+'/data_remap_90x180/'
idir = data_top_dir+'/'+opts.case+'/run/'
odir = data_top_dir+'/'+opts.case+'/clim/'

if not os.path.exists(odir) : os.makedirs(odir)
#-------------------------------------------------------------------------------
# Specify mapping file
#-------------------------------------------------------------------------------
if 'ne30_'     in opts.case: src_grid_name = 'ne30np4'
if 'ne30pg2_'  in opts.case: src_grid_name = 'ne30pg2'
if 'ne30pg3_'  in opts.case: src_grid_name = 'ne30pg3'
if 'ne30pg4_'  in opts.case: src_grid_name = 'ne30pg4'
if 'ne120pg2_' in opts.case: src_grid_name = 'ne30pg2'

if 'src_grid_name' in locals():
  # nlat_dst,nlon_dst = 90,180
  nlat_dst,nlon_dst = 180,360
  # if 'np4' in src_grid_name:
  #   map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}.nc'
  # else:
  #   map_file = f'{home}/maps/map_{src_grid_name}_to_{nlat_dst}x{nlon_dst}_aave.nc'
  map_file = f'$HOME/maps/map_{src_grid_name}_to_cmip6_{nlat_dst}x{nlon_dst}_aave.20200624.nc'

#-------------------------------------------------------------------------------
# Create climatologies
#-------------------------------------------------------------------------------
cmd = 'ncclimo '
cmd = cmd+' -c '+opts.case
cmd = cmd+' -a sdd '             # seasonally discontinuous December 
cmd = cmd+' -s '+opts.yr1+' -e '+opts.yr2+' '
cmd = cmd+' -i '+idir+' -o '+odir
cmd = cmd+' -O '+odir
if 'map_file' in locals(): cmd = cmd+' --map='+map_file

print('\n'+tcolor.GREEN+cmd+tcolor.ENDC+'\n')
try:
  sp.check_output(cmd,shell=True,universal_newlines=True)
except sp.CalledProcessError as error:
  print(error.output)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------