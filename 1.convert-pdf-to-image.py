import fitz
import os

dpi = 300
zoom = dpi/72
magnify = fitz.Matrix(zoom, zoom)

input_folder = "E:/Works/narendra_tasks/invoice-ocr/docai/pocr/template_data/invoice-templates-pdf"
output_folder = "E:/Works/narendra_tasks/invoice-ocr/docai/pocr/template_data/invoice-templates-images"

#input_folder = "E:/Works/narendra_tasks/invoice-ocr/sample_bills_bakcup19Nov23"
#output_folder = "E:/Works/narendra_tasks/invoice-ocr/sample_bills_bakcup19Nov23/bill-images"

#input_folder = "E:/Works/narendra_tasks/invoice-ocr/sample_bills/FW Electricity Bills of Various Vendors"
#output_folder = "E:/Works/narendra_tasks/invoice-ocr/sample_bills/FW Electricity Bills of Various Vendors/process"

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(input_folder, filename)

        doc = fitz.open(pdf_path)

        for page_num, page in enumerate(doc):
            count = page_num + 1
            pix = page.get_pixmap(matrix=magnify)
            output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_page_{count}.png")
            pix.save(output_path)

        doc.close()