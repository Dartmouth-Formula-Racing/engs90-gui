import panel as pn
import base64
import os

TIME_SECOND_FIELD = 'Time (s)'
TIME_MILLISECOND_FIELD = 'Time (ms)'
EMPTY_FLOAT_PANEL_DISPLAY = pn.Row(visible = False, height = 0, width = 0)
EMPTY_TABULATOR_DISPLAY = pn.Row(visible=False, sizing_mode="stretch_both")
TABULATOR_PAGE_SIZE = 10
FLOAT_PANEL_BUTTON_HEIGHT = 35
FLOAT_PANEL_ROW_HEIGHT = 70
FLOAT_PANEL_TEXT_INPUT_HEIGHT = 70
FLOAT_PANEL_CHECKBOX_ROW_HEIGHT = 15
FLOAT_PANEL_TEXT_ROW_HEIGHT = 60
DEFAULT_FLOAT_PANEL_WIDTH = 500
FLOAT_PANEL_BUFFER_HEIGHT = 45
GROUPING_FLOAT_PANEL_HEIGHT = FLOAT_PANEL_TEXT_ROW_HEIGHT + 2 * FLOAT_PANEL_ROW_HEIGHT + FLOAT_PANEL_BUFFER_HEIGHT
EXPORT_PROJECT_FLOAT_PANEL_HEIGHT = FLOAT_PANEL_TEXT_ROW_HEIGHT + 3 * FLOAT_PANEL_ROW_HEIGHT + FLOAT_PANEL_CHECKBOX_ROW_HEIGHT + FLOAT_PANEL_BUFFER_HEIGHT
CREATE_PROJECT_FLOAT_PANEL_HEIGHT = FLOAT_PANEL_TEXT_ROW_HEIGHT + 5 * FLOAT_PANEL_ROW_HEIGHT + FLOAT_PANEL_BUFFER_HEIGHT
SIDEBAR_BUTTON_HEIGHT = 35
SIDEBAR_ROW_HEIGHT = 70
PLOT_MIN_HEIGHT = 600
USER_ROOT_PATH = os.path.expanduser("~")
UI_THEME_COLOR = "#00693e"
DBC_FILE_TYPES =  (("DBC Files","*.dbc"),("all files","*.*"))
LOG_FILE_TYPES = (("Data Files","*.log"),("all files","*.*"))
CSV_FILE_TYPES = (("CSV Files","*.csv"),("all files","*.*"))
FAVORITES_DIRECTORY_STRING = "./FAVORITES/"
PROJECTS_DIRECTORY_STRING = './PROJECTS/'
ERROR_NOTIFICATION_MILLISECOND_DURATION = 5000
SUCCESS_NOTIFICATION_MILLISECOND_DURATION = 5000
INFO_NOTIFICATION_DURATION = 5000
YAXIS_ERROR_NOTIFICATION_MILLISECOND_DURATION = 10000

EMPTY_STRING = ''
with open("DFRLOGO.png","rb") as image_file:
    LOGO_ENCODED_STRING = base64.b64encode(image_file.read()).decode("utf-8")

JSON_CSS = '''
.json-formatter-constructor-name {
    color: LightGray !important;
}
.json-formatter-key {
    color: black !important;
}
.json-formatter-number {
    color: #00693e !important;
}
'''
