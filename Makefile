# Makefile for TazInst.
# Check the README for more information.
#
PREFIX?=/usr
DOCDIR?=/usr/share/doc
DESTDIR?=
TAZPANEL?=/var/www/tazpanel
LINGUAS?=el es es_AR fr pt_BR sv ru

PACKAGE	=	tazinst
VERSION	:=	$(shell grep ^VERSION ${PACKAGE} | cut -d '=' -f 2)
TARBALL	=	$(PACKAGE)-$(VERSION).tar.gz

all:

# i18n.

pot:
	xgettext -o po/tazinst/tazinst.pot -L Shell \
		--package-name="TazInst" \
		--package-version="$(VERSION)" \
		./tazinst
	xgettext -o po/slitaz-installer/slitaz-installer.pot -L Shell \
		--package-name="slitaz-installer" \
		--package-version="$(VERSION)" \
		./slitaz-installer
	xgettext -o po/installer/installer.pot -L Shell \
		--package-name="installer.cgi" \
		--package-version="$(VERSION)" \
		./installer.cgi

msgmerge:
	@for l in $(LINGUAS); do \
		if [ -f "po/tazinst/$$l.po" ]; then \
			echo -n "Updating tazinst $$l po file."; \
			msgmerge -U po/tazinst/$$l.po po/tazinst/tazinst.pot ; \
		fi;\
		if [ -f "po/slitaz-installer/$$l.po" ]; then \
			echo -n "Updating slitaz-installer $$l po file."; \
			msgmerge -U po/slitaz-installer/$$l.po \
				po/slitaz-installer/slitaz-installer.pot ; \
		fi;\
		if [ -f "po/installer/$$l.po" ]; then \
			echo -n "Updating installer $$l po file."; \
			msgmerge -U po/installer/$$l.po po/installer/installer.pot ; \
		fi;\
	done;

msgfmt:
	@for l in $(LINGUAS); do \
		if [ -f "po/tazinst/$$l.po" ]; then \
			echo "Compiling tazinst $$l mo file..."; \
			mkdir -p po/mo/$$l/LC_MESSAGES; \
			msgfmt -o po/mo/$$l/LC_MESSAGES/tazinst.mo po/tazinst/$$l.po ; \
		fi;\
		if [ -f "po/slitaz-installer/$$l.po" ]; then \
			echo "Compiling slitaz-installer $$l mo file..."; \
			mkdir -p po/mo/$$l/LC_MESSAGES; \
			msgfmt -o po/mo/$$l/LC_MESSAGES/slitaz-installer.mo \
				po/slitaz-installer/$$l.po ; \
		fi;\
		if [ -f "po/installer/$$l.po" ]; then \
			echo "Compiling installer $$l mo file..."; \
			mkdir -p po/mo/$$l/LC_MESSAGES; \
			msgfmt -o po/mo/$$l/LC_MESSAGES/installer.mo po/installer/$$l.po ; \
		fi;\
	done;

# Installation.

install: msgfmt
	@echo "Installing Tazinst into $(DESTDIR)$(PREFIX)/sbin..."
	mkdir -p $(DESTDIR)$(PREFIX)/sbin
	install -m 0755 tazinst $(DESTDIR)$(PREFIX)/sbin
	@echo "Installing slitaz-installer into $(DESTDIR)$(PREFIX)/sbin..."
	mkdir -p $(DESTDIR)$(PREFIX)/sbin
	install -m 0755 slitaz-installer $(DESTDIR)$(PREFIX)/sbin
	@echo "Installing installer.cgi into $(DESTDIR)$(TAZPANEL)..."
	mkdir -p $(DESTDIR)$(TAZPANEL)/menu.d
	install -m 0755 installer.cgi $(DESTDIR)$(TAZPANEL)
	@echo "Installing installer.menu into $(DESTDIR)$(TAZPANEL)/menu.d..."
	install -m 0755 installer.menu $(DESTDIR)$(TAZPANEL)/menu.d
	@echo "Installing config file into $(DESTDIR)/etc/slitaz..."
	mkdir -p $(DESTDIR)/etc/slitaz
	install -m 0755 etc/tazinst.conf $(DESTDIR)/etc/slitaz

	@echo "Installing Tazinst documentation..."
	mkdir -p $(DESTDIR)$(DOCDIR)/tazinst
	cp -a doc/* $(DESTDIR)$(DOCDIR)/tazinst
	# i18n
	mkdir -p $(DESTDIR)$(PREFIX)/share/locale
	cp -a po/mo/* $(DESTDIR)$(PREFIX)/share/locale
	# Desktop integration
	@echo "Setting up desktop integration..."
	mkdir -p $(DESTDIR)$(PREFIX)/share
	cp -a  applications $(DESTDIR)$(PREFIX)/share

# Uninstallation and tarball clean-up commands.

uninstall:
	rm -f $(DESTDIR)/etc/slitaz/tazinst.conf
	rm -f $(DESTDIR)$(PREFIX)/sbin/tazinst
	rm -f $(DESTDIR)$(PREFIX)/sbin/slitaz_installer
	rm -f $(DESTDIR)$(TAZPANEL)/installer.cgi
	rm -f $(DESTDIR)$(TAZPANEL)/menu.d/installer.menu
	rm -rf $(DESTDIR)$(DOCDIR)/tazinst
	rm -rf $(DESTDIR)$(PREFIX)/share/locale/*/LC_MESSAGES/tazinst*.mo
	rm -rf $(DESTDIR)$(PREFIX)/share/locale/*/LC_MESSAGES/slitaz-installer*.mo
	rm -rf $(DESTDIR)$(PREFIX)/share/locale/*/LC_MESSAGES/installer*.mo
	rm -f $(DESTDIR)$(PREFIX)/share/applications/tazinst.desktop

clean:
	rm -rf _pkg
	rm -rf po/mo
	rm -f po/*/*~

dist-clean:
	rm -rf $(DISTDIR)

# Build tarball and MD5 file for packaging.
dist: dist-clean
	hg archive -t tgz $(TARBALL)
	md5sum $(TARBALL) > $(PACKAGE)-$(VERSION).md5
