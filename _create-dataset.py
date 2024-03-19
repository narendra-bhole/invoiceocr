import json

def convert_bounding_box(x, y, width, height):
	"""Converts the given bounding box coordinates to the YOLO format.

	Args:
	x: The x-coordinate of the top-left corner of the bounding box.
	y: The y-coordinate of the top-left corner of the bounding box.
	width: The width of the bounding box.
	height: The height of the bounding box.

	Returns:
	A tuple of four coordinates (x1, y1, x2, y2) in the YOLO format.
	"""

	x1 = x
	y1 = y
	x2 = x + width
	y2 = y + height

	return [x1, y1, x2, y2]



####################################### Loading json data ###################################
with open("E:/Works/narendra_tasks/invoice-ocr/docai/aiody/Training_json.json") as f:
    label_studio_data = json.load(f)

final_list = []

for annotated_image in label_studio_data:
    data = {}
    annotation = []

    if len(annotated_image) < 8:
        continue

    for k, v in annotated_image.items():
        word_list = []
        ner_tags_list = []
        bboxes_list = []
        if k == 'id':
            data['id'] = v
            
        if k == 'data':
            data["file_name"] = os.path.basename(v['ocr'])

        if k == 'annotations':
            if v:
                for label_ in v[0].get("result", []):
                    value_dict = label_.get("value", {})
                    
                    if "text" in value_dict:
                        word_list.append(value_dict["text"][0])
                        x, y, w, h = value_dict.get("x", 0), value_dict.get("y", 0), value_dict.get("width", 0), value_dict.get("height", 0)
                        original_w, original_h = label_.get("original_width", {}), label_.get("original_height", {})
                        
                        x1 = int((x * original_w) / 100)
                        y1 = int((y * original_h) / 100)
                        x2 = x1 + int(original_w * w / 100)
                        y2 = y1 + int(original_h * h / 100)
                        coord = [x1, y1, x2, y2]
                        bboxes_list.append(coord)
                        #print(bboxes_list)
                        
                    if "labels" in value_dict:
                        label_id = label2id[value_dict["labels"][0]]
                        ner_tags_list.append(label_id)
                        #print(ner_tags_list)
                        
            data['tokens'] = word_list
            data['bboxes'] = bboxes_list
            data['ner_tags'] = ner_tags_list

    final_list.append(data)


