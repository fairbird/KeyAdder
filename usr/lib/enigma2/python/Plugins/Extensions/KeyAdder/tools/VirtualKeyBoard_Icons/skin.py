# Created BY RAED 13-04-2021


from Screens.Screen import Screen

SKIN_HD = """
<screen name="VirtualKeyBoardKeyAdder" title="Virtual keyboard" position="center,center" size="586,282" zPosition="99" backgroundColor="#16000000">
	<widget name="header" conditional="header" position="5,65" size="569,35" font="Regular;30" foregroundColor="#00ffff00" halign="center" transparent="1" noWrap="1"/>
	<eLabel position="5,105" size="573,49" zPosition="1" backgroundColor="#0066ccff" foregroundColor="#00ffffff"/>
	<eLabel position="0,51" size="586,2" backgroundColor="#0066ccff" zPosition="1"/>
	<widget name="text" position="8,106" size="567,45" foregroundColor="#00ffffff" zPosition="3" font="Regular;40" noWrap="1" valign="center" halign="center"/>
	<widget name="list" position="45,175" size="497,91" selectionDisabled="1" transparent="1"/>
</screen>
"""

SKIN_FHD = """
<screen name="VirtualKeyBoardKeyAdder" title="Virtual keyboard" position="center,center" size="1010,400" zPosition="99" backgroundColor="#16000000">
	<widget name="header" conditional="header" position="38,52" size="927,45" font="Regular;36" foregroundColor="#00ffff00" halign="center" transparent="1" noWrap="1"/>
	<eLabel position="5,108" size="991,68" zPosition="1" backgroundColor="#0066ccff" foregroundColor="#00ffffff"/>
	<eLabel position="0,51" size="1010,2" backgroundColor="#0066ccff" zPosition="1"/>
	<widget name="text" position="8,111" size="984,60" foregroundColor="#00ffffff" zPosition="3" font="Regular;55" noWrap="1" valign="center" halign="center"/>
	<widget name="list" position="100,200" size="900,160" itemHeight="70" selectionDisabled="1" transparent="1" />
</screen>
"""
