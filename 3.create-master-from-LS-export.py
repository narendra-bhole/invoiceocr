import os
import json
from collections import defaultdict
import pprint

final_list = []
def convert_annotation_to_fund(result):
    data = {}
    # collect all LS results and combine labels, text, coordinates into one record
    for item in result:
        #print(item['meta'])
        if 'id' in item:
            id_val = item['id']
            if id_val not in data:
                #data[id_val] = {}  # Initialize the dictionary if the key doesn't exist
                data[id_val] = {'box': [],'text': '','meta':''}
            
            '''
            labels = item.get('value', {}).get('labels', None)
            if labels:                
                if id_val not in data:
                    data[id_val] = {}
                data[id_val]["label"] = label2id[labels[0]]
            '''

            meta = item.get('meta', None)    
            if meta:
                if id_val not in data:
                    data[id_val] = {}
                data[id_val]['meta'] = meta['text'][0]
            
            text = item.get('value', {}).get('text', None)         
            if text:
                if id_val not in data:
                    data[id_val] = {}
                data[id_val]['text'] = text[0]
            
            if 'box' not in data:
                if id_val not in data:
                    data[id_val] = {}
                w, h = item['original_width'], item['original_height']
                v = item.get('value')
                x = v['x']
                y = v['y']
                width = v['width']
                height = v['height']

                data[id_val]['box'] = {"x":x, "y":y, "width":width, "height":height}
                #data[id_val]['box'] = [item['original_width'], item['original_height'], v['width'], v['height']]
                            
    #pprint.pprint(data)
    
    # make FUNSD output
    output = {}
    counter = 0
    
    word_list = []
    ner_word_list = []
    bboxes_list = []

    for key in data:
        counter += 1
        #search_and_replace(data,key,counter)
        
        #word_list.append(data[key]['text'])
        #bboxes_list.append(data[key]['box'])
        #ner_word_list.append(data[key]['label'])
        #print(data[key]['box'])

        '''
        output.append(
            {
                "id": key,
                "box": data[key]['box'],
                "text": data[key]['text'],
                "meta": data[key]['meta'],
                #"label": data[key]['label'],
                #"words": [{"box": data[key]['box'], "text": data[key]['text']}],
                #"linking": link_list,
            }
        ) 
        '''    
        output[data[key]['meta']] = (
            {
                "id": key,
                "box": data[key]['box'],
                "text": data[key]['text'],
                #"meta": data[key]['meta'],
                #"label": data[key]['label'],
                #"words": [{"box": data[key]['box'], "text": data[key]['text']}],
                #"linking": link_list,
            }
        )    
    
    #output['tokens'] = word_list
    #output['bboxes'] = bboxes_list
    #output['ner_lables'] = ner_word_list
    #print("=====================")   
    #pprint.pprint(output)
    return output

#=================== end def convert_annotation_to_fund ==================

#pprint.pprint(final_list)



#print('Usage:', sys.argv[0], 'export.json')
#print('This command will export your LS OCR annotations to "./funsd/" directory')

ls_export_path = "E:/Works/narendra_tasks/invoice-ocr/docai/pocr/template_data/LS-export-all-15Mar23.json"
master_data_dir = "E:/Works/narendra_tasks/invoice-ocr/docai/pocr/template_data/master_templates"
with open(ls_export_path) as f:
    tasks = json.load(f)

os.makedirs(master_data_dir, exist_ok=True)

for task in tasks:
    final_list
    for annotation in task['annotations']:
        output = {}
        output["annotations"] = convert_annotation_to_fund(annotation['result'])
        output["id"] = annotation['id']
        output["file_name"] = os.path.basename(task['data']['ocr'])
        
        #final_list.append(output)
        
        fname = task["data"]['ocr']
        fname = os.path.basename(fname)
        filename, extension  = os.path.splitext(fname)
        filename = (f'{master_data_dir}/{filename}.json')

        with open(filename, 'w') as f:
            json.dump(output, f, indent=4)