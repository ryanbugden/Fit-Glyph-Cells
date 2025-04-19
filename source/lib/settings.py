import ezui
from mojo.extensions import getExtensionDefault, setExtensionDefault
import importlib
import defaults
importlib.reload(defaults)
from defaults import FGC_EXTENSION_KEY, FGC_EXTENSION_DEFAULTS


class FitGlyphCellsSettings(ezui.WindowController):

    def build(self):
        content = """
        * TwoColumnForm        @form
        
        > : Fit on Open:
        > [X]                  @fitOnOpen
        
        > : Allowance:
        > [_ 0 _]              @allowance
        
        > : Max Cell Size:
        > [_ 99 _]             @maxCellSize
        
        ---
        
        (Reset Defaults)       @resetDefaultsButton
        """
        title_column_width = 100
        item_column_width = 70
        descriptionData = dict(
            form=dict(
                titleColumnWidth=title_column_width,
                itemColumnWidth=item_column_width
            ),
            allowance=dict(
                valueType="float",
                value=0,
                valueIncrement=0.1,
                valueWidth=50,
            ),
            maxCellSize=dict(
                valueType="integer",
                value=99,
                minValue=0,
                valueIncrement=1,
                valueWidth=50,
            ),
            resetDefaultsButton=dict(
                width='fill'
            ),
        )
        self.w = ezui.EZWindow(
            title="Settings",
            content=content,
            descriptionData=descriptionData,
            controller=self
        )
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        prefs = getExtensionDefault(FGC_EXTENSION_KEY, fallback=FGC_EXTENSION_DEFAULTS)
        try: self.w.setItemValues(prefs)
        except KeyError as e: print(f"Fit Glyph Cells Settings error: {e}")
        
    def started(self):
        self.w.open()
        
    def formCallback(self, sender):
        setExtensionDefault(FGC_EXTENSION_KEY, self.w.getItemValues())
        
    def resetDefaultsButtonCallback(self, sender):
        self.w.setItemValues(FGC_EXTENSION_DEFAULTS)
        setExtensionDefault(FGC_EXTENSION_KEY, FGC_EXTENSION_DEFAULTS)
        

if __name__ == '__main__':
    FitGlyphCellsSettings()
    