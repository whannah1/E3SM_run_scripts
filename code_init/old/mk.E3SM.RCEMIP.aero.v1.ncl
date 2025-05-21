; Create a topography file for aqua planet experiments
; v1 - use existing file
; v2 - use existing file only for var names - get grid info from latlon/scrip file
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/custom_functions.ncl"
begin 

    debug = False

    host = getenv("HOST")
    if isStrSubset(host,"edison") then host = "nersc" end if
    if isStrSubset(host,"cori")   then host = "nersc" end if
    if isStrSubset(host,"titan")  then host = "olcf"  end if

    setfileoption("nc", "Format",  "64BitOffset")

    res = "ne4"    ; ne4 / ne30
    
    if host.eq."olcf"  then idir  = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/chem/trop_mam/aero/" end if
    if host.eq."nersc" then idir  = "/project/projectdirs/acme/inputdata/atm/cam/chem/trop_mam/aero/" end if

    ifile = idir+"mam4_0.9x1.2_L72_2000clim_c170323.nc"

    ; odir = "~/E3SM/init_files/"   ; Not enough space here! output file is ~12GB
    if host.eq."nersc" then odir = "/global/cscratch1/sd/whannah/acme_scratch/init_files/" end if
    ; ofile = odir+"RCEMIP_aero."+res+".v1.nc"
    ofile = odir+"RCEMIP_aero.v1.nc"

    ;;; input file from SCM RCE equilibrium run
    d1 =  70
    d2 = 100
    To = 300.       ; 295 / 300 / 305
    sdir  = "~/E3SM/init_files/"
    sfile = "E3SM_SCM_RCE_"+To+"_SP1_T42_64x1_4km_00.cam.h1.0000-01-01-00000.nc"

;=============================================================================
; Load CESM default SST input data
;=============================================================================
    scmfile = addfile(sdir+sfile,"r")
    infile = addfile(ifile,"r")

    printline()

;=============================================================================
; Create outfile and populate with input data
;=============================================================================
    if isfilepresent(ofile) then system("rm "+ofile) end if
    outfile = addfile(ofile,"c")

    var = getfilevarnames(infile)

    do v = 0,dimsizes(var)-1

        if isatt(infile->$var(v)$,"long_name") then 
            var_name = infile->$var(v)$@long_name 
        else
            var_name = ""
        end if

        print("  "+strpad(var(v),20) + "    " + var_name)

        V_in = infile->$var(v)$

        ;--------------------------------------------------
        ; zero out all aerosol fields
        ;--------------------------------------------------
        if any((/ isStrSubset(var(v),"bc_") \
                 ,isStrSubset(var(v),"dst_") \
                 ,isStrSubset(var(v),"ncl_") \
                 ,isStrSubset(var(v),"num_") \
                 ,isStrSubset(var(v),"pom_") \
                 ,isStrSubset(var(v),"so4_") \
                 ,isStrSubset(var(v),"soa_") \
                 ,isStrSubset(var(v),"wat_") \
                /)) then
            V_out = V_in
            V_out = (/0.0/)
        end if

        ;--------------------------------------------------
        ; make surface pressure consistent with SCM
        ;--------------------------------------------------
        if var(v).eq."PS" then
            S = avg( scmfile->PS({d1:d2},0,0) )
            V_out = V_in
            V_out = (/ totype(S,typeof(V_out)) /)
            delete(S)
        end if
        ;--------------------------------------------------
        ;--------------------------------------------------
        if .not.isvar("V_out") then
            V_out = V_in
        end if
        ;--------------------------------------------------
        ; Write to the file
        ;--------------------------------------------------
        if .not.debug then
            outfile->$var(v)$ = V_out
        end if
        ;--------------------------------------------------
        ; Clean up
        ;--------------------------------------------------

        delete([/V_in,V_out/])
        ;--------------------------------------------------
        ;--------------------------------------------------

    end do

    print("")
    print("    "+ofile)
    print("")
    printline()
;=============================================================================
;=============================================================================
end