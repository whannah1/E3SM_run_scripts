import os, numpy as np, xarray as xr

p0 = 1000e2
ps = 1000e2

pm_default = 18230.50  # for hybrid levels [Pa] - level to switch from sigma to pressure
pt_default = 100.0     # for hybrid levels [Pa] - not sure... top pressure? [pa]

# flags for printing debugging/tuning info/lists
print_int_debug = False
print_mid_debug = False

print_final_mid_int_levels = False

nsmooth = 0

# Set up terminal colors
class tcolor: ENDC,RED,GREEN,CYAN = '\033[0m','\033[31m','\033[32m','\033[36m'
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def generate_grid(grid_name=None,pm=None):

    #---------------------------------------------------------------------------
    # Load E3SM default L72 and convert to approx height 
    # to mimic main level generation script
    #---------------------------------------------------------------------------
    home = os.getenv('HOME')
    ds72 = xr.open_dataset(f'{home}/E3SM/vert_grid_files/L72_E3SM.nc')
    am72, bm72 = ds72.hyam.values, ds72.hybm.values
    ai72, bi72 = ds72.hyai.values, ds72.hybi.values
    mlev72 = compute_pressure_from_hybrid_coef(am72,bm72)
    ilev72 = compute_pressure_from_hybrid_coef(ai72,bi72)
    
    ### rough estimate of height from pressure
    zlev = np.log(ilev72[::-1]/1e3) * -6740.

    dz = []
    for k in range(len(zlev)-1): dz.append(zlev[k+1]-zlev[k])
    #---------------------------------------------------------------------------
    # use curve fit from climatology to get pressure from height
    #---------------------------------------------------------------------------
    ilev = np.exp( -1*zlev/(6740.) ) * 1000
    ilev = ilev[::-1]
    num_ilev = len(ilev)
    num_mlev = num_ilev-1
    #---------------------------------------------------------------------------
    # Generate hybrid vertical grid
    #---------------------------------------------------------------------------
    [ai,bi] = compute_hybrid_coef_from_pressure(ilev*1e2,pm=pm)

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
    #---------------------------------------------------------------------------

    ### print mid and interface levels
    if print_final_mid_int_levels:
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
    
    # if 'grid_name' not in locals(): grid_name = f'L{num_mlev}_v1'

    ofile = os.getenv('HOME')+f'/E3SM/vert_grid_files/{grid_name}.nc'
    
    # if nsmooth>0: ofile = ofile.replace('.nc',f'.nsmooth_{nsmooth}.nc')

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

    # print(f'\n{ofile}\n')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def compute_hybrid_coef_from_pressure(plev,pm=None,pt=None):
    """ 
    compute hybrid coefficients from pressure levels 
    """
    if pm is None: pm = pm_default
    if pt is None: pt = pt_default
    psize = len(plev)
    a,b = np.empty(psize),np.empty(psize)
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

    # pm_list = [400e2,200e2,100e2,50e2]
    pm_list = [300e2]

    for pm in pm_list:
        pm_mb = int(pm/1e2)
        grid_name = f'L72_E3SM_pm{pm_mb}'
        generate_grid(grid_name=grid_name,pm=pm)
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------