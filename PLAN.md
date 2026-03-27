## Implementation Phases
Phase 1: Basic Window and Layout
Goal: Create three-panel layout with GTK4

## Files to create:

src/main.py - GTK application setup
src/window.py - Main window with Gtk.Paned for three columns
Specifications:

Use Gtk.ApplicationWindow as main window
Use nested Gtk.Paned widgets to create three resizable panels
Set default window size: 1400x900
Set default pane positions: left=250px, right=400px
Acceptance criteria:

Application launches
Three empty panels are visible
Panels are resizable with mouse

## Phase 2: File Tree Panel
Goal: Display folder structure and allow navigation

Files to create/modify:

src/file_tree.py - Implement file tree widget
src/window.py - Integrate file tree into left panel
Specifications:

Use Gtk.TreeView or Gtk.ColumnView with Gtk.TreeListModel
Show folders and .gmi files only (filter other files)
Display folder icons vs file icons
Single-click to select, double-click to open file
"Open Folder" button at top to choose project root
Store current project path in application state
Acceptance criteria:

Can select a folder as project root
File tree displays folders and .gmi files
Double-clicking a .gmi file triggers "open file" event

## Phase 3: Text Editor Panel
Goal: Edit Gemtext files with syntax highlighting

Files to create/modify:

src/editor.py - Text editor component
resources/gemtext.lang - Syntax highlighting definition
src/window.py - Integrate editor into center panel
Specifications:

Use GtkSource.View for editor
Load gemtext.lang for syntax highlighting
Show line numbers
Use monospace font
Ctrl+S to save current file
Track "dirty" state (unsaved changes)
Gemtext syntax highlighting rules:

Links (lines starting with =>) - blue
Headings (lines starting with #, ##, ###) - bold
List items (lines starting with *) - normal
Preformatted blocks (between ```  markers) - gray background ```
Quotes (lines starting with >) - italic
Regular text - default
Acceptance criteria:

Opening a file loads its content into editor
Syntax highlighting works for Gemtext
Ctrl+S saves the file
Window title shows asterisk (*) when file is modified

## Phase 4: Gemtext Preview Panel
Goal: Live rendering of Gemtext as you type

Files to create/modify:

src/gemtext_parser.py - Parse .gmi format
src/preview.py - Render parsed Gemtext
src/window.py - Integrate preview into right panel
Specifications:

Use Gtk.TextView with TextTags for styled rendering (OR use WebKit2.WebView for HTML rendering)
Parse editor content on every change (debounce if needed)
Render Gemtext according to spec:
Links: Show URL and optional text
Headings: Larger text, bold
Preformatted: Monospace, preserve whitespace
Quotes: Indented, italic
Lists: Bullet points
Regular text: Normal paragraph
Gemtext Parser (gemtext_parser.py):
def parse_gemtext(content: str) -> list[dict]:
    """
    Parse gemtext content into list of line objects.
    
    Returns:
        List of dicts with 'type' and 'content' keys
        Types: 'link', 'heading1', 'heading2', 'heading3', 
               'list', 'quote', 'preformatted', 'text'
    """
Acceptance criteria:

Preview updates as you type
All Gemtext line types render correctly
Preview scrolls independently from editor

## Phase 5: File Operations
Goal: Create, delete, rename files and folders

Files to create/modify:

src/file_operations.py - CRUD functions
src/file_tree.py - Add context menu
Specifications:

Right-click on file tree shows context menu:
"New File..." (in selected folder)
"New Folder..." (in selected folder)
"Rename..."
"Delete"
Operations show confirmation dialogs where appropriate
File tree refreshes after operations
Create new files with .gmi extension by default
Acceptance criteria:

Can create new .gmi files
Can create new folders
Can rename files/folders
Can delete files/folders
Confirmation dialog appears before delete
File tree updates reflect changes immediately

## Phase 6: Polish and Keyboard Shortcuts
Goal: Improve UX with shortcuts and warnings

Specifications:

Keyboard shortcuts:
Ctrl+S - Save current file
Ctrl+N - New file
Ctrl+O - Open folder
Ctrl+Q - Quit application
Warn before closing window with unsaved changes
Show status bar with current file path
Add basic application menu
Acceptance criteria:

All shortcuts work
Unsaved changes warning prevents accidental data loss
Status bar shows current file

## Code Guidelines
GTK Best Practices
Use Gtk.Application instead of raw window management
Connect signals properly and disconnect when needed
Use Gio.File for file operations (async-friendly)
Follow GTK's Model-View pattern
Python Style
Follow PEP 8
Type hints for function signatures
Docstrings for public functions
Keep functions small and focused
Error Handling
Catch file I/O errors gracefully
Show error dialogs to user for failures
Log errors for debugging
State Management
Current project folder path
Currently opened file path
Dirty (unsaved) state per file
Store in simple class or dict

## Testing Approach
Manual Testing Checklist

Open a folder containing .gmi files
File tree displays correctly
Open a .gmi file
Edit the file, preview updates
Save the file (Ctrl+S)
Create a new file
Create a new folder
Rename a file
Delete a file
Close with unsaved changes (should warn)
Reopen, changes are saved

## Edge Cases
Empty folders
Very long file names
Files without .gmi extension in project folder
Invalid Gemtext syntax
Read-only files/folders

## Future Enhancements (Not for MVP)
Preferences dialog (font, theme)
Recent projects list
Find in file (Ctrl+F)
Multiple file tabs
Dark mode toggle

## Getting Started
Initial Development Command
bash
mkdir -p gemtext-editor/src gemtext-editor/resources
cd gemtext-editor
python3 -m venv venv
source venv/bin/activate
pip install PyGObject

## Running the Application
bash
python3 src/main.py

## Implementation Notes for Claude
When implementing:

Start with Phase 1, get the window structure working first
Test each phase before moving to the next
Keep functions small and single-purpose
Use GTK's built-in widgets whenever possible (don't reinvent)
Comment complex GTK signal connections
Handle file paths with pathlib.Path for safety
Ask for clarification if:

GTK4 API is unclear
File operation edge cases arise
Preview rendering approach needs decision (TextView vs WebView)
Performance issues with live preview
Remember: Simplicity is key. If a feature feels complex, it might not be needed.

---

This CLAUDE.md gives Claude Code everything needed to implement your editor. You can drop this into your project and start working through the phases. Would you like me to adjust anything in the plan or the implementation guide?
