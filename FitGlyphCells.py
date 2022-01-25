import os
from AppKit import NSApp
import math
from vanilla import ImageButton
from mojo.UI import CurrentFontWindow, getDefault, setDefault
from mojo.subscriber import Subscriber, registerFontOverviewSubscriber


fit_resources_path = os.path.abspath("./resources/")

class fitGlyphCells(Subscriber):
    
    '''
    Scale the glyph cells in Font Overview as large as 
    they can be while justfied to the width of the frame.
    Happens on `Open` now.
    
    Ryan Bugden
    2020.04.03
    '''

    def started(self):
        self.i = 0
        self.resize(None)

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
        fw = CurrentFontWindow()
        fo = fw.fontOverview
        v = fo.getGlyphCollection().getGlyphCellView()

        # make cells small first
        starter = 10
        v.setCellSize_([starter, starter])

        # get the width of the cell view
        vw, vh = v.frameSize().width, v.frameSize().height
        
        # get number of glyphs
        num_g = len(fo.getGlyphOrder())
        
        # debug
        print("vw ",  vw)
        print("vh ",  vh)
        print("num g ",  num_g)
        
        cells_across = 1
        cw = int(vw / cells_across)
        while ((num_g) / cells_across) * cw > vh:
            cells_across += 1
            cw = ch = int(vw / cells_across)
    
        vw = cw * cells_across
        
        # debug
        print("cells across ",  cells_across)
        print("cw ",  cw)
        print("ch ",  ch)
        print("vw ", vw)
        
        # set frame size
        if getDefault("singleWindowMode") == 1:
            x, y, w, h = fw.window().getPosSize()
            fw.editor.splitView.setDimension('fontOverview', vw)
            fw.editor.splitView.setDimension('glyphView', w - vw)
            fw.centerGlyphInView()
        else:
            windows = NSApp().orderedWindows()
            (x, y), (w, h) =  windows[0].frame()
            x_diff = w - vw
            windows[0].setFrame_display_animate_(((x + x_diff, y), (vw, h)), True, False)
    
        # do it
        v.setCellSize_([cw, ch])
        fo.views.sizeSlider.set(cw)
        setDefault("fontCollectionViewGlyphSize", int(cw))
        
        
registerFontOverviewSubscriber(fitGlyphCells)