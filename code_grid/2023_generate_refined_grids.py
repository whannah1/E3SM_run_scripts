import os, numpy as np, xarray as xr

p0 = 1000e2
ps = 1000e2

# flags for printing debugging/tuning info/lists
print_int_debug = False
print_mid_debug = False
print_L72_comparison = False

nsmooth = 40



# Set up terminal colors
class tcolor: ENDC,RED,GREEN,CYAN = '\033[0m','\033[31m','\033[32m','\033[36m'
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def main():


    add_nlev = 8

    grid_name = f'2023_refined_grid_test_L72+{add_nlev:02d}.nsmooth_{nsmooth:02d}'

    # print(grid_name)
    # exit()

    #---------------------------------------------------------------------------
    # Load E3SM default L72 and convert to approx height 
    # to mimic main level generation script
    #---------------------------------------------------------------------------
    home = os.getenv('HOME')
    ds72 = xr.open_dataset(f'{home}/E3SM/vert_grid_files/L72_E3SM.nc')
    # ds72 = xr.open_dataset(f'{home}/E3SM/vert_grid_files/L100_v1.nc')
    am72, bm72 = ds72.hyam.values, ds72.hybm.values
    ai72, bi72 = ds72.hyai.values, ds72.hybi.values
    mlev72 = compute_pressure_from_hybrid_coef(am72,bm72)
    ilev72 = compute_pressure_from_hybrid_coef(ai72,bi72)

    # print(ilev72)
    # exit()
    
    ### rough estimate of height from pressure
    # ilevz = np.log(ilev72/1e3) * -6740.
    # mlevz = np.log(mlev72/1e3) * -6740.
    zlev = np.log(ilev72[::-1]/1e3) * -6740.
    

    ### define lower limit for smoothing
    limit_z_km = 10
    limit_k = (np.abs(zlev - limit_z_km*1e3)).argmin()

    # print(); print(f'  limit_k: {limit_k}'); print()


    dz = []
    for k in range(len(zlev)-1): dz.append(zlev[k+1]-zlev[k])

    # for k in range(len(zlev)-1): print(f'k: {k:3d}   {zlev[k+1]}  {dz[k]}')
    # exit()
    
    ### old method to convert dk/dz list to dz/zlev
    # dk_list = [ 4, 4, 2,  4,  1,  2,  2,  2,  4,  6,  4, 14,  4,   2,   2,   6,   5,   4]
    # dz_list = [50,60,80,100,125,150,200,300,400,500,550,600,800,1000,1500,2000,2500,3000]
    # dz = []
    # if 'dz_list' in locals() and 'zlev' not in locals():
    #     zlev = np.zeros(np.sum(dk_list)+1)
    #     kk = 1
    #     for d,dk in enumerate(dk_list):
    #         for k in range(dk):
    #             zlev[kk] = zlev[kk-1] + dz_list[d]
    #             dz.append(dz_list[d])
    #             # print(f'{kk}  {zlev[kk]:10.1}  {dz_list[d]}')
    #             kk += 1

    #---------------------------------------------------------------------------
    # functions to help with refinement methods
    #---------------------------------------------------------------------------
    def is_monotonic(nz,dz):
        for k in range(nz-1):
            if dz[k+1]<dz[k] and np.absolute(dz[k+1]-dz[k])>1:
                return False
        return True
    def print_levs(zlev_new,zlev_old,dz_new,dz_old,refine_limit_k1,refine_limit_k2):
        print()
        for k in range(refine_limit_k1-2,len(zlev)-1): 
            msg1 = f'{zlev_old[k+1]:>8.2f}'
            msg2 = f'{zlev_new[k+1]:>8.2f}'
            if k<len(zlev):
                msg1 = msg1+f'{dz_old[k]:>10.2f}'
                msg2 = msg2+f'{dz_new[k]:>10.2f}'
            else:
                msg1 = msg1+' '*10
                msg2 = msg2+' '*10
            msg = f'k: {k:3d}      {msg1}       {msg2}'
            if k==refine_limit_k1: msg = msg + '  <<<<<<<<<<'
            if k==refine_limit_k2: msg = msg + '  <<<<<<<<<<'
            print(msg)
    #---------------------------------------------------------------------------
    # refinement the grid by adding levels
    #---------------------------------------------------------------------------
    # if add_nlev>0:

    # dz_orig   = copy.deepcopy(dz)
    # zlev_orig = copy.deepcopy(zlev)

    if True:

        ### start at lower limit for smoothing and continue spacing from just below
        min_dz = dz[limit_k-1] # 550 
        residual_sum = 0
        # residual_cnt = 0
        for n in range(add_nlev):
            dz.insert(limit_k,min_dz)
            residual_sum += min_dz
            # residual_cnt += 1

        ### to preserve model top scale the layers above - proportional to thickness?
        # weight = []
        # for k in range(limit_k+add_nlev,len(dz)):
        #     weight.append()

        ### to preserve model top scale the layers above uniformly
        if residual_sum>0:
            # nlev_above = len(dz) - limit_k+add_nlev
            # nlev_above = 0
            # for k in range(limit_k+add_nlev,len(dz)):
            #     if dz[k]>min_dz: nlev_above += 1
            # for k in range(limit_k+add_nlev,len(dz)):
            #     tmp_dz = dz[k]
            #     dz[k] -= residual_sum / nlev_above
            #     print(f' {k}   {tmp_dz}  {dz[k]}')

            nlev_above = 0
            wgt = np.zeros(len(dz))
            for k in range(limit_k+add_nlev,len(dz)):
                if dz[k]>min_dz: 
                    nlev_above += 1
                    wgt[k] = dz[k] - min_dz
            for k in range(limit_k+add_nlev,len(dz)):
                tmp_dz = dz[k]
                tmp_wgt = wgt[k] / np.sum(wgt)
                dz[k] -= residual_sum * tmp_wgt
                # print(f' {k}   {tmp_dz}  {dz[k]}     {tmp_wgt}')

            # while_cnt = 0
            # while 
            # if while_cnt>100: exit(f'exiting refinement due to iteration limit!  (cnt={cnt})')
        # exit()


        # recalculate zlev
        zlev = np.zeros(len(dz)+1)
        for k in range(1,len(dz)+1): zlev[k] = zlev[k-1]+dz[k-1]

        # nz = len(zlev)-1
        # for k in range(nz): 
        #     print(f'k: {k:3d}   {zlev[k+1]:6.2f}  {dz[k]:6.2f}')
        # exit()

        # print()
        # for k in range(limit_k,limit_k+20): 
        #     print(f'k: {k:3d}   {zlev[k+1]:6.2f}  {dz[k]:6.2f}')
        # exit()
    
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
    dz_smoothed   = np.zeros(num_mlev)
    zlev_smoothed = np.copy(zlev)

    for s in range(nsmooth):
        zs_tmp = np.copy(zlev_smoothed)
        # for k in range(1,num_mlev): 
        for k in range(limit_k,num_mlev): # only smooth upper levels
        # for k in range(1,limit_k): # only smooth upper levels
            zlev_smoothed[k] = ( 0.25*zs_tmp[k-1] + 0.5*zs_tmp[k] + 0.25*zs_tmp[k+1] )
    
    for k in range(0,num_mlev): dz_smoothed[k] = zlev_smoothed[k+1] - zlev_smoothed[k]

    zlev = zlev_smoothed
    dz = dz_smoothed
    ilev = np.exp( -1*zlev/(6740.) ) * 1000
    ilev = ilev[::-1]

    

    # for k in range(len(zlev)-1): print(f'k: {k:3d}   {zlev[k+1]:6.2f}  {dz[k]:6.2f}')
    # exit()

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
    # for k in range(num_mlev):
    #     k2 = num_mlev-k-1
    #     msg1 = f'{k:3}  ({k2:3})'
    #     msg2 = ' '*len(msg1)
    #     if k==0:
    #         ki = 0
    #         msg2 = msg2 +' '*4+' '*7+f'{ilev[ki]:8.2f}          {ai[ki]:8.5f}        {bi[ki]:8.5f}'
    #         msg2 = tcolor.GREEN + msg2 + tcolor.ENDC
    #         print(msg2)
    #     km = k
    #     ki = k+1
    #     msg1 = f'{k:3}  ({k2:3})'
    #     msg2 = ' '*len(msg1)
    #     msg1 = msg1 +' '*4+      f'{mlev[km]:8.2f}          {am[km]:8.5f}        {bm[km]:8.5f}'
    #     msg2 = msg2 +' '*4+' '*7+f'{ilev[ki]:8.2f}          {ai[ki]:8.5f}        {bi[ki]:8.5f}'
    #     msg2 = tcolor.GREEN + msg2 + tcolor.ENDC
    #     print(msg1)
    #     print(msg2)

    # exit()

    #---------------------------------------------------------------------------
    # Write to file
    #---------------------------------------------------------------------------
    
    if 'grid_name' not in locals(): exit('Error: grid_name not defined!')

    ofile = os.getenv('HOME')+f'/E3SM/vert_grid_files/{grid_name}.nc'    

    mlev = xr.DataArray(mlev)
    ilev = xr.DataArray(ilev)

    ds = xr.Dataset()
    ds['lev']  = ('lev', mlev.values)
    ds['hyam'] = ('lev', am)
    ds['hybm'] = ('lev', bm)
    ds['ilev'] = ('ilev',ilev.values)
    ds['hyai'] = ('ilev',ai)
    ds['hybi'] = ('ilev',bi)
    ds['P0'] = p0

    ds['lev' ].attrs['units']     = 'level'
    ds['lev' ].attrs['positive']  = 'down'
    ds['ilev'].attrs['units']     = 'level'
    ds['ilev'].attrs['positive']  = 'down'
    ds['P0'  ].attrs['units']     = 'Pa'
    ds['P0'  ].attrs['long_name'] = 'reference pressure'
    ds['hyam'].attrs['long_name'] = 'hybrid A coefficient at layer midpoints'
    ds['hybm'].attrs['long_name'] = 'hybrid B coefficient at layer midpoints'
    ds['hyai'].attrs['long_name'] = 'hybrid A coefficient at layer interfaces'
    ds['hybi'].attrs['long_name'] = 'hybrid B coefficient at layer interfaces'
    
    # print(f'\n{ofile}\n')

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