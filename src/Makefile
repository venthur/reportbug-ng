DIRS = ui translations

all:
	for i in $(DIRS); do \
	    $(MAKE) all -C $$i; \
	done

install:
	for i in $(DIRS); do \
	    $(MAKE) install -C $$i; \
	done

	mkdir -p $(DESTDIR)/usr/share/reportbug-ng
	cp *.py $(DESTDIR)/usr/share/reportbug-ng/

	mkdir -p $(DESTDIR)/usr/bin
	cp reportbug-ng $(DESTDIR)/usr/bin/reportbug-ng
	ln -s reportbug-ng $(DESTDIR)/usr/bin/rng

	mkdir -p $(DESTDIR)/usr/share/man/man1
	cp reportbug-ng.1 $(DESTDIR)/usr/share/man/man1/
	ln -s reportbug-ng.1 $(DESTDIR)/usr/share/man/man1/rng.1

	mkdir -p $(DESTDIR)/usr/share/applications
	cp *.desktop $(DESTDIR)/usr/share/applications/

clean:
	for i in $(DIRS); do \
	    $(MAKE) clean -C $$i; \
	done
	rm -f *.pyc
