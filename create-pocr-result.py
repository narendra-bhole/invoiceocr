import os
from paddleocr import PaddleOCR
import json
import numpy as np
import hashlib

ocr_model = PaddleOCR(lang='en', use_gpu=False)
def scan_result_():
    input_folder = "E:/Works/narendra_tasks/invoice-ocr/sample_bills_bakcup19Nov23/invoice-templates-images"
    output_folder = "E:/Works/narendra_tasks/invoice-ocr/sample_bills_bakcup19Nov23/invoice-templates-json"

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through image files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(input_folder, filename)

            # Perform OCR on the current image
            result = ocr_model.ocr(image_path)

            # Store the results in a dictionary
            image_results = {
                "image_path": image_path,
                "text_results": result
            }

            # Save the results to a JSON file with the same name as the image
            output_json_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_ocr_result.json")
            with open(output_json_path, "w", encoding="utf-8") as json_file:
                json.dump(image_results, json_file, ensure_ascii=False, indent=4)

            print(f"OCR results for {filename} saved to {output_json_path}")
def scan_result_per_line():
    input_folder = "E:/Works/narendra_tasks/invoice-ocr/sample_bills_bakcup19Nov23/invoice-templates-images"
    output_folder = "E:/Works/narendra_tasks/invoice-ocr/sample_bills_bakcup19Nov23/invoice-templates-json"

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Iterate through image files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(input_folder, filename)
            
            img = np.asarray(image_path)
            image_height, image_width = img.shape[:2]

            data = []
            # Perform OCR on the current image
            print("ocr process start")
            result = ocr_model.ocr(img,cls=False)
            print("ocr process done")

            for i, res in enumerate(result[0]):
                # Store the results in a dictionary
                co_ord = res[0]
                four_co_ord = [co_ord[0][0],co_ord[1][1],co_ord[2][0]-co_ord[0][0],co_ord[2][1]-co_ord[1][1]]
                bbox_normal = {
                'x': 100 * four_co_ord[0] / image_width,
                'y': 100 * four_co_ord[1] / image_height,
                'width': 100 * four_co_ord[2] / image_width,
                'height': 100 * four_co_ord[3] / image_height,
                'rotation': 0
                }
                bbox_normal_str = '_'.join(map(str, bbox_normal))
                region_id = hashlib.sha256(bbox_normal_str.encode()).hexdigest()[:10]

                image_results = {"id": i,"region_id":region_id,"bbox_normal":bbox_normal,"bbox":res[0],"text_result": res[1][0]}
                
                data.append(image_results)
                i += 1
            
            # Save the results to a JSON file with the same name as the image
            output_json_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_ocr_result.json")
            with open(output_json_path, "w", encoding="utf-8") as json_file:
                for item in data:
                    json.dump(item, json_file, ensure_ascii=False)
                    json_file.write("\n")

            print(f"OCR results for {filename} saved to {output_json_path}")

scan_result_per_line()