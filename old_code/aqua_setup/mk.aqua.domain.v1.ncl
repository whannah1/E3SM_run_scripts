; Create a input "domian" file for the land and ocean components of CESM
; since this is for an aqua planet, there is all ocean and no land
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
; load "$NCARG_ROOT/custom_functions.ncl"
begin 
    
    ; idir = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/share/domains/"
    idir = "~/ACME/aqua_setup/data/"
    odir = "~/ACME/aqua_setup/data/"

    res = "ne16"

;=============================================================================
; Make new LND domain file
;=============================================================================
    ; printline()
    ; ifile = idir+"domain.lnd.fv1.9x2.5_gx1v6.090206.nc"
    if res.eq."ne16" then ifile = idir+"domain.lnd.ne16np4_gx3v7.120406.nc" end if
    if res.eq."ne30" then ifile = idir+"domain.lnd.ne30np4_gx1v6.110905.nc" end if

    ofile = odir+"aqua_domain.lnd."+res+".v1.nc"

    if isfilepresent(ofile) then system("rm "+ofile) end if
    infile  = addfile(ifile,"r")
    outfile = addfile(ofile,"c")
    
    vname = getfilevarnames(infile)
    do v = 0,dimsizes(vname)-1 outfile->$vname(v)$ = infile->$vname(v)$ end do

    outfile->frac = 0.
    outfile->mask = 0
    

    print("")
    print("    "+ofile)
    print("")
;=============================================================================
;=============================================================================
    ; printline()
    ; ifile = idir+"domain.ocn.1.9x2.5_gx1v6_090403.nc"
    if res.eq."ne16" then ifile = idir+"domain.ocn.ne16np4_gx3v7.121113.nc" end if
    if res.eq."ne30" then ifile = idir+"domain.ocn.ne30np4_gx1v6_110217.nc" end if

    ofile = odir+"aqua_domain.ocn."+res+".v1.nc"

    if isfilepresent(ofile) then system("rm "+ofile) end if
    infile  = addfile(ifile,"r")
    outfile = addfile(ofile,"c")
    
    vname = getfilevarnames(infile)
    do v = 0,dimsizes(vname)-1 outfile->$vname(v)$ = infile->$vname(v)$ end do

    outfile->frac = 1.
    outfile->mask = 1
    

    print("")
    print("    "+ofile)
    print("")
;=============================================================================
;=============================================================================
; printline()
end
