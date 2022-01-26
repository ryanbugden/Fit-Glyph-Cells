import os
from AppKit import NSApp, NSMenuItem, NSAlternateKeyMask, NSCommandKeyMask
import math
from vanilla import ImageButton
from mojo.tools import CallbackWrapper
from mojo.UI import CurrentFontWindow, getDefault, setDefault
from mojo.extensions import getExtensionDefault, setExtensionDefault
from mojo.subscriber import Subscriber, registerFontOverviewSubscriber


fit_resources_path = os.path.abspath("./resources/")

class fitGlyphCells(Subscriber):
	
	'''
	Scale the glyph cells in Font Overview as large as 
	they can be while justfied to the width of the frame.
	Happens on `Open` now.
	
	Ryan Bugden
	2020.04.03
	2022.01.25 - Extension
	'''
	
	def build(self):
		self.key = 'com.ryanbugden.FitGlyphCells.FitOnStartup'
		self.startupSetting = getExtensionDefault(self.key, fallback = 1)
		
		# put in the menu item
		title = "Fit Glyph Cells on Startup"
		fontMenu = NSApp().mainMenu().itemWithTitle_("Font")
		if not fontMenu:
			print("Fit Glyph Cells - Error")
			return
		fontMenu = fontMenu.submenu()
		if fontMenu.itemWithTitle_(title):
			return
			
		index = fontMenu.indexOfItemWithTitle_("Sort")
		self.target = CallbackWrapper(self.togglePref)
		newItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, "action:", "F")
		newItem.setKeyEquivalentModifierMask_(NSAlternateKeyMask | NSCommandKeyMask)
		newItem.setTarget_(self.target)
		newItem.setState_(self.startupSetting)
		fontMenu.insertItem_atIndex_(newItem, index+1)
		
	def started(self):
		# resize the glyph cells
		if self.startupSetting == 1:
			self.resize(None)

	def togglePref(self, sender):
		new_setting = not(self.startupSetting)
		setExtensionDefault(self.key, new_setting)
		self.startupSetting = new_setting

	def fontOverviewDidOpen(self, info):
		# add button
		self.sb = info["fontOverview"].statusBar
		
		path = os.path.join(fit_resources_path, '_icon_Fit.pdf')

		if hasattr(self.sb, 'fit_button'):
			del self.sb.fit_button
			
		self.sb.fit_button = ImageButton(
			(-122, -19, 18, 18), 
			imagePath = path,
			callback = self.resize, 
			sizeStyle = 'regular'
			)
		self.sb.fit_button.getNSButton().setBordered_(0)
		self.sb.fit_button.getNSButton().setBezelStyle_(2)

	def fontOverviewWantsContextualMenuItems(self, info):
		# add contextual menu item
		myMenuItems = [
			("Fit all glyphs in overview", self.resize)
		]
		info["itemDescriptions"].extend(myMenuItems)

	def resize(self, sender):
		SWM = getDefault("singleWindowMode")
		
		fw = CurrentFontWindow()
		fo = fw.fontOverview
		v = fo.getGlyphCollection().getGlyphCellView()

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
		
		# # debug
		# print("vw ",  vw)
		# print("vh ",  vh)
		# print("num g ",  num_g)
		# print("w ", sets_w)
		# print("sets_w ", sets_w)
		
		cells_across = 1
		cw = int(vw / cells_across)
		while ((num_g) / cells_across) * cw > vh:
			cells_across += 1
			cw = ch = int(vw / cells_across)
	
		vw = cw * cells_across
		fo_total_w = vw + sets_w
		
		# # debug
		# print()
		# print("cells across ",  cells_across)
		# print("cw ",  cw)
		# print("ch ",  ch)
		# print("vw ", vw)
		# print("sets_w ", sets_w)
		
		# set frame size
		if SWM == 1:
			fw.editor.splitView.setDimension('fontOverview', fo_total_w)
			fw.editor.splitView.setDimension('glyphView', w - fo_total_w)
			fw.centerGlyphInView()
		else:
			windows = NSApp().orderedWindows()
			(x, y), (w, h) =  windows[0].frame()
			x_diff = w - vw
			windows[0].setFrame_display_animate_(((x + x_diff, y), (fo_total_w, h)), True, False)
	
		# do it!
		v.setCellSize_([cw, ch])
		fo.views.sizeSlider.set(cw)
		setDefault("fontCollectionViewGlyphSize", int(cw))
		
registerFontOverviewSubscriber(fitGlyphCells)