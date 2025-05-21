; Create lnd and ocn domain files for pg1 experiments
; v1 - use existing defualt np4 file
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/custom_functions.ncl"
begin 

    host = getenv("HOST")
    if isStrSubset(host,"edison") then host = "nersc" end if
    if isStrSubset(host,"cori")   then host = "nersc" end if
    if isStrSubset(host,"titan")  then host = "olcf"  end if

    setfileoption("nc", "Format",  "64BitOffset")

    res = "ne30"    ; ne4 / ne30 
    
    if host.eq."olcf"  then idir  = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/share/domains/" end if
    if host.eq."nersc" then idir  = "/project/projectdirs/acme/inputdata/share/domains/" end if
    
    if res.eq."ne30" then 
        lnd_ifile = "domain.lnd.ne30np4_gx1v6.110905.nc"
        ocn_ifile = "domain.ocn.ne30np4_gx1v6_110217.nc" 
    end if
    if res.eq."ne4"  then 
        lnd_ifile = "domain.lnd.ne4np4_oQU240.160614.nc"
        ocn_ifile = "domain.ocn.ne4np4_oQU240.160614.nc" 
    end if

    odir = "~/E3SM/init_files/"
    lnd_ofile = "pg1.domain.lnd."+res+".nc"
    ocn_ofile = "pg1.domain.ocn."+res+".nc"

    print("")
    print("  idir : "+idir)
    print("  odir : "+odir)
    print("")

;==================================================================================================
; Load file that maps from np4 => np1
;==================================================================================================
    map_file = addfile("~/E3SM/data_grid/np4_to_pg1."+res+".v1.nc","r")
    
    gll_area = map_file->gll_area
    gll_lat  = map_file->gll_lat
    gll_lon  = map_file->gll_lon

    element_area = map_file->element_area
    element_lat  = map_file->element_lat
    element_lon  = map_file->element_lon

    element_corner_lat = map_file->element_corner_lat
    element_corner_lon = map_file->element_corner_lon

    elm_gll_middle_ind = map_file->elm_gll_middle_ind
    elm_gll_corner_ind = map_file->elm_gll_corner_ind
    elm_gll_edge_ind   = map_file->elm_gll_edge_ind

    elm_gll_corner_lat = map_file->elm_gll_corner_lat
    elm_gll_corner_lon = map_file->elm_gll_corner_lon

    ncol_out = dimsizes(element_lat)

    element_lat!0 = "ncol"
    element_lon!0 = "ncol"
;==================================================================================================
; Make new domain files
;==================================================================================================
    do f = 0,1

        if f.eq.0 then 
            ifile = lnd_ifile 
            ofile = lnd_ofile
        end if
        if f.eq.1 then 
            ifile = ocn_ifile
            ofile = ocn_ofile
        end if

        printline()
        print("")
        print("  Land domain file:")
        print("")
        print("    ifile: "+idir+ifile)
        print("")

        if isfilepresent(odir+ofile) then system("rm "+odir+ofile) end if
        infile  = addfile(idir+ifile,"r")
        outfile = addfile(odir+ofile,"c")
        
        ; var = getfilevarnames(infile)
        var = (/"xc","yc","xv","yv","area","frac","mask"/)

        do v = 0,dimsizes(var)-1 
            
            print("  var: "+var(v))

            V_in := infile->$var(v)$

            dim_name := getfilevardims(infile,var(v))
            dims := dimsizes(V_in)
            ndim := dimsizes(dims)

            ;;; Use an area weighted average over the element for these variables
            if any(var(v).eq.(/"frac"/)) then 
                V_out := new((/1,ncol_out/),typeof(infile->$var(v)$))
                do e = 0,ncol_out-1
                    ;;; start with middle nodes
                    gll_ind := elm_gll_middle_ind(e,:)
                    ;;; add corners
                    tmp_ind := array_append_record(gll_ind,elm_gll_corner_ind(e,:),0)
                    gll_ind := tmp_ind
                    ;;; add edges
                    tmp_ind := array_append_record(gll_ind,elm_gll_edge_ind(e,:),0)
                    gll_ind := tmp_ind
                    ;; define area weights
                    wgt = gll_area(gll_ind) / sum(gll_area(gll_ind))
                    ;;; calcualte average
                    V_out(0,e) =  sum( V_in(0,gll_ind) * wgt )
                end do ; e
                V_out!0 = "nj"
                V_out!1 = "ni"
            end if

            if var(v).eq."frac" then tfrac = V_out(0,:) end if
            if var(v).eq."mask" then
                V_out(0,:) = where(tfrac.gt.0.,1,0)
            end if

            if any(var(v).eq.(/"area","xc","yc"/)) then
                V_out := new((/1,ncol_out/),typeof(infile->$var(v)$))
                if var(v).eq."area" then V_out(0,:) = element_area end if
                if var(v).eq."xc"   then V_out(0,:) = element_lon  end if
                if var(v).eq."yc"   then V_out(0,:) = element_lat  end if
                V_out!0 = "nj"
                V_out!1 = "ni"
            end if

            if any(var(v).eq.(/"xv","yv"/)) then
                V_out := new((/1,ncol_out,5/),typeof(infile->$var(v)$))
                if var(v).eq."xv" then V_out(0,:,:) = element_corner_lon end if
                if var(v).eq."yv" then V_out(0,:,:) = element_corner_lat end if
                V_out!0 = "nj"
                V_out!1 = "ni"
                V_out!2 = "nv"
            end if

            copy_VarAtts(infile->$var(v)$,V_out)

            ;;; copy coordinate names
            do n = 0,ndim-1
                V_out!n = dim_name(n)
            end do
            
            outfile->$var(v)$ = V_out

            ;;; create a diagnostic plot
            if any(var(v).eq.(/"frac","mask"/)) then 
                V_in@long_name = var(v)
                V_out@long_name = var(v)
                np4_scrip = addfile("~/Research/E3SM/data_grid/"+res+"np4_scrip.nc","r")
                np1_scrip = addfile("~/Research/E3SM/data_grid/"+res+"np1_scrip.nc","r")
                fig_file = "pg1.domain.test"
                qpwks = gsn_open_wks("x11",fig_file)
                qplot = new(2,graphic)
                    qpres = setres_contour_fill()
                    qpres@cnFillOn      = True
                    qpres@cnFillMode    = "CellFill"
                    qpres@sfXArray      := np4_scrip->grid_center_lon
                    qpres@sfYArray      := np4_scrip->grid_center_lat
                    qpres@sfXCellBounds := np4_scrip->grid_corner_lon(:,:)
                    qpres@sfYCellBounds := np4_scrip->grid_corner_lat(:,:)
                qplot(0) = gsn_csm_contour_map_ce(qpwks,V_in(0,:),qpres)
                    qpres@sfXArray      := np1_scrip->grid_center_lon
                    qpres@sfYArray      := np1_scrip->grid_center_lat
                    qpres@sfXCellBounds := np1_scrip->grid_corner_lon(:,:)
                    qpres@sfYCellBounds := np1_scrip->grid_corner_lat(:,:)
                qplot(1) = gsn_csm_contour_map_ce(qpwks,V_out(0,:),qpres)
                gsn_panel(qpwks,qplot,(/dimsizes(qplot),1/),setres_panel())
                ; trimPNG(fig_file)
                ; exit
            end if

        end do ; v
        
        print("    ofile: "+odir+ofile)
        print("")

    end do ; f

;==================================================================================================
;==================================================================================================
end