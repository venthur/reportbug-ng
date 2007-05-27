MSGFMT = msgfmt

all:
	for i in $(shell find *.po); do \
	    LANG=$$(basename $$i .po); \
	    $(MSGFMT) $$i -o $$LANG.mo; \
	done

install:
	for i in $(shell find *.mo); do \
	    LANG=$$(basename $$i .mo); \
	    mkdir -p $(DESTDIR)/usr/share/local/$$LANG/LC_MESSAGES/; \
	    cp $$i $(DESTDIR)/usr/share/local/$$LANG/LC_MESSAGES/reportbug-ng.mo; \
	done

clean:
	rm -f *.mo
