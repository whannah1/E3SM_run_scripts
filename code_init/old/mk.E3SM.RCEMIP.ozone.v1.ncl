; Walter Hannah - Lawrence Livermore National Lab
; Create a RCEMIP initialization file (cami) for the E3SM model
; v1 - 
load "$NCARG_ROOT/custom_functions.ncl"
begin

    host = getenv("HOST")
    if isStrSubset(host,"edison") then host = "nersc" end if
    if isStrSubset(host,"cori")   then host = "nersc" end if
    if isStrSubset(host,"titan")  then host = "olcf"  end if


    ; setfileoption("nc", "Format",  "64BitOffset")
    ; setfileoption("nc", "Format",  "netcdf4")
    setfileoption("nc", "Format",  "classic")
    
    debug = False

    ; res = "ne4"    ; ne4 / ne30

    ;;; input file for global grid
    if host.eq."olcf"  then idir  = "/lustre/atlas1/cli900/world-shared/cesm/" end if
    if host.eq."nersc" then idir  = "/project/projectdirs/acme/" end if
    idir = idir+"inputdata/atm/cam/ozone/"
    ; idir = idir+"inputdata/atm/cam/inic/homme/"
    ifile = "ozone_1.9x2.5_L26_2000clim_c091112.nc"

    ;;; alternate method for SE grid - doesn't work for some reason...
    ; idir = "~/E3SM/init_files/"
    ; if res.eq."ne30" then ifile = "cami_mam3_Linoz_ne30np4_L72_c160214.nc" end if
    ; if res.eq."ne4"  then ifile = "cami_mam3_Linoz_ne4np4_L72_c160909.nc" end if    
    ; ifile = str_sub_str(ifile,".nc","_RCEMIP.nc")

    ; Use this for vertical coord
    lev_file = "/project/projectdirs/acme/inputdata/atm/cam/inic/homme/cami_mam3_Linoz_ne30np4_L72_c160214.nc"

    ;;; output file
    odir  = "~/E3SM/init_files/"
    ofile = "RCEMIP_ozone.v1.nc"

    ; do_extend_levels = True         ; Extend data upward

    const_sfc_pressure = 101480.

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
        if isfilepresent(odir+ofile) then system("rm "+odir+ofile) end if
        ; if fileexists(odir+ofile) then system("rm "+odir+ofile) end if
        outfile = addfile(odir+ofile,"c")
    end if
    
    infile_data  = addfile(idir+ifile,"r")

    infile_lev  = addfile(lev_file,"r")

    ; var = (/"time","O3","P0","PS","date","datesec","hyai","hyam","hybi","hybm","lev","ilev"/)

    var = getfilevarnames(infile_data)

;================================================================================
; Loop through input file variables
;================================================================================
    ; printline()
    do v = 0,dimsizes(var)-1

        if isatt(infile_data->$var(v)$,"long_name") then 
            var_name = infile_data->$var(v)$@long_name 
        else
            var_name = ""
        end if

        ;--------------------------------------------------
        ;--------------------------------------------------
        if any(var(v).eq.(/"P0","lev","ilev","hyam","hybm","hyai","hybi"/)) then
            V_in := infile_lev->$var(v)$
        else
            V_in = infile_data->$var(v)$
        end if
        ;--------------------------------------------------
        ;--------------------------------------------------
        if var(v).eq."PS" then
            V_out = V_in
            V_out = (/ const_sfc_pressure /)
        end if
        ;--------------------------------------------------
        ; analytic ozone profile from RCEMIP protocol
        ;--------------------------------------------------
        if var(v).eq."O3" then

            P0   = infile_lev->P0
            hyam = infile_lev->hyam
            hybm = infile_lev->hybm

            PS = infile_data->PS
            PS = (/ const_sfc_pressure /)  ; reset PS to constant value
            
            dims = dimsizes(V_in)
            lev_ind = 1
            dims(lev_ind) = dimsizes(infile_lev->lev)

            p = new(dims,double)
            do t = 0,dims(0)-1
                do k = 0,dims(1)-1
                    do j = 0,dims(2)-1
                        do i = 0,dims(3)-1
                            p(t,k,j,i) = ( P0*hyam(k) + PS(t,j,i)*hybm(k) )/100.
                        end do
                    end do
                end do
            end do

            ; Shape parameters from RCEMIP protocol
            g1 = 3.6478
            g2 = 0.83209
            g3 = 11.3515

            V_out = g1 * p^g2 * exp(-p/g3)
            
            ; convert VMR (ppmv) to MMR (mol/mol)
            V_out = (/ V_out / ( 28.9644 / 47.9982 * 1e6 )  /)
            
            copy_VarAtts(V_in,V_out)
            V_out!0 = "time"
            V_out!1 = "lev"
            V_out!2 = "lat"
            V_out!3 = "lon"

            V_out&time = V_in&time
            V_out&lev = infile_lev->lev
            V_out&lat = V_in&lat
            V_out&lon = V_in&lon

            ; printVarSummary(V_in)
            ; printVarSummary(V_out)
            ; exit

        end if


        ;;; alternate method for SE grid - doesn't work for some reason...
        ;--------------------------------------------------
        ; date/time variables specified from: 
        ; inputdata/atm/cam/ozone/ozone_1.9x2.5_L26_2000clim_c091112.nc
        ;--------------------------------------------------
        ; if var(v).eq."time" then 
        ;     time = new(12,double)
        ;     time = (/55129, 55160, 55188, 55219, \
        ;              55249, 55280, 55310, 55341, \
        ;              55372, 55402, 55433, 55463 /) 
        ;     time!0 = "time"
        ;     time&time = time
        ;     time@long_name = "time"
        ;     time@units     = "days since 1849-01-01 00:00" ;
        ;     time@calendar  = "noleap"
        ;     time@bounds    = "time_bnds"
        ;     V_out = time
        ; end if

        ; if var(v).eq."date" then 
        ;     V_out = (/20000115, 20000215, 20000315, 20000415, \
        ;               20000515, 20000615, 20000715, 20000815, \
        ;               20000915, 20001015, 20001115, 20001215 /) 
        ;     V_out!0 = "time"
        ;     V_out&time = time
        ;     V_out@long_name = "date"
        ;     V_out@format    = "YYYYMMDD"
        ; end if

        ; if var(v).eq."datesec" then 
        ;     V_out = (/0,0,0,0,0,0,0,0,0,0,0,0/) 
        ;     V_out!0 = "time"
        ;     V_out&time = time
        ;     V_out@long_name = "current seconds of current date"
        ; end if
        ;--------------------------------------------------
        ;--------------------------------------------------
        if .not.isvar("V_out") then
            V_out = V_in
        end if
        ;--------------------------------------------------
        ; Add redundant time records
        ;--------------------------------------------------
        ; if isdim(V_out,"time") then 
        ;     if dimsizes(V_out&time).eq.1 then
        ;         tmp = V_out
        ;         dims := dimsizes(V_out)
        ;         ndim := dimsizes(dims)
        ;         dims(0) = 12
        ;         V_out := new(dims,typeof(tmp))
        ;         do t = 0,11
        ;             if ndim.eq.3 then V_out(t,:,:) = tmp(0,:,:) end if
        ;             if ndim.eq.2 then V_out(t,:)   = tmp(0,:)   end if
        ;             if ndim.eq.1 then V_out(t)     = tmp(0)     end if
        ;         end do
        ;         delete([/tmp,dims/])
        ;         V_out!0 = "time"
        ;         time&time = time
        ;     end if
        ; end if
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
;================================================================================

end