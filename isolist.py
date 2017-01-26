from flask import Flask, render_template, request, Markup
import xml.etree.ElementTree as ET
import os
import re

app = Flask(__name__)

def get_data_directory():
    """
    Defines and returns the location of xml data files
    """
    # get directory names
    app_directory=os.path.dirname(os.path.realpath(__file__))
    data_directory="{0}/{1}".format(app_directory,"../data/2.x_extended_info/")

    return data_directory


@app.route('/isolist/', defaults = {'start': 0, 'length': 50, 'view_type': "normal" })
@app.route('/isolist/all/', defaults = {'start': 0, 'length': 99999, 'view_type': "all" })
@app.route('/isolist/<int:start>/<int:length>/', defaults = {'view_type': "normal" })
def index(start, length, view_type):
    """
    This controller method provides the logic behind displaying the isolist.html view
    """

    # Read XML data
    iso_tree_list, iso_root_list = Isolist.parse_xml()

    # Sort list by Last modified
    iso_root_list = sorted(iso_root_list, reverse=True, key = lambda iso: iso.find('last_mod').text)

    #Return template and variables it requires
    return render_template('isolist.html', iso_list=iso_root_list[start:(start + length)], Isolist=Isolist, start=start, length=length, view_type=view_type)

@app.route('/save_tag', methods=['POST'])
def add_entry():
    """
    Handle XML edits when cells are edited
    """

    # Read XML data
    iso_tree_list, iso_root_list = Isolist.parse_xml()

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
            iso_tree.write("{0}{1}.xml".format(get_data_directory(), file_name))

            break


    # Empty response
    return ('', 204)

@app.route('/isolist/shutdown/', methods=['GET', 'POST'])
def shutdown():
    """
    For shutting down the flask server conveniently. Based on 
    http://flask.pocoo.org/snippets/67/
    """

    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Isolist app shutting down. To restart, run the command "python {0}/isolist.py & disown"'.format(os.path.dirname(os.path.realpath(__file__)))

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
    def parse_xml():
        """
        Parses all xml files in data folder. For meaning of tree 
        and root see the documentation for xml.etree.ElementTree
        """

        # Generate list of .xml filepaths
        xml_filepath_list = Isolist.get_filepaths(get_data_directory())

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
        iso_location="/home/admin/iso_files/2.x/" 
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
    app.run(host="0.0.0.0", port=8000, threaded=True)
