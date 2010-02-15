from IGRF import IGRF
from numpy import *
import pylab as p

mfield=IGRF()

altitude=565.0
year=2000.0

latitudes=arange(-30,30.1,1.0)
longitudes=arange(-180,180,1.0)
cutoff=["Rigidity cutoff map"]
bb0=["B/B0 map"]
ilat=["Invariant latitude map"]
ilambda=["Invariant lambda map"]
ir=["Invariant radius map"]

for lat in latitudes:
   for lon in longitudes:
      mfield.compute(lat,lon,altitude,year)
      cutoff.append(mfield.RigidityCutoff)
      bb0.append(mfield.BB0)
      ilambda.append(mfield.InvariantLambda)
      ilat.append(mfield.InvariantLatitude)
      ir.append(mfield.InvariantRadius)

for arr in [cutoff,bb0,ilat,ilambda,ir]:
    arrx=array(arr[1:]).reshape(len(latitudes),-1)
    p.figure()
    p.title(arr[0])
    p.pcolor(longitudes,latitudes,arrx,shading='flat') 
    p.xlim(-180,180)
    p.colorbar()

p.show()
