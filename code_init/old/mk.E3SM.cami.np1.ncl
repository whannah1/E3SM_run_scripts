; Walter Hannah - Lawrence Livermore National Lab
; Create new initialization file (cami) with 1 column per element
; v1 - average data on middle element nodes
load "$NCARG_ROOT/custom_functions.ncl"
begin

    host = getenv("HOST")
    if isStrSubset(host,"edison") then host = "nersc" end if
    if isStrSubset(host,"cori")   then host = "nersc" end if
    if isStrSubset(host,"titan")  then host = "olcf"  end if


    setfileoption("nc", "Format",  "64BitOffset")
    
    debug = True

    idir  = "~/E3SM/init_files/"
    ifile = "cami_mam3_Linoz_ne4np4_L72_c160909_RCEMIP.nc"

    ;;; output file
    odir  = "~/E3SM/init_files/"
    ofile = str_sub_str(ifile,".nc",".np1.nc")

;================================================================================
; Print setup info for reference
;================================================================================
    
    print("")
    print("  ifile : "+idir+ifile)
    print("  ofile : "+odir+ofile)
    print("")

;================================================================================
; open input files and create output file
;================================================================================
    
    if .not.debug then
        if fileexists(odir+ofile) then system("rm "+odir+ofile) end if
        outfile = addfile(odir+ofile,"c")
    end if
    
    infile  = addfile(idir+ifile,"r")

    var = getfilevarnames(infile)

    ; var := "O3"

; print(var)
; printline()
; tmp = infile->CLDLIQ
; printVarSummary(tmp)
; printMAM(tmp)
; exit

;================================================================================
; Loop through input file variables
;================================================================================
    ; printline()
    do v = 0,dimsizes(var)-1

        if isatt(infile->$var(v)$,"long_name") then 
            var_name = infile->$var(v)$@long_name 
        else
            var_name = ""
        end if

        print("  "+strpad(var(v),20) + "    " + var_name)

        V_in = infile->$var(v)$

        ;--------------------------------------------------
        ; date/time variables
        ;--------------------------------------------------
        ; if var(v) .eq. "nbdate" then V = 20000101 end if
        ; if var(v) .eq. "ndcur"  then V = 000 end if
        ; if var(v) .eq. "date"   then V = 20000101 end if
        
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
    
    ; mfile = "/ccs/home/hannah6/maps/map_ne30np4_to_fv128x256_aave.20160301.nc"
    ; ofile2 = str_sub_str(ofile,".nc",".remap.nc")

    ; print("")
    ; print("ncremap  -m "+mfile+" -i  "+odir+ofile+" -o "+odir+ofile2)
    ; print("")
    
;================================================================================
;================================================================================

end