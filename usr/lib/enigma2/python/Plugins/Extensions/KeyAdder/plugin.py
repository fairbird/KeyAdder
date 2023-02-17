#!/usr/bin/python
# -*- coding: utf-8 -*-
# Code By RAED and mfaraj57

from enigma import eConsoleAppContainer, eDVBDB, iServiceInformation, eTimer, loadPNG, getDesktop, RT_WRAP, RT_HALIGN_LEFT, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.config import config, getConfigListEntry, ConfigText, ConfigSubsection, ConfigYesNo, configfile, ConfigSelection
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
from Components.ActionMap import ActionMap, NumberActionMap
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
resheight = getDesktop(0).size().height()
config.plugins.KeyAdder = ConfigSubsection()
config.plugins.KeyAdder.update = ConfigYesNo(default=True)
config.plugins.KeyAdder.lastcaid = ConfigText(default='0', fixed_size=False)
config.plugins.KeyAdder.softcampath = ConfigYesNo(default=False) #False = Auto Detecte path
config.plugins.KeyAdder.custom_softcampath = ConfigText(default="/usr/keys", visible_width = 250, fixed_size = False)
config.plugins.KeyAdder.keyboardStyle = ConfigYesNo(default=True)
BRANATV='/usr/lib/enigma2/python/boxbranding.so' ## OpenATV
BRANDPLI='/usr/share/enigma2/rc_models/rc_models.cfg' ## OpenPLI/OV
BRANDOPEN='/usr/lib/enigma2/python/Tools/StbHardware.pyo' ## Open source
BRANDTS='/usr/lib/enigma2/python/Plugins/TSimage/__init__.pyo' ## TS
BRANDOS='/var/lib/dpkg/status' ## DreamOS
BRANDVU='/proc/stb/info/vumodel' ## VU+

def DreamOS():
    if os_path.exists('/var/lib/dpkg/status'):
        return DreamOS

def BHVU():
    if os.path.exists('/proc/stb/info/vumodel') and os.path.exists('/usr/lib/enigma2/python/Blackhole'):
        return BHVU

def VTI():
    VTI = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/VTIPanel/plugin.pyo")
    if os.path.exists(VTI):
        return VTI

if config.plugins.KeyAdder.keyboardStyle.value == True:
	from Plugins.Extensions.KeyAdder.tools.VirtualKeyboardKeyAdder import VirtualKeyBoardKeyAdder
else:
	if DreamOS():
        	from Plugins.Extensions.KeyAdder.tools.VirtualKeyBoardOS import VirtualKeyBoardKeyAdder
	elif BHVU() or VTI():
        	from Plugins.Extensions.KeyAdder.tools.VirtualKeyBoardVU import VirtualKeyBoardKeyAdder
	else:
        	from Plugins.Extensions.KeyAdder.tools.VirtualKeyBoardopen import VirtualKeyBoardKeyAdder

def logdata(label_name = '', data = None):
    try:
        data=str(data)
        fp = open('/tmp/KeyAdder.log', 'a')
        fp.write( str(label_name) + ': ' + data+"\n")
        fp.close()
    except:
        trace_error()    
        pass

def trace_error():
    import sys
    import traceback
    try:
        traceback.print_exc(file=sys.stdout)
        traceback.print_exc(file=open('/tmp/KeyAdderError.log', 'a'))
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
              if line.startswith('T'):
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
                        <widget name="menu" position="center,43" size="650,306" backgroundColor="#16000000"/>
                        <eLabel position="25,360" size="110,50" backgroundColor="#00ff0000" zPosition="1"/>
                        <eLabel text="MENU" font="Regular;30" position="28,364" size="103,43" foregroundColor="#00000000" backgroundColor="#00ffffff" zPosition="3" valign="center" halign="center"/>
                        <eLabel text="Press Menu for more options" font="Regular;33" position="148,360" size="546,50" foregroundColor="#00ffffff" backgroundColor="#00000000" zPosition="2" valign="center"/>
                </screen>'''
    else:
           skin = '''
                <screen name="KeyAdderUpdate" position="center,center" size="476,306" backgroundColor="#16000000" title="KeyAdderUpdate">
                        <widget name="menu" position="15,25" size="450,230" backgroundColor="#16000000"/>
                        <eLabel position="15,259" size="80,40" backgroundColor="#00ff0000" zPosition="1"/>
                        <eLabel text="MENU" font="Regular;26" position="18,261" size="74,35" foregroundColor="#00000000" backgroundColor="#00ffffff" zPosition="3" valign="center" halign="center"/>
                        <eLabel text="Press Menu for more options" font="Regular;25" position="104,259" size="369,40" foregroundColor="#00ffffff" backgroundColor="#00000000" zPosition="2" valign="center"/>
                </screen>'''

    def __init__(self, session, title='', datalist = []):
        Screen.__init__(self, session)
        self['menu'] = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self['actions'] = ActionMap(['WizardActions', 'ColorActions','MenuActions'], {
         'ok': self.select,
         'back': self.close,
         'menu' :self.showMenuoptions})
        title = 'KeyAdder Version %s' % VER
        menuData = []
        menuData.append((0, 'Add key Manually', 'key'))
        menuData.append((1, 'Update Softcam online', 'update'))
        if config.plugins.KeyAdder.softcampath.value == True:
                menuData.append((2, 'Select Softcam.key Path', 'path'))
        menuData.append((3, 'Exit', 'exit'))
        self.new_version = VER
        self.settitle(title, menuData)

    def settitle(self, title, datalist):
        if config.plugins.KeyAdder.update.value:
             self.checkupdates()
        self.setTitle(title)
        self.showmenulist(datalist)

    def select(self):
        index = self['menu'].getSelectionIndex()
        if index==0:
                keymenu(self.session)
        elif index==1:
                self.siteselect()
        elif index==2:
                if config.plugins.KeyAdder.softcampath.value == True:
                        self.pathselect()
                else:
                        self.close()
        else:
            self.close()

    def pathselect(self):
        paths = ["/var/keys",
               "/etc",
               "/etc/tuxbox/config",
               "/etc/tuxbox/config/ncam",
               "/etc/tuxbox/config/oscam",
               "/etc/tuxbox/config/gcam",
               "/etc/tuxbox/config/oscam-emu",
               "/etc/tuxbox/config/oscam-trunk",
               "Add your custom path"]
        list=[]
        for path in paths:
                pathsfiles = path.split('" "')
                list.append((pathsfiles))
        from Screens.ChoiceBox import ChoiceBox
        self.session.openWithCallback(self.pathCallback, ChoiceBox, _('select your softcams file path'), list)

    def pathCallback(self, result):
         if result:
             customPath = result[0]
             if customPath == "Add your custom path":
                from Screens.VirtualKeyBoard import VirtualKeyBoard
                self.session.openWithCallback(self.savepath, VirtualKeyBoard, title=_("Please enter the path"), text="")
             else:
                config.plugins.KeyAdder.custom_softcampath.value = customPath
             config.plugins.KeyAdder.custom_softcampath.save()
             configfile.save()
             softcamkey = os_path.join(config.plugins.KeyAdder.custom_softcampath.value, "SoftCam.Key")
             if not os_path.exists(softcamkey):
                os.system('mkdir -p %s' % config.plugins.KeyAdder.custom_softcampath.value)
                #os.system('touch %s/SoftCam.Key' % config.plugins.KeyAdder.custom_softcampath.value)
         return

    def savepath(self, word):
         if word is None:
                pass
         else:
                config.plugins.KeyAdder.custom_softcampath.value = word
                config.plugins.KeyAdder.custom_softcampath.save()
                configfile.save()
                softcamkey = os_path.join(config.plugins.KeyAdder.custom_softcampath.value, "SoftCam.Key")
                if not os_path.exists(softcamkey):
                        os.system('mkdir -p %s' % config.plugins.KeyAdder.custom_softcampath.value)

    def siteselect(self):
        list1 = []
        list1.append(("softcam.org (Always Updated)", "softcam.org"))
        list1.append(("MOHAMED_OS (Always Updated)", "MOHAMED_OS"))
        list1.append(("enigma1969 (Always Updated)", "enigma1969"))
        list1.append(("Serjoga", "Serjoga"))
        self.session.openWithCallback(self.Downloadkeys, ChoiceBox, _('select site to downloan file'), list1)
           
    def Downloadkeys(self, select, SoftCamKey=None):
        self.list = []
        cmdlist = []
        SoftCamKey = findSoftCamKey()
        agent='--header="User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/8.0 Safari/600.1.17"'
        crt="--debug --no-check-certificate"
        command=''
        if select: 
            if select[1] == "softcam.org":
                myurl = 'http://www.softcam.org/deneme6.php?file=SoftCam.Key'
                command = 'wget -O %s %s' % (SoftCamKey, myurl)
                self.session.open(imagedownloadScreen,'softcam',SoftCamKey, myurl)
            elif select[1] == "MOHAMED_OS":
                myurl = 'https://raw.githubusercontent.com/MOHAMED19OS/SoftCam_Emu/main/Enigma2/SoftCam.Key'
                command = 'wget -q %s %s %s %s' % (crt, agent, SoftCamKey, myurl)
                self.session.open(imagedownloadScreen,'softcam',SoftCamKey,myurl)
            elif select[1] == "enigma1969":
                myurl = 'http://drive.google.com/uc?authuser=0&id=1aujij43w7qAyPHhfBLAN9sE-BZp8_AwI&export=download'
                command = 'wget -O %s %s' % (SoftCamKey, myurl)
                self.session.open(imagedownloadScreen,'softcam',SoftCamKey,myurl)
            elif select[1] == "Serjoga":
                myurl = 'http://raw.githubusercontent.com/audi06/SoftCam.Key_Serjoga/master/SoftCam.Key'
                command = 'wget -q %s %s %s %s' % (crt, agent, SoftCamKey, myurl)
                self.session.open(imagedownloadScreen,'softcam',SoftCamKey,myurl)
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
            self['menu'].l.setItemHeight(50)
            self['menu'].l.setFont(0, gFont('Regular', 28))
        else:
            self['menu'].l.setItemHeight(75)
            self['menu'].l.setFont(0, gFont('Regular', 42))
        for i in range(0, len(datalist)):
            txt = datalist[i][1]
            if reswidth == 1280:
                  png = os_path.join(resolveFilename(SCOPE_PLUGINS, 'Extensions/KeyAdder/buttons/%s.png' % datalist[i][2]))
            else:
                  png = os_path.join(resolveFilename(SCOPE_PLUGINS, 'Extensions/KeyAdder/buttons/fhd/%s.png' % datalist[i][2]))
            res.append(MultiContentEntryText(pos=(0, 1), size=(0, 0), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER | RT_WRAP, text='', color=scolor, color_sel=cccolor, border_width=3, border_color=806544))
            if reswidth == 1280:
                res.append(MultiContentEntryText(pos=(60, 1), size=(723, 50), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER | RT_WRAP, text=str(txt), color=16777215, color_sel=16777215))
                res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(40, 40), png=loadPNG(png)))
            else:
                res.append(MultiContentEntryText(pos=(100, 1), size=(1080, 75), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER | RT_WRAP, text=str(txt), color=16777215, color_sel=16777215))
                res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(75, 75), png=loadPNG(png)))
            menulist.append(res)
            res = []
        self['menu'].l.setList(menulist)
        self['menu'].show()

    def showMenuoptions(self):
        choices=[]
        self.list = []
        EnablecheckUpdate = config.plugins.KeyAdder.update.value
        Enablesoftcampath = config.plugins.KeyAdder.softcampath.value
        EnablekeyboardStyle = config.plugins.KeyAdder.keyboardStyle.value
        choices.append(("Install KeyAdder version %s" %self.new_version,"Install"))
        if EnablecheckUpdate == False:
                choices.append(("Press Ok to [Enable checking for Online Update]","enablecheckUpdate"))
        else:
                choices.append(("Press Ok to [Disable checking for Online Update]","disablecheckUpdate"))
        if Enablesoftcampath == False:
                choices.append(("Press Ok to [Enable custom softCam file path]","enablesoftcampath"))
        else:
                choices.append(("Press Ok to [Disable auto softCam file path]","disablesoftcampath"))
        if EnablekeyboardStyle == False:
        	choices.append(("Press Ok to [Enable New keyboard Style]","enablekeyboardStyle"))
        else:
        	choices.append(("Press Ok to [Enable Old keyboard Style]","disablekeyboardStyle"))
        self.session.openWithCallback(self.choicesback, ChoiceBox, _('select task'),choices)

    def choicesback(self, select):
        if select:
                if select[1] == "Install":
                         self.install(True)
                elif select[1] == "enablecheckUpdate":
                         config.plugins.KeyAdder.update.value = True
                         config.plugins.KeyAdder.update.save()
                         configfile.save()
                elif select[1] == "disablecheckUpdate":
                         config.plugins.KeyAdder.update.value = False
                         config.plugins.KeyAdder.update.save()
                elif select[1] == "enablesoftcampath":
                         config.plugins.KeyAdder.softcampath.value = True
                         config.plugins.KeyAdder.softcampath.save()
                         configfile.save()
                         self.close()
                elif select[1] == "disablesoftcampath":
                         config.plugins.KeyAdder.softcampath.value = False
                         config.plugins.KeyAdder.softcampath.save()
                         configfile.save()
                         self.close()
                elif select[1] == "enablekeyboardStyle":
                         config.plugins.KeyAdder.keyboardStyle.value = True
                         config.plugins.KeyAdder.keyboardStyle.save()
                         configfile.save()
                         self.session.openWithCallback(self.restart, MessageBox, _("Settings changed, restart enigma2 need it now ?!"))
                elif select[1] == "disablekeyboardStyle":
                         config.plugins.KeyAdder.keyboardStyle.value = False
                         config.plugins.KeyAdder.keyboardStyle.save()
                         configfile.save()
                         self.session.openWithCallback(self.restart, MessageBox, _("Settings changed, restart enigma2 need it now ?!"))

    def restart(self, answer=None):
        if answer:
                self.session.open(TryQuitMainloop, 3)
                return
        self.close(True)


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
                self.session.openWithCallback(self.install, MessageBox, _('New version %s is available.\n\n%s.\n\nDo want ot install now.' % (new_version, new_description)), MessageBox.TYPE_YESNO)

    def install(self,answer=False):
        try:
                if answer:
                           cmdlist = []
                           cmd='wget https://raw.githubusercontent.com/fairbird/KeyAdder/main/installer.sh -O - | /bin/sh'
                           cmdlist.append(cmd)
                           self.session.open(Console, title='Installing last update, enigma will be started after install', cmdlist=cmdlist, finishedCallback=self.myCallback, closeOnSuccess=False)
        except:
                trace_error()

    def myCallback(self,result):
         return

class HexKeyBoard(VirtualKeyBoardKeyAdder):
      def __init__(self, session, title="", **kwargs):
            VirtualKeyBoardKeyAdder.__init__(self, session, title, **kwargs)

            self.skinName = "VirtualKeyBoardKeyAdder"
            self.keys_list = [[
                               [u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE", u"", u""],
                               [u"PASTE", u"A", u"B", u"C", u"D", u"E", u"F", u"OK", u"LEFT", u"RIGHT", u"ALL", u"CLR", u"", u""]
                             ]]
            self.locales = { "hex" : [_("HEX"), _("HEX"), self.keys_list] }
            self.lang = "hex"
            try:
                 self.setLocale()
            except:
                 self.max_key = all
                 self.setLang()
            self.buildVirtualKeyBoard()

      def setLang(self):
            self.keys_list = [[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
                                 [u"PASTE", u"A", u"B", u"C", u"D", u"E", u"F", u"OK", u"LEFT", u"RIGHT", u"ALL", u"CLEAR"]]

      #def Menucopypast(self):
      #      choices=[]
      #      choices.append(("Copy keys", "Copy"))
      #      choices.append(("Paste keys", "Paste"))
      #      self.session.openWithCallback(self.choicesback, ChoiceBox, _('select task'),choices)

      #def choicesback(self, select):
      #      if select:
      #          #if select[1] == "Copy":
                #         self.session.open(MessageBox, "Copy Function Test", MessageBox.TYPE_INFO, timeout=10)
      #          if select[1] == "Paste":
      #                   value=self.readKey()
      #                   if value!='':
      #                      self["text"].setText(value)

      #def readKey(self):
      #      if os.path.exists("/usr/keys/savekeys"):
      #         key=open("/usr/keys/savekeys").read()
      #         return key
      #      else:
      #         return ""

def saveKey(key):
     try:
      f=open("/usr/keys/savekeys","w")
      f.write(str(key))
      f.close()
     except:
             pass

table = array('L')
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
      saveKey(key)
      service = session.nav.getCurrentService()
      info = service and service.info()
      caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
      SoftCamKey = findSoftCamKey()
      ref = session.nav.getCurrentlyPlayingServiceReference()
      if key: key = "".join(c for c in key if c in hexdigits).upper()
      if key and len(key) == 14:
            if key != findKeyPowerVU(session, SoftCamKey, ""): # no change was made ## PowerVU
                  keystr = "P %s 00 %s" % (getonidsid(session), key)
                  name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
                  datastr = "\n%s ; Added on %s for %s at %s\n" % (keystr, datetime.now(), name, getOrb(session))
                  restartmess = "\n*** Need to Restart emu TO Active new key ***\n"
                  open(SoftCamKey, "a").write(datastr)
                  eConsoleAppContainer().execute("/etc/init.d/softcam restart")
                  session.open(MessageBox, _("PowerVU key saved sucessfuly!%s %s" % (datastr, restartmess)), MessageBox.TYPE_INFO, timeout=10)
      elif key and len(key) == 16:
            if 0x2600 in caids:
                 if key != findKeyBISS(session, SoftCamKey, ""): # no change was made ## BISS
                       keystr = "F %08X 00 %s" % (getHash(session), key)
                       name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
                       datastr = "\n%s ; Added on %s for %s at %s\n" % (keystr, datetime.now(), name, getOrb(session))
                       restartmess = "\n*** Need to Restart emu TO Active new key ***\n"
                       open(SoftCamKey, "a").write(datastr)
                       eConsoleAppContainer().execute("/etc/init.d/softcam restart")
                       session.open(MessageBox, _("BISS key saved sucessfuly!%s %s" % (datastr, restartmess)), MessageBox.TYPE_INFO, timeout=10)
            else:
                 if key != findKeyTandberg(session, SoftCamKey, ""): # no change was made ## Tandberg
                       newcaid=getnewcaid(SoftCamKey)
                       keystr = "T %s 01 %s" % (newcaid, key) 
                       name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
                       datastr = "\n%s ; Added on %s for %s at %s\n" % (keystr, datetime.now(), name, getOrb(session))
                       restartmess = "\n*** Need to Restart emu TO Active new key ***\n"       
                       open(SoftCamKey, "a").write(datastr)
                       eConsoleAppContainer().execute("/etc/init.d/softcam restart")
                       session.open(MessageBox, _("Tandberg key saved sucessfuly!%s %s" % (datastr, restartmess)), MessageBox.TYPE_INFO, timeout=10)
      elif key and len(key) == 32:
            if key != findKeyIRDETO(session, SoftCamKey, ""): # no change was made ## IRDETO
                  keystr = "I 0604 M1 %s" % key
                  name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
                  datastr = "\n%s ; Added on %s for %s at %s\n" % (keystr, datetime.now(), name, getOrb(session))
                  restartmess = "\n*** Need to Restart emu TO Active new key ***\n"
                  open(SoftCamKey, "a").write(datastr)
                  eConsoleAppContainer().execute("/etc/init.d/softcam restart")
                  session.open(MessageBox, _("IRDETO key saved sucessfuly!%s %s" % (datastr, restartmess)), MessageBox.TYPE_INFO, timeout=10)
      elif key:
               session.openWithCallback(boundFunction(setKeyCallback, session,SoftCamKey), HexKeyBoard,
                  title=_("Invalid key, length is %d" % len(key)), text=key.ljust(16,'*'))

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
        with open(SoftCamKey, 'rU') as f:
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
        with open(SoftCamKey, 'rU') as f:
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
        with open(SoftCamKey, 'rU') as f:
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
        with open(SoftCamKey, 'rU') as f:
            for line in f:
                  if line.startswith(keystart):
                        keyline = line
      if keyline:
            return keyline.split()[3]
      else:
            return key

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
