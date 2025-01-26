import os
import csv
from PyPDF2 import PdfReader

# Base directory where manufacturer folders are located
base_dir = r"C:\Users\hanna\OneDrive\Desktop\Exploded_diagrams"

# Output file to save extracted data
output_file = os.path.join(base_dir, "scraped_data.csv")

# Define a function to extract table data from a PDF
def extract_table_data_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text
            else:
                print(f"No text extracted from page in {pdf_path}")

        # Debug: Print first 500 characters of the extracted text
        print(f"Extracted text from {pdf_path} (first 500 characters):")
        print(text[:500])

        # Extract rows from the table by splitting the text into lines
        rows = text.splitlines()
        data = []
        start_recording = False

        for row in rows:
            # Look for the multilingual header row to start recording
            if "POS CODICE/CODE DESCRIZIONE DESCRIPTION" in row:
                start_recording = True
                continue  # Skip the header row itself

            if start_recording:
                # Attempt to parse the row into columns
                columns = row.split(maxsplit=3)  # Split into at most 4 parts
                if len(columns) == 4:
                    position, code, italian_description, english_description = columns

                    # Validate that the row fits the expected format
                    if position.isalnum() and code.isalnum() and english_description.strip():
                        data.append((position, code, english_description))
                    else:
                        print(f"Skipped invalid row: {row}")

        return data
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return []

# Main function to loop through folders and scrape PDFs
def scrape_exploded_diagrams():
    data = []

    for manufacturer_folder in os.listdir(base_dir):
        manufacturer_path = os.path.join(base_dir, manufacturer_folder)

        if os.path.isdir(manufacturer_path):
            manufacturer_name = manufacturer_folder
            print(f"Processing manufacturer: {manufacturer_name}")

            for file in os.listdir(manufacturer_path):
                if file.lower().endswith(".pdf"):
                    pdf_path = os.path.join(manufacturer_path, file)
                    print(f"Scraping PDF: {pdf_path}")

                    table_data = extract_table_data_from_pdf(pdf_path)

                    for position, code, description in table_data:
                        data.append([manufacturer_name, position, code, description])

    if data:
        # Save data to a CSV file
        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Manufacturer", "Position", "Part Code (MPN)", "Part Description"])
            writer.writerows(data)
        print(f"Scraping complete. Data saved to {output_file}")
    else:
        print("No data found to write to the CSV file.")

if __name__ == "__main__":
    scrape_exploded_diagrams()
