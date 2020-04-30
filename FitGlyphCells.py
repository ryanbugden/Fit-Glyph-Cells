import os
from AppKit import NSApp
import math
from mojo.events import addObserver
from mojo.UI import CurrentFontWindow
from lib.tools.defaults import getDefault
from vanilla import ImageButton

class fitGlyphCells(object):
    '''
    Scale the glyph cells in Font Overview as large as 
    they can be while justfied to the width of the frame.
    
    Ryan Bugden
    2020.04.3
    '''

    def __init__(self):
        self.i = 0
        self.resources_path = os.path.abspath("./resources")
        addObserver(self, "addButton", "fontWindowDidOpen")
        addObserver(self, "menu", "fontOverviewAdditionContextualMenuItems")

    def addButton(self, notification):
        
        self.sb = CurrentFontWindow().fontOverview.statusBar
        path = self.resources_path + '/_icon_Fit.pdf'

        fitButton = ImageButton(
            (-122, -19, 18, 18), 
            imagePath = path,
            callback = self.resize, 
            sizeStyle = 'regular'
            )
        fitButton.getNSButton().setBordered_(0)
        fitButton.getNSButton().setBezelStyle_(2)
        
        setattr(
            self.sb,
            'fit_button_%s' % self.i,
            fitButton)
                
        self.i += 1

    def menu(self, notification):
        myMenuItems = [
            ("Fit all glyphs in overview", self.resize)
        ]
        notification["additionContextualMenuItems"].extend(myMenuItems)

    def resize(self, sender):
        fo = CurrentFontWindow().fontOverview
        v = fo.getGlyphCollection().getGlyphCellView()


        # make cells small first
        starter = 10
        v.setCellSize_([starter, starter])
        # # need to recalculate frame (I assume this has to do with the scrollbar)
        # v.recalculateFrame()

        # get the width of the cell view
        vw = v.frameSize().width
        vh = v.frameSize().height

        # get number of glyphs
        num_g = len(fo.getGlyphOrder())

        print("vw ",  vw)
        print("vh ",  vh)
        print("num g ",  num_g)

        cells_across = 1
        extra_row = 0
        cw = int(vw / cells_across)
        while ((num_g) / cells_across) * cw > vh:
            cells_across += 1
            cw = ch = int(vw / cells_across)
    
        vw = cw * cells_across

        print("cells across ",  cells_across)
        print("cw ",  cw)
        print("ch ",  ch)
        print("vw ", vw)

        # set frame size
        if getDefault("singleWindowMode") == 1:
            v.recalculateFrame()
            x, y, w, h = fo.getPosSize()
            fo.setPosSize((x, y, vw, h))
        else:
            windows = NSApp().orderedWindows()
            (x, y), (w, h) =  windows[0].frame()
            x_diff = w - vw
            windows[0].setFrame_display_animate_(((x + x_diff, y), (vw, h)), True, False)
    
        # do it
        v.setCellSize_([cw, ch])
        fo.views.sizeSlider.set(cw)
        
fitGlyphCells()