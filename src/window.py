import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, GLib, Gio, Gdk, Pango

from file_tree import FileTreePanel
from editor import EditorPanel
from preview import PreviewPanel


class AppWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_default_size(1400, 900)

        self.is_dirty: bool = False
        self._preview_timeout_id: int | None = None

        self._build_header()
        self._build_layout()
        self._setup_actions()
        self.connect("close-request", self._on_close_request)

    # -------------------------------------------------------------------------
    # Header bar
    # -------------------------------------------------------------------------

    def _build_header(self):
        header = Gtk.HeaderBar()
        self.set_titlebar(header)

        # Save button (left side)
        self._save_btn = Gtk.Button(icon_name="document-save-symbolic")
        self._save_btn.set_tooltip_text("Save  Ctrl+S")
        self._save_btn.set_sensitive(False)
        self._save_btn.connect("clicked", lambda _: self._editor.save_file())
        header.pack_start(self._save_btn)

        # Hamburger menu (right side)
        menu = Gio.Menu()
        menu.append("New File", "win.new-file")
        menu.append("Open Folder", "win.open-folder")

        section = Gio.Menu()
        section.append("Dark Mode", "win.dark-mode")
        menu.append_section(None, section)

        menu_btn = Gtk.MenuButton()
        menu_btn.set_icon_name("open-menu-symbolic")
        menu_btn.set_menu_model(menu)
        menu_btn.set_tooltip_text("Menu")
        header.pack_end(menu_btn)

    # -------------------------------------------------------------------------
    # Main layout
    # -------------------------------------------------------------------------

    def _build_layout(self):
        root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        outer_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        outer_paned.set_position(250)
        outer_paned.set_vexpand(True)

        inner_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        inner_paned.set_position(750)

        self._file_tree = FileTreePanel()
        self._file_tree.connect("file-activated", self._on_file_activated)

        self._editor = EditorPanel()
        self._editor.connect("dirty-changed", self._on_dirty_changed)
        self._editor.buffer.connect("changed", self._on_editor_buffer_changed)

        self._preview = PreviewPanel()

        inner_paned.set_start_child(self._editor)
        inner_paned.set_end_child(self._preview)

        outer_paned.set_start_child(self._file_tree)
        outer_paned.set_end_child(inner_paned)

        root_box.append(outer_paned)

        # Status bar
        root_box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        self._status_label = Gtk.Label(label="No file open")
        self._status_label.set_xalign(0)
        self._status_label.set_margin_start(8)
        self._status_label.set_margin_end(8)
        self._status_label.set_margin_top(4)
        self._status_label.set_margin_bottom(4)
        self._status_label.set_ellipsize(Pango.EllipsizeMode.START)
        root_box.append(self._status_label)

        self.set_child(root_box)

    # -------------------------------------------------------------------------
    # Actions and keyboard shortcuts
    # -------------------------------------------------------------------------

    def _setup_actions(self):
        app = self.get_application()

        simple_actions = [
            ("open-folder", lambda *_: self._file_tree.trigger_open_folder(), "<Control>o"),
            ("new-file",    lambda *_: self._file_tree.trigger_new_file(),    "<Control>n"),
            ("quit",        lambda *_: self.close(),                           "<Control>q"),
        ]
        for name, handler, accel in simple_actions:
            action = Gio.SimpleAction(name=name)
            action.connect("activate", handler)
            self.add_action(action)
            app.set_accels_for_action(f"win.{name}", [accel])

        # Dark mode — stateful toggle (shows checkmark in menu)
        dark_action = Gio.SimpleAction.new_stateful(
            "dark-mode", None, GLib.Variant.new_boolean(False)
        )
        dark_action.connect("activate", self._on_dark_mode_toggled)
        self.add_action(dark_action)

    # -------------------------------------------------------------------------
    # Signal handlers
    # -------------------------------------------------------------------------

    def _on_file_activated(self, _file_tree, file_path: str):
        self._editor.load_file(file_path)
        self._save_btn.set_sensitive(True)
        self._update_title(file_path, dirty=False)
        self._status_label.set_label(file_path)
        self._preview.render(self._editor.get_text())

    def _on_dirty_changed(self, _editor, is_dirty: bool):
        self.is_dirty = is_dirty
        file_path = str(self._editor.file_path) if self._editor.file_path else None
        self._update_title(file_path, dirty=is_dirty)

    def _on_editor_buffer_changed(self, _buffer):
        if self._preview_timeout_id is not None:
            GLib.source_remove(self._preview_timeout_id)
        self._preview_timeout_id = GLib.timeout_add(300, self._do_preview_update)

    def _on_dark_mode_toggled(self, action, _param):
        current = action.get_state().get_boolean()
        new_state = not current
        action.set_state(GLib.Variant.new_boolean(new_state))
        Gtk.Settings.get_default().set_property(
            "gtk-application-prefer-dark-theme", new_state
        )
        self._preview.set_dark_mode(new_state)

    def _on_close_request(self, _window) -> bool:
        if not self.is_dirty:
            return False

        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.NONE,
            text="You have unsaved changes.",
            secondary_text="Save before closing?",
        )
        dialog.add_button("Discard", Gtk.ResponseType.NO)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Save", Gtk.ResponseType.YES)
        dialog.set_default_response(Gtk.ResponseType.YES)

        def on_response(d, response):
            d.destroy()
            if response == Gtk.ResponseType.YES:
                self._editor.save_file()
                self.destroy()
            elif response == Gtk.ResponseType.NO:
                self.destroy()

        dialog.connect("response", on_response)
        dialog.present()
        return True

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _do_preview_update(self) -> bool:
        self._preview.render(self._editor.get_text())
        self._preview_timeout_id = None
        return False

    def _update_title(self, file_path: str | None, dirty: bool):
        if file_path:
            name = file_path.split("/")[-1]
            prefix = "* " if dirty else ""
            self.set_title(f"{prefix}{name} — Gemtext Editor")
        else:
            self.set_title("Gemtext Editor")
