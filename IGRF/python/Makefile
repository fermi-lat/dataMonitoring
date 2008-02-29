G77 = /usr/bin/g77
F2PY = f2py2.5
G77FLAGS = -shared -fPIC -O2 -funroll-loops -mmmx -m3dnow -msse2 -msse
G77COMMAND= '$(G77) $(G77FLAGS)'


igrf.so: igrf_sub.f
	$(F2PY) --f77exec=$(G77COMMAND) -c -m igrf igrf_sub.f
	
clean:
	rm -f igrf.so IGRF.pyo
