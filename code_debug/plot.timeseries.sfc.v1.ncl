; plot a timeseries of ACME surface quantities for debugging 
; use model output in scratch directory
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/custom_functions.ncl"
; load "$NCARG_ROOT/custom_functions_ACME.ncl"
begin

    idir = "/lustre/atlas1/cli115/scratch/hannah6/"

    ; case = "ACME_ZM_CTL_ne30_03"
    case = "ACME_SP2_CTL_ne16_06"
    ; case = "ACME_SP2_CTL_ne30_05"
    ; case = "ACME_SP2_CTL_ne4_31"
    

    fig_type = "png"
    fig_file = "~/ACME/figs_debug/timeseries.sfc.v1"

    ; var = (/"TS","SHFLX","Q"/)
    ; ovar1 = (/"T1","LHFLX",""/)
    ; ovar2 = (/"T2","","Q2"/)

    ; var = (/"TS","SHFLX","WSPEED"/)
    ; ovar1 = (/"T1","LHFLX","","",""/)
    ; ovar2 = (/"T2","","","",""/)

    var = (/"SHFLX"/)
    ovar1 = (/"LHFLX","","",""/)
    ovar2 = (/"","","",""/)

    xlat =  -4
    xlon = 294

    ; xlat =  -2
    ; xlon = 288

    ; ne4 problem point
    ; xlat =  -7.5
    ; xlon = 300

    ; xlat = (/ -2,  0/)
    ; xlon = (/288,290/)

;===================================================================================
;===================================================================================
    num_x = dimsizes(xlat)
    num_c = dimsizes(case)
    num_v = dimsizes(var)

    wks = gsn_open_wks(fig_type,fig_file)
    ; plot = new(num_v,graphic)
    plot = new(num_v*num_x,graphic)
    ; plot = new(1,graphic)
        res = setres_xy()
        ; res@tiYAxisString               = "Height [km]"
        res@tmXBLabelFontHeightF        = 0.02
        res@tmYLLabelFontHeightF        = 0.02
        res@tiXAxisFontHeightF          = 0.025
        res@tiYAxisFontHeightF          = 0.025
        res@gsnLeftStringFontHeightF    = 0.025
        res@gsnRightStringFontHeightF   = 0.025
        ; res@gsnLeftString               = ""
        ; res@gsnRightString              = ""
        res@xyMarkLineMode              = "MarkLines"
        res@xyMarker                    = 16
        res@xyMarkerSizeF               = 0.01

        ; zero line
        lres = res
        lres@xyLineThicknessF       = 1.
        lres@xyDashPattern          = 0
        lres@xyLineColor            = "black"
;===================================================================================
;===================================================================================
; type = gsn_create_text(wks, var(0), False)
; print(type)

; test = new(1,list)

; test = type

; exit



txt_id = new(num_v,graphic)
ann_id = new(num_v,graphic)

c = 0
; do c = 0,num_c-1
do x = 0,num_x-1
    do v = 0,num_v-1


        files = systemfunc("ls -1 "+idir+case(c)+"/run/*h1*nc ")
        ; files = systemfunc("ls -1 "+idir+case(c)+"/run/*h1*remap.nc ")

        ifile = files(0)
        infile = addfile(ifile,"r")

        ; print(infile)
        ; exit
        ;------------------------------------------------------------------
        ;------------------------------------------------------------------
        time := infile->time
        lev  := infile->lev
        lat  := infile->lat
        lon  := infile->lon

        ; kmax = ind(lev.eq.max(lev))
        kmax = dimsizes(lev)-1

        dims := dimsizes(infile->$var(v)$)
        ndim := dimsizes(dims)
        
        ; if ndim.eq.2 then V := infile->$var(v)$({xlat},{xlon}) end if
        ; if ndim.eq.3 then V := infile->$var(v)$(:,{xlat},{xlon}) end if
        ; if ndim.eq.4 then V := infile->$var(v)$(:,kmax,{xlat},{xlon}) end if

        ; dlat = ind_nearest_coord(lat,xlat,0)
        ; dlon = ind_nearest_coord(lon,xlon,0)

        dlat := lat-xlat(x)
        dlon := lon-xlon(x)
        dist := sqrt(dlat^2.+dlon^2.)
        ncol := ind(dist.eq.min(dist))

        tlat = lat(ncol)
        tlon = lon(ncol)

        if ndim.eq.2 then V := infile->$var(v)$(:,ncol) end if
        if ndim.eq.3 then V := infile->$var(v)$(:,kmax,ncol) end if

        if var(v).eq."Q" then
            V = (/V*1e3/)
        end if

        if var(v).eq."PRECT" then
            V = (/ V * 86400. * 1e3 /)
            V@long_name = "Precipitation (mm/day)"
        end if
        ;------------------------------------------------------------------
        ; create plot
        ;------------------------------------------------------------------
        oflag = False
        ; ip = v
        ip = x*num_v + v

        tres := res
        tres@trXMaxF = max(time)
        ; tres@gsnRightString = var(v)
        fmt = "%4.1F"
        tres@gsnRightString = "lat / lon : "+sprintf(fmt,tlat)+" / "+sprintf(fmt,tlon)
        tres@xyLineColor = "black"

        if any(var(v).eq.(/"TS","T","T1","T2"/)) then
            tres@trYMinF = 290
            tres@trYMaxF = 310
        end if
        if any(var(v).eq.(/"Q","Q1","Q2"/)) then
            tres@trYMinF = 10
            tres@trYMaxF = 16
        end if
        if any(var(v).eq.(/"SHFLX","LHFLX"/)) then
            tres@trYMinF = -200
            tres@trYMaxF =  200;50
        end if

        ; if ovar(v).ne."" then
        ;     tres@gsnRightString = var(v)+" / "+ovar(v)
        ; end if

        tres@xyMarkerColor = tres@xyLineColor

        plot(ip) = gsn_csm_xy(wks,time,V,tres)

        ;------------------------------------------------------------------
        ; add text annotation
        ;------------------------------------------------------------------
            txres               = True
            txres@txJust        = "CenterLeft"
            txres@txFontColor   = tres@xyLineColor
            txres@txFontHeightF = 0.015  ; Use same font height as left axis
        txt_id(v) = gsn_create_text(wks, var(v), txres)
            amres                  = True
            amres@amParallelPosF   =  0.35
            amres@amOrthogonalPosF = -0.4
        ann_id(v) = gsn_add_annotation(plot(ip), txt_id(v), amres)

        ;------------------------------------------------------------------
        ; overlay variable if ovar is not blank
        ;------------------------------------------------------------------
        if ovar1(v).ne."" then

            tvar = ovar1(v)
            if tvar.eq."T1" then tvar = "T" end if
            if tvar.eq."Q1" then tvar = "Q" end if

            dims := dimsizes(infile->$tvar$)
            ndim := dimsizes(dims)
            if ndim.eq.2 then oV := infile->$tvar$(:,ncol) end if
            if ndim.eq.3 then oV := infile->$tvar$(:,kmax,ncol) end if
            
            tres@xyLineColor = "red"
            tres@xyMarkerColor = tres@xyLineColor

            overlay( plot(ip) , gsn_csm_xy(wks,time,oV,tres) )

                txres               = True
                txres@txFontColor   = tres@xyLineColor
            txt_id(v) = gsn_create_text(wks, ovar1(v), txres)
                amres                  = True
                amres@amParallelPosF   = amres@amParallelPosF
                amres@amOrthogonalPosF = amres@amOrthogonalPosF + txres@txFontHeightF * 3
            ann_id(v) = gsn_add_annotation(plot(ip), txt_id(v), amres)

        end if

        if ovar2(v).ne."" then

            tvar = ovar2(v)
            tk = kmax
            if ovar2(v).eq."T2" then tvar = "T" end if
            if ovar2(v).eq."Q2" then tvar = "Q" end if
            if ovar2(v).eq."T2" then tk = kmax-1 end if
            if ovar2(v).eq."Q2" then tk = kmax-1 end if

            dims := dimsizes(infile->$tvar$)
            ndim := dimsizes(dims)
            if ndim.eq.2 then oV := infile->$tvar$(:,ncol) end if
            if ndim.eq.3 then oV := infile->$tvar$(:,tk,ncol) end if
            
            tres@xyLineColor = "green"
            tres@xyMarkerColor = tres@xyLineColor

            if any(var(v).eq.(/"Q","Q2"/)) then
                oV = (/oV*1e3/)
            end if

            overlay( plot(ip) , gsn_csm_xy(wks,time,oV,tres) )

                txres               = True
                txres@txFontColor   = tres@xyLineColor
            txt_id(v) = gsn_create_text(wks, ovar2(v), txres)
                amres                  = True
                amres@amParallelPosF   = amres@amParallelPosF
                amres@amOrthogonalPosF = amres@amOrthogonalPosF + txres@txFontHeightF * 3
            ann_id(v) = gsn_add_annotation(plot(ip), txt_id(v), amres)

        end if

        ;------------------------------------------------------------------
        ;------------------------------------------------------------------
    end do
end do
;===================================================================================
;===================================================================================
        pres = setres_panel()
        ; pres = setres_panel_labeled()
        pres@gsnPanelXWhiteSpacePercent = 5
        pres@gsnPanelYWhiteSpacePercent = 5
        pres@gsnPanelBottom = 0.1
        ;pres@txString = season

    ; layout = (/1,dimsizes(plot)/)
    layout = (/num_x,num_v/)

    gsn_panel(wks,plot,layout,pres)


    trimPNG(fig_file)
;===================================================================================
;===================================================================================
end