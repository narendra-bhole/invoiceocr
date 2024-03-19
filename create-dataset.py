import os
import json
from collections import defaultdict
import pprint

final_list = []
def convert_annotation_to_fund(result):
    data = {}
    # collect all LS results and combine labels, text, coordinates into one record
    for item in result:
        
        if 'id' in item:
            id_val = item['id']
            if id_val not in data:
                #data[id_val] = {}  # Initialize the dictionary if the key doesn't exist
                data[id_val] = {'box': [],'text': '', 'label': '','words': [], 'linking': []}
            
            labels = item.get('value', {}).get('labels', None)
            if labels:                
                if id_val not in data:
                    data[id_val] = {}
                data[id_val]["label"] = label2id[labels[0]]
                
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
                x1 = int((v['x'] * w) / 100.0)
                y1 = int((v['y'] *h) / 100.0)
                x2 = x1 + int((v['width'] *w) / 100.0)
                y2 = y1 + int((v['height'] *h) / 100.0)

                data[id_val]['box'] = [round(x1), round(x2), round(y1), round(y2)]
                #data[id_val]['box'] = [item['original_width'], item['original_height'], v['width'], v['height']]
                
            data[id_val]['linking'] = []
            
        if 'direction' in item:
            #print("infile")
            id_from = item['from_id']
            id_to = item['to_id']
            
            data[id_from]['linking'] = [item['from_id'],item['to_id']]
            data[id_to]['linking'] = [item['from_id'],item['to_id']]
            
    #pprint.pprint(data)
    
    # make FUNSD output
    output = {}
    counter = 0
    
    word_list = []
    ner_word_list = []
    bboxes_list = []

    for key in data:
        counter += 1
        search_and_replace(data,key,counter)
        if not data[key]['linking']:
            link_list = []
        else:    
            link_list = [data[key]['linking']]
        
        word_list.append(data[key]['text'])
        bboxes_list.append(data[key]['box'])
        ner_word_list.append(data[key]['label'])
        
        '''
        output.append(
            {
                "id": key,
                "box": data[key]['box'],
                "text": data[key]['text'],
                "label": data[key]['label'],
                "words": [{"box": data[key]['box'], "text": data[key]['text']}],
                "linking": link_list,
            }
        )    
        '''
    
    output['tokens'] = word_list
    output['bboxes'] = bboxes_list
    output['ner_lables'] = ner_word_list
    #print("=====================")   
    #pprint.pprint(output)
    return output

#=================== end def convert_annotation_to_fund ==================

def search_and_replace(dictionary, search_val, replace_val):
    for key, value in dictionary.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    search_and_replace(item, search_val, replace_val)
                elif item == search_val:
                    value[value.index(item)] = replace_val
        elif isinstance(value, dict):
            search_and_replace(value, search_val, replace_val)
        elif value == search_val:
            dictionary[key] = replace_val
        
def ls_to_funsd_converter(
    ls_export_path='export.json', funsd_dir='funsd', data_key='ocr'
):
    with open(ls_export_path) as f:
        tasks = json.load(f)

    os.makedirs(funsd_dir, exist_ok=True)

    for task in tasks:

        final_list
        for annotation in task['annotations']:
            output = convert_annotation_to_fund(annotation['result'])
            output["id"] = annotation['id']
            output["file_name"] = os.path.basename(task['data']['ocr'])
            
            final_list.append(output)
            
            '''
            fname = task["data"][data_key]
            fname = os.path.basename(fname)
            filename, extension  = os.path.splitext(fname)
            filename = (f'{funsd_dir}/{filename}.json')

            with open(filename, 'w') as f:
                json.dump(output, f, indent=4)
            '''

    #pprint.pprint(final_list)

if __name__ == '__main__':
    import sys

    #print('Usage:', sys.argv[0], 'export.json')
    #print('This command will export your LS OCR annotations to "./funsd/" directory')

    ls_to_funsd_converter("E:/Works/narendra_tasks/invoice-ocr/docai/aiody/Training_json.json")