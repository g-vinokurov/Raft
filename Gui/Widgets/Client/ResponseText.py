
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

from Gui.Fonts import Font
from Gui.Themes import CurrentTheme as Theme

from Log import log


class ResponseText(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        self.setObjectName('client-response-text')

        self.setStyleSheet(f'''
            color: {Theme.ClientResponseTextColor};
            background: none;
            border: none;
            outline: none;
            padding: 0px;
        ''')
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setWordWrap(False)
        
        font = Font(Theme.ClientResponseTextFont)
        font.setPointSize(Theme.ClientResponseTextFontSize)
        font.setWeight(Theme.ClientResponseTextFontWeight)
        self.setFont(font)

        self.setText('')
