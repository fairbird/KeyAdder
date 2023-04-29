#!/usr/bin/python
# -*- coding: utf-8 -*-
# Code By RAED and mfaraj57

from enigma import eConsoleAppContainer, eDVBDB, iServiceInformation, eTimer, loadPNG, getDesktop, RT_WRAP, RT_HALIGN_LEFT, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.config import config, getConfigListEntry, ConfigText, ConfigSelectionNumber, ConfigSubsection, ConfigYesNo, configfile, ConfigSelection
from Components.ConfigList import ConfigListScreen
from Plugins.Plugin import PluginDescriptor
from Tools.BoundFunction import boundFunction
from ServiceReference import ServiceReference
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
from shutil import copyfile
from Plugins.Extensions.KeyAdder.tools.downloader import getversioninfo, imagedownloadScreen

# python3
from os import path as os_path
from Plugins.Extensions.KeyAdder.tools.Console import Console
from Plugins.Extensions.KeyAdder.tools.compat import PY3

VER = getversioninfo()

reswidth = getDesktop(0).size().width()
config.plugins.KeyAdder = ConfigSubsection()
config.plugins.KeyAdder.update = ConfigYesNo(default=True)
config.plugins.KeyAdder.lastcaid = ConfigText(default="0", fixed_size=False)
config.plugins.KeyAdder.softcampath = ConfigYesNo(default=False) #False = Auto Detecte path
config.plugins.KeyAdder.custom_softcampath = ConfigText(default="/usr/keys", visible_width = 250, fixed_size = False)
config.plugins.KeyAdder.keyboardStyle = ConfigSelection(default = "Style2", choices = [("Style1", _("Old Style keyboard")),("Style2", _("New Style keyboard"))])
config.plugins.KeyAdder.savenumber = ConfigSelectionNumber(1, 20, 1, default=5)
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

class KeyAdderUpdate(Screen):
    if reswidth == 1920:
           skin = '''
                <screen name="KeyAdderUpdate" position="center,center" size="704,424" backgroundColor="#16000000" title="KeyAdderUpdate">
                        <widget name="pathfile" position="center,10" size="650,45" font="Regular;28" foregroundColor="#00cccc40" backgroundColor="#16000000"/>
                        <widget name="menu" position="center,55" size="650,280" backgroundColor="#16000000"/>
                        <eLabel position="25,360" size="110,50" backgroundColor="#00ff0000" zPosition="1"/>
                        <eLabel text="MENU" font="Regular;30" position="28,364" size="103,43" foregroundColor="#00000000" backgroundColor="#00ffffff" zPosition="3" valign="center" halign="center"/>
                        <eLabel text="Press Menu for more options" font="Regular;33" position="148,360" size="546,50" foregroundColor="#00ffffff" backgroundColor="#00000000" zPosition="2" valign="center"/>
                </screen>'''
    else:
           skin = '''
                <screen name="KeyAdderUpdate" position="center,center" size="476,306" backgroundColor="#16000000" title="KeyAdderUpdate">
                        <widget name="pathfile" position="10,5" size="458,61" font="Regular;24" foregroundColor="#00cccc40" backgroundColor="#16000000"/>
                        <widget name="menu" position="10,75" size="450,173" backgroundColor="#16000000"/>
                        <eLabel position="15,259" size="80,40" backgroundColor="#00ff0000" zPosition="1"/>
                        <eLabel text="MENU" font="Regular;26" position="18,261" size="74,35" foregroundColor="#00000000" backgroundColor="#00ffffff" zPosition="3" valign="center" halign="center"/>
                        <eLabel text="Press Menu for more options" font="Regular;25" position="104,259" size="369,40" foregroundColor="#00ffffff" backgroundColor="#00000000" zPosition="2" valign="center"/>
                </screen>'''

    def __init__(self, session, title="", datalist = []):
        Screen.__init__(self, session)
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
        list1 = []
        list1.append(("smcam (Always Updated)", "smcam"))
        list1.append(("softcam.org (Always Updated)", "softcam.org"))
        list1.append(("enigma1969 (Always Updated)", "enigma1969"))
        list1.append(("MOHAMED_OS (Always Updated)", "MOHAMED_OS"))
        list1.append(("MOHAMED_Nasr (Always Updated)", "MOHAMED_Nasr"))
        list1.append(("Serjoga", "Serjoga"))
        self.session.openWithCallback(self.Downloadkeys, ChoiceBox, _("select site to downloan file"), list1)
           
    def Downloadkeys(self, select, SoftCamKey=None):
        cmdlist = []
        SoftCamKey = findSoftCamKey()
        agent='--header="User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/8.0 Safari/600.1.17"'
        crt="--debug --no-check-certificate"
        command=""
        if select: 
            if select[1] == "softcam.org":
                myurl = "http://www.softcam.org/deneme6.php?file=SoftCam.Key"
                command = "wget -O %s %s" % (SoftCamKey, myurl)
                self.session.open(imagedownloadScreen,"softcam",SoftCamKey, myurl)
            elif select[1] == "MOHAMED_OS":
                myurl = "https://raw.githubusercontent.com/MOHAMED19OS/SoftCam_Emu/main/Enigma2/SoftCam.Key"
                command = "wget -q %s %s %s %s" % (crt, agent, SoftCamKey, myurl)
                self.session.open(imagedownloadScreen,"softcam",SoftCamKey,myurl)
            elif select[1] == "MOHAMED_Nasr":
                myurl = "https://raw.githubusercontent.com/popking159/softcam/master/SoftCam.Key"
                command = "wget -q %s %s %s %s" % (crt, agent, SoftCamKey, myurl)
                self.session.open(imagedownloadScreen,"softcam",SoftCamKey,myurl)
            elif select[1] == "smcam":
                myurl = "https://raw.githubusercontent.com/smcam/s/main/SoftCam.Key"
                command = "wget -q %s %s %s %s" % (crt, agent, SoftCamKey, myurl)
                self.session.open(imagedownloadScreen,"softcam",SoftCamKey,myurl)
            elif select[1] == "enigma1969":
                myurl = "http://drive.google.com/uc?authuser=0&id=1aujij43w7qAyPHhfBLAN9sE-BZp8_AwI&export=download"
                command = "wget -O %s %s" % (SoftCamKey, myurl)
                self.session.open(imagedownloadScreen,"softcam",SoftCamKey,myurl)
            elif select[1] == "Serjoga":
                myurl = "http://raw.githubusercontent.com/audi06/SoftCam.Key_Serjoga/master/SoftCam.Key"
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
        if reswidth == 1280:
            self["menu"].l.setItemHeight(50)
            self["menu"].l.setFont(0, gFont("Regular", 28))
        else:
            self["menu"].l.setItemHeight(75)
            self["menu"].l.setFont(0, gFont("Regular", 42))
        for i in range(0, len(datalist)):
            txt = datalist[i][1]
            if reswidth == 1280:
                  png = os_path.join(resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/buttons/%s.png" % datalist[i][2]))
            else:
                  png = os_path.join(resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/buttons/fhd/%s.png" % datalist[i][2]))
            res.append(MultiContentEntryText(pos=(0, 1), size=(0, 0), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER | RT_WRAP, text="", color=scolor, color_sel=cccolor, border_width=3, border_color=806544))
            if reswidth == 1280:
                res.append(MultiContentEntryText(pos=(60, 1), size=(723, 50), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER | RT_WRAP, text=str(txt), color=16777215, color_sel=16777215))
                res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(40, 40), png=loadPNG(png)))
            else:
                res.append(MultiContentEntryText(pos=(100, 1), size=(1080, 75), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER | RT_WRAP, text=str(txt), color=16777215, color_sel=16777215))
                res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(75, 75), png=loadPNG(png)))
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
        if reswidth == 1920:
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
            self.keys_list = [[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
                                 [u"PASTE", u"A", u"B", u"C", u"D", u"E", u"F", u"OK", u"LEFT", u"RIGHT", u"CLEAR", u"Clean/PASTE"]]

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
      
def setKeyCallback(session, SoftCamKey, key):
      global newcaid
      service = session.nav.getCurrentService()
      info = service and service.info()
      caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
      SoftCamKey = findSoftCamKey()
      ref = session.nav.getCurrentlyPlayingServiceReference()
      if key: key = "".join(c for c in key if c in hexdigits).upper()
      saveKey(key)
      if key and len(key) == 14:
            if key != findKeyPowerVU(session, SoftCamKey, ""): # no change was made ## PowerVU
                  keystr = "P %s 00 %s" % (getonidsid(session), key)
                  name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
                  datastr = "\n%s ; Added on %s for %s at %s" % (keystr, datetime.now(), name, getOrb(session))
                  restartmess = "\n*** Need to Restart emu TO Active new key ***\n"
                  open(SoftCamKey, "a").write(datastr)
                  eConsoleAppContainer().execute("/etc/init.d/softcam restart")
                  session.open(MessageBox, _("PowerVU key saved sucessfuly!%s %s" % (datastr, restartmess)), MessageBox.TYPE_INFO, timeout=10)
      elif key and len(key) == 16:
            if 0x2600 in caids:
                 if key != findKeyBISS(session, SoftCamKey, ""): # no change was made ## BISS
                       keystr = "F %08X 00 %s" % (getHash(session), key)
                       name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
                       datastr = "\n%s ; Added on %s for %s at %s" % (keystr, datetime.now(), name, getOrb(session))
                       restartmess = "\n*** Need to Restart emu TO Active new key ***\n"
                       open(SoftCamKey, "a").write(datastr)
                       eConsoleAppContainer().execute("/etc/init.d/softcam restart")
                       session.open(MessageBox, _("BISS key saved sucessfuly!%s %s" % (datastr, restartmess)), MessageBox.TYPE_INFO, timeout=10)
            else:
                 if key != findKeyTandberg(session, SoftCamKey, ""): # no change was made ## Tandberg
                       newcaid=getnewcaid(SoftCamKey)
                       keystr = "T %s 01 %s" % (newcaid, key) 
                       name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
                       datastr = "\n%s ; Added on %s for %s at %s" % (keystr, datetime.now(), name, getOrb(session))
                       restartmess = "\n*** Need to Restart emu TO Active new key ***\n"       
                       open(SoftCamKey, "a").write(datastr)
                       eConsoleAppContainer().execute("/etc/init.d/softcam restart")
                       session.open(MessageBox, _("Tandberg key saved sucessfuly!%s %s" % (datastr, restartmess)), MessageBox.TYPE_INFO, timeout=10)
      elif key and len(key) == 32:
            if key != findKeyIRDETO(session, SoftCamKey, ""): # no change was made ## IRDETO
                  keystr = "I 0604 M1 %s" % key
                  name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
                  datastr = "\n%s ; Added on %s for %s at %s" % (keystr, datetime.now(), name, getOrb(session))
                  restartmess = "\n*** Need to Restart emu TO Active new key ***\n"
                  open(SoftCamKey, "a").write(datastr)
                  eConsoleAppContainer().execute("/etc/init.d/softcam restart")
                  session.open(MessageBox, _("IRDETO key saved sucessfuly!%s %s" % (datastr, restartmess)), MessageBox.TYPE_INFO, timeout=10)
      elif key:
               session.openWithCallback(boundFunction(setKeyCallback, session,SoftCamKey), HexKeyBoard,
                  title=_("Invalid key, length is %d" % len(key)), text=key.ljust(16,"*"))

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
        if reswidth == 1280:
                skin="""
<screen name="keyAdder_setup" position="center,center" size="620,398" title="keyAdder setup">
<widget source="Title" position="5,5" size="610,30" render="Label" font="Regular;25" foregroundColor="#00ffa500" backgroundColor="#16000000" transparent="1" halign="center"/>
<widget name="config" position="15,45" size="584,303" scrollbarMode="showOnDemand"/>
<widget source="help" render="Label" position="15,826" size="1187,199" font="Regular;25" foregroundColor="#00e5b243" backgroundColor="#16000000" valign="center" halign="center" transparent="1" zPosition="5"/>
<eLabel text="" foregroundColor="#00ff2525" backgroundColor="#00ff2525" size="150,3" position="108,394" zPosition="-10"/>
<eLabel text="" foregroundColor="#00389416" backgroundColor="#00389416" size="150,3" position="379,394" zPosition="-10"/>
<widget render="Label" source="key_red" position="108,360" size="150,35" zPosition="5" valign="center" halign="left" backgroundColor="#16000000" font="Regular;28" transparent="1" foregroundColor="#00ffffff" shadowColor="black"  shadowOffset="-1,-1"/>
<widget render="Label" source="key_green" position="379,360" size="150,35" zPosition="5" valign="center" halign="left" backgroundColor="#16000000" font="Regular;28" transparent="1" foregroundColor="#00ffffff" shadowColor="black" shadowOffset="-1,-1"/>
</screen>"""
        else:
                if DreamOS():
                        skin="""
<screen name="keyAdder_setup" position="center,center" size="840,560" title="keyAdder setup">
<widget source="Title" position="5,5" size="826,50" render="Label" font="Regular;28" foregroundColor="#00ffa500" backgroundColor="#16000000" transparent="1" halign="center"/>
<widget name="config" position="28,70" size="780,433" scrollbarMode="showOnDemand"/>
<widget source="help" render="Label" position="10,420" size="818,90" font="Regular;28" foregroundColor="#00e5b243" backgroundColor="#16000000" valign="center" halign="center" transparent="1" zPosition="5"/>
<eLabel text="" foregroundColor="#00ff2525" backgroundColor="#00ff2525" size="235,5" position="123,550" zPosition="-10"/>
<eLabel text="" foregroundColor="#00389416" backgroundColor="#00389416" size="235,5" position="445,550" zPosition="-10"/>
<widget render="Label" source="key_red" position="123,515" size="235,40" zPosition="5" valign="center" halign="center" backgroundColor="#16000000" font="Regular;28" transparent="1" foregroundColor="#00ffffff" shadowColor="black"  shadowOffset="-1,-1"/>
<widget render="Label" source="key_green" position="445,515" size="235,40" zPosition="5" valign="center" halign="center" backgroundColor="#16000000" font="Regular;28" transparent="1" foregroundColor="#00ffffff" shadowColor="black" shadowOffset="-1,-1"/>
</screen>"""
                else:
                        skin="""
<screen name="keyAdder_setup" position="center,center" size="840,560" title="keyAdder setup">
<widget source="Title" position="5,5" size="826,50" render="Label" font="Regular;28" foregroundColor="#00ffa500" backgroundColor="#16000000" transparent="1" halign="center"/>
<widget name="config" font="Regular;28" itemHeight="45" position="28,70" size="780,433" scrollbarMode="showOnDemand"/>
<widget source="help" render="Label" position="10,420" size="818,90" font="Regular;28" foregroundColor="#00e5b243" backgroundColor="#16000000" valign="center" halign="center" transparent="1" zPosition="5"/>
<eLabel text="" foregroundColor="#00ff2525" backgroundColor="#00ff2525" size="235,5" position="123,550" zPosition="-10"/>
<eLabel text="" foregroundColor="#00389416" backgroundColor="#00389416" size="235,5" position="445,550" zPosition="-10"/>
<widget render="Label" source="key_red" position="123,515" size="235,40" zPosition="5" valign="center" halign="center" backgroundColor="#16000000" font="Regular;28" transparent="1" foregroundColor="#00ffffff" shadowColor="black"  shadowOffset="-1,-1"/>
<widget render="Label" source="key_green" position="445,515" size="235,40" zPosition="5" valign="center" halign="center" backgroundColor="#16000000" font="Regular;28" transparent="1" foregroundColor="#00ffffff" shadowColor="black" shadowOffset="-1,-1"/>
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
                }, -2)

                # Impoert class KeyAdderUpdate()
                self.KeyAdderUpdate = KeyAdderUpdate(session)
                self.EnablekeyboardStyle_value = config.plugins.KeyAdder.keyboardStyle.value

                self["key_red"] = StaticText(_("Exit"))
                self["key_green"] = StaticText(_("Save"))
                self["help"] = StaticText()
                self.createConfigList()
                self.onLayoutFinish.append(self.setWindowTitle)

        def setWindowTitle(self):
                self.setTitle("KeyAdder Setup V%s" % VER)

        def cancel(self):
                self.close()

        def createConfigList(self):
                self.EnablecheckUpdate = getConfigListEntry(_("Enable checking for Online Update"), config.plugins.KeyAdder.update, _(" This Option to Enable or Disable checking for Online Update"))
                self.Enablesoftcampath = getConfigListEntry(_("Enable custom softCam file path"), config.plugins.KeyAdder.softcampath, _("This option to Enable custom softCam file path"))
                self.EnablekeyboardStyle = getConfigListEntry(_("Change VirtualKeyboard Style"), config.plugins.KeyAdder.keyboardStyle, _("This option to change Enable VirtualKeyboard Style appear"))
                self.Selectsavenumber = getConfigListEntry(_("Choose keys save numbers"), config.plugins.KeyAdder.savenumber, _("This option to choose how many keys need to save it inside savefile"))

                list = []
                list.append(self.EnablecheckUpdate)
                list.append(self.Enablesoftcampath)
                list.append(self.EnablekeyboardStyle)
                list.append(self.Selectsavenumber)

                self["config"].list = list
                self["config"].l.setList(list)
                self["config"].onSelectionChanged.append(self.updateHelp)

        def updateHelp(self):
                cur = self["config"].getCurrent()
                if cur:
                        self["help"].text = cur[2]

        def save(self):
                for x in self["config"].list:
                        if len(x)>1:
                                x[1].save()
                configfile.save()
                self.close()


def main(session, **kwargs):
    session.open(KeyAdderUpdate)

def Plugins(**kwargs):
    #NAME = "KeyAdder V{}".format(VER)
    NAME = "KeyAdder"
    ICON = "plugin.png"
    DES = "Manually add Key to current service"
    Descriptors = []
    Descriptors.append(PluginDescriptor(name=NAME,description=DES,icon=ICON,where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main, needsRestart = False))
    return Descriptors
