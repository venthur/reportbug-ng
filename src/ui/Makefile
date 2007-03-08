PYUIC = pyuic

GUI_CLASSES = MainWindow.py \
	SubmitDialog.py

all: $(GUI_CLASSES)

%.py: %.ui
	$(PYUIC) $< -o $@

clean:
	rm -f $(GUI_CLASSES)

