MSGFMT = msgfmt
SRCFILES = ../*.py ../ui/*.py

all:
	@echo Compiling translations...
	for i in $(shell find *.ts); do \
	    lrelease $$i; \
	done

install:
	for i in $(shell find *.mo); do \
	    LANG=$$(basename $$i .mo); \
	    mkdir -p $(DESTDIR)/usr/share/locale/$$LANG/LC_MESSAGES/; \
	    cp $$i $(DESTDIR)/usr/share/locale/$$LANG/LC_MESSAGES/reportbug-ng.mo; \
	done

clean:
	@echo Removing generated files...
	rm -f *.qm

update:
	@echo Updating translation files...
	for i in $(shell find *.ts); do \
	    echo $$i; \
	    pylupdate4 $(SRCFILES) -ts $$i; \
	done

template:
	@echo Generating translation template...
	pylupdate4 ../*.py ../ui/*.py -ts rng_XX.ts
	@echo Rename template according to your language and edit.
