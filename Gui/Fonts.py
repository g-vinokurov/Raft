
import pathlib

from PyQt5.QtWidgets import QApplication

from PyQt5.QtGui import QFontDatabase
from PyQt5.QtGui import QFont

from Config import FONTS_DIR

from Log import log


class Font(QFont):
    Thin       = QFont.Weight.Thin
    ExtraLight = QFont.Weight.ExtraLight
    Light      = QFont.Weight.Light
    Regular    = QFont.Weight.Normal
    Medium     = QFont.Weight.Medium
    SemiBold   = QFont.Weight.DemiBold
    Bold       = QFont.Weight.Bold
    ExtraBold  = QFont.Weight.ExtraBold
    Black      = QFont.Weight.Black
    
    _fonts = {}
    
    def __init__(self, path: str | pathlib.Path):
        path = str(path)
        if path not in self._fonts:
            self._load(path)
        super().__init__(self._fonts.get(path))
    
    @classmethod
    def _load(cls, path: str):

        if QApplication.instance() is None:
            log.warning('App not started - could not load fonts')
            return
        
        font_id = QFontDatabase.addApplicationFont(path)
        if font_id == -1:
            log.warning(f'Could not load font {path}')
            return

        families = QFontDatabase.applicationFontFamilies(font_id)
        if not families:
            return

        cls._fonts[path] = font = families[0]
        log.info(f'Font {font} loaded')


FONT_JET_BRAINS_MONO_NL_BOLD        = FONTS_DIR / 'JetBrainsMonoNL-Bold.ttf'
FONT_JET_BRAINS_MONO_NL_EXTRA_BOLD  = FONTS_DIR / 'JetBrainsMonoNL-ExtraBold.ttf'
FONT_JET_BRAINS_MONO_NL_EXTRA_LIGHT = FONTS_DIR / 'JetBrainsMonoNL-ExtraLight.ttf'
FONT_JET_BRAINS_MONO_NL_LIGHT       = FONTS_DIR / 'JetBrainsMonoNL-Light.ttf'
FONT_JET_BRAINS_MONO_NL_MEDIUM      = FONTS_DIR / 'JetBrainsMonoNL-Medium.ttf'
FONT_JET_BRAINS_MONO_NL_REGULAR     = FONTS_DIR / 'JetBrainsMonoNL-Regular.ttf'
FONT_JET_BRAINS_MONO_NL_SEMI_BOLD   = FONTS_DIR / 'JetBrainsMonoNL-SemiBold.ttf'
FONT_JET_BRAINS_MONO_NL_THIN        = FONTS_DIR / 'JetBrainsMonoNL-Thin.ttf'
