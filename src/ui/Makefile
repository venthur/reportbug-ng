PYUIC = pyuic

GUI_CLASSES = MainWindow.py \
	SubmitDialog.py

all: $(GUI_CLASSES)

%.py: %.ui
	$(PYUIC) -tr _ $< -o $@

install:
	mkdir -p $(DESTDIR)/usr/share/reportbug-ng/ui
	cp -r *.py $(DESTDIR)/usr/share/reportbug-ng/ui/

clean:
	rm -f $(GUI_CLASSES)
	rm -f *.pyc
