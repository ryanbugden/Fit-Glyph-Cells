import os
from AppKit import NSApp, NSMenuItem, NSAlternateKeyMask, NSCommandKeyMask
import math
from vanilla import ImageButton
from mojo.tools import CallbackWrapper
from mojo.UI import CurrentFontWindow, getDefault, setDefault
from mojo.extensions import ExtensionBundle, getExtensionDefault, setExtensionDefault
from mojo.subscriber import Subscriber, registerFontOverviewSubscriber
import importlib
import defaults
importlib.reload(defaults)
from defaults import FGC_EXTENSION_KEY, FGC_EXTENSION_DEFAULTS


BUNDLE = ExtensionBundle("Fit Glyph Cells")
ICON = BUNDLE.getResourceImage("icon")
INITIAL_CELL_SIZE = 10


def calculate_cells_per_row(cell_count, view_width, view_height):
    """
    Calculate the optimal number of cells per row that will fit in the given view dimensions.
    """
    def fits(cells_per_row):
        total_rows = math.ceil(cell_count / cells_per_row)
        cell_width = view_width / cells_per_row
        collection_height = total_rows * cell_width
        return collection_height - (getExtensionDefault(FGC_EXTENSION_KEY)["allowance"] * cell_width) <= view_height 
    cells_per_row = 1
    while not fits(cells_per_row):
        cells_per_row += 1
    return cells_per_row

def get_view_dimensions(font_window):
    """
    Get the dimensions of various views in the font window.
    """
    x, y, window_width, h = font_window.window().getPosSize()
    font_overview = font_window.fontOverview
    font_overview_width = font_overview.getNSView().frameSize().width
    
    glyph_collection = font_overview.getGlyphCollection()
    cell_view = glyph_collection.getGlyphCellView()
    
    # Initialize with small cell size to get accurate frame sizes
    cell_view.setCellSize_([INITIAL_CELL_SIZE, INITIAL_CELL_SIZE])
    
    view_width, view_height = cell_view.frameSize().width, cell_view.frameSize().height
    sets_menu_width = font_overview_width - view_width
    
    return view_width, view_height, font_overview_width, sets_menu_width, window_width

def adjust_window_layout(font_window, desired_overview_width):
    """
    Adjust the window layout based on single/multi-window mode.
    """
    is_single_window = getDefault("singleWindowMode") == 1
    
    if is_single_window:
        window_width = font_window.window().getPosSize()[2]
        font_window.editor.splitView.setDimension('fontOverview', desired_overview_width)
        font_window.editor.splitView.setDimension('glyphView', window_width - desired_overview_width)
        font_window.centerGlyphInView()
    else:
        window = font_window.window().getNSWindow()
        (x, y), (w, h) = window.frame()
        x_diff = w - desired_overview_width
        window.setFrame_display_animate_(
            ((x + x_diff, y), (desired_overview_width, h)), True, False
        )


class FitGlyphCells(Subscriber):
    '''
    Scale the glyph cells in Font Overview as large as 
    they can be while justified to the width of the frame.
    
    Ryan Bugden
    '''

    def fontOverviewWillOpen(self, info):
        # Add button
        self.sb = info["fontOverview"].statusBar
        if hasattr(self.sb, 'fit_button'):
            del self.sb.fit_button
        self.sb.fit_button = ImageButton(
            (-122, -19, 18, 18), 
            imageObject = ICON,
            callback = self.fit_glyph_cells, 
            sizeStyle = 'regular'
            )
        self.sb.fit_button.getNSButton().setBordered_(0)
        self.sb.fit_button.getNSButton().setBezelStyle_(2)
        self.sb.fit_button.getNSButton().image().setTemplate_(True)
        
    def fontDocumentWindowDidOpen(self, info):
        font_window = info['lowLevelEvents'][0]['window']
        # Fit the glyph cells, per the setting
        if getExtensionDefault(FGC_EXTENSION_KEY)["fitOnOpen"]:
            self.fit_glyph_cells(None, font_window)

    def fontOverviewWantsContextualMenuItems(self, info):
        """Add contextual menu item."""
        menu_items = [
            ("Fit Glyph Cells", self.fit_glyph_cells)
        ]
        info["itemDescriptions"].extend(menu_items)

    def fit_glyph_cells(self, sender, font_window=None):
        """Updates the glyph cell sizes and font overview size."""
        if not font_window:
            font_window = CurrentFontWindow()
            if not font_window:
                return

        # Get view dimensions
        view_width, view_height, fo_width, sets_width, window_width = get_view_dimensions(font_window)
    
        # Calculate grid layout
        font_overview = font_window.fontOverview
        glyph_collection = font_overview.getGlyphCollection()
        cell_view = glyph_collection.getGlyphCellView()
        num_glyphs = len(glyph_collection.getGlyphNames())
    
        cols = calculate_cells_per_row(num_glyphs, view_width, view_height)
        cell_width = math.floor(view_width / cols)
        desired_view_width = cell_width * cols
        desired_overview_width = desired_view_width + sets_width
    
        # Update view sizes
        cell_view.setCellSize_([cell_width, cell_width])
        font_overview.views.sizeSlider.set(cell_width)
        setDefault("fontCollectionViewGlyphSize", cell_width)
    
        # Adjust window layout
        adjust_window_layout(
            font_window, 
            desired_overview_width
        )
        
        
registerFontOverviewSubscriber(FitGlyphCells)