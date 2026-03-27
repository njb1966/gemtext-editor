# Gemtext Editor

A native Linux GTK4 desktop application for editing Gemini capsule content (`.gmi` files).

Three-panel layout: file tree, syntax-highlighted editor, and live preview — all in one window.

## Features

- **File tree** — browse folders, filter to `.gmi` files only; right-click for New File, New Folder, Rename, Delete
- **Syntax highlighting** — GtkSourceView with a custom Gemtext language definition (links, headings, lists, quotes, preformatted blocks)
- **Live preview** — rendered Gemtext updates as you type (300ms debounce)
- **Dark mode** — toggle via the hamburger menu; preformatted blocks render in cyan against the dark background
- **Keyboard shortcuts** — Ctrl+S save, Ctrl+N new file, Ctrl+O open folder, Ctrl+Q quit
- **Unsaved changes warning** — prompted to save, discard, or cancel before closing

## Requirements

Debian/Ubuntu system packages:

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-gtksource-5
```

No pip dependencies. No build step.

## Running

```bash
python3 src/main.py
```

## Editing Files on a Remote Server

Mount the server locally with SSHFS, then open the mount point as your project folder:

```bash
sudo apt install sshfs
mkdir -p ~/mounts/mycapsule
sshfs user@192.168.x.x:/path/to/capsule ~/mounts/mycapsule
```

To mount automatically on login, create a systemd user service:

```bash
# ~/.config/systemd/user/capsule-mount.service
[Unit]
Description=Mount capsule server via SSHFS
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/sshfs user@192.168.x.x:/path/to/capsule /home/USER/mounts/mycapsule \
  -o reconnect,ServerAliveInterval=15,IdentityFile=/home/USER/.ssh/id_rsa
ExecStop=/usr/bin/fusermount -u /home/USER/mounts/mycapsule

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now capsule-mount.service
loginctl enable-linger $USER   # mount at boot, not just login
```

## Project Structure

```
src/
  main.py             # Gtk.Application entry point
  window.py           # AppWindow: layout, actions, keyboard shortcuts
  file_tree.py        # File tree panel with context menu CRUD
  editor.py           # GtkSource.View editor, dirty tracking, save
  gemtext_parser.py   # Pure parser: gemtext string → list of typed dicts
  preview.py          # Read-only Gtk.TextView renderer with TextTags
  file_operations.py  # pathlib-based file/folder CRUD (no GTK)
  config.py           # (reserved for future configuration)
resources/
  gemtext.lang        # GtkSourceView language definition for .gmi files
```
