all: index.html commands.html developer.html python-api.html testing.html \
     other.html browsing.html

%.html : %.txt
	rst2html.py $< $@
