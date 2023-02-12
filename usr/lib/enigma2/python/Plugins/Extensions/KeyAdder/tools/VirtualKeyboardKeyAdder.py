# -*- coding: UTF-8 -*-
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_CENTER, RT_VALIGN_CENTER, getPrevAsciiCode, eTimer
from Screens.Screen import Screen
from Components.Language import language
from Components.ActionMap import ActionMap, HelpableActionMap, NumberActionMap
from Components.Sources.StaticText import StaticText
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from Screens.HelpMenu import HelpableScreen
from enigma import eWidget, gRGB
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap
from Tools.NumericalTextInput import NumericalTextInput
import skin, os
from Components.GUIComponent import GUIComponent
from sys import version_info

def parseColor(s):
	return gRGB(int(s[1:], 0x10))

PY3 = version_info[0] == 3

class VirtualKeyBoardList(MenuList):
	def __init__(self, list, enableWrapAround=False):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		self.l.setFont(0, gFont('Regular', 28))
		self.l.setFont(1, gFont("Regular", 28))
		self.l.setItemHeight(45)

def VirtualKeyBoardEntryComponent(keys, selectedKey, shiftMode=False):
	primaryColor = '#282828'
	secondaryColor = '#4e4e4e'
	res = [(keys)]
	bg = skin.parseColor("#00494949").argb()
	bgkey = skin.parseColor(primaryColor).argb()
	bgsel = skin.parseColor(secondaryColor).argb()
	bgok = skin.parseColor("#00009900").argb()
	bgcancel = skin.parseColor("#00990000").argb()
	bgselok = skin.parseColor("#00006600").argb()
	bgselcancel = skin.parseColor("#00660000").argb()

	height = 45
	width = int(1880/12)
	x = 0
	count = 0
	for key in keys:
		if key == "EXIT":
			if selectedKey == count:
				res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=0, text="EXIT",
									  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgsel))
			else:
				res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=0, text="EXIT",
									  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgkey))
		elif key == "BACKSPACE":
			if selectedKey == count:
				res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text="BACKSPACE",
									  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgselcancel))
			else:
				res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text="BACKSPACE",
									  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgcancel))
		elif key == "CLEAR":
			if selectedKey == count:
				res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=0, text="CLR",
									  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgsel))
			else:
				res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=0, text="CLR",
									  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgkey))
		elif key == "SHIFT":
			if shiftMode:
				if selectedKey == count:
					res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text="SHIFT",
										  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgsel))
				else:
					res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text="SHIFT",
										  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bg))
			else:
				if selectedKey == count:
					res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text="SHIFT",
										  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgsel))
				else:
					res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text="SHIFT",
										  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgkey))
		elif key == "SPACE":
			if selectedKey == count:
				res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=0, text="",
									  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgsel))
			else:
				res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text="",
									  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgkey))
		elif key == "OK":
			if selectedKey == count:
				res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=0, text="OK",
									  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgselok))
			else:
				res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=0, text="OK",
									  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgok))
		elif key == "LEFT":
			if selectedKey == count:
				res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text="LEFT",
									  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgsel))
			else:
				res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text="LEFT",
									  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgkey))
		elif key == "RIGHT":
			if selectedKey == count:
				res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text="RIGHT",
									  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgsel))
			else:
				res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=1, text="RIGHT",
									  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgkey))
		else:
			if not PY3:
				key = key.encode("utf-8")
			if selectedKey == count:
				res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=0, text=key,
									  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgsel))
			else:
				res.append(MultiContentEntryText(pos=(x + 3, 3), size=(width - 6, height - 6), font=0, text=key,
									  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, backcolor=bgkey))
		x += width
		count += 1
	return res


class VirtualKeyBoardKeyAdder(Screen, NumericalTextInput, HelpableScreen):
	
			
	def __init__(self, session, title="", text="",nb_only=False):
		Screen.__init__(self, session)
		NumericalTextInput.__init__(self, nextFunc=self.timeoutNI, handleTimeout=True)
		self.skin = self.buildSKin()
		self.sms_txt = None
		self.keys_list = []
		self.shiftkeys_list = []
		self.lang = language.getLanguage()
		self.nextLang = None
		self.shiftMode = False
		self.nb_only = nb_only
		self.cursor = "XcursorX"
		self.gui_cursor = "| "
		self.text = text + self.cursor
		self.selectedKey = 0
		self.cursor_show = True
		self.cursor_time = 600
		self.cursorTimer = eTimer()
		#try:
		#	self.cursorTimer.callback.append(self.toggleCursor)
		#except:
		#	self.cursorTimer_conn = self.cursorTimer.timeout.connect(self.toggleCursor)
		self.cursorTimer.start(self.cursor_time, True)
		self["country"] = StaticText("")
		self["header"] = Label(title)
		self["text"] = Label()
		self["list"] = VirtualKeyBoardList([])


		self["actions"] = ActionMap(["KeyboardInputActions", "InputAsciiActions"],
									{
										"gotAsciiCode": self.keyGotAscii,
										"deleteBackward": self.backClicked,
									}, -2)
		self["InputBoxActions"] = HelpableActionMap(self, "InputBoxActions",
													{
														"deleteBackward": (self.cursorLeft, _("Move cursor left")),
														"deleteForward": (self.cursorRight, _("Move cursor right")),
													}, -2)
		self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
													{
														"ok": (self.okClicked, _("Select key")),
														"cancel": (self.exit, _("Cancel")),
													}, -2)
		self["ShortcutActions"] = HelpableActionMap(self, "ShortcutActions",
													{
														"red": (self.backClicked, _("Delete (left of the cursor)")),
														"blue": (self.backSpace, _("Delete (right of the cursor)")),
														"green": (self.ok, _("Save")),
													}, -2)
		self["WizardActions"] = HelpableActionMap(self, "WizardActions",
												  {
													  "left": (self.left, _("Left")),
													  "right": (self.right, _("Right")),
													  "up": (self.up, _("Up")),
													  "down": (self.down, _("Down")),
												  }, -2)
		self["SeekActions"] = HelpableActionMap(self, "SeekActions",
												{
													"seekBack": (self.move_to_begin, _("Move to begin")),
													"seekFwd": (self.move_to_end, _("Move to end")),
												}, -2)
		self["NumberActions"] = NumberActionMap(["NumberActions"],
												{
													"1": self.keyNumberGlobal,
													"2": self.keyNumberGlobal,
													"3": self.keyNumberGlobal,
													"4": self.keyNumberGlobal,
													"5": self.keyNumberGlobal,
													"6": self.keyNumberGlobal,
													"7": self.keyNumberGlobal,
													"8": self.keyNumberGlobal,
													"9": self.keyNumberGlobal,
													"0": self.keyNumberGlobal
												})

		
		self.set_GUI_Text()
		HelpableScreen.__init__(self)
		self.onExecBegin.append(self.setKeyboardModeAscii)
		self.onLayoutFinish.append(self.setLang)
		self.onLayoutFinish.append(self.buildVirtualKeyBoard)
  
	def buildSKin(self):
		primaryColor = '#282828'
		primaryColorLabel = '#DCE1E3'
		skin = """<screen backgroundColor="#70000000" flags="wfNoBorder" name="VirtualKeyBoard KeyAdder" position="0,0" size="1920,1080" title="Virtual KeyBoard" transparent="0" zPosition="99">
			<eLabel position="0,720" size="1920,360" backgroundColor="#70000000"/>
			<widget backgroundColor="#70000000" font="Regular;30" foregroundColor="#DCE1E3" name="header" noWrap="1" position="center,260" size="1235,40" transparent="1" valign="center" zPosition="30" />
			<widget backgroundColor="#70000000" foregroundColor="{}" name="list" position="20,725" selectionDisabled="1" size="1880,350" transparent="0" zPosition="30" />
			<widget backgroundColor="{}" font="Regular;33" foregroundColor="{}" halign="right" name="text" noWrap="1" position="center,300" size="1235,70" valign="center" zPosition="30" />
		</screen>""".format(primaryColorLabel,primaryColor,primaryColorLabel)
		return skin

	def switchLang(self):
		self.lang = self.nextLang
		self.setLang()
		self.buildVirtualKeyBoard()

	def setLang(self):
		
		if self.lang == 'de_DE':
			self.nbkeys_list = [u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0",
				u"CLEAR", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.keys_list = [
				u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"-",
				u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"+", u"@",
				u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"#", u"\\", u"|",
				u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".",
				u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.shiftkeys_list = [
				u"EXIT", u"!", u'"', u"$", u"%", u"&", u"/", u"(", u")", u"=", u"_",
				u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"*", u"[",
				u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"'", u"?", u"]",
				u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":",
				u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.nextLang = 'en_EN'
		else:
			self.nbkeys_list = [u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0",
				u"CLEAR", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.keys_list = [
				u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"-",
				u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"+", u"@",
				u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"#", u"\\", u"|",
				u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".",
				u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.shiftkeys_list = [
				u"EXIT", u"!", u'"', u"$", u"%", u"&", u"/", u"(", u")", u"=", u"_",
				u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"*", u"[",
				u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"'", u"?", u"]",
				u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":",
				u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.lang = 'en_EN'
			self.nextLang = 'de_DE'
		self.keys_list = self.buildKeyBoardLayout(self.keys_list)
		self.shiftkeys_list = self.buildKeyBoardLayout(self.shiftkeys_list)
		self.nbkeys_list = self.buildKeyBoardLayout(self.nbkeys_list)
		self["country"].setText(self.lang)

	def buildVirtualKeyBoard(self, selectedKey=0):
		list = []
		self.max_key = -1
		self.setUseableChars(u'1234567890aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ')
		if self.nb_only:
			self.k_list = self.nbkeys_list
			self.setUseableChars(u'1234567890')
			for keys in self.k_list:
				keyslen = len(keys)
				self.max_key += keyslen
				if selectedKey < keyslen and selectedKey > -1:
					list.append(VirtualKeyBoardEntryComponent(keys, selectedKey))
				else:
					list.append(VirtualKeyBoardEntryComponent(keys, -1))
				selectedKey -= keyslen
		elif self.shiftMode:
			self.k_list = self.shiftkeys_list
			for keys in self.k_list:
				keyslen = len(keys)
				self.max_key += keyslen
				if selectedKey < keyslen and selectedKey > -1:
					list.append(VirtualKeyBoardEntryComponent(keys, selectedKey, True))
				else:
					list.append(VirtualKeyBoardEntryComponent(keys, -1, True))
				selectedKey -= keyslen
		else:
			self.k_list = self.keys_list
			for keys in self.k_list:
				keyslen = len(keys)
				self.max_key += keyslen
				if selectedKey < keyslen and selectedKey > -1:
					list.append(VirtualKeyBoardEntryComponent(keys, selectedKey))
				else:
					list.append(VirtualKeyBoardEntryComponent(keys, -1))
				selectedKey -= keyslen
		self.first_line_len = len(self.k_list[0])
		self.no_of_lines = len(self.k_list)
		self["list"].setList(list)

	def buildKeyBoardLayout(self, key_list):
		line_len = 12
		if self["list"].skinAttributes:
			for (attrib, value) in self["list"].skinAttributes:
				if attrib == "linelength":
					line_len = int(value)
		k_list = []
		line = []
		i = 0
		for key in key_list:
			i += 1
			line.append(key)
			if i == line_len:
				k_list.append(line)
				i = 0
				line = []
		k_list.append(line)
		return k_list

	def toggleCursor(self):
		whitespace = " " * len(self.gui_cursor)
		if self.cursor_show:
			self.cursor_show = False
			txt = self.text.replace(self.cursor, whitespace)
		else:
			self.cursor_show = True
			txt = self.text.replace(self.cursor, self.gui_cursor)
		self["text"].setText(txt)
		self.cursorTimer.start(self.cursor_time, True)

	def set_GUI_Text(self):
		txt = self.text.replace(self.cursor, "|")
		self["text"].setText(txt)

	def backClicked(self):
		txt = self.text.split(self.cursor)
		del_len = self.checkUnicode(txt[0][-1:])
		self.text = txt[0][:-del_len] + self.cursor + txt[1]
		self.set_GUI_Text()

	def backSpace(self):
		txt = self.text.split(self.cursor)
		del_len = self.checkUnicode(txt[1][:1])
		self.text = txt[0] + self.cursor + txt[1][del_len:]
		self.set_GUI_Text()

	def cursorLeft(self):
		self.moveCursor(-1)

	def cursorRight(self):
		self.moveCursor(+1)

	def checkUnicode(self, char):
		try:
			len(u'%s' % char)
		except UnicodeDecodeError:
			return 2
		return 1

	def moveCursor(self, direction):
		txt = self.text.split(self.cursor)
		if direction < 0:
			direction *= self.checkUnicode(txt[0][-1:])
		elif direction > 0:
			direction *= self.checkUnicode(txt[1][:1])
		pos = self.text.find(self.cursor) + direction
		clean_txt = self.text.replace(self.cursor, "")
		if pos > len(clean_txt):
			self.text = self.cursor + clean_txt
		elif pos < 0:
			self.text = clean_txt + self.cursor
		else:
			self.text = clean_txt[:pos] + self.cursor + clean_txt[pos:]
		self.set_GUI_Text()

	def move_to_begin(self):
		clean_txt = self.text.replace(self.cursor, "")
		self.text = self.cursor + clean_txt

	def move_to_end(self):
		clean_txt = self.text.replace(self.cursor, "")
		self.text = clean_txt + self.cursor

	def toggleShift(self):
		if self.shiftMode:
			self.shiftMode = False
		else:
			self.shiftMode = True
		self.buildVirtualKeyBoard(self.selectedKey)

	def keyNumberGlobal(self, number):
		self.cursorTimer.stop()
		if number != self.lastKey and self.lastKey != -1:
			self.nextChar()
		if not PY3:
			txt = self.getKey(number).encode("UTF-8")
		else:
			txt = self.getKey(number)
		if self.nb_only:
			if len(self.text.replace('XcursorX','')) < 14:
				self.sms_txt = self.text.replace(self.cursor, txt + self.cursor)
				self.got_sms_key(txt)
				self.set_GUI_SMS_Text()
		else:
			self.sms_txt = self.text.replace(self.cursor, txt + self.cursor)
			self.got_sms_key(txt)
			self.set_GUI_SMS_Text()

	def set_GUI_SMS_Text(self):
		txt = self.sms_txt.replace(self.cursor, "| ")
		self["text"].setText(txt)

	def timeoutNI(self):
		if self.sms_txt:
			self.text = self.sms_txt
		self.sms_txt = None
		self.set_GUI_Text()
		self.cursorTimer.start(self.cursor_time, True)

	def okClicked(self):
		if self.shiftMode:
			list = self.shiftkeys_list
		elif self.nb_only:
			list = self.nbkeys_list
		else:
			list = self.keys_list
		selectedKey = self.selectedKey

		text = None

		for x in list:
			xlen = len(x)
			if selectedKey < xlen:
				if selectedKey < len(x):
					text = x[selectedKey]
				break
			else:
				selectedKey -= xlen

		if text is None:
			return

		if not PY3:
			text = text.encode("UTF-8")
			
		if text == "EXIT":
			self.exit()
		elif text == "BACKSPACE":
			self.backClicked()
		elif text == "CLEAR":
			self.text = "" + self.cursor
			self.set_GUI_Text()
		elif text == "SHIFT":
			self.toggleShift()
		elif text == "SPACE":
			self.text = self.text.replace(self.cursor, " " + self.cursor)
			self.set_GUI_Text()
		elif text == "OK":
			self.ok()
		elif text == "LEFT":
			self.cursorLeft()
		elif text == "RIGHT":
			self.cursorRight()
		elif text == "PASTE":
			value = self.readKey()
			self["text"].setText(value)
		else:
			if self.nb_only:
				if len(self.text.replace('XcursorX','')) < 14:
					self.text = self.text.replace(self.cursor, text + self.cursor)
					self.set_GUI_Text()
			else:
				self.text = self.text.replace(self.cursor, text + self.cursor)
				self.set_GUI_Text()

	def readKey(self):
		if os.path.exists("/usr/keys/savekeys"):
			key = open("/usr/keys/savekeys").read()
			return key
		else:
			return ""

	def ok(self):
		if PY3:
			text = self.text
		else:
			text = self.text.encode("utf-8")
		text = text.replace(self.cursor, "")
		self.close(text)

	def exit(self):
		self.close(None)

	def moveActiveKey(self, direction):
		self.selectedKey += direction
		for k in range(0, self.no_of_lines, 1):
			no_of_chars = k * self.first_line_len
			if direction == -1:
				if self.selectedKey == no_of_chars - 1:
					self.selectedKey = no_of_chars - 1 + self.first_line_len
					if self.selectedKey > self.max_key:
						self.selectedKey = self.max_key
					break
			elif direction == 1:
				if self.selectedKey == no_of_chars + self.first_line_len:
					self.selectedKey = no_of_chars
					break
				if self.selectedKey > self.max_key:
					self.selectedKey = (self.no_of_lines - 1) * self.first_line_len
					break
			elif direction == -self.first_line_len:
				if self.selectedKey < 0:
					self.selectedKey = (
									   self.no_of_lines - 1) * self.first_line_len + self.first_line_len + self.selectedKey
					if self.selectedKey > self.max_key:
						self.selectedKey = self.selectedKey - self.first_line_len
				break
			elif direction == self.first_line_len:
				tmp_key = self.selectedKey - self.first_line_len
				if self.selectedKey > self.max_key:
					line_no = k + 1
					if line_no * self.first_line_len > tmp_key:
						self.selectedKey = tmp_key - (line_no - 1) * self.first_line_len
						break
				elif self.selectedKey <= self.max_key:
					break
		self.showActiveKey()

	def left(self):
		self.moveActiveKey(-1)

	def right(self):
		self.moveActiveKey(+1)

	def up(self):
		self.moveActiveKey(-self.first_line_len)

	def down(self):
		self.moveActiveKey(+self.first_line_len)

	def showActiveKey(self):
		self.buildVirtualKeyBoard(self.selectedKey)

	def inShiftKeyList(self, key):
		for KeyList in self.shiftkeys_list:
			for char in KeyList:
				if char == key:
					return True
		return False

	def got_sms_key(self, char):
		if self.inShiftKeyList(char):
			self.shiftMode = True
			list = self.shiftkeys_list
		else:
			self.shiftMode = False
			list = self.keys_list
		selkey = 0
		for keylist in list:
			for key in keylist:
				if key == char:
					self.selectedKey = selkey
					self.showActiveKey()
					return
				else:
					selkey += 1

	def keyGotAscii(self):
		from Components.config import getCharValue
		char = getCharValue(getPrevAsciiCode())
		if len(str(char)) == 1:
			if PY3:
				char = char
			else:
				char = char.encode("utf-8")
		if self.inShiftKeyList(char):
			self.shiftMode = True
			list = self.shiftkeys_list
		else:
			self.shiftMode = False
			list = self.keys_list
		if char == " ":
			char = "SPACE"
		selkey = 0
		for keylist in list:
			for key in keylist:
				if key == char:
					self.selectedKey = selkey
					self.okClicked()
					self.showActiveKey()
					return
				else:
					selkey += 1