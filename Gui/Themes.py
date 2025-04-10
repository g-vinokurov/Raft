
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


class DefaultTheme(Theme):
    pass


CurrentTheme = DefaultTheme
