#!/usr/bin/env python
#======================================================================================================================
#  Jan, 2018 - Walter Hannah - Lawrence Livermore National Lab
#  Common routines for running E3SM
#======================================================================================================================
# Machine-specific settings:
#   get_home_dir            Return user home directory of current machine
#   get_host_name           Return machine name
#   get_host_acct           Return account for running jobs on host
#   get_scratch_dir         Return scratch directory for current host
# 
# Functions for setting up a case:
#   get_num_dyn             Return number of dynamics elements for a given input grid_name
#   get_default_config      Return default options for CAM_CONFIG_OPTS
#   debug_queue_clear       Return True if debug queue is clear 
# 
# Case class methods
#   xmlchange               Set variable to value in xmlfile
#   set_NTASKS_all          Set NTASKS for all components
#   set_NTHRDS_all          Set NTHRDS for all components
#======================================================================================================================
#======================================================================================================================
import sys
import os
import fileinput
import subprocess

#--------------------------------------------------------------------------------------------------
# Machine-specific settings
#--------------------------------------------------------------------------------------------------

def get_home_dir():
    """ Return user home directory of current machine """
    home = os.getenv("HOME")
    return home

def get_host_name():
    """ Return machine name """
    # host = os.getenv("dnsdomainname")
    host = subprocess.check_output(["dnsdomainname"],universal_newlines=True).strip()
    if 'nersc' in host : host = None
    if host==None : host = os.getenv("host")
    if host==None : host = os.getenv("HOST")
    opsys = os.getenv("os")
    # if opsys=="Darwin" : host = "mac"
    if "cori"   in host : host = "cori-knl"
    if "titan"  in host : host = "titan"  
    if "summit" in host : host = "summit" 
    return host

def get_host_acct(host):
    """ Return account for running jobs on host """
    if "cori"   in host : acct = "m3312" # m2861
    if "titan"  in host : acct = "cli115"
    if "summit" in host : acct = "cli115"
    if 'acct' not in vars() : 
        print("ERROR: acct not found for host: "+host)
        exit()
    return acct

def get_scratch_dir(host,acct):
    """ Return scratch directory for current host """
    scratch_dir = os.getenv("CSCRATCH","")
    if "cori"   in host : scratch_dir = scratch_dir+"acme_scratch/"+host
    if "summit" in host : scratch_dir = "/gpfs/alpine/scratch/hannah6/cli115/"
    if scratch_dir=="" : 
        if host=="titan" :
            if acct == "cli115" : 
                scratch_dir = "/lustre/atlas1/"+acct+"/scratch/hannah6/"
            else : 
                scratch_dir = "/lustre/atlas/scratch/hannah6/"+acct+"/"
    return scratch_dir

#--------------------------------------------------------------------------------------------------
# Functions for setting up a case
#--------------------------------------------------------------------------------------------------

def get_num_dyn(grid_name):
    """ Return number of dynamics elements for a given input grid_name """
    if "ne4"   in grid_name : return 96
    if "ne16"  in grid_name : return 1536
    if "ne30"  in grid_name : return 5400
    if "ne120" in grid_name : return 86400 
    # if grid_name=="0.9x1.25" : return 1536
    # if grid_name=="1.9x2.5"  : return 1536


def get_default_config( cld, nlev_gcm=72, nlev_crm=58, \
                        crm_nx=64, crm_ny=1, \
                        crm_dx=1000, crm_dt=5,  \
                        crm_nx_rad=4, crm_ny_rad=1,\
                        crm_adv='MPDATA' ):
    """ Return default options for CAM_CONFIG_OPTS """
    

    if cld=='ZM' :
        cam_opt  = ' -phys cam5  -rad rrtmg -nlev '+str(nlev_gcm)+'  -clubb_sgs -microphys mg2 '
        chem_opt = ' -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates '
        crm_rad_opt = ''

    if 'SP' in cld :
        ### set options common to all SP setups
        cam_opt = ' -phys cam5 -use_SPCAM  -rad rrtmg  -nlev '+str(nlev_gcm) \
                 +'  -crm_nz '+str(nlev_crm)+' -crm_adv '+crm_adv    \
                 +' -crm_nx '+str(crm_nx)   +' -crm_ny '+str(crm_ny) \
                 +' -crm_dx '+str(crm_dx)   +' -crm_dt '+str(crm_dt)
        ### 1-moment microphysics
        if cld=='SP1' : cam_opt = cam_opt + ' -SPCAM_microp_scheme sam1mom ' 
        ### 2-moment microphysics
        if cld=='SP2' : cam_opt = cam_opt + ' -SPCAM_microp_scheme m2005  ' 

        ### Use mg2 since mg1 isn't supported anymore
        cam_opt = cam_opt + ' -microphys mg2 '

        ### chemistry and aerosols settings
        # chem_opt = ' -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates '
        if cld=='SP1'      : chem_opt = ' -chem none '
        if cld=='SP2'      : chem_opt = ' -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates '
        if cld=='SP2+ECPP' : chem_opt = ' -chem linoz_mam4_resus_mom_soag -rain_evap_to_coarse_aero -bc_dep_to_snow_updates -use_ECPP  '

        ### reduce rad columns
        crm_rad_opt = ' -crm_nx_rad '+str(crm_nx_rad)+' -crm_ny_rad '+str(crm_ny_rad)+' '
        ### use all columns for radiation with CAMRT
        if ' camrt ' in cam_opt : crm_rad_opt = crm_rad_opt.replace(crm_rad_opt,'')

    cam_opt = cam_opt + crm_rad_opt + chem_opt

    return cam_opt


def debug_queue_clear():
    """ Return True if debug queue is clear """
    ### get user name
    user = subprocess.check_output(["whoami"]).strip()
    ### get data on all jobs 
    out = subprocess.check_output(['qstat','-f'])
    lines = out.split('\n')
    ### build list of jobs for the user, each job is a dictionary
    jobs = []
    for line in lines:
        if "Job Id:" in line:  # new job
            job = {}
            s = line.split(":")
            job_id = s[1].split('.')[0].strip()
            job[s[0].strip()] = job_id
        if '=' in line:
            s = line.split("=")
            job[s[0].strip()] = s[1].strip()
        elif line == '':
            jobs.append(job)
    ### Check current jobs in case one is already in the debug queue
    debug_clear = True
    for job in jobs:
        if job['Job_Owner'].split('@')[0] == user:     
            if job['queue']=="debug" :
                if job['job_state'] != 'C' :
                    debug_clear = False
    # if debug_clear : 
    #     os.system(cdcmd+"./xmlchange -file env_batch.xml   -id JOB_QUEUE -val debug")
    #     wall_time = debug_wall_time

    return debug_clear 


#--------------------------------------------------------------------------------------------------
# Moving files around
#--------------------------------------------------------------------------------------------------
def file_copy(dir_from,dir_to,file_name):
    """ copy file from dir_from to dir_to  """
    CMD = "cp -u "+dir_from+"/"+file_name+" "+dir_to+"/"
    print(CMD)
    os.system(CMD)

#--------------------------------------------------------------------------------------------------
# Classes
#--------------------------------------------------------------------------------------------------

class Case(object):
    """ Class for creating an E3SM case """
    def __init__(self, case_name,
                 compset="FC5AV1C-L",
                 res="ne30",
                 mach="cori-knl",
                 project="m2861",
                 compiler="intel",
                 cld="SP1",
                 case_dir=None, 
                 src_dir=None, 
                 scratch_dir=None):
        self.case_name = case_name
        self.compset = compset
        self.res = res
        # if mach is None:
        #     _, mach = getenv()
        self.mach = mach
        self.project = project
        self.compiler = compiler
        self.cld = cld
        self.case_dir = case_dir
        self.verbose = True
        # self.Directory = AcmeDirectory(case_name=self.case_name,
        #                                top_dir=top_dir, src_dir=src_dir,
        #                                scratch_dir=scratch_dir)
        # self._cdcmd = "cd " + self.Directory.case_dir + " ; "
        self.cdcmd = "cd "+self.case_dir+" ; "
        # self._nproc = None
        # self.namelist = {}  # dictionary to hold namelist modifications

    def __repr__(self):
        return "Case(%s, compset=%s, res=%s, sp=%s)" % (self.case_name,
                                                        self.compset,
                                                        self.res,
                                                        self.sp)

    def xmlchange(self, xmlfile, variable, value):
        """ Set variable to value in xmlfile """
        cmd = self.cdcmd+"./xmlchange -file "+xmlfile+"  -id "+variable+" -val "+str(value)+" "
        if self.verbose : print(cmd.replace(self.cdcmd,""))
        os.system(cmd)

    def xmlquery(self, variable):
        """ Query value of variable in xmlfile """
        (output_value , err) = subprocess.Popen(self.cdcmd+"./xmlquery "+variable+" -value", \
                                                stdout=subprocess.PIPE,     \
                                                shell=True,                 \
                                                universal_newlines=True     \
                                                ).communicate()
        return output_value

    def set_NTASKS_all(self, ntask):
        """ Set NTASKS for all components """
        self.xmlchange("env_mach_pes.xml", "NTASKS_ATM",  ntask   )
        self.xmlchange("env_mach_pes.xml", "NTASKS_LND",  ntask   )
        self.xmlchange("env_mach_pes.xml", "NTASKS_ICE",  ntask   )
        self.xmlchange("env_mach_pes.xml", "NTASKS_OCN",  ntask   )
        self.xmlchange("env_mach_pes.xml", "NTASKS_CPL",  ntask   )
        self.xmlchange("env_mach_pes.xml", "NTASKS_GLC",  ntask   )
        self.xmlchange("env_mach_pes.xml", "NTASKS_WAV",  ntask   )
        self.xmlchange("env_mach_pes.xml", "NTASKS_ROF",  ntask   )

    def set_NTHRDS_all(self, nthrd):
        """ Set NTHRDS for all components """
        self.xmlchange("env_mach_pes.xml", "NTHRDS_ATM",  nthrd   )
        self.xmlchange("env_mach_pes.xml", "NTHRDS_OCN",  nthrd   )
        self.xmlchange("env_mach_pes.xml", "NTHRDS_LND",  nthrd   )
        self.xmlchange("env_mach_pes.xml", "NTHRDS_CPL",  nthrd   )
        self.xmlchange("env_mach_pes.xml", "NTHRDS_GLC",  nthrd   )
        self.xmlchange("env_mach_pes.xml", "NTHRDS_ICE",  nthrd   )
        self.xmlchange("env_mach_pes.xml", "NTHRDS_WAV",  nthrd   )
        self.xmlchange("env_mach_pes.xml", "NTHRDS_ROF",  nthrd   )

    def set_ROOTPE_all(self, rootpe):
        """ Set ROOTPE for all components """
        self.xmlchange("env_mach_pes.xml", "ROOTPE_ATM",  rootpe   )
        self.xmlchange("env_mach_pes.xml", "ROOTPE_LND",  rootpe   )
        self.xmlchange("env_mach_pes.xml", "ROOTPE_ICE",  rootpe   )
        self.xmlchange("env_mach_pes.xml", "ROOTPE_OCN",  rootpe   )
        self.xmlchange("env_mach_pes.xml", "ROOTPE_CPL",  rootpe   )
        self.xmlchange("env_mach_pes.xml", "ROOTPE_GLC",  rootpe   )
        self.xmlchange("env_mach_pes.xml", "ROOTPE_WAV",  rootpe   )
        self.xmlchange("env_mach_pes.xml", "ROOTPE_ROF",  rootpe   )

    def set_domain_file_name_path(self, init_dir, domain_ocn_file, domain_lnd_file):
        """ set domain file names and paths for idealized simuations (aqua, RCE, etc.) """
        self.xmlchange("env_run.xml", "ATM_DOMAIN_PATH", init_dir )
        self.xmlchange("env_run.xml", "OCN_DOMAIN_PATH", init_dir )
        self.xmlchange("env_run.xml", "ICE_DOMAIN_PATH", init_dir )
        self.xmlchange("env_run.xml", "LND_DOMAIN_PATH", init_dir )

        self.xmlchange("env_run.xml", "ATM_DOMAIN_FILE", domain_ocn_file )
        self.xmlchange("env_run.xml", "OCN_DOMAIN_FILE", domain_ocn_file )
        self.xmlchange("env_run.xml", "ICE_DOMAIN_FILE", domain_ocn_file )
        self.xmlchange("env_run.xml", "LND_DOMAIN_FILE", domain_lnd_file )
        # self.xmlchange("env_run.xml", "LND_DOMAIN_FILE", "UNSET" )
        self.xmlchange("env_run.xml", "ROF_DOMAIN_FILE", "UNSET" )
        self.xmlchange("env_run.xml", "WAV_DOMAIN_FILE", "UNSET" )
        self.xmlchange("env_run.xml", "GLC_DOMAIN_FILE", "UNSET" )

    def set_debug_mode(self, debug_flag) :
        """ specify debug mode in XML file """
        if debug_flag :
            self.xmlchange("env_build.xml", "DEBUG", "TRUE" )
        else :
            self.xmlchange("env_build.xml", "DEBUG", "FALSE" )

    def setup(self, clean) :
        """ Invoke case.setup """
        if clean:
            cmd = self.cdcmd+"./case.setup --clean"
            if self.verbose : print(cmd.replace(self.cdcmd,""))
            os.system(cmd)
        cmd = self.cdcmd+"./case.setup"
        if self.verbose : print(cmd.replace(self.cdcmd,""))
        os.system(cmd)

    def build(self, clean=False):
        """ Invoke case.build """
        # cmd = self.cdcmd+"./case.build --reset"
        # if self.verbose : print(cmd.replace(self.cdcmd,""))
        # os.system(cmd)
        if clean : 
            cmd = self.cdcmd+"./case.build --clean"
            if self.verbose : print(cmd.replace(self.cdcmd,""))
            os.system(cmd)
        cmd = self.cdcmd+"./case.build"
        if self.verbose : print(cmd.replace(self.cdcmd,""))
        os.system(cmd)


    def submit(self, clean=False):
        """ Submit the case """
        cmd = self.cdcmd+"./case.submit"
        if self.verbose : print(cmd.replace(self.cdcmd,""))
        os.system(cmd)

    # def _system_call(self, os_cmd, cwd=None, test=True, verbose=True):
    #     """Call os_cmd from command line
    #     """
    #     if test or verbose:
    #         print_os_command(os_cmd, cwd=cwd)
    #     if not test:
    #         if isinstance(os_cmd, str):
    #             cmd_to_execute = shlex.split(os_cmd)
    #         elif isinstance(os_cmd, list):
    #             cmd_to_execute = os_cmd
    #         else:
    #             raise ValueError("os_cmd must be str 'cmd args' or "
    #                              "list [cmd, args]")
    #         subprocess.call(cmd_to_execute, cwd=cwd)


#======================================================================================================================
#======================================================================================================================