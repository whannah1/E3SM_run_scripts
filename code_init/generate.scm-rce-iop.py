# This script creates a custom IOP file for use in the E3SM SCM
# The essential variables are:
#   bdate     Base date
#   time      Time after 0Z on base date
#   lev       pressure levels
#   lat       Latitude
#   lon       Longitude
#   phis      Surface geopotential
#   t         Temperature
#   divt      Horizontal T advective tendency
#   q         Specific humidity
#   divq      Horizontal Q advective tendency
#   ps        Surface pressure
#   omega     Vertical pressure velocity
#   u         U wind
#   v         V windspeed
#   usrf      U wind at surface
#   vsrf      V wind at surface
#   pt        Surface pressure tendency
#-------------------------------------------------------------------------------
import os, datetime, xarray as xr, numpy as np
#-------------------------------------------------------------------------------
# Calculate saturation specific humidity (kg/kg) from temperature (k) and pressure (mb)
# Buck Research Manual (1996)
def calc_Qsat (Ta,Pa) :
   Tc = Ta - 273.
   ew = 6.1121*(1.0007+3.46e-6*Pa)*np.exp((17.502*Tc)/(240.97+Tc))       # in mb
   qs = 0.62197*(ew/(Pa-0.378*ew))                                       # mb -> kg/kg
   return qs
#-------------------------------------------------------------------------------

ndays   = 1000     # number of days to simulate
tstep   = 3*3600   # model time step in seconds


sst_case = [300]

debug_mode = False

output_path = '/global/cfs/projectdirs/m3312/whannah/init_files'

#-------------------------------------------------------------------------------
# Constants
zt  = 20e3       # m
po  = 1014.8     # hPa
g   = 9.79764    # m/s
Rd  = 287.04     # J / (kg K)
G   = 0.0067     # Lapse Rate [ K/m ]
zq1 = 4e3        # m
zq2 = 7.5e3      # m
qt  = 10^-11     # g/kg

tsz = int(ndays*86400/tstep)     # number of time steps

lat,lon = 0.,0.
yr1 = 0000

ztop,dz = 65e3, 1000

#-------------------------------------------------------------------------------
for c,sst in enumerate(sst_case):

  ofile = f'{output_path}/RCE_iopfile.SST_{sst}K.nc'

  #-----------------------------------------------------------------------------
  # Setup time variables
  bdate       = yr1*1e4 + 101
  tsec        = np.arange(0,(tsz)*tstep,tstep)
  time        = tsec / 86400.

  time = xr.DataArray(time,coords={'time':time})
  time['units'] = f'days since {yr1}-01-01 00:00:00'

  lat = xr.DataArray([lat],dims='lat')
  lon = xr.DataArray([lon],dims='lon')

  lat.attrs['units'],lat.attrs['long_name'],lat.attrs['standard_name'] = 'degrees_N','latitude','latitude'
  lon.attrs['units'],lon.attrs['long_name'],lon.attrs['standard_name'] = 'degrees_E','longitude','longitude'

  #-----------------------------------------------------------------------------
  # Setup vertical coordinate
  zlev = np.linspace(0,ztop,int(ztop/dz))
  nlev = len(zlev)

  #-----------------------------------------------------------------------------
  # Generate profiles of temperature, humidity, pressure 

  T  = np.zeros(nlev)
  q  = np.zeros(nlev)
  p  = np.zeros(nlev)
  Tv = np.zeros(nlev)
  RH = np.zeros(nlev)

  # set parameter for specific humidity [g/kg]
  if sst==295: qo = 12.00
  if sst==300: qo = 18.65
  if sst==305: qo = 24.00

  # set temperature parameters
  To  = sst
  Tvo = To*( 1. + 0.608*qo/1e3 )
  Tvt = Tvo - G*zt

  # set pressure parameter
  pt = po * np.power( Tvt/Tvo, g/(Rd*G) )

  # iterate upwards from the surface to generate analytic profiles
  for k in range(nlev):
    # Analytic profiles
    if zlev[k]<=zt:
      q[k]  = qo * np.exp(-1.*zlev[k]/zq1) * np.exp(-1.*np.square(zlev[k]/zq2))
      Tv[k] = Tvo - G*zlev[k]
      p[k]  = po * np.power( (Tvo-G*zlev[k])/Tvo , g/(Rd*G) )
    else:
      q[k]  = qt
      Tv[k] = Tvt
      p[k]  = pt * np.exp( -1.*( (g*(zlev[k]-zt))/(Rd*Tvt) ) )

    # specify temperature from virtual temperature
    T[k] = Tv[k] / ( 1.0 + 0.608*q[k]/1e3 )

    qsat = calc_Qsat(T[k],p[k]) * 1e3
    RH[k] = ( q[k] / qsat ) *100.

    # limit RH to 100%
    if RH[k]>1.: RH[k]==1.

  # convert pressure to Pa
  plev = p*1e2
  plev = xr.DataArray(plev,coords={'lev':plev})
  plev['units'] = 'hPa'
  
  #-----------------------------------------------------------------------------
  # prepare output data - broadcast to all times
  output_dim_1d = [tsz,1,1]
  output_dim_2d = [tsz,nlev,1,1]


  # Basic Variables
  T_out    = xr.DataArray( np.zeros(output_dim_2d), coords={'time':time,'lev':plev,'lat':lat,'lon':lon} )
  q_out    = xr.DataArray( np.zeros(output_dim_2d), coords={'time':time,'lev':plev,'lat':lat,'lon':lon} )
  u        = xr.DataArray( np.zeros(output_dim_2d), coords={'time':time,'lev':plev,'lat':lat,'lon':lon} )
  v        = xr.DataArray( np.zeros(output_dim_2d), coords={'time':time,'lev':plev,'lat':lat,'lon':lon} )
  omega    = xr.DataArray( np.zeros(output_dim_2d), coords={'time':time,'lev':plev,'lat':lat,'lon':lon} )
  # surface Variables
  phis     = xr.DataArray( np.zeros(output_dim_1d), coords={'time':time,'lat':lat,'lon':lon} )
  ps       = xr.DataArray( np.zeros(output_dim_1d), coords={'time':time,'lat':lat,'lon':lon} )
  Tg       = xr.DataArray( np.zeros(output_dim_1d), coords={'time':time,'lat':lat,'lon':lon} )
  Tsair    = xr.DataArray( np.zeros(output_dim_1d), coords={'time':time,'lat':lat,'lon':lon} )
  vsrf     = xr.DataArray( np.zeros(output_dim_1d), coords={'time':time,'lat':lat,'lon':lon} )
  usrf     = xr.DataArray( np.zeros(output_dim_1d), coords={'time':time,'lat':lat,'lon':lon} )
  TS       = xr.DataArray( np.zeros(output_dim_1d), coords={'time':time,'lat':lat,'lon':lon} )
  TSOCN    = xr.DataArray( np.zeros(output_dim_1d), coords={'time':time,'lat':lat,'lon':lon} )
  TSICE    = xr.DataArray( np.zeros(output_dim_1d), coords={'time':time,'lat':lat,'lon':lon} )
  TSICERAD = xr.DataArray( np.zeros(output_dim_1d), coords={'time':time,'lat':lat,'lon':lon} )
  SICTHK   = xr.DataArray( np.zeros(output_dim_1d), coords={'time':time,'lat':lat,'lon':lon} )
  ICEFRAC  = xr.DataArray( np.zeros(output_dim_1d), coords={'time':time,'lat':lat,'lon':lon} )
  # Tendency variables
  Ptend    = xr.DataArray( np.zeros(output_dim_1d), coords={'time':time,'lat':lat,'lon':lon} )             # surface pressure tendency
  divt     = xr.DataArray( np.zeros(output_dim_2d), coords={'time':time,'lev':plev,'lat':lat,'lon':lon} )  # temperature divergence
  divq     = xr.DataArray( np.zeros(output_dim_2d), coords={'time':time,'lev':plev,'lat':lat,'lon':lon} )  # specific humidity divergence

  
  # copy analytic profiles
  for t in range(tsz):
    T_out[t,:,0,0] = T[:]
    q_out[t,:,0,0] = q[:]

  # Flip profiles
  T_out = T_out[:,::-1,0,0]
  q_out = q_out[:,::-1,0,0]

  q_out = q_out/1e3   # convert to kg/kg

  # Set surface variables
  ps[:]      = 1014.8 *1e2
  Tg[:]      = sst
  Tsair[:]   = sst
  TS[:]      = sst
  TSOCN[:]   = sst
  TSICE[:]   = 271.36
  usrf[:]    = 1.
  vsrf[:]    = 1.

  #-----------------------------------------------------------------------------
  # add meta data

  ps.attrs['units'],      ps.attrs['long_name']       = 'Pa',      'Surface Pressure'
  phis.attrs['units'],    phis.attrs['long_name']     = 'm2/s2',   'Surface geopotential'
  omega.attrs['units'],   omega.attrs['long_name']    = 'Pa/s',    'Vertical pressure velocity'
  u.attrs['units'],       u.attrs['long_name']        = 'm/s',     'U wind'
  v.attrs['units'],       v.attrs['long_name']        = 'm/s',     'V wind'
  Ptend.attrs['units'],   Ptend.attrs['long_name']    = 'Pa/s',    'Surface pressure tendency'
  Tg.attrs['units'],      Tg.attrs['long_name']       = 'K',       'Ground temperature'
  Tsair.attrs['units'],   Tsair.attrs['long_name']    = 'K',       'Surface air temperature'
  TS.attrs['units'],      TS.attrs['long_name']       = 'K',       'Surface temperature'
  TSOCN.attrs['units'],   TSOCN.attrs['long_name']    = 'K',       'Ocean temperature'
  TSICE.attrs['units'],   TSICE.attrs['long_name']    = 'K',       'Surface Ice temperature'
  TSICERAD.attrs['units'],TSICERAD.attrs['long_name'] = 'K',       'Radiatively equivalent ice temperature'
  SICTHK.attrs['units'],  SICTHK.attrs['long_name']   = 'm',       'Sea Ice Thickness'
  ICEFRAC.attrs['units'], ICEFRAC.attrs['long_name']  = 'fraction','Fraction of sfc area covered by sea-ice'
  usrf.attrs['units'],    usrf.attrs['long_name']     = 'm/s',     'Surface U wind'
  vsrf.attrs['units'],    vsrf.attrs['long_name']     = 'm/s',     'surface V wind'

  #-----------------------------------------------------------------------------
  # create output dataset

  ds = xr.Dataset()
  ds.attrs['description']   = 'RCE forcing file for E3SM SCM'
  ds.attrs['author']        = 'Walter Hannah (LLNL)'
  ds.attrs['creation_date'] = datetime.datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S")

  ds['bdate']    = bdate
  ds['tsec']     = tsec
  ds['T']        = T_out
  ds['q']        = q_out
  ds['phis']     = phis
  ds['Ps']       = ps
  ds['omega']    = omega
  ds['u']        = u
  ds['v']        = v
  ds['Tg']       = Tg
  ds['Tsair']    = Tsair
  ds['TS']       = TS
  ds['TSOCN']    = TSOCN
  ds['TSICE']    = TSICE
  ds['TSICE']    = TSICERAD
  ds['SICTHK']   = SICTHK
  ds['ICEFRAC']  = ICEFRAC
  ds['usrf']     = usrf
  ds['vsrf']     = vsrf
  ds['Ptend']    = Ptend
  ds['divt']     = divt
  ds['divq']     = divq

  # print(ds)
  # exit()

  # write output file
  ds.to_netcdf(ofile,format='NETCDF3_64BIT')

  # use nccopy to convert to "classic" file option
  tfile = ofile.replace('.nc','_classic.nc')
  os.system(f'nccopy -k classic {ofile}  {tfile}')
  os.system(f'mv {tfile} {ofile}')

  print(f'\n{ofile}\n')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------