import sys

from Gui.Widgets.Client.Screen import ClientScreen

from App import app


if __name__ == '__main__':

    app.gui.navigator.register('client', ClientScreen)
    app.gui.navigator.goto('client')
    app.gui.show()
    
    sys.exit(app.exec())
