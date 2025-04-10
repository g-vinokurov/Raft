
from Gui import Colors
from Gui import Fonts


class Theme:
    TableBackgroundColor = Colors.COLOR_VSC_PRIMARY
    TableItemColor = Colors.COLOR_VSC_LIGHT
    TableItemSelectedBackgroundColor = Colors.COLOR_VSC_SECONDARY

    TableHeaderSectionBackgroundColor = Colors.COLOR_VSC_TERTIARY
    TableHeaderSectionColor = Colors.COLOR_VSC_LIGHT
    TableHeaderSectionBorderColor = Colors.COLOR_VSC_PRIMARY

    TableScrollBackgroundColor = Colors.COLOR_VSC_SECONDARY
    TableScrollBorderColor = Colors.COLOR_VSC_SECONDARY
    TableScrollHandleBackgroundColor = Colors.COLOR_VSC_TERTIARY

    TableFont       = Fonts.FONT_JET_BRAINS_MONO_NL_REGULAR
    TableFontWeight = Fonts.Font.Regular
    TableFontSize   = 9
    
    TableHeaderFont       = Fonts.FONT_JET_BRAINS_MONO_NL_LIGHT
    TableHeaderFontWeight = Fonts.Font.Light
    TableHeaderFontSize   = 8

    DashboardScreenBackgroundColor = Colors.COLOR_VSC_PRIMARY
    DashboardServerConfigSectionBackgroundColor = Colors.COLOR_VSC_PRIMARY
    DashboardServerLogSectionBackgroundColor = Colors.COLOR_VSC_PRIMARY
    DashboardServerStateSectionBackgroundColor = Colors.COLOR_VSC_PRIMARY
    DashboardServerStateSectionBorderColor = Colors.COLOR_VSC_TERTIARY

    DashboardStartStopServerBackgroundColor = Colors.COLOR_VSC_TERTIARY
    DashboardStartStopServerColor = Colors.COLOR_VSC_LIGHT
    DashboardStartStopServerFont = Fonts.FONT_JET_BRAINS_MONO_NL_LIGHT
    DashboardStartStopServerFontWeight = Fonts.Font.Light
    DashboardStartStopServerFontSize   = 10

    ClientScreenBackgroundColor = Colors.COLOR_WHITE

    ClientDeleteFromStorageBackgroundColor = Colors.COLOR_BS_DANDER
    ClientDeleteFromStorageColor = Colors.COLOR_WHITE
    ClientDeleteFromStorageFont = Fonts.FONT_JET_BRAINS_MONO_NL_LIGHT
    ClientDeleteFromStorageFontWeight = Fonts.Font.Light
    ClientDeleteFromStorageFontSize   = 10

    ClientGetFromStorageBackgroundColor = Colors.COLOR_BS_INFO
    ClientGetFromStorageColor = Colors.COLOR_WHITE
    ClientGetFromStorageFont = Fonts.FONT_JET_BRAINS_MONO_NL_LIGHT
    ClientGetFromStorageFontWeight = Fonts.Font.Light
    ClientGetFromStorageFontSize   = 10

    ClientPutToStorageBackgroundColor = Colors.COLOR_BS_SUCCESS
    ClientPutToStorageColor = Colors.COLOR_WHITE
    ClientPutToStorageFont = Fonts.FONT_JET_BRAINS_MONO_NL_LIGHT
    ClientPutToStorageFontWeight = Fonts.Font.Light
    ClientPutToStorageFontSize   = 10
    
    ClientKeyValueArgsBorderColor = Colors.COLOR_BS_DARK
    ClientKeyValueArgsColor = Colors.COLOR_BS_DARK
    ClientKeyValueArgsFont = Fonts.FONT_JET_BRAINS_MONO_NL_LIGHT
    ClientKeyValueArgsFontWeight = Fonts.Font.Light
    ClientKeyValueArgsFontSize   = 10
    
    ClientResponseTextColor = Colors.COLOR_BS_DARK
    ClientResponseTextFont = Fonts.FONT_JET_BRAINS_MONO_NL_LIGHT
    ClientResponseTextFontWeight = Fonts.Font.Light
    ClientResponseTextFontSize   = 10

class DefaultTheme(Theme):
    pass


CurrentTheme = DefaultTheme
