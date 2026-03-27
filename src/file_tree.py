import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk, GObject

from pathlib import Path
import file_operations


class FileTreePanel(Gtk.Box):
    """Left panel: folder selector and .gmi file tree with context menu."""

    __gsignals__ = {
        # Emitted with the full file path when a .gmi file is double-clicked
        "file-activated": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    COL_ICON = 0
    COL_NAME = 1
    COL_PATH = 2
    COL_IS_DIR = 3

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self._project_root: Path | None = None
        self._context_target: dict | None = None  # {path, is_dir}
        self._folder_dialog: Gtk.FileChooserNative | None = None
        self._build_ui()
        self._build_context_menu()

    # -------------------------------------------------------------------------
    # UI construction
    # -------------------------------------------------------------------------

    def _build_ui(self):
        open_btn = Gtk.Button(label="Open Folder")
        open_btn.connect("clicked", self._on_open_folder_clicked)
        self.append(open_btn)

        # TreeStore columns: icon-name, display-name, full-path, is-dir
        self._store = Gtk.TreeStore(str, str, str, bool)

        self._tree_view = Gtk.TreeView(model=self._store)
        self._tree_view.set_headers_visible(False)
        self._tree_view.connect("row-activated", self._on_row_activated)

        column = Gtk.TreeViewColumn("Files")

        icon_renderer = Gtk.CellRendererPixbuf()
        column.pack_start(icon_renderer, False)
        column.add_attribute(icon_renderer, "icon-name", self.COL_ICON)

        text_renderer = Gtk.CellRendererText()
        column.pack_start(text_renderer, True)
        column.add_attribute(text_renderer, "text", self.COL_NAME)

        self._tree_view.append_column(column)

        # Right-click gesture for context menu
        gesture = Gtk.GestureClick(button=3)
        gesture.connect("pressed", self._on_right_click)
        self._tree_view.add_controller(gesture)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(self._tree_view)
        self.append(scrolled)

    def _build_context_menu(self):
        """Build a Gtk.Popover with buttons for file operations."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_margin_start(4)
        box.set_margin_end(4)
        box.set_margin_top(4)
        box.set_margin_bottom(4)

        for label, handler in [
            ("New File…",    self._on_new_file),
            ("New Folder…",  self._on_new_folder),
            ("Rename…",      self._on_rename),
            ("Delete",       self._on_delete),
        ]:
            btn = Gtk.Button(label=label)
            btn.set_has_frame(False)
            btn.connect("clicked", handler)
            box.append(btn)

        self._context_menu = Gtk.Popover()
        self._context_menu.set_child(box)
        self._context_menu.set_parent(self._tree_view)
        self._context_menu.set_has_arrow(False)

    # -------------------------------------------------------------------------
    # Open folder
    # -------------------------------------------------------------------------

    def _on_open_folder_clicked(self, _button):
        self._folder_dialog = Gtk.FileChooserNative(
            title="Open Project Folder",
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            accept_label="Open",
            cancel_label="Cancel",
        )
        self._folder_dialog.set_transient_for(self.get_root())
        self._folder_dialog.connect("response", self._on_folder_chosen)
        self._folder_dialog.show()

    def _on_folder_chosen(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            folder = dialog.get_file()
            if folder:
                self._project_root = Path(folder.get_path())
                self._populate_tree()
        self._folder_dialog = None

    # -------------------------------------------------------------------------
    # Tree population
    # -------------------------------------------------------------------------

    def _populate_tree(self):
        self._store.clear()
        if self._project_root and self._project_root.is_dir():
            self._add_directory(None, self._project_root)

    def _add_directory(self, parent_iter, directory: Path):
        """Recursively populate the store with folders and .gmi files."""
        try:
            entries = sorted(
                directory.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower()),
            )
        except PermissionError:
            return

        for entry in entries:
            if entry.is_dir():
                row_iter = self._store.append(
                    parent_iter, ["folder", entry.name, str(entry), True]
                )
                self._add_directory(row_iter, entry)
            elif entry.suffix == ".gmi":
                self._store.append(
                    parent_iter,
                    ["text-x-generic", entry.name, str(entry), False],
                )

    # -------------------------------------------------------------------------
    # Public triggers (for keyboard shortcuts in AppWindow)
    # -------------------------------------------------------------------------

    def trigger_open_folder(self):
        """Programmatically open the folder picker."""
        self._on_open_folder_clicked(None)

    def trigger_new_file(self, parent_dir: Path | None = None):
        """Open the new-file dialog for parent_dir (falls back to project root)."""
        parent = parent_dir or self._project_root
        if parent is not None:
            self._show_new_file_dialog(parent)

    # -------------------------------------------------------------------------
    # Row activation (double-click)
    # -------------------------------------------------------------------------

    def _on_row_activated(self, _tree_view, path, _column):
        row_iter = self._store.get_iter(path)
        is_dir = self._store.get_value(row_iter, self.COL_IS_DIR)
        file_path = self._store.get_value(row_iter, self.COL_PATH)
        if not is_dir:
            self.emit("file-activated", file_path)

    # -------------------------------------------------------------------------
    # Right-click / context menu
    # -------------------------------------------------------------------------

    def _on_right_click(self, gesture, _n_press, x, y):
        result = self._tree_view.get_path_at_pos(int(x), int(y))
        if result is None:
            return

        tree_path, _col, _cx, _cy = result
        row_iter = self._store.get_iter(tree_path)
        self._context_target = {
            "path": Path(self._store.get_value(row_iter, self.COL_PATH)),
            "is_dir": self._store.get_value(row_iter, self.COL_IS_DIR),
        }
        self._tree_view.get_selection().select_path(tree_path)

        rect = Gdk.Rectangle()
        rect.x, rect.y, rect.width, rect.height = int(x), int(y), 1, 1
        self._context_menu.set_pointing_to(rect)
        self._context_menu.popup()

    # -------------------------------------------------------------------------
    # Context menu action handlers
    # -------------------------------------------------------------------------

    def _on_new_file(self, _button):
        self._context_menu.popdown()
        if self._context_target is None:
            return
        target = self._context_target["path"]
        parent = target if self._context_target["is_dir"] else target.parent
        self._show_new_file_dialog(parent)

    def _show_new_file_dialog(self, parent: Path):
        def create(name):
            try:
                file_operations.create_file(parent, name)
                self._populate_tree()
            except FileExistsError:
                self._show_error(f"'{name}.gmi' already exists.")
            except OSError as e:
                self._show_error(str(e))

        self._show_name_dialog("New File", "", create)

    def _on_new_folder(self, _button):
        self._context_menu.popdown()
        if self._context_target is None:
            return
        target = self._context_target["path"]
        parent = target if self._context_target["is_dir"] else target.parent

        def create(name):
            try:
                file_operations.create_folder(parent, name)
                self._populate_tree()
            except FileExistsError:
                self._show_error(f"'{name}' already exists.")
            except OSError as e:
                self._show_error(str(e))

        self._show_name_dialog("New Folder", "", create)

    def _on_rename(self, _button):
        self._context_menu.popdown()
        if self._context_target is None:
            return
        path = self._context_target["path"]

        def do_rename(name):
            try:
                file_operations.rename(path, name)
                self._populate_tree()
            except OSError as e:
                self._show_error(str(e))

        self._show_name_dialog("Rename", path.name, do_rename)

    def _on_delete(self, _button):
        self._context_menu.popdown()
        if self._context_target is None:
            return
        path = self._context_target["path"]

        def do_delete():
            try:
                file_operations.delete(path)
                self._populate_tree()
            except OSError as e:
                self._show_error(str(e))

        self._show_confirm_delete(path, do_delete)

    # -------------------------------------------------------------------------
    # Dialog helpers
    # -------------------------------------------------------------------------

    def _show_name_dialog(self, title: str, initial: str, callback):
        """Show a modal input dialog; calls callback(name) on OK."""
        dialog = Gtk.Dialog(title=title, transient_for=self.get_root(), modal=True)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("OK", Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)

        entry = Gtk.Entry(text=initial)
        entry.set_activates_default(True)
        entry.set_margin_start(12)
        entry.set_margin_end(12)
        entry.set_margin_top(8)
        entry.set_margin_bottom(8)

        dialog.get_content_area().append(entry)

        def on_response(d, response):
            name = entry.get_text().strip()
            d.destroy()
            if response == Gtk.ResponseType.OK and name:
                callback(name)

        dialog.connect("response", on_response)
        dialog.present()

    def _show_confirm_delete(self, path: Path, callback):
        """Show a delete confirmation dialog; calls callback() on confirm."""
        text = f"Delete '{path.name}'?"
        secondary = "This will delete the folder and all its contents." if path.is_dir() else ""

        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.NONE,
            text=text,
            secondary_text=secondary or None,
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Delete", Gtk.ResponseType.OK)

        def on_response(d, response):
            d.destroy()
            if response == Gtk.ResponseType.OK:
                callback()

        dialog.connect("response", on_response)
        dialog.present()

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
