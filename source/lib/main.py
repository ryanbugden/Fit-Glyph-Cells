import os
from AppKit import NSApp, NSMenuItem, NSAlternateKeyMask, NSCommandKeyMask
import math
from vanilla import ImageButton
from mojo.tools import CallbackWrapper
from mojo.UI import CurrentFontWindow, getDefault, setDefault
from mojo.extensions import ExtensionBundle, getExtensionDefault, setExtensionDefault
from mojo.subscriber import Subscriber, registerFontOverviewSubscriber


bundle = ExtensionBundle("Fit Glyph Cells")
icon = bundle.getResourceImage("icon")


class FitGlyphCells(Subscriber):
	
	'''
	Scale the glyph cells in Font Overview as large as 
	they can be while justified to the width of the frame.
	
	Ryan Bugden
	'''
	
	def build(self):

		self.key = 'com.ryanbugden.FitGlyphCells.FitOnStartup'
		self.startupSetting = getExtensionDefault(self.key, fallback = 1)
		
		# put in the menu item
		title = "Fit Glyph Cells on Open"
		font_menu = NSApp().mainMenu().itemWithTitle_("Font")
		if not font_menu:
			print("Fit Glyph Cells - Error")
			return
		font_menu = font_menu.submenu()
		if font_menu.itemWithTitle_(title):
			return
			
		index = font_menu.indexOfItemWithTitle_("Sort")
		self.target = CallbackWrapper(self.togglePref)
		new_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, "action:", "F")
		new_item.setKeyEquivalentModifierMask_(NSAlternateKeyMask | NSCommandKeyMask)
		new_item.setTarget_(self.target)
		new_item.setState_(self.startupSetting)
		font_menu.insertItem_atIndex_(new_item, index+1)


	def togglePref(self, sender):
		new_setting = not(self.startupSetting)
		setExtensionDefault(self.key, new_setting)
		self.startupSetting = new_setting

	def fontOverviewDidOpen(self, info):
		# resize the glyph cells
		if self.startupSetting == 1:
			self.resize(None)

		# add button
		self.sb = info["fontOverview"].statusBar

		if hasattr(self.sb, 'fit_button'):
			del self.sb.fit_button
			
		self.sb.fit_button = ImageButton(
			(-122, -19, 18, 18), 
			imageObject = icon,
			callback = self.resize, 
			sizeStyle = 'regular'
			)
		self.sb.fit_button.getNSButton().setBordered_(0)
		self.sb.fit_button.getNSButton().setBezelStyle_(2)
		self.sb.fit_button.getNSButton().image().setTemplate_(True)

	def fontOverviewWantsContextualMenuItems(self, info):
		# add contextual menu item
		myMenuItems = [
			("Fit glyph cells", self.resize)
		]
		info["itemDescriptions"].extend(myMenuItems)

	def resize(self, sender):
		SWM = getDefault("singleWindowMode")
		
		fw = CurrentFontWindow()
		fo = fw.fontOverview
		gc = fo.getGlyphCollection()
		v = gc.getGlyphCellView()

		# make cells small first
		starter = 10
		v.setCellSize_([starter, starter])
		# get the width of the whole window
		x, y, w, h = fw.window().getPosSize()
		# get the width of overall font overview
		fo_w = fo.getNSView().frameSize().width
		# get the width of the cell view
		vw, vh = v.frameSize().width, v.frameSize().height
		# get the width of the sets menu to the left of the font overview
		sets_w = fo_w - vw
		# get number of glyphs
		num_g = len(gc.getGlyphNames())
		
		cells_across = 1
		cw = ch = int(vw / cells_across)
		while ((num_g) / cells_across) * cw > vh:
			cells_across += 1
			cw = ch = int(vw / cells_across)
	
		vw = cw * cells_across
		fo_total_w = vw + sets_w
		
		# set frame size in single window mode
		if SWM == 1:
			fw.editor.splitView.setDimension('fontOverview', fo_total_w)
			fw.editor.splitView.setDimension('glyphView', w - fo_total_w)
			fw.centerGlyphInView()
		# set frame size in multi-window mode
		else:
			windows = NSApp().orderedWindows()
			(x, y), (w, h) =  windows[0].frame()
			x_diff = w - fo_total_w
			windows[0].setFrame_display_animate_(((x + x_diff, y), (fo_total_w, h)), True, False)
	
		# change the cell size once and for all, update the slider to reflect the change
		v.setCellSize_([cw, ch])
		fo.views.sizeSlider.set(cw)
		# set this as the new default cell size (this happens when you use the native slide too)
		setDefault("fontCollectionViewGlyphSize", int(cw))
		
		
registerFontOverviewSubscriber(FitGlyphCells)