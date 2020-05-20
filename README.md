# Fit Glyph Cells
A RoboFont [start-up script](https://robofont.com/documentation/how-tos/setting-up-a-startup-script/) that places a button to the left of the glyph cell size slider (below Font Overview). This button, when pressed, sizes the glyph cells such that they’re as large as possible, while all being shown. 
<br><br>
*Note:
Font Overview window’s width also slightly changes, because they can be floats, while glyph cell size cannot.*

![](./_images/_fitGlyphCells_demo.png)


### Known issues:

* In Multi-Window mode, you may experience bad fitting. If so, make sure your `System Preferences > General > Show scroll bars` does not read `Automatically based on mouse or trackpad`.
* If you have open fonts and change your SWM preference, you may experience weird window/panel behavior unless you restart.


### Thanks:

Frederik Berlaen, Gustavo Ferreira, Frank Grießhammer, Connor Davenport

