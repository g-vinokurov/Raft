
import sys

from Gui.Widgets.Dashboard.Screen import DashboardScreen

from App import app


if __name__ == '__main__':

    app.gui.navigator.register('dashboard', DashboardScreen)
    app.gui.navigator.goto('dashboard')
    app.gui.show()
    
    sys.exit(app.exec())
