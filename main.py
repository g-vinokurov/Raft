
import sys

from Gui.Widgets.Dashboard.Screen import DashboardScreen

from App import app


if __name__ == '__main__':
    this = 'localhost:9001'
    others = [
        'localhost:9002',
        'localhost:9003', 
        'localhost:9004',
        'localhost:9005'
    ]
    app.server.config(this, others)
    app.server.start()
    
    app.gui.navigator.register('dashboard', DashboardScreen)
    app.gui.navigator.goto('dashboard')
    app.gui.show()
    
    sys.exit(app.exec())
