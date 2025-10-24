# tools/apt.py
"""
Mini 'apt' manager for WinTerm.

Commands supported (via check_apt_command):
  - apt list
  - apt search <term>
  - apt install <tool>
  - apt help

The list output is shown in a neat grid/table (columns aligned horizontally and vertically).
"""

from math import ceil
from typing import List
from . import install_tools

# Number of columns to show in the grid for `apt list`. You can change this.
DEFAULT_COLUMNS = 3

def _get_available_names() -> List[str]:
    """Return sorted list of available tool names (strings)."""
    installers = install_tools.available_installers()
    names = sorted(installers.keys())
    return names

def _make_grid(items: List[str], cols: int) -> List[List[str]]:
    """Arrange items into a grid (list of rows), filling rows left-to-right, top-to-bottom."""
    if cols < 1:
        cols = 1
    rows = ceil(len(items) / cols)
    grid = [["" for _ in range(cols)] for _ in range(rows)]
    for idx, item in enumerate(items):
        r = idx % rows
        c = idx // rows
        grid[r][c] = item
    return grid

def _print_grid(items: List[str], cols: int = DEFAULT_COLUMNS):
    """Print items in a neatly aligned grid with the given number of columns."""
    if not items:
        print("No tools available.")
        return

    grid = _make_grid(items, cols)

    # calculate max width for each column
    col_widths = []
    for c in range(len(grid[0])):
        width = 0
        for r in range(len(grid)):
            cell = grid[r][c] if c < len(grid[r]) else ""
            if cell:
                width = max(width, len(cell))
        col_widths.append(width)

    # print rows
    for row in grid:
        row_cells = []
        for c, cell in enumerate(row):
            if not cell:
                row_cells.append(" " * col_widths[c])
            else:
                row_cells.append(cell.ljust(col_widths[c]))
        # join with two spaces to visually separate columns
        print("  ".join(row_cells))

def list_tools(columns: int = DEFAULT_COLUMNS):
    """
    Print available tools in a table/grid.
    :param columns: number of columns in the grid
    """
    names = _get_available_names()
    print("\nAvailable tools:\n")
    _print_grid(names, cols=columns)
    print("")  # trailing newline for spacing

def search_tools(query: str, columns: int = DEFAULT_COLUMNS):
    """
    Search available tools by substring and print matches.
    :param query: substring to search (case-insensitive)
    """
    q = query.strip().lower()
    if not q:
        print("Usage: apt search <term>")
        return
    names = _get_available_names()
    matches = [n for n in names if q in n.lower()]
    if not matches:
        print(f"No tools found matching '{query}'.")
        return
    print(f"\nSearch results for '{query}':\n")
    _print_grid(matches, cols=columns)
    print("")

def _install_tool(tool_name: str):
    """Install the tool by name using the installer available in install_tools.available_installers."""
    installers = install_tools.available_installers()
    key = tool_name.strip().lower()
    if key not in installers:
        print(f"Tool '{tool_name}' not found. Run 'apt list' to see available tools.")
        return
    func = installers[key]
    try:
        ok = func()
        if ok:
            print(f"\n✅ {key} installation completed (or installer launched).")
        else:
            print(f"\n⚠️ {key} could not be installed automatically. Please follow the instructions opened in your browser or run manual steps.")
    except Exception as e:
        print(f"\n❌ Error while installing {key}: {e}")

def apt_help():
    help_text = """
apt - WinTerm mini package manager

Commands:
  apt list
      Show all available tools in a neat table.

  apt search <term>
      Search for tools by name (substring match).

  apt install <tool>
      Attempt to install the given tool (calls the corresponding installer function).

  apt help
      Show this help text.
"""
    print(help_text)

def check_apt_command(raw_input: str):
    """
    Parse and handle apt-like commands.
    Examples:
      apt list
      apt search nmap
      apt install nmap
      apt help
    """
    parts = raw_input.strip().split()
    if len(parts) == 0:
        print("Usage: apt <command>. Try 'apt help'.")
        return

    # when user types exactly "apt" -> show help (or list)
    if len(parts) == 1:
        # show help to be explicit
        apt_help()
        return

    cmd = parts[1].lower()

    if cmd == "list":
        # optional: if user provided a column number, e.g., "apt list 4"
        cols = DEFAULT_COLUMNS
        if len(parts) >= 3 and parts[2].isdigit():
            cols = max(1, int(parts[2]))
        list_tools(columns=cols)
        return

    if cmd == "search":
        if len(parts) < 3:
            print("Usage: apt search <term>")
            return
        query = " ".join(parts[2:])
        search_tools(query)
        return

    if cmd in ("install", "get"):
        if len(parts) < 3:
            print("Usage: apt install <tool>")
            return
        tool_name = " ".join(parts[2:]).strip().lower()
        _install_tool(tool_name)
        return

    if cmd == "help":
        apt_help()
        return

    print(f"apt: unknown command '{cmd}'. Try 'apt help'.")
