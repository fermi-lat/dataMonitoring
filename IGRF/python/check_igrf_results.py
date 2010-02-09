import sys,IGRF

f=open(sys.argv[1])
m=IGRF.IGRF()

head=f.readline()
toks=head.split()
if toks[0]!='Date': raise RuntimeError,'File not understood'

year,alt=float(toks[2]),float(toks[5])

print 'Date:',year,'Altitude:',alt

maxdf,maxdx,maxdy,maxdz=0.,0.,0.,0.

for line in f:
   toks=line.split()
   if len(toks)!=9: continue
   try: lat,lon,md,mi,mh,mx,my,mz,mf=[float(x) for x in toks]
   except: continue
   
   m.compute(lat,lon,alt,year)
   deltaf=(mf-m.BAbs*1e5)/mf
   deltax=(mx-m.BNorth*1e5)/mf
   deltay=(my-m.BEast*1e5)/mf
   deltaz=(mz-m.BDown*1e5)/mf

   maxdf=max(maxdf,deltaf)
   maxdx=max(maxdx,deltax)
   maxdy=max(maxdy,deltay)
   maxdz=max(maxdz,deltaz)

   if (deltaf+deltax+deltay+deltaz>0.01):   
      print "Comparison: lat=%.1f lon=%.1f ref=%.1f igrf=%.1f delta=%f"\
            %(lat,lon,mf, m.BAbs*1e5,deltaf)  
      print "            refx=%.1f igrfx=%.1f deltax=%f"\
            %(mx, m.BNorth*1e5,deltax)  
      print "            refy=%.1f igrfy=%.1f deltax=%f"\
            %(my, m.BEast*1e5,deltay)  
      print "            refz=%.1f igrfz=%.1f deltax=%f"\
            %(mz, m.BDown*1e5,deltaz)  
 
    
print "Max deviation: "
print "  Df=",maxdf
print "  Dx=",maxdx
print "  Dy=",maxdy
print "  Dz=",maxdz
      
