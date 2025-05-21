; This script prints out heating and flux information for 
; tracking down problems in test runs with SP_CRM_SPLIT
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$HOME/NCL/custom_functions_ACME.ncl"
begin

    ifile = "/ccs/home/hannah6/ACME/scratch/ACME_SP1_CTL_ne16_64x1_4km_08/run/ACME_SP1_CTL_ne16_64x1_4km_08.cam.h1.2000-01-01-00000.remap.nc"


    lat = -2
    lon = 284

;===================================================================================
;===================================================================================
    
    infile = addfile(ifile,"r")

    ;------------------------------------------
    ; Load data from file
    ;------------------------------------------
    time = infile->time
    lev  = infile->lev
    ilev = infile->ilev

    hyam = infile->hyam
    hybm = infile->hybm
    hyai = infile->hyai
    hybi = infile->hybi

    Ps = infile->PS(:,{lat},{lon})
    P0 = infile->P0

    SPDT1 = infile->SPDT1(:,:,{lat},{lon})
    SPDT2 = infile->SPDT2(:,:,{lat},{lon})

    SPDQ1 = infile->SPDQ1(:,:,{lat},{lon})
    SPDQ2 = infile->SPDQ2(:,:,{lat},{lon})
    
    LHFLX = infile->LHFLX(:,{lat},{lon})
    SHFLX = infile->SHFLX(:,{lat},{lon})

    num_t = dimsizes(time)
    num_k = dimsizes(lev)
    num_i = dimsizes(ilev)

    ;------------------------------------------
    ; Calculate stuff
    ;------------------------------------------
    Pi = new((/num_t,num_i/),float)

    do t = 0,num_t-1
        Pi(t,:) = tofloat( hyai*P0 + hybi*Ps(t) )
    end do

    dP = Pi(:,num_i-1) - Pi(:,num_i-2)

    ; kk = num_k-1
    kk = ind( lev .eq. lev({500}) )

    SPDT1w = SPDT1(:,kk)*cpd*dP/g
    SPDT2w = SPDT2(:,kk)*cpd*dP/g
    SPDQ1w = SPDQ1(:,kk)*Lv *dP/g
    SPDQ2w = SPDQ2(:,kk)*Lv *dP/g


    ;------------------------------------------
    ; Print some diagnostics
    ;------------------------------------------


    fmt = "%8.2f"


    ; diff = SHFLX-SPDT2w

    ; print( sprintf(fmt,SPDT1w)+"     "+sprintf(fmt,SPDT2w)+"      "+sprintf(fmt,SHFLX)+"          "+sprintf(fmt,SHFLX-SPDT2w) )
    ; print( sprintf(fmt,SPDQ1w)+"     "+sprintf(fmt,SPDQ2w)+"      "+sprintf(fmt,LHFLX)+"          "+sprintf(fmt,LHFLX-SPDQ2w) )

    if kk.eq.(num_k-1) then
        str_T = sprintf(fmt,SPDT1w)+"     "+sprintf(fmt,SPDT2w)+"      "+sprintf(fmt,SHFLX)+"          "+sprintf(fmt,SHFLX+SPDT2w)
        str_Q = sprintf(fmt,SPDQ1w)+"     "+sprintf(fmt,SPDQ2w)+"      "+sprintf(fmt,LHFLX)+"          "+sprintf(fmt,LHFLX+SPDQ2w)
    else
        str_T = sprintf(fmt,SPDT1w)+"     "+sprintf(fmt,SPDT2w)
        str_Q = sprintf(fmt,SPDQ1w)+"     "+sprintf(fmt,SPDQ2w)
    end if

    print( str_T +"                     "+ str_Q )



;===================================================================================
;===================================================================================
end