#!/usr/bin/env python
# coding: utf-8

from paddleocr import PaddleOCR, draw_ocr
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from shapely.geometry import Polygon
import json
import os

import fitz
import shutil


work_dir = "E:/Works/narendra_tasks/invoice-ocr/docai/pocr"

# ### Read Template Configuration file template_config.json
print("Reading configuration...")
ocr_model = PaddleOCR(lang='en', use_gpu=True)

template_config_file = f"{work_dir}/template_config.json"
with open(template_config_file) as f:
    configdata = json.load(f)


#     - Read PDF 
#     - Convert to Image
#     - Scan all pages/images
# 

# #### Read folder  for pdf and convert to images


processed_folder = f"{work_dir}/processed_files"
temp_dir = f"{work_dir}/temp_files"

def convert_pdf_to_image(temp_dir):
    dpi = 300
    zoom = dpi/72    
    magnify = fitz.Matrix(zoom, zoom)
    file_array = []
    for filename in os.listdir(temp_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(temp_dir, filename)
    
            doc = fitz.open(pdf_path)
    
            for page_num, page in enumerate(doc):
                count = page_num + 1
                pix = page.get_pixmap(matrix=magnify)
                output_path = os.path.join(processed_folder, f"{os.path.splitext(filename)[0]}_page_{count}.png")
                pix.save(output_path)
                file_array.append(f"{os.path.splitext(filename)[0]}_page_{count}.png")
            doc.close()
            shutil.move(pdf_path, f"{processed_folder}/{filename}")
    return file_array

# ----------------------------------------------------

files = os.listdir(temp_dir)
image_files = []
if(len(files)>0):
    image_files = convert_pdf_to_image(temp_dir)
else:
    print("No files to process yet.....")
    exit(1)


print("Processing files: ",image_files)


# #### Loop all converted images - First Page find Template. Template Found - Process all Images for Invoice Fileds extraction
# 
#     Execute Safely - OCR Data
# 

page_data = []
for image_file in image_files:
    image_file_path = f"{processed_folder}/{image_file}"
    # For first page screen search template
    print(image_file_path)
    pimg = Image.open(image_file_path)
    
    pimg = np.asarray(pimg)
    img_height, img_width = pimg.shape[:2]
    ocrdata = ocr_model.ocr(pimg)
    image_result = []
    image_result = {"image":image_file,"ocrdata":ocrdata,"image_height":img_height,"image_width":img_width}
    
    page_data.append(image_result)


import pprint
pprint.pprint(page_data)


# #### Transform core pocr data into normalised bbox

bill_ocr_data = []

for data_dict in page_data:
    transform_data = {}
    image_width = data_dict["image_width"]
    image_height = data_dict["image_height"]
    image = data_dict["image"]
    ocrdata = data_dict["ocrdata"]
    ocr_box = []
    for box, (text, confidence) in ocrdata[0]:
        four_co_ord = [box[0][0],box[1][1],box[2][0]-box[0][0],box[2][1]-box[1][1]]
        target_bbox = {
            'x': 100 * four_co_ord[0] / image_width,
            'y': 100 * four_co_ord[1] / image_height,
            'width': 100 * four_co_ord[2] / image_width,
            'height': 100 * four_co_ord[3] / image_height,
            'rotation': 0
        }
        ocr_box.append({"bbox":target_bbox,"text_result":text})
    
    transform_data["image"] = data_dict["image"]
    transform_data["image_width"] = data_dict["image_width"]
    transform_data["image_height"] = data_dict["image_height"]
    transform_data["ocrdata"] = ocr_box
    bill_ocr_data.append(transform_data)

#pprint.pprint(bill_ocr_data)
#pprint.pprint(bill_ocr_data[1])


# ### Search for Template using keyword search in ocr data


def search_all_keys(target_data, substrings):
    result = all(any(keyword in item['text_result'] for item in target_data) for keyword in substrings)
    return result


for configitem in configdata:
    #for entry in configitem['keywords']:
    substrings = [entry['key'] for entry in configitem['keywords']]
    if search_all_keys(bill_ocr_data[0]['ocrdata'], substrings):
        found_template = configitem.copy()

print(found_template)
if(len(found_template) < 1):
    print("Template not found")
    exit(1)

# #### Load Template Json file having master data for matching fields
# Example : Adani_Commercial_HT_II_page_1.json, Adani_Commercial_HT_II_page_2.json


def calculate_iou(bbox1, bbox2):
  """
  Calculates the Intersection over Union (IoU) between two bounding boxes.

  Args:
      bbox1: A dictionary representing the first bounding box with keys 'x', 'y', 'width', and 'height'.
      bbox2: A dictionary representing the second bounding box with the same keys.

  Returns:
      The IoU value between the two bounding boxes (float).
  """
  # Calculate bottom right coordinates for each bbox
  bbox1_br_x = bbox1['x'] + bbox1['width']
  bbox1_br_y = bbox1['y'] + bbox1['height']
  bbox2_br_x = bbox2['x'] + bbox2['width']
  bbox2_br_y = bbox2['y'] + bbox2['height']

  # Determine intersection coordinates
  xmin = max(bbox1['x'], bbox2['x'])
  ymin = max(bbox1['y'], bbox2['y'])
  xmax = min(bbox1_br_x, bbox2_br_x)
  ymax = min(bbox1_br_y, bbox2_br_y)

  # Calculate intersection area (handle no overlap case)
  intersection_area = 0
  if xmax >= xmin and ymax >= ymin:
    intersection_area = (xmax - xmin) * (ymax - ymin)

  # Calculate union area
  union_area = (bbox1['width'] * bbox1['height']) + (bbox2['width'] * bbox2['height']) - intersection_area

  # Calculate and return IoU
  iou = intersection_area / union_area if union_area > 0 else 0
  return iou

def extract_data(master_data,bill_data):
    annotations = master_data.get("annotations", {})
    for variable_name, master_variable_data in annotations.items():
        for bill_data_item in bill_data:
            target_bbox = bill_data_item["bbox"].copy()
            try:
                if isinstance(master_variable_data['box'], dict):
                    iou = calculate_iou(master_variable_data['box'],target_bbox) 
                    if(iou >= 0.3):
                        print(f"Found: {variable_name}: {bill_data_item['text_result']} == {iou}")
                    elif(0.1 <= iou < 0.3):
                        print("No match found",iou)
                else:
                    print("Not dict box:", master_variable_data)
            except TypeError:
                print("No box found: ",master_variable_data)


template_folder = f"{work_dir}/template_data/master_templates"

for i,json_template in enumerate(found_template['pages']):
    json_file_path = f"{template_folder}/{json_template}"
    master_data = {}
    with open(json_file_path, 'r') as file:
        master_data = json.load(file)
        ### ---- Compare Bill OCR Data (bill_ocr_data[0]['ocrdata']) with Master Veairble Data (data)
        print(f"Extracting using {json_template}")
        #print(bill_ocr_data[i]['ocrdata'])
        extract_data(master_data,bill_ocr_data[i]['ocrdata'])
        

