SUBDIRS = common osx

CLEANFILES = \
	trayicon.c
INCLUDES = \
	$(PYTHON_INCLUDES) 
export MACOSX_DEPLOYMENT_TARGET=10.4

if BUILD_GTKSPELL
gtkspelllib_LTLIBRARIES = gtkspell.la
gtkspelllibdir = $(libdir)/gajim

gtkspell_la_LIBADD = \
	$(GTKSPELL_LIBS) $(PYGTK_LIBS) 

gtkspell_la_SOURCES = \
	gtkspellmodule.c

gtkspell_la_LDFLAGS = \
	-module -avoid-version 

gtkspell_la_CFLAGS = $(GTKSPELL_CFLAGS) $(PYGTK_CFLAGS)
endif
if BUILD_TRAYICON
trayiconlib_LTLIBRARIES = trayicon.la
trayiconlibdir = $(libdir)/gajim
trayicon_la_LIBADD = $(PYGTK_LIBS)
trayicon_la_SOURCES = \
					  eggtrayicon.c \
					  trayiconmodule.c

nodist_trayicon_la_SOURCES = \
					trayicon.c

trayicon_la_LDFLAGS = \
	-module -avoid-version 
trayicon_la_CFLAGS = $(PYGTK_CFLAGS)

trayicon.c: 
	    pygtk-codegen-2.0 --prefix trayicon \
		    --register $(PYGTK_DEFS)/gdk-types.defs \
		    --register $(PYGTK_DEFS)/gtk-types.defs \
		    --override $(srcdir)/trayicon.override \
		    $(srcdir)/trayicon.defs > $@
endif
gajimsrcdir = $(pkgdatadir)/src
gajimsrc_PYTHON = $(srcdir)/*.py 

gajimsrc1dir = $(pkgdatadir)/src/common
gajimsrc1_PYTHON = \
				$(srcdir)/common/*.py 

gajimsrc2dir = $(pkgdatadir)/src/common/xmpp
gajimsrc2_PYTHON = \
				$(srcdir)/common/xmpp/*.py 

gajimsrc3dir = $(pkgdatadir)/src/common/zeroconf
gajimsrc3_PYTHON = \
				$(srcdir)/common/zeroconf/*.py 

DISTCLEANFILES = 

EXTRA_DIST = $(gajimsrc_PYTHON) \
			$(gajimsrc1_PYTHON) \
			$(gajimsrc2_PYTHON) \
			$(gajimsrc3_PYTHON) \
			gtkspellmodule.c \
			eggtrayicon.c \
			trayiconmodule.c \
			eggtrayicon.h \
			trayicon.defs \
			trayicon.override 

dist-hook:
			rm -f $(distdir)/ipython_view.py

MAINTAINERCLEANFILES = Makefile.in
