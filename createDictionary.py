import xml.etree.ElementTree as ET
import xml.dom.minidom
import os
import re
from deep_translator import GoogleTranslator

def precess_xml(input_path):
    tree = ET.parse(input_path)
    root = tree.getroot()

    print(f"Processing XML file: {input_path}")
    
    dictionary = create_dictionary(root)
    convert_concrete_values(root, './/dct_Constant_RT')

    dictionary_root = dict_to_xml(dictionary)

    # print("Setting titles...")
    # setTitle(root)
    # Write back to file
    xml_str = ET.tostring(root, encoding='utf-8')

    # output_path = input_path.replace('.xml', '_with_english.xml')
    output_path = input_path
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

    flat_xml = flatten_xml_file(output_path)
    pretty_xml = xml.dom.minidom.parseString(flat_xml).toprettyxml(indent="  ")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
        
    xml_str = ET.tostring(dictionary_root, encoding='utf-8')
    pretty_xml = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="  ")
    dict_output_path = output_path.replace('.xml', '_dictionary.xml')

    with open(dict_output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
       


def dict_to_xml(data: dict):
    root = ET.Element("Entries")

    for value, index in data.items():
        entry = ET.SubElement(root, "Entry")

        key_elem = ET.SubElement(entry, "Key")
        key_elem.text = str(index)

        value_elem = ET.SubElement(entry, "Value")
        if more_hebrew_than_english(value):
            heb_elem = ET.SubElement(value_elem, "Hebrew")
            heb_elem.text = value
        else:
            eng_elem = ET.SubElement(value_elem, "English")
            eng_elem.text = value
        
    return root

def convert_concrete_values(root, tagName):
    for desc in root.findall(tagName):
        value_elem = desc.find('Value')
        if value_elem is not None:
            conctrite_value_elem = value_elem.find('ConcreteValue')
            heb_elem = conctrite_value_elem.find('DictionaryIndex')
            if heb_elem is not None:
                index = int(heb_elem.text.strip())
                str = f"\"<DictionaryIndex>{index}</DictionaryIndex>\""
                conctrite_value_elem.clear()
                conctrite_value_elem.text = str

def more_hebrew_than_english(text: str) -> bool:
    hebrew_letters = re.findall(r'[\u0590-\u05FF]', text)
    english_letters = re.findall(r'[A-Za-z]', text)
    return len(hebrew_letters) > len(english_letters)


def create_dictionary(root):
    dictionary = {}
    for heb_elem in root.findall('.//DictionaryIndex'):
        if heb_elem is not None and heb_elem.text and len(heb_elem.text) > 1:
            text = heb_elem.text
            index = dictionary.get(text)
            if index is None:
                index = len(dictionary) + 1
                dictionary[text] = index    
            heb_elem.text = str(index)
    return dictionary

def convert_dictionaries(dictionary, eng_dictionary, heb_dictionary):
    for text, index in dictionary.items():
        if more_hebrew_than_english(text):
            heb_dictionary[index] = text
        else:      
            eng_dictionary[index] = text 

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
