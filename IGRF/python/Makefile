G77 = /usr/bin/g77
F2PY = f2py2.5
LDFLAGS = -shared 

igrf.so: igrf_sub.f
	$(F2PY) -c -m igrf igrf_sub.f
	
clean:
	rm -f igrf.so IGRF.pyo IGRF.pyc
