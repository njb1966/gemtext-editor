import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Pango

from gemtext_parser import parse_gemtext


class PreviewPanel(Gtk.Box):
    """Right panel: read-only live Gemtext renderer."""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self._build_ui()

    def _build_ui(self):
        self._buffer = Gtk.TextBuffer()
        self._create_tags()

        self._view = Gtk.TextView(buffer=self._buffer)
        self._view.set_editable(False)
        self._view.set_cursor_visible(False)
        self._view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self._view.set_left_margin(16)
        self._view.set_right_margin(16)
        self._view.set_top_margin(12)
        self._view.set_bottom_margin(12)
        self._view.set_hexpand(True)
        self._view.set_vexpand(True)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        scrolled.set_child(self._view)
        self.append(scrolled)

    def _create_tags(self):
        self._buffer.create_tag("heading1",
            weight=Pango.Weight.BOLD, scale=1.8)
        self._buffer.create_tag("heading2",
            weight=Pango.Weight.BOLD, scale=1.4)
        self._buffer.create_tag("heading3",
            weight=Pango.Weight.BOLD, scale=1.15)
        self._buffer.create_tag("link",
            foreground="#4a90d9",
            underline=Pango.Underline.SINGLE)
        self._buffer.create_tag("list",
            left_margin=20)
        self._buffer.create_tag("quote",
            style=Pango.Style.ITALIC,
            left_margin=20,
            foreground="#888888")
        self._buffer.create_tag("preformatted",
            family="Monospace",
            background="#f0f0f0",
            left_margin=12,
            right_margin=12)

    def render(self, content: str):
        """Parse and render gemtext content into the preview buffer."""
        self._buffer.set_text("")

        parsed = parse_gemtext(content)
        first = True

        for item in parsed:
            line_type = item["type"]

            if line_type == "preformatted_toggle":
                continue  # Don't render the ``` markers themselves

            if not first:
                self._insert("\n")
            first = False

            if line_type == "link":
                self._insert(f"→ {item['label']}", "link")

            elif line_type == "heading1":
                self._insert(item["content"], "heading1")

            elif line_type == "heading2":
                self._insert(item["content"], "heading2")

            elif line_type == "heading3":
                self._insert(item["content"], "heading3")

            elif line_type == "list":
                self._insert(f"• {item['content']}", "list")

            elif line_type == "quote":
                self._insert(f"❝ {item['content']}", "quote")

            elif line_type == "preformatted":
                self._insert(item["content"], "preformatted")

            else:  # text
                self._insert(item["content"])

    def _insert(self, text: str, *tag_names: str):
        """Insert text at end of buffer, optionally with named tags."""
        end = self._buffer.get_end_iter()
        if tag_names:
            self._buffer.insert_with_tags_by_name(end, text, *tag_names)
        else:
            self._buffer.insert(end, text)
