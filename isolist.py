from flask import Flask, render_template, request, Markup
import xml.etree.ElementTree as ET
import os
import re

app = Flask(__name__)

# Global variables so that index and add_entry can share
global iso_tree_list
global app_directory
global data_directory

@app.route('/isolist/')
def index():
    """
    This controller method provides the logic behind displaying the isolist.html view
    """

    # Global vars to use
    global iso_tree_list
    global app_directory
    global data_directory

    #get directory names
    app_directory=os.path.dirname(os.path.realpath(__file__))
    data_directory="{0}/{1}".format(app_directory,"/data/")

    #Generate list of .xml filepaths
    xml_filepath_list = Isolist.get_filepaths(data_directory)

    #Read XML data
    iso_tree_list, iso_root_list = Isolist.parse_xml(xml_filepath_list)

    #Sort list by Last modified
    # by_last_mod = lambda iso: iso.find('last_mod').text
    iso_root_list = sorted(iso_root_list, reverse=True, key = lambda iso: iso.find('last_mod').text)

    return render_template('isolist.html', iso_list=iso_root_list, Isolist=Isolist)

@app.route('/save_tag', methods=['POST'])
def add_entry():
    """
    Handle XML edits when cells are edited
    """
    #Global vars to use
    global iso_tree_list
    global app_directory
    global data_directory

    # Assign variables to posted data
    file_name = request.form['file_name']
    tag = request.form['tag']
    value = request.form['value']

    # search list for iso with right filename
    for iso_tree in iso_tree_list:
        if iso_tree.getroot().find('file_name').text == file_name:

            # if tag exists, modify it
            if iso_tree.getroot().find(tag) is not None:
                # set the value in the tree (xml object)
                iso_tree.getroot().find(tag).text = value
            # else create it
            else:
                element = ET.SubElement(iso_tree.getroot(), tag)
                element.text = value

            # Write changes to file
            iso_tree.write("{0}{1}.xml".format(data_directory, file_name))

            break


    # Empty response
    return ('', 204)

class Isolist(object):
    """
    This class contains the methods used for this page
    """

    @staticmethod
    def get_filepaths(directory):
        """
        This method will generate the file names in a directory 
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

    @staticmethod
    def parse_xml(xml_filepath_list):
        """
        Parses all xml files in data folder. For meaning of tree 
        and root see the documentation for xml.etree.ElementTree
        """
        tree_list = []
        root_list = []
        for file in xml_filepath_list:
            tree = ET.parse(file)
            tree_list.append(tree)

            root = tree.getroot()
            root_list.append(root)

        return (tree_list, root_list)

    @staticmethod
    def hide_none(cell_string):
        """
        Works around an odd interaction between xml.etree.ElementTree 
        and jinja where empty tags would sometimes result in a cell 
        displaying the string "None"
        """
        if cell_string is None:
            cell_string=""
        return cell_string

    @staticmethod
    def get_version(file_name):
        """
        Given an iso filename, parses the version number
        """
        return file_name[20:-4]

    @staticmethod
    def link_from_30(file_name):
        """
        For the isos that are available on .30, the filename should be a hyperlink to the download
        """
        # iso_location="/home/admin/iso_files/2.x/"
        iso_location="/home/donnchadh.macsuibhne/Downloads/"
        iso_link_location="http://10.44.86.30/iso/2.x/"

        if os.path.exists("".join((iso_location,file_name))):
            return Markup('<a href="{0}{1}">{1}</a>'.format(iso_link_location,file_name))
        else:
            return file_name

    @staticmethod
    def proc_jira(comment):
        """
        Turns JIRA ticket names into hyperlinks
        """
        app.logger.debug(comment)
        app.logger.debug(type(comment))

        if isinstance(comment, basestring):
            comment = re.sub(r'(?i)(LITP|ERIC|STORY|EPIC|DESIGN|MRS)-[0-9]+', Isolist.jira_amm_issue_callback, comment)
            comment = re.sub(r'(?i)(LITPCDS|TORF|CIS)-[0-9]+', Isolist.jira_eri_issue_callback, comment)
        return Markup(comment)

    @staticmethod
    def jira_amm_issue_callback(m):
        """
        Formatting method used by proc_jira
        """
        issueName = m.group(0)
        return '<a contenteditable="false" class="jira_link" href="https://team.ammeon.com/jira/browse/' + issueName.upper() + '">' + issueName + '</a>'

    @staticmethod
    def jira_eri_issue_callback(m):
        """
        Formatting method used by proc_jira
        """
        issueName = m.group(0)
        return '<a contenteditable="false" class="jira_link" href="http://jira-oss.lmera.ericsson.se/browse/' + issueName.upper() + '">' + issueName + '</a>'


if __name__ == "__main__":
    app.run(host="0.0.0.0")