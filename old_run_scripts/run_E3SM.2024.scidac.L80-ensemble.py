#!/usr/bin/env python3
import os
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END); os.system(cmd); return
#---------------------------------------------------------------------------------------------------
''' NOTES
The branch (whannah/scidac-2024) started with master @ Nov 20:
   commit 3871f59e0faa454e0ab1cdfe370ab9578d17ac39 (origin/master)
   Merge: 98ac5d3071 decd0238ee
   Author: Jon Wolfe <jonbob@lanl.gov>
   Date:   Tue Nov 19 10:41:29 2024 -0600
also merges in whannah/update-gw-convect-src (PR was not merged yet)

Initial condition was taken from:
/lcrc/group/e3sm2/ac.wlin/E3SMv3/AMIP/v3.LR.amip_0101/archive/rest/

parameter ranges for LHC sampling:
   gweff       0.05 -  0.90
   cfrac       5.00 - 50.00
   hdpth       0.25 -  1.50
   hdpth_min   1.00 -  5.00 # minimum hdepth threshold
   stspd_min   0.00 - 50.00 # minimum convective storm speed
   plev_srcw   500  - 950   # pressure level for steering flow level
'''
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run,reset_resub,st_archive = False,False,False,False,False,False,False,False

acct = 'm4310'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC2' # branch => whannah/scidac-2024

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True
### reset_resub  = True

disable_bfb = False

# queue = 'batch' # batch / debug
num_nodes       = 22
grid,grid_short = 'ne30pg2_r05_IcoswISC30E3r5','ne30pg2'
compset         = 'F20TR'

# stop_opt,stop_n,resub,walltime = 'ndays',365,  0,  '2:00:00' #  1 year
# stop_opt,stop_n,resub,walltime = 'ndays',365*2,2-1,'6:00:00' #  4 years
# stop_opt,stop_n,resub,walltime = 'ndays',365*2,3-1,'6:00:00' #  6 years
# stop_opt,stop_n,resub,walltime = 'ndays',365*2,4-1,'6:00:00' #  8 years
# stop_opt,stop_n,resub,walltime = 'ndays',365*2,5-1,'6:00:00' # 10 years

stop_opt,stop_n,resub,walltime = 'ndays',365*5,0,'12:00:00' #  5 years

# queue = 'regular' 
# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00' #  1-day test



#-------------------------------------------------------------------------------
nlev_list      = []
gweff_list     = []
cfrac_list     = []
hdpth_list     = []
hdpth_min_list = []
stspd_min_list = []
plev_srcw_list = []
def add_case( nlev=80, gweff=0.35, cfrac=10, hdpth=0.50, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ):
   nlev_list.append(nlev)
   gweff_list.append(gweff)
   cfrac_list.append(cfrac)
   hdpth_list.append(hdpth)
   hdpth_min_list.append(hdpth_min)
   stspd_min_list.append(stspd_min)
   plev_srcw_list.append(plev_srcw)
#-------------------------------------------------------------------------------

# add_case( gweff=0.35, cfrac=10, hdpth=0.50, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ) # v3 defaults

### Ensemble values from => https://acme-climate.atlassian.net/wiki/spaces/QIE/pages/4791500859/2024-11-21+Initial+sample

# L80_iter0
# add_case( gweff=0.18, cfrac=10.95, hdpth=0.48, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.13, cfrac=18.87, hdpth=0.55, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.09, cfrac=20.33, hdpth=0.99, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.07, cfrac=28.99, hdpth=1.18, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ) # BAD
# add_case( gweff=0.14, cfrac=36.95, hdpth=1.47, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ) # BAD
# add_case( gweff=0.28, cfrac= 5.86, hdpth=0.71, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.32, cfrac=15.00, hdpth=0.83, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.34, cfrac=25.64, hdpth=1.04, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.21, cfrac=28.28, hdpth=1.30, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ) # BAD
# add_case( gweff=0.25, cfrac=33.11, hdpth=0.44, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.50, cfrac= 8.76, hdpth=0.92, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.36, cfrac=14.13, hdpth=1.13, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.44, cfrac=21.60, hdpth=1.26, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.44, cfrac=32.59, hdpth=0.31, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.40, cfrac=37.86, hdpth=0.66, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ) # BAD
# add_case( gweff=0.57, cfrac= 7.70, hdpth=1.24, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.62, cfrac=16.32, hdpth=1.38, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.55, cfrac=22.14, hdpth=0.38, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.52, cfrac=26.04, hdpth=0.57, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.60, cfrac=39.84, hdpth=0.76, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ) # BAD
# add_case( gweff=0.69, cfrac=10.53, hdpth=1.44, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.71, cfrac=12.36, hdpth=0.27, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.78, cfrac=24.44, hdpth=0.62, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.68, cfrac=31.00, hdpth=0.85, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.76, cfrac=35.69, hdpth=1.08, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )

# L80_iter1
# add_case( gweff=0.21, cfrac=19.51, hdpth=0.36, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.10, cfrac=18.23, hdpth=1.27, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.76, cfrac= 9.11, hdpth=0.60, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.59, cfrac=15.62, hdpth=0.67, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.66, cfrac=13.34, hdpth=1.10, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.26, cfrac= 7.22, hdpth=1.06, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.76, cfrac=17.73, hdpth=1.32, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.44, cfrac=11.74, hdpth=0.42, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.52, cfrac= 5.58, hdpth=0.76, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )

# add_case( gweff=0.14, cfrac= 9.89, hdpth=0.30, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.65, cfrac=16.85, hdpth=0.90, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.59, cfrac=11.58, hdpth=1.33, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.39, cfrac= 7.47, hdpth=0.64, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.72, cfrac=13.47, hdpth=1.18, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.17, cfrac= 8.48, hdpth=0.44, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.46, cfrac=14.65, hdpth=0.50, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.76, cfrac=20.10, hdpth=1.41, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.34, cfrac=18.69, hdpth=1.01, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.26, cfrac=15.72, hdpth=0.61, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.42, cfrac= 9.54, hdpth=0.86, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.48, cfrac=12.81, hdpth=1.22, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.55, cfrac=17.13, hdpth=0.33, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.37, cfrac= 5.96, hdpth=0.96, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.79, cfrac= 6.51, hdpth=0.77, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.22, cfrac=20.76, hdpth=1.47, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )

# L80_iter2
# add_case( gweff=0.50, cfrac=7.00 , hdpth=1.00, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.49, cfrac=7.50 , hdpth=1.00, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.48, cfrac=8.00 , hdpth=1.00, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.47, cfrac=8.50 , hdpth=1.00, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.48, cfrac=7.79 , hdpth=1.00, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.33, cfrac=8.21 , hdpth=0.69, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.33, cfrac=8.76 , hdpth=0.70, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.32, cfrac=8.82 , hdpth=0.69, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.35, cfrac=8.21 , hdpth=0.72, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( gweff=0.33, cfrac=8.58 , hdpth=0.69, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )


# 2025-01-10 - first ensemble to perturb new parameters
# L80_iter3
# add_case( gweff=0.40, cfrac=11.56, hdpth=0.76, hdpth_min=1.23, stspd_min=44.05, plev_srcw=779.94 )
# add_case( gweff=0.28, cfrac= 9.32, hdpth=0.59, hdpth_min=2.29, stspd_min= 6.86, plev_srcw=830.73 )
# add_case( gweff=0.15, cfrac= 6.97, hdpth=0.40, hdpth_min=1.04, stspd_min=36.36, plev_srcw=617.36 )
# add_case( gweff=0.74, cfrac=18.00, hdpth=1.27, hdpth_min=3.34, stspd_min=25.07, plev_srcw=558.72 )
# add_case( gweff=0.86, cfrac=20.28, hdpth=1.44, hdpth_min=4.20, stspd_min=13.74, plev_srcw=747.48 )
# add_case( gweff=0.43, cfrac=12.17, hdpth=0.81, hdpth_min=3.49, stspd_min=49.69, plev_srcw=936.26 )
# add_case( gweff=0.57, cfrac=14.72, hdpth=1.01, hdpth_min=4.00, stspd_min=10.90, plev_srcw=640.98 )
# add_case( gweff=0.12, cfrac= 6.22, hdpth=0.35, hdpth_min=4.49, stspd_min= 0.35, plev_srcw=821.24 )
# add_case( gweff=0.07, cfrac= 5.36, hdpth=0.28, hdpth_min=4.92, stspd_min=14.45, plev_srcw=670.28 )
# add_case( gweff=0.51, cfrac=13.69, hdpth=0.93, hdpth_min=4.56, stspd_min=16.67, plev_srcw=529.54 )
# add_case( gweff=0.85, cfrac=20.02, hdpth=1.42, hdpth_min=2.03, stspd_min=39.50, plev_srcw=760.21 )
# add_case( gweff=0.71, cfrac=17.39, hdpth=1.22, hdpth_min=3.77, stspd_min=32.90, plev_srcw=524.59 )
# add_case( gweff=0.77, cfrac=18.50, hdpth=1.30, hdpth_min=1.47, stspd_min=34.69, plev_srcw=915.59 )
# add_case( gweff=0.31, cfrac= 9.96, hdpth=0.64, hdpth_min=2.57, stspd_min= 5.24, plev_srcw=865.17 )
# add_case( gweff=0.37, cfrac=11.10, hdpth=0.73, hdpth_min=3.06, stspd_min=45.74, plev_srcw=699.25 )
# add_case( gweff=0.62, cfrac=15.75, hdpth=1.09, hdpth_min=1.70, stspd_min=20.60, plev_srcw=700.09 )
# add_case( gweff=0.61, cfrac=15.49, hdpth=1.07, hdpth_min=2.37, stspd_min=23.39, plev_srcw=599.29 )
# add_case( gweff=0.22, cfrac= 8.22, hdpth=0.50, hdpth_min=2.94, stspd_min=29.75, plev_srcw=880.35 )

# 2025-04-03 - 2nd 6 parameter ensemble - after QBOi meeting
# L80_iter3
add_case( gweff=0.02, cfrac=17.80, hdpth=1.30, hdpth_min=4.88, stspd_min=4.52, plev_srcw=851.56 )
add_case( gweff=0.05, cfrac=18.79, hdpth=0.90, hdpth_min=1.00, stspd_min=0.10, plev_srcw=500.00 )
add_case( gweff=0.06, cfrac=22.32, hdpth=0.61, hdpth_min=2.25, stspd_min=1.83, plev_srcw=584.38 )
add_case( gweff=0.09, cfrac=16.24, hdpth=0.72, hdpth_min=3.62, stspd_min=0.37, plev_srcw=935.94 )
add_case( gweff=0.11, cfrac=17.30, hdpth=0.60, hdpth_min=1.50, stspd_min=0.18, plev_srcw=668.75 )
add_case( gweff=0.13, cfrac=11.95, hdpth=0.99, hdpth_min=4.38, stspd_min=3.02, plev_srcw=795.31 )
add_case( gweff=0.15, cfrac=13.00, hdpth=1.40, hdpth_min=2.75, stspd_min=1.22, plev_srcw=640.62 )
add_case( gweff=0.18, cfrac=18.40, hdpth=0.32, hdpth_min=3.12, stspd_min=0.65, plev_srcw=767.19 )
add_case( gweff=0.20, cfrac=15.70, hdpth=1.05, hdpth_min=4.00, stspd_min=0.32, plev_srcw=612.50 )
add_case( gweff=0.23, cfrac=10.77, hdpth=0.48, hdpth_min=1.88, stspd_min=2.02, plev_srcw=739.06 )
add_case( gweff=0.25, cfrac= 9.69, hdpth=0.75, hdpth_min=3.25, stspd_min=4.09, plev_srcw=696.88 )
add_case( gweff=0.28, cfrac=11.83, hdpth=1.05, hdpth_min=2.62, stspd_min=0.12, plev_srcw=823.44 )
add_case( gweff=0.31, cfrac= 9.76, hdpth=1.03, hdpth_min=4.50, stspd_min=0.56, plev_srcw=556.25 )
add_case( gweff=0.34, cfrac=12.04, hdpth=0.43, hdpth_min=1.38, stspd_min=1.35, plev_srcw=907.81 )
add_case( gweff=0.37, cfrac= 9.84, hdpth=0.51, hdpth_min=3.75, stspd_min=2.73, plev_srcw=528.12 )
add_case( gweff=0.40, cfrac= 7.45, hdpth=1.25, hdpth_min=2.12, stspd_min=0.21, plev_srcw=879.69 )
add_case( gweff=0.43, cfrac= 9.17, hdpth=0.89, hdpth_min=3.00, stspd_min=1.00, plev_srcw=725.00 )
add_case( gweff=0.46, cfrac= 5.95, hdpth=0.47, hdpth_min=2.88, stspd_min=0.87, plev_srcw=626.56 )
add_case( gweff=0.49, cfrac= 8.57, hdpth=0.33, hdpth_min=4.25, stspd_min=0.24, plev_srcw=809.38 )
add_case( gweff=0.52, cfrac=11.62, hdpth=1.44, hdpth_min=1.62, stspd_min=2.47, plev_srcw=710.94 )
add_case( gweff=0.55, cfrac= 6.64, hdpth=1.25, hdpth_min=3.50, stspd_min=1.50, plev_srcw=893.75 )
add_case( gweff=0.58, cfrac= 8.83, hdpth=0.23, hdpth_min=2.38, stspd_min=0.49, plev_srcw=570.31 )
add_case( gweff=0.61, cfrac= 9.44, hdpth=0.57, hdpth_min=4.75, stspd_min=0.13, plev_srcw=865.62 )
add_case( gweff=0.64, cfrac= 7.27, hdpth=0.85, hdpth_min=1.12, stspd_min=3.70, plev_srcw=542.19 )
add_case( gweff=0.66, cfrac= 6.73, hdpth=0.56, hdpth_min=2.00, stspd_min=2.24, plev_srcw=837.50 )
add_case( gweff=0.69, cfrac= 8.74, hdpth=0.84, hdpth_min=3.88, stspd_min=0.27, plev_srcw=514.06 )
add_case( gweff=0.72, cfrac= 8.13, hdpth=1.11, hdpth_min=1.25, stspd_min=0.75, plev_srcw=921.88 )
add_case( gweff=0.75, cfrac= 6.23, hdpth=0.56, hdpth_min=4.62, stspd_min=1.11, plev_srcw=598.44 )
add_case( gweff=0.78, cfrac= 8.92, hdpth=0.32, hdpth_min=2.50, stspd_min=3.34, plev_srcw=781.25 )
add_case( gweff=0.81, cfrac= 6.77, hdpth=1.02, hdpth_min=3.38, stspd_min=0.15, plev_srcw=682.81 )
add_case( gweff=0.84, cfrac= 4.98, hdpth=0.95, hdpth_min=1.75, stspd_min=0.42, plev_srcw=753.12 )
add_case( gweff=0.89, cfrac= 7.28, hdpth=0.66, hdpth_min=4.12, stspd_min=1.65, plev_srcw=654.69 )

#-------------------------------------------------------------------------------
# new L72 ensemble

# add_case( nlev=72, gweff=0.35, cfrac=10, hdpth=0.50, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ) # v3 defaults

### Ensemble values from => https://acme-climate.atlassian.net/wiki/spaces/QIE/pages/4791500859/2024-11-21+Initial+sample
# L72_iter0
# add_case( nlev=72, gweff=0.18, cfrac=10.95, hdpth=0.48, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.13, cfrac=18.87, hdpth=0.55, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.09, cfrac=20.33, hdpth=0.99, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.07, cfrac=28.99, hdpth=1.18, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ) # BAD for L80 & L72
# add_case( nlev=72, gweff=0.14, cfrac=36.95, hdpth=1.47, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ) # BAD for L80 & L72
# add_case( nlev=72, gweff=0.28, cfrac= 5.86, hdpth=0.71, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.32, cfrac=15.00, hdpth=0.83, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.34, cfrac=25.64, hdpth=1.04, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.21, cfrac=28.28, hdpth=1.30, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ) # BAD for L80 & L72
# add_case( nlev=72, gweff=0.25, cfrac=33.11, hdpth=0.44, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.50, cfrac= 8.76, hdpth=0.92, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.36, cfrac=14.13, hdpth=1.13, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.44, cfrac=21.60, hdpth=1.26, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.44, cfrac=32.59, hdpth=0.31, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.40, cfrac=37.86, hdpth=0.66, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ) # BAD for L80
# add_case( nlev=72, gweff=0.57, cfrac= 7.70, hdpth=1.24, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.62, cfrac=16.32, hdpth=1.38, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.55, cfrac=22.14, hdpth=0.38, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.52, cfrac=26.04, hdpth=0.57, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.60, cfrac=39.84, hdpth=0.76, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 ) # BAD for L80 & L72
# add_case( nlev=72, gweff=0.69, cfrac=10.53, hdpth=1.44, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.71, cfrac=12.36, hdpth=0.27, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.78, cfrac=24.44, hdpth=0.62, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.68, cfrac=31.00, hdpth=0.85, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.76, cfrac=35.69, hdpth=1.08, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )

# add_case( nlev=72, gweff=0.21, cfrac=19.51, hdpth=0.36, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.10, cfrac=18.23, hdpth=1.27, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.76, cfrac= 9.11, hdpth=0.60, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.59, cfrac=15.62, hdpth=0.67, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.66, cfrac=13.34, hdpth=1.10, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.26, cfrac= 7.22, hdpth=1.06, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.76, cfrac=17.73, hdpth=1.32, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.44, cfrac=11.74, hdpth=0.42, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )
# add_case( nlev=72, gweff=0.52, cfrac= 5.58, hdpth=0.76, hdpth_min=2.5, stspd_min=10.0, plev_srcw=700 )

# Bad L72 cases
# E3SM_2024-SCIDAC-00-L72_F20TR_ne30pg2_EF_0.07_CF_28.99_HD_1.18_HM_02.5_SS_10.0_PS_700
# E3SM_2024-SCIDAC-00-L72_F20TR_ne30pg2_EF_0.14_CF_36.95_HD_1.47_HM_02.5_SS_10.0_PS_700
# E3SM_2024-SCIDAC-00-L72_F20TR_ne30pg2_EF_0.21_CF_28.28_HD_1.30_HM_02.5_SS_10.0_PS_700
# E3SM_2024-SCIDAC-00-L72_F20TR_ne30pg2_EF_0.60_CF_39.84_HD_0.76_HM_02.5_SS_10.0_PS_700


#-------------------------------------------------------------------------------
din_loc_root = '/global/cfs/cdirs/e3sm/inputdata'
init_root = '/global/cfs/cdirs/m4310/whannah/E3SM/init_data/v3.LR.amip_0101/archive/rest/2000-01-01-00000'

# atm_init_file = f'{init_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000.nc'
lnd_init_file = f'{init_root}/v3.LR.amip_0101.elm.r.2000-01-01-00000.nc'

lnd_data_root = f'{din_loc_root}/lnd/clm2/surfdata_map'
lnd_data_file = f'{lnd_data_root}/surfdata_0.5x0.5_simyr1850_c200609_with_TOP.nc'
lnd_luse_file = f'{lnd_data_root}/landuse.timeseries_0.5x0.5_hist_simyr1850-2015_c240308.nc'

RUN_START_DATE = '1995-01-01'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(nlev=None, gweff=None, cfrac=None, hdpth=None, hdpth_min=None, stspd_min=None, plev_srcw=None):
   if nlev not in [72,80]: raise ValueError(f'nlev={nlev} is not supported')

   ens_id = '2024-SCIDAC-00'

   if nlev==72: ens_id = ens_id+'-L72'

   case_list = ['E3SM',ens_id,compset,grid_short]

   case_list.append(f'EF_{gweff:0.2f}')
   # case_list.append(f'CF_{cfrac:02.0f}') # initial runs truncated the precision of the CF values
   # case_list.append(f'CF_{cfrac:02.2f}')
   case_list.append(f'CF_{cfrac:05.2f}')
   case_list.append(f'HD_{hdpth:0.2f}')
   case_list.append(f'HM_{hdpth_min:04.1f}')
   case_list.append(f'SS_{stspd_min:04.1f}')
   case_list.append(f'PS_{plev_srcw:3.0f}')

   case = '_'.join(case_list)

   # print(case); return

   case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'

   init_root_L72 = '/global/cfs/cdirs/m4310/whannah/E3SM/init_data/'
   if nlev==72: atm_init_file = f'{init_root_L72}/v3.LR.amip_0101.eam.i.2000-01-01-00000.remap_L72_20250110.nc'
   if nlev==80: atm_init_file = f'{init_root    }/v3.LR.amip_0101.eam.i.2000-01-01-00000.nc'
   #------------------------------------------------------------------------------------------------
   # print(case); return
   #------------------------------------------------------------------------------------------------
   print('\n  case : '+case+'\n')
   atm_ntasks,atm_nthrds = num_nodes*128,1
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      # Check if directory already exists   
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case} --handle-preexisting-dirs u'
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --compset {compset} --res {grid} '
      cmd += f' --machine pm-cpu --pecount {atm_ntasks}x{atm_nthrds} '
      cmd += f' --project {acct}  --walltime {walltime} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config :
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------
      # when specifying ncdata, do it here to avoid an error message
      write_atm_nl_opts(atm_init_file, gweff, cfrac, hdpth, hdpth_min, stspd_min, plev_srcw)
      #-------------------------------------------------------
      if nlev==72: run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val=\' -nlev 72 \'')
      # run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val=\'-cosp\'')
      #-------------------------------------------------------
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if 'debug-on' in case : run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #-------------------------------------------------------
      sst_file = '/global/cfs/cdirs/e3sm/benedict/e3sm_v3_inputs/AMIP/sstice-ext/sst_ice_CMIP6_DECK_E3SM_1x1_c20221024.nc'
      run_cmd(f'./xmlchange SSTICE_DATA_FILENAME={sst_file}')
      run_cmd(f'./xmlchange SSTICE_YEAR_END=2022')
      #-------------------------------------------------------
      write_atm_nl_opts(atm_init_file, gweff, cfrac, hdpth, hdpth_min, stspd_min, plev_srcw)
      write_lnd_nl_opts()
      #-------------------------------------------------------
      run_cmd(f'./xmlchange RUN_STARTDATE={RUN_START_DATE}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      # if 'resub' in globals() and not continue_run: run_cmd(f'./xmlchange RESUBMIT={resub}')
      # if 'resub' in globals() and reset_resub: run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'resub' in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      #-------------------------------------------------------
      if     disable_bfb: run_cmd('./xmlchange BFBFLAG=FALSE')
      if not disable_bfb: run_cmd('./xmlchange BFBFLAG=TRUE')
      #-------------------------------------------------------
      if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def get_atm_nl_opts(atm_init_file, gweff, cfrac, hdpth, hdpth_min, stspd_min, plev_srcw):
   global ncdata
   return f'''
 ncdata = \'{atm_init_file}\'

 use_gw_convect_old           = .false.
 effgw_beres                  = {gweff}
 gw_convect_hcf               = {cfrac}
 hdepth_scaling_factor        = {hdpth}
 gw_convect_hdepth_min        = {hdpth_min}
 gw_convect_storm_speed_min   = {stspd_min}
 gw_convect_plev_src_wind     = {plev_srcw*1e2}

 cosp_lite = .false.
 inithist = 'NONE'

 empty_htapes = .true.
 fincl1 = 'AODALL', 'AODDUST', 'AODVIS'
         ,'FLDS', 'FLNS', 'FLNSC', 'FLNT', 'FLUT'
         ,'FLUTC', 'FSDS', 'FSDSC', 'FSNS', 'FSNSC', 'FSNT', 'FSNTOA', 'FSNTOAC'
         ,'ICEFRAC', 'LANDFRAC', 'OCNFRAC'
         ,'PSL', 'PS', 'OMEGA', 'U', 'V', 'Z3', 'T', 'Q', 'RELHUM', 'O3'
         ,'PRECC', 'PRECL', 'PRECSC', 'PRECSL'
         ,'QFLX', 'SCO', 'SHFLX', 'SOLIN', 'SWCF', 'LWCF'
         ,'TAUX', 'TAUY', 'TCO', 'TGCLDLWP', 'TGCLDIWP', 'TMQ'
         ,'TS', 'TREFHT', 'TREFMNAV', 'TREFMXAV'
         ,'HDEPTH', 'MAXQ0', 'UTGWSPEC', 'BUTGWSPEC', 'UTGWORO'

'''
#         ,'PSzm','Uzm','Vzm','Wzm','THzm','VTHzm','WTHzm','UVzm','UWzm','THphys'
# phys_grid_ctem_zm_nbas = 120 ! num basis functions for TEM
# phys_grid_ctem_za_nlat =  90 ! num latitude points for TEM
# phys_grid_ctem_nfreq   =  -6 ! frequency of TEM diags (neg => hours)
def write_atm_nl_opts(atm_init_file, gweff, cfrac, hdpth, hdpth_min, stspd_min, plev_srcw):
   file=open('user_nl_eam','w')
   file.write(get_atm_nl_opts(atm_init_file, gweff, cfrac, hdpth, hdpth_min, stspd_min, plev_srcw))
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

   for n in range(len(hdpth_list)):
      print('-'*80)
      main( nlev=nlev_list[n],
            gweff=gweff_list[n],
            cfrac=cfrac_list[n],
            hdpth=hdpth_list[n],
            hdpth_min=hdpth_min_list[n],
            stspd_min=stspd_min_list[n],
            plev_srcw=plev_srcw_list[n],
          )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
