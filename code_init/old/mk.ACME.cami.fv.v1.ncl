; Walter Hannah - 2017 - Lawrence Livermore National Lab
; Create a modified initialization file (cami) for the ACME model
; Adds more vertical levels to the standard 30 level setup
; v1 - interpolate levels from previous file - can't change model top
; v2 - regrid SE file for higher model top
; Titan directory :
; /lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/inic/fv/
load "$NCARG_ROOT/custom_functions.ncl"
begin

    ; dir = "~/ACME/IC_CESM/"       ; for input and output
    dir = "/lustre/atlas1/cli115/scratch/hannah6/init_files/" ; for input and output

    onlevm = 72     ; # output midpoint levels

    ; afile = "cami_1987-01-01_0.9x1.25_L26_c060703.nc"               ; for F compset
    afile = "cami-mam3_0000-01-01_1.9x2.5_L30_c090306.nc"
    ifile = dir+afile

    debug  = True      ; debug modes does not write output file
    mkplot = False      ; switch for diagnostic plot

    fig_type = "x11"

    loglin = 0     ; 1 = linear , 0 = log


    ; specify SE file for vertical levels
    ; zfile = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/inic/homme/cami_mam3_Linoz_ne16np4_L72_c160614.nc"
    ; zfile = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/inic/homme/cami_mam3_Linoz_ne30np4_L72_c160214.nc"
;===========================================================================
;===========================================================================
    ; use this when starting with nlev=26 (CAM4)
    
    ver = 1

    ;p1 = 150    ; upper boundary of mid-point interpolation
    ;p2 = 825    ; lower boundary of mid-point interpolation

    ; ofile = dir+"cami_F_0000-01-01_0.9x1.25_L"+onlevm+".v"+ver+".nc"
    ofile = dir+"cami_F_0000-01-01_01_1.9x2.5_L"+onlevm+".v"+ver+".nc"

    fig_file = dir+"new_levels.nlevm_"+onlevm+".v"+ver

    if debug then fig_type = "x11" end if

    infile  = addfile(ifile,"r")
    var = getfilevarnames(infile)
    ;if debug then var := (/"T"/) end if
    nvar = dimsizes(var)

    onlevi = onlevm+1

;===========================================================================
; Load input level set
;===========================================================================
    hyai = infile->hyai
    hyam = infile->hyam
    hybi = infile->hybi
    hybm = infile->hybm

    lev = infile->lev
    po = 1e3

    levm = hyam*po + hybm*1000.
    levi = hyai*po + hybi*1000.

    nlevm = dimsizes(levm)
    nlevi = dimsizes(levi)

    etam = hyam + hybm
    etai = hyai + hybi

    dlevm = levi(1:nlevi-1) - levi(0:nlevi-2)
    detam = etai(1:nlevi-1) - etai(0:nlevi-2)

    dlev = levi(1:nlevi-1) - levi(0:nlevi-2)

    levm!0 = "levm"
    levm&levm = levm
    copy_VarCoords(levm,etam)

    levi!0 = "levi"
    levi&levi = levi
    copy_VarCoords(levi,etai)
;===========================================================================
; create new set of levels
;===========================================================================
    new_levm = new(onlevm,double)
    new_levi = new(onlevi,double)
    new_etam = new(onlevm,double)
    new_etai = new(onlevi,double)
    new_hyam = new(onlevm,double)
    new_hyai = new(onlevi,double)
    new_hybm = new(onlevm,double)
    new_hybi = new(onlevi,double)
    ;------------------------------------------------
    ; add levels above p1
    ;------------------------------------------------
    tmp := etam({:p1})
    tn1 = dimsizes(tmp) - 1
    new_etam(:tn1) = tmp
    new_etai(:tn1) = etai(:tn1)
    new_hyam(:tn1) = hyam({:p1})
    new_hybm(:tn1) = hybm({:p1})
    ;------------------------------------------------
    ; add levels below p2
    ;------------------------------------------------
    tmp := etam({p2:})
    tn2 = onlevm - 0 - dimsizes(tmp)
    new_etam(tn2:) = tmp
    new_etai(tn2:) = etai(nlevi-(onlevi-tn2):)
    new_hyam(tn2:) = hyam({p2:})
    new_hybm(tn2:) = hybm({p2:})
    ;------------------------------------------------
    ; Create new levels in between p1 and p2
    ;------------------------------------------------
    tn3 = tn2 - tn1 
    ;new_etai(tn1:tn2) = fspan( etai({p1}), etai({p2}), tn3 )
    new_etam(tn1:tn2-1) = fspan( etam({p1}), etam({p2}), tn3 )
    ;------------------------------------------------
    ; calculate new interface eta values
    ;------------------------------------------------
    ;new_etam = ( new_etai(1:onlevi-1) + new_etai(0:onlevi-2) )/2.
    ;new_etai(1:onlevi-2) = ( new_etam(1:onlevm-1) + new_etam(0:onlevm-2) )/2.
    new_etai(tn1+1:tn2) = ( new_etam(tn1+1-1:tn2-1) + new_etam(tn1+1:tn2) )/2.
    new_etai(0) = etai(0)
    new_etai(onlevi-1) = etai(nlevi-1)
    ;------------------------------------------------
    ; diagnose idealized pressure values
    ;------------------------------------------------
    new_levm = new_etam*1000
    new_levi = new_etai*1000
    ;new_levm = new_hyam*po + new_hybm*1000
    ;new_levi = new_hyai*po + new_hybi*1000
    ;------------------------------------------------
    ; diagnose new A and B coefficient values
    ;------------------------------------------------
    ma = ( hyam({p2})-hyam({p1}) ) / ( levm({p2}) - levm({p1}) )
    mb = ( hybm({p2})-hybm({p1}) ) / ( levm({p2}) - levm({p1}) )

    ao = hyam({p1}) - ma*levm({p1})
    bo = hybm({p1}) - mb*levm({p1}) 
    
    new_hyam(tn1:tn2-1) = ma*new_levm(tn1:tn2-1) + ao
    new_hybm(tn1:tn2-1) = mb*new_levm(tn1:tn2-1) + bo
    
    new_hyai(:tn1) = hyai(:tn1)
    new_hybi(:tn1) = hybi(:tn1)
    new_hyai(tn2:) = hyai(nlevi-(onlevi-tn2):)
    new_hybi(tn2:) = hybi(nlevi-(onlevi-tn2):)
    new_hyai(tn1+1:tn2-1) = ( new_hyam(tn1+1:tn2-1) + new_hyam(tn1:tn2-2) )/2.
    new_hybi(tn1+1:tn2-1) = ( new_hybm(tn1+1:tn2-1) + new_hybm(tn1:tn2-2) )/2.
    ;new_hyai(tn1+1:tn2-1) = ( new_hyam(tn1+1:tn2-1) * new_hyam(tn1:tn2-2) )^.5
    ;new_hybi(tn1+1:tn2-1) = ( new_hybm(tn1+1:tn2-1) * new_hybm(tn1:tn2-2) )^.5

    ;new_hyai(1:onlevi-2) = ( new_hyam(1:onlevm-1) + new_hyam(0:onlevm-2) )/2.
    ;new_hybi(1:onlevi-2) = ( new_hybm(1:onlevm-1) + new_hybm(0:onlevm-2) )/2.
    
    new_hyai(0) = hyai(0)
    new_hybi(0) = hybi(0)
    new_hyai(onlevi-1) = hyai(nlevi-1)
    new_hybi(onlevi-1) = hybi(nlevi-1)
    ;------------------------------------------------
    ; calculate new layer thickness
    ;------------------------------------------------
    new_dlevm = new_levi(1:onlevi-1) - new_levi(0:onlevi-2)
    new_detam = new_etai(1:onlevi-1) - new_etai(0:onlevi-2)
    ;------------------------------------------------
    ;------------------------------------------------
    new_levm!0 = "lev"
    new_levi!0 = "ilev"
    new_levm&lev  = new_levm
    new_levi&ilev = new_levi
    copy_VarCoords(new_levm,new_hyam)
    copy_VarCoords(new_levm,new_hybm)

    copy_VarCoords(new_levi,new_hyai)
    copy_VarCoords(new_levi,new_hybi)

    new_dlev = new_levi(1:onlevi-1) - new_levi(0:onlevi-2)
;===========================================================================
;===========================================================================
    printline()
    fmt1 = "%12.8F"
    fmt2 = "%12.8F"
    print(  sprintf(fmt1,levm)+"  "+\
            sprintf(fmt2,etam)+"  "+\
            sprintf(fmt1,levi(:nlevm-1))+"  "+\
            sprintf(fmt2,etai(:nlevm-1))+"  "+\
            sprintf(fmt2,hyai(:nlevm-1))+"  "+\
            sprintf(fmt2,hybi(:nlevm-1)) )
    printline()
    print(  sprintf(fmt1,new_levm)+"  "+\
            sprintf(fmt2,new_etam)+"  "+\
            sprintf(fmt1,new_levi(:onlevm-1))+"  "+\
            sprintf(fmt2,new_etai(:onlevm-1))+"  "+\
            sprintf(fmt2,new_hyai(:onlevm-1))+"  "+\
            sprintf(fmt2,new_hybi(:onlevm-1)) )
    printline()
;===========================================================================
;===========================================================================
if mkplot then 
    wks = gsn_open_wks(fig_type,fig_file)
    plot = new(4,graphic)
        res = setres_default()
        res@xyMarkLineMode    = "MarkLines"
        res@xyMarker          = 16
        res@xyMarkerSizeF     = 0.015
        res@xyLineThicknessF  = 4.
        res@gsnLeftString     = nlevm+" vs "+onlevm+" levels"
    ;----------------------------------------
    ;----------------------------------------
        res@gsnRightString    = "Mid-point levels"
        res@tiYAxisString     = "eta (hya+hyb)"
        res@tiXAxisString     = "Pressure [hPa]"
    ;plot(0) = gsn_csm_xy(wks,levi,etai,res)
    plot(0) = gsn_csm_xy(wks,levm,(/etam,hyam,hybm/),res)
        res@gsnRightString    = "Interface levels"
    plot(1) = gsn_csm_xy(wks,levi,(/etai,hyai,hybi/),res)
        res@tiXAxisString     = "Normalized Coordinate []"
    plot(2) = gsn_csm_xy(wks,fspan(0,1,nlevi),etai,res)
        res@gsnRightString    = "Layer thickness"
        res@tiYAxisString     = "dP [hPa]"
    plot(3) = gsn_csm_xy(wks,levm,dlevm,res)
        res@gsnRightString    = ""
        res@gsnLeftString     = ""

        res@xyMarkerSizeF     = 0.007
        res@xyMarkerColor = "red"
    overlay(plot(0),gsn_csm_xy(wks,new_levm,(/new_etam,new_hyam,new_hybm/),res))
    overlay(plot(1),gsn_csm_xy(wks,new_levi,(/new_etai,new_hyai,new_hybi/),res))
        res@xyLineColor = "red"
    overlay(plot(2),gsn_csm_xy(wks,fspan(0,1,onlevi),new_etai,res))
    overlay(plot(3),gsn_csm_xy(wks,new_levm,new_dlevm,res))
    ;----------------------------------------
    ; add lines showing area of interpolation
    ;----------------------------------------
        res := setres_default()
        res@xyDashPattern = 1
        res@xyLineThicknessF  = 1.
    overlay(plot(0),gsn_csm_xy(wks,(/1,1/)*p1,(/-1e3,1e3/),res))
    overlay(plot(0),gsn_csm_xy(wks,(/1,1/)*p2,(/-1e3,1e3/),res))
    overlay(plot(1),gsn_csm_xy(wks,(/1,1/)*p1,(/-1e3,1e3/),res))
    overlay(plot(1),gsn_csm_xy(wks,(/1,1/)*p2,(/-1e3,1e3/),res))
    overlay(plot(3),gsn_csm_xy(wks,(/1,1/)*p1,(/-1e3,1e3/),res))
    overlay(plot(3),gsn_csm_xy(wks,(/1,1/)*p2,(/-1e3,1e3/),res))

    tp = 600
    res@xyDashPattern = 2
    overlay(plot(0),gsn_csm_xy(wks,(/1,1/)*tp,(/-1e3,1e3/),res))
    overlay(plot(1),gsn_csm_xy(wks,(/1,1/)*tp,(/-1e3,1e3/),res))
    overlay(plot(3),gsn_csm_xy(wks,(/1,1/)*tp,(/-1e3,1e3/),res))
    ;----------------------------------------
    ; finalize plot
    ;----------------------------------------
    ;gsn_panel(wks,plot,(/1,dimsizes(plot)/),setres_panel())
    gsn_panel(wks,plot,(/2,2/),setres_panel())
    trimPNG(fig_file)
    if debug then exit end if
end if
printline()
;===========================================================================
; Create new cam.i file with new levels
;===========================================================================
if .not.debug then 
    if isfilepresent(ofile) then system("rm "+ofile) end if
    outfile = addfile(ofile,"c")
end if
do v = 0,nvar-1
    ;---------------------------------------------
    ; Load variable
    ;---------------------------------------------
    V = infile->$var(v)$
    dims := getfilevardims(infile,var(v))
    if isatt(V,"long_name") then 
        var_name = infile->$var(v)$@long_name 
    else
        var_name = ""
    end if
    print("  "+strpad(var(v),20) + "    " + var_name)
    if debug then iV = V end if
    ;---------------------------------------------
    ; interpolate if necessary
    ;---------------------------------------------
    if any(dims.eq."lev").or.any(dims.eq."ilev") then
        if iscoord(V,"lev") then
            kdim = ind(dims.eq."lev")
            ;V = (/ V * conform(V,dlev,kdim) /)
            ;V := linint1_n_Wrap(infile->lev,V,False,new_levm,0,kdim)
            V := int2p_n_Wrap(infile->lev,V,new_levm,loglin,kdim)
            ;V = (/ V / conform(V,new_dlev,kdim) /)
            V!kdim = "lev"
        end if
        if iscoord(V,"ilev") then
            kdim = ind(dims.eq."ilev")
            ;V := linint1_n_Wrap(infile->ilev,V,False,new_levi,0,kdim)
            V := int2p_n_Wrap(infile->ilev,V,new_levi,loglin,kdim)
            V!kdim = "ilev"
        end if
    end if
    ;---------------------------------------------
    ; create plot to see how interpolation is working
    ;---------------------------------------------
    ;if debug then
    if False then
        print("before interpolation : ") 
        print(""+dim_collapse(iV,1))
        printline()
        print("after interpolation : ") 
        print(""+dim_collapse(V,1))
        wks = gsn_open_wks("x11","debug")
            res = setres_default()
            res@xyLineColor     = "black"
            res@xyMarkLineMode  = "Markers"
            res@xyMarker        = 16
            res@xyMarkerSizeF   = 0.01
        ;plot := gsn_csm_xy(wks,levm,dim_collapse(iV,1),res)
        plot := gsn_csm_xy(wks,new_levm,dim_collapse(V,1),res)
            res@xyMarkerColor   = "red"
            res@xyMarkerSizeF   = 0.008
        overlay(plot , gsn_csm_xy(wks,new_levm,dim_collapse(V,1),res))
        draw(plot)
        frame(wks)
    end if
    ;---------------------------------------------
    ;---------------------------------------------
    if var(v) .eq. "nbdate" then V = 20000101 end if
    if var(v) .eq. "ndcur"  then V = 000 end if
    if var(v) .eq. "date"   then V = 20000101 end if
    if var(v) .eq. "hyam"   then V := new_hyam end if
    if var(v) .eq. "hyai"   then V := new_hyai end if
    if var(v) .eq. "hybm"   then V := new_hybm end if
    if var(v) .eq. "hybi"   then V := new_hybi end if
    if var(v) .eq. "lev"    then V := new_levm end if
    if var(v) .eq. "ilev"   then V := new_levi end if

    if.not.debug then outfile->$var(v)$ = V end if
    delete(V)
    ;---------------------------------------------
    ;---------------------------------------------
end do

if.not.debug then 
    ;print(getvaratts(infile))
    copy_VarAtts(infile,outfile)
    outfile@intermediate_file = afile
    outfile@interp_p1 = p1
    outfile@interp_p2 = p2
    outfile@title = str_sub_str(outfile@title,"-nlev "+nlevm,"-nlev "+onlevm)
end if
printline()
;===========================================================================
;===========================================================================
    print("")
    print("  input  : "+ifile)
    print("  output : "+ofile)
    if mkplot.and.(fig_type.eq."png") then print("  figure : "+fig_file) end if
    print("")

;===========================================================================
;===========================================================================

end