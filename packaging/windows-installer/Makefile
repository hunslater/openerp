include Makefile.version

WEB_CLIENT_DIRECTORY=../web
GTK_CLIENT_DIRECTORY=../client
SERVER_DIRECTORY=../server
FILES_DIRECTORY=files

LAUNCH_PY2EXE=/cygdrive/c/Python25/python.exe setup.py py2exe

#MAKENSIS_ARGUMENTS=/DMAJOR_VERSION=$(MAJOR_VERSION) /DMINOR_VERSION=$(MINOR_VERSION) /DREVISION_VERSION=$(REVISION_VERSION) 

MAKENSIS_ARGUMENTS=/DMAJOR_VERSION=$(MAJOR_VERSION) /DMINOR_VERSION=$(MINOR_VERSION) /DREVISION_VERSION=$(REVISION_VERSION) /DBUILD_VERSION=$(BUILD_VERSION)

LAUNCH_MAKENSIS=makensis $(MAKENSIS_ARGUMENTS) setup.nsi

default: allinone

clean: client_clean server_clean web_clean
	rm -rf $(FILES_DIRECTORY)/*.exe
	rm -rf *.exe

client_clean:
	rm -rf $(GTK_CLIENT_DIRECTORY)/dist 
	rm -rf $(GTK_CLIENT_DIRECTORY)/build
	rm -rf $(GTK_CLIENT_DIRECTORY)/*.exe
	rm -rf $(GTK_CLIENT_DIRECTORY)/.cyg*
	rm -rf $(GTK_CLIENT_DIRECTORY)/openerp-client

client: client_clean
	(cd $(GTK_CLIENT_DIRECTORY) && $(LAUNCH_PY2EXE))
	(cd $(GTK_CLIENT_DIRECTORY) && $(LAUNCH_MAKENSIS))
	cp $(GTK_CLIENT_DIRECTORY)/openerp-*.exe $(FILES_DIRECTORY)

server_clean:
	rm -rf $(SERVER_DIRECTORY)/dist 
	rm -rf $(SERVER_DIRECTORY)/build
	rm -rf $(SERVER_DIRECTORY)/win32/dist 
	rm -rf $(SERVER_DIRECTORY)/win32/build
	rm -rf $(SERVER_DIRECTORY)/*.exe
	rm -rf $(SERVER_DIRECTORY)/.cyg*

server: server_clean
	(cd $(SERVER_DIRECTORY)/win32 && $(LAUNCH_PY2EXE))
	(cd $(SERVER_DIRECTORY) && $(LAUNCH_PY2EXE))
	(cd $(SERVER_DIRECTORY) && $(LAUNCH_MAKENSIS))
	cp $(SERVER_DIRECTORY)/openerp-*.exe $(FILES_DIRECTORY)

web_clean:
	rm -rf $(WEB_CLIENT_DIRECTORY)/dist 
	rm -rf $(WEB_CLIENT_DIRECTORY)/build
	rm -rf $(WEB_CLIENT_DIRECTORY)/win32/dist 
	rm -rf $(WEB_CLIENT_DIRECTORY)/win32/build
	rm -rf $(WEB_CLIENT_DIRECTORY)/*.exe
	rm -rf $(WEB_CLIENT_DIRECTORY)/.cyg*

web:	web_clean
	(cd $(WEB_CLIENT_DIRECTORY)/win32 && $(LAUNCH_PY2EXE))
	(cd $(WEB_CLIENT_DIRECTORY) && $(LAUNCH_PY2EXE))
	(cd $(WEB_CLIENT_DIRECTORY) && $(LAUNCH_MAKENSIS))
	cp $(WEB_CLIENT_DIRECTORY)/openerp-*.exe $(FILES_DIRECTORY)

standalone:	client server web

allinone:	standalone
	$(LAUNCH_MAKENSIS)
