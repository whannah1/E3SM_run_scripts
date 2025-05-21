; Create a "domian" file for the land and ocean components of CESM
; since this is for an aqua planet, there is all ocean and no land
; load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
; load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
; load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
; load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/custom_functions.ncl"
begin 
    
    idir = "/lustre/atlas1/cli900/world-shared/cesm/inputdata" + "/share/domains/" + ""
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

    ; ifile = idir+"domain.lnd.fv1.9x2.5_gx1v6.090206.nc"
    ifile = idir+"domain.lnd.ne30np4_gx1v6.110905.nc"
    ofile = odir+"aqua_domain.lnd.ne30np4_gx1v6.v1.nc"

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
;=============================================================================
    printline()

    ; ifile = idir+"domain.ocn.1.9x2.5_gx1v6_090403.nc"
    ifile = idir+"domain.ocn.ne30np4_gx1v6_110217.nc"
    ofile = odir+"aqua_domain.ocn.ne30np4_gx1v6.v1.nc"

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