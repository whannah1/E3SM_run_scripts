; Walter Hannah - Lawrence Livermore National Lab
; Create a modified initialization file (cami) for the ACME model
; v1 - zero out cloud ice to solve run-time error in ACME-SP
; v2 - modify temperature profile to remove unstable layers near the surface
; v3 - modify vertical grid - average pairs of levels together to reduce grid
; v4 - modify vertical grid - similar to v3 - simply take away levels without averaging
load "$NCARG_ROOT/custom_functions.ncl"
begin

    ;;; number of levels to throw away
    nlev_reduce = 8    ; 72L > 64L

    nlev_in  = 72
    nlev_out = nlev_in - nlev_reduce

    idir  = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/inic/homme/"
    ifile = "cami_mam3_Linoz_ne30np4_L72_c160214.nc"
    ; ifile = "cami_mam3_Linoz_ne16np4_L72_c160614.nc"
    ; ifile = "cami_mam3_Linoz_ne4np4_L72_c160909.nc"

    odir  = "~/E3SM/init_files/"
    ; odir = "/lustre/atlas1/cli115/scratch/hannah6/init_files/"
    ofile = str_sub_str(ifile,"L"+nlev_in,"L"+nlev_out)


; idir  = "~/E3SM/init_files/"
; ifile = "aqua_init.v1.nc"
; odir  = "~/E3SM/init_files/"
; ofile = "cami_mam3_Linoz_ne30np4_L62_c160214_smoothed.nc"

    debug = False

;================================================================================
;================================================================================
    
    infile  = addfile(idir+ifile,"r")

    lev_in_idx  = ispan(0,nlev_in-1,1)
    lev_out_idx = lev_in_idx(:nlev_out-1)

    do k = 0,nlev_reduce-1
        kk = nlev_in-1-k*2-1
        lev_out_idx(nlev_out-1-k) = lev_in_idx(kk)
    end do

    ; print(lev_out_idx+1)
    ; exit

    ;;; useful block of code for probing the input grid
    ; if False
    ;     hyam = infile->hyam
    ;     hybm = infile->hybm
    ;     hyai = infile->hyai
    ;     hydi = infile->hybi
    ;     lev = infile->lev

    ;     hysum = hyam+hybm

    ;     nlev = dimsizes(hysum)
    ;     dhysum = new(nlev,double)
    ;     dhyam = new(nlev,double)
    ;     dhybm = new(nlev,double)

    ;     dhysum(1:nlev-1) = hysum(1:nlev-1) - hysum(0:nlev-2)
    ;     dhyam (1:nlev-1) = hyam (1:nlev-1) - hyam (0:nlev-2)
    ;     dhybm (1:nlev-1) = hybm (1:nlev-1) - hybm (0:nlev-2)

    ;     ; qplot_xy( lev, (/hyam,hybm/) )
    ;     ; qplot_xy( lev, (hyam+hybm) )

            
    ;     wks = gsn_open_wks("x11","?")
    ;     plot = new(4,graphic)
    ;         res = setres_xy()
    ;         res@xyMarkLineMode = "MarkLines"
    ;         res@xyMarker = 16
    ;     ; plot = gsn_csm_xy(wks,lev,dhysum,res)
    ;     plot = gsn_csm_xy(wks,lev,(/dhyam,dhybm/),res)

    ;         pres = setres_panel()
    ;         pres@gsnPanelYWhiteSpacePercent = 5
    ;         gsn_panel(wks,plot,(/1,1/),pres)

    ;     exit
    ; end if

    ;;; create output file
    ; if isfilepresent(odir+ofile) then system("rm "+odir+ofile) end if
    if fileexists(odir+ofile) then system("rm "+odir+ofile) end if
    outfile = addfile(odir+ofile,"c")

    var = getfilevarnames(infile)
;================================================================================
;================================================================================
    printline()
    flag = True

    do v = 0,dimsizes(var)-1

        if isatt(infile->$var(v)$,"long_name") then 
            var_name = infile->$var(v)$@long_name 
        else
            var_name = ""
        end if

        print("  "+strpad(var(v),20) + "    " + var_name)

        Vi := infile->$var(v)$

        dims := dimsizes(Vi)
        ndim := dimsizes(dims)

        if isdim(Vi,"ilev") .or. isdim(Vi,"lev") then

            if isdim(Vi, "ilev") then nk1 = nlev_in +1 else nk1 = nlev_in  end if
            if isdim(Vi, "ilev") then nk2 = nlev_out+1 else nk2 = nlev_out end if

            ; lev_array := ispan(0,nk2-1,1)

            if isdim(Vi, "ilev") then 
                lev_array = lev_out_idx(:nlev_in-1+1)
            else
                lev_array = lev_out_idx(:nlev_in-1)
            end if

            if ndim.eq.5 then Vo := Vi(:,lev_array,:,:,:) end if
            if ndim.eq.4 then Vo := Vi(:,lev_array,:,:) end if
            if ndim.eq.3 then Vo := Vi(:,lev_array,:) end if
            if ndim.eq.1 then Vo := Vi(  lev_array) end if

            ; kk0 = nk1 - nlev_reduce
            ; do kk = kk0,nk2-1
            ;     ki = (kk - kk0) * 2 + kk0

            ;     if var(v).eq."lev" then
            ;         print("  "+kk+"   "+ki+"   "+(ki+1) )
            ;         ; print("  "+kk+"   "+ki+"   "+(ki+1) +"   "+Vi(ki)+"   "+Vi(ki+1) +"   "+Vo(kk) )
            ;     end if

            ;     if ndim.eq.5 then Vo(:,kk,:,:,:) = (/ ( Vi(:,ki,:,:,:) + Vi(:,ki+1,:,:,:) )/2. /) end if
            ;     if ndim.eq.4 then Vo(:,kk,:,:)   = (/ ( Vi(:,ki,:,:)   + Vi(:,ki+1,:,:)   )/2. /) end if
            ;     if ndim.eq.3 then Vo(:,kk,:)     = (/ ( Vi(:,ki,:)     + Vi(:,ki+1,:)     )/2. /) end if
            ;     if ndim.eq.2 then Vo(:,kk)       = (/ ( Vi(:,ki)       + Vi(:,ki+1)       )/2. /) end if
            ;     if ndim.eq.1 then Vo(  kk)       = (/ ( Vi(  ki)       + Vi(  ki+1)       )/2. /) end if

            ; end do

            ;;; Set vertical coordinate

            if var(v).eq."lev"  then lev_out  = Vo end if
            if var(v).eq."ilev" then ilev_out = Vo end if

            if isdim(Vi, "lev") then Vo&lev  =  lev_out end if
            if isdim(Vi,"ilev") then Vo&ilev = ilev_out end if

            


if var(v).eq."lev" then
    fmt = "%8.2f"
    do k = 0,nk1-1
        str := sprinti("%2.2i",k)+"       "+sprinti("%2.2i",(nk1-k))+"   "+sprintf(fmt,Vi(k) )
        if k.lt.nk2 then str = str +"     "+ sprinti("%2.2i",(nk2-k))+"   "+ sprintf(fmt,Vo(k) ) end if
        print("    "+str)
    end do
    ; exit
end if


            ;;; old method - only considers bottom layer

            ; if isdim(Vi, "ilev") k2 = nlev_out else k2 = nlev_out-1 end if

            ; if ndim.eq.5 then Vo := Vi(:,:k2,:,:,:) end if
            ; if ndim.eq.4 then Vo := Vi(:,:k2,:,:) end if
            ; if ndim.eq.3 then Vo := Vi(:,:k2,:) end if
            ; if ndim.eq.1 then Vo := Vi(:k2) end if

            ; ; alternate method - average lowest layers instead of just omitting
            ; navg = nlev_in - nlev_out + 1
            ; do kk = nlev_out,nlev_in-1
            ;     if ndim.eq.5 then Vo(:,k2,:,:,:) = (/ Vo(:,k2,:,:,:) + Vi(:,kk,:,:,:,:) /) end if
            ;     if ndim.eq.4 then Vo(:,k2,:,:)   = (/ Vo(:,k2,:,:)   + Vi(:,kk,:,:)     /) end if
            ;     if ndim.eq.3 then Vo(:,k2,:)     = (/ Vo(:,k2,:)     + Vi(:,kk,:)       /) end if
            ;     if ndim.eq.1 then Vo(  k2)       = (/ Vo(  k2)       + Vi(  kk)         /) end if
            ; end do
            ; if ndim.eq.5 then Vo(:,k2,:,:,:) = (/ Vo(:,k2,:,:,:) / navg /) end if
            ; if ndim.eq.4 then Vo(:,k2,:,:)   = (/ Vo(:,k2,:,:)   / navg /) end if
            ; if ndim.eq.3 then Vo(:,k2,:)     = (/ Vo(:,k2,:)     / navg /) end if
            ; if ndim.eq.1 then Vo(  k2)       = (/ Vo(  k2)       / navg /) end if
            
        else
            Vo := Vi
        end if

; if ndim.eq.3 .and. flag then        
;     printVarSummary(Vo)
;     exit
;     flag = False
; end if

        outfile->$var(v)$ = Vo

;;; use this to break out early and make a plot
if debug then
if var(v).eq."T" then
    break
end if
end if


    end do

    printline()
;===========================================================================
;===========================================================================
    ;;; code for comparing input and output grid
    if True then
        ;------------------------------------------------------
        ;------------------------------------------------------
        hyam := infile->hyam
        hybm := infile->hybm
        lev1 := infile->lev
        hysum1 = hyam+hybm

        tmpfile = addfile(odir+ofile,"r")
        hyam := tmpfile->hyam
        hybm := tmpfile->hybm
        lev2 := tmpfile->lev
        hysum2 = hyam+hybm
        
        fig_file = "cami.v3.lev_chk1"
        wks = gsn_open_wks("png",fig_file)
        plot = new(2,graphic)
            res = setres_xy()
            res@xyMarkLineMode = "MarkLines"
            res@xyMarker = 16
        plot(0) = gsn_csm_xy(wks,lev1,hysum1,res)
        plot(1) = gsn_csm_xy(wks,lev2,hysum2,res)

            pres = setres_panel()
            pres@gsnPanelYWhiteSpacePercent = 5
            gsn_panel(wks,plot,(/1,dimsizes(plot)/),pres)

        trimPNG(fig_file)
        ;------------------------------------------------------
        ;------------------------------------------------------
        T1 := infile->T
        T2 := tmpfile->T

        top_lev = 500.
        dT = 0.5

        aT1 = dim_avg_n_Wrap(dim_avg_n_Wrap(T1(:,{top_lev:},:),2),0)
        aT2 = dim_avg_n_Wrap(dim_avg_n_Wrap(T2(:,{top_lev:},:),2),0)

        fig_file = "cami.v3.lev_chk2"
        wks := gsn_open_wks("png",fig_file)
        plot := new(1,graphic)
            res = setres_xy()
            res@xyMarkLineMode = "MarkLines"
            res@xyMarker   = 16
            res@trYReverse = True
            res@trXMinF = min( (/ min(aT1), min(aT2+dT) /) )
            res@trXMaxF = max( (/ max(aT1), max(aT2+dT) /) )

        ; plot(0) = gsn_csm_xy(wks,aT1,lev1,res)
        ; plot(1) = gsn_csm_xy(wks,aT2,lev2,res)

        res@xyLineColor   = "blue"
        res@xyMarkerColor = res@xyLineColor
        plot(0) = gsn_csm_xy(wks,aT1,lev1({top_lev:}),res)

        res@xyLineColor = "red"
        res@xyMarkerColor = res@xyLineColor
        overlay( plot(0) , gsn_csm_xy(wks,aT2+dT,lev2({top_lev:}),res) )

            pres = setres_panel()
            pres@gsnPanelYWhiteSpacePercent = 5
            gsn_panel(wks,plot,(/1,dimsizes(plot)/),pres)

        trimPNG(fig_file)
        ;------------------------------------------------------
        ;------------------------------------------------------
        ; exit
    end if
;===========================================================================
;===========================================================================
    print("")
    print("")
    print("  input file  : "+idir+ifile)
    print("")
    print("  output file : "+odir+ofile)
    print("")
    print("")

;================================================================================
; regrid for viewing
;================================================================================
    
    mfile = "/ccs/home/hannah6/maps/map_ne30np4_to_fv128x256_aave.20160301.nc"
    ofile2 = str_sub_str(ofile,".nc",".remap.nc")

    print("")
    print("USe this command to create a regrided file for viewing...")
    print("   ncremap  -m "+mfile+" -i  "+odir+ofile+" -o "+odir+ofile2)
    print("")
;================================================================================
;================================================================================

end