PREFIX   := $(HOME)/.local
APP_DIR  := $(PREFIX)/share/applications
ICON_DIR := $(PREFIX)/share/icons/hicolor/scalable/apps
SRCDIR   := $(abspath .)

.PHONY: install uninstall

install:
	@echo "Installing Gemtext Editor..."
	install -Dm644 resources/icons/hicolor/scalable/apps/org.gemtext.editor.svg \
		$(ICON_DIR)/org.gemtext.editor.svg
	sed 's|@SRCDIR@|$(SRCDIR)|g' resources/org.gemtext.editor.desktop \
		> /tmp/org.gemtext.editor.desktop
	install -Dm644 /tmp/org.gemtext.editor.desktop \
		$(APP_DIR)/org.gemtext.editor.desktop
	rm /tmp/org.gemtext.editor.desktop
	gtk-update-icon-cache -f -t $(PREFIX)/share/icons/hicolor 2>/dev/null || true
	update-desktop-database $(APP_DIR) 2>/dev/null || true
	@echo "Done. Find it in your application menu or run: python3 src/main.py"

uninstall:
	@echo "Uninstalling Gemtext Editor..."
	rm -f $(ICON_DIR)/org.gemtext.editor.svg
	rm -f $(APP_DIR)/org.gemtext.editor.desktop
	gtk-update-icon-cache -f -t $(PREFIX)/share/icons/hicolor 2>/dev/null || true
	update-desktop-database $(APP_DIR) 2>/dev/null || true
	@echo "Done."
