; Create a new land input file with no vegetation
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/custom_functions.ncl"
begin 

    idir = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/lnd/clm2/surfdata_map/"
    odir = "~/E3SM/init_files/"

    ;ifile = idir+"cami-mam3_0000-01-01_1.9x2.5_L30_c090306.nc"    ; fv 1.9 x 2.5
    ; ifile = idir+"USGS-gtopo30_1.9x2.5_remap_c050602.nc"
    ifile = idir+"surfdata_ne30np4_simyr2000_c180306.nc" ; E3SM se dycore
    ; ofile = str_sub_str(ifile,".nc","_no-vegetation.nc")
    ofile = str_sub_str(ifile,idir,odir)
    ofile = str_sub_str(ofile,".nc","_no-vegetation.nc")
    

    ;fig_type = "png"
    ;fig_file = odir+"fig.aqua.topo.v1"

;=============================================================================
; Load default input data file
;=============================================================================
    infile = addfile(ifile,"r")

    printline()

;=============================================================================
; Stuff for probing the default input file
;=============================================================================
    ; if True then 
    ;     ;;; check default fractions add up properly
    ;     ; var = (/"PCT_NATVEG","PCT_CROP"/)
    ;     ; var = (/"PCT_NATVEG","PCT_CROP","PCT_WETLAND","PCT_LAKE","PCT_GLACIER","PCT_URBAN"/)
    ;     var = (/"PCT_NAT_PFT"/)
        
    ;     tmp_sum = new(dimsizes(infile->TOPO),double)
    ;     tmp_sum = 0.
    ;     do v = 0,dimsizes(var)-1
    ;         dims := dimsizes(infile->$var(v)$)
    ;         ndim := dimsizes(dims)
            
    ;         tmp := infile->$var(v)$

    ;         tmp@lat = infile->LATIXY
    ;         tmp@lon = infile->LONGXY

    ;         ; printMAM(tmp)
    ;         ; printVarSummary(tmp)
    ;         ; qplot_map_se(tmp)

    ;         ; if var(v).eq."PCT_URBAN"
    ;         ; qplot_map_se(tmp(0,:))
    ;         ; qplot_map_se(tmp(1,:))
    ;         ; qplot_map_se(tmp(2,:))
    ;         ; end if

    ;         ;----------------------------------------------------
    ;         ; plot maps of the plant functional types (PFT)
    ;         ;----------------------------------------------------
    ;         if var(v).eq."PCT_NAT_PFT"
    ;             fig_file = "PCT_NAT_PFT_maps"
    ;             wks = gsn_open_wks("png",fig_file)
    ;             plot = new(dims(0),graphic)
    ;                 res = setres_contour_fill()
    ;                 ; res@gsnDraw       = True
    ;                 ; res@gsnFrame      = True
    ;                 res@sfXArray      = tmp@lon
    ;                 res@sfYArray      = tmp@lat
    ;             do p = 0,dims(0)-1
    ;                 plot(p) = gsn_csm_contour_map_ce(wks,tmp(p,:),res)
    ;             end do
    ;             pres = setres_panel()
    ;             gsn_panel(wks,plot,(/5,4/),pres)
    ;             trimPNG(fig_file)
    ;             exit
    ;         end if
    ;         ;----------------------------------------------------
    ;         ;----------------------------------------------------

    ;         if ndim.eq.1 then
    ;             tmp_sum = tmp_sum + infile->$var(v)$
    ;         end if
    ;         if var(v).eq."PCT_URBAN"
    ;             tmp_sum = tmp_sum + dim_sum_n( infile->$var(v)$ ,0)
    ;             ; tmp = tmp + infile->$var(v)$(0,:)
    ;         end if
    ;         if var(v).eq."PCT_NAT_PFT"
    ;             tmp_sum = tmp_sum + dim_sum_n( infile->$var(v)$ ,0)
    ;             ; tmp = tmp + infile->$var(v)$(0,:)
    ;         end if
    ;     end do

    ;     printMAM(tmp_sum)
    ;     exit
    ; end if

;=============================================================================
; Create outfile and populate with input data
;=============================================================================
    if isfilepresent(ofile) then system("rm "+ofile) end if
    ; if fileexists(ofile)    then system("rm "+ofile) end if
    outfile = addfile(ofile,"c")

    vname = getfilevarnames(infile)

    ;;; loop through all variables
    do v = 0,dimsizes(vname)-1
        
        tmp := infile->$vname(v)$

        ; if vname(v).eq."PCT_NATVEG"  then 
        ;     ; tnveg = tmp
        ;     tmp = (/0./) 
        ; end if
        ; if vname(v).eq."PCT_CROP"    then 
        ;     ; tcrop = tmp
        ;     tmp = (/0./) 
        ; end if
        if vname(v).eq."PCT_NAT_PFT" then 
            tmp(0 ,:) = (/100./) 
            tmp(1:,:) = (/  0./) 
        end if

        outfile->$vname(v)$ = tmp

    end do

    

    printline()
    print("")
    print("    "+ofile)
    print("")
;=============================================================================
;=============================================================================
end