# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_CENTER, RT_VALIGN_CENTER, getPrevAsciiCode, getDesktop
from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Components.Language import language
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Sources.StaticText import StaticText
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap
from Tools.NumericalTextInput import NumericalTextInput
import skin
import os
from .compat import PY3
from Plugins.Extensions.KeyAdder.tools.VirtualKeyBoard_Icons.skin import SKIN_HD, SKIN_FHD

from skin import TemplatedListFonts, componentSizes
from six import unichr
from six.moves import range
import six


def getDesktopSize():
    s = getDesktop(0).size()
    return (s.width(), s.height())

def isHD():
    desktopSize = getDesktopSize()
    return desktopSize[0] == 1280

class VirtualKeyBoardList(MenuList):
	COMPONENT_VIRTUAL_KEYBOARD_LIST = "VirtualKeyBoardList"
	def __init__(self, list, enableWrapAround=False):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		tlf = TemplatedListFonts()
		self.l.setFont(0, gFont(tlf.face(tlf.KEYBOARD, default=tlf.face(tlf.BIG)), tlf.size(tlf.KEYBOARD, default=tlf.size(tlf.BIG))))
		self.l.setItemHeight(VirtualKeyBoardList.itemHeight())

	@staticmethod
	def itemHeight():
		return componentSizes.itemHeight(VirtualKeyBoardList.COMPONENT_VIRTUAL_KEYBOARD_LIST, 45)

def VirtualKeyBoardEntryComponent(keys, selectedKey,shiftMode=False):
	if isHD():
		key_backspace = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/VirtualKeyBoard_Icons/buttonsHD/vkey_backspace.png"))
		key_bg = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/VirtualKeyBoard_Icons/buttonsHD/vkey_bg.png"))
		key_clr = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/VirtualKeyBoard_Icons/buttonsHD/vkey_clr.png"))
		key_esc = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/VirtualKeyBoard_Icons/buttonsHD/vkey_esc.png"))
		key_ok = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/VirtualKeyBoard_Icons/buttonsHD/vkey_ok.png"))
		key_sel = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/VirtualKeyBoard_Icons/buttonsHD/vkey_sel.png"))
		key_shift = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/VirtualKeyBoard_Icons/buttonsHD/vkey_shift.png"))
		key_shift_sel = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/VirtualKeyBoard_Icons/buttonsHD/vkey_shift_sel.png"))
		key_space = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/VirtualKeyBoard_Icons/buttonsHD/vkey_space.png"))
	else:
		key_backspace = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/VirtualKeyBoard_Icons/buttonsFHD/vkey_backspace.png"))
		key_bg = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/VirtualKeyBoard_Icons/buttonsFHD/vkey_bg.png"))
		key_clr = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/VirtualKeyBoard_Icons/buttonsFHD/vkey_clr.png"))
		key_esc = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/VirtualKeyBoard_Icons/buttonsFHD/vkey_esc.png"))
		key_ok = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/VirtualKeyBoard_Icons/buttonsFHD/vkey_ok.png"))
		key_sel = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/VirtualKeyBoard_Icons/buttonsFHD/vkey_sel.png"))
		key_shift = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/VirtualKeyBoard_Icons/buttonsFHD/vkey_shift.png"))
		key_shift_sel = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/VirtualKeyBoard_Icons/buttonsFHD/vkey_shift_sel.png"))
		key_space = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/KeyAdder/tools/VirtualKeyBoard_Icons/buttonsFHD/vkey_space.png"))
	res = [ (keys) ]
	
	x = 0
	count = 0
	height = VirtualKeyBoardList.itemHeight()
	if shiftMode:
		shiftkey_png = key_shift_sel
	else:
		shiftkey_png = key_shift
	for key in keys:
		width = None
		if key == "EXIT":
			width = key_esc.size().width()
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, height), png=key_esc))
		elif key == "BACKSPACE":
			width = key_backspace.size().width()
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, height), png=key_backspace))
		elif key == "CLEAR":
			width = key_clr.size().width()
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, height), png=key_clr))
		elif key == "SHIFT":
			width = shiftkey_png.size().width()
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, height), png=shiftkey_png))
		elif key == "SPACE":
			width = key_space.size().width()
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, height), png=key_space))
		elif key == "OK":
			width = key_ok.size().width()
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, height), png=key_ok))
		#elif key == "<-":
		#	res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(45, 45), png=key_left))
		#elif key == "->":
		#	res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(45, 45), png=key_right))
		
		else:
			width = key_bg.size().width()
			try:
				res.extend((
					MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, height), png=key_bg),
					MultiContentEntryText(pos=(x, 0), size=(width, height), font=0, text=six.ensure_str(key), flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER)
				))
			except:
				res.extend((
					MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, height), png=key_bg),
					MultiContentEntryText(pos=(x, 0), size=(width, height), font=0, text=key.encode("utf-8"), flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER)
				))

		if selectedKey == count:
			width = key_sel.size().width()
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, height), png=key_sel))

		if width is not None:
			x += width
		else:
			x += height
		count += 1
	
	return res


class VirtualKeyBoardKeyAdder(Screen, NumericalTextInput):
	IS_DIALOG = True
	LINESIZE = 12

	def __init__(self, session, title="", text=""):
		Screen.__init__(self, session)
		if isHD():
			self.skin = SKIN_HD
		else:
			self.skin = SKIN_FHD
		NumericalTextInput.__init__(self, nextFunc = self.nextFunc)
		self.setZPosition(10000)
		self.keys_list = []
		self.shiftkeys_list = []
		self.lang = language.getLanguage()
		self.nextLang = None
		self.shiftMode = False
		self.text = text
		self.selectedKey = 0
		self.editing = False

		self["country"] = StaticText("")
		self["header"] = Label(title)
		self["text"] = Label(self.text)
		self["list"] = VirtualKeyBoardList([])

		self["actions"] = ActionMap(["OkCancelActions", "WizardActions", "ColorActions", "KeyboardInputActions", "InputBoxActions", "InputAsciiActions"],
			{
				"gotAsciiCode": self.keyGotAscii,
				"ok": self.okClicked,
				"cancel": self.exit,
				"left": self.left,
				"right": self.right,
				"up": self.up,
				"down": self.down,
				"red": self.backClicked,
				"green": self.ok,
				"yellow": self.switchLang,
				"deleteBackward": self.backClicked,
				"back": self.exit
			}, -2)
		self["numberActions"] = NumberActionMap(["NumberActions"],
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
		self.setLang()
		self.onExecBegin.append(self.setKeyboardModeAscii)
		self.onLayoutFinish.append(self.buildVirtualKeyBoard)

	def switchLang(self):
		self.lang = self.nextLang
		self.setLang()
		self.buildVirtualKeyBoard()

	def setLang(self):
		if self.lang == 'de_DE':
			self.keys_list = [
				[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
				[u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"ü", u"+"],
				[u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"ö", u"ä", u"#"],
				[u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".", u"-", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"@", u"ß", u"OK"]]
			self.shiftkeys_list = [
				[u"EXIT", u"!", u'"', u"§", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"BACKSPACE"],
				[u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"Ü", u"*"],
				[u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"Ö", u"Ä", u"'"],
				[u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":", u"_", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"?", u"\\", u"OK"]]
			self.nextLang = 'es_ES'
		elif self.lang == 'es_ES':
			#still missing keys (u"ùÙ")
			self.keys_list = [
				[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
				[u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"ú", u"+"],
				[u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"ó", u"á", u"#"],
				[u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".", u"-", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"@", u"Ł", u"ŕ", u"é", u"č", u"í", u"ě", u"ń", u"ň", u"OK"]]
			self.shiftkeys_list = [
				[u"EXIT", u"!", u'"', u"§", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"BACKSPACE"],
				[u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"Ú", u"*"],
				[u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"Ó", u"Á", u"'"],
				[u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":", u"_", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"?", u"\\", u"Ŕ", u"É", u"Č", u"Í", u"Ě", u"Ń", u"Ň", u"OK"]]
			self.nextLang = 'fi_FI'
		elif self.lang == 'fi_FI':
			self.keys_list = [
				[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
				[u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"é", u"+"],
				[u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"ö", u"ä", u"#"],
				[u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".", u"-", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"@", u"ß", u"ĺ", u"OK"]]
			self.shiftkeys_list = [
				[u"EXIT", u"!", u'"', u"§", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"BACKSPACE"],
				[u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"É", u"*"],
				[u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"Ö", u"Ä", u"'"],
				[u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":", u"_", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"?", u"\\", u"Ĺ", u"OK"]]
			self.nextLang = 'ru_RU'
		elif self.lang == 'ru_RU':
			self.keys_list = [
				[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
				[u"й", u"ц", u"у", u"к", u"е", u"н", u"г", u"ш", u"щ", u"з", u"х", u"+"],
				[u"ф", u"ы", u"в", u"а", u"п", u"р", u"о", u"л", u"д", u"ж", u"э", u"#"],
				[u"<", u"ё", u"я", u"ч", u"с", u"м", u"и", u"т", u",", ".", u"-", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"@", u"ь", u"б", u"ю", u"ъ", u"OK"]]
			self.shiftkeys_list = [
				[u"EXIT", u"!", u'"', u"§", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"BACKSPACE"],
				[u"Й", u"Ц", u"У", u"К", u"Е", u"Н", u"Г", u"Ш", u"Щ", u"З", u"Х", u"*"],
				[u"Ф", u"Ы", u"В", u"А", u"П", u"Р", u"О", u"Л", u"Д", u"Ж", u"Э", u"'"],
				[u">", u"Ё", u"Я", u"Ч", u"С", u"М", u"И", u"Т", u";", u":", u"_", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"?", u"\\", u"Ь", u"Б", u"Ю",  u"Ъ", u"OK"]]
			self.nextLang = 'sv_SE'
		elif self.lang == 'sv_SE':
			self.keys_list = [
				[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
				[u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"é", u"+"],
				[u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"ö", u"ä", u"#"],
				[u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".", u"-", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"@", u"ß", u"ĺ", u"OK"]]
			self.shiftkeys_list = [
				[u"EXIT", u"!", u'"', u"§", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"BACKSPACE"],
				[u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"É", u"*"],
				[u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"Ö", u"Ä", u"'"],
				[u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":", u"_", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"?", u"\\", u"Ĺ", u"OK"]]
			self.nextLang = 'sk_SK'
		elif self.lang =='sk_SK':
			self.keys_list = [
				[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
				[u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"ú", u"+"],
				[u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"ľ", u"@", u"#"],
				[u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".", u"-", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"š", u"č", u"ž", u"ý", u"á", u"í", u"é", u"OK"]]
			self.shiftkeys_list = [
				[u"EXIT", u"!", u'"', u"§", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"BACKSPACE"],
				[u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"ť", u"*"],
				[u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"ň", u"ď", u"'"],
				[u"Á", u"É", u"Ď", u"Í", u"Ý", u"Ó", u"Ú", u"Ž", u"Š", u"Č", u"Ť", u"Ň"],
				[u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":", u"_", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"?", u"\\", u"ä", u"ö", u"ü", u"ô", u"ŕ", u"ĺ", u"OK"]]
			self.nextLang = 'cs_CZ'
		elif self.lang == 'cs_CZ':
			self.keys_list = [
				[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
				[u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"ú", u"+"],
				[u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"ů", u"@", u"#"],
				[u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".", u"-", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"ě", u"š", u"č", u"ř", u"ž", u"ý", u"á", u"í", u"é", u"OK"]]
			self.shiftkeys_list = [
				[u"EXIT", u"!", u'"', u"§", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"BACKSPACE"],
				[u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"ť", u"*"],
				[u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"ň", u"ď", u"'"],
				[u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":", u"_", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"?", u"\\", u"Č", u"Ř", u"Š", u"Ž", u"Ú", u"Á", u"É", u"OK"]]
			self.nextLang = 'en_GB'
		else:
			self.keys_list = [
				[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
				[u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"+", u"@"],
				[u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"#", u"\\"],
				[u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".", u"-", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"OK"]]
			self.shiftkeys_list = [
				[u"EXIT", u"!", u'"', u"§", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"BACKSPACE"],
				[u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"*"],
				[u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"'", u"?"],
				[u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":", u"_", u"CLEAR"],
				[u"SHIFT", u"SPACE", u"OK"]]
			self.lang = 'en_GB'
			self.nextLang = 'de_DE'		
		self["country"].setText(self.lang)

	def buildVirtualKeyBoard(self, selectedKey=0):
		list = []
		
		if self.shiftMode:
			self.k_list = self.shiftkeys_list
			for keys in self.k_list:
				if selectedKey < self.LINESIZE and selectedKey > -1:
					list.append(VirtualKeyBoardEntryComponent(keys, selectedKey,True))
				else:
					list.append(VirtualKeyBoardEntryComponent(keys, -1,True))
				selectedKey -= self.LINESIZE
		else:
			self.k_list = self.keys_list
			for keys in self.k_list:
				if selectedKey < self.LINESIZE and selectedKey > -1:
					list.append(VirtualKeyBoardEntryComponent(keys, selectedKey))
				else:
					list.append(VirtualKeyBoardEntryComponent(keys, -1))
				selectedKey -= self.LINESIZE
		self.lines = len(self.k_list)
		self.max_key = (self.lines - 1) * self.LINESIZE #len of all lines but last (may be shorter)
		self.max_key += len(self.k_list[-1]) - 1 #len of last line
		self["list"].setList(list)
	
	def backClicked(self):
		self.nextKey()
		self.editing = False
		self["text"].setMarkedPos(-1)
		self.text = self["text"].getText()[:-1]
		self["text"].setText(self.text)
			
	def okClicked(self):
		self.nextKey()
		self.editing = False
		self["text"].setMarkedPos(-1)
		if self.shiftMode:
			list = self.shiftkeys_list
		else:
			list = self.keys_list
		
		selectedKey = self.selectedKey

		text = None

		for x in list:
			if selectedKey < self.LINESIZE:
				if selectedKey < len(x):
					text = x[selectedKey]
				break
			else:
				selectedKey -= self.LINESIZE

		if text is None:
			return

		try:
			text = six.ensure_str(text)
		except:
			text = text.encode("UTF-8")

		if text == "EXIT":
			self.close(None)
		
		elif text == "BACKSPACE":
			self.text = self["text"].getText()[:-1]
			self["text"].setText(self.text)
		
		elif text == "CLEAR":
			self.text = ""
			self["text"].setText(self.text)
		
		elif text == "SHIFT":
			if self.shiftMode:
				self.shiftMode = False
			else:
				self.shiftMode = True
			self.buildVirtualKeyBoard(self.selectedKey)
		
		elif text == "SPACE":
			self.text += " "
			self["text"].setText(self.text)
		
		elif text == "OK":
			self.close(self["text"].getText())

		elif text == "PASTE":
			value = self.readKey()
			self["text"].setText(value)
		
		else:
			self.text = self["text"].getText()
			self.text += text
			self["text"].setText(self.text)

	def readKey(self):
		if os.path.exists("/usr/keys/savekeys"):
			key=open("/usr/keys/savekeys").read()
			return key
		else:
			return ""

	def ok(self):
		self.close(self["text"].getText())

	def exit(self):
		self.close(None)

	def left(self):
		self.selectedKey -= 1
		for line in range(0,self.LINESIZE):
			if self.selectedKey == (self.LINESIZE * line) - 1:
				selectedKey = ((line + 1) * self.LINESIZE) - 1
				self.selectedKey = min(self.max_key, selectedKey)
				break
		self.showActiveKey()

	def right(self):
		self.selectedKey += 1
		if self.selectedKey > self.max_key:
			self.selectedKey = (self.lines - 1) * self.LINESIZE
		else:
			for line in range(0,self.LINESIZE):
				if self.selectedKey == self.LINESIZE * ( line + 1 ):
					self.selectedKey = line * self.LINESIZE
					break
		self.showActiveKey()

	def up(self):
		lines = self.lines
		self.selectedKey -= self.LINESIZE

		if (self.selectedKey < 0) and (self.selectedKey >= (self.max_key - lines * self.LINESIZE)):
			self.selectedKey += self.LINESIZE * (lines -1)
		elif self.selectedKey < 0:
			self.selectedKey += self.LINESIZE * lines
		self.showActiveKey()

	def down(self):
		lines = self.lines
		self.selectedKey += self.LINESIZE
		if (self.selectedKey > self.max_key) and (self.selectedKey > (lines * self.LINESIZE) - 1):
			self.selectedKey -= lines * self.LINESIZE
		elif self.selectedKey > self.max_key:
			self.selectedKey -= (lines - 1) * self.LINESIZE
		self.showActiveKey()

	def showActiveKey(self):
		self.buildVirtualKeyBoard(self.selectedKey)

	def inShiftKeyList(self,key):
		for KeyList in self.shiftkeys_list:
			for char in KeyList:
				if char == key:
					return True
		return False

	def keyGotAscii(self):
		try:
			char = six.ensure_str(unichr(getPrevAsciiCode()))
		except:
			char = str(unichr(getPrevAsciiCode()).encode('utf-8'))
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

	def keyNumberGlobal(self, number):
		unichar = self.getKey(number)
		if not self.editing:
			self.text = self["text"].getText()
			self.editing = True
			self["text"].setMarkedPos(len(self.text))
		try:
			self["text"].setText(self.text + six.ensure_str(unichar))
		except:
			self["text"].setText(self.text + unichar.encode('utf-8', 'ignore'))

	def nextFunc(self):
		self.text = self["text"].getText()
		self.editing = False
		self["text"].setMarkedPos(-1)
