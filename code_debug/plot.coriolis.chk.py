import os, copy, ngl, xarray as xr, numpy as np
import hapy_common as hc, hapy_E3SM   as he, hapy_setres as hs
#-------------------------------------------------------------------------------

fig_file,fig_type = 'figs_debug/coriolis.chk','png'



#-------------------------------------------------------------------------------
wkres = ngl.Resources()
# npix=1024; wkres.wkWidth,wkres.wkHeight=npix,npix
wks = ngl.open_wks(fig_type,fig_file,wkres)
res = hs.res_xy()

lres = hs.res_xy()
lres.xyDashPattern    = 0
lres.xyLineThicknessF = 2
lres.xyLineColor      = 'black' 

#-------------------------------------------------------------------------------

lat = np.linspace(-90,90,num=180*4+1)

num_lat = len(lat)
pi = np.pi

omega = 2*pi/86400

fcorz1 = np.zeros(num_lat)
fcorz2 = np.zeros(num_lat)


for y in range(num_lat):
  fcorz1[y] = 2*omega*np.cos(lat[y]*pi/180.0)

  fcor = 2*omega*np.sin(lat[y]*pi/180.)
  fcorz2[y] = np.sqrt( (2*omega)**2 - fcor**2 )


res.xyLineColor = 'red'
plot = ngl.xy(wks, lat, fcorz1, res)

res.xyLineColor = 'blue'
res.xyDashPattern = 1
ngl.overlay( plot, ngl.xy(wks, lat, fcorz2 , res) )

#-------------------------------------------------------------------------------
ngl.draw(plot)
ngl.frame(wks)

print(f'\n{fig_file}.{fig_type}\n')

#-------------------------------------------------------------------------------