import os, numpy as np, xarray as xr, copy
class tclr: ENDC,RED,GREEN,CYAN = '\033[0m','\033[31m','\033[32m','\033[36m'
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

# flags for printing debugging/tuning info/lists
print_int_debug     = False
print_mid_debug     = False
baseline_comparison = False

# # grid parameters
# add_nlev        = 32 # number of levels to add for refinement
# nsmooth         = 10 # number of smoothing iterations after refinement
# limit_z_km_bot  = 15 # lower altitude bound for refinement [km]
# limit_z_km_top  = 28 # upper altitude bound for refinement [km]


# # grid parameters
# add_nlev        = 16 # number of levels to add for refinement
# nsmooth         = 10 # number of smoothing iterations after refinement
# limit_z_km_bot  = 20 # lower altitude bound for refinement [km]
# limit_z_km_top  = 30 # upper altitude bound for refinement [km]

# grid parameters
add_nlev        = 16 # number of levels to add for refinement
nsmooth         = 10 # number of smoothing iterations after refinement
limit_z_km_bot  = 10 # lower altitude bound for refinement [km]
limit_z_km_top  = 35 # upper altitude bound for refinement [km]

#-------------------------------------------------------------------------------
# constants
p0 = 1000e2
ps = 1000e2
#-------------------------------------------------------------------------------
def main():

    grid_name  = f'2024_L80_refine_test'
    grid_name += f'.rlev_{add_nlev:02d}'
    grid_name += f'.nsmth_{nsmooth:02d}'
    grid_name += f'.zbot_{limit_z_km_bot:02d}'
    grid_name += f'.ztop_{limit_z_km_top:02d}'

    # print(grid_name)
    # exit()

    #---------------------------------------------------------------------------
    # Load E3SM default L_base and convert to approx height 
    # to mimic main level generation script
    #---------------------------------------------------------------------------
    home = os.getenv('HOME')
    
    ds_base = xr.open_dataset(f'{home}/E3SM/vert_grid_files/L80_for_E3SMv3.nc')
    am_base, bm_base = ds_base.hyam.values, ds_base.hybm.values
    ai_base, bi_base = ds_base.hyai.values, ds_base.hybi.values
    mlev_base = compute_pressure_from_hybrid_coef(am_base,bm_base)
    ilev_base = compute_pressure_from_hybrid_coef(ai_base,bi_base)
    nlev_base = len(mlev_base)

    ### rough estimate of height from pressure
    zlev = np.log(ilev_base[::-1]/1e3) * -6740.
    
    ### calculate dz
    dz = []
    for k in range(len(zlev)-1): 
        dz.append(zlev[k+1]-zlev[k])

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
    # refine the grid by adding levels
    #---------------------------------------------------------------------------
    # define index limits for refinement based on altitude limits
    limit_k_bot = (np.abs(zlev - limit_z_km_bot*1e3)).argmin()
    limit_k_top = (np.abs(zlev - limit_z_km_top*1e3)).argmin()

    dz_old = copy.deepcopy(dz)

    # add the new layers - matching the bottom layer of the refinement region
    for n in range(add_nlev):
        dz.insert(limit_k_bot,dz[limit_k_bot])

    # calculate the original thickness of refinement region
    dz_layer_sum_old = 0
    for k in range(limit_k_bot,limit_k_top+1):
        dz_layer_sum_old += dz_old[k]

    # calculate the new thickness of refinement region + extra points
    dz_layer_sum_new = 0
    for k in range(limit_k_bot,limit_k_top+add_nlev+1):
        dz_layer_sum_new += dz[k]

    # calculate and apply scaling factor that will restore the original thickness
    scaling_factor = dz_layer_sum_old / dz_layer_sum_new
    
    for k in range(limit_k_bot,limit_k_top+add_nlev+1):
        dz[k] = dz[k] * scaling_factor

    # recalculate zlev
    zlev = np.zeros(len(dz)+1)
    for k in range(1,len(dz)+1): zlev[k] = zlev[k-1]+dz[k-1]

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
    ### define limits for smoothing
    limit_k_bot = (np.abs(zlev - limit_z_km_bot*1e3)).argmin()
    limit_k_top = (np.abs(zlev - limit_z_km_top*1e3)).argmin()

    dz_smoothed   = np.zeros(num_mlev)
    zlev_smoothed = np.copy(zlev)

    for s in range(nsmooth):
        zs_tmp = np.copy(zlev_smoothed)
        dk = 4
        # only smooth modified levels and buffer of dk levels
        # for k in range(limit_k_bot-dk,limit_k_top+dk+1): 
        # dk_top = int(np.floor(s/2)) # this reduces kink at top of refinement region
        dk_top = s # this reduces kink at top of refinement region
        for k in range(limit_k_bot-dk,limit_k_top+dk_top+1): 
            zlev_smoothed[k] = ( 0.25*zs_tmp[k-1] + 0.5*zs_tmp[k] + 0.25*zs_tmp[k+1] )
            # zlev_smoothed[k] = (  (1./9.)*zs_tmp[k-2] \
            #                     + (2./9.)*zs_tmp[k-1] \
            #                     + (3./9.)*zs_tmp[k] \
            #                     + (2./9.)*zs_tmp[k+1] \
            #                     + (1./9.)*zs_tmp[k+2] \
            #                    )
        # # only smooth the edges of refinement region
        # for k in range(limit_k_bot-dk,limit_k_bot+dk+1): 
        #     zlev_smoothed[k] = ( 0.25*zs_tmp[k-1] + 0.5*zs_tmp[k] + 0.25*zs_tmp[k+1] )
        # for k in range(limit_k_top-dk,limit_k_top+dk+1): 
        #     zlev_smoothed[k] = ( 0.25*zs_tmp[k-1] + 0.5*zs_tmp[k] + 0.25*zs_tmp[k+1] )
    
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

    ### make sure bottom 3 levels are pure terrain following
    if (num_ilev-1)==nlev_base:
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
            # dlev = mlev_base[k] - mlev[k]
            # print(f'{k:3}  ({k2:3})    {mlev[k]:8.2f}    {am[k]:5.3f}  {bm[k]:5.3f}')
            print(f'{k:3}  ({k2:3})    {mlev[k]:8.2f}    {zmid:8.1f}     {dz:5.0f}')
            # print(f'{k:02}  ({k2:02})    {mlev[k]:8.2f}    {zmid:8.1f}    ')
        print()
    
    if print_int_debug or print_mid_debug:
        exit('Exiting before writing')

    #---------------------------------------------------------------------------
    ### compare with E3SM's L_base
    #---------------------------------------------------------------------------
    # for k in range(num_mlev):
    #     k2 = num_mlev-k-1
    #     dz = zlev[k2+1] - zlev[k2] ; dlev = mlev_base[k] - mlev[k]
    #     # print(f'{k:3}  ({k2:3})   {dz:8.1f}    {mlev[k]:8.2f}      {lev_base[k]:8.2f}    {dlev:8.2f}')
    #     print(f'{k:3}  ({k2:3})     {am[k]:6.5f}  {am_base[k]:6.5f}      {bm[k]:6.5f}  {bm_base[k]:6.5f}')
    # print()

    if baseline_comparison:
        for k in range(num_ilev): 
        # for k in range(20):
            k2 = num_ilev-k-1
            if k2<num_ilev-1:
                dz = zlev[k2+1] - zlev[k2] 
            else:
                dz = 0
            # dlev = ilev_base[k] - ilev[k]
            # print(f'{k:3}  ({k2:3})   {dz:8.1f}    {ilev[k]:8.2f}      {ilev_base[k]:8.2f}    {dlev:8.2f}')
            if k<num_ilev-1:
                dlev1 = ilev[k+1] - ilev[k]
                dlev2 = ilev_base[k+1] - ilev_base[k]
            else:
                dlev1,dlev2 = 0,0
            print(f'{k:3}      {ilev[k]:6.1f}  ({dlev1:4.1f})       {ilev_base[k]:6.1f}  ({dlev2:4.1f})')
            # msg = f'{k:3}  ({k2:3})'
            # msg += f'         {ilev[k]:8.2f}  {ilev_base[k]:8.2f}'
            # msg += f'         {ai[k]  :6.5f}  {ai_base[k]  :6.5f}'
            # msg += f'         {bi[k]  :6.5f}  {bi_base[k]  :6.5f}'
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
    #         msg2 = tclr.GREEN + msg2 + tclr.ENDC
    #         print(msg2)
    #     km = k
    #     ki = k+1
    #     msg1 = f'{k:3}  ({k2:3})'
    #     msg2 = ' '*len(msg1)
    #     msg1 = msg1 +' '*4+      f'{mlev[km]:8.2f}          {am[km]:8.5f}        {bm[km]:8.5f}'
    #     msg2 = msg2 +' '*4+' '*7+f'{ilev[ki]:8.2f}          {ai[ki]:8.5f}        {bi[ki]:8.5f}'
    #     msg2 = tclr.GREEN + msg2 + tclr.ENDC
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

    root_path = os.getenv('HOME')+f'/E3SM/vert_grid_files/'


    print(); print(f'{ofile}')
    print(); print(f'{ofile.replace(root_path,"")}')
    print()

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