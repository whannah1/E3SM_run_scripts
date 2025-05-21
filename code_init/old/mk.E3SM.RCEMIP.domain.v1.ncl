; Create a "domian" file for the land and ocean components of E3SM
; since this is for an aqua planet, there is all ocean and no land
; v1 - use existing domain files
; v2 - use existing domain files only for var names - get grid info from latlon file
; load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
; load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
; load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
; load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/custom_functions.ncl"
begin 

    host = getenv("HOST")
    if isStrSubset(host,"edison") then host = "nersc" end if
    if isStrSubset(host,"cori")   then host = "nersc" end if
    if isStrSubset(host,"titan")  then host = "olcf"  end if

    setfileoption("nc", "Format",  "64BitOffset")

    res = "ne4"    ; ne4 / ne30
    
    if host.eq."olcf"  then idir  = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/share/domains/" end if
    if host.eq."nersc" then idir  = "/project/projectdirs/acme/inputdata/share/domains/" end if
    ; idir = "~/E3SM/init_files/"
    odir = "~/E3SM/init_files/"

    print("")
    print("  idir : "+idir)
    print("  odir : "+odir)
    print("")

;=============================================================================
; Make new LND domain file
;=============================================================================
    printline()

    if res.eq."ne30" then ifile = "domain.lnd.ne30np4_gx1v6.110905.nc" end if
    if res.eq."ne4"  then ifile = "domain.lnd.ne4np4_oQU240.160614.nc" end if

    ofile = "RCEMIP_"+ifile

    ifile = idir+ifile
    ofile = odir+ofile

    print("")
    print("  Land domain files:")
    print("")
    print("    ifile: "+ifile)
    print("")

    if isfilepresent(ofile) then system("rm "+ofile) end if
    infile  = addfile(ifile,"r")
    outfile = addfile(ofile,"c")
    
    vname = getfilevarnames(infile)
    do v = 0,dimsizes(vname)-1 outfile->$vname(v)$ = infile->$vname(v)$ end do

    outfile->frac = 0.
    outfile->mask = 0
    
    
    print("    ofile: "+ofile)
    print("")
;=============================================================================
; Make new OCN domain file (also used for sea ice)
;=============================================================================
    printline()

    if res.eq."ne30" then ifile = "domain.ocn.ne30np4_gx1v6_110217.nc" end if
    if res.eq."ne4"  then ifile = "domain.ocn.ne4np4_oQU240.160614.nc" end if

    ofile = "RCEMIP_"+ifile

    ifile = idir+ifile
    ofile = odir+ofile

    print("")
    print("  Ocean domain files:")
    print("")
    print("    ifile: "+ifile)
    print("")

    if isfilepresent(ofile) then system("rm "+ofile) end if
    infile  = addfile(ifile,"r")
    outfile = addfile(ofile,"c")
    
    vname = getfilevarnames(infile)
    do v = 0,dimsizes(vname)-1 outfile->$vname(v)$ = infile->$vname(v)$ end do

    outfile->frac = 1.
    outfile->mask = 1
    

    
    print("    ofile: "+ofile)
    print("")
;=============================================================================
;=============================================================================
printline()
end