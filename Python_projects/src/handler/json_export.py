import json
import xml.etree.ElementTree as ET

# Creating class to write our queries into JSON format instead of using a context manager
class Writer:
    def __init__(self, path):
        self.path = path

    def export_json(self, data):
        with open(self.path, "w") as file:
            file.write(json.dumps(data, indent=4))

    def export_xml(self, data, item_name='item'):
        root = ET.Element("data")
        for row in data:
            item = ET.SubElement(root, item_name)
            for k,v in row.items():
                child = ET.SubElement(item,k)
                child.text = str(v)

            tree = ET.ElementTree(root)
            tree.write(self.path, encoding="utf-8", xml_declaration=True)