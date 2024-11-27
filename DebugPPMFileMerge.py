import os
import PyPDF2
import re
import tkinter as tk
from tkinter import filedialog, ttk
from pdfrw import PdfReader, PdfWriter

# Function to find the MOR folder
def find_mor_folder(start_path):
    current_path = os.path.dirname(start_path)
    while current_path:
        folder_name = os.path.basename(current_path)
        if folder_name == "MOR":
            return current_path
        current_path = os.path.dirname(current_path)
    return None

# Function to find the Table of Contents folder
def find_table_of_contents_folder(mor_path):
    for folder_name in os.listdir(mor_path):
        folder_path = os.path.join(mor_path, folder_name)
        if os.path.isdir(folder_path) and "Table of Contents" in folder_name:
            return folder_path
    return None

# Function to extract bullet points from a PDF
def extract_bullet_points_from_pdf(file_path):
    bullet_points = []
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                points = re.findall(r'^\s* (.+)', text, re.MULTILINE)
                for point in points:
                    trimmed_point = point.strip()
                    if trimmed_point not in bullet_points:
                        bullet_points.append(trimmed_point)
    return bullet_points

# Function to find operations reports
def find_operations_reports(mor_path, property_name, year, month):
    operations_reports_path = os.path.join(mor_path, property_name, year, month, "Operations Reports")
    if not os.path.exists(operations_reports_path):
        print(f'Operations Reports folder not found for {property_name}.')
        return []
    pdf_files = [f for f in os.listdir(operations_reports_path) if f.endswith('.pdf')]
    return pdf_files

# Function to merge PDFs using pdfrw
import os

def merge_pdfs_pdfrw(output_path, pdf_paths_to_merge):
    # Check if output file already exists
    base, ext = os.path.splitext(output_path)
    counter = 1
    new_output_path = output_path

    # Keep modifying output path if it exists
    while os.path.exists(new_output_path):
        new_output_path = f"{base} ({counter}){ext}"
        counter += 1

    # Merge PDFs using pdfrw
    from pdfrw import PdfWriter, PdfReader
    writer = PdfWriter()

    for pdf_path in pdf_paths_to_merge:
        reader = PdfReader(pdf_path)
        writer.addpages(reader.pages)

    # Save to the new_output_path (with numbering if needed)
    writer.write(new_output_path)
    print(f"PDF merged and saved as: {new_output_path}")


# Function to match bullet points with operation reports
def found_bullet_points(order_array, operations_reports):
    matched_bullets = []
    unmatched_bullets = []
    for bullet in order_array:
        matched = False
        for pdf_file in operations_reports:
            pdf_name = os.path.basename(pdf_file)[:-4]
            if bullet.lower() in pdf_name.lower():
                matched_bullets.append(bullet)
                matched = True
                break
        if not matched:
            unmatched_bullets.append(bullet)
    return matched_bullets, unmatched_bullets

import tkinter as tk
from tkinter import ttk
def show_matching_gui(bullet_points, file_names, property_name, additional_width=520):
        # Debug statements to print the input values
    print(f"Debug: bullet_points = {bullet_points}")
    print(f"Debug: file_names = {file_names}")
    print(f"Debug: property_name = {property_name}")
    print(f"Debug: additional_width = {additional_width}")
    root = tk.Tk()
    root.title(property_name)

    matches = {}
    pre_matched_files = set()
    combo_vars = []
    combo_boxes = []

    # Calculate dropdown width based on the longest file name with a limit
    max_file_length = max(len(file) for file in file_names)
    combo_width = max(20, min(60, max_file_length))  # Width range: 20 to 60

    # Pre-match function
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

    # Update function to refresh dropdown options dynamically
    def update_dropdown_options():
        selected_files = {var.get() for var in combo_vars if var.get()}
        remaining_files = [file for file in file_names if file not in selected_files]

        for var, combo in zip(combo_vars, combo_boxes):
            current_selection = var.get()
            combo['values'] = [""] + ([current_selection] if current_selection else []) + [file for file in remaining_files if file != current_selection]

    # Scrollable frame creation with dynamic height
    screen_height = root.winfo_screenheight()
    frame_height = int(screen_height * 0.8)  # 80% of screen height for scrollable area
    frame_width = 600 + additional_width  # Extra width for scrollbar adjustment

    canvas = tk.Canvas(root, width=frame_width, height=frame_height)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    canvas.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    # Dropdown creation for each bullet point
    for i, bullet in enumerate(bullet_points):
        label = tk.Label(scrollable_frame, text=bullet, anchor="w", width=40)
        label.grid(row=i, column=0, padx=5, pady=2, sticky="w")

        combo_var = tk.StringVar(value="")
        combo = ttk.Combobox(scrollable_frame, textvariable=combo_var, values=[""] + file_names, width=combo_width, state="readonly")
        combo.grid(row=i, column=1, padx=5, pady=2, sticky="w")
        combo.bind("<MouseWheel>", lambda e: "break")  # Disable mouse wheel on dropdown
        combo_vars.append(combo_var)
        combo_boxes.append(combo)

        combo.bind("<<ComboboxSelected>>", lambda e: update_dropdown_options())

    # Run pre-match to fill dropdowns automatically
    pre_match()
    update_dropdown_options()

    # Submit function
    def on_submit():
        for i, bullet in enumerate(bullet_points):
            matches[bullet] = combo_vars[i].get()
        print("Matched Files:")
        for bullet, file in matches.items():
            print(f"{bullet}: {file}")
        root.quit()
        root.destroy()

    # Submit button
    submit_button = tk.Button(root, text="Submit", command=on_submit)
    submit_button.grid(row=1, column=0, columnspan=2, pady=10)

    # Close window event
    def on_close():
        print("Window closed without submission.")
        root.quit()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

    return matches


















import re
import os
from PyPDF2 import PdfReader, PdfWriter

def split_pdf_based_on_bottommost_keyword(mor_folder_path, property_name, YYYY, MM, bullet_points):
    # Construct the path for the report.pdf
    
    operations_reports_path = os.path.join(mor_folder_path, property_name, YYYY, MM, "Operations Reports")
    if not os.path.exists(operations_reports_path):
        print(f"Directory not found: {operations_reports_path}")
        return  # Exit the function if the directory doesn't exist

    report_pdf_path = next((os.path.join(operations_reports_path, file) 
                            for file in os.listdir(operations_reports_path) 
                            if file.lower().startswith("report")), None)

    if not report_pdf_path:
        print(f"No report file found in {operations_reports_path}")
        return  # Exit the function if no matching file is found

    # Create the output directory for split PDFs
    output_dir = os.path.join(mor_folder_path, property_name, YYYY, MM, "Operations Reports")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read the PDF
    reader = PdfReader(report_pdf_path)
    current_writer = None
    current_keyword = None
    start_page = None
    page_ranges = []

    # Iterate through each page to find matches
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            # Split the text into lines and reverse to start searching from the bottom
            lines = text.splitlines()[::-1]
            found_keyword = None

            # Search for the first keyword found in the reversed lines
            for line in lines:
                for keyword in bullet_points:
                    if re.search(re.escape(keyword), line, re.IGNORECASE):
                        found_keyword = keyword
                        break
                if found_keyword:
                    break

            # If no keyword is found, use "Not Found" as the keyword
            if not found_keyword:
                found_keyword = "Not Found"

            # If a keyword is found and is different from the current one, handle PDF saving
            if current_writer and current_keyword != found_keyword:
                # Determine the page range format
                if start_page == i - 1:
                    page_range_str = f"Pg {start_page + 1}"
                else:
                    page_range_str = f"Pg {start_page + 1}-{i}"

                # Save the current PDF with the previous keyword and page range
                output_filename = f"{current_keyword} - {page_range_str}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                with open(output_path, "wb") as output_file:
                    current_writer.write(output_file)
                print(f"Created: {output_filename}")
                page_ranges.append((current_keyword, start_page, i))

                # Reset the writer for the new keyword
                current_writer = PdfWriter()
                start_page = i
                current_keyword = found_keyword
            elif not current_writer:  # If no current writer, initialize it for the first keyword match
                current_writer = PdfWriter()
                start_page = i
                current_keyword = found_keyword

            # Add the page to the current writer
            if current_writer:
                current_writer.add_page(page)

    # Save the last matched PDF
    if current_writer:
        # Determine the page range format for the last section
        if start_page == len(reader.pages) - 1:
            page_range_str = f"Pg {start_page + 1}"
        else:
            page_range_str = f"Pg {start_page + 1}-{len(reader.pages)}"

        output_filename = f"{current_keyword} - {page_range_str}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, "wb") as output_file:
            current_writer.write(output_file)
        print(f"Created: {output_filename}")
        page_ranges.append((current_keyword, start_page, len(reader.pages)))

    return page_ranges





# Function to process each property
def process_property(mor_folder_path, property_name, YYYY, MM, cover_page_path, toc_path):
    print(f"Processing property: {property_name}")

    # Step 1: Extract bullet points from the Table of Contents PDF
    bullet_points = extract_bullet_points_from_pdf(toc_path)
    print(f"Bullet points extracted for {property_name}: {bullet_points}")

    # Step 1.5: Split report.pdf if it exists
    split_pdf_based_on_bottommost_keyword(mor_folder_path, property_name, YYYY, MM, bullet_points)

    # Step 2: Find operations reports for the property AFTER splitting
    operations_reports = find_operations_reports(mor_folder_path, property_name, YYYY, MM)

    # Call GUI to allow the user to match bullet points with the operations reports
    matched_files = show_matching_gui(bullet_points, operations_reports, property_name)
    print("Matched files returned from GUI:")
    for bullet, file in matched_files.items():
        print(f"{bullet}: {file}")

    # Step 3: Prepare the list of PDFs to merge
    pdf_paths_to_merge = [cover_page_path, toc_path]
    for bullet, file in matched_files.items():
        if file:
            file_path = os.path.join(mor_folder_path, property_name, YYYY, MM, "Operations Reports", file)
            pdf_paths_to_merge.append(file_path)

    # Step 4: Output path for the merged PDF
    output_folder = os.path.join(mor_folder_path, property_name, YYYY, MM)
    os.makedirs(output_folder, exist_ok=True)
    output_path_pdfrw = os.path.join(output_folder, f"{property_name} {MM}.{YYYY}.pdf")

    # Step 5: Merge using pdfrw
    merge_pdfs_pdfrw(output_path_pdfrw, pdf_paths_to_merge)



# Main function
def main():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(
        title="Select Cover Page Files",
        filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
    )

    if not file_paths:
        print("No files selected.")
        return

    mor_folder_path = find_mor_folder(file_paths[0])
    if not mor_folder_path:
        print("MOR folder not found.")
        return

    parent_folder = os.path.basename(os.path.dirname(file_paths[0]))
    MM = parent_folder[:2]
    YYYY = parent_folder[-4:]

    table_of_contents_folder = find_table_of_contents_folder(mor_folder_path)
    if not table_of_contents_folder:
        print('"Table of Contents" folder not found inside MOR.')
        return

    # Process each selected cover page file
    for cover_page_path in file_paths:
        property_name = os.path.splitext(os.path.basename(cover_page_path))[0]

        # Find corresponding Table of Contents file
        toc_path = os.path.join(table_of_contents_folder, f"{property_name}.pdf")
        if not os.path.exists(toc_path):
            print(f"Table of Contents file not found for {property_name}. Skipping...")
            continue

        # Find operations reports for the property
        # operations_reports = find_operations_reports(mor_folder_path, property_name, YYYY, MM)

        # Process the property
        process_property(mor_folder_path, property_name, YYYY, MM, cover_page_path, toc_path)
        
if __name__ == "__main__":
    main()
