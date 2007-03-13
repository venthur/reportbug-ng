all:
	$(MAKE) all -C src 

install:
	mkdir -p $(DESTDIR)/usr/bin
	cp src/reportbug-ng $(DESTDIR)/usr/bin/reportbug-ng

	mkdir -p $(DESTDIR)/usr/share/reportbug-ng/ui	
	cp -r src/ui/*.py $(DESTDIR)/usr/share/reportbug-ng/ui/
	
	mkdir -p $(DESTDIR)/usr/share/reportbug-ng/lib
	cp -r src/lib/*.py $(DESTDIR)/usr/share/reportbug-ng/lib/

	mkdir -p $(DESTDIR)/usr/share/applications
	cp *.desktop $(DESTDIR)/usr/share/applications/

clean:
	$(MAKE) clean -C src
