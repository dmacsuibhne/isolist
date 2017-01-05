from flask import Flask, render_template
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)

@app.route('/')
def isolist():
    app_directory=os.path.dirname(os.path.realpath(__file__))
    data_directory="".join([app_directory,"data/"])

    xml_filepaths = get_filepaths(app_directory +"/data")

    (tree_dict, root_dict) = parse_xml(xml_filepaths)

    # table=[]
    # table.append({'row1':xml_filepaths, 'row2':'lo',})



    return render_template('isolist.html', root_dict=root_dict)

def get_filepaths(directory):
    """
    This function will generate the file names in a directory 
    tree by walking the tree either top-down or bottom-up.
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.

def parse_xml(xml_filepaths):
    """
    Parses all xml files in data folder
    """
    tree_dict = {}
    root_dict = {}
    for file in xml_filepaths:
        tree = ET.parse(file)
        tree_dict[file] = tree

        root = tree.getroot()
        root_dict[file] = root

    return (tree_dict, root_dict)