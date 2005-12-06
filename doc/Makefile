all: index.html commands.html developer.html python-api.html testing.html \
     other.html

%.html : %.txt
	rst2html.py $< $@
