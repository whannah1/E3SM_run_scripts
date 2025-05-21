load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$HOME/NCL/custom_functions_ACME.ncl"
begin

    dir = "/lustre/atlas1/cli115/scratch/hannah6/E3SM_SP1_CTL_ne30_64x1_4km_s1_99/run/"

    ; bin_min = (/ 0.0000, 0.0001, 0.0003 /)
    ; bin_max = (/ 0.0001, 0.0003, 0.0006 /)
    ; bin_name = (/"corner","edge","center"/)+" nodes"

    print("")
    print(""+dir)
    print("")

    fig_type = "png"
    fig_file = "~/E3SM/chk.corners.out"

;===================================================================================
;===================================================================================
    
    hist_files = systemfunc("ls "+dir+"*cam.h1*.nc ")

    hfile = addfile(hist_files(0),"r")


    area = hfile->area
    hlat = hfile->lat
    hlon = hfile->lon

    precip = hfile->PRECT

    precip = (/ precip*86400.*1e3 /)


    dump_files = systemfunc("ls "+dir+"glitter*.nc ")

    corner_cnt = 0
    center_cnt = 0

    ; do f = 0,dimsizes(dump_files)-1
    do f = 80,dimsizes(dump_files)-1
        fname = dump_files(f)
        infile = addfile(fname,"r")

        ; fname = str_sub_str(fname,dir,"")

        lat = infile@latitude0
        lon = infile@longitude0


        ; i = ind( (lat.eq.hlat).and.(lon.eq.hlon) ) 

        dlat = abs(lat-hlat)
        dlon = abs(lon-hlon)

        tolerance = 0.01

        i = ind( (dlat.lt.min(dlat)+tolerance) .and. (dlon.lt.min(dlon)+tolerance) ) 

        if area(i).gt.0.0000 .and. area(i).le.0.0001 then area_str = "corner" end if
        if area(i).gt.0.0001 .and. area(i).le.0.0003 then area_str = "edge"   end if
        if area(i).gt.0.0003 .and. area(i).le.0.0006 then area_str = "center" end if

        ; if area_str.eq."corner" then
        if area_str.eq."corner" .or. area_str.eq."center" then

            cnt_limit = 10

            if area_str.eq."corner".and.corner_cnt.ge.cnt_limit then continue end if
            if area_str.eq."center".and.center_cnt.ge.cnt_limit then continue end if

            str =  strpad(f               , 5) +"  " \
                  +strpad(fname           ,40) +"  " \
                  +strpad(lat             ,20) +"  " \
                  +strpad(lon             ,20) +"  " \
                  +strpad(area_str        ,10) +"  " \
                  +strpad(avg(precip(:,i)),10) +"  " \
                  +strpad(max(precip(:,i)),10) +"  " \
                  +""
            
            ; if avg(precip(:,i)).gt.1 then 

                print(""+str)
                
                ; X = infile->qcl + infile->qpl + infile->qci + infile->qpi
                ; copy_VarMeta(infile->qcl,X)

                dims := dimsizes(infile->t)
                X := infile->t(:,:,:,4:dims(3)-1-4)
                X = (/ X - conform(X,X(0,:,:,:),(/1,2,3/)) /)
                
                X!0 = "time"
                X!1 = "z"
                X!2 = "y"
                X!3 = "x"

                crm_dt = 5
                time = ispan(1,dims(0),1) *crm_dt / tofloat(30*60)
                X&time = time

                tX := dim_avg_n_Wrap( X(z|:,time|:,y|0,x|:) ,2)

                if area_str.eq."corner"
                    if corner_cnt.eq.0 then X_corner_avg = tX else X_corner_avg = (/ ( X_corner_avg*corner_cnt + tX ) / tofloat((corner_cnt+1)) /) end if
                    corner_cnt = corner_cnt+1
                end if

                if area_str.eq."center"
                    if center_cnt.eq.0 then X_center_avg = tX else X_center_avg = (/ ( X_center_avg*center_cnt + tX ) / tofloat((center_cnt+1)) /) end if
                    center_cnt = center_cnt+1
                end if

                ; if corner_cnt.gt.0 then break end if

                if (corner_cnt.ge.cnt_limit) .and. (center_cnt.ge.cnt_limit) then break end if

            ; end if

        end if

    end do

print("")
print("  corner_cnt: "+corner_cnt)
print("")


printMAM(X_corner_avg)
printMAM(X_center_avg)

;===================================================================================
;===================================================================================
    
    wks = gsn_open_wks(fig_type,fig_file)
    plot = new(2,graphic)

    res = setres_contour_fill()
    res@vpHeightF       = 0.4
    ; res@lbLabelBarOn    = False
    res@cnLineLabelsOn  = False
    res@cnInfoLabelOn   = False
    ; res@tmXBLabelFontHeightF        = 0.02
    ; res@tmYLLabelFontHeightF        = 0.02
    ; res@gsnLeftStringFontHeightF    = 0.025
    ; res@gsnCenterStringFontHeightF  = 0.025
    ; res@gsnRightStringFontHeightF   = 0.025
    ; res@trYReverse      = True
    ; dlb = 0.3     ; shift labels down to make room for X-axis label
    ; res@lbTopMarginF    = 0.05 + dlb
    ; res@lbBottomMarginF = 0.05 - dlb ;+ 0.1
    res@tiYAxisString   = "[hPa]"
    ; res@tmYLMode        = "Explicit"
    ; res@tmYLValues      = ispan(0,1000,200)
    ; res@tmYLLabels      = ispan(0,1000,200)
    ; res@tmYLPrecision   = 0
    ; res@gsnYAxisIrregular2Linear   = True
    res@lbTitlePosition    = "Bottom"
    res@lbTitleFontHeightF = 0.015 

    res@cnFillMode = "CellFill"

;===================================================================================
;===================================================================================
    
    dims := dimsizes(X_corner_avg)

    t1 = 0
    t2 = dims(1)/2

    plot(0) = gsn_csm_contour(wks,X_corner_avg(:,t1:t2),res)
    plot(1) = gsn_csm_contour(wks,X_center_avg(:,t1:t2),res)

;===================================================================================
;===================================================================================
    pres = setres_panel()
    ; if num_c.gt.1 then pres = setres_panel_labeled() end if
    pres@gsnPanelYWhiteSpacePercent = 5
    pres@gsnPanelBottom = 0.1

    ; layout = (/num_v,num_c/)
    layout = (/dimsizes(plot),1/)

    gsn_panel(wks,plot,layout,pres)
    trimPNG(fig_file)


;===================================================================================
;===================================================================================
end