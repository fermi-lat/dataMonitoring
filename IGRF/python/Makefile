G77 = /usr/bin/g77
F2PY = /afs/slac/g/glast/ground/GLAST_EXT/redhat5-i686-32bit-gcc41/python/2.6.5/gcc41/bin/f2py
LDFLAGS = -shared 

igrf.so: igrf_sub.f
	$(F2PY) -c -m igrf igrf_sub.f
	
clean:
	rm -f igrf.so IGRF.pyo IGRF.pyc
