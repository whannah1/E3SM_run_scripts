; parses the model timing output files to create plots 
; of timing data across an ensemble of ACME runs
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/custom_functions.ncl"

undef("str_to_flt")
function str_to_flt (str)
local tmp,flt
begin
    tmp = str_split(str," ")
    flt = tofloat(tmp(ind(is_string_numeric(tmp))))
    return flt
end

begin

    ; idir = "/lustre/atlas1/cli115/scratch/hannah6/"
    idir = "~/ACME/Cases/"

    grd = "ne30_d"
    ; grd = "1.9x2.5"
    ; cld = "SP2"
    fac = 1
    cnx = 64
    cny = 1

    ; grd = "ne30"+(/"_d","_p"/)
    ; grd = (/"ne16_d","ne16_p","ne30_d","ne30_p"/)
    ; grd = (/"ne16_p","ne30_p"/)
    cld = (/"ZM","SP1","SP2"/)
    ; fac = (/1,4/)

    ; cnx = (/64,16,8/)
    ; cny = (/ 1, 4,8/)

    ; npr = (/64,128,256,512,1024/)

    

    fig_type = "png"
    fig_file = "~/ACME/figs_timing/timing.v1"

    ; case = "ACME_timing_ne16_SP2_128"

    ver = "2"

;===================================================================================
;===================================================================================
    num_grd = dimsizes(grd)
    num_cld = dimsizes(cld)
    num_fac = dimsizes(fac)

    num_cnx = dimsizes(cnx)

;===================================================================================
;===================================================================================
    max_num_npr = 12

    xdim = (/num_grd,num_cld,num_fac,num_cnx,max_num_npr/)

    npr  = new(xdim,float)
    npr2 = new(xdim,float)

    total_cost = new(xdim,float)    ; Model cost - pe-hrs/sim_yr
    total_ypdy = new(xdim,float)    ; throughput - sim_yr/day

    total_phys1 = new(xdim,float)    ; physics
    total_phys2 = new(xdim,float)    ; physics

    annoid1    = new(xdim,graphic)  ; used for overlaying lines on plot
    annoid2    = new(xdim,graphic)  ; used for overlaying lines on plot
    
    pdim = (/num_grd,num_cld,num_fac,num_cnx/)  

    name = new(pdim,string)         ; sim name for legend
    clr  = new(pdim,string)         ; color for legend
    dsh  = new(pdim,integer)        ; dash pattern for legend
    mrk  = new(pdim,integer)        ; marker index for legend

    first = True

    g := 0
    do g = 0,num_grd-1
    do c = 0,num_cld-1
    do f = 0,num_fac-1
    do x = 0,num_cnx-1

        if fac(f).eq.1 then 
            if grd(g).eq."1.9x2.5" then tnpr := (/256/) end if
            ; if grd(g).eq."ne4"  then tnpr := (/  96,  192,  384, 768, 1536/) end if
            ; if grd(g).eq."ne16" then tnpr := (/1729, 3457, 6144, 13826/) end if
            if grd(g).eq."ne16" then tnpr := (/865, 1536, 1729, 3072, 3457, 6144, 6913, 12288, 13826/) end if
            ; if grd(g).eq."ne30" then tnpr := (/5400,10800,21600/) end if
            if grd(g).eq."ne30" then tnpr := (/2700, 3038, 5400, 6076, 10800, 12151, 21600, 24301, 43200, 48602/) end if


            if grd(g).eq."ne16_p" then tnpr := (/865, 1729, 3457, 6913, 13826/) end if
            if grd(g).eq."ne16_d" then tnpr := (/1536, 3072, 6144, 12288/) end if

            if grd(g).eq."ne30_d" then tnpr := (/2700, 5400, 10800, 21600, 43200/) end if
            if grd(g).eq."ne30_p" then tnpr := (/3038, 6076,12151,24301,48602/) end if

        end if

        ; if fac(f).eq.4 then 
            ; if grd(g).eq."ne4"  then tnpr := (/  48,  96, 192, 384/) end if
            ; if grd(g).eq."ne16" then tnpr := (/ 384, 768,1536, 3072, 6144/) end if
            ; if grd(g).eq."ne16" then tnpr := (/1536, 3072, 6144/) end if
            ; if grd(g).eq."ne30" then tnpr := (/1350,2700,5400,10800/) end if
        ; end if

        num_npr  = dimsizes(tnpr )
        ; num_npr2 = dimsizes(tnpr2)

        npr (g,c,f,x,:num_npr-1) = tnpr

        ; npr2(g,c,f,x,:num_npr-1) = tnpr2


        do n = 0,num_npr-1

            tgrd = grd(g)
            if isStrSubset(grd(g),"_p") then tgrd = str_sub_str(tgrd,"_p","") end if
            if isStrSubset(grd(g),"_d") then tgrd = str_sub_str(tgrd,"_d","") end if

            ; if (cnx(x).eq.32 .and. cny(x).eq.1).or.cld(c).eq."ZM" then
            if cld(c).eq."ZM" then
                case = "ACME_timing"+ver+"_"+tgrd+"_"+cld(c)+"_f"+fac(f)+"_"+npr(g,c,f,x,n)
            else
                case = "ACME_timing"+ver+"_"+tgrd+"_"+cnx(x)+"x"+cny(x)+"_"+cld(c)+"_f"+fac(f)+"_"+npr(g,c,f,x,n)
            end if

            name(g,c,f,x) = grd(g) + "_"+cld(c) 

            if num_fac.gt.1 then name(g,c,f,x) = name(g,c,f,x) + "_f"+fac(f) end if

            if num_cnx.gt.1 then name(g,c,f,x) = name(g,c,f,x) + "_"+cnx(x)+"x"+cny(x) end if

            ; case = "ACME_SP2_CTL_ne4_31"

            if fileexists(idir+case+"/timing") then
                ;--------------------------------------------------------
                ; find the names of the available timing files
                ;--------------------------------------------------------

                files_1 := systemfunc("ls -1t "+idir+case+"/timing/acme_timing."+case+"*")
                files_2 := systemfunc("ls -1t "+idir+case+"/timing/acme_timing_stats.*")
; print(""+files_1)

                file1 = files_1(0)
                file2 = files_2(0)

                ;--------------------------------------------------------
                ; unzip the timing stats file
                ;--------------------------------------------------------
                if isStrSubset(file2,".gz") then
                    ; print("Uzipping file2 : "+file2)
                    system("gunzip "+file2)
                    file2 = str_sub_str(file2,".gz","")
                end if
                ;--------------------------------------------------------
                ; load and parse the data
                ;--------------------------------------------------------
                if fileexists(file1) then

                    data1 := asciiread(file1,-1,"string")
                    data2 := asciiread(file2,-1,"string")

                    ; print(data)

                    do i = 0,dimsizes(data1)-1
                        if isStrSubset(data1(i),"Model Cost:      ") then total_cost(g,c,f,x,n) = str_to_flt(data1(i)) end if
                        if isStrSubset(data1(i),"Model Throughput:") then total_ypdy(g,c,f,x,n) = str_to_flt(data1(i)) end if
                    end do


                    do i = 0,dimsizes(data2)-1
                        ; if isStrSubset(data2(i),"phys_run1") then
                        ;     print( data2(i) )
                        ;     print( str_to_flt(data2(i)) )
                        ;     exit
                        ; end if

                        ; use 3 for "walltotal"
                        ; use 4 for "wallmax"
                        di = 3

                        if isStrSubset(data2(i),"phys_run1") then 
                            tmp := str_to_flt(data2(i))
                            total_phys1(g,c,f,x,n) = tmp(di) 
                        end if
                        ; if isStrSubset(data2(i),"phys_run2") then 
                        if isStrSubset(data2(i),"moist_convection") then 
                            tmp := str_to_flt(data2(i))
                            total_phys2(g,c,f,x,n) = tmp(di) 
                        end if
                    end do

                end if
            end if

            
            ;--------------------------------------------------------
            ;--------------------------------------------------------
            
            if n.eq.0 then print("") end if

            fmt = "%10.2f"
            if first then
                print( strpad("",35) +"    "+ strpad("yr / day",12) +"    "+ strpad("total_cost",12) \
                                     +"    "+ strpad("phys_run1",12)  +"    "+ strpad("phys_run2",12) )
                first = False
            end if

            if ismissing(total_cost(g,c,f,x,n)) then
                print( strpad(case,36) +"    "+strpad("missing",12))
            else
                ; print( strpad(case,30) +"    "+ sprintf(fmt,total_cost(g,c,f,x,n)) +"    "+ sprintf(fmt,total_ypdy(g,c,f,x,n)) )
                print( strpad(case,35) +"    "+ sprintf(fmt,total_ypdy (g,c,f,x,n)) +"    "+ sprintf(fmt,total_cost (g,c,f,x,n)) \
                                       +"    "+ sprintf(fmt,total_phys1(g,c,f,x,n)) +"    "+ sprintf(fmt,total_phys2(g,c,f,x,n)) )
            end if

            ; print(total_cost)
            ; print(total_ypdy)
            ; exit
            
            ;--------------------------------------------------------
            ;--------------------------------------------------------
        end do
    end do
    end do
    end do
    end do
;===================================================================================
;===================================================================================

    wks = gsn_open_wks(fig_type,fig_file)
    plot = new(1,graphic)
    np = dimsizes(plot)
        ; res = setres_xy()
        res = True
        res@gsnDraw  = False
        res@gsnFrame = False
        if np.ge.2 then
            res@tmXBLabelFontHeightF        = 0.02
            res@tmYLLabelFontHeightF        = 0.02
            res@tiXAxisFontHeightF          = 0.025
            res@tiYAxisFontHeightF          = 0.025
        end if
        ; res@gsnLeftStringFontHeightF    = 0.025
        ; res@gsnRightStringFontHeightF   = 0.025
        ; res@gsnLeftString               = ""
        ; res@gsnRightString              = ""
        ; res@tiYAxisString               = ""
        ; res@tmGridDrawOrder   = "PreDraw"
        res@tmXMajorGrid      = True
        res@tmYMajorGrid      = True
        res@tmXMinorGrid      = True
        res@tmYMinorGrid      = True
        res@tmXMajorGridThicknessF = 4
        res@tmYMajorGridThicknessF = 4
        res@tmXMajorGridLineColor = "gray"
        res@tmYMajorGridLineColor = "gray"
        res@tmXMinorGridLineColor = "gray"
        res@tmYMinorGridLineColor = "gray"
        res@tmXBMinorPerMajor = 8
        res@tmYLMinorPerMajor = 8
        res@xyLineColor = "white"
        res@tiXAxisString = "Np"

        res@trXMinF = 300 
        ; res@trXMinF = min(npr)/2
        res@trXMaxF = max(npr) * 2

        res@xyXStyle          = "Log"
        res@xyYStyle          = "Log"
        

        res1 = res
        res2 = res

        ; res1@trYMinF = 0.01 ;0.01
        ; res1@trYMaxF = 10
        res1@trYMinF = min(total_ypdy)/2
        res1@trYMaxF = max(total_ypdy)*4

        ; res1@trYMinF = 0.001
        ; res1@trYMaxF = 10
        ; res2@trYMinF = min(total_cost)/2
        ; res2@trYMaxF = max(total_cost)*2

        res1@tiYAxisString = "Sim Yr / Day"
        res2@tiYAxisString = "Core Hr / Sim Yr" ; "pe-hrs / sim year"
        

        ; set defaults for individual lines to be overlaid
        lres1 = res1
        lres2 = res2

        lres1@tmXMajorGrid      = False
        lres1@tmYMajorGrid      = False
        lres1@tmXMinorGrid      = False
        lres1@tmYMinorGrid      = False

        lres1@xyLineThicknessF  = 6
        lres1@xyLineColor       = "black"
        lres1@xyDashPattern     = 0

        lres1@xyMarkLineMode    = "MarkLines"
        lres1@xyMarker          = 16
        lres1@xyMarkerSizeF     = 0.01

        lres2@tmXMajorGrid      = lres1@tmXMajorGrid
        lres2@tmYMajorGrid      = lres1@tmYMajorGrid
        lres2@tmXMinorGrid      = lres1@tmXMinorGrid
        lres2@tmYMinorGrid      = lres1@tmYMinorGrid
        lres2@xyLineThicknessF  = lres1@xyLineThicknessF
        lres2@xyLineColor       = lres1@xyLineColor
        lres2@xyDashPattern     = lres1@xyDashPattern
        lres2@xyMarkLineMode    = lres1@xyMarkLineMode
        lres2@xyMarker          = lres1@xyMarker
        lres2@xyMarkerSizeF     = lres1@xyMarkerSizeF

        ores2 = res2
        ores2@xyMarkLineMode    = "Lines"
        ores2@xyDashPattern     = 1


    ;--------------------------------------------------------
    ; plot the timing data
    ;--------------------------------------------------------
    first = True

    do g = 0,num_grd-1
    do c = 0,num_cld-1
    do f = 0,num_fac-1
    do x = 0,num_cnx-1
    ; do n = 0,num_npr-1

        tres1 := lres1
        tres2 := lres2
        ; if fac(f).eq."1"  then tres1@xyMarker = 4 end if
        ; if fac(f).eq."4"  then tres1@xyMarker = 16 end if
        ; if cld(c).eq."SP1"  then tres1@xyDashPattern = 0 end if
        ; if cld(c).eq."SP2"  then tres1@xyDashPattern = 1 end if
        ; if grd(g).eq."ne4"  then tres1@xyLineColor = "red"   end if
        ; if grd(g).eq."ne16" then tres1@xyLineColor = "blue"  end if
        ; if grd(g).eq."ne30" then tres1@xyLineColor = "green" end if

        ; if cld(c).eq."ZM"  then tres1@xyLineColor = "blue"  end if
        ; if cld(c).eq."SP1" then tres1@xyLineColor = "green" end if
        ; if cld(c).eq."SP2" then tres1@xyLineColor = "red" end if

        if cld(c).eq."ZM" .and.isStrSubset(grd(g),"ne16") then tres1@xyLineColor = "blue"  end if
        if cld(c).eq."SP1".and.isStrSubset(grd(g),"ne16") then tres1@xyLineColor = "green" end if
        if cld(c).eq."SP2".and.isStrSubset(grd(g),"ne16") then tres1@xyLineColor = "red" end if
        if cld(c).eq."ZM" .and.isStrSubset(grd(g),"ne30") then tres1@xyLineColor = "cyan"  end if
        if cld(c).eq."SP1".and.isStrSubset(grd(g),"ne30") then tres1@xyLineColor = "darkolivegreen1" end if
        if cld(c).eq."SP2".and.isStrSubset(grd(g),"ne30") then tres1@xyLineColor = "magenta" end if

        ; clr := new((/6,3/),integer)
        ; clr(0,:) = (/000,000,255/)
        ; clr(1,:) = (/000,255,000/)
        ; clr(2,:) = (/255,000,000/)
        ; clr(3,:) = (/000,000,200/)
        ; clr(4,:) = (/000,200,000/)
        ; clr(5,:) = (/200,000,000/)

        ; if cld(c).eq."ZM" .and.isStrSubset(grd(g),"ne16") then tres1@xyLineColor := clr(0,:) end if
        ; if cld(c).eq."SP1".and.isStrSubset(grd(g),"ne16") then tres1@xyLineColor := clr(1,:) end if
        ; if cld(c).eq."SP2".and.isStrSubset(grd(g),"ne16") then tres1@xyLineColor := clr(2,:) end if
        ; if cld(c).eq."ZM" .and.isStrSubset(grd(g),"ne30") then tres1@xyLineColor := clr(3,:) end if
        ; if cld(c).eq."SP1".and.isStrSubset(grd(g),"ne30") then tres1@xyLineColor := clr(4,:) end if
        ; if cld(c).eq."SP2".and.isStrSubset(grd(g),"ne30") then tres1@xyLineColor := clr(5,:) end if



        ; if grd(g).eq."ne16" then tres1@xyLineColor = "cyan"  end if
        ; if grd(g).eq."ne30" then tres1@xyLineColor = "magenta" end if

        ; if fac(f).eq."1"  then tres1@xyLineColor = "cyan" end if
        ; if fac(f).eq."4"  then tres1@xyLineColor = "magenta" end if

        ; if cnx(x).eq.64  then tres1@xyDashPattern = 0 end if
        ; if cnx(x).eq.16  then tres1@xyDashPattern = 1 end if
        ; if cnx(x).eq. 8  then tres1@xyDashPattern = 2 end if

        if isStrSubset(grd(g),"_p") then 
            tres1@xyDashPattern = 0 
            tres1@xyMarker = 16
        ; else
        ;     tres1@xyDashPattern = 1
        ;     tres1@xyMarker = 4
        ;     tres1@xyMarkerThicknessF = 4
        end if

        if isStrSubset(grd(g),"_d") then 
            tres1@xyDashPattern = 1
            tres1@xyMarker = 4
            tres1@xyMarkerThicknessF = 4
        end if
        

        tres1@xyMarkerColor = tres1@xyLineColor
        tres2@xyMarkerColor := tres1@xyMarkerColor
        tres2@xyDashPattern = tres1@xyDashPattern
        tres2@xyLineColor   := tres1@xyLineColor
        tres2@xyMarker      = tres1@xyMarker

        ; clr(g,c,f,x) = tres1@xyLineColor
        dsh(g,c,f,x) = tres1@xyDashPattern
        mrk(g,c,f,x) = tres1@xyMarker

        xx = npr (g,c,f,x,:)
        ; x2 = npr2(g,c,f,x,:)

        y1 = total_ypdy(g,c,f,x,:)
        y2 = total_cost(g,c,f,x,:)

        if first then 
            
            plot(0) = gsn_csm_xy(wks,xx,y1,res1)
            if np.ge.2 then plot(1) = gsn_csm_xy(wks,xx,y2,res2) end if

            ; if isvar("tnpr2") then 
            ;     overlay(plot(0),gsn_csm_xy(wks,x2,y1,res1))
            ; end if

            first = False

            ; add plot w/o grid to ensure data lies over the grid
            annoid1(g,c,f,x,0) = gsn_add_annotation(plot(0),gsn_csm_xy(wks,xx,y1,tres1),False) 
            if np.ge.2 then annoid2(g,c,f,0) = gsn_add_annotation(plot(1),gsn_csm_xy(wks,xx,y2,tres2),False) end if
        else
            ; overlay(plot,gsn_csm_xy(wks,xx,yy,res))
            annoid1(g,c,f,x,0) = gsn_add_annotation(plot(0),gsn_csm_xy(wks,xx,y1,tres1),False) 
            if np.ge.2 then annoid2(g,c,f,0) = gsn_add_annotation(plot(1),gsn_csm_xy(wks,xx,y2,tres2),False) end if
        end if

    end do
    end do
    end do
    end do
    ;--------------------------------------------------------
    ;--------------------------------------------------------

;===================================================================================
;===================================================================================
        pres = setres_panel()
        pres@gsnFrame = False
        ; pres = setres_panel_labeled()
        pres@gsnPanelXWhiteSpacePercent = 5
        ; pres@gsnPanelYWhiteSpacePercent = 5
        ; pres@gsnPanelBottom = 0.1
        ; pres@txString = season

    layout = (/1,dimsizes(plot)/)

    gsn_panel(wks,plot,layout,pres)

    lname = name
    ldsh = dsh
    lclr = clr

; lname := (/"ne16_ZM","ne16_SP1","ne16_SP2"/)
lclr := (/"blue","green","red","cyan","darkolivegreen1","magenta"/)
; lclr := (/"blue","green","red","DarkBlue","DarkGreen","DarkRed"/)
lname := (/"ne16_ZM","ne16_SP1","ne16_SP2","ne30_ZM","ne30_SP1","ne30_SP2"/)
ldsh = 0

    num_name = dimsizes(ndtooned(lname))

    legend = create "Legend" legendClass wks
        "lgAutoManage"              : False
        "vpXF"                      : 0.16
        "vpYF"                      : 0.92
        "vpWidthF"                  : 0.11
        "vpHeightF"                 : 0.04 * num_name
        "lgPerimOn"                 : True
        "lgPerimFill"               : "SolidFill"
        "lgPerimFillColor"          : "white"
        "lgItemCount"               : num_name
        "lgLabelStrings"            : " "+ndtooned(lname)
        "lgLabelsOn"                : True
        "lgLineLabelsOn"            : False
        "lgLabelFontHeightF"        : 0.012
        "lgLineThicknessF"          : 8
        "lgDashIndexes"             : ndtooned(ldsh)
        "lgLineColors"              : ndtooned(lclr)
        ; "lgLineColors"              : lclr
        ; "lgMarkerSizeF"             : lres1@xyMarkerSizeF
        ; "lgItemType"                : "MarkLines"
        ; "lgMarkerColors"            : ndtooned(clr)
        ; "lgMarkerIndexes"           : ndtooned(mrk)
    end create

    draw(legend)
    frame(wks)

    trimPNG(fig_file)
;===================================================================================
;===================================================================================
end