import xml.etree.ElementTree as ET
import xml.dom.minidom
import os
import re
from deep_translator import GoogleTranslator
from pathlib import Path

def precess_xml(input_path):
    tree = ET.parse(input_path)
    root = tree.getroot()

    print(f"Processing XML file: {input_path}")

    heb_dictionary = {}
    eng_dictionary = {}
    
    create_dictionaries(input_path, heb_dictionary, eng_dictionary)

    tagNames = {'.//Description', './/DisplayName', './/DisplayDescription', './/Notes' }
    for tagName in tagNames:
        print("Adding Hebrew descriptions...")
        return_strings_from_dictionary(root, tagName, heb_dictionary, eng_dictionary)

    print("Setting titles...")
    setTitle(root)
    # Write back to file
    xml_str = ET.tostring(root, encoding='utf-8')

    # output_path = input_path.replace('.xml', '_with_english.xml')
    output_path = input_path
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

    flat_xml = flatten_xml_file(output_path)
    pretty_xml = xml.dom.minidom.parseString(flat_xml).toprettyxml(indent="  ")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)      

def return_strings_from_dictionary(root, tagName, heb_dictionary, eng_dictionary):
    for desc in root.findall(tagName):
        heb_elem = desc.find('Hebrew')
        if heb_elem is not None and heb_elem.text:
            index = int(heb_elem.text.strip())  
            text = heb_dictionary.get(index)
            if text is None:
                heb_elem.text = f"NOT_TRANSLATED Missing text for index {index}"
            else:
                heb_elem.text = text
                
            eng_elem = ET.Element('English')
            text = eng_dictionary.get(index)
            if text is None:
                eng_elem.text = f"NOT_TRANSLATED Missing text for index {index}"
            else:
                eng_elem.text = text
            desc.append(eng_elem)

def create_dictionaries(input_path, heb_dictionary, eng_dictionary):
    path = Path(input_path)
    name = path.name
    directory = path.parent
    
    heb_file_name = directory / 'translation/hebrew' / name.replace('.xml', '_dictionary_heb.txt')
    if heb_file_name.exists() and heb_file_name.is_file():
        with open(heb_file_name, "r", encoding="utf-8") as f:
            lines = f.readlines()
        heb_dictionary.update(read_dictionary_file(lines))

    heb_file_name = directory / 'translation/english/translated' / name.replace('.xml', '_dictionary_eng.txt')
    if heb_file_name.exists() and heb_file_name.is_file():
        with open(heb_file_name, "r", encoding="utf-8") as f:
            lines = f.readlines()
        heb_dictionary.update(read_dictionary_file(lines))
    
    eng_file_name = directory / 'translation/english' / name.replace('.xml', '_dictionary_eng.txt')    
    if eng_file_name.exists() and eng_file_name.is_file():
        with open(eng_file_name, "r", encoding="utf-8") as f:
            lines = f.readlines()
        eng_dictionary.update(read_dictionary_file(lines))
    
    eng_file_name = directory / 'translation/hebrew/translated' / name.replace('.xml', '_dictionary_eng.txt')
    if eng_file_name.exists() and eng_file_name.is_file():
        with open(eng_file_name, "r", encoding="utf-8") as f:
            lines = f.readlines()
        eng_dictionary.update(read_dictionary_file(lines)) 

def more_hebrew_than_english(text: str) -> bool:
    hebrew_letters = re.findall(r'[\u0590-\u05FF]', text)
    english_letters = re.findall(r'[A-Za-z]', text)
    return len(hebrew_letters) > len(english_letters)

def read_dictionary_file(lines):
    dictionary = {}

    index = None
    text_lines = []
    for line in lines:
        if line.strip().isdigit():
            new_index = int(line.strip())
            
        if index is None or new_index > index:
            if index is not None:
                dictionary[index] = '\n'.join(text_lines).strip()
            index = int(line.strip())
            text_lines = []
        else:
            text_lines.append(line.strip('\n'))
    if index is not None:
        dictionary[index] = '\n'.join(text_lines).strip()
    return dictionary

def create_dictionary(root, tagName, list):
    for desc in root.findall(tagName):
        heb_elem = desc.find('Hebrew')
        eng_elem = desc.find('English')
        if heb_elem is not None and heb_elem.text:
            if eng_elem is not None and eng_elem.text:
                text = heb_elem.text
                index = len(list)  
                list.append((index, text))
                eng_elem.text = str(index)

def setTitle(root):
    for desc in root.findall('.//English'):
        if desc is not None and desc.text:
            print('+' , end='')
            desc.text = desc.text.title()


def flatten_xml_file(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        xml_string = f.read()
    dom = xml.dom.minidom.parseString(xml_string)
    # Remove all text nodes that are only whitespace
    def remove_whitespace_nodes(node):
        remove_list = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE and child.data.strip() == '':
                remove_list.append(child)
            elif child.hasChildNodes():
                remove_whitespace_nodes(child)
        for child in remove_list:
            node.removeChild(child)
    remove_whitespace_nodes(dom)
    flat_xml_as_string = dom.toxml()
    return flat_xml_as_string

if __name__ == "__main__":
    current_dir = os.getcwd()
    files = os.listdir(current_dir)
    for file in files:
        if file.endswith('.xml'):
            input_path = os.path.join(current_dir, file)
            precess_xml(input_path)
