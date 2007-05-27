PYUIC = pyuic

GUI_CLASSES = MainWindow.py \
	SubmitDialog.py

all: $(GUI_CLASSES)

%.py: %.ui
	$(PYUIC) -tr _ $< -o $@

clean:
	rm -f $(GUI_CLASSES)
	rm -f *.pyc
