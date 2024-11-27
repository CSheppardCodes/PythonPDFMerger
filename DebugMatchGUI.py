import tkinter as tk
from tkinter import ttk

# Full list of hardcoded bullet points for testing
bullet_points = [
    "E Summary", "Boxscore", "Test 1", "Test 2", "Test 3"
]

# Full list of hardcoded file names for testing with additional files
file_names = [
    "5054542_Boxscore_7141962.pdf",
    "Test 625", "test 1", "Test 626"
]

def show_matching_gui(bullet_points, file_names, property_name, additional_width=520):
        # Debug statements to print the input values
    print(f"Debug: bullet_points = {bullet_points}")
    print(f"Debug: file_names = {file_names}")
    print(f"Debug: property_name = {property_name}")
    print(f"Debug: additional_width = {additional_width}")
    root = tk.Tk()
    root.title(property_name)

    # Track selected files and combobox variables
    matches = {}
    pre_matched_files = set()
    combo_vars = []
    combo_boxes = []

    # Calculate the maximum width for the dropdown dynamically based on the longest file name
    max_file_length = max(len(file) for file in file_names)
    combo_width = max(20, min(60, max_file_length))  # Limit the width within a range

    # Pre-match function for auto-selection
    def pre_match():
        """Automatically pair bullet points with files if they have an exact substring match."""
        for i, bullet in enumerate(bullet_points):
            lower_bullet = bullet.lower()
            matched_file = None
            for file in file_names:
                if file.lower() not in pre_matched_files and lower_bullet in file.lower():
                    matched_file = file
                    pre_matched_files.add(file)
                    break
            if matched_file:
                combo_vars[i].set(matched_file)

    # Update function to dynamically refresh dropdown options
    def update_dropdown_options():
        """Dynamically update dropdowns to show only unmatched files."""
        selected_files = {var.get() for var in combo_vars if var.get()}
        remaining_files = [file for file in file_names if file not in selected_files]

        for var, combo in zip(combo_vars, combo_boxes):
            current_selection = var.get()
            combo['values'] = [""] + ([current_selection] if current_selection else []) + [file for file in remaining_files if file != current_selection]

    # Create scrollable frame with dynamic height based on screen size
    screen_height = root.winfo_screenheight()
    frame_height = int(screen_height * 0.8)  # Set to 80% of screen height for scrollable area
    frame_width = 600 + additional_width  # Add extra width for scrollbar adjustment

    # Create a canvas with a scrollbar for the bullet points
    canvas = tk.Canvas(root, width=frame_width, height=frame_height)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    # Configure the canvas to scroll the frame
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Bind mouse wheel scrolling to the canvas
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    canvas.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    # Set up labels and dropdowns for each bullet point
    for i, bullet in enumerate(bullet_points):
        label = tk.Label(scrollable_frame, text=bullet, anchor="w", width=40)
        label.grid(row=i, column=0, padx=5, pady=2, sticky="w")

        combo_var = tk.StringVar(value="")
        combo = ttk.Combobox(scrollable_frame, textvariable=combo_var, values=[""] + file_names, width=combo_width, state="readonly")
        combo.grid(row=i, column=1, padx=5, pady=2, sticky="w")

        # Disable mouse wheel scrolling for this dropdown to prevent accidental changes
        combo.bind("<MouseWheel>", lambda e: "break")

        combo_vars.append(combo_var)
        combo_boxes.append(combo)

        combo.bind("<<ComboboxSelected>>", lambda e: update_dropdown_options())

    # Run pre-match to auto-fill dropdowns and update dropdown options immediately
    pre_match()
    update_dropdown_options()

    # Submit function to collect matches
    def on_submit():
        for i, bullet in enumerate(bullet_points):
            matches[bullet] = combo_vars[i].get()
        print("Matched Files:")
        for bullet, file in matches.items():
            print(f"{bullet}: {file}")
        root.quit()
        root.destroy()

    # Submit button outside scrollable frame
    submit_button = tk.Button(root, text="Submit", command=on_submit)
    submit_button.grid(row=1, column=0, columnspan=2, pady=10)

    # Handle window close event
    def on_close():
        print("Window closed without submission.")
        root.quit()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

    return matches

# Test the GUI with hardcoded values and property name
if __name__ == "__main__":
    property_name = "H Apartment Homes"
    matched_files = show_matching_gui(bullet_points, file_names, property_name, additional_width=520)
    print("Final Matched Files:")
    for bullet, file in matched_files.items():
        print(f"{bullet}: {file}")
