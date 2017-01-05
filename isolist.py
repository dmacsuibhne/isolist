from flask import Flask, render_template
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)

@app.route('/')
def isolist():
    app_directory=os.path.dirname(os.path.realpath(__file__))
    data_directory="".join([app_directory,"data/"])

    xml_filepath_list = get_filepaths(app_directory +"/data")

    # (tree_dict, root_dict) = parse_xml(xml_filepath_list)

    # iso_tree = ET.parse('/home/donnchadh.macsuibhne/Desktop/isolist/isolist/data/ERIClitp_CXP9024296-2.54.3.iso.xml')
    # iso_root = iso_tree.getroot()

    iso_tree_list, iso_root_list = parse_xml(xml_filepath_list)

    # return render_template('isolist.html', root_dict=root_dict)
    return render_template('isolist.html', iso_list=iso_root_list)

def get_filepaths(directory):
    """
    This function will generate the file names in a directory 
    tree by walking the tree either top-down or bottom-up.
    """
    file_path_list = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_path_list.append(filepath)  # Add it to the list.

    return file_path_list  # Self-explanatory.

def parse_xml(xml_filepath_list):
    """
    Parses all xml files in data folder
    """
    tree_list = []
    root_list = []
    for file in xml_filepath_list:
        tree = ET.parse(file)
        tree_list.append(tree)

        root = tree.getroot()
        root_list.append(root)

    #
    # app.logger.debug('DEBUG TEXT')
    # app.logger.debug(root_dict)
    #
    return (tree_list, root_list)