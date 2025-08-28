import xml.etree.ElementTree as ET
import xml.dom.minidom
import os
from deep_translator import GoogleTranslator

def precess_xml(input_path):
    tree = ET.parse(input_path)
    root = tree.getroot()

    print(f"Processing XML file: {input_path}")

    tagNames = {'.//Description', './/DisplayName', './/DisplayDescription', './/Notes' }
    for tagName in tagNames:
        add_dictionary_index(root, tagName)
        # print("Adding English translations...")
        # Add English translations after Hebrew
        # add_english(root, tagName)

    tagNames = {'.//dct_Constant_RT' }
    for tagName in tagNames:
        add_concrete_dictionary_index(root, tagName)


    print("Setting titles...")
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
    # with open(input_path, 'w', encoding='utf-8') as f:
    #     f.write(xml_str)

def add_dictionary_index(root, tagName):
    for desc in root.findall(tagName):
        if len(desc) > 0:
            continue    
        
        # Skip if already wrapped
        if desc.text and len(desc.text) > 1:
            heb_elem = desc.find('DictionaryIndex')
            if heb_elem is None:
                text = desc.text
                desc.clear()
                hebrew = ET.SubElement(desc, "DictionaryIndex")
                hebrew.text = text

def add_concrete_dictionary_index(root, tagName):
    for desc in root.findall(tagName):
        value_elem = desc.find('Value')
        if value_elem is not None:
            type_elem = value_elem.find('Type')
            conctrite_value_elem = value_elem.find('ConcreteValue')
            if type_elem is not None and type_elem.text == 'STRING' and conctrite_value_elem is not None:
                if len(conctrite_value_elem.text.strip()) > 3:
                    text = conctrite_value_elem.text.strip()[1:-1] 
                    if not text.isupper():
                        heb_elem = conctrite_value_elem.find('DictionaryIndex')
                        if heb_elem is None:
                            conctrite_value_elem.clear()
                            hebrew = ET.SubElement(conctrite_value_elem, "DictionaryIndex")
                            hebrew.text = text
            

def add_english(root, tagName):
    translator = GoogleTranslator(source='iw', target='en');
    for desc in root.findall(tagName):
        heb_elem = desc.find('Hebrew')
        if heb_elem is not None and heb_elem.text:
            eng_elem = desc.find('English')
            if eng_elem is None:

                # Translate Hebrew to English
                try:
                    translation = translator.translate(heb_elem.text)
                except Exception as e:
                    print(f"\nError translating '{heb_elem.text}': {e}")
                    translation = "NOT TRANSLATED"

                print('.' ,end='')
                # print(f"Translating Hebrew: {heb_elem.text} to English: {translation}")
                english_elem = ET.Element('English')
                english_elem.text = translation
                # Insert after Hebrew
                idx = list(desc).index(heb_elem)
                desc.insert(idx + 1, english_elem)

def setTitle(root):
    for desc in root.findall('.//English'):
        if desc is not None and desc.text:
            print('+' , end='')
            desc.text = desc.text.title()

def detect_language(text):
    if not text:
        return "unknown"
    hebrew_count = len(re.findall(r'[\u0590-\u05FF]', text))
    english_count = len(re.findall(r'[A-Za-z]', text))
    if hebrew_count > english_count:
        return "hebrew"
    elif english_count > hebrew_count:
        return "english"
    else:
        return "unknown"

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
