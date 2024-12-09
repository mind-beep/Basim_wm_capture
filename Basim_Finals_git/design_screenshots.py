import tkinter as tk

def create_watermark(symbol=None):
    """
    Create a watermark overlay with evenly spaced symbols of equal size.

    Args:
        symbol (str): A single symbol to use for the watermark. Defaults to random symbols.
    """
    # Create a transparent overlay window
    root = tk.Tk()
    root.title("Symbol Watermark")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}")  # Cover the whole screen
    root.attributes('-topmost', True)  # Keep on top
    root.attributes('-alpha', 0.3)  # Set transparency
    root.overrideredirect(True)  # Remove window borders

    # Set up a canvas to place the watermark
    canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg="white", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    # Define symbols
    if symbol is None:
        symbols = ["★", "☂", "☀", "♠", "♥", "♣", "♦", "♪", "♫", "✈", "☯"]
    else:
        symbols = [symbol]

    # Define grid parameters
    num_rows = 11  # Number of rows for the grid
    num_cols = 11  # Number of columns for the grid
    cell_width = screen_width // num_cols
    cell_height = screen_height // num_rows
    font_size = min(cell_width, cell_height) // 2  # Adjust font size to fit the cell

    # Place symbols at the center of each grid cell
    for row in range(num_rows):
        for col in range(num_cols):
            x = cell_width * col + cell_width // 2
            y = cell_height * row + cell_height // 2
            chosen_symbol = symbols[(row * num_cols + col) % len(symbols)]  # Cycle through symbols
            font_style = ("Arial", font_size, "bold")
            canvas.create_text(x, y, text=chosen_symbol, fill="gray", font=font_style)

    # Keep the window borderless and pass-through
    root.lift()
    root.wm_attributes("-transparentcolor", "white")  # Set white as transparent
    root.after(10, lambda: root.attributes("-disabled", True))  # Allow clicks to pass through

    root.mainloop()

if __name__ == "__main__":
    # Example usage
    # Pass a single symbol to use it exclusively, or leave blank for random symbols
    create_watermark(symbol="♫")  # Example: Musical note symbol
