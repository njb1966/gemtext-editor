import sys
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio

from window import AppWindow


class GemtextEditorApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="org.gemtext.editor",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )

    def do_activate(self):
        win = self.get_active_window()
        if not win:
            win = AppWindow(application=self)
        win.present()


def main():
    app = GemtextEditorApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
