""" repository files and addons.xml generator """

""" Modified by Rodrigo@XMBCHUB to zip plugins/repositories to a "zip" folder """
""" Modified by BartOtten to also create a repository addon """

""" This file is "as is", without any warranty whatsoever. Use as own risk """

import os
import md5
import zipfile
import shutil
from xml.dom import minidom
import glob
import datetime
from ConfigParser import SafeConfigParser

class Generator:
    global output
    global rootdir
    global sep
    global config
    
    sep=os.path.sep
       
    """
       Load the configuration
    """
    config = SafeConfigParser()
    config.read('config.ini')
    addonid=config.get('addon', 'id')
    output="_" + config.get('locations', 'output')
    
    os.chdir(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)))

    
    if not os.path.exists(output):
        os.makedirs(output)

    """
        Generates a new addons.xml file from each addons addon.xml file
        and a new addons.xml.md5 hash file. Must be run from the root of
        the checked-out repo. Only handles single depth folder structure.
    """

    def __init__( self ):

        # generate files
        if not os.path.isfile(self.addonid + sep + "addon.xml"):
            self._generate_repo_files()
        
        self._generate_addons_file()
        self._generate_md5_file()
        self._generate_zip_files()
        # notify user
        print "Finished updating addons xml, md5 files and zipping addons"


    def _generate_repo_files ( self ):
        print "Create repository addon"
        
        repo_xml = u"""<?xml version="1.0" encoding="UTF-8"?>
        <addon id="{addonid}" name="{name}" version="{version}" provider-name="{author}">
            <requires>
                <import addon="xbmc.addon" version="12.0.0"/>
            </requires>
            <extension point="xbmc.addon.repository" name="{name}">
                <info compressed="false">{url}{output}addons.xml</info>
                <checksum>{url}{output}addons.xml.md5</checksum>
                <datadir zip="true">{url}{output}</datadir>
                <hashes>false</hashes>
            </extension>
            <extension point="xbmc.addon.metadata">
                <summary>{summary}</summary>
                <description>{description}</description>
                <platform>all</platform>
        </extension>
        </addon>""".format(
            addonid=config.get('addon', 'id'), 
            name=config.get('addon', 'name'), 
            version=config.get('addon', 'version'), 
            author=config.get('addon', 'author'), 
            summary=config.get('addon', 'summary'), 
            description=config.get('addon', 'description'), 
            url=config.get('locations', 'url'),
            output="_" + config.get('locations', 'output') + "/")
        
        # save file
        if not os.path.exists(self.addonid):
            os.makedirs(self.addonid)
            
        self._save_file( repo_xml.encode( "utf-8" ), file=self.addonid + sep + "addon.xml" )
        

    def _generate_zip_files ( self ):
        addons = os.listdir( "." )
        # loop thru and add each addons addon.xml file
        for addon in addons:
            try:
                # skip any file or .git folder
                if ( not os.path.isdir( addon ) or addon == ".git" or addon == output): continue
                # create path
                _path = os.path.join( addon, "addon.xml" )
                # split lines for stripping
                document = minidom.parse(_path)
                for parent in document.getElementsByTagName("addon"):
                    version = parent.getAttribute("version")
                    addonid = parent.getAttribute("id")
                self._generate_zip_file(addon, version, addonid)
            except Exception, e:
                print e

    def _generate_zip_file ( self, path, version, addonid):
        print "Generate zip file for " + addonid + " " + version
        filename = path + "-" + version + ".zip"
        try:
            zip = zipfile.ZipFile(filename, 'w')
            for root, dirs, files in os.walk(path + sep):
                for file in files:
                    zip.write(os.path.join(root, file))
                    
            zip.close()
         
            if not os.path.exists(output + sep + addonid):
                os.makedirs(output + sep + addonid)
         
            if os.path.isfile(output + sep + addonid + sep + filename):
                os.rename(output + sep + addonid + sep + filename, output + sep + addonid + sep + filename + "." + datetime.datetime.now().strftime("%Y%m%d%H%M%S") )
            shutil.move(filename, output + sep + addonid + sep + filename)
        except Exception, e:
            print e

    def _generate_addons_file( self ):
        # addon list
        addons = os.listdir( "." )
        # final addons text
        addons_xml = u"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<addons>\n"
        # loop thru and add each addons addon.xml file
        for addon in addons:
            try:
                # skip any file or .git folder
                if ( not os.path.isdir( addon ) or addon == ".git" ): continue
                # create path
                _path = os.path.join( addon, "addon.xml" )
                # split lines for stripping
                xml_lines = open( _path, "r" ).read().splitlines()
                # new addon
                addon_xml = ""
                # loop thru cleaning each line
                for line in xml_lines:
                    # skip encoding format line
                    if ( line.find( "<?xml" ) >= 0 ): continue
                    # add line
                    addon_xml += unicode( line.rstrip() + "\n", "utf-8" )
                # we succeeded so add to our final addons.xml text
                addons_xml += addon_xml.rstrip() + "\n\n"
            except Exception, e:
                # missing or poorly formatted addon.xml
                print "Excluding %s for %s" % ( _path, e, )
        # clean and add closing tag
        addons_xml = addons_xml.strip() + u"\n</addons>\n"
        # save file
        self._save_file( addons_xml.encode( "utf-8" ), file=output + sep + "addons.xml" )

    def _generate_md5_file( self ):
        try:
            # create a new md5 hash
            m = md5.new( open(output + sep +  "addons.xml" ).read() ).hexdigest()
            # save file
            self._save_file( m, file=output + sep + "addons.xml.md5" )
        except Exception, e:
            # oops
            print "An error occurred creating addons.xml.md5 file!\n%s" % ( e, )

    def _save_file( self, data, file ):
        try:
            # write data to the file
            open( file, "w" ).write( data )
        except Exception, e:
            # oops
            print "An error occurred saving %s file!\n%s" % ( file, e, )


if ( __name__ == "__main__" ):
    # start
    Generator()