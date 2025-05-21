; Walter Hannah - Lawrence Livermore National Lab
; Create a RCEMIP initialization file (cami) for the E3SM model
; v1 - use existing cami file
; v2 - use existing cami file only for var names - get grid info from latlon file
load "$NCARG_ROOT/custom_functions.ncl"
begin

    host = getenv("HOST")
    if isStrSubset(host,"edison") then host = "nersc" end if
    if isStrSubset(host,"cori")   then host = "nersc" end if
    if isStrSubset(host,"titan")  then host = "olcf"  end if


    setfileoption("nc", "Format",  "64BitOffset")
    
    debug = False

    To = 300.       ; 295 / 300 / 305

    ;;; day limits for SCM data
    d1 =  70
    d2 = 100

    res = "ne4"    ; ne4 / ne30

    ;;; input file for global grid
    if host.eq."olcf"  then idir  = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/inic/homme/" end if
    if host.eq."nersc" then idir  = "/project/projectdirs/acme/inputdata/atm/cam/inic/homme/" end if


    if res.eq."ne30" then ifile = "cami_mam3_Linoz_ne30np4_L72_c160214.nc" end if
    if res.eq."ne4"  then ifile = "cami_mam3_Linoz_ne4np4_L72_c160909.nc" end if
    

    ;;; input file from SCM RCE equilibrium run
    sdir  = "~/E3SM/init_files/"
    sfile = "E3SM_SCM_RCE_"+To+"_SP1_T42_64x1_4km_00.cam.h1.0000-01-01-00000.nc"


    ;;; output file
    odir  = "~/E3SM/init_files/"
    ofile = str_sub_str(ifile,".nc","_RCEMIP.nc")

;================================================================================
; Print setup info for reference
;================================================================================
    
    print("")
    print("  ifile : "+idir+ifile)
    print("  sfile : "+sdir+sfile)
    print("  ofile : "+odir+ofile)
    print("")


;================================================================================
; open input files and create output file
;================================================================================
    
    if .not.debug then
        ; if isfilepresent(odir+ofile) then system("rm "+odir+ofile) end if
        if fileexists(odir+ofile) then system("rm "+odir+ofile) end if
        outfile = addfile(odir+ofile,"c")
    end if
    
    infile  = addfile(idir+ifile,"r")
    scmfile = addfile(sdir+sfile,"r")


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

        ; print("  "+strpad(var(v),20) + "    " + var_name)

        V_in = infile->$var(v)$

        ;--------------------------------------------------
        ; date/time variables
        ;--------------------------------------------------
        ; if var(v) .eq. "nbdate" then V = 20000101 end if
        ; if var(v) .eq. "ndcur"  then V = 000 end if
        ; if var(v) .eq. "date"   then V = 20000101 end if


        ;--------------------------------------------------
        ; main variables set from SCM run
        ;--------------------------------------------------
        if any(var(v).eq.(/"T","Q"/)) then 

            S = scmfile->$var(v)$({d1:d2},:,0,0)

            ;;; Average in time
            S_avg = dim_avg_n(S,0)

            V_out = conform( V_in, S_avg, 1 )

            ;;; copy meta data from infile
            copy_VarMeta(V_in,V_out)

            ;;; clip min T values for RRTMGP (can't go below 160)
            if var(v).eq."T" then
                min_T = 170.
                V_out = where(V_out.lt.min_T,min_T,V_out)
            end if

            delete(S)

        end if

        if var(v).eq."PS" then
            S = avg( scmfile->PS({d1:d2},0,0) )
            V_out = V_in
            V_out = (/ totype(S,typeof(V_out)) /)
            delete(S)
        end if
        ;--------------------------------------------------
        ; analytic ozone profile
        ;--------------------------------------------------
        if var(v).eq."O3" then
            p = V_in&lev

            g1 = 3.6478
            g2 = 0.83209
            g3 = 11.3515

            tmp = g1 * p^g2 * exp(-p/g3)

            V_out = conform( V_in, tmp, 1)

            copy_VarMeta(V_in,V_out)

            ; convert VMR (ppmv) to MMR (mol/mol)
            V_out = (/ V_out / ( 28.9644 / 47.9982 * 1e6 )  /)
        end if
        ;--------------------------------------------------
        ; zero out horizontal wind
        ;--------------------------------------------------
        if any(var(v).eq.(/"U","V"/)) then 
            V_out := V_in
            V_out = (/ 0.0 /)
            ; copy_VarMeta(V_in, V_out)
        end if
        ;--------------------------------------------------
        ; zero out cloud liquid and ice
        ;--------------------------------------------------
        if any(var(v).eq.(/"CLDLIQ","CLDICE"/)) then
            V_out := V_in
            V_out = (/ 0.0 /)
            ; copy_VarMeta(V_in, V_out)
        end if
        ;--------------------------------------------------
        ; zero out aerosol fields
        ;--------------------------------------------------
        if       isStrSubset(var(v),"bc_")  \
            .or. isStrSubset(var(v),"dst_") \
            .or. isStrSubset(var(v),"mom_") \
            .or. isStrSubset(var(v),"ncl_") \
            .or. isStrSubset(var(v),"num_") \
            .or. isStrSubset(var(v),"pom_") \
            .or. isStrSubset(var(v),"so4_") \
            .or. isStrSubset(var(v),"soa_") \
        then
            V_out := V_in
            V_out = (/ 0.0 /)
            ; copy_VarMeta(V_in,V_out)
        end if
        ;--------------------------------------------------
        ; zero out other tracers...
        ;--------------------------------------------------
        if       var(v).eq."SO2"   \
            .or. var(v).eq."SOAG"  \
            .or. var(v).eq."DMS"   \
            .or. var(v).eq."H2O2"  \
            .or. var(v).eq."H2SO4" \
        then
            V_out := V_in
            V_out = (/ 0.0 /)
            ; copy_VarMeta(V_in,V_out)
        end if
        ;--------------------------------------------------
        ; Add white noise to certain fields?
        ;--------------------------------------------------
        if var(v).eq."T" then scale_factor = 0.25 end if
        ; if var(v).eq."" then scale_factor = ??? end if

        if isvar("scale_factor") then
            dims := dimsizes(V_out)
            rseed1 = toint( v * 5e6 )
            rseed2 = toint( v * 1e4 )
            random_setallseed(rseed1,rseed2)
            unf = random_uniform(-1., 1., dims)
            V_out = (/ V_out + unf*scale_factor /)
            delete(scale_factor)
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