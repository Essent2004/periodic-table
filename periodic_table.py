
"""
Timo van Essen  3755069
Premaster Biomedical engineeering
periodic table assagnment

Loads ellements and information form CSV file. whnen the files reads. it draws a periodic table.
The table is codes so its interactive, user can click on different elements to see information.
"""
import csv
import glob
import os
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

# Configurations section
# The values below are used to configure the appearance of the periodic table visualization.
FIGURE_WIDTH = 14  # Width of the figure
FIGURE_HEIGHT = 8  # Height of the figure
MAX_GROUPS = 18  # Max number of columns in the periodic table
MAX_PERIODS = 7  # Max number rows in the periodic table
TEXT_SIZE = 10                # Text size for element symbols and numbers
BOX_COLOR = "lightblue"      # Background color of each element box
BOX_BORDER_COLOR = "black"   # Border color of each element box


CSV_FILENAME = "Periodic Table of Elements.csv"  # CSV file name with periodic table data

# This function tries to find the CSV file. It looks first in the same folder
# as the script, then searches all subfolders. It returns the full file path.
def csv_path(filename: str) -> str:
    """Returns path to CSV next to this script or other subfolders."""
    script = os.path.dirname(os.path.abspath(__file__))
    # Check CSV in same folder
    direct_path = os.path.join(script, filename)
    if os.path.isfile(direct_path):
        return direct_path
    pattern = os.path.join(script, "**", filename)
    # Check all subfolders
    matches = glob.glob(pattern, recursive=True)
    if matches:
        return matches[0]
    return filename

# Reads the CSV file and loads every element as a dictionary.
# Each element dictionary contains:
# atomic number, symbol, period (row), name, group (column), flags for metal / nonmetal
def lezen(filename: str) -> list:
    """Read the CSV and return a list of element dictionaries."""
    elements = []
    filename = csv_path(filename)
    # Read CSV as a list of dictionarie
    with open(filename, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                element = {
                    "number": int(row["AtomicNumber"]),
                    "name": row["Element"],
                    "symbol": row["Symbol"],
                   "period": int(float(row["Period"])),
                    "group": int(float(row["Group"])),
                     "is_nonmetal": (row.get("Nonmetal", "").lower() == "yes"),
                    "is_metal": (row.get("Metal", "").lower() == "yes"),
                }
                elements.append(element)
            except (ValueError, KeyError):
                # dont read rows with missing or invalid data
                continue
    return elements

# Draws the full table using matplotlib.
# its drawed with the values from the config section.
# Metals are yellow, nonmetals red, others blue.
# Clicking an element shows a small pop-up window with information.
def teken_table(elements: list) -> None:
    """Draw the interactive periodic table and enable click popups."""
    fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))

    pos_to_element = {}
    texts = []
    # Draw each element box
    for el in elements:
        group = el["group"]  # Column
        period = el["period"]  # Row

        # Determine box color based on element type
        if el.get("is_nonmetal"):
            face = "lightcoral"  # red
        elif el.get("is_metal"):
            face = "khaki"       # yellow
        else:
            face = BOX_COLOR
        # Draw the text box for the element
        txt = ax.text(
            group,
            -period,
            f"{el['symbol']}\n{el['number']}",
            ha="center",
            va="center",
            fontsize=TEXT_SIZE,
            bbox=dict(facecolor=face, edgecolor=BOX_BORDER_COLOR, boxstyle="round,pad=0.3"),
            picker=True,    # allow picking
        )
        texts.append(txt)
        pos_to_element[(group, -period)] = el
    # Set axis limits and labels
    ax.set_ylim(-MAX_PERIODS - 0.5, -0.5)
    ax.set_xlim(0.5, MAX_GROUPS + 0.5)
    ax.set_yticks([-p for p in range(1, MAX_PERIODS + 1)])
    ax.set_xticks(range(1, MAX_GROUPS + 1))
    ax.set_yticklabels(range(1, MAX_PERIODS + 1))  # Make period numbers positive
    ax.set_ylabel("Period")
    ax.set_title("Periodic Table of Elements")
    ax.set_xlabel("Group")
    # Add cursor for visualization of mouse when clickend on element
    Cursor(ax, useblit=True, color="gray", linewidth=1)
        # Annotation box for displaying element info
    annot = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(10, 10),
         bbox=dict(boxstyle="round", fc="w", ec="0.5"),
        arrowprops=dict(arrowstyle="->"),
        textcoords="offset points",
    )
    annot.set_visible(False)

    # Function to update and show information on click
    def informatie(event) -> None:
        """Handle mouse clicks and show/hide the info annotation."""
        if event.inaxes != ax:
            return
        gy = round(event.ydata)
        gx = round(event.xdata)
        key = (gx, gy)
        el = pos_to_element.get(key)

        # If direct lookup fails, check each text box
        if not el:
            for txt in texts:
                contains, _ = txt.contains(event)
                if contains:
                    x, y = txt.get_position()
                    el = pos_to_element.get((x, y))
                    key = (x, y)
                    break

        # Position information on clicked element
        if el:
            annot.xy = (key[0], key[1])
            middle = MAX_GROUPS // 2
            # Adjust  information text box position based on element location
            if key[0] > middle + 2:             # Right side of the table
                annot.set_position((-40, 0))
                annot.set_ha("right")
                annot.set_va("center")
            elif abs(key[0] - middle) <= 2:     # Middle of the table
                annot.set_position((0, 30))
                annot.set_ha("center")
                annot.set_va("bottom")
            else:                               # Left side of the table
                annot.set_position((40, 0))
                annot.set_ha("left")
                annot.set_va("center")
            # Set the text for the information box
            annot.set_text(
                f"{el['name']} ({el['symbol']})\n"
                f"Atomic number: {el['number']}\n"
                f"Group: {el['group']}  Period: {el['period']}"
            )
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            # Hide annotation on right-click outside elements
            if event.button == 3:
                annot.set_visible(False)
                fig.canvas.draw_idle()
    # Connect the click event to the informatie function
    fig.canvas.mpl_connect("button_press_event", informatie)

    plt.tight_layout()
    plt.show()
# The "main" function runs first when the script is executed directly.
# It loads the CSV, prints status messages and draws the periodic table.
def main() -> None:
    """Entry point: load CSV| render table| print short status messages."""
    print("Loading data of periodic table")
    elements =lezen(CSV_FILENAME)
    print(f"Loaded {len(elements)} elements.")
    print("draw periodic table")
    teken_table(elements)

# Run the program if this file is launched directly
if __name__ == "__main__":
    main()
