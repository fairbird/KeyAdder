#!/usr/bin/python
# -*- coding: utf-8 -*-
# Code By RAED and mfaraj57

from enigma import eConsoleAppContainer, eDVBDB, iServiceInformation, eTimer, loadPNG, getDesktop, RT_WRAP, RT_HALIGN_LEFT, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.config import config, getConfigListEntry, ConfigText, ConfigSelectionNumber, ConfigSubsection, ConfigYesNo, configfile, ConfigSelection, ConfigClock
from Components.ConfigList import ConfigListScreen
from Plugins.Plugin import PluginDescriptor
from Tools.BoundFunction import boundFunction
from ServiceReference import ServiceReference
from Screens import Standby
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.ChoiceBox import ChoiceBox
from Screens.InputBox import InputBox
from Components.Input import Input
from Components.Sources.StaticText import StaticText
from Components.FileList import FileList
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Label import Label
from array import array
from string import hexdigits
from datetime import datetime
from Components.MenuList import MenuList
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS
import binascii
import os
import subprocess
from shutil import copyfile
from Plugins.Extensions.KeyAdder.tools.downloader import getversioninfo, imagedownloadScreen, imagedownloadScreen2

# python3
from os import path as os_path, remove as os_remove
from Plugins.Extensions.KeyAdder.tools.Console import Console
from Plugins.Extensions.KeyAdder.tools.compat import PY3, compat_urlparse, compat_urlretrieve, compat_Request, compat_urlopen, compat_URLError

VER = getversioninfo()

reswidth = getDesktop(0).size().width()
config.plugins.KeyAdder = ConfigSubsection()
config.plugins.KeyAdder.update = ConfigYesNo(default=True)
config.plugins.KeyAdder.autorestart = ConfigYesNo(default=True)
config.plugins.KeyAdder.lastcaid = ConfigText(default="0", fixed_size=False)
config.plugins.KeyAdder.softcampath = ConfigYesNo(default=False) #False = Auto Detecte path
config.plugins.KeyAdder.custom_softcampath = ConfigText(default="/usr/keys", visible_width = 250, fixed_size = False)
config.plugins.KeyAdder.keyboardStyle = ConfigSelection(default = "Style2", choices = [
    ("Style1", _("Old Style keyboard")),
    ("Style2", _("New Style keyboard")),
    ])
config.plugins.KeyAdder.AddkeyStyle = ConfigSelection(default = "auto", choices = [
    ("auto", _("Auto detect and add keys")),
    ("manual", _("Manual add all info keys")),
    ])
config.plugins.KeyAdder.savenumber = ConfigSelectionNumber(1, 20, 1, default=5)
config.plugins.KeyAdder.Autodownload_enabled = ConfigYesNo(default=False)
config.plugins.KeyAdder.wakeup = ConfigClock(default=((7 * 60) + 9) * 60)  # 7:00
config.plugins.KeyAdder.Show_Autoflash = ConfigYesNo(default=False)
config.plugins.KeyAdder.Autodownload_sitelink = ConfigSelection(default = "smcam", choices = [
        ("smcam", _("smcam")),
        ("softcam.org", _("softcam.org")),
        #("enigma1969", _("enigma1969")),
        ("MOHAMED_OS", _("MOHAMED_OS")),
        ("MOHAMED_Nasr", _("MOHAMED_Nasr")),
        ("Serjoga", _("Serjoga")),
        ("Novaler4k", _("Novaler4k")),
        ])

BRANATV="/usr/lib/enigma2/python/boxbranding.so" ## OpenATV
BRANDPLI="/usr/share/enigma2/rc_models/rc_models.cfg" ## OpenPLI/OV
BRANDOPEN="/usr/lib/enigma2/python/Tools/StbHardware.pyo" ## Open source
BRANDTS="/usr/lib/enigma2/python/Plugins/TSimage/__init__.pyo" ## TS
BRANDOS="/var/lib/dpkg/status" ## DreamOS
BRANDVU="/proc/stb/info/vumodel" ## VU+

save_key = "/etc/enigma2/savekeys"

def DreamOS():
    if os_path.exists("/var/lib/dpkg/status"):
        return DreamOS

def BHVU():
    if os.path.exists("/proc/stb/info/vumodel") and os.path.exists("/usr/lib/enigma2/python/Blackhole"):
        return BHVU

def VTI():
    VTI = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/VTIPanel/plugin.pyo")
    if os.path.exists(VTI):
        return VTI

from Plugins.Extensions.KeyAdder.tools.VirtualKeyboardKeyAdder import VirtualKeyBoardKeyAdder

def logdata(label_name = "", data = None):
    try:
        data=str(data)
        fp = open("/tmp/KeyAdder.log", "a")
        fp.write( str(label_name) + ": " + data+"\n")
        fp.close()
    except:
        trace_error()    
        pass

def dellog(label_name = '', data = None):
    try:
        if os_path.exists('/tmp/KeyAdder.log'):
            os_remove('/tmp/KeyAdder.log')
        if os_path.exists('/tmp/KeyAdderError.log'):
            os_remove('/tmp/KeyAdderError.log')
    except:
        pass

def trace_error():
    import sys
    import traceback
    try:
        traceback.print_exc(file=sys.stdout)
        traceback.print_exc(file=open("/tmp/KeyAdderError.log", "a"))
    except:
        pass

def getnewcaid(SoftCamKey):
    ##T 0001
    caidnumbers=[]
    newkey=1
    if os_path.exists(SoftCamKey):
        try:
            lines=open(SoftCamKey).readlines()
            for line in lines:
                line=line.strip()
                if line.startswith("T"):
                    caidnumber=line[2:6]
                    try:
                        caidnumbers.append(int(caidnumber))
                    except:
                        continue
        except:
            caidnumbers=[]
        try:
            newcaid=max(caidnumbers)+1
        except:
                newcaid=1
        formatter="{:04}"
        newcaid=formatter.format(newcaid)
        saved_caid=int(config.plugins.KeyAdder.lastcaid.value)+1
        if saved_caid>newcaid:
            newcaid=saved_caid
        elif newcaid>saved_caid :                                                    
            config.plugins.KeyAdder.lastcaid.value=newcaid
            config.plugins.KeyAdder.lastcaid.save()
        elif  newcaid==9999:
            config.plugins.KeyAdder.lastcaid.value="1111"
            config.plugins.KeyAdder.lastcaid.save()
            newcaid=="1111"
        return newcaid 

def findSoftCamKey():
        paths = ["/etc/tuxbox/config/oscam-emu",
               "/etc/tuxbox/config/oscam-trunk",
               "/etc/tuxbox/config/oscam",
               "/etc/tuxbox/config/ncam",
               "/etc/tuxbox/config/gcam",
               "/etc/tuxbox/config",
               "/etc",
               "/usr/keys",
               "/var/keys"]
        if config.plugins.KeyAdder.softcampath.value == False:
                if os_path.exists("/tmp/.oscam/oscam.version"):
                        data = open("/tmp/.oscam/oscam.version", "r").readlines()
                if os_path.exists("/tmp/.ncam/ncam.version"):
                        data = open("/tmp/.ncam/ncam.version", "r").readlines()
                if os_path.exists("/tmp/.gcam/gcam.version"):
                        data = open("/tmp/.gcam/gcam.version", "r").readlines()
                        for line in data:
                                if "configdir:" in line.lower():
                                        paths.insert(0, line.split(":")[1].strip())
                for path in paths:
                        softcamkey = os_path.join(path, "SoftCam.Key")
                        print("[key] the %s exists %d" % (softcamkey, os_path.exists(softcamkey)))
                        if os_path.exists(softcamkey):
                                return softcamkey
                return "/usr/keys/SoftCam.Key"
        else:
                return os_path.join(config.plugins.KeyAdder.custom_softcampath.value, "SoftCam.Key")

def downloadFile(url, filePath):
    try:
        # Download the file from `url` and save it locally under `file_name`:
        compat_urlretrieve(url, filePath)
        return True
        req = compat_Request(url, headers={'User-Agent': 'Mozilla/5.0'}) # add [headers={'User-Agent': 'Mozilla/5.0'}] to fix HTTP Error 403: Forbidden
        response = compat_urlopen(req,timeout=5)
        print("response.read",response.read())
        output = open(filePath, 'wb')
        output.write(response.read())
        output.close()
        response.close()
    except:
        trace_error()
        return

def restartemu():
        # Execute the shell command and get the first matching emulator name
        try:
                result = subprocess.check_output(
                        'ps -eo comm | grep -E "^(ncam|oscam|cccam|mgcamd|gbox|wicardd)" | sort -u | head -n1',
                        shell=True, universal_newlines=True
                ).strip()
                emuname = result
                # print(f"emuname ************************* {emuname}")
                command = ""
                if emuname:
                        clean_tmp = os.system('rm -rf /tmp/*.info* /tmp/*.tmp* /tmp/.%s /tmp/*share* /tmp/*.pid* /tmp/*sbox* /tmp/%s.* /tmp/*.%s' % (emuname, emuname, emuname))
                        if os_path.exists("/usr/bin/%s" % emuname):
                                clean_tmp
                                command = "killall -9 %s && /usr/bin/%s &" % (emuname, emuname)
                        elif os_path.exists("/usr/camd/%s" % emuname):
                                clean_tmp
                                command = "killall -9 %s && /usr/camd/%s &" % (emuname, emuname)
                        elif os_path.exists("/usr/cam/%s" % emuname):
                                clean_tmp
                                command = "killall -9 %s && /usr/cam/%s &" % (emuname, emuname)
                        elif os_path.exists("/usr/emu/%s" % emuname):
                                clean_tmp
                                command = "killall -9 %s && /usr/emu/%s &" % (emuname, emuname)
                        elif os_path.exists("/usr/softcams/%s" % emuname):
                                clean_tmp
                                command = "killall -9 %s && /usr/softcams/%s &" % (emuname, emuname)
                        elif os_path.exists("/var/bin/%s" % emuname):
                                clean_tmp
                                command = "killall -9 %s && /var/bin/%s &" % (emuname, emuname)
                        elif os_path.exists("/var/emu/%s" % emuname):
                                clean_tmp
                                command = "killall -9 %s && /var/emu/%s &" % (emuname, emuname)
                        os.system(command)
                        logdata("command",command)
                else:
                        print("No matching emulator found.")
        except subprocess.CalledProcessError as e:
                print("Error while detecting emulator: %s" % e)



class KeyAdderUpdate(Screen):
    if reswidth == 2560:
        skin = '''
                        <screen name="KeyAdderUpdate" position="center,center" size="960,634" backgroundColor="#16000000" title="KeyAdderUpdate" flags="wfNoBorder">
                                <widget source="Title" render="Label" position="0,0" size="956,63" font="Regular;45" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#16000000"/>
                                <widget name="pathfile" position="center,70" size="908,45" font="Regular;35" foregroundColor="#00cccc40" backgroundColor="#16000000"/>
                                <widget name="menu" position="25,123" size="907,440" backgroundColor="#16000000"/>
                                <eLabel position="20,570" size="160,60"  backgroundColor="#00ff0000" zPosition="1"/>
                                <eLabel text="MENU" font="Regular;45" position="23,574" size="153,53" foregroundColor="#00000000" backgroundColor="#00ffffff" zPosition="3" valign="center" halign="center"/>
                                <eLabel text="Press Menu for more options" font="Regular;45" position="191,570" size="739,60" foregroundColor="#00ffffff" backgroundColor="#00000000" zPosition="2" valign="center"/>
                        </screen>'''
    elif reswidth == 1920:
        skin = '''
                        <screen name="KeyAdderUpdate" position="center,center" size="704,450" backgroundColor="#16000000" title="KeyAdderUpdate" flags="wfNoBorder">
                                <widget source="Title" render="Label" position="0,0" size="704,45" font="Regular;35" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#16000000"/>
                                <widget name="pathfile" position="center,40" size="650,45" font="Regular;28" foregroundColor="#00cccc40" backgroundColor="#16000000"/>
                                <widget name="menu" position="center,85" size="650,290" backgroundColor="#16000000"/>
                                <eLabel position="25,390" size="110,50" backgroundColor="#00ff0000" zPosition="1"/>
                                <eLabel text="MENU" font="Regular;30" position="28,394" size="103,43" foregroundColor="#00000000" backgroundColor="#00ffffff" zPosition="3" valign="center" halign="center"/>
                                <eLabel text="Press Menu for more options" font="Regular;33" position="148,390" size="546,50" foregroundColor="#00ffffff" backgroundColor="#00000000" zPosition="2" valign="center"/>
                        </screen>'''
    else:
        skin = '''
                        <screen name="KeyAdderUpdate" position="center,center" size="476,306" backgroundColor="#16000000" title="KeyAdderUpdate" flags="wfNoBorder">
                                <widget source="Title" render="Label" position="0,0" size="476,35" font="Regular;28" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#16000000"/>
                                <widget name="pathfile" position="10,40" size="458,35" font="Regular;24" foregroundColor="#00cccc40" backgroundColor="#16000000"/>
                                <widget name="menu" position="10,80" size="450,173" backgroundColor="#16000000"/>
                                <eLabel position="15,259" size="80,40" backgroundColor="#00ff0000" zPosition="1"/>
                                <eLabel text="MENU" font="Regular;26" position="18,261" size="74,35" foregroundColor="#00000000" backgroundColor="#00ffffff" zPosition="3" valign="center" halign="center"/>
                                <eLabel text="Press Menu for more options" font="Regular;25" position="104,259" size="369,40" foregroundColor="#00ffffff" backgroundColor="#00000000" zPosition="2" valign="center"/>
                        </screen>'''

    def __init__(self, session, title="", datalist = []):
        Screen.__init__(self, session)
        dellog()
        self["menu"] = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self["actions"] = ActionMap(["WizardActions", "ColorActions","MenuActions"],
        {
            "ok": self.select,
            "back": self.close,
            "menu" :self.menu,
        })
        title = "KeyAdder Version %s" % VER
        self["pathfile"] = Label()
        self["pathfile"].setText("Current Path : " + findSoftCamKey())
        menuData = []
        menuData.append((0, "Add key Manually", "key"))
        menuData.append((1, "Update Softcam online", "update"))
        if config.plugins.KeyAdder.softcampath.value == True:
            menuData.append((2, "Select Softcam.key Path", "path"))
        menuData.append((3, "Exit", "exit"))
        self.new_version = VER
        self.settitle(title, menuData)

    def menu(self):
        self.session.open(keyAdder_setup)
        self.close()

    def settitle(self, title, datalist):
        if config.plugins.KeyAdder.update.value:
             self.checkupdates()
        self.setTitle(title)
        self.showmenulist(datalist)

    def select(self):
        index = self["menu"].getSelectionIndex()
        if index == 0:
                keymenu(self.session)
        elif index == 1:
                self.siteselect()
        elif index == 2:
                if config.plugins.KeyAdder.softcampath.value == True:
                        self.pathselect()
                else:
                        self.close()
        else:
            self.close()

    def pathselect(self):
        self.session.open(PathsSelect)
        self.close()

    def siteselect(self):
        list = []
        list.append(("smcam (Always Updated)", "smcam"))
        list.append(("softcam.org (Always Updated)", "softcam.org"))
        list.append(("enigma1969 (Always Updated)", "enigma1969"))
        list.append(("MOHAMED_OS (Always Updated)", "MOHAMED_OS"))
        list.append(("MOHAMED_Nasr (Always Updated)", "MOHAMED_Nasr"))
        list.append(("Serjoga", "Serjoga"))
        list.append(("Novaler4k", "Novaler4k"))
        self.session.openWithCallback(self.Downloadkeys, ChoiceBox, _("select site to downloan file"), list)
 
    def Downloadkeys(self, select, SoftCamKey=None):
        cmdlist = []
        SoftCamKey = findSoftCamKey()
        agent = '--header="User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/8.0 Safari/600.1.17"'
        crt = "--debug --no-check-certificate"
        command = ""
        if select:
                ### This codes if using site and get error (sslv3 alert handshake failure) from such as gitlab site
                #myurl = "https://gitlab.com/xxxx/-/raw/main/SoftCam.Key"
                #downloadFile(myurl, SoftCamKey)
                #self.session.open(imagedownloadScreen2)
            if select[1] == "smcam":
                myurl = "https://raw.githubusercontent.com/smcam/s/main/SoftCam.Key"
                command = "wget -q %s %s %s %s" % (crt, agent, SoftCamKey, myurl)
                self.session.open(imagedownloadScreen,"softcam",SoftCamKey,myurl)
            elif select[1] == "softcam.org":
                myurl = "http://www.softcam.org/deneme6.php?file=SoftCam.Key"
                os.system("wget -O %s %s" % (SoftCamKey, myurl))
                #os.system("wget -O {0} {1}".format(SoftCamKey, myurl)) # Just other code if the above does not work
                self.session.open(imagedownloadScreen2)
            elif select[1] == "enigma1969":
                myurl = "https://docs.google.com/uc?export=download&id=1aujij43w7qAyPHhfBLAN9sE-BZp8_AwI&export"
                command = "wget %s -q %s %s" % (crt, SoftCamKey, myurl)
                self.session.open(imagedownloadScreen,"softcam",SoftCamKey,myurl)
            elif select[1] == "MOHAMED_OS":
                myurl = "https://raw.githubusercontent.com/MOHAMED19OS/SoftCam_Emu/main/SoftCam.Key"
                command = "wget -q %s %s %s %s" % (crt, agent, SoftCamKey, myurl)
                self.session.open(imagedownloadScreen,"softcam",SoftCamKey,myurl)
            elif select[1] == "MOHAMED_Nasr":
                myurl = "https://raw.githubusercontent.com/popking159/softcam/master/SoftCam.Key"
                command = "wget -q %s %s %s %s" % (crt, agent, SoftCamKey, myurl)
                self.session.open(imagedownloadScreen,"softcam",SoftCamKey,myurl)
            elif select[1] == "Serjoga":
                myurl = "http://raw.githubusercontent.com/audi06/SoftCam.Key_Serjoga/master/SoftCam.Key"
                command = "wget -q %s %s %s %s" % (crt, agent, SoftCamKey, myurl)
                self.session.open(imagedownloadScreen,"softcam",SoftCamKey,myurl)
            elif select[1] == "Novaler4k":
                myurl = "http://novaler.homelinux.com/SoftCam.Key"
                command = "wget -q %s %s %s %s" % (crt, agent, SoftCamKey, myurl)
                self.session.open(imagedownloadScreen,"softcam",SoftCamKey,myurl)
            else:
                self.close()
            logdata("command",command)
            self.close()

    def showmenulist(self, datalist):
        cacolor = 16776960
        cbcolor = 16753920
        cccolor = 15657130
        cdcolor = 16711680
        cecolor = 16729344
        cfcolor = 65407
        cgcolor = 11403055
        chcolor = 13047173
        cicolor = 13789470
        scolor = cbcolor
        res = []
        menulist = []
        if reswidth == 2560:
            self["menu"].l.setItemHeight(85)
            self["menu"].l.setFont(0, gFont("Regular", 50))
        elif reswidth == 1920:
            self["menu"].l.setItemHeight(75)
            self["menu"].l.setFont(0, gFont("Regular", 42))
        else:
            self["menu"].l.setItemHeight(50)
            self["menu"].l.setFont(0, gFont("Regular", 28))
        for i in range(0, len(datalist)):
            txt = datalist[i][1]
            if reswidth == 2560 or reswidth == 1920:
                  png = os_path.join(resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/buttons/fhd/%s.png" % datalist[i][2]))
            else:
                  png = os_path.join(resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/buttons/%s.png" % datalist[i][2]))
            res.append(MultiContentEntryText(pos=(0, 1), size=(0, 0), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER | RT_WRAP, text="", color=scolor, color_sel=cccolor, border_width=3, border_color=806544))
            if reswidth == 2560:
                res.append(MultiContentEntryText(pos=(100, 1), size=(1440, 85), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER | RT_WRAP, text=str(txt), color=16777215, color_sel=16777215))
                res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(75, 75), png=loadPNG(png)))
            elif reswidth == 1920:
                res.append(MultiContentEntryText(pos=(100, 1), size=(1080, 75), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER | RT_WRAP, text=str(txt), color=16777215, color_sel=16777215))
                res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(75, 75), png=loadPNG(png)))
            else:
                res.append(MultiContentEntryText(pos=(60, 1), size=(723, 50), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER | RT_WRAP, text=str(txt), color=16777215, color_sel=16777215))
                res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(40, 40), png=loadPNG(png)))
            menulist.append(res)
            res = []
        self["menu"].l.setList(menulist)
        self["menu"].show()

    def checkupdates(self):
        try:
                from twisted.web.client import getPage, error
                url = b"https://raw.githubusercontent.com/fairbird/KeyAdder/main/installer.sh"
                getPage(url,timeout=10).addCallback(self.parseData).addErrback(self.errBack)
        except Exception as error:
                trace_error()

    def errBack(self,error=None):
        logdata("errBack-error",error)

    def parseData(self, data):
        if PY3:
                data = data.decode("utf-8")
        else:
                data = data.encode("utf-8")
        if data:
                lines = data.split("\n")
                for line in lines:
                       #line=str(line)
                       if line.startswith("version"):
                          self.new_version = line.split("=")
                          self.new_version = line.split("'")[1]
                          #break #if enabled the for loop will exit before reading description line
                       if line.startswith("description"):
                          self.new_description = line.split("=")
                          self.new_description = line.split("'")[1]
                          break
        if float(VER) == float(self.new_version) or float(VER)>float(self.new_version):
                logdata("Updates","No new version available")
        else :
                new_version = self.new_version
                new_description = self.new_description
                self.session.openWithCallback(self.install, MessageBox, _("New version %s is available.\n\n%s.\n\nDo want ot install now." % (new_version, new_description)), MessageBox.TYPE_YESNO)

    def install(self,answer=False):
        try:
                if answer:
                           cmdlist = []
                           cmd="wget https://raw.githubusercontent.com/fairbird/KeyAdder/main/installer.sh -O - | /bin/sh"
                           cmdlist.append(cmd)
                           self.session.open(Console, title="Installing last update, enigma will be started after install", cmdlist=cmdlist, finishedCallback=self.myCallback, closeOnSuccess=False)
        except:
                trace_error()

    def myCallback(self,result):
         return


class PathsSelect(Screen):
        if reswidth == 1920 or reswidth == 2560:
                if DreamOS():
                        skin = """
                                <screen name="PathsSelect" position="center,center" size="906,812" title="Select Select" >
                                        <eLabel position="180,805" size="170,3" foregroundColor="#00ff2525" backgroundColor="#00ff2525"/>
                                        <eLabel position="525,805" size="170,3" foregroundColor="#00389416" backgroundColor="#00389416"/>
                                        <widget name="list_head" position="5,5" size="891,40" foregroundColor="#00cccc40"/>
                                        <widget source="key_red" render="Label" position="180,765" zPosition="1" size="170,40" font="Regular;28" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
                                        <widget source="key_green" render="Label" position="525,765" zPosition="1" size="170,40" font="Regular;28" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
                                        <widget name="checkList" position="5,50" zPosition="2" size="892,707" scrollbarMode="showOnDemand"/>
                                </screen>"""
                else:
                        skin = """
                                <screen name="PathsSelect" position="center,center" size="906,812" title="Select Select" >
                                        <eLabel position="180,805" size="170,3" foregroundColor="#00ff2525" backgroundColor="#00ff2525"/>
                                        <eLabel position="525,805" size="170,3" foregroundColor="#00389416" backgroundColor="#00389416"/>
                                        <widget name="list_head" position="5,5" size="891,40" font="Regular;28" foregroundColor="#00cccc40"/>
                                        <widget source="key_red" render="Label" position="180,765" zPosition="1" size="170,40" font="Regular;28" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
                                        <widget source="key_green" render="Label" position="525,765" zPosition="1" size="170,40" font="Regular;28" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
                                        <widget name="checkList" font="Regular;28" itemHeight="40" position="5,50" zPosition="2" size="892,707" scrollbarMode="showOnDemand"/>
                                </screen>"""
        else:
                skin = """
                        <screen name="PathsSelect" position="center,center" size="708,590" title="Select Select" >
                                <eLabel position="95,580" size="170,3" foregroundColor="#00ff2525" backgroundColor="#00ff2525"/>
                                <eLabel position="415,580" size="170,3" foregroundColor="#00389416" backgroundColor="#00389416"/>
                                <widget name="list_head" position="5,5" size="689,38" foregroundColor="#00cccc40"/>
                                <widget source="key_red" render="Label" position="95,540" zPosition="1" size="170,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
                                <widget source="key_green" render="Label" position="415,540" zPosition="1" size="170,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
                                <widget name="checkList" position="5,50" zPosition="2" size="693,483" scrollbarMode="showOnDemand"/>
                        </screen>"""

        def __init__(self, session):
                Screen.__init__(self, session)
                self.setTitle(_("Select Softcam.key Path"))

                self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "MenuActions"],
                {
                        "cancel": self.exit,
                        "red": self.exit,
                        "green": self.saveSelection,
                        "ok": self.okClicked,
                        "left": self.left,
                        "right": self.right,
                        "down": self.down,
                        "up": self.up
                }, -1)

                self["key_red"] = StaticText(_("Close"))
                self["key_green"] = StaticText(_("Save"))

                self["list_head"] = Label()

                self.filelist = FileList("/", matchingPattern="")
                self["checkList"] = self.filelist
                self.onLayoutFinish.append(self.layoutFinished)
                self.updateHead()

        def layoutFinished(self):
                idx = 0
                self["checkList"].moveToIndex(idx)

        def up(self):
                self["checkList"].up()
                self.updateHead()

        def down(self):
                self["checkList"].down()
                self.updateHead()

        def left(self):
                self["checkList"].pageUp()
                self.updateHead()

        def right(self):
                self["checkList"].pageDown()
                self.updateHead()

        def updateHead(self):
                curdir = self["checkList"].getCurrentDirectory()
                self["list_head"].setText(curdir)

        def saveSelection(self):
                self.selectedFiles = self["checkList"].getCurrentDirectory()
                config.plugins.KeyAdder.custom_softcampath.value = self.selectedFiles
                config.plugins.KeyAdder.custom_softcampath.save()
                configfile.save()
                softcamkey = os_path.join(config.plugins.KeyAdder.custom_softcampath.value, "SoftCam.Key")
                if not os_path.exists(softcamkey):
                        os.system("mkdir -p %s" % config.plugins.KeyAdder.custom_softcampath.value)
                self.close(True)

        def okClicked(self):
                if self.filelist.canDescent():
                        self.filelist.descent()

        def exit(self):
                self.close(True)


class HexKeyBoard(VirtualKeyBoardKeyAdder):
      def __init__(self, session, title="", **kwargs):
            VirtualKeyBoardKeyAdder.__init__(self, session, title, **kwargs)

            self.locales = { "hex" : [_("HEX"), _("HEX"), self.keys_list] }
            self.lang = "hex"
            self.max_key = all
            self.setLang()
            self.buildVirtualKeyBoard()

      def setLang(self):
            if config.plugins.KeyAdder.AddkeyStyle.value == "auto":
                self.keys_list = [[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
                                    [u"PASTE", u"A", u"B", u"C", u"D", u"E", u"F", u"OK", u"LEFT", u"RIGHT", u"CLEAR", u"Clean/PASTE"]]
            else:
                self.keys_list = [[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
                                    [u"PASTE", u"A", u"B", u"C", u"D", u"E", u"F", u"OK", u"LEFT", u"RIGHT", u"CLEAR", u"SPACE"]]

def saveKey(key):
        try:
            if key != None:
                ## read save keys file
                if not fileExists(save_key):
                        os.system("touch %s" % save_key)
                        with open(save_key, "w") as f:
                                f.writelines(str(key.replace("|", "") + "\n"))
                                return
                ## Replace new key with None value
                with open(save_key, "r") as r:
                        for line in r:
                                line = line.strip()
                                if line == "None":
                                        with open(save_key, "w") as r:
                                                r.write(str(key.replace("|", "") + "\n"))
                                                return
                with open(save_key, "r") as file:
                        keyslist = [line.rstrip("\n") for line in file]
                ## check current key if in list
                currentkey = str(key.replace("|", ""))
                if currentkey in keyslist:
                        print("[KeyAdder] ****** Key already in save list")
                        return
                ## count numbers of lines
                lines = 1
                linemubers = config.plugins.KeyAdder.savenumber.value
                with open(save_key, "r") as file:
                        for i, l in enumerate(file):
                                lines = i + 1
                ## save key in line 5 If the specified number is exceeded
                with open(save_key, "r") as file:
                        data = file.readlines()
                print("[KeyAdder] lines ************** %s" % lines)
                if lines == linemubers:
                        with open(save_key, "w") as f:
                                for i,line in enumerate(data,1):
                                        if i == linemubers:
                                                f.writelines("%s" % currentkey)
                                        else:
                                                f.writelines("%s" % line)
                else:
                        with open(save_key, "a") as f:
                                f.writelines(str(key.replace("|", "") + "\n"))
        except Exception as error:
                trace_error()

table = array("L")
for byte in range(256):
      crc = 0
      for bit in range(8):
                if (byte ^ crc) & 1:
                        crc = (crc >> 1) ^ 0xEDB88320
                else:
                        crc >>= 1
                byte >>= 1
      table.append(crc)

def crc32(string):
      value = 0x2600 ^ 0xffffffff
      for ch in string:
                if PY3:
                        value = table[(ch ^ value) & 0xff] ^ (value >> 8)
                else:
                        value = table[(ord(ch) ^ value) & 0xff] ^ (value >> 8)
      return value ^ 0xffffffff

def crc323(string):
      value = 0xe00 ^ 0xffffffff
      for ch in string:
                if PY3:
                        value = table[(ch ^ value) & 0xff] ^ (value >> 8)
                else:
                        value = table[(ord(ch) ^ value) & 0xff] ^ (value >> 8)
      return value ^ 0xffffffff

def hasCAID(session):
      service = session.nav.getCurrentService()
      info = service and service.info()
      caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
      if caids and 0xe00 in caids: return True
      if caids and 0x2600 in caids: return True
      if caids and 0x604 in caids: return True
      if caids and 0x1010 in caids: return True
      try:
            return eDVBDB.getInstance().hasCAID(ref, 0xe00) # PowerVU
      except:
            pass
      try:
            return eDVBDB.getInstance().hasCAID(ref, 0x2600) # BISS     
      except:
            pass
      try:
            return eDVBDB.getInstance().hasCAID(ref, 0x604) # IRDETO
      except:
            pass
      try:
            return eDVBDB.getInstance().hasCAID(ref, 0x1010) # Tandberg
      except:
            pass
      return False

def getCAIDS(session):
      service = session.nav.getCurrentService()
      info = service and service.info()
      caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
      caidstr = "None"
      if caids: caidstr = " ".join(["%04X (%d)" % (x,x) for x in sorted(caids)])
      return caidstr

def keymenu(session, service=None):
      service = session.nav.getCurrentService()
      info = service and service.info()
      caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
      SoftCamKey = findSoftCamKey()
      ref = session.nav.getCurrentlyPlayingServiceReference()
      if config.plugins.KeyAdder.AddkeyStyle.value == "auto":
        if not os_path.exists(SoftCamKey):
                session.open(MessageBox, _("Emu misses SoftCam.Key (%s)" % SoftCamKey), MessageBox.TYPE_ERROR)
        elif not hasCAID(session):
                session.open(MessageBox, _("CAID is missing for service (%s) CAIDS: %s\nOr the channel is FAT" % (ref.toString(), getCAIDS(session))), MessageBox.TYPE_ERROR)
        else:
            if caids and 0xe00 in caids:
                    session.openWithCallback(boundFunction(setKeyCallback, session, SoftCamKey), HexKeyBoard,
                        title=_("Please enter new key:"), text=findKeyPowerVU(session, SoftCamKey))
            elif caids and 0x2600 in caids:
                    session.openWithCallback(boundFunction(setKeyCallback, session, SoftCamKey), HexKeyBoard,
                        title=_("Please enter new key:"), text=findKeyBISS(session, SoftCamKey))
            elif caids and 0x604 in caids:
                    session.openWithCallback(boundFunction(setKeyCallback, session, SoftCamKey), HexKeyBoard,
                        title=_("Please enter new key:"), text=findKeyIRDETO(session, SoftCamKey))
            elif caids and 0x1010 in caids:
                    newcaid=getnewcaid(SoftCamKey)
                    session.openWithCallback(boundFunction(setKeyCallback, session, SoftCamKey), HexKeyBoard,
                        title=_("Please enter new key for caid:"+newcaid), text=findKeyTandberg(session, SoftCamKey))
      else:
        session.openWithCallback(boundFunction(setKeyCallback, session, SoftCamKey), HexKeyBoard, title=_("Please enter new key:"))

def setKeyCallback(session, SoftCamKey, key):
      global newcaid
      service = session.nav.getCurrentService()
      info = service and service.info()
      caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
      SoftCamKey = findSoftCamKey()
      ref = session.nav.getCurrentlyPlayingServiceReference()
      if config.plugins.KeyAdder.AddkeyStyle.value == "auto":
        if key: key = "".join(c for c in key if c in hexdigits).upper()
        saveKey(key)
        if key and len(key) == 14:
                if key != findKeyPowerVU(session, SoftCamKey, ""): # no change was made ## PowerVU
                    keystr = "P %s 00 %s" % (getonidsid(session), key)
                    name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
                    datastr = "\n%s ; Added on %s for %s at %s" % (keystr, datetime.now(), name, getOrb(session))
                    restartmess = "\n*** Need to Restart emu TO Active new key ***\n"
                    open(SoftCamKey, "a").write(datastr)
                    if config.plugins.KeyAdder.autorestart.value:
                        restartemu()
                    session.open(MessageBox, _("PowerVU key saved sucessfuly!%s %s" % (datastr, restartmess)), MessageBox.TYPE_INFO, timeout=10)
        elif key and len(key) == 16:
                if 0x2600 in caids:
                    if key != findKeyBISS(session, SoftCamKey, ""): # no change was made ## BISS
                            if getOrb(session) == "21.5E" or getOrb(session) == "21.6E" : # get keystr by (sid & vpid)
                                sid = info.getInfo(iServiceInformation.sSID)
                                vpid = info.getInfo(iServiceInformation.sVideoPID)
                                sid_part = "{:04X}".format(sid)
                                vpid_part = "{:04X}".format(vpid)
                                keystr = "F %s%s 00 %s" % (sid_part, vpid_part, key)
                            else: # get keystr by (Hash)
                                keystr = "F %08X 00 %s" % (getHash(session), key)
                            name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
                            datastr = "\n%s ; Added on %s for %s at %s" % (keystr, datetime.now(), name, getOrb(session))
                            restartmess = "\n*** Need to Restart emu TO Active new key ***\n"
                            open(SoftCamKey, "a").write(datastr)
                            if config.plugins.KeyAdder.autorestart.value:
                                restartemu()
                            session.open(MessageBox, _("BISS key saved sucessfuly!%s %s" % (datastr, restartmess)), MessageBox.TYPE_INFO, timeout=10)
                else:
                    if key != findKeyTandberg(session, SoftCamKey, ""): # no change was made ## Tandberg
                            newcaid=getnewcaid(SoftCamKey)
                            keystr = "T %s 01 %s" % (newcaid, key) 
                            name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
                            datastr = "\n%s ; Added on %s for %s at %s" % (keystr, datetime.now(), name, getOrb(session))
                            restartmess = "\n*** Need to Restart emu TO Active new key ***\n"       
                            open(SoftCamKey, "a").write(datastr)
                            if config.plugins.KeyAdder.autorestart.value:
                                restartemu()
                            session.open(MessageBox, _("Tandberg key saved sucessfuly!%s %s" % (datastr, restartmess)), MessageBox.TYPE_INFO, timeout=10)
        elif key and len(key) == 32:
                if key != findKeyIRDETO(session, SoftCamKey, ""): # no change was made ## IRDETO
                    keystr = "I 0604 M1 %s" % key
                    name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
                    datastr = "\n%s ; Added on %s for %s at %s" % (keystr, datetime.now(), name, getOrb(session))
                    restartmess = "\n*** Need to Restart emu TO Active new key ***\n"
                    open(SoftCamKey, "a").write(datastr)
                    if config.plugins.KeyAdder.autorestart.value:
                        restartemu()
                    session.open(MessageBox, _("IRDETO key saved sucessfuly!%s %s" % (datastr, restartmess)), MessageBox.TYPE_INFO, timeout=10)
        elif key:
                session.openWithCallback(boundFunction(setKeyCallback, session,SoftCamKey), HexKeyBoard,
                    title=_("Invalid key, length is %d" % len(key)), text=key.ljust(16,"*"))
      else:
        if key != None:
            saveKey(key)
            keystr = "%s" % key
            name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
            datastr = "\n%s ; Added on %s for %s at %s" % (keystr.replace("|", ""), datetime.now(), name, getOrb(session))
            restartmess = "\n*** Need to Restart emu TO Active new key ***\n"
            open(SoftCamKey, "a").write(datastr)
            if config.plugins.KeyAdder.autorestart.value:
                restartemu()
            session.open(MessageBox, _("key saved sucessfuly!%s %s" % (datastr, restartmess)), MessageBox.TYPE_INFO, timeout=10)

def getHash(session):
      ref = session.nav.getCurrentlyPlayingServiceReference()
      sid = ref.getUnsignedData(1)
      tsid = ref.getUnsignedData(2)
      onid = ref.getUnsignedData(3)
      namespace = ref.getUnsignedData(4) | 0xA0000000

      # check if we have stripped or full namespace
      if namespace & 0xFFFF == 0:
            # Namespace without frequency - Calculate hash with srvid, tsid, onid and namespace
            data = "%04X%04X%04X%08X" % (sid, tsid, onid, namespace)
      else:
            # Full namespace - Calculate hash with srvid and namespace only
            data = "%04X%08X" % (sid, namespace)
      return crc32(binascii.unhexlify(data))

def getonidsid(session):
      ref = session.nav.getCurrentlyPlayingServiceReference()
      sid = ref.getUnsignedData(1)
      onid = ref.getUnsignedData(3)
      return "%04X%04X" % (onid, sid)

def getOrb(session):
      ref = session.nav.getCurrentlyPlayingServiceReference()
      orbpos = ref.getUnsignedData(4) >> 16
      if orbpos == 0xFFFF:
            desc = "C"
      elif orbpos == 0xEEEE:
            desc = "T"
      else:
            if orbpos > 1800:
                  orbpos = 3600 - orbpos
                  h = "W"
            else:
                  h = "E"
            desc = ("%d.%d%s") % (orbpos / 10, orbpos % 10, h)
      return desc

def findKeyBISS(session, SoftCamKey, key="0000000000000000"):
      if getOrb(session) == "21.5E" or getOrb(session) == "21.6E" :
        service = session.nav.getCurrentService()
        info = service and service.info()
        sid = info.getInfo(iServiceInformation.sSID)
        vpid = info.getInfo(iServiceInformation.sVideoPID)
        sid_part = "{:04X}".format(sid)
        vpid_part = "{:04X}".format(vpid)
        keystart = "F %s%s" % (sid_part, vpid_part)
      else:
        keystart = "F %08X" % getHash(session)
      keyline = ""
      if PY3:
        with open(SoftCamKey,"r", errors="ignore") as f:
            for line in f:
                  if line.startswith(keystart):
                        keyline = line
      else:
        with open(SoftCamKey, "rU") as f:
            for line in f:
                  if line.startswith(keystart):
                        keyline = line
      if keyline:
            return keyline.split()[3]
      else:
            return key

def findKeyPowerVU(session, SoftCamKey, key="00000000000000"):
      keystart = "P %s" % getonidsid(session)
      keyline = ""
      if PY3:
        with open(SoftCamKey,"r", errors="ignore") as f:
            for line in f:
                  if line.startswith(keystart):
                        keyline = line
      else:
        with open(SoftCamKey, "rU") as f:
            for line in f:
                  if line.startswith(keystart):
                        keyline = line
      if keyline:
            return keyline.split()[3]
      else:
            return key

def findKeyTandberg(session, SoftCamKey, key="0000000000000000"):
      keystart = "T 0001"
      keyline = ""
      if PY3:
        with open(SoftCamKey,"r", errors="ignore") as f:
            for line in f:
                  if line.startswith(keystart):
                        keyline = line
      else:
        with open(SoftCamKey, "rU") as f:
            for line in f:
                  if line.startswith(keystart):
                        keyline = line
      if keyline:
            return keyline.split()[3]
      else:
            return key

def findKeyIRDETO(session, SoftCamKey, key="00000000000000000000000000000000"):
      keystart = "I 0604"
      keyline = ""
      if PY3:
        with open(SoftCamKey,"r", errors="ignore") as f:
            for line in f:
                  if line.startswith(keystart):
                        keyline = line
      else:
        with open(SoftCamKey, "rU") as f:
            for line in f:
                  if line.startswith(keystart):
                        keyline = line
      if keyline:
            return keyline.split()[3]
      else:
            return key


class keyAdder_setup(ConfigListScreen, Screen):
        if reswidth == 2560:
                if DreamOS():
                        skin = """
                                <screen name="keyAdder_setup" position="center,center" size="840,708" title="keyAdder setup">
                                        <!--widget source="Title" position="5,5" size="826,50" render="Label" font="Regular;35" foregroundColor="#00ffa500" backgroundColor="#16000000" transparent="1" halign="center"/-->
                                        <widget source="global.CurrentTime" render="Label" position="5,5" size="826,50" font="Regular;35" halign="right" foregroundColor="#00ffa500" backgroundColor="#16000000" transparent="1">
                                                <convert type="ClockToText">Format:%d-%m-%Y    %H:%M:%S</convert>
                                        </widget>
                                        <widget name="config" position="28,70" size="780,508" scrollbarMode="showOnDemand"/>
                                        <widget source="help" render="Label" position="10,566" size="818,90" font="Regular;35" foregroundColor="#00e5b243" backgroundColor="#16000000" valign="center" halign="center" transparent="1" zPosition="5"/>
                                        <eLabel text="" foregroundColor="#00ff2525" backgroundColor="#00ff2525" size="235,5" position="123,695" zPosition="-10"/>
                                        <eLabel text="" foregroundColor="#00389416" backgroundColor="#00389416" size="235,5" position="445,695" zPosition="-10"/>
                                        <widget render="Label" source="key_red" position="123,655" size="235,40" zPosition="5" valign="center" halign="center" backgroundColor="#16000000" font="Regular;35" transparent="1" foregroundColor="#00ffffff" shadowColor="black"  />
                                        <widget render="Label" source="key_green" position="445,655" size="235,40" zPosition="5" valign="center" halign="center" backgroundColor="#16000000" font="Regular;35" transparent="1" foregroundColor="#00ffffff" shadowColor="black" />
                                </screen>"""
                else:
                        skin = """
                                <screen name="keyAdder_setup" position="center,center" size="840,560" title="keyAdder setup">
                                        <!--widget source="Title" position="5,5" size="826,50" render="Label" font="Regular;35" foregroundColor="#00ffa500" backgroundColor="#16000000" transparent="1" halign="center"/-->
                                        <widget source="global.CurrentTime" render="Label" position="5,5" size="826,50" font="Regular;35" halign="right" foregroundColor="#00ffa500" backgroundColor="#16000000" transparent="1">
                                                <convert type="ClockToText">Format:%d-%m-%Y    %H:%M:%S</convert>
                                        </widget>
                                        <widget name="config" font="Regular;35" secondfont="Regular;35" itemHeight="45" position="28,70" size="780,433" scrollbarMode="showOnDemand"/>
                                        <widget source="help" render="Label" position="10,420" size="818,90" font="Regular;35" foregroundColor="#00e5b243" backgroundColor="#16000000" valign="center" halign="center" transparent="1" zPosition="5"/>
                                        <eLabel text="" foregroundColor="#00ff2525" backgroundColor="#00ff2525" size="235,5" position="123,550" zPosition="-10"/>
                                        <eLabel text="" foregroundColor="#00389416" backgroundColor="#00389416" size="235,5" position="445,550" zPosition="-10"/>
                                        <widget render="Label" source="key_red" position="123,515" size="235,40" zPosition="5" valign="center" halign="center" backgroundColor="#16000000" font="Regular;35" transparent="1" foregroundColor="#00ffffff" shadowColor="black"  />
                                        <widget render="Label" source="key_green" position="445,515" size="235,40" zPosition="5" valign="center" halign="center" backgroundColor="#16000000" font="Regular;35" transparent="1" foregroundColor="#00ffffff" shadowColor="black" />
                                </screen>"""
        elif reswidth == 1920:
                if DreamOS():
                        skin = """
                                <screen name="keyAdder_setup" position="center,center" size="1040,560" title="keyAdder setup">
                                        <!--widget source="Title" position="5,5" size="1022,50" render="Label" font="Regular;28" foregroundColor="#00ffa500" backgroundColor="#16000000" transparent="1" halign="center"/-->
                                        <widget source="global.CurrentTime" render="Label" position="5,5" size="1022,50" font="Regular;28" halign="right" foregroundColor="#00ffa500" backgroundColor="#16000000" transparent="1">
                                                <convert type="ClockToText">Format:%d-%m-%Y    %H:%M:%S</convert>
                                        </widget>
                                        <widget name="config" position="18,70" size="1005,344" scrollbarMode="showOnDemand"/>
                                        <widget source="help" render="Label" position="18,425" size="1000,90" font="Regular;28" foregroundColor="#00e5b243" backgroundColor="#16000000" valign="center" halign="center" transparent="1" zPosition="5"/>
                                        <eLabel text="" foregroundColor="#00ff2525" backgroundColor="#00ff2525" size="235,5" position="223,550" zPosition="-10"/>
                                        <eLabel text="" foregroundColor="#00389416" backgroundColor="#00389416" size="235,5" position="585,550" zPosition="-10"/>
                                        <widget render="Label" source="key_red" position="223,515" size="235,40" zPosition="5" valign="center" halign="center" backgroundColor="#16000000" font="Regular;28" transparent="1" foregroundColor="#00ffffff" shadowColor="black"/>
                                        <widget render="Label" source="key_green" position="585,515" size="235,40" zPosition="5" valign="center" halign="center" backgroundColor="#16000000" font="Regular;28" transparent="1" foregroundColor="#00ffffff" shadowColor="black" shadowOffset="-1,-1"/>
                                </screen>"""
                else:
                        skin = """
                                <screen name="keyAdder_setup" position="center,center" size="1040,560" title="keyAdder setup">
                                        <!--widget source="Title" position="5,5" size="826,50" render="Label" font="Regular;28" foregroundColor="#00ffa500" backgroundColor="#16000000" transparent="1" halign="center"/-->
                                        <widget source="global.CurrentTime" render="Label" position="5,5" size="1022,50" font="Regular;28" halign="right" foregroundColor="#00ffa500" backgroundColor="#16000000" transparent="1">
                                                <convert type="ClockToText">Format:%d-%m-%Y    %H:%M:%S</convert>
                                        </widget>
                                        <widget name="config" font="Regular;28" secondfont="Regular;28" itemHeight="45" position="18,70" size="1005,344" scrollbarMode="showOnDemand"/>
                                        <widget source="help" render="Label" position="18,425" size="1000,90" font="Regular;28" foregroundColor="#00e5b243" backgroundColor="#16000000" valign="center" halign="center" transparent="1" zPosition="5"/>
                                        <eLabel text="" foregroundColor="#00ff2525" backgroundColor="#00ff2525" size="235,5" position="223,550" zPosition="-10"/>
                                        <eLabel text="" foregroundColor="#00389416" backgroundColor="#00389416" size="235,5" position="585,550" zPosition="-10"/>
                                        <widget render="Label" source="key_red" position="223,515" size="235,40" zPosition="5" valign="center" halign="center" backgroundColor="#16000000" font="Regular;28" transparent="1" foregroundColor="#00ffffff" shadowColor="black"/>
                                        <widget render="Label" source="key_green" position="585,515" size="235,40" zPosition="5" valign="center" halign="center" backgroundColor="#16000000" font="Regular;28" transparent="1" foregroundColor="#00ffffff" shadowColor="black" shadowOffset="-1,-1"/>
                                </screen>"""
        else:
                skin = """
                        <screen name="keyAdder_setup" position="center,center" size="620,398" title="keyAdder setup">
                                <!--widget source="Title" position="5,5" size="371,30" render="Label" font="Regular;25" foregroundColor="#00ffa500" backgroundColor="#16000000" transparent="1" halign="center"/!-->
                                <widget source="global.CurrentTime" render="Label" position="5,5" size="371,30" font="Regular;25" halign="right" foregroundColor="#00ffa500" backgroundColor="#16000000" transparent="1">
                                        <convert type="ClockToText">Format:%d-%m-%Y    %H:%M:%S</convert>
                                </widget>
                                <widget name="config" position="15,45" size="584,303" scrollbarMode="showOnDemand"/>
                                <widget source="help" render="Label" position="15,826" size="1187,199" font="Regular;25" foregroundColor="#00e5b243" backgroundColor="#16000000" valign="center" halign="center" transparent="1" zPosition="5"/>
                                <eLabel text="" foregroundColor="#00ff2525" backgroundColor="#00ff2525" size="150,3" position="108,394" zPosition="-10"/>
                                <eLabel text="" foregroundColor="#00389416" backgroundColor="#00389416" size="150,3" position="379,394" zPosition="-10"/>
                                <widget render="Label" source="key_red" position="108,360" size="150,35" zPosition="5" valign="center" halign="left" backgroundColor="#16000000" font="Regular;28" transparent="1" foregroundColor="#00ffffff" shadowColor="black"/>
                                <widget render="Label" source="key_green" position="379,360" size="150,35" zPosition="5" valign="center" halign="left" backgroundColor="#16000000" font="Regular;28" transparent="1" foregroundColor="#00ffffff" shadowColor="black" shadowOffset="-1,-1"/>
                        </screen>"""

        def __init__(self, session):
                self.session = session
                Screen.__init__(self, session)
                self.list = []
                ConfigListScreen.__init__(self, self.list)

                self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
                {
                        "cancel": self.cancel,
                        "red": self.cancel,
                        "green": self.save,
                        "left": self.keyLeft,
                        "right": self.keyRight,
                }, -2)

                # Impoert class KeyAdderUpdate()
                self.KeyAdderUpdate = KeyAdderUpdate(session)
                # Impoert class AutoStartTimer()
                #self.AutoStartTimer = AutoStartTimer(session)

                self["key_red"] = StaticText(_("Exit"))
                self["key_green"] = StaticText(_("Save"))
                self["help"] = StaticText()
                self.initConfig()
                self.createSetup()
                self.onLayoutFinish.append(self.setWindowTitle)

        def setWindowTitle(self):
                self.setTitle("KeyAdder Setup V%s" % VER)

        def initConfig(self):
                self.EnablecheckUpdate = getConfigListEntry(_("Enable checking for Online Update"), config.plugins.KeyAdder.update, _(" This option to Enable or Disable checking for Online Update"))
                self.Enablesoftcampath = getConfigListEntry(_("Enable custom softCam file path"), config.plugins.KeyAdder.softcampath, _("This option to Enable custom softCam file path"))
                self.Enableautorestart = getConfigListEntry(_("Enable auto restart emu"), config.plugins.KeyAdder.autorestart, _(" This option to Enable or Disable auto restart emus after add new keys"))
                self.EnablekeyboardStyle = getConfigListEntry(_("Change Add keys Style"), config.plugins.KeyAdder.AddkeyStyle, _("This option allows keys to be entered automatically or manually "))
                self.AddkeyStyle = getConfigListEntry(_("Change VirtualKeyboard Style"), config.plugins.KeyAdder.keyboardStyle, _("This option to change Enable VirtualKeyboard Style appear"))
                self.Selectsavenumber = getConfigListEntry(_("Choose keys save numbers"), config.plugins.KeyAdder.savenumber, _("This option to choose how many keys need to save it inside savefile"))
                self.Auto_enabled = getConfigListEntry(_("Automatic softcam.key update"), config.plugins.KeyAdder.Autodownload_enabled, _("This option to change Enable VirtualKeyboard Style appear"))
                self.Auto_wakeup = getConfigListEntry(_("Choose update start time"), config.plugins.KeyAdder.wakeup, _("This option to choose the time hour to start download file"))
                self.Auto_site = getConfigListEntry(_("Choose site to download file from it"), config.plugins.KeyAdder.Autodownload_sitelink, _("This option to choose the site you want to download file from it"))
                self.Show_Autoflash = getConfigListEntry(_("Enable Show message after finish download file"), config.plugins.KeyAdder.Show_Autoflash, _("This option to Showing message of successfully after finish download file"))

                self.org_wakeup = config.plugins.KeyAdder.wakeup.getValue()

        def createSetup(self):
                self.list = []
                self.list.append(self.Auto_enabled)
                if config.plugins.KeyAdder.Autodownload_enabled.value:
                    self.list.append(self.Auto_wakeup)
                    self.list.append(self.Auto_site)
                    self.list.append(self.Show_Autoflash)
                self.list.append(self.Enablesoftcampath)
                self.list.append(self.Enableautorestart)
                self.list.append(self.EnablekeyboardStyle)
                self.list.append(self.AddkeyStyle)
                self.list.append(self.Selectsavenumber)

                self["config"].list = self.list
                self["config"].l.setList(self.list)
                self["config"].onSelectionChanged.append(self.updateHelp)

        def updateHelp(self):
                cur = self["config"].getCurrent()
                if cur:
                        self["help"].text = cur[2]

        def keyLeft(self):
                ConfigListScreen.keyLeft(self)
                self.createSetup()

        def keyRight(self):
                ConfigListScreen.keyRight(self)
                self.createSetup()

        def cancel(self):
                self.close()

        def save(self):
                global autoStartTimer
                for x in self["config"].list:
                        if len(x)>1:
                                x[1].save()
                configfile.save()
                if autoStartTimer != None:
                        autoStartTimer.update()
                        if self.org_wakeup != config.plugins.KeyAdder.wakeup.getValue():
                                self.changedFinished()
                self.close()

        def changedFinished(self):
                self.session.openWithCallback(self.ExecuteRestart, MessageBox, _("You need to restart the GUI") + "\n" + _("Do you want to restart now?"), MessageBox.TYPE_YESNO)
                self.close()

        def ExecuteRestart(self, result):
                if result:
                        Standby.quitMainloop(3)
                else:
                        self.close()


autoStartTimer = None

class AutoStartTimer:
    def __init__(self, session):
        self.session = session
        self.timer = eTimer()
        try:
            self.timer_conn = self.timer.timeout.connect(self.onTimer)
        except:
            self.timer.callback.append(self.onTimer)
        self.update()

    def getWakeTime(self):
        import time
        if config.plugins.KeyAdder.Autodownload_enabled.value:
            clock = config.plugins.KeyAdder.wakeup.value
            nowt = time.time()
            now = time.localtime(nowt)
            return int(time.mktime((now.tm_year, now.tm_mon, now.tm_mday, clock[0], clock[1], 0, now.tm_wday, now.tm_yday, now.tm_isdst)))
        else:
            return -1

    def update(self, atLeast=0):
        import time
        self.timer.stop()
        wake = self.getWakeTime()
        nowtime = time.time()
        if wake > 0:
            if wake < nowtime + atLeast:
                # Tomorrow.
                wake += 24 * 3600
            next = wake - int(nowtime)
            if next > 3600:
                next = 3600
            if next <= 0:
                next = 60
            self.timer.startLongTimer(next)
        else:
            wake = -1
        return wake

    def onTimer(self):
        import time
        self.timer.stop()
        now = int(time.time())
        wake = self.getWakeTime()
        atLeast = 0
        if abs(wake - now) < 60:
            self.runUpdate()
            atLeast = 60
        self.update(atLeast)

    def runUpdate(self):
        print("\n *********** Auto updating Softcam.key file************ \n")
        SoftCamKey = findSoftCamKey()
        agent = '--header="User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/8.0 Safari/600.1.17"'
        crt = "--debug --no-check-certificate"
        command = ""
        Site_Value = config.plugins.KeyAdder.Autodownload_sitelink.value
        if Site_Value == "smcam":
                myurl = "https://raw.githubusercontent.com/smcam/s/main/SoftCam.Key"
                os.system("wget -O %s %s" % (SoftCamKey, myurl))
        elif Site_Value == "softcam.org":
                myurl = "http://www.softcam.org/deneme6.php?file=SoftCam.Key"
                os.system("wget -O %s %s" % (SoftCamKey, myurl))
        elif Site_Value == "enigma1969":
                myurl = "https://docs.google.com/uc?export=download&id=1aujij43w7qAyPHhfBLAN9sE-BZp8_AwI&export"
                os.system("wget %s -O %s %s" % (crt, SoftCamKey, myurl))
        elif Site_Value == "MOHAMED_OS":
                myurl = "https://raw.githubusercontent.com/MOHAMED19OS/SoftCam_Emu/main/SoftCam.Key"
                os.system("wget -O %s %s" % (SoftCamKey, myurl))
        elif Site_Value == "MOHAMED_Nasr":
                myurl = "https://raw.githubusercontent.com/popking159/softcam/master/SoftCam.Key"
                os.system("wget -O %s %s" % (SoftCamKey, myurl))
        elif Site_Value == "Serjoga":
                myurl = "http://raw.githubusercontent.com/audi06/SoftCam.Key_Serjoga/master/SoftCam.Key"
                os.system("wget -O %s %s" % (SoftCamKey, myurl))
        elif Site_Value == "Novaler4k":
                myurl = "http://novaler.homelinux.com/SoftCam.Key"
                os.system("wget -O %s %s" % (SoftCamKey, myurl))
        else:
                close()
        if config.plugins.KeyAdder.Show_Autoflash.value:
            try:
                file_size = os.path.getsize(SoftCamKey)
            except Exception as error:
                trace_error()
            if fileExists(SoftCamKey) and file_size > int(0):
                self.session.open(MessageBox, _("Download the file from the (%s) successfully !\n\nTo the path (%s) !" % (Site_Value, SoftCamKey)), MessageBox.TYPE_INFO)
            else:
                self.session.open(MessageBox, _("Download the file from the (%s) not successfully !" % Site_Value), MessageBox.TYPE_ERROR)


def main(session=None, **kwargs):
    session.open(KeyAdderUpdate)
    global autoStartTimer
    if session != None:
        if autoStartTimer is None:
            autoStartTimer = AutoStartTimer(session)
    return


def Plugins(**kwargs):
    #NAME = "KeyAdder V{}".format(VER)
    NAME = "KeyAdder"
    ICON = "plugin.png"
    DES = "Manually add Key to current service"
    Descriptors = []
    Descriptors.append(PluginDescriptor(name=NAME,description=DES,icon=ICON,where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main, needsRestart = False))
    return Descriptors
