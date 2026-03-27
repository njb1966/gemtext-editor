import gi

gi.require_version("Gtk", "4.0")
gi.require_version("GtkSource", "5")
from gi.repository import Gtk, GtkSource, Gdk, GObject

from pathlib import Path

RESOURCES_DIR = Path(__file__).parent.parent / "resources"


class EditorPanel(Gtk.Box):
    """Center panel: GtkSourceView editor for .gmi files."""

    __gsignals__ = {
        # Emitted when dirty state changes; bool = is_dirty
        "dirty-changed": (GObject.SignalFlags.RUN_FIRST, None, (bool,)),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self._file_path: Path | None = None
        self._build_ui()

    def _build_ui(self):
        # Register resources dir so gemtext.lang is discoverable
        lang_manager = GtkSource.LanguageManager.get_default()
        search_paths = list(lang_manager.get_search_path())
        resources_str = str(RESOURCES_DIR)
        if resources_str not in search_paths:
            search_paths.insert(0, resources_str)
            lang_manager.set_search_path(search_paths)

        self._buffer = GtkSource.Buffer()
        language = lang_manager.get_language("gemtext")
        if language:
            self._buffer.set_language(language)
        self._buffer.connect("changed", self._on_buffer_changed)

        self._view = GtkSource.View(buffer=self._buffer)
        self._view.set_show_line_numbers(True)
        self._view.set_monospace(True)
        self._view.set_tab_width(4)
        self._view.set_hexpand(True)
        self._view.set_vexpand(True)

        # Ctrl+S to save
        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.connect("key-pressed", self._on_key_pressed)
        self._view.add_controller(key_ctrl)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        scrolled.set_child(self._view)
        self.append(scrolled)

    # --- signal handlers ---

    def _on_buffer_changed(self, _buffer):
        self.emit("dirty-changed", True)

    def _on_key_pressed(self, _controller, keyval, _keycode, state):
        if keyval == Gdk.KEY_s and (state & Gdk.ModifierType.CONTROL_MASK):
            self.save_file()
            return True
        return False

    # --- public API ---

    def load_file(self, file_path: str):
        path = Path(file_path)
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as e:
            self._show_error(f"Cannot open file:\n{e}")
            return

        self._file_path = path
        # Block changed signal while loading to avoid a false dirty notification
        self._buffer.handler_block_by_func(self._on_buffer_changed)
        self._buffer.set_text(content)
        self._buffer.handler_unblock_by_func(self._on_buffer_changed)
        self.emit("dirty-changed", False)

    def save_file(self):
        if not self._file_path:
            return
        start = self._buffer.get_start_iter()
        end = self._buffer.get_end_iter()
        content = self._buffer.get_text(start, end, include_hidden_chars=True)
        try:
            self._file_path.write_text(content, encoding="utf-8")
            self.emit("dirty-changed", False)
        except OSError as e:
            self._show_error(f"Cannot save file:\n{e}")

    def get_text(self) -> str:
        start = self._buffer.get_start_iter()
        end = self._buffer.get_end_iter()
        return self._buffer.get_text(start, end, include_hidden_chars=True)

    @property
    def buffer(self) -> GtkSource.Buffer:
        return self._buffer

    @property
    def file_path(self) -> Path | None:
        return self._file_path

    # --- helpers ---

    def _show_error(self, message: str):
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text=message,
        )
        dialog.connect("response", lambda d, _: d.destroy())
        dialog.present()
