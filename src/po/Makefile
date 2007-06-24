MSGFMT = msgfmt

all:
	for i in $(shell find *.po); do \
	    LANG=$$(basename $$i .po); \
	    $(MSGFMT) $$i -o $$LANG.mo; \
	done

install:
	for i in $(shell find *.mo); do \
	    LANG=$$(basename $$i .mo); \
	    mkdir -p $(DESTDIR)/usr/share/locale/$$LANG/LC_MESSAGES/; \
	    cp $$i $(DESTDIR)/usr/share/locale/$$LANG/LC_MESSAGES/reportbug-ng.mo; \
	done

clean:
	rm -f *.mo *.po~

update:
	pygettext --keyword=tr --default-domain=reportbug-ng ..
	for i in $(shell find *.po); do \
	    echo $$i; \
	    msgmerge -U $$i reportbug-ng.pot; \
	    msgfmt --statistics $$i; \
	done
