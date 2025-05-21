; Walter Hannah - Lawrence Livermore National Lab
; Create a modified initialization file (cami) for the ACME model
; v1 - zero out cloud ice to solve run-time error in ACME-SP
; v2 - modify temperature profile to remove unstable layers near the surface
; v3 - modify vertical grid - remove lowest levels
load "$NCARG_ROOT/custom_functions.ncl"
begin

    idir  = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/inic/homme/"
    ; ifile = "cami_mam3_Linoz_ne30np4_L72_c160214.nc"
    ; ifile = "cami_mam3_Linoz_ne16np4_L72_c160614.nc"
    ifile = "cami_mam3_Linoz_ne4np4_L72_c160909.nc"

    ; odir  = "~/ACME/init_files/"
    odir = "/lustre/atlas1/cli115/scratch/hannah6/init_files/"
    ofile = str_sub_str(ifile,".nc",".no_ice.nc")

;================================================================================
;================================================================================
    if isfilepresent(ofile) then system("rm "+ofile) end if
    ; if fileexists(ofile) then system("rm "+ofile) end if
    
    infile  = addfile(idir+ifile,"r")
    outfile = addfile(odir+ofile,"c")

    ; exit

    var = getfilevarnames(infile)
;================================================================================
;================================================================================
    ; printline()
    do v = 0,dimsizes(var)-1

        if isatt(infile->$var(v)$,"long_name") then 
            var_name = infile->$var(v)$@long_name 
        else
            var_name = ""
        end if

        ; print("  "+strpad(var(v),20) + "    " + var_name)

        V = infile->$var(v)$

        ; if var(v) .eq. "nbdate" then V = 20000101 end if
        ; if var(v) .eq. "ndcur"  then V = 000 end if
        ; if var(v) .eq. "date"   then V = 20000101 end if

        if any(var(v) .eq. (/"CLDICE","NUMICE"/) ) then 
            V(:,{:50},:) = 0.
        end if
        
        outfile->$var(v)$ = V

        delete(V)

    end do
    ; printline()
;===========================================================================
;===========================================================================
    print("")
    print("  "+idir+ifile)
    print("  "+odir+ofile)
    print("")

;================================================================================
; regrid for viewing
;================================================================================
    
    mfile = "/ccs/home/hannah6/maps/map_ne30np4_to_fv128x256_aave.20160301.nc"
    ofile2 = str_sub_str(ofile,".nc",".remap.nc")

    print("")
    print("ncremap  -m "+mfile+" -i  "+odir+ofile+" -o "+odir+ofile2)
    print("")
;================================================================================
;================================================================================

end