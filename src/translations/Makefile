SRCFILES = ../*.py ../ui/*.py

all:
	@echo Compiling translations...
	for i in $(shell find *.ts); do \
	    lrelease $$i; \
	done

install:
	@echo Installing translation files...
	mkdir -p $(DESTDIR)/usr/share/reportbug-ng/translations/;
	for i in $(shell find *.qm); do \
	    cp $$i $(DESTDIR)/usr/share/reportbug-ng/translations; \
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
	pylupdate4 ../*.py ../ui/*.py -ts xx_XX.ts
	@echo Rename template according to your language and edit.
