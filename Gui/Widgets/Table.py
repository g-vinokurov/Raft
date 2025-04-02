
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QAbstractScrollArea

from PyQt5.QtCore import Qt

from Gui.Fonts import Font
from Gui.Themes import CurrentTheme as Theme


class Table(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):       
        # https://programmersought.com/article/225611454918/
        self.setStyleSheet(f'''
            QTableWidget {{
                background-color: {Theme.TableBackgroundColor}; 
                border: none;
            }}

            QTableWidget::item {{
                color: {Theme.TableItemColor};
                padding: 20px;
            }}

            QTableWidget::item:selected {{
                background-color: {Theme.TableItemSelectedBackgroundColor};
            }}

            QHeaderView::section {{
                background-color: {Theme.TableHeaderSectionBackgroundColor};
                border: none;
                color: {Theme.TableHeaderSectionColor};
                border-right: 1px solid {Theme.TableHeaderSectionBorderColor};
            }}

            QScrollBar:horizontal {{
                height: 15px;
                border: 1px transparent {Theme.TableScrollBorderColor};
                background-color: {Theme.TableScrollBackgroundColor};
            }}

            QScrollBar::handle:horizontal {{
                background-color: {Theme.TableScrollHandleBackgroundColor};
                min-width: 5px;
            }}

            QScrollBar::add-line:horizontal {{
                background: none;
            }}

            QScrollBar::sub-line:horizontal {{
                background: none;
            }}

            QScrollBar::up-arrow:horizontal {{
                background: none;
            }}

            QScrollBar::down-arrow:horizontal {{
                background: none;
            }}

            QScrollBar::add-page:horizontal {{
                background: none;
            }}

            QScrollBar::sub-page:horizontal {{
                background: none;
            }}

            QScrollBar:vertical {{
                background-color: {Theme.TableScrollBackgroundColor};
                width: 15px;
                border: 1px transparent {Theme.TableScrollBorderColor};
            }}

            QScrollBar::handle:vertical {{
                background-color: {Theme.TableScrollHandleBackgroundColor};
                min-height: 5px;
            }}

            QScrollBar::add-line:vertical {{
                background: none;
            }}

            QScrollBar::sub-line:vertical {{
                background: none;
            }}

            QScrollBar::up-arrow:vertical {{
                background: none;
            }}

            QScrollBar::down-arrow:vertical {{
                background: none;
            }}

            QScrollBar::add-page:vertical {{
                background: none;
            }}

            QScrollBar::sub-page:vertical {{
                background: none;
            }}
        ''')
        # Customize rows in QTableWidget
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(True)
        self.setShowGrid(True)
        
        # Make columns fill the full width of QTableWidget but with min cell width
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        
        self.setSortingEnabled(True)

        table_font = Font(Theme.TableFont)
        table_font.setPointSize(Theme.TableFontSize)
        table_font.setWeight(Theme.TableFontWeight)
        self.setFont(table_font)
        
        header_font = Font(Theme.TableHeaderFont)
        header_font.setPointSize(Theme.TableHeaderFontSize)
        header_font.setWeight(Theme.TableHeaderFontWeight)
        self.horizontalHeader().setFont(header_font)
