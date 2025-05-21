; Walter Hannah - 2017 - Lawrence Livermore National Lab
; Create a modified initialization file (cami) for the ACME model
; Adds more vertical levels to the standard 30 level setup
; v1 - interpolate levels from previous file - can't change model top
; v2 - regrid SE file for higher model top
; Titan directory :
; /lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/inic/fv/
load "$NCARG_ROOT/custom_functions.ncl"
begin

    odir = "/lustre/atlas1/cli115/scratch/hannah6/init_files/"
    ofile = "cami_F_2000-01-01_01_1.9x2.5_L72.nc" 


    ; ifile = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/inic/fv/cami-mam3_0000-01-01_1.9x2.5_L30_c090306.nc"
    ; ifile = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/inic/homme/cami_mam3_Linoz_ne16np4_L72_c160614.nc"
    ifile = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/inic/homme/cami_mam3_Linoz_ne30np4_L72_c160214.nc"
;===========================================================================
;===========================================================================
    
    ; mfile = "/ccs/home/hannah6/maps/map_ne30np4_to_fv128x256_aave.20160301.nc"
    ; mfile = "/ccs/home/hannah6/maps/map_ne30np4_to_fv129x256_aave.150418.nc"
    ; mfile = "/ccs/home/hannah6/maps/map_ne30np4_to_fv129x256_aave.20150901.nc"
    mfile = "/ccs/home/hannah6/maps/map_ne30np4_to_fv256x512_bilin.20160301.nc"
    ; mfile = "/ccs/home/hannah6/maps/map_ne30np4_to_fv257x512_bilin.150418.nc"
    ; mfile = "/ccs/home/hannah6/maps/map_ne30np4_to_fv257x512_bilin.20150901.nc"


    ; cmd = "ncremap -m "+mfile+" -i "+ifile+" -o "+odir+ofile
    ; print(cmd)
    ; system(cmd)


;===========================================================================
; Just output level stuff
;===========================================================================
    ofile = "~/ACME/ACME_L72.nc"
    if fileexists(ofile) then system("rm "+ofie) end if
    infile  = addfile(ifile,"r")
    outfile = addfile(ofile,"c")

    outfile->hyai = infile->hyai
    outfile->hyam = infile->hyam
    outfile->hybi = infile->hybi
    outfile->hybm = infile->hybm
    outfile->ilev = infile->ilev
    outfile->lev  = infile->lev
    
    print("")
    print("    "+ofile)
    print("")
;===========================================================================
;===========================================================================

end