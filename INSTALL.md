# Installation

## Dependencies

Gemtext Editor requires Python 3.11+ and the following system packages.

### Debian / Ubuntu

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-gtksource-5
```

### Fedora

```bash
sudo dnf install python3-gobject gtk4 gtksourceview5
```

### Arch Linux

```bash
sudo pacman -S python-gobject gtk4 gtksourceview5
```

No pip dependencies. No build step.

---

## Installing

Clone the repository and run `make install` from the project root:

```bash
git clone <repo-url>
cd gemtext-editor
make install
```

This installs:

| File | Destination |
|------|-------------|
| Application icon | `~/.local/share/icons/hicolor/scalable/apps/org.gemtext.editor.svg` |
| Desktop entry | `~/.local/share/applications/org.gemtext.editor.desktop` |

No root access required. The app runs directly from the cloned directory — do not move or delete it after installing.

After installation the app will appear in your application menu. You can also continue running it directly:

```bash
python3 src/main.py
```

---

## Uninstalling

```bash
make uninstall
```

This removes the icon and desktop entry. The cloned repository itself is not touched — delete it manually if you no longer need it.

---

## Notes

- The desktop entry bakes in the path to the project at install time. If you move the project folder, re-run `make install` from the new location.
- `make install` must be run from the project root directory.
