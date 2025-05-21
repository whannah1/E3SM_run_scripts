; Create a topography file for aqua planet experiments
; v1 - use existing file
; v2 - use existing file only for var names - get grid info from latlon/scrip file
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/custom_functions.ncl"
begin 

    host = getenv("HOST")
    if isStrSubset(host,"edison") then host = "nersc" end if
    if isStrSubset(host,"cori")   then host = "nersc" end if
    if isStrSubset(host,"titan")  then host = "olcf"  end if

    setfileoption("nc", "Format",  "64BitOffset")

    res = "ne30"    ; ne4 / ne30
    
    if host.eq."olcf"  then idir  = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/topo/" end if
    if host.eq."nersc" then idir  = "/project/projectdirs/acme/inputdata/atm/cam/topo/" end if

    ;ifile = idir+"cami-mam3_0000-01-01_1.9x2.5_L30_c090306.nc"    ; fv 1.9 x 2.5
    ; ifile = idir+"USGS-gtopo30_1.9x2.5_remap_c050602.nc"
    if res.eq."ne30" then ifile = idir+"USGS-gtopo30_ne30np4_16xdel2-PFC-consistentSGH.nc" end if
    if res.eq."ne4"  then ifile = idir+"USGS-gtopo30_ne4np4_16x.c20160612.nc" end if

    odir = "~/E3SM/init_files/"
    ofile = odir+"RCEMIP_topo."+res+".v1.nc"

;=============================================================================
; Load CESM default SST input data
;=============================================================================
    infile = addfile(ifile,"r")

    printline()

;=============================================================================
; Create outfile and populate with input data
;=============================================================================
    if isfilepresent(ofile) then system("rm "+ofile) end if
    outfile = addfile(ofile,"c")

    vname = getfilevarnames(infile)

    do v = 0,dimsizes(vname)-1
        ; outfile->$vname(v)$ = infile->$vname(v)$
        tmp := infile->$vname(v)$

        if vname(v).eq."PHIS"         then tmp = 0. end if
        if vname(v).eq."SGH"          then tmp = 0. end if
        if vname(v).eq."SGH30"        then tmp = 0. end if
        if vname(v).eq."LANDFRAC"     then tmp = 0. end if
        if vname(v).eq."LANDM_COSLAT" then tmp = 0. end if

        outfile->$vname(v)$ = tmp

        delete(tmp)

    end do

    ; outfile->PHIS         = (/0./)
    ; outfile->SGH          = (/0./)
    ; outfile->SGH30        = (/0./)
    ; outfile->LANDFRAC     = (/0./)
    ; outfile->LANDM_COSLAT = (/0./)

    print("")
    print("    "+ofile)
    print("")
    printline()
;=============================================================================
;=============================================================================
end