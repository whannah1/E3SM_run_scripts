; Walter Hannah - Lawrence Livermore National Lab
; Create a modified initialization file (cami) for the ACME model
; v1 - zero out cloud ice to solve run-time error in ACME-SP
; v2 - modify temperature profile to remove unstable layers near the surface
; v3 - modify vertical grid - average pairs of levels together to reduce grid
; v4 - modify vertical grid - similar to v3 - simply take away levels without averaging
load "$NCARG_ROOT/custom_functions.ncl"
begin

    ;;; number of levels to reduce by half
    ; nlev_reduce = 44    ; 72L > 50L
    ; nlev_reduce = 20    ; 72L > 62L
    ; nlev_reduce = 16    ; 72L > 64L
    ; nlev_reduce = 10    ; 72L > 68L
    nlev_reduce = 8    ; 72L > 68L
    ; nlev_reduce = 4    ; 72L > 70L

    nlev_in  = 72
    nlev_out = nlev_in - nlev_reduce/2

    idir  = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/inic/homme/"
    ifile = "cami_mam3_Linoz_ne30np4_L72_c160214.nc"
    ; ifile = "cami_mam3_Linoz_ne16np4_L72_c160614.nc"
    ; ifile = "cami_mam3_Linoz_ne4np4_L72_c160909.nc"

    ; odir = "/lustre/atlas1/cli115/scratch/hannah6/init_files/"
    odir  = "~/E3SM/init_files/"
    ofile = str_sub_str(ifile,"L"+nlev_in,"L"+nlev_out)


; idir  = "~/E3SM/init_files/"
; ifile = "aqua_init.v1.nc"
; odir  = "~/E3SM/init_files/"
; ofile = "cami_mam3_Linoz_ne30np4_L"+nlev_out+"_c160214_smoothed.nc"

    debug = True

    chk_lev_out = False  ; just print new levels and exit

    chk_sum = False

    setfileoption("nc", "Format",  "64BitOffset") 

;================================================================================
;================================================================================
    
    infile  = addfile(idir+ifile,"r")

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

    if chk_lev_out then var := "lev" end if

    if debug then var := (/"lev","ilev","T"/) end if
;================================================================================
;================================================================================
    printline()
    flag = True

    PS = infile->PS
    PO = infile->P0

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

            ;;; nk1 = # of input levels
            ;;; nk2 = # of output levels
            ;;; kk0 = loop index start (only loop over levels that need to be reduced)
            ;;; kk = loop index - goes over lower layers of output grid
            ;;; ki = used to find corresponding layers in input grid

            if isdim(Vi, "ilev") then nk1 = nlev_in +1 else nk1 = nlev_in  end if
            if isdim(Vi, "ilev") then nk2 = nlev_out+1 else nk2 = nlev_out end if

            lev_array := ispan(0,nk2-1,1)
            ; lev_array(nlev_reduce:) = 

            if ndim.eq.5 then Vo := Vi(:,lev_array,:,:,:) end if
            if ndim.eq.4 then Vo := Vi(:,lev_array,:,:) end if
            if ndim.eq.3 then Vo := Vi(:,lev_array,:) end if
            if ndim.eq.1 then Vo := Vi(  lev_array) end if

            kk0 = nk1 - nlev_reduce
            do kk = kk0,nk2-1
                if isdim(Vi,  "lev") then ki = (kk - kk0) * 2 + kk0 end if
                if isdim(Vi, "ilev") then ki = (kk - kk0) * 2 + kk0 end if

                ; if var(v).eq."lev" then
                ;     print("  "+kk+"   "+ki+"   "+(ki+1) )
                ; end if

                ; if var(v).eq."ilev" then
                ;     print("  "+kk+"   "+(ki+1));+"   "+( ((ki-kk0)/2)%2 ) )
                ; end if
                    

                ;;; for most variables we average 2 levels together
                if isdim(Vi, "lev") then 
                    if ndim.eq.5 then Vo(:,kk,:,:,:) = (/ ( Vi(:,ki,:,:,:) + Vi(:,ki+1,:,:,:) )/2. /) end if
                    if ndim.eq.4 then Vo(:,kk,:,:)   = (/ ( Vi(:,ki,:,:)   + Vi(:,ki+1,:,:)   )/2. /) end if
                    if ndim.eq.3 then Vo(:,kk,:)     = (/ ( Vi(:,ki,:)     + Vi(:,ki+1,:)     )/2. /) end if
                    if ndim.eq.2 then Vo(:,kk)       = (/ ( Vi(:,ki)       + Vi(:,ki+1)       )/2. /) end if
                    if ndim.eq.1 then Vo(  kk)       = (/ ( Vi(  ki)       + Vi(  ki+1)       )/2. /) end if
                end if

                ;;; for interface variables we simply omit layers instead of averaging
                if isdim(Vi,"ilev") then 
                    if ndim.eq.5 then Vo(:,kk,:,:,:) = (/ Vi(:,ki+1,:,:,:) /) end if
                    if ndim.eq.4 then Vo(:,kk,:,:)   = (/ Vi(:,ki+1,:,:)   /) end if
                    if ndim.eq.3 then Vo(:,kk,:)     = (/ Vi(:,ki+1,:)     /) end if
                    if ndim.eq.2 then Vo(:,kk)       = (/ Vi(:,ki+1)       /) end if
                    if ndim.eq.1 then Vo(  kk)       = (/ Vi(  ki+1)       /) end if
                end if

            end do

            ;;; Set vertical coordinate

            if var(v).eq."lev"  then lev_out  = Vo end if
            if var(v).eq."ilev" then ilev_out = Vo end if

            if isdim(Vi, "lev") then Vo&lev  =  lev_out end if
            if isdim(Vi,"ilev") then Vo&ilev = ilev_out end if

            ;;; check mass weighted integral
            if chk_sum then
                if all(var(v).ne.(/"lev","ilev","hyam","hyai","hybm","hybi"/)) then
                    if isdim(Vi, "lev") then 
                        p1 := conform(Vi, infile->hyam,1)*PO + conform(Vi, infile->hybm,1) * conform(Vi,PS,(/ndim-1-1,ndim-1/))
                        p2 := conform(Vo,outfile->hyam,1)*PO + conform(Vo,outfile->hybm,1) * conform(Vo,PS,(/ndim-1-1,ndim-1/))
                        p1!1 = "lev"
                        p2!1 = "lev"
                        p1&lev = infile->lev
                        p2&lev = lev_out
                    else
                        p1 = conform(Vi, infile->hyai,1)*PO + conform(Vi, infile->hybi,1) * conform(Vi,PS,(/ndim-1-1,ndim-1/))
                        p2 = conform(Vo,outfile->hyai,1)*PO + conform(Vo,outfile->hybi,1) * conform(Vo,PS,(/ndim-1-1,ndim-1/))
                        p1!1 = "ilev"
                        p2!1 = "ilev"
                        p1&lev = infile->ilev
                        p2&lev = ilev_out
                    end if

                    p1!2 = "ncol"
                    p2!2 = "ncol"
                    p1@units = "Pa"
                    p2@units = "Pa"
                    
                    dp1 = calc_dP(p1,PS)
                    dp2 = calc_dP(p2,PS)

                    ;;; mass weighted integral
                    ; sum1 = sum( Vi * dp1 )
                    ; sum2 = sum( Vo * dp2 )

                    ;;; mass weighted average
                    sum1 = sum( Vi * dp1 ) / sum(dp1)
                    sum2 = sum( Vo * dp2 ) / sum(dp2)

                    fmt = "%8.2f"
                    print("        sum1: "+sprintf(fmt,sum1)+"      sum2: "+sprintf(fmt,sum2)+"      diff: "+sprintf(fmt,(sum1-sum2)) )
                end if
            end if ; chk_sum

            

; if chk_lev_out then 
    if var(v).eq."lev" then
        fmt = "%8.2f"
        do k = 0,nk1-1
            str := sprinti("%2.2i",k)+"       "+sprinti("%2.2i",(nk1-k))+"   "+sprintf(fmt,Vi(k) )
            if k.lt.nk2 then 
                if Vi(k).eq.Vo(k) then 
                    if (nk1-k).eq.58 then
                        str = str + " ==== "
                    else
                        str = str + "  ==  "
                    end if
                else
                    str = str + "      "   ;+"     "+
                end if
                str = str + sprinti("%2.2i",(nk2-k))+"   "+ sprintf(fmt,Vo(k) ) 
                
            end if
            print("    "+str)
        end do
        if chk_lev_out then exit end if
    end if
; end if

; if var(v).eq."ilev" then
;     fmt = "%8.2f"
;     do k = 0,nk1-1
;         str := sprinti("%2.2i",k)+"       "+sprinti("%2.2i",(nk1-k))+"   "+sprintf(fmt,Vi(k) )
;         if k.lt.nk2 then str = str +"     "+ sprinti("%2.2i",(nk2-k))+"   "+ sprintf(fmt,Vo(k) ) end if
;         print("    "+str)
;     end do
;     exit
; end if


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
        tmpfile = addfile(odir+ofile,"r")
        ;------------------------------------------------------
        ;------------------------------------------------------
        if False then 
            hyam := infile->hyam
            hybm := infile->hybm
            lev1 := infile->lev
            hysum1 = hyam+hybm

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
        end if
        ;------------------------------------------------------
        ;------------------------------------------------------
        if False then 
            T1 := infile->T
            T2 := tmpfile->T

            top_lev = 700.  ; limit for better viewing
            dT = 0.0        ; offset to separate the lines

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
            res@xyMarker    = 4         ; open circle
            res@xyMarkerColor = res@xyLineColor
            overlay( plot(0) , gsn_csm_xy(wks,aT2+dT,lev2({top_lev:}),res) )

                pres = setres_panel()
                pres@gsnPanelYWhiteSpacePercent = 5
                gsn_panel(wks,plot,(/1,dimsizes(plot)/),pres)

            trimPNG(fig_file)
        end if
        ;------------------------------------------------------
        ;------------------------------------------------------
        if True then 
            mlev1 := infile->lev
            mlev2 := tmpfile->lev

            ilev1 := infile->ilev
            ilev2 := tmpfile->ilev

            mX1 = new(dimsizes(mlev1),float)
            mX2 = new(dimsizes(mlev2),float)
            iX1 = new(dimsizes(ilev1),float)
            iX2 = new(dimsizes(ilev2),float)

            top_lev = 900.  ; limit for better viewing
            dx = 0.0        ; offset to separate the lines

            mX1 = 1 ;+ 0.3
            iX1 = 1 ;- 0.3
            mX2 = 2 ;- 0.3
            iX2 = 2 ;+ 0.3

            fig_file = "cami.v3.lev_chk3"
            wks := gsn_open_wks("png",fig_file)
            plot := new(1,graphic)
                res = setres_xy()
                res@tmXBOn = False
                res@trYReverse = True
                res@trXMinF = 0
                res@trXMaxF = 3
                res@trYMinF = top_lev

                res@xyLineThicknessF = 12

                res@tiYAxisString = "Pressure [hPa]"

                ; res@xyMarkLineMode = "MarkLines"
                ; res@xyMarker            = 2
                ; res@xyMarkerSizeF       = 0.02
                ; res@xyLineThicknessF    = 12.

                res@xyMarkerThicknessF = res@xyLineThicknessF


            res@xyLineColor   = "blue"
            res@xyMarkerColor = res@xyLineColor
            ; plot(0) = gsn_csm_xy(wks,mX1,mlev1,res)
            plot(0) = gsn_csm_xy(wks,iX1,ilev1,res)

            res@xyLineColor = "red"
            res@xyMarkerColor = res@xyLineColor
            ; overlay( plot(0) , gsn_csm_xy(wks,mX2,mlev2,res) )
            overlay( plot(0) , gsn_csm_xy(wks,iX2,ilev2,res) )

            ; res@xyLineColor = "blue"
            ; res@xyMarkerColor = res@xyLineColor
            ; overlay( plot(0) , gsn_csm_xy(wks,iX1,ilev1,res) )

            ; res@xyLineColor = "red"
            ; res@xyMarkerColor = res@xyLineColor
            ; overlay( plot(0) , gsn_csm_xy(wks,iX2,ilev2,res) )


            dxi = 0.25
            dxm = 0.2           

            lres = setres_xy()
            lres@xyLineThicknessF = res@xyLineThicknessF 

            lres@xyLineColor = "blue"

            lres@xyDashPattern = 0
            tlev := ilev1
            txx = mX1(0)
            dx = dxi
            do k = 0,dimsizes(tlev)-1
                xx = txx + (/-dx,dx/)
                yy = tlev(k) * (/1,1/)
                overlay( plot(0) , gsn_csm_xy(wks,xx,yy,lres) )            
            end do

            lres@xyDashPattern = 2
            tlev := mlev1
            dx = dxm
            do k = 0,dimsizes(tlev)-1
                xx = txx + (/-dx,dx/)
                yy = tlev(k) * (/1,1/)
                overlay( plot(0) , gsn_csm_xy(wks,xx,yy,lres) )            
            end do


            lres@xyLineColor = "red"

            lres@xyDashPattern = 0
            tlev := ilev2
            txx = mX2(0)
            dx = dxi
            do k = 0,dimsizes(tlev)-1
                xx = txx + (/-dx,dx/)
                yy = tlev(k) * (/1,1/)
                overlay( plot(0) , gsn_csm_xy(wks,xx,yy,lres) )            
            end do

            lres@xyDashPattern = 2
            tlev := mlev2
            dx = dxm
            do k = 0,dimsizes(tlev)-1
                xx = txx + (/-dx,dx/)
                yy = tlev(k) * (/1,1/)
                overlay( plot(0) , gsn_csm_xy(wks,xx,yy,lres) )            
            end do



                pres = setres_panel()
                pres@gsnPanelYWhiteSpacePercent = 5
                gsn_panel(wks,plot,(/1,dimsizes(plot)/),pres)

            trimPNG(fig_file)
        end if
        ;------------------------------------------------------
        ;------------------------------------------------------
        if debug then exit end if
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
    print("Use this command to create a regrided file for viewing...")
    print("   ncremap  -m "+mfile+" -i  "+odir+ofile+" -o "+odir+ofile2)
    print("")
;================================================================================
;================================================================================

end