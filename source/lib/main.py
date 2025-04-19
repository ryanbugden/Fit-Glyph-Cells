import math
from vanilla import ImageButton
from mojo.UI import CurrentFontWindow, getDefault, setDefault
from mojo.extensions import ExtensionBundle, getExtensionDefault
from mojo.subscriber import Subscriber, registerFontOverviewSubscriber
import importlib
import defaults
importlib.reload(defaults)
from defaults import FGC_EXTENSION_KEY


BUNDLE = ExtensionBundle("Fit Glyph Cells")
ICON = BUNDLE.getResourceImage("icon")
INITIAL_CELL_SIZE = 10


def calculate_cells_per_row(cell_count, view_width, view_height):
    """
    Calculate the optimal number of cells per row that will fit in the given view dimensions.
    """
    def fits(cells_per_row):
        total_rows = math.ceil(cell_count / cells_per_row)
        cell_size = view_width / cells_per_row
        collection_height = total_rows * cell_size
        return collection_height <= view_height 
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
    font_overview_width, font_overview_height = font_overview.getNSView().frameSize().width, font_overview.getNSView().frameSize().height
    
    glyph_collection = font_overview.getGlyphCollection()
    cell_view = glyph_collection.getGlyphCellView()
    
    # Initialize with small cell size to get accurate frame sizes
    cell_view.setCellSize_([INITIAL_CELL_SIZE, INITIAL_CELL_SIZE])
    
    view_width, view_height = cell_view.frameSize().width, cell_view.frameSize().height
    sets_menu_width = font_overview_width - view_width
    
    return view_width, view_height, font_overview_width, font_overview_height, sets_menu_width, window_width

def adjust_window(font_window, width_diff, height_diff, view_width, window_width):
    """
    Adjust the window layout based on single/multi-window mode.
    """
    is_single_window = getDefault("singleWindowMode")
    
    if is_single_window:
        new_fo_w = view_width + width_diff
        new_window_width = window_width - new_fo_w
        font_window.editor.splitView.setDimension('fontOverview', new_fo_w)
        font_window.editor.splitView.setDimension('glyphView', new_window_width)
        font_window.centerGlyphInView()
    else:
        window = font_window.window().getNSWindow()
        (x, y), (w, h) = window.frame()
        window.setFrame_display_animate_(
            ((x - width_diff, y), (w + width_diff, h - height_diff)), True, False
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
        view_width, view_height, fo_width, fo_height, sets_width, window_width = get_view_dimensions(font_window)
    
        # Calculate grid layout
        font_overview = font_window.fontOverview
        glyph_collection = font_overview.getGlyphCollection()
        cell_view = glyph_collection.getGlyphCellView()
        num_glyphs = len(glyph_collection.getGlyphNames())
    
        cols = calculate_cells_per_row(num_glyphs, view_width, view_height)
        cell_size = math.floor(view_width / cols)
        max_cell_size = getExtensionDefault(FGC_EXTENSION_KEY)["maxCellSize"]
        if max_cell_size > 0 and max_cell_size < cell_size:
            cell_size = max_cell_size
        rows = math.ceil(num_glyphs / cols)
        new_view_width = cell_size * cols
        new_view_height = cell_size * rows
    
        # Update view sizes
        cell_view.setCellSize_([cell_size, cell_size])
        font_overview.views.sizeSlider.set(cell_size)
        setDefault("fontCollectionViewGlyphSize", cell_size)
    
        # Adjust window layout
        adjust_width, adjust_height = getExtensionDefault(FGC_EXTENSION_KEY)["allowWidthAdjust"], getExtensionDefault(FGC_EXTENSION_KEY)["allowHeightAdjust"]
        if adjust_width or adjust_height:
            width_diff, height_diff = 0, 0
            if adjust_width:
                width_diff = (new_view_width + sets_width) - view_width
            if adjust_height:
                height_diff = view_height - new_view_height
            adjust_window(
                font_window, 
                width_diff,
                height_diff,
                # Clean this up later
                view_width,
                window_width
            )
        
        
registerFontOverviewSubscriber(FitGlyphCells)