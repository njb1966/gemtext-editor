# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Native Linux GTK4 application for editing Gemini capsule content (.gmi files). Three-panel layout: file tree (left), text editor with syntax highlighting (center), live Gemtext preview (right).

**Stack**: Python 3.11+, GTK4 via PyGObject, GtkSourceView 5, Debian Linux target.

## Setup

Install system dependencies:
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-gtksource-5
```

Optional venv for PyGObject (system packages preferred on Debian):
```bash
python3 -m venv venv && source venv/bin/activate
pip install PyGObject
```

## Running

```bash
python3 src/main.py
```

No build step. No test framework defined yet — testing is manual (see PLAN.md checklist).

## Architecture

The app follows GTK's Model-View pattern with `Gtk.Application` managing lifecycle.

**`src/main.py`** — Entry point. Creates `Gtk.Application`, connects `activate` signal to instantiate `AppWindow`.

**`src/window.py`** — `AppWindow(Gtk.ApplicationWindow)`. Owns the three-panel layout via nested `Gtk.Paned` widgets (default: left=250px, right=400px, total=1400x900). Holds application state: current project path, current open file path, dirty flag. Wires together all sub-components.

**`src/file_tree.py`** — File tree sidebar. Uses `Gtk.TreeView`/`Gtk.ColumnView` with `Gtk.TreeListModel`. Filters to show only folders and `.gmi` files. "Open Folder" button sets project root. Double-click emits signal to open file in editor.

**`src/editor.py`** — `GtkSource.View` with `gemtext.lang` syntax highlighting, line numbers, monospace font. Tracks dirty state; updates window title with `*` prefix when modified. Ctrl+S saves via `Gio.File`.

**`src/gemtext_parser.py`** — Pure function `parse_gemtext(content: str) -> list[dict]`. Returns list of `{type, content}` dicts. Types: `link`, `heading1`, `heading2`, `heading3`, `list`, `quote`, `preformatted`, `text`. No GTK dependencies.

**`src/preview.py`** — Renders parser output. Uses `Gtk.TextView` with `TextTag`s for styled rendering (or optionally `WebKit2.WebView` for HTML). Debounce live updates on editor change events.

**`src/file_operations.py`** — CRUD functions for files/folders using `pathlib.Path`. Called by file tree context menu (right-click: New File, New Folder, Rename, Delete). All destructive ops show confirmation dialogs.

**`src/config.py`** — Application constants and configuration (window size, pane positions, font settings).

**`resources/gemtext.lang`** — GtkSourceView language definition for `.gmi` syntax highlighting. Defines patterns for `=>` links, `#`/`##`/`###` headings, `*` lists, triple-backtick preformatted blocks, `>` quotes.

## Key Implementation Notes

- Use `Gio.File` for all file I/O (async-friendly, handles encoding)
- Use `pathlib.Path` for path manipulation
- Signal connections: comment complex GTK signal wiring; disconnect when widgets are destroyed
- Preview debouncing: connect to `GtkSource.Buffer::changed`, use `GLib.timeout_add` to debounce
- Gemtext spec: line-oriented format — each line's type is determined solely by its prefix character(s)
- File tree must filter non-`.gmi` files; folders always shown
- State lives in `AppWindow` instance, passed down to components via signals or direct references

## Implementation Phases

See PLAN.md for full acceptance criteria per phase:
1. Basic window + three-panel layout
2. File tree panel
3. Text editor with syntax highlighting
4. Gemtext preview (live)
5. File operations (CRUD via context menu)
6. Polish + keyboard shortcuts (Ctrl+S/N/O/Q, status bar, unsaved-changes warning)
7. MVP manual testing
