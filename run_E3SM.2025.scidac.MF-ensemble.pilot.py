#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np, hashlib
from shutil import copy2
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
''' Notes
defaults from case => /pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/E3SM.2025-MF-test-00.ne30pg2.F20TR.NN_32/run/atm_in
 effgw_beres               =  0.35
 gw_convect_hcf            =  10.0
 hdepth_scaling_factor     =  0.50
 gw_convect_hdepth_min     = 2.5
 gw_convect_plev_src_wind  = 70000
 frontgfc                  = 1.25D-15  =>  7.4925 = 1.25e-15 * (360*111/(30*4*2)) * 3600e10
 effgw_cm                  = 1.D0
 taubgnd                   = 2.5D-3
 effgw_oro                 = 0.375

Initial conditions - use HICCUP script: ~/HICCUP/user_scripts/2025-SciDAC-multifidelity-create_EAM_IC_from_EAM.horz_only.py

nohup python -u ~/E3SM/run_E3SM.2025.scidac.MF-ensemble.pilot.py > ~/E3SM/run_E3SM.2025.scidac.MF-ensemble.pilot.out &

oct 10 - ne26 / ne22 / ne18 @ login12

'''
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm4310'
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # branch => whannah/scidac-2025-multifidelity

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

disable_bfb = False

queue = 'regular' # regular / debug

# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,  0,  '2:00:00' #  1 year
stop_opt,stop_n,resub,walltime = 'ndays',365*5,2-1,'10:00:00' # 10 years

#---------------------------------------------------------------------------------------------------
# add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.350, CF=10.00, HD=0.500, HM=2.500, PS=700.0, FT= 7.4925, FE=1.000, OB=0.002500, OE=0.375) # v3 defaults
# add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.350, CF=10.00, HD=0.500, HM=2.500, PS=700.0, FT= 7.4925, FE=1.000, OB=0.002500, OE=0.375) # v3 defaults
# add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.350, CF=10.00, HD=0.500, HM=2.500, PS=700.0, FT= 7.4925, FE=1.000, OB=0.002500, OE=0.375) # v3 defaults
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.350, CF=10.00, HD=0.500, HM=2.500, PS=700.0, FT= 7.4925, FE=1.000, OB=0.002500, OE=0.375) # v3 defaults

# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.258, CF= 7.96, HD=1.013, HM=2.327, PS=893.9, FT=24.0591, FE=0.477, OB=0.004277, OE=0.502)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.104, CF= 9.01, HD=1.449, HM=2.970, PS=617.5, FT=37.4295, FE=0.098, OB=0.005117, OE=0.267)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.497, CF=16.44, HD=0.727, HM=2.156, PS=693.2, FT=32.6917, FE=0.801, OB=0.006306, OE=0.239)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.206, CF= 6.95, HD=1.114, HM=2.222, PS=544.0, FT=26.8732, FE=0.625, OB=0.007590, OE=0.136)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.864, CF=18.31, HD=1.460, HM=2.158, PS=780.7, FT=45.3363, FE=0.655, OB=0.000796, OE=0.838)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.882, CF= 8.92, HD=0.911, HM=2.354, PS=624.8, FT=20.3930, FE=0.503, OB=0.009547, OE=0.865)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.766, CF=17.02, HD=1.219, HM=1.211, PS=805.5, FT=18.8529, FE=0.982, OB=0.005674, OE=0.393)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.636, CF= 6.22, HD=0.718, HM=1.073, PS=669.8, FT=33.2284, FE=0.247, OB=0.003074, OE=0.423)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.675, CF= 5.04, HD=1.195, HM=4.715, PS=929.7, FT=30.6970, FE=0.367, OB=0.006921, OE=0.629)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.182, CF=13.10, HD=0.607, HM=4.185, PS=879.7, FT=12.4441, FE=0.859, OB=0.009861, OE=0.934)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.063, CF=19.48, HD=0.954, HM=2.271, PS=787.4, FT=47.8909, FE=0.060, OB=0.009084, OE=0.755)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.075, CF= 6.31, HD=0.881, HM=2.909, PS=708.9, FT=25.7578, FE=0.919, OB=0.001912, OE=0.206)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.728, CF= 9.27, HD=0.459, HM=3.764, PS=700.1, FT=17.2012, FE=0.442, OB=0.006580, OE=0.091)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.420, CF= 8.23, HD=1.003, HM=2.455, PS=686.2, FT=41.3869, FE=0.370, OB=0.001089, OE=0.968)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.842, CF=10.16, HD=1.398, HM=3.206, PS=770.3, FT= 5.7825, FE=0.494, OB=0.006828, OE=0.476)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.602, CF=15.58, HD=0.890, HM=1.111, PS=778.0, FT=23.5953, FE=0.206, OB=0.008406, OE=0.912)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.070, CF=16.09, HD=1.377, HM=1.935, PS=875.3, FT= 6.7562, FE=0.430, OB=0.002318, OE=0.295)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.891, CF=10.11, HD=0.426, HM=1.576, PS=939.3, FT=31.3464, FE=0.362, OB=0.007056, OE=0.081)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.337, CF=19.45, HD=0.296, HM=4.409, PS=752.6, FT=16.4815, FE=0.095, OB=0.004069, OE=0.236)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.198, CF=10.90, HD=1.211, HM=4.334, PS=684.1, FT=44.1856, FE=0.561, OB=0.008999, OE=0.412)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.777, CF=15.08, HD=1.060, HM=4.226, PS=755.4, FT=20.1310, FE=0.297, OB=0.001896, OE=0.719)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.859, CF= 8.39, HD=0.825, HM=3.956, PS=842.0, FT=49.2608, FE=0.188, OB=0.003559, OE=0.190)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.612, CF= 9.65, HD=0.649, HM=1.157, PS=711.0, FT=44.5606, FE=0.721, OB=0.006997, OE=0.892)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.654, CF=11.00, HD=0.319, HM=3.228, PS=539.7, FT=29.8784, FE=0.759, OB=0.004778, OE=0.462)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.140, CF= 7.44, HD=0.291, HM=2.672, PS=754.7, FT= 8.2686, FE=0.203, OB=0.000598, OE=0.955)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.320, CF=10.64, HD=0.980, HM=1.134, PS=875.5, FT=20.7423, FE=0.094, OB=0.006341, OE=0.093)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.159, CF= 5.94, HD=1.165, HM=2.052, PS=815.9, FT=27.8530, FE=0.695, OB=0.007402, OE=0.104)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.441, CF= 6.37, HD=0.733, HM=2.429, PS=942.7, FT=34.2648, FE=0.657, OB=0.006773, OE=0.981)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.257, CF=11.21, HD=0.832, HM=3.928, PS=935.7, FT=49.8922, FE=0.761, OB=0.003623, OE=0.198)
# add_case(prefix='E3SM.2025-MF0',g='ne30',EF=0.084, CF=17.94, HD=0.324, HM=1.620, PS=846.6, FT=22.6030, FE=0.731, OB=0.002902, OE=0.276)

add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.258, CF= 7.96, HD=1.013, HM=2.327, PS=893.9, FT=24.0591, FE=0.477, OB=0.004277, OE=0.502)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.104, CF= 9.01, HD=1.449, HM=2.970, PS=617.5, FT=37.4295, FE=0.098, OB=0.005117, OE=0.267)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.497, CF=16.44, HD=0.727, HM=2.156, PS=693.2, FT=32.6917, FE=0.801, OB=0.006306, OE=0.239)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.206, CF= 6.95, HD=1.114, HM=2.222, PS=544.0, FT=26.8732, FE=0.625, OB=0.007590, OE=0.136)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.864, CF=18.31, HD=1.460, HM=2.158, PS=780.7, FT=45.3363, FE=0.655, OB=0.000796, OE=0.838)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.882, CF= 8.92, HD=0.911, HM=2.354, PS=624.8, FT=20.3930, FE=0.503, OB=0.009547, OE=0.865)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.766, CF=17.02, HD=1.219, HM=1.211, PS=805.5, FT=18.8529, FE=0.982, OB=0.005674, OE=0.393)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.636, CF= 6.22, HD=0.718, HM=1.073, PS=669.8, FT=33.2284, FE=0.247, OB=0.003074, OE=0.423)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.675, CF= 5.04, HD=1.195, HM=4.715, PS=929.7, FT=30.6970, FE=0.367, OB=0.006921, OE=0.629)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.182, CF=13.10, HD=0.607, HM=4.185, PS=879.7, FT=12.4441, FE=0.859, OB=0.009861, OE=0.934)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.063, CF=19.48, HD=0.954, HM=2.271, PS=787.4, FT=47.8909, FE=0.060, OB=0.009084, OE=0.755)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.075, CF= 6.31, HD=0.881, HM=2.909, PS=708.9, FT=25.7578, FE=0.919, OB=0.001912, OE=0.206)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.728, CF= 9.27, HD=0.459, HM=3.764, PS=700.1, FT=17.2012, FE=0.442, OB=0.006580, OE=0.091)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.420, CF= 8.23, HD=1.003, HM=2.455, PS=686.2, FT=41.3869, FE=0.370, OB=0.001089, OE=0.968)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.842, CF=10.16, HD=1.398, HM=3.206, PS=770.3, FT= 5.7825, FE=0.494, OB=0.006828, OE=0.476)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.602, CF=15.58, HD=0.890, HM=1.111, PS=778.0, FT=23.5953, FE=0.206, OB=0.008406, OE=0.912)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.070, CF=16.09, HD=1.377, HM=1.935, PS=875.3, FT= 6.7562, FE=0.430, OB=0.002318, OE=0.295)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.891, CF=10.11, HD=0.426, HM=1.576, PS=939.3, FT=31.3464, FE=0.362, OB=0.007056, OE=0.081)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.337, CF=19.45, HD=0.296, HM=4.409, PS=752.6, FT=16.4815, FE=0.095, OB=0.004069, OE=0.236)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.198, CF=10.90, HD=1.211, HM=4.334, PS=684.1, FT=44.1856, FE=0.561, OB=0.008999, OE=0.412)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.777, CF=15.08, HD=1.060, HM=4.226, PS=755.4, FT=20.1310, FE=0.297, OB=0.001896, OE=0.719)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.859, CF= 8.39, HD=0.825, HM=3.956, PS=842.0, FT=49.2608, FE=0.188, OB=0.003559, OE=0.190)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.612, CF= 9.65, HD=0.649, HM=1.157, PS=711.0, FT=44.5606, FE=0.721, OB=0.006997, OE=0.892)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.654, CF=11.00, HD=0.319, HM=3.228, PS=539.7, FT=29.8784, FE=0.759, OB=0.004778, OE=0.462)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.140, CF= 7.44, HD=0.291, HM=2.672, PS=754.7, FT= 8.2686, FE=0.203, OB=0.000598, OE=0.955)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.320, CF=10.64, HD=0.980, HM=1.134, PS=875.5, FT=20.7423, FE=0.094, OB=0.006341, OE=0.093)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.159, CF= 5.94, HD=1.165, HM=2.052, PS=815.9, FT=27.8530, FE=0.695, OB=0.007402, OE=0.104)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.441, CF= 6.37, HD=0.733, HM=2.429, PS=942.7, FT=34.2648, FE=0.657, OB=0.006773, OE=0.981)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.257, CF=11.21, HD=0.832, HM=3.928, PS=935.7, FT=49.8922, FE=0.761, OB=0.003623, OE=0.198)
add_case(prefix='E3SM.2025-MF0',g='ne26',EF=0.084, CF=17.94, HD=0.324, HM=1.620, PS=846.6, FT=22.6030, FE=0.731, OB=0.002902, OE=0.276)

add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.258, CF= 7.96, HD=1.013, HM=2.327, PS=893.9, FT=24.0591, FE=0.477, OB=0.004277, OE=0.502)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.104, CF= 9.01, HD=1.449, HM=2.970, PS=617.5, FT=37.4295, FE=0.098, OB=0.005117, OE=0.267)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.497, CF=16.44, HD=0.727, HM=2.156, PS=693.2, FT=32.6917, FE=0.801, OB=0.006306, OE=0.239)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.206, CF= 6.95, HD=1.114, HM=2.222, PS=544.0, FT=26.8732, FE=0.625, OB=0.007590, OE=0.136)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.864, CF=18.31, HD=1.460, HM=2.158, PS=780.7, FT=45.3363, FE=0.655, OB=0.000796, OE=0.838)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.882, CF= 8.92, HD=0.911, HM=2.354, PS=624.8, FT=20.3930, FE=0.503, OB=0.009547, OE=0.865)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.766, CF=17.02, HD=1.219, HM=1.211, PS=805.5, FT=18.8529, FE=0.982, OB=0.005674, OE=0.393)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.636, CF= 6.22, HD=0.718, HM=1.073, PS=669.8, FT=33.2284, FE=0.247, OB=0.003074, OE=0.423)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.675, CF= 5.04, HD=1.195, HM=4.715, PS=929.7, FT=30.6970, FE=0.367, OB=0.006921, OE=0.629)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.182, CF=13.10, HD=0.607, HM=4.185, PS=879.7, FT=12.4441, FE=0.859, OB=0.009861, OE=0.934)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.063, CF=19.48, HD=0.954, HM=2.271, PS=787.4, FT=47.8909, FE=0.060, OB=0.009084, OE=0.755)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.075, CF= 6.31, HD=0.881, HM=2.909, PS=708.9, FT=25.7578, FE=0.919, OB=0.001912, OE=0.206)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.728, CF= 9.27, HD=0.459, HM=3.764, PS=700.1, FT=17.2012, FE=0.442, OB=0.006580, OE=0.091)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.420, CF= 8.23, HD=1.003, HM=2.455, PS=686.2, FT=41.3869, FE=0.370, OB=0.001089, OE=0.968)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.842, CF=10.16, HD=1.398, HM=3.206, PS=770.3, FT= 5.7825, FE=0.494, OB=0.006828, OE=0.476)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.602, CF=15.58, HD=0.890, HM=1.111, PS=778.0, FT=23.5953, FE=0.206, OB=0.008406, OE=0.912)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.070, CF=16.09, HD=1.377, HM=1.935, PS=875.3, FT= 6.7562, FE=0.430, OB=0.002318, OE=0.295)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.891, CF=10.11, HD=0.426, HM=1.576, PS=939.3, FT=31.3464, FE=0.362, OB=0.007056, OE=0.081)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.337, CF=19.45, HD=0.296, HM=4.409, PS=752.6, FT=16.4815, FE=0.095, OB=0.004069, OE=0.236)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.198, CF=10.90, HD=1.211, HM=4.334, PS=684.1, FT=44.1856, FE=0.561, OB=0.008999, OE=0.412)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.777, CF=15.08, HD=1.060, HM=4.226, PS=755.4, FT=20.1310, FE=0.297, OB=0.001896, OE=0.719)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.859, CF= 8.39, HD=0.825, HM=3.956, PS=842.0, FT=49.2608, FE=0.188, OB=0.003559, OE=0.190)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.612, CF= 9.65, HD=0.649, HM=1.157, PS=711.0, FT=44.5606, FE=0.721, OB=0.006997, OE=0.892)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.654, CF=11.00, HD=0.319, HM=3.228, PS=539.7, FT=29.8784, FE=0.759, OB=0.004778, OE=0.462)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.140, CF= 7.44, HD=0.291, HM=2.672, PS=754.7, FT= 8.2686, FE=0.203, OB=0.000598, OE=0.955)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.320, CF=10.64, HD=0.980, HM=1.134, PS=875.5, FT=20.7423, FE=0.094, OB=0.006341, OE=0.093)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.159, CF= 5.94, HD=1.165, HM=2.052, PS=815.9, FT=27.8530, FE=0.695, OB=0.007402, OE=0.104)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.441, CF= 6.37, HD=0.733, HM=2.429, PS=942.7, FT=34.2648, FE=0.657, OB=0.006773, OE=0.981)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.257, CF=11.21, HD=0.832, HM=3.928, PS=935.7, FT=49.8922, FE=0.761, OB=0.003623, OE=0.198)
add_case(prefix='E3SM.2025-MF0',g='ne22',EF=0.084, CF=17.94, HD=0.324, HM=1.620, PS=846.6, FT=22.6030, FE=0.731, OB=0.002902, OE=0.276)

add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.258, CF= 7.96, HD=1.013, HM=2.327, PS=893.9, FT=24.0591, FE=0.477, OB=0.004277, OE=0.502)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.104, CF= 9.01, HD=1.449, HM=2.970, PS=617.5, FT=37.4295, FE=0.098, OB=0.005117, OE=0.267)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.497, CF=16.44, HD=0.727, HM=2.156, PS=693.2, FT=32.6917, FE=0.801, OB=0.006306, OE=0.239)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.206, CF= 6.95, HD=1.114, HM=2.222, PS=544.0, FT=26.8732, FE=0.625, OB=0.007590, OE=0.136)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.864, CF=18.31, HD=1.460, HM=2.158, PS=780.7, FT=45.3363, FE=0.655, OB=0.000796, OE=0.838)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.882, CF= 8.92, HD=0.911, HM=2.354, PS=624.8, FT=20.3930, FE=0.503, OB=0.009547, OE=0.865)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.766, CF=17.02, HD=1.219, HM=1.211, PS=805.5, FT=18.8529, FE=0.982, OB=0.005674, OE=0.393)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.636, CF= 6.22, HD=0.718, HM=1.073, PS=669.8, FT=33.2284, FE=0.247, OB=0.003074, OE=0.423)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.675, CF= 5.04, HD=1.195, HM=4.715, PS=929.7, FT=30.6970, FE=0.367, OB=0.006921, OE=0.629)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.182, CF=13.10, HD=0.607, HM=4.185, PS=879.7, FT=12.4441, FE=0.859, OB=0.009861, OE=0.934)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.063, CF=19.48, HD=0.954, HM=2.271, PS=787.4, FT=47.8909, FE=0.060, OB=0.009084, OE=0.755)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.075, CF= 6.31, HD=0.881, HM=2.909, PS=708.9, FT=25.7578, FE=0.919, OB=0.001912, OE=0.206)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.728, CF= 9.27, HD=0.459, HM=3.764, PS=700.1, FT=17.2012, FE=0.442, OB=0.006580, OE=0.091)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.420, CF= 8.23, HD=1.003, HM=2.455, PS=686.2, FT=41.3869, FE=0.370, OB=0.001089, OE=0.968)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.842, CF=10.16, HD=1.398, HM=3.206, PS=770.3, FT= 5.7825, FE=0.494, OB=0.006828, OE=0.476)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.602, CF=15.58, HD=0.890, HM=1.111, PS=778.0, FT=23.5953, FE=0.206, OB=0.008406, OE=0.912)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.070, CF=16.09, HD=1.377, HM=1.935, PS=875.3, FT= 6.7562, FE=0.430, OB=0.002318, OE=0.295)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.891, CF=10.11, HD=0.426, HM=1.576, PS=939.3, FT=31.3464, FE=0.362, OB=0.007056, OE=0.081)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.337, CF=19.45, HD=0.296, HM=4.409, PS=752.6, FT=16.4815, FE=0.095, OB=0.004069, OE=0.236)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.198, CF=10.90, HD=1.211, HM=4.334, PS=684.1, FT=44.1856, FE=0.561, OB=0.008999, OE=0.412)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.777, CF=15.08, HD=1.060, HM=4.226, PS=755.4, FT=20.1310, FE=0.297, OB=0.001896, OE=0.719)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.859, CF= 8.39, HD=0.825, HM=3.956, PS=842.0, FT=49.2608, FE=0.188, OB=0.003559, OE=0.190)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.612, CF= 9.65, HD=0.649, HM=1.157, PS=711.0, FT=44.5606, FE=0.721, OB=0.006997, OE=0.892)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.654, CF=11.00, HD=0.319, HM=3.228, PS=539.7, FT=29.8784, FE=0.759, OB=0.004778, OE=0.462)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.140, CF= 7.44, HD=0.291, HM=2.672, PS=754.7, FT= 8.2686, FE=0.203, OB=0.000598, OE=0.955)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.320, CF=10.64, HD=0.980, HM=1.134, PS=875.5, FT=20.7423, FE=0.094, OB=0.006341, OE=0.093)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.159, CF= 5.94, HD=1.165, HM=2.052, PS=815.9, FT=27.8530, FE=0.695, OB=0.007402, OE=0.104)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.441, CF= 6.37, HD=0.733, HM=2.429, PS=942.7, FT=34.2648, FE=0.657, OB=0.006773, OE=0.981)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.257, CF=11.21, HD=0.832, HM=3.928, PS=935.7, FT=49.8922, FE=0.761, OB=0.003623, OE=0.198)
add_case(prefix='E3SM.2025-MF0',g='ne18',EF=0.084, CF=17.94, HD=0.324, HM=1.620, PS=846.6, FT=22.6030, FE=0.731, OB=0.002902, OE=0.276)

#---------------------------------------------------------------------------------------------------
compset        = 'F20TR'
din_loc_root   = '/global/cfs/cdirs/e3sm/inputdata'
init_root      = '/global/cfs/cdirs/m4310/whannah/E3SM/init_data/v3.LR.amip_0101/archive/rest/2000-01-01-00000'
lnd_init_file  = f'{init_root}/v3.LR.amip_0101.elm.r.2000-01-01-00000.nc'
lnd_data_root  = f'{din_loc_root}/lnd/clm2/surfdata_map'
lnd_data_file  = f'{lnd_data_root}/surfdata_0.5x0.5_simyr1850_c200609_with_TOP.nc'
lnd_luse_file  = f'{lnd_data_root}/landuse.timeseries_0.5x0.5_hist_simyr1850-2015_c240308.nc'
RUN_START_DATE = '1995-01-01'
# atm_init_file  = f'{init_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000.nc'
#---------------------------------------------------------------------------------------------------
def main(opts):
   global debug_mode, compset, din_loc_root, init_root, lnd_init_file, lnd_data_root, lnd_data_file, lnd_luse_file, RUN_START_DATE

   grid_short = opts['g']
   if grid_short=='ne18': grid = 'ne18pg2_r05_IcoswISC30E3r5'; num_nodes=12; ne=18
   if grid_short=='ne22': grid = 'ne22pg2_r05_IcoswISC30E3r5'; num_nodes=18; ne=22
   if grid_short=='ne26': grid = 'ne26pg2_r05_IcoswISC30E3r5'; num_nodes=24; ne=26
   if grid_short=='ne30': grid = 'ne30pg2_r05_IcoswISC30E3r5'; num_nodes=32; ne=30
   #----------------------------------------------------------------------------
   case_list = []
   for key,val in opts.items(): 
      if key in ['prefix']:
         case_list.append(val)
      # elif key in ['num_nodes']:
      #    case_list.append(f'NN_{val}')
      elif key in ['g']:
         case_list.append(grid_short)
      elif key in ['debug']:
         case_list.append('debug')
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            fmt = 'g'
            if key in ['EF','CF','HD','HM','PS','FT','FE','OB','OE']: fmt = '0.3f'
            if key=='CF':fmt='05.2f'
            if key=='PS':fmt='05.1f'
            if key=='FT':fmt='07.4f'
            if key=='OB':fmt='0.6f'
            case_list.append(f'{key}_{val:{fmt}}')

   #----------------------------------------------------------------------------
   case = '.'.join(case_list)
   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
   #----------------------------------------------------------------------------
   opts['dx']=360*111/(ne*4*2)
   # alt_init_root = '/global/cfs/cdirs/m4310/whannah/E3SM/init_data'
   alt_init_root = '/global/cfs/cdirs/m4310/whannah/files_init'
   atm_init_file = None
   if grid_short=='ne18': atm_init_file  = f'{alt_init_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000.ne18np4.20251001.nc'
   if grid_short=='ne22': atm_init_file  = f'{alt_init_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000.ne22np4.20251001.nc'
   if grid_short=='ne26': atm_init_file  = f'{alt_init_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000.ne26np4.20251001.nc'
   if grid_short=='ne30': atm_init_file  = f'{    init_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000.nc'
   if atm_init_file is None: raise ValueError('no valid atm_init_file found')
   opts["atm_init_file"] = atm_init_file
   #----------------------------------------------------------------------------
   # print(case)
   # return
   #----------------------------------------------------------------------------
   # # simple hash method
   # suffix_orig = case.replace(opts['prefix'],'')
   # suffix_hash = hashlib.md5(suffix_orig.encode('utf-8')).hexdigest()
   # case_hash = f'{opts["prefix"]}.{suffix_hash}'
   # print( case_hash )
   # return
   #----------------------------------------------------------------------------
   print(f'\n  case : {case}\n')
   #----------------------------------------------------------------------------
   max_mpi_per_node,atm_nthrds  = 128,1 
   atm_ntasks = max_mpi_per_node*num_nodes
   case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
   #------------------------------------------------------------------------------------------------
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --mach pm-cpu --pecount {atm_ntasks}x{atm_nthrds} '
      cmd += f' --case {case} --handle-preexisting-dirs u '
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --compset {compset} --res {grid} '
      cmd += f' --project {acct} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config :
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------------------------
      # when specifying ncdata, do it here to avoid an error message
      write_atm_nl_opts(opts)
      #-------------------------------------------------------------------------
      # run_cmd('./xmlchange --id CAM_CONFIG_OPTS --append --val=\'-cosp\' ')
      #-------------------------------------------------------------------------
      run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build :
      if 'debug' in opts:
         if opts['debug']: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #-------------------------------------------------------
      write_atm_nl_opts(opts)
      write_lnd_nl_opts()
      #-------------------------------------------------------------------------
      if not continue_run: run_cmd(f'./xmlchange --file env_run.xml RUN_STARTDATE={RUN_START_DATE}')
      #-------------------------------------------------------------------------
      # Set some run-time stuff
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      #-------------------------------------------------------------------------
      if     disable_bfb: run_cmd('./xmlchange BFBFLAG=FALSE')
      if not disable_bfb: run_cmd('./xmlchange BFBFLAG=TRUE')
      #-------------------------------------------------------------------------
      if     continue_run: run_cmd('./xmlchange CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------------------------
      # Submit the run
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def get_atm_nl_opts(opts):
   return f'''
 ncdata = \'{opts["atm_init_file"]}\'
 use_gw_convect_old       = .false.
 effgw_beres              = { opts["EF"]}
 gw_convect_hcf           = { opts["CF"]}
 hdepth_scaling_factor    = { opts["HD"]}
 gw_convect_hdepth_min    = { opts["HM"]}
 gw_convect_plev_src_wind = {(opts["PS"]*1e2)}
 frontgfc                 = {(opts["FT"]/(opts["dx"]*3600e10))}
 effgw_cm                 = { opts["FE"]}
 taubgnd                  = { opts["OB"]}
 effgw_oro                = { opts["OE"]}

 cosp_lite = .false.
 inithist = 'NONE'

 tropopause_output_all = .true.

 empty_htapes = .true.
 fincl1 = 'AODALL', 'AODDUST', 'AODVIS'
         ,'FLDS', 'FLNS', 'FLNSC', 'FLNT', 'FLUT'
         ,'FLUTC', 'FSDS', 'FSDSC', 'FSNS', 'FSNSC', 'FSNT', 'FSNTOA', 'FSNTOAC'
         ,'ICEFRAC', 'LANDFRAC', 'OCNFRAC'
         ,'PSL', 'PS', 'OMEGA', 'U', 'V', 'Z3', 'T', 'Q', 'RELHUM', 'O3'
         ,'TROP_Z', 'TROP_P', 'TROP_T'
         ,'TROPF_Z', 'TROPF_P', 'TROPF_T'
         ,'TROPE3D_Z', 'TROPE3D_P', 'TROPE3D_T'
         ,'PRECC', 'PRECL', 'PRECSC', 'PRECSL'
         ,'QFLX', 'SCO', 'SHFLX', 'SOLIN', 'SWCF', 'LWCF'
         ,'TAUX', 'TAUY', 'TCO', 'TGCLDLWP', 'TGCLDIWP', 'TMQ'
         ,'TS', 'TREFHT', 'TREFMNAV', 'TREFMXAV'
         ,'HDEPTH', 'MAXQ0', 'UTGWSPEC', 'BUTGWSPEC', 'UTGWORO'
         ,'PSzm','Uzm','Vzm','Wzm','THzm','VTHzm','WTHzm','UVzm','UWzm'

 phys_grid_ctem_zm_nbas = 120 ! num basis functions for TEM
 phys_grid_ctem_za_nlat =  90 ! num latitude points for TEM
 phys_grid_ctem_nfreq   =  -6 ! frequency of TEM diags (neg => hours)

'''
def write_atm_nl_opts(opts):
   file=open('user_nl_eam','w')
   file.write(get_atm_nl_opts(opts))
   file.close()
   return
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def get_lnd_nl_opts():
   global lnd_luse_file, lnd_data_file, lnd_init_file
   return f'''
 flanduse_timeseries = \'{lnd_luse_file}\'
 fsurdat = \'{lnd_data_file}\'
 finidat = \'{lnd_init_file}\'
 ! -- Reduce the size of land outputs since we dont need them --
 hist_fincl1 = 'SNOWDP'
 hist_mfilt = 1
 hist_nhtfrq = 0
 hist_avgflag_pertape = 'A'

'''
# check_dynpft_consistency = .false.
# check_finidat_year_consistency = .false.
def write_lnd_nl_opts():
   file=open('user_nl_elm','w')
   file.write(get_lnd_nl_opts())
   file.close()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
