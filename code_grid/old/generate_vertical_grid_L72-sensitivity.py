import os, numpy as np, xarray as xr

p0 = 1000e2
ps = 1000e2

# flags for printing debugging/tuning info/lists
print_int_debug = False
print_mid_debug = False
print_L72_comparison = False
print_final = False

nsmooth = 20

# Set up terminal colors
class tcolor: ENDC,RED,GREEN,CYAN = '\033[0m','\033[31m','\033[32m','\033[36m'
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def main():

    #---------------------------------------------------------------------------
    # Load default L72 for comparison
    #---------------------------------------------------------------------------
    home = os.getenv('HOME')
    ds72 = xr.open_dataset(f'{home}/E3SM/vert_grid_files/L72_E3SM.nc')
    # ds72 = xr.open_dataset(f'{home}/E3SM/vert_grid_files/L100_v1.nc')
    am72, bm72 = ds72.hyam.values, ds72.hybm.values
    ai72, bi72 = ds72.hyai.values, ds72.hybi.values
    mlev72 = compute_pressure_from_hybrid_coef(am72,bm72)
    ilev72 = compute_pressure_from_hybrid_coef(ai72,bi72)
    #---------------------------------------------------------------------------
    # Read array of height levels
    #---------------------------------------------------------------------------
    # height_file = open(os.getenv('HOME')+'/E3SM/vert_grid_files/grd_L100','r')
    # zlev_file = []
    # for z in height_file.read().split(): zlev_file.append( float(z) )
    # zlev_file = np.array(zlev_file)

    #---------------------------------------------------------------------------
    # simple recipe using a list of height thicknesses
    #---------------------------------------------------------------------------

    #---------------------------------------------
    # new versions of L72 to propose for v3
    #--------------------------------------------- 
    # grid_name = 'L72_E3SM_new_v1'
    # dk_list = [ 4, 4,  4,  4, 30,  4,  4,   4,   4,   4,   6]
    # dz_list = [40,80,160,320,550,650,800,1000,1300,1800,2500]
    # nsmooth = 20

    # grid_name = 'L72_E3SM_new_v2'
    # dk_list = [ 5,  5,  5,  5, 30,  4,   4,   4,   4,   6]
    # dz_list = [50,100,200,350,550,750,1000,1500,2000,2500]
    # nsmooth = 20

    # grid_name = 'L72_E3SM_new_v3'
    # dk_list = [ 5, 10,  5, 30,  4,   4,   4,   4,   6]
    # dz_list = [50,100,250,500,800,1200,1800,2400,2500]
    # nsmooth = 20

    grid_name = 'L72_E3SM_new_v4'
    dk_list = [ 4, 4,  4,  4, 30,  4,  4,   4,   4,   4,   6]
    dz_list = [60,100,160,320,550,650,800,1000,1300,1800,2500]
    nsmooth = 20

    #---------------------------------------------
    # sensitivity tests based on L72_E3SM_new_v1 - replace bottom levels with L72
    #---------------------------------------------

    # num_replace = 10
    # num_replace = 5
    # num_replace = 2

    # if 'num_replace' in locals():
        # fix_replace_top = False
        # nsmooth_replace = 2
        # grid_name += f'_R{num_replace}'

    #---------------------------------------------
    #---------------------------------------------
    ### "short" vertical grids to test normalized plotting coordinate
    # grid_name = 'L40_test'
    # dk_list = [ 12,  8,  8,  8,   4]
    # dz_list = [100,200,400,500,1000]

    # grid_name = 'L30_test'
    # dk_list = [ 12,  8,  8,  2]
    # dz_list = [100,200,400,500]

    # grid_name = 'L20_test'
    # dk_list = [ 12,  8]
    # dz_list = [100,200]


    #---------------------------------------------
    # special cases for ert grid sensitivity tests
    #---------------------------------------------

    ### L20
    # dk_list = [  2,  2,  3,   5,   4,   4]
    # dz_list = [200,400,800,1600,3200,6400]

    ### L22 - only refine L20 near surface
    # dk_list = [  4,  2,  3,   5,   4,   4]
    # dz_list = [100,400,800,1600,3200,6400]

    ### L38 - only refine L20 above surface
    # dk_list = [  2,  4,  6, 10,   8,   8]
    # dz_list = [200,200,400,800,1600,3200]

    ### L40 - double L20
    # dk_list = [  4,  4,  6, 10,   8,   8]
    # dz_list = [100,200,400,800,1600,3200]

    ### L80 - quadruple L20
    # dk_list = [ 8,  8, 12, 20, 16,  16]
    # dz_list = [50,100,200,400,800,1600]
    #--------------------------------------
    #--------------------------------------

    dz = []
    if 'dz_list' in locals() and 'zlev' not in locals():
        zlev = np.zeros(np.sum(dk_list)+1)
        kk = 1
        for d,dk in enumerate(dk_list):
            for k in range(dk):
                zlev[kk] = zlev[kk-1] + dz_list[d]
                dz.append(dz_list[d])
                # print(f'{kk}  {zlev[kk]:10.1}  {dz_list[d]}')
                kk += 1
    
    #---------------------------------------------------------------------------
    # use curve fit from climatology to get pressure from height
    #---------------------------------------------------------------------------
    ilev = np.exp( -1*zlev/(6740.) ) * 1000

    ilev = ilev[::-1]
    num_ilev = len(ilev)

    num_mlev = num_ilev-1

    #---------------------------------------------------------------------------
    # Smoothing
    #---------------------------------------------------------------------------
    # dz_smoothed   = np.zeros(num_mlev)
    zlev_smoothed = np.copy(zlev)

    for s in range(nsmooth):
        zs_tmp = np.copy(zlev_smoothed)
        for k in range(1,num_mlev): 
            zlev_smoothed[k] = ( 0.25*zs_tmp[k-1] + 0.5*zs_tmp[k] + 0.25*zs_tmp[k+1] )
    
    # for k in range(0,num_mlev): dz_smoothed[k] = zlev_smoothed[k+1] - zlev_smoothed[k]

    zlev = zlev_smoothed
    ilev = np.exp( -1*zlev/(6740.) ) * 1000
    ilev = ilev[::-1]

    #---------------------------------------------------------------------------
    # Generate hybrid vertical grid
    #---------------------------------------------------------------------------

    [ai,bi] = compute_hybrid_coef_from_pressure(ilev*1e2)

    ### make sure bottom 3 levels are pure terrain following for L72
    if (num_ilev-1)==72:
        # for a,b in ai[-3:],bi[-3:]:
        for k in range(0,3):
            k2 = num_ilev-k-1
            if ai[k2]>0:
                bi[k2] = bi[k2] + ai[k2]
                ai[k2] = 0

    ### calculate mid-level hybrid coefficients
    am = np.empty(num_mlev)
    bm = np.empty(num_mlev)
    for k in range(num_mlev):
        am[k] = ( ai[k+1] + ai[k] )/2.
        bm[k] = ( bi[k+1] + bi[k] )/2.

    mlev = compute_pressure_from_hybrid_coef(am,bm)

    #---------------------------------------------------------------------------
    # replace <num_replace> levels from bottom up with default L72
    #---------------------------------------------------------------------------
    if 'num_replace' in locals():
        if num_replace>0:

            replace_k_top = num_ilev-1-num_replace

            for k in range(num_ilev):
                if ilev72[k]>ilev[replace_k_top]:
                    k_top_replace = k
                    break

            ai = np.concatenate( ( ai[:(replace_k_top)] , ai72[k_top_replace:] ) )
            bi = np.concatenate( ( bi[:(replace_k_top)] , bi72[k_top_replace:] ) )

            ilev = compute_pressure_from_hybrid_coef(ai,bi)
            num_ilev = len(ilev)
            num_mlev = num_ilev-1

            ### re-calculate mid-level coefficients and pressure levels
            am = np.empty(num_mlev)
            bm = np.empty(num_mlev)
            for k in range(num_mlev):
                am[k] = ( ai[k+1] + ai[k] )/2.
                bm[k] = ( bi[k+1] + bi[k] )/2.
            mlev = compute_pressure_from_hybrid_coef(am,bm)

            ### add levels to new list in order to avoid disrupting smoothness

            if fix_replace_top:
                ratio_threshold = 0.3
                # for n in range(3):
                if True:
                    if 'dilev_prev' in locals(): del dilev_prev
                    cnt = 0
                    print()
                    for i in range(num_replace+10):
                        k = num_ilev-i-1
                        dilev = ilev[k] - ilev[k-1]
                        if 'dilev_prev' not in locals():
                            dilev_prev = dilev
                        else:
                            dilev_ratio = dilev / dilev_prev
                            # if n==0 or n==2:
                            #     msg = f' '
                            #     msg+= ' '*6+f'mlev: {mlev[k]:6.2f} '
                            #     msg+= ' '*6+f'ilev[k]: {ilev[k]:6.2f} '
                            #     msg+= ' '*6+f'ilev[k-1]: {ilev[k-1]:6.2f} '
                            #     msg+= ' '*8+f'dilev: {dilev:6.2f} '
                            #     msg+= ' '*6+f'prev: {dilev_prev:6.2f}'
                            #     msg+= ' '*8+f'ratio: {dilev_ratio:6.2f}'
                            #     ratio_condition = np.absolute(1-dilev_ratio) > ratio_threshold
                            #     ratio_condition1 = 1-dilev_ratio >    ratio_threshold
                            #     ratio_condition2 = 1-dilev_ratio < -1*ratio_threshold
                            #     if np.any(ilev[k-1]==ilev72) and not ratio_condition: 
                            #         msg += '   !!!!'
                            #     if np.any(ilev[k-1]==ilev72) and ratio_condition: 
                            #         msg += '   !!**'
                            #     if not np.any(ilev[k-1]==ilev72) and ratio_condition: 
                            #         msg += '   ****'
                            #     if not np.any(ilev[k-1]==ilev72) and ratio_condition1: 
                            #         msg += '   --'
                            #     if not np.any(ilev[k-1]==ilev72) and ratio_condition2: 
                            #         msg += '   ++'
                            #     print(msg)
                        dilev_prev = dilev
                        # if n==1:
                        if True:
                            if cnt<1:
                                if not np.any(ilev[k-1]==ilev72) and dilev_ratio>(1.+ratio_threshold):
                                    dilev_tmp = ( ilev[k] - ilev[k-2] )/3.
                                    ilev[k-1] = ilev[k]-dilev_tmp
                                    ilev = np.insert(ilev,k-1,ilev[k]-2*dilev_tmp)
                                    dilev_prev = ilev[k] - ilev[k-1]

                                    [ai,bi] = compute_hybrid_coef_from_pressure(ilev*1e2)
                                    num_ilev = len(ilev); num_mlev = num_ilev-1
                                    ### re-calculate mid-level coefficients and pressure levels
                                    am = np.empty(num_mlev)
                                    bm = np.empty(num_mlev)
                                    for k in range(num_mlev):
                                        am[k] = ( ai[k+1] + ai[k] )/2.
                                        bm[k] = ( bi[k+1] + bi[k] )/2.
                                    mlev = compute_pressure_from_hybrid_coef(am,bm)
                                    cnt += 1
                # exit()

            ### smooth the interface levels
            if nsmooth_replace>0:
                ks1,ks2 = replace_k_top-2,replace_k_top+1
                ilev_smoothed = np.copy(ilev)
                for s in range(nsmooth_replace):
                    is_tmp = np.copy(ilev_smoothed)
                    for k in range(ks1,ks2): 
                        ilev_smoothed[k] = ( 0.25*is_tmp[k-1] + 0.5*is_tmp[k] + 0.25*is_tmp[k+1] )
                ilev = ilev_smoothed
            ### recompute hybrid coefficients after smoothing
            [ai,bi] = compute_hybrid_coef_from_pressure(ilev*1e2)

            ### re-calculate mid-level coefficients and pressure levels
            am = np.empty(num_mlev)
            bm = np.empty(num_mlev)
            for k in range(num_mlev):
                am[k] = ( ai[k+1] + ai[k] )/2.
                bm[k] = ( bi[k+1] + bi[k] )/2.
            mlev = compute_pressure_from_hybrid_coef(am,bm)
        
    #---------------------------------------------------------------------------
    # Debug print statements
    #---------------------------------------------------------------------------

    ### print interface levels
    if print_int_debug:
        for k in range(num_ilev): 
            k2 = num_ilev-k-1
            # print(f'{k:3}  ({k2:3})    {ilev[k]:8.1f}    {ai[k]:5.3f}  {bi[k]:5.3f}')
            print(f'{k:02}  ({k2:02})    {ilev[k]:8.2f}    {zlev[k2]:8.1f}')


    ### print mid-level pressure and height
    if print_mid_debug:
        print(f'            pressure    height')
        for k in range(num_mlev): 
            k2 = num_mlev-k-1
            dz = zlev[k2+1] - zlev[k2] 
            zmid = ( zlev[k2+1] + zlev[k2] ) / 2.
            # dlev = mlev72[k] - mlev[k]
            # print(f'{k:3}  ({k2:3})    {mlev[k]:8.2f}    {am[k]:5.3f}  {bm[k]:5.3f}')
            print(f'{k:3}  ({k2:3})    {mlev[k]:8.2f}    {zmid:8.1f}     {dz:5.0f}')
            # print(f'{k:02}  ({k2:02})    {mlev[k]:8.2f}    {zmid:8.1f}    ')
        print()
    
    if print_int_debug or print_mid_debug:
        exit('Exiting before writing')

    #---------------------------------------------------------------------------
    ### compare with E3SM's L72
    #---------------------------------------------------------------------------
    # for k in range(num_mlev):
    #     k2 = num_mlev-k-1
    #     dz = zlev[k2+1] - zlev[k2] ; dlev = mlev72[k] - mlev[k]
    #     # print(f'{k:3}  ({k2:3})   {dz:8.1f}    {mlev[k]:8.2f}      {lev72[k]:8.2f}    {dlev:8.2f}')
    #     print(f'{k:3}  ({k2:3})     {am[k]:6.5f}  {am72[k]:6.5f}      {bm[k]:6.5f}  {bm72[k]:6.5f}')
    # print()
    if print_L72_comparison:
        for k in range(num_ilev): 
        # for k in range(20):
            k2 = num_ilev-k-1
            if k2<num_ilev-1:
                dz = zlev[k2+1] - zlev[k2] 
            else:
                dz = 0
            # dlev = ilev72[k] - ilev[k]
            # print(f'{k:3}  ({k2:3})   {dz:8.1f}    {ilev[k]:8.2f}      {ilev72[k]:8.2f}    {dlev:8.2f}')
            if k<num_ilev-1:
                dlev1 = ilev[k+1] - ilev[k]
                dlev2 = ilev72[k+1] - ilev72[k]
            else:
                dlev1,dlev2 = 0,0
            print(f'{k:3}      {ilev[k]:6.1f}  ({dlev1:4.1f})       {ilev72[k]:6.1f}  ({dlev2:4.1f})')
            # msg = f'{k:3}  ({k2:3})'
            # msg += f'         {ilev[k]:8.2f}  {ilev72[k]:8.2f}'
            # msg += f'         {ai[k]  :6.5f}  {ai72[k]  :6.5f}'
            # msg += f'         {bi[k]  :6.5f}  {bi72[k]  :6.5f}'
            # print(msg)
        # exit()
    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------

    ### print mid and interface levels
    if print_final:
        for k in range(num_mlev):
            k2 = num_mlev-k-1
            msg1 = f'{k:3}  ({k2:3})'
            msg2 = ' '*len(msg1)
            if k==0:
                ki = 0
                msg2 = msg2 +' '*4+' '*7+f'{ilev[ki]:8.2f}          {ai[ki]:8.5f}        {bi[ki]:8.5f}'
                msg2 = tcolor.GREEN + msg2 + tcolor.ENDC
                print(msg2)
            km = k
            ki = k+1
            msg1 = f'{k:3}  ({k2:3})'
            msg2 = ' '*len(msg1)
            msg1 = msg1 +' '*4+      f'{mlev[km]:8.2f}          {am[km]:8.5f}        {bm[km]:8.5f}'
            msg2 = msg2 +' '*4+' '*7+f'{ilev[ki]:8.2f}          {ai[ki]:8.5f}        {bi[ki]:8.5f}'
            msg2 = tcolor.GREEN + msg2 + tcolor.ENDC
            print(msg1)
            print(msg2)
        # exit()

    #---------------------------------------------------------------------------
    # Write to file
    #---------------------------------------------------------------------------
    
    if 'grid_name' not in locals(): grid_name = f'L{num_mlev}_v1'

    # ofile = os.getenv('HOME')+f'/E3SM/vert_grid_files/{grid_name}.nc'
    ofile = os.getenv('HOME')+f'/E3SM/vert_grid_files/{grid_name}.nsmooth_{nsmooth}.nc'

    mlev = xr.DataArray(mlev)
    ilev = xr.DataArray(ilev)

    ds = xr.Dataset()
    ds['lev']  = ('lev', mlev)
    ds['hyam'] = ('lev', am)
    ds['hybm'] = ('lev', bm)
    ds['ilev'] = ('ilev',ilev)
    ds['hyai'] = ('ilev',ai)
    ds['hybi'] = ('ilev',bi)
    ds['P0'] = p0

    ds['lev'].attrs['units']      = 'level'
    ds['lev'].attrs['positive']   = 'down'
    ds['ilev'].attrs['units']     = 'level'
    ds['ilev'].attrs['positive']  = 'down'
    ds['P0'].attrs['units']       = 'Pa'
    ds['P0'].attrs['long_name']   = 'reference pressure'
    ds['hyam'].attrs['long_name'] = 'hybrid A coefficient at layer midpoints'
    ds['hybm'].attrs['long_name'] = 'hybrid B coefficient at layer midpoints'
    ds['hyai'].attrs['long_name'] = 'hybrid A coefficient at layer interfaces'
    ds['hybi'].attrs['long_name'] = 'hybrid B coefficient at layer interfaces'
    
    print(f'\n{ofile}\n')

    ds.to_netcdf(ofile)

    print(f'\n{ofile}\n')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def compute_hybrid_coef_from_pressure(plev):
    """ 
    compute hybrid coefficients from pressure levels 
    """
    pm = 18230.50  # level to switch from sigma to pressure? [pa]
    pt = 100.0     # top pressure? [pa]

    psize = len(plev)
    a = np.empty(psize)
    b = np.empty(psize)

    for i in range(psize) :
        # compute sigma
        if plev[i]<pm:
            sigma = ( plev[i] - pm ) / ( pm - pt )
        else:
            sigma = ( plev[i] - pm ) / ( ps - pm )
        # compute delta
        delta = 0.0 if sigma<0.0 else 1.0
        # compute A and B, pressure coefficients
        a[i] = ( pm*(1-sigma)*delta + (1-delta)*(pm*(1+sigma)-sigma*pt) ) / p0
        b[i] = np.abs( sigma*delta )

    return [a,b]
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def compute_pressure_from_hybrid_coef(a,b):
    """
    compute pressure from hybrid coefficients
    """
    lev = ( a*p0 + b*ps ) / 100.0
    return lev
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------