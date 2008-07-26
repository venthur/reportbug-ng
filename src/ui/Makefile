PYUIC = pyuic4
RCC = rcc
PYRCC = pyrcc4

GUI_CLASSES = mainwindow.py \
	submitdialog.py \
	settings.py

RCCS = icons.rcc
PYRCCS = icons_rc.py


all: $(GUI_CLASSES) $(RCCS) $(PYRCCS)

%.rcc: %.qrc
	$(RCC) $< -o $@

%_rc.py: %.qrc
	$(PYRCC) $< -o $@

%.py: %.ui
	$(PYUIC) $< -o $@

install:
	mkdir -p $(DESTDIR)/usr/share/python-support/reportbug-ng/ui
	cp -r *.py $(DESTDIR)/usr/share/python-support/reportbug-ng/ui/

clean:
	rm -f $(GUI_CLASSES) $(RCCS) $(PYRCCS)
	rm -f *.pyc

