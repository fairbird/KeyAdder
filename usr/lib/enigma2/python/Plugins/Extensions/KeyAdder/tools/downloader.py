#!/usr/bin/python
# Code by mfaraj57 and RAED (c) 2018

# python3
from __future__ import print_function

from Components.ActionMap import ActionMap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from enigma import eTimer, eConsoleAppContainer,getDesktop
from os import path as os_path
from Components.GUIComponent import *
from Components.ProgressBar import ProgressBar
from Tools.Downloader import downloadWithProgress
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import os
import time

try:
	from Components.HTMLComponent import *
except:
	print("KeyAdder: No HTMLComponent file found")

#### imagedownloadScreen screen
sz_w = getDesktop(0).size().width()
if sz_w == 1280 :
        SKIN_imagedownloadScreen = """
<screen name="imagedownloadScreen" position="center,center" size="560,155" title="Downloading image...">
<widget name="activityslider" position="20,50" size="510,20" borderWidth="1" transparent="1" />
<widget name="package" position="20,5" size="510,45" font="Regular;18" halign="center" valign="center" transparent="1" />
<widget name="status" position="20,80" size="510,45" font="Regular;16" halign="center" valign="center" transparent="1" />
</screen>"""
else:
        SKIN_imagedownloadScreen = """
<screen name="imagedownloadScreen" position="center,center" size="805,232" title="Downloading image...">
<widget name="activityslider" position="30,75" size="755,30" borderWidth="1" transparent="1" />
<widget name="package" position="30,7" size="755,60" font="Regular;27" halign="center" valign="center" transparent="1" />
<widget name="status" position="30,120" size="755,60" font="Regular;24" halign="center" valign="center" transparent="1" />
</screen>"""

#### progress screen
sz_w = getDesktop(0).size().width()
if sz_w == 1280 :
        SKIN_Progress = """
<screen position="350,250"  size="550,155" title="Command execution..." >
<widget name="text" position="10,10"  size="550,130" font="Console;18" />
<widget name="slider" position="0,142" size="550,15" borderWidth="1" transparent="1" />
</screen>"""
else:
        SKIN_Progress = """
<screen position="500,430"  size="850,200" title="Command execution..." >
<widget name="text" position="20,20"  size="850,160" font="Console;24" />
<widget name="slider" position="0,185" size="850,20" borderWidth="1" transparent="1" />
</screen>"""

def log(label,data):
    data=str(data)
    open("/tmp/KeyAdder.log","a").write("\n"+label+":>"+data)

def getversioninfo():
    currversion = '1.0'
    version_file = resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/version")
    if os.path.exists(version_file):
        try:
            fp = open(version_file, 'r').readlines()
            for line in fp:
                if 'version' in line:
                    currversion = line.split('=')[1].strip()
        except:
            pass
    return (currversion)
    
class imagedownloadScreen(Screen):
    def __init__(self, session, name='', target='', url=''):
        Screen.__init__(self, session)
        self.skin = SKIN_imagedownloadScreen
        self.target = target
        self.name=name
        self.url=url
        self.shown=True
        self.count_success = 0
        self.success=False 
        self['activityslider'] = ProgressBar()
        self['activityslider'].setRange((0, 100))
        self['activityslider'].setValue(0)
        self['status'] = Label()
        self['package'] = Label()
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'ok': self.dexit,
         'cancel': self.dexit}, -1)
        self['status'].setText(_('Downloading softcam,please wait..'))
        self.downloading = False
        self.downloader = None
        self.setTitle(_('Connecting') + '...')
        self.timer = eTimer()
        try:
            self.timer.callback.append(self.startDownload)
        except:
            self.timer_conn = self.timer.timeout.connect(self.startDownload)
        self.timer.start(5000, 1)

    def startDownload(self):
        try:
            self.timer.stop()
            del self.timer
        except:
            pass
        self.currentIndex = 0
        self.count_success = 0
        self.count_failed = 0
        self.downloading = True
        self.downloadfile2(self.url,self.target)

    def downloadfile(self,url,target):
            import ssl,urllib2
            list1 = []
            try:
                req = urllib2.Request(url)
                try:
                    response = urllib2.urlopen(req, context=ssl._create_unverified_context())
                except:
                    response = urllib2.urlopen(req)
                data = response.read()
                response.close()
                with open(ofile, 'wb') as f:
                    f.write(r.content)
                f.close()
                self['status'].setText('softcam downloaded successfully')
            except urllib2.URLError as e:
                trace_error()
                if hasattr(e, 'code'):
                    print('We failed with error code - %s.' % e.code)
                    if '401' in str(e.code):
                        self['status'].setText('Falied to download softcam-401')  
                        return None
                    if '404' in str(e.code):
                        self['status'].setText('Falied to download softcam-404')
                        return None
                    if '400' in str(e.code):
                        self['status'].setText('Falied to download softcam-400')
                        return None
                    if '403' in str(e.code):
                        self['status'].setText('Falied to download softcam-403')
                        return None
                elif hasattr(e, 'reason'):
                        self['status'].setText('Falied to download softcam-')
                        return None

    def downloadfile2(self,url = None,ofile=''):
        debug = True
        if True:
            self['package'].setText(self.name)
            self.setTitle(_('Connecting') + '...')
            self['status'].setText(_('Connecting') + ' to server....')
            self.downloading = True
            self.downloader = downloadWithProgress(self.url, self.target)
            self.downloader.addProgress(self.progress)
            self.downloader.start().addCallback(self.responseCompleted).addErrback(self.responseFailed)

    def progress(self, current, total):
        p = int(100 * (float(current) / float(total)))
        self['activityslider'].setValue(p)
        info = _('Downloading') + ' ' + '%d of %d kBytes' % (current / 1024, total / 1024)
        self['package'].setText(self.name)
        self['status'].setText(info)
        self.setTitle(_('Downloading') + ' ' + str(p) + '%...')

    def responseCompleted(self, data = None):
        print('[Softcam downloader] Download succeeded. ')
        info = 'Download completed successfully.\npress Ok To Exit'   
        self['status'].setText(info)
        self.setTitle(_('Download completed successfully.'))
        self.downloading = False
        self.success=True
        self.instance.show()

    def responseFailed(self, failure_instance = None, error_message = ''):
        print('[Softcam downloader] Download failed. ')
        self.error_message = error_message
        if error_message == '' and failure_instance is not None:
            self.error_message = failure_instance.getErrorMessage()
        info = self.error_message
        self['status'].setText(info)
        self.setTitle(_('Download failed Press Ok To Exit'))
        cmd = "echo 'message' > /tmp//.download_error.log"
        cmd = cmd.replace('message', info)
        self.container = eConsoleAppContainer()
        self.container.execute(cmd)
        self.downloading = False
        self.success=False
        self['key_green'].hide()
        self.instance.show()
        self.remove_target()
        return

    def dexit(self):
        try:
            path=os.path.split(self.target)[0]
        except:
            pass
        if self.downloading:
            self.session.openWithCallback(self.abort,MessageBox, _('Are you sure to stop download.'), MessageBox.TYPE_YESNO)
        else:
            self.close(False)

    def remove_target(self):
            import os
            try:
                if os.path.exists(self.target):
                    os.remove(self.target)
            except:
                pass

    def abort(self,answer=True):
        if answer==False:
            return
        if not self.downloading:
            if os_path.exists('/tmp/download_install.log'):
               os.remove('/tmp/download_install.log')
            self.close(False)
        elif self.downloader is not None:
            self.downloader.stop
            info = _('Aborting...')
            self['status'].setText(info)
            cmd = 'echo canceled > /tmp/.download_error.log ; rm target'
            cmd = cmd.replace('target', self.target)
            self.remove_target()
            try:
                self.close(False)
               
            except:
                pass
        else: 
            self.close(False)
        return
