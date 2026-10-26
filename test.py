from mojo.UI import CurrentFontWindow


def get_view_dimensions(font_window):
    """
    Get the dimensions of various views in the font window.
    """
    x, y, window_width, h = font_window.window().getPosSize()
    font_overview = font_window.fontOverview
    font_overview_width, font_overview_height = (
        font_overview.getNSView().frameSize().width,
        font_overview.getNSView().frameSize().height,
    )

    glyph_collection = font_overview.getGlyphCollection()
    cell_view = glyph_collection.getGlyphCellView()

    # Initialize with small cell size to get accurate frame sizes
    cell_view.setCellSize_([10, 10])

    view_width, view_height = cell_view.frameSize().width, cell_view.frameSize().height
    sets_menu_width = font_overview_width - view_width

    return (
        view_width,
        view_height,
        font_overview_width,
        font_overview_height,
        sets_menu_width,
        window_width,
    )


(
    view_width,
    view_height,
    font_overview_width,
    font_overview_height,
    sets_menu_width,
    window_width,
) = get_view_dimensions(CurrentFontWindow())

print("view_width", view_width)
print("view_height", view_height)
print("font_overview_width", font_overview_width)
print("font_overview_height", font_overview_height)
print("sets_menu_width", sets_menu_width)
print("window_width", window_width)

"""
view_width 875.0
view_height 325.0
font_overview_width 875.0
font_overview_height 345.0
sets_menu_width 0.0
window_width 875.0
"""
