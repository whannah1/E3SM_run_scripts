; Create a topography file for pg1 experiments
; v1 - use existing defualt np4 file
load "$NCARG_ROOT/custom_functions.ncl"
begin 

    host = getenv("HOST")
    if isStrSubset(host,"edison") then host = "nersc" end if
    if isStrSubset(host,"cori")   then host = "nersc" end if
    if isStrSubset(host,"titan")  then host = "olcf"  end if

    setfileoption("nc", "Format",  "64BitOffset")

    res = "ne30"    ; ne4 / ne30
    
    if host.eq."olcf"  then idir  = "/lustre/atlas1/cli900/world-shared/cesm/inputdata/atm/cam/topo/" end if
    if host.eq."nersc" then idir  = "/project/projectdirs/acme/inputdata/atm/cam/topo/" end if

    if res.eq."ne30" then ifile = idir+"USGS-gtopo30_ne30np4_16xdel2-PFC-consistentSGH.nc" end if
    if res.eq."ne4"  then ifile = idir+"USGS-gtopo30_ne4np4_16x.c20160612.nc" end if

    odir = "~/E3SM/init_files/"
    ofile = odir+"pg1.topo."+res+".v1.nc"


    print("")
    print("  ifile : "+ifile)
    print("  ofile : "+ofile)
    print("")

;=============================================================================
;=============================================================================
    map_file = addfile("~/E3SM/data_grid/np4_to_pg1."+res+".v1.nc","r")
    
    gll_area = map_file->gll_area
    gll_lat  = map_file->gll_lat
    gll_lon  = map_file->gll_lon

    element_area = map_file->element_area
    element_lat  = map_file->element_lat
    element_lon  = map_file->element_lon

    elm_gll_middle_ind = map_file->elm_gll_middle_ind
    elm_gll_corner_ind = map_file->elm_gll_corner_ind
    elm_gll_edge_ind   = map_file->elm_gll_edge_ind

    ncol_out = dimsizes(element_lat)

    element_lat!0 = "ncol"
    element_lon!0 = "ncol"

;=============================================================================
; Create outfile
;=============================================================================
    if isfilepresent(ofile) then system("rm "+ofile) end if
    outfile = addfile(ofile,"c")

    outfile->lat = element_lat
    outfile->lon = element_lon

;=============================================================================
; loop through np4 input variables and translate to pg1 grid
;=============================================================================
    infile = addfile(ifile,"r")
    var = getfilevarnames(infile)
    do v = 0,dimsizes(var)-1 

        V_in := infile->$var(v)$
        dim_name := getfilevardims(infile,var(v))
        dims := dimsizes(V_in)
        ndim := dimsizes(dims)

        V_out := new(ncol_out,typeof(infile->$var(v)$))

        do e = 0,ncol_out-1
            g1 = elm_gll_middle_ind(e,:)
            g2 = elm_gll_corner_ind(e,:)
            g3 = elm_gll_edge_ind(e,:)

            w1 = gll_area(g1)
            w2 = gll_area(g2)
            w3 = gll_area(g3)

            ;;; Use an area weighted average over the element for these variables
            if any(var(v).eq.(/"PHIS","LANDFRAC","LANDM_COSLAT"/)) then 
                V_out(e) =  sum(  sum( V_in(g1) * w1 )   \
                                + sum( V_in(g2) * w2 )   \
                                + sum( V_in(g3) * w3 ) ) \
                            / ( sum(w1) + sum(w2) + sum(w3) )
            end if
        
            ;;; These variables require a pooled variance approach (w/ area weighting instead of sample size)
            if any(var(v).eq.(/"SGH","SGH30"/)) then 
                V_out(e) =  sqrt( sum(  sum( V_in(g1)^2. * w1 )   \
                                      + sum( V_in(g2)^2. * w2 )   \
                                      + sum( V_in(g3)^2. * w3 ) ) \
                                  / ( sum(w1) + sum(w2) + sum(w3) ) )
            end if

        end do ; e
            
        ;;; copy the attributes over from the input file
        copy_VarAtts(infile->$var(v)$,V_out)

        ;;; copy coordinate names one by one
        do n = 0,ndim-1
            V_out!n = dim_name(n)
            if isfilevarcoord(infile,var(v),dim_name(n)) .and. dim_name(n).ne."ncol" then
                V_out&$dim_name(n)$ = infile->$var(v)$&$dim_name(n)$
            end if
        end do
        
        outfile->$var(v)$ = V_out

    end do
;=============================================================================
;=============================================================================
    ; print("")
    ; print("    "+ofile)
    ; print("")
    ; printline()
;=============================================================================
;=============================================================================
end