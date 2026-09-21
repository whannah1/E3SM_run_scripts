#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np, hashlib
from shutil import copy2
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
# opt_list = []
# def add_case( **kwargs ):
#    case_opts = {}
#    for k, val in kwargs.items(): case_opts[k] = val
#    opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
ens_opt_list,exe_opt_list = [],[]
def add_case( exe=False, **kwargs):
   global cnt
   case_opts = {}
   for key,val in kwargs.items(): case_opts[key] = val
   if     exe: exe_opt_list.append(case_opts)
   if not exe: ens_opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
''' Notes
# to generate add_case() calls - this script will parse the CSV file from Luis Damiano
python ./parse_params.2026-2027.scidac.ensemble.py
# run this script
nohup python -u ~/E3SM/run_E3SM.2025.scidac.MF-ensemble.pilot.py > ~/E3SM/run_E3SM.2025.scidac.MF-ensemble.pilot.out &
'''
#---------------------------------------------------------------------------------------------------
clean_exe,create_exe,config_exe,build_exe,print_case_list = False,False,False,False,False
newcase,config,set_params,set_timestep,set_output,set_runopt,submit,continue_run = False,False,False,False,False,False,False,False

acct = 'm4310'
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # branch => whannah/scidac-2026-ens (master @ Sept 18)

# create_exe   = True
# config_exe   = True
# build_exe    = True

# newcase        = True # create the case via create_newcase
# config         = True # configure the case via case.setup
set_runopt     = True # update run-time parameters - including run length
submit         = True # only runs case.submit
# continue_run   = True

queue = 'regular' # regular / debug

stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,  0,  '2:00:00' #  1 year
# stop_opt,stop_n,resub,walltime = 'ndays',365*5,1,'10:00:00' # 10 years

#---------------------------------------------------------------------------------------------------
compset        = 'F20TR'
din_loc_root   = '/global/cfs/cdirs/e3sm/inputdata'
init_root      = '/global/cfs/cdirs/m4310/whannah/E3SM/init_data/v3.LR.amip_0101/archive/rest/2000-01-01-00000'
atm_init_file  = f'{init_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000.nc' # ne30
lnd_init_file  = f'{init_root}/v3.LR.amip_0101.elm.r.2000-01-01-00000.nc'
lnd_data_root  = f'{din_loc_root}/lnd/clm2/surfdata_map'
lnd_data_file  = f'{lnd_data_root}/surfdata_0.5x0.5_simyr1850_c200609_with_TOP.nc'
lnd_luse_file  = f'{lnd_data_root}/landuse.timeseries_0.5x0.5_hist_simyr1850-2015_c240308.nc'
RUN_START_DATE = '1995-01-01'
ens_case_root  = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/2026-SCIDAC'
grid = 'ne30pg2_r05_IcoswISC30E3r5'; num_nodes=32; ne=30
mach, max_mpi_per_node, atm_nthrds = 'pm-cpu',128,1
atm_ntasks = max_mpi_per_node*num_nodes
#---------------------------------------------------------------------------------------------------

kwargs = {'prefix':'E3SM.2026-SCIDAC-ENS','g':'ne30','num_nodes':4}

# add_case(exe=True,**kwargs)

add_case(**kwargs,member='000',EF= 0.350000000000000, CF=10.000000000000000, HD= 0.500000000000000, HM= 2.500000000000000, PS=700.000000000000000, FT= 7.492500000000000, FE= 1.000000000000000, OB= 0.002500000000000, OE= 0.375000000000000)
# add_case(**kwargs,member='001',EF= 0.153906250000000, CF=11.950146006778899, HD= 0.340908125934825, HM= 1.386686482771510, PS=645.068240509100974, FT= 8.785402655214879, FE= 0.055468750000000, OB= 0.000118281457302, OE= 0.219531250000000)
# add_case(**kwargs,member='002',EF= 0.427343750000000, CF=13.148540397448400, HD= 0.554350625713866, HM= 1.695702001073850, PS=713.524114441170013, FT= 8.998670249596650, FE= 0.471093750000000, OB= 0.000665145514444, OE= 0.296093750000000)
# add_case(**kwargs,member='003',EF= 0.832031250000000, CF=17.122984978774401, HD= 0.655532031326977, HM= 3.315790130121800, PS=863.150577718101999, FT=22.387813015973201, FE= 0.624218750000000, OB= 0.001821447536396, OE= 0.088281250000000)
# add_case(**kwargs,member='004',EF= 0.952343750000000, CF=21.298199014235902, HD= 1.239565682465750, HM= 4.715054564454500, PS=946.157454364757996, FT=37.947077797617098, FE= 0.930468750000000, OB= 0.009763000989628, OE= 0.066406250000000)
# add_case(**kwargs,member='005',EF= 0.241406250000000, CF=14.933664082088701, HD= 0.712850740772644, HM= 4.263841945628070, PS=645.068240509100974, FT=14.891153405782500, FE= 0.667968750000000, OB= 0.005759922853514, OE= 0.383593750000000)
# add_case(**kwargs,member='006',EF= 0.383593750000000, CF= 6.126381646888590, HD= 0.996821407334335, HM= 2.757380636621300, PS=713.524114441170013, FT= 6.748050711864770, FE= 1.017968750000000, OB= 0.002315172383515, OE= 0.372656250000000)
# add_case(**kwargs,member='007',EF= 0.613281250000000, CF=21.992985387391101, HD= 0.260700793196363, HM= 1.971868596466020, PS=835.059385651895013, FT=37.047735809163001, FE= 0.285156250000000, OB= 0.000976300098963, OE= 0.405468750000000)
# add_case(**kwargs,member='008',EF= 0.941406250000000, CF=16.527084777721701, HD= 0.438380690551416, HM= 1.275186171342970, PS=936.782664243703039, FT=26.480631493234000, FE= 0.350781250000000, OB= 0.000280489537712, OE= 0.438281250000000)
# add_case(**kwargs,member='009',EF= 0.164843750000000, CF=19.193538680590699, HD= 0.352532554817429, HM= 2.411288756633150, PS=817.813700810827982, FT=49.403949714643403, FE= 0.317968750000000, OB= 0.006339913511725, OE= 0.689843750000000)
# add_case(**kwargs,member='010',EF= 0.449218750000000, CF=21.415562147264200, HD= 0.476712021786966, HM= 4.409232224395120, PS=645.068240509100974, FT=21.339210015813300, FE= 0.208593750000000, OB= 0.002103374801087, OE= 0.755468750000000)
# add_case(**kwargs,member='011',EF= 0.591406250000000, CF=10.378576190884800, HD= 0.788286756853443, HM= 1.060433115174030, PS=913.798104127087981, FT= 9.670041494698699, FE= 0.864843750000000, OB= 0.000886985799018, OE= 0.821093750000000)
# add_case(**kwargs,member='012',EF= 1.028906250000000, CF=12.956507776017400, HD= 0.932166746132649, HM= 1.843971567870210, PS=889.200149296606014, FT= 6.911861136789500, FE= 0.613281250000000, OB= 0.000294272717621, OE= 0.646093750000000)
# add_case(**kwargs,member='013',EF= 0.077343750000000, CF=21.180185561431401, HD= 0.801613768576933, HM= 1.724370046364960, PS=796.870914683721026, FT=19.857672216242900, FE= 1.083593750000000, OB= 0.000182144753640, OE= 0.919531250000000)
# add_case(**kwargs,member='014',EF= 0.405468750000000, CF=18.393308622521801, HD= 1.030811443583660, HM= 1.115131526179530, PS=505.974194994172024, FT=42.782057885955901, FE= 0.755468750000000, OB= 0.000768098057277, OE= 0.908593750000000)
# add_case(**kwargs,member='015',EF= 0.711718750000000, CF=14.069442730613000, HD= 0.288288937674577, HM= 4.054695872963900, PS=936.782664243703039, FT= 7.079648096043890, FE= 0.547656250000000, OB= 0.001074607828321, OE= 0.974218750000000)
# add_case(**kwargs,member='016',EF= 0.853906250000000, CF= 5.244664947989210, HD= 0.396429341585526, HM= 2.578534647206220, PS=876.346437569029945, FT=13.857291016616299, FE= 0.230468750000000, OB= 0.008869857990182, OE= 0.996093750000000)
# add_case(**kwargs,member='017',EF= 0.219531250000000, CF= 8.222571196610790, HD= 0.460992891967552, HM= 2.144285744285750, PS=936.782664243703039, FT=28.456293901521299, FE= 0.733593750000000, OB= 0.002428939327345, OE= 0.186718750000000)
# add_case(**kwargs,member='018',EF= 0.569531250000000, CF=16.065661167533701, HD= 0.335240450591584, HM= 1.363632503739300, PS=849.633756071107996, FT=17.196035684244698, FE= 0.941406250000000, OB= 0.008058421877615, OE= 0.121093750000000)
# add_case(**kwargs,member='019',EF= 0.766406250000000, CF=18.797682425855900, HD= 1.120944005845250, HM= 3.371847869964030, PS=796.870914683721026, FT=13.528874590878900, FE= 0.219531250000000, OB= 0.000143301257024, OE= 0.164843750000000)
# add_case(**kwargs,member='020',EF= 0.842968750000000, CF=19.961714657897801, HD= 0.592800132780247, HM= 2.331778781500730, PS=608.357871803216995, FT= 5.985425152478650, FE= 0.394531250000000, OB= 0.000930572040930, OE= 0.153906250000000)
# add_case(**kwargs,member='021',EF= 0.263281250000000, CF=16.220927519206001, HD= 0.980249024096266, HM= 2.711538554672520, PS=913.798104127087981, FT=20.339721605415200, FE= 0.088281250000000, OB= 0.000323904265044, OE= 0.350781250000000)
# add_case(**kwargs,member='022',EF= 0.317968750000000, CF=10.617337923572601, HD= 0.689345159155325, HM= 4.958262729862990, PS=835.059385651895013, FT=45.973934315944000, FE= 0.482031250000000, OB= 0.000308733199257, OE= 0.449218750000000)
# add_case(**kwargs,member='023',EF= 0.580468750000000, CF=22.444230652515898, HD= 0.545134420132807, HM= 1.296744850221400, PS=772.250557689071002, FT= 8.175450079252499, FE= 0.799218750000000, OB= 0.005232991146815, OE= 0.317968750000000)
# add_case(**kwargs,member='024',EF= 1.061718750000000, CF=18.529080466031399, HD= 0.269590278660634, HM= 1.639787825068800, PS=680.281772274135960, FT=14.538234543735800, FE= 0.886718750000000, OB= 0.002548296747979, OE= 0.339843750000000)
# add_case(**kwargs,member='025',EF= 0.252343750000000, CF=18.256527086223201, HD= 0.403131494624268, HM= 3.855808642036510, PS=835.059385651895013, FT= 7.607845265768870, FE= 0.853906250000000, OB= 0.000523299114681, OE= 0.580468750000000)
# add_case(**kwargs,member='026',EF= 0.536718750000000, CF=20.942163659708100, HD= 0.364553358372758, HM= 2.948631302453860, PS=925.501899963800042, FT=11.999919638807601, FE= 0.646093750000000, OB= 0.000267351935993, OE= 0.722656250000000)
# add_case(**kwargs,member='027',EF= 0.700781250000000, CF=10.134190787461399, HD= 1.159166426744130, HM= 1.875146302811690, PS=505.974194994172024, FT=24.642135293766000, FE= 0.536718750000000, OB= 0.004987887696449, OE= 0.602343750000000)
# add_case(**kwargs,member='028',EF= 0.974218750000000, CF=15.100574285437000, HD= 0.677884638668129, HM= 1.212636906371860, PS=744.329315891844999, FT=32.860815548505300, FE= 0.164843750000000, OB= 0.001736134364005, OE= 0.591406250000000)
# add_case(**kwargs,member='029',EF= 0.088281250000000, CF=20.334923520469200, HD= 1.198692171851670, HM= 1.192476541242100, PS=849.633756071107996, FT=10.643758308981900, FE= 0.514843750000000, OB= 0.002942727176209, OE= 1.017968750000000)
# add_case(**kwargs,member='030',EF= 0.547656250000000, CF=16.374721689746899, HD= 0.737157825613465, HM= 2.005205596832710, PS=925.501899963800042, FT= 8.373910939820510, FE= 0.077343750000000, OB= 0.004117023380296, OE= 0.897656250000000)
# add_case(**kwargs,member='031',EF= 0.788281250000000, CF=12.563640080937301, HD= 0.536071436071437, HM= 2.851402963090580, PS=570.296198082088040, FT=34.475587123757101, FE= 0.963281250000000, OB= 0.000124093776075, OE= 1.039843750000000)
# add_case(**kwargs,member='032',EF= 0.930468750000000, CF=11.523018177399001, HD= 0.283496068336814, HM= 3.428853338725430, PS=817.813700810827982, FT=22.931282133185601, FE= 0.580468750000000, OB= 0.000339820832894, OE= 0.930468750000000)
# add_case(**kwargs,member='033',EF= 0.799218750000000, CF=19.708982987883100, HD= 0.409946956267200, HM= 1.078361114642540, PS=946.157454364757996, FT=29.147076735680400, FE= 0.263281250000000, OB= 0.008454410545947, OE= 0.471093750000000)
# add_case(**kwargs,member='034',EF= 0.875781250000000, CF=11.079436188272400, HD= 0.775181309739296, HM= 2.899609634567820, PS=772.250557689071002, FT=11.166789709277600, FE= 1.061718750000000, OB= 0.000220673406908, OE= 0.482031250000000)
# add_case(**kwargs,member='035',EF= 0.066406250000000, CF=15.590587104082999, HD= 0.278782881544882, HM= 1.559354453478350, PS=889.200149296606014, FT= 5.569869299974010, FE= 0.405468750000000, OB= 0.000475426443011, OE= 0.328906250000000)
# add_case(**kwargs,member='036',EF= 0.394531250000000, CF=18.118712990073700, HD= 1.218957620291890, HM= 3.791704943983550, PS=608.357871803216995, FT=23.487944083532501, FE= 0.722656250000000, OB= 0.001503430419787, OE= 0.547656250000000)
# add_case(**kwargs,member='037',EF= 0.678906250000000, CF= 9.883764570412090, HD= 0.324186212555349, HM= 4.123245774334650, PS=936.782664243703039, FT=15.622900650669900, FE= 0.503906250000000, OB= 0.003087331992570, OE= 0.099218750000000)
# add_case(**kwargs,member='038',EF= 0.996093750000000, CF=22.332274150878600, HD= 0.886442956060720, HM= 2.180537680531230, PS=744.329315891844999, FT=33.658519120724897, FE= 0.744531250000000, OB= 0.000805842187761, OE= 0.055468750000000)
# add_case(**kwargs,member='039',EF= 0.142968750000000, CF=17.556641964889899, HD= 0.445792085645316, HM= 2.493509896390510, PS=863.150577718101999, FT=20.833472850226599, FE= 0.110156250000000, OB= 0.000242893932735, OE= 0.230468750000000)
# add_case(**kwargs,member='040',EF= 0.416406250000000, CF=15.750537358558100, HD= 0.623377474097627, HM= 1.133984273347260, PS=570.296198082088040, FT= 7.427540085863870, FE= 0.897656250000000, OB= 0.004754264430111, OE= 0.175781250000000)
# add_case(**kwargs,member='041',EF= 0.821093750000000, CF=13.524428130239000, HD= 0.423925500268462, HM= 1.813315120007030, PS=796.870914683721026, FT=25.240328583337401, FE= 0.875781250000000, OB= 0.002804895377122, OE= 1.050781250000000)
# add_case(**kwargs,member='042',EF= 0.908593750000000, CF=18.663864652048900, HD= 0.749620436330442, HM= 4.483776023380980, PS=901.690851838553954, FT= 7.792527393832310, FE= 0.153906250000000, OB= 0.000549013891434, OE= 1.094531250000000)
# add_case(**kwargs,member='043',EF= 0.197656250000000, CF=20.086888084436200, HD= 0.318796542835742, HM= 1.253985910417700, PS=531.277381873821014, FT= 9.904783892751690, FE= 0.602343750000000, OB= 0.000102427522138, OE= 0.875781250000000)
# add_case(**kwargs,member='044',EF= 0.438281250000000, CF= 8.811170112419800, HD= 0.947926235995887, HM= 2.371200531120990, PS=863.150577718101999, FT=43.820601812297603, FE= 0.449218750000000, OB= 0.004531583637601, OE= 0.963281250000000)
# add_case(**kwargs,member='045',EF= 0.624218750000000, CF=19.062500000000000, HD= 0.298119135310524, HM= 2.535665920620170, PS=713.524114441170013, FT= 6.588122577799620, FE= 0.821093750000000, OB= 0.007321217907829, OE= 0.700781250000000)
# add_case(**kwargs,member='046',EF= 1.094531250000000, CF=15.265659651103601, HD= 0.857213334681357, HM= 1.433970302590240, PS=946.157454364757996, FT=19.387047349888899, FE= 0.383593750000000, OB= 0.000191095297497, OE= 0.744531250000000)
# add_case(**kwargs,member='047',EF= 0.274218750000000, CF=10.850847221146701, HD= 0.509776550625052, HM= 4.794768687406660, PS=608.357871803216995, FT=35.312489633446603, FE= 1.094531250000000, OB= 0.000697830584860, OE= 0.777343750000000)
# add_case(**kwargs,member='048',EF= 0.503906250000000, CF=22.219753552113598, HD= 0.815166090747330, HM= 2.039106202500210, PS=849.633756071107996, FT=15.252639451335099, FE= 0.066406250000000, OB= 0.001910952974970, OE= 0.613281250000000)
# add_case(**kwargs,member='049',EF= 0.667968750000000, CF=21.061510857090301, HD= 0.700999434630235, HM= 2.803997738520940, PS=531.277381873821014, FT=16.788491340296101, FE= 0.372656250000000, OB= 0.000633991351172, OE= 0.525781250000000)
# add_case(**kwargs,member='050',EF= 0.897656250000000, CF= 9.626826125468350, HD= 0.468786575702923, HM= 1.096592210233130, PS=876.346437569029945, FT= 5.060324153109150, FE= 0.810156250000000, OB= 0.002206734069085, OE= 0.569531250000000)
# add_case(**kwargs,member='051',EF= 0.296093750000000, CF=13.708507471031799, HD= 0.901429425850955, HM= 4.192954600844350, PS=796.870914683721026, FT=14.193679823793801, FE= 0.132031250000000, OB= 0.005490138914342, OE= 0.536718750000000)
# add_case(**kwargs,member='052',EF= 0.328906250000000, CF=18.930554281812999, HD= 0.346671620692877, HM= 1.906848087147860, PS=925.501899963800042, FT=44.884356622365701, FE= 1.007031250000000, OB= 0.000107460782832, OE= 0.427343750000000)
# add_case(**kwargs,member='053',EF= 0.744531250000000, CF= 6.522696751855530, HD= 0.842961967491007, HM= 1.783168342581260, PS=570.296198082088040, FT= 7.251508120879120, FE= 0.197656250000000, OB= 0.000136589296015, OE= 0.241406250000000)
# add_case(**kwargs,member='054',EF= 1.017968750000000, CF=22.106660242635801, HD= 0.329667001643529, HM= 4.335927733068310, PS=849.633756071107996, FT=24.058119125958701, FE= 0.908593750000000, OB= 0.003924189758485, OE= 0.110156250000000)
# add_case(**kwargs,member='055',EF= 0.110156250000000, CF=17.839891220240101, HD= 0.633916480155041, HM= 1.172651346780510, PS=744.329315891844999, FT=31.321676832844300, FE= 0.438281250000000, OB= 0.001182814573015, OE= 0.197656250000000)
# add_case(**kwargs,member='056',EF= 0.482031250000000, CF=13.890147512415700, HD= 0.527159126187046, HM= 3.153147027413770, PS=901.690851838553954, FT=12.589592439516100, FE= 0.766406250000000, OB= 0.000453158363760, OE= 0.274218750000000)
# add_case(**kwargs,member='057',EF= 0.755468750000000, CF=12.362525278032800, HD= 0.644633661801555, HM= 4.875830481167540, PS=835.059385651895013, FT=30.579356191586900, FE= 0.678906250000000, OB= 0.000210337480109, OE= 0.941406250000000)
# add_case(**kwargs,member='058',EF= 0.963281250000000, CF=19.452968121857399, HD= 0.383357457513359, HM= 1.507936209405490, PS=505.974194994172024, FT=10.391502290395200, FE= 0.525781250000000, OB= 0.003740388100368, OE= 0.842968750000000)
# add_case(**kwargs,member='059',EF= 0.208593750000000, CF=21.648379702647500, HD= 1.102308056098780, HM= 2.666458607791160, PS=913.798104127087981, FT= 7.981692721439710, FE= 0.974218750000000, OB= 0.001024275221382, OE= 1.028906250000000)
# add_case(**kwargs,member='060',EF= 0.361718750000000, CF= 8.521953879050660, HD= 0.303159226592964, HM= 1.042803172785450, PS=817.813700810827982, FT=17.613473257365499, FE= 0.142968750000000, OB= 0.000498788769645, OE= 1.072656250000000)
# add_case(**kwargs,member='061',EF= 0.722656250000000, CF=17.979842590616101, HD= 1.013673968240970, HM= 1.233138108665370, PS=889.200149296606014, FT=10.145224714485099, FE= 0.919531250000000, OB= 0.000356519536578, OE= 0.788281250000000)
# add_case(**kwargs,member='062',EF= 0.864843750000000, CF=14.246481656301400, HD= 0.313496477604425, HM= 2.254890572893840, PS=531.277381873821014, FT=48.233080995560002, FE= 0.252343750000000, OB= 0.001365892960146, OE= 0.733593750000000)
# add_case(**kwargs,member='063',EF= 0.186718750000000, CF= 7.250628564706190, HD= 0.666614651947790, HM= 1.612525978497070, PS=946.157454364757996, FT=21.857224063055501, FE= 0.832031250000000, OB= 0.006042963902381, OE= 0.832031250000000)
# add_case(**kwargs,member='064',EF= 0.372656250000000, CF=21.878719921802301, HD= 0.492967149116505, HM= 4.636665706976500, PS=744.329315891844999, FT= 6.279547323237110, FE= 0.427343750000000, OB= 0.000254829674798, OE= 0.766406250000000)
# add_case(**kwargs,member='065',EF= 0.525781250000000, CF=20.822132405607899, HD= 0.871705639748654, HM= 2.998481745321770, PS=680.281772274135960, FT=27.781882552170000, FE= 0.591406250000000, OB= 0.001577308583391, OE= 0.886718750000000)
# add_case(**kwargs,member='066',EF= 1.050781250000000, CF=14.421347385617800, HD= 0.256366583052469, HM= 1.753522762205660, PS=863.150577718101999, FT= 8.577189481714401, FE= 0.492968750000000, OB= 0.006651455144439, OE= 0.853906250000000)
# add_case(**kwargs,member='067',EF= 0.285156250000000, CF=19.323688776128300, HD= 0.431092511591240, HM= 1.153155750698310, PS=901.690851838553954, FT=13.208241601930499, FE= 0.985156250000000, OB= 0.000231517238352, OE= 1.083593750000000)
# add_case(**kwargs,member='068',EF= 0.777343750000000, CF= 9.362839335194570, HD= 0.762293743672329, HM= 3.920996096385060, PS=772.250557689071002, FT=40.778226863237400, FE= 0.241406250000000, OB= 0.000431933279405, OE= 0.864843750000000)
# add_case(**kwargs,member='069',EF= 0.558593750000000, CF=14.764867154273100, HD= 0.376984052351372, HM= 3.486822558994610, PS=531.277381873821014, FT= 6.130722673118020, FE= 0.842968750000000, OB= 0.000411702338030, OE= 0.667968750000000)
# add_case(**kwargs,member='070',EF= 0.985156250000000, CF=21.763854543332499, HD= 0.828947532530450, HM= 1.410130219269720, PS=863.150577718101999, FT=27.123454685056601, FE= 0.186718750000000, OB= 0.000157730858339, OE= 0.678906250000000)
# add_case(**kwargs,member='071',EF= 0.055468750000000, CF= 7.911868063232600, HD= 1.083981933267080, HM= 2.217402502855460, PS=901.690851838553954, FT=41.768127347891301, FE= 0.657031250000000, OB= 0.003565195365776, OE= 0.624218750000000)
# add_case(**kwargs,member='072',EF= 0.657031250000000, CF=17.268747360960099, HD= 0.370716606503761, HM= 2.452054725678020, PS=772.250557689071002, FT=11.437866001592001, FE= 0.558593750000000, OB= 0.001301917106190, OE= 0.711718750000000)
# add_case(**kwargs,member='073',EF= 0.514843750000000, CF=16.678056004323000, HD= 1.065960486407020, HM= 1.458213433491030, PS=876.346437569029945, FT=29.854628476065301, FE= 0.569531250000000, OB= 0.000374038810037, OE= 0.252343750000000)
# add_case(**kwargs,member='074',EF= 1.007031250000000, CF=11.303403340734700, HD= 0.252104430140704, HM= 3.545771824242880, PS=570.296198082088040, FT=10.902137898264600, FE= 0.689843750000000, OB= 0.000173613436400, OE= 0.132031250000000)
# add_case(**kwargs,member='075',EF= 0.230468750000000, CF=20.211286296275201, HD= 0.518394985487079, HM= 3.100725238957180, PS=713.524114441170013, FT= 5.183164642188490, FE= 0.099218750000000, OB= 0.003239042650439, OE= 0.208593750000000)
# add_case(**kwargs,member='076',EF= 0.810156250000000, CF=12.761585830791800, HD= 0.563722643223461, HM= 1.585717366342100, PS=925.501899963800042, FT=18.041044219986802, FE= 1.028906250000000, OB= 0.001127413765933, OE= 0.307031250000000)
# add_case(**kwargs,member='077',EF= 0.339843750000000, CF= 5.702589872154580, HD= 0.416877642143478, HM= 1.533429830053430, PS=849.633756071107996, FT=12.895207583089400, FE= 0.296093750000000, OB= 0.002673519359934, OE= 0.492968750000000)
# add_case(**kwargs,member='078',EF= 1.039843750000000, CF=19.581393964254300, HD= 0.573253106864667, HM= 3.049174974689320, PS=505.974194994172024, FT=39.811786922106499, FE= 1.039843750000000, OB= 0.003398208328943, OE= 0.361718750000000)
# add_case(**kwargs,member='079',EF= 0.307031250000000, CF=13.337808493776899, HD= 1.048238650211090, HM= 3.605717703403820, PS=796.870914683721026, FT=18.927576246293100, FE= 0.460156250000000, OB= 0.000165481709994, OE= 0.558593750000000)
# add_case(**kwargs,member='080',EF= 0.635156250000000, CF=20.457813554157401, HD= 0.308284527166344, HM= 1.025466332209880, PS=913.798104127087981, FT= 6.431984724684870, FE= 0.635156250000000, OB= 0.000845441054595, OE= 0.416406250000000)
# add_case(**kwargs,member='081',EF= 0.492968750000000, CF=20.701405195863700, HD= 0.293162836695128, HM= 1.667510568573910, PS=817.813700810827982, FT=32.082017472004303, FE= 0.996093750000000, OB= 0.000150343041979, OE= 1.061718750000000)
# add_case(**kwargs,member='082',EF= 1.083593750000000, CF=14.594118036044501, HD= 0.916669261382592, HM= 2.622128125307910, PS=936.782664243703039, FT=12.291220344600999, FE= 0.307031250000000, OB= 0.000575992285351, OE= 1.007031250000000)
# add_case(**kwargs,member='083',EF= 0.132031250000000, CF=17.413289644693801, HD= 0.724902408641956, HM= 4.559580082131910, PS=889.200149296606014, FT= 5.437863948774530, FE= 0.788281250000000, OB= 0.002004856686553, OE= 0.985156250000000)
# add_case(**kwargs,member='084',EF= 0.733593750000000, CF=11.738524981870601, HD= 0.484771457833365, HM= 1.008417720562820, PS=645.068240509100974, FT=16.390605756967300, FE= 0.361718750000000, OB= 0.007680980572768, OE= 0.952343750000000)
# add_case(**kwargs,member='085',EF= 0.471093750000000, CF=15.908879530522100, HD= 0.613013681419506, HM= 1.318668006574110, PS=744.329315891844999, FT= 9.440862468248801, FE= 0.711718750000000, OB= 0.009305720409297, OE= 0.799218750000000)
# add_case(**kwargs,member='086',EF= 0.886718750000000, CF=21.532285594350299, HD= 0.501301399208178, HM= 3.666677045530370, PS=913.798104127087981, FT=47.089961749246299, FE= 0.328906250000000, OB= 0.001654817099943, OE= 0.657031250000000)
# add_case(**kwargs,member='087',EF= 0.121093750000000, CF= 6.896273903348100, HD= 0.265108278793507, HM= 3.206455074307730, PS=876.346437569029945, FT=18.478994562382098, FE= 1.050781250000000, OB= 0.000604296390238, OE= 0.810156250000000)
# add_case(**kwargs,member='088',EF= 0.646093750000000, CF=16.827672831282001, HD= 0.963952160509128, HM= 2.108636504748180, PS=680.281772274135960, FT= 5.705079110297410, FE= 0.175781250000000, OB= 0.000130191710619, OE= 0.635156250000000)
# add_case(**kwargs,member='089',EF= 0.350781250000000, CF=17.698833236026200, HD= 0.274148052558283, HM= 3.987285629337340, PS=925.501899963800042, FT=25.853043147442001, FE= 0.121093750000000, OB= 0.004319332794052, OE= 0.285156250000000)
# add_case(**kwargs,member='090',EF= 0.919531250000000, CF= 9.091190218191089, HD= 1.139895020532980, HM= 1.482866426015040, PS=772.250557689071002, FT= 5.843571168699380, FE= 1.072656250000000, OB= 0.001240937760752, OE= 0.142968750000000)
# add_case(**kwargs,member='091',EF= 0.099218750000000, CF=20.579969782533698, HD= 0.602822189158288, HM= 1.939085831333460, PS=680.281772274135960, FT=11.715522730913600, FE= 0.416406250000000, OB= 0.000732121790783, OE= 0.077343750000000)
# add_case(**kwargs,member='092',EF= 0.689843750000000, CF=15.428978754819299, HD= 0.453328780001757, HM= 3.260664362989320, PS=876.346437569029945, FT=36.169708136833698, FE= 0.700781250000000, OB= 0.000200485668655, OE= 0.263281250000000)
# add_case(**kwargs,member='093',EF= 0.460156250000000, CF= 7.588454086088070, HD= 0.582944695375182, HM= 2.293012427458670, PS=946.157454364757996, FT= 5.308987111334860, FE= 0.339843750000000, OB= 0.000112741376593, OE= 0.394531250000000)
# add_case(**kwargs,member='094',EF= 1.072656250000000, CF=16.975971069426301, HD= 0.389838613369587, HM= 2.073579941948320, PS=817.813700810827982, FT=16.002150022587500, FE= 0.777343750000000, OB= 0.000392418975848, OE= 0.503906250000000)
# add_case(**kwargs,member='095',EF= 0.175781250000000, CF=12.158084158972899, HD= 0.358492575647561, HM= 1.340961802366340, PS=608.357871803216995, FT=38.868251511938801, FE= 0.274218750000000, OB= 0.001433012570237, OE= 0.460156250000000)
# add_case(**kwargs,member='096',EF= 0.602343750000000, CF=19.835751340697900, HD= 1.178763641113620, HM= 3.728666984530590, PS=889.200149296606014, FT= 9.217114962045549, FE= 0.952343750000000, OB= 0.006978305848599, OE= 0.514843750000000)


#---------------------------------------------------------------------------------------------------
# def get_grid_stuff(opts):
#    grid_short = opts['g']
#    grid,num_nodes,ne = None,None,None
#    if grid_short=='ne18': grid = 'ne18pg2_r05_IcoswISC30E3r5'; num_nodes=12; ne=18
#    if grid_short=='ne22': grid = 'ne22pg2_r05_IcoswISC30E3r5'; num_nodes=18; ne=22
#    if grid_short=='ne26': grid = 'ne26pg2_r05_IcoswISC30E3r5'; num_nodes=24; ne=26
#    if grid_short=='ne30': grid = 'ne30pg2_r05_IcoswISC30E3r5'; num_nodes=32; ne=30
#    if grid is None: raise ValueError(f'no valid grid details for opts[\'g\']: {opts['g']}')
#    return grid_short,grid,num_nodes,ne
#---------------------------------------------------------------------------------------------------
# def get_atm_init_file(opts):
#    grid_short,grid,num_nodes,ne = get_grid_stuff(opts)
#    alt_init_root = '/global/cfs/cdirs/m4310/whannah/files_init'
#    atm_init_file = None
#    if grid_short=='ne18': atm_init_file  = f'{alt_init_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000.ne18np4.20251001.nc'
#    if grid_short=='ne22': atm_init_file  = f'{alt_init_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000.ne22np4.20251001.nc'
#    if grid_short=='ne26': atm_init_file  = f'{alt_init_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000.ne26np4.20251001.nc'
#    if grid_short=='ne30': atm_init_file  = f'{    init_root}/v3.LR.amip_0101.eam.i.2000-01-01-00000.nc'
#    if atm_init_file is None: raise ValueError('no valid atm_init_file found')
#    return atm_init_file
#---------------------------------------------------------------------------------------------------
def get_case_root(case): return f'{ens_case_root}/{case}'
#---------------------------------------------------------------------------------------------------
def get_case_name(opts,exe=False):
   case_list = []
   for key,val in opts.items(): 
      if key in ['prefix']:               case_list.append(val)
      elif key in ['num_nodes']:          case_list.append(f'NN_{val}')
      elif key in ['g']:                  case_list.append(val)
      elif key=='member':
         if not exe: case_list.append(f'{key}_{val}')
      # elif key in ['debug']:     case_list.append('debug')
      else:
         # if key not in ['member']:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         # else:
         #    fmt = 'g'
         #    if key in ['EF','CF','HD','HM','PS','FT','FE','OB','OE']: fmt = '0.3f'
         #    if key=='CF':fmt='05.2f'
         #    if key=='PS':fmt='05.1f'
         #    if key=='FT':fmt='07.4f'
         #    if key=='OB':fmt='0.6f'
         #    case_list.append(f'{key}_{val:{fmt}}')
   case = '.'.join(case_list)
   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
   if exe:
      case = f'{case}.EXE'
   else:
      param_str = '_'.join( [str(val) for val in opts.values()] ) # only use values
      suffix_hash = hashlib.md5(param_str.encode('utf-8')).hexdigest()
      case = f'{case}.{suffix_hash[:12]}' # truncate the hash to 12 characters
   return case
#---------------------------------------------------------------------------------------------------
def create_ens_exe(opts):
   case = get_case_name(opts,exe=True); case_root = get_case_root(case)
   #----------------------------------------------------------------------------
   print(f'\n  case : {case}\n')
   #----------------------------------------------------------------------------
   if create_exe:
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --mach {mach} --pecount {atm_ntasks}x{atm_nthrds} '
      cmd += f' --case {case} --handle-preexisting-dirs u '
      cmd += f' --output-root {case_root} --script-root {case_root}/case_scripts '
      cmd += f' --compset {compset} --res {grid} --project {acct} '
      run_cmd(cmd)
   #----------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #----------------------------------------------------------------------------
   if config_exe:
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld,RUNDIR={case_root}/run ')
      write_lnd_nl_opts(opts)
      run_cmd('./case.setup --reset')
   #----------------------------------------------------------------------------
   if build_exe:
      if clean_exe : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #----------------------------------------------------------------------------
   return
#---------------------------------------------------------------------------------------------------
def run_ens_member(opts):
   global compset, din_loc_root, init_root, atm_init_file
   global lnd_init_file, lnd_data_root, lnd_data_file, lnd_luse_file, RUN_START_DATE
   global grid_short, grid, num_nodes, ne
   #----------------------------------------------------------------------------
   case = get_case_name(opts)
   case_root = get_case_root(case)
   exe_root = get_case_root( get_case_name(opts,exe=True) )
   #----------------------------------------------------------------------------
   opts['dx'] = 360*111/(ne*4*2)
   opts['atm_init_file'] = atm_init_file
   #----------------------------------------------------------------------------
   print()
   print(f'  case : {case}'); print()
   print(f'  case_root: {case_root.replace(case,"")}')
   print(f'  exe_root : {exe_root}')
   print()
   #----------------------------------------------------------------------------
   # return
   #------------------------------------------------------------------------------------------------
   if newcase:
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --mach {mach} --pecount {atm_ntasks}x{atm_nthrds} '
      cmd += f' --case {case} --handle-preexisting-dirs u '
      cmd += f' --output-root {case_root} --script-root {case_root}/case_scripts '
      cmd += f' --compset {compset} --res {grid} --project {acct} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config:
      run_cmd(f'./xmlchange EXEROOT={exe_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------------------------
      # when specifying ncdata, do it here to avoid an error message
      write_atm_nl_opts(opts)
      #-------------------------------------------------------------------------
      # run_cmd('./xmlchange --id CAM_CONFIG_OPTS --append --val=\'-cosp\' ')
      #-------------------------------------------------------------------------
      run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
      run_cmd('./case.setup --reset')
      run_cmd(f'./xmlchange BUILD_COMPLETE=TRUE ')
   #------------------------------------------------------------------------------------------------
   if set_runopt:
      #-------------------------------------------------------
      write_atm_nl_opts(opts)
      write_lnd_nl_opts(opts)
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
      # if 'disable_bfb' in globals() and     disable_bfb: run_cmd('./xmlchange BFBFLAG=FALSE')
      # if 'disable_bfb' in globals() and not disable_bfb: run_cmd('./xmlchange BFBFLAG=TRUE')
      #-------------------------------------------------------------------------
      if     continue_run: run_cmd('./xmlchange CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange CONTINUE_RUN=FALSE ')
   #------------------------------------------------------------------------------------------------
   if submit:
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def get_atm_nl_opts(opts):
   if 'dx' not in opts: raise ValueError('dx value is missing from opts!')
   if 'EF' not in opts: raise ValueError('EF value is missing from opts!')
   if 'CF' not in opts: raise ValueError('CF value is missing from opts!')
   if 'HD' not in opts: raise ValueError('HD value is missing from opts!')
   if 'HM' not in opts: raise ValueError('HM value is missing from opts!')
   if 'PS' not in opts: raise ValueError('PS value is missing from opts!')
   if 'FT' not in opts: raise ValueError('FT value is missing from opts!')
   if 'FE' not in opts: raise ValueError('FE value is missing from opts!')
   if 'OB' not in opts: raise ValueError('OB value is missing from opts!')
   if 'OE' not in opts: raise ValueError('OE value is missing from opts!')
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

 use_tau_limiter          = .true.
 use_gw_front_rr_scaling  = .true.
 use_fgf_zgrad_correction = .true.

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
def write_lnd_nl_opts(opts):
   file=open('user_nl_elm','w')
   file.write(get_lnd_nl_opts())
   file.close()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
# if __name__ == '__main__':
#    for n in range(len(opt_list)):
#       main( opt_list[n] )
if __name__ == '__main__':

      if any([create_exe,config_exe,build_exe]):
         for n in range(len(exe_opt_list)):
            create_ens_exe(exe_opt_list[n])

      if print_case_list:
         print()
         for n in range(len(ens_opt_list)):
            print(get_case_name(ens_opt_list[n]))
         print()
         exit()

      if any([newcase,config,set_params,set_output,set_runopt,submit]):

         for n in range(len(ens_opt_list)):
            print('-'*80)
            print(f'case #: {n+1:3} of {len(ens_opt_list)}')
            run_ens_member( ens_opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
