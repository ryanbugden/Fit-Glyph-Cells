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
        
        > : Adjust Window:
        > [X] Width            @allowWidthAdjust
        > [X] Height           @allowHeightAdjust
        
        > : Max Cell Size:
        > [_ 99 _]             @maxCellSize
        
        > : Contextual Menu:
        > [X]                  @addToContextualMenu
        
        ---
        
        (Reset Defaults)       @resetDefaultsButton
        """
        title_column_width = 110
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
        
        # Load preferences with validation
        prefs = getExtensionDefault(FGC_EXTENSION_KEY, fallback=FGC_EXTENSION_DEFAULTS)
        # Ensure all required keys are present
        for key in FGC_EXTENSION_DEFAULTS:
            if key not in prefs:
                prefs[key] = FGC_EXTENSION_DEFAULTS[key]
        
        try:
            self.w.setItemValues(prefs)
        except KeyError as e:
            print(f"Fit Glyph Cells Settings error: {e}")
            # Fall back to defaults if there's an error
            self.w.setItemValues(FGC_EXTENSION_DEFAULTS)
        
    def started(self):
        self.w.open()
        
    def formCallback(self, sender):
        try:
            current_values = self.w.getItemValues()
            # Validate all required keys are present before saving
            for key in FGC_EXTENSION_DEFAULTS:
                if key not in current_values:
                    current_values[key] = FGC_EXTENSION_DEFAULTS[key]
            setExtensionDefault(FGC_EXTENSION_KEY, current_values)
        except Exception as e:
            print(f"Error saving preferences: {e}")
            
    def windowWillClose(self, sender):
        # Save preferences when window closes
        self.formCallback(sender)
        
    def resetDefaultsButtonCallback(self, sender):
        self.w.setItemValues(FGC_EXTENSION_DEFAULTS)
        setExtensionDefault(FGC_EXTENSION_KEY, FGC_EXTENSION_DEFAULTS)
        

if __name__ == '__main__':
    FitGlyphCellsSettings()
    