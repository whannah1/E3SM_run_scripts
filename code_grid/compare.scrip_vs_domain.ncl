load "$NCARG_ROOT/custom_functions.ncl"
begin
    
    setfileoption("nc", "Format",  "64BitOffset")

    ;================================================================================
    ;================================================================================
    infile1 = addfile("~/E3SM/data_grid/ne4np4_scrip.nc","r")
    infile2 = addfile("~/E3SM/init_files/RCEMIP_domain.lnd.ne4np4_oQU240.160614.nc","r")


    x1 = infile1->grid_center_lat
    x2 = infile2->yc

    printDim(x1)
    printDim(x2)

    ncol = dimsizes(x1)

    dx = new(ncol,typeof(x1))

    cnt = 0

    fmt = "%12.6g"
    do n = 0,ncol-1
        dx(n) = x2(0,n) - x1(n)
        if dx(n).eq.0. then cnt = cnt+1 end if
        print( "   "+ sprintf(fmt,x1(n)) +"   "+ sprintf(fmt,x2(0,n)) +"   "+ sprintf(fmt,dx(n)) )
    end do

    printline()
    print("maxdx: "+max(dx))
    print("  cnt: "+cnt)

    ;================================================================================
    ;================================================================================
end