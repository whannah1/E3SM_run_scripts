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
    ; idir = "~/ACME/Cases/"

    ; grd = "ne30_d"
    ; grd = "1.9x2.5"
    ; cld = "SP2"
    fac = 1
    cnx = 64
    cny = 1

    ; grd = "ne30"+(/"_d","_p"/)
    grd = (/"ne16_d","ne16_p","ne30_d","ne30_p"/)
    ; grd = (/"ne16_p","ne30_p"/)
    cld = (/"ZM","SP1","SP2"/)
    ; fac = (/1,4/)

    ; cnx = (/64,16,8/)
    ; cny = (/ 1, 4,8/)

    ; npr = (/64,128,256,512,1024/)


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

    file_names = ""
    file_count = 0

    g := 0
    do g = 0,num_grd-1
    do c = 0,num_cld-1
    do f = 0,num_fac-1
    do x = 0,num_cnx-1

        if fac(f).eq.1 then 
            if grd(g).eq."1.9x2.5" then tnpr := (/256/) end if
            ; if grd(g).eq."ne4"  then tnpr := (/  96,  192,  384, 768, 1536/) end if
            if grd(g).eq."ne16" then tnpr := (/865, 1536, 1729, 3072, 3457, 6144, 6913, 12288, 13826/) end if
            if grd(g).eq."ne30" then tnpr := (/2700, 3038, 5400, 6076, 10800, 12151, 21600, 24301, 43200, 48602/) end if


            if grd(g).eq."ne16_p" then tnpr := (/865, 1729, 3457, 6913, 13826/) end if
            if grd(g).eq."ne16_d" then tnpr := (/1536, 3072, 6144, 12288/) end if

            if grd(g).eq."ne30_d" then tnpr := (/2700, 5400, 10800, 21600, 43200/) end if
            if grd(g).eq."ne30_p" then tnpr := (/3038, 6076,12151,24301,48602/) end if

        end if

    

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

            ;---------------------------------------------------------------------------------
            ;---------------------------------------------------------------------------------
            idir = "~/ACME/scratch/"
            ;---------------------------------------------------------------------------------
            ;---------------------------------------------------------------------------------

            ; idir = "~/ACME/Cases/"
            idir = "/ccs/home/hannah6/ACME/Cases/"
            if fileexists(idir+case+"/timing") then
                ;--------------------------------------------------------
                ; find the names of the available timing files
                ;--------------------------------------------------------
                files_1 := systemfunc("ls -1t "+idir+case+"/timing/acme_timing."+case+"*")
                files_2 := systemfunc("ls -1t "+idir+case+"/timing/acme_timing_stats.*")
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

                cmd = "cp "+file2+" ~/ACME/timing_files/"+case+"."+str_sub_str(file2,idir+case+"/timing/","")
                print(""+cmd)
                system(cmd)

                ; file_names = file_names+" "+file2
                ; file_count = file_count+1

                ; if file_count.eq.0 then
                ;     file_names = file2
                ; else
                ;     file_names := array_append_record(file_names,file2,0)
                ; end if
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
                    ; do i = 0,dimsizes(data2)-1
                    ;     ; if isStrSubset(data2(i),"phys_run1") then
                    ;     ;     print( data2(i) )
                    ;     ;     print( str_to_flt(data2(i)) )
                    ;     ;     exit
                    ;     ; end if

                    ;     ; use 3 for "walltotal"
                    ;     ; use 4 for "wallmax"
                    ;     di = 3

                    ;     if isStrSubset(data2(i),"phys_run1") then 
                    ;         tmp := str_to_flt(data2(i))
                    ;         total_phys1(g,c,f,x,n) = tmp(di) 
                    ;     end if
                    ;     ; if isStrSubset(data2(i),"phys_run2") then 
                    ;     if isStrSubset(data2(i),"moist_convection") then 
                    ;         tmp := str_to_flt(data2(i))
                    ;         total_phys2(g,c,f,x,n) = tmp(di) 
                    ;     end if

                    ; end do
                end if
            end if
            ;---------------------------------------------------------------------------------
            ;---------------------------------------------------------------------------------
            
            ; if n.eq.0 then print("") end if

            ; fmt = "%10.2f"
            ; if first then
            ;     print( strpad("",35) +"    "+ strpad("yr / day",12) +"    "+ strpad("total_cost",12) \
            ;                          +"    "+ strpad("phys_run1",12)  +"    "+ strpad("phys_run2",12) )
            ;     first = False
            ; end if

            ; if ismissing(total_cost(g,c,f,x,n)) then
            ;     print( strpad(case,36) +"    "+strpad("missing",12))
            ; else
            ;     ; print( strpad(case,30) +"    "+ sprintf(fmt,total_cost(g,c,f,x,n)) +"    "+ sprintf(fmt,total_ypdy(g,c,f,x,n)) )
            ;     print( strpad(case,35) +"    "+ sprintf(fmt,total_ypdy (g,c,f,x,n)) +"    "+ sprintf(fmt,total_cost (g,c,f,x,n)) \
            ;                            +"    "+ sprintf(fmt,total_phys1(g,c,f,x,n)) +"    "+ sprintf(fmt,total_phys2(g,c,f,x,n)) )
            ; end if

            ; print(total_cost)
            ; print(total_ypdy)
            ; exit
            
            ;---------------------------------------------------------------------------------
            ;---------------------------------------------------------------------------------
        end do
    end do
    end do
    end do
    end do
    

    ; system("cp "+file_names+" ~/ACME/timing_files/")

;===================================================================================
;===================================================================================
end