import panel as pn
import os
import pandas as pd
import CANverter as canvtr
import projects
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import Tk
import traceback
import pickle
from getcomponents import *
from constants import *

pn.extension('plotly')
pn.extension('tabulator')
pn.extension('floatpanel')
pn.extension(notifications=True)
Tk().withdraw()
pn.state.notifications.position = 'bottom-right'

curr_project = projects.Project(TIME_MILLISECOND_FIELD)
time_series_canverter = None
message_canverter = None
log_file_path = EMPTY_STRING
csv_file_path = EMPTY_STRING
project_options = get_projects()
current_project_name = EMPTY_STRING
favorites_options = get_favorites()

def build_current_project(log_file_path, project_name):
    global curr_project
    global time_series_canverter
    global message_canverter

    curr_project.ts_dataframe = time_series_canverter.log_to_dataframe(log_file_path)
    curr_project.ts_dataframe = curr_project.ts_dataframe.sort_values(by=TIME_MILLISECOND_FIELD)
    msg_df = message_canverter.log_to_dataframe(log_file_path).sort_values(by=TIME_MILLISECOND_FIELD).set_index(TIME_MILLISECOND_FIELD)
    curr_project.store_msg_df_as_dict(msg_df)
    with open(PROJECTS_DIRECTORY_STRING+project_name+".project", 'wb') as project:
        pickle.dump(curr_project, project)
    interpolate_dataframe()
    
def interpolate_dataframe():
    global curr_project
    print(TIME_SECOND_FIELD)
    if TIME_SECOND_FIELD not in curr_project.ts_dataframe.columns:
        print("\nNo Second time field!\n")
        curr_project.ts_dataframe.insert(0, TIME_SECOND_FIELD, curr_project.ts_dataframe[TIME_MILLISECOND_FIELD] / 1000)

    curr_project.ts_dataframe = curr_project.ts_dataframe.interpolate(method='linear', axis=0)
    all_columns = curr_project.ts_dataframe.columns.tolist()
    print(all_columns)
    x_axis_field_select.options = all_columns

    columns_to_remove = [TIME_SECOND_FIELD, TIME_MILLISECOND_FIELD]
    copy_current_dataframe = curr_project.ts_dataframe.drop(columns=columns_to_remove)
    y_columns = copy_current_dataframe.columns.tolist()
    y_axes_field_multiselect.options = y_columns

def update_message_log():
    global msg_json
    global curr_project
    msg_json.object = curr_project.msg_dict
       
"""
############################ FLOAT CALLBACKS ##################################
"""
def time_series_dbc_file_btn_callback(event):
    global time_series_canverter
    time_series_dbc_file_path = askopenfilename(title = "Select Time Series DBC File",filetypes = DBC_FILE_TYPES) 
    if time_series_dbc_file_path != EMPTY_STRING:
        time_series_dbc_file_input_text.value = time_series_dbc_file_path
        time_series_canverter = canvtr.CANverter(time_series_dbc_file_path)

def message_dbc_file_btn_callback(event):
    global message_canverter
    message_dbc_file_path = askopenfilename(title = "Select Message DBC File",filetypes = DBC_FILE_TYPES) 
    if message_dbc_file_path != EMPTY_STRING:
        message_dbc_file_input_text.value = message_dbc_file_path
        message_canverter = canvtr.CANverter(message_dbc_file_path)

def data_file_btn_callback(event):
    global log_file_path
    log_file_path = askopenfilename(title = "Select Data File",filetypes = LOG_FILE_TYPES) 
    if log_file_input_text != EMPTY_STRING:
        log_file_input_text.value = log_file_path
    
def create_project_button_callback(event):
    global time_series_canverter
    global message_canverter
    global log_file_path 
    global time_series_dbc_file_input_text
    global message_dbc_file_input_text
    global project_name_input_text
    import_notification = pn.state.notifications.info("Importing Data", duration=INFO_NOTIFICATION_DURATION)
    try:
        # Get the file extension
        log_file_path = log_file_input_text.value
        file_extension = log_file_path.split(".")[-1].lower()
        project_name = project_name_input_text.value.replace(" ", "_").lower()
        if project_name != None and project_name != EMPTY_STRING:
            if (file_extension == 'log'):
                if (time_series_canverter == None):
                    try:
                        time_series_canverter = canvtr.CANverter(time_series_dbc_file_input_text.value)
                    except Exception as ex:
                        pn.state.notifications.error("Importing Failed. Please provide a valid time series .dbc file.", duration=ERROR_NOTIFICATION_MILLISECOND_DURATION)
                        raise ex
                if (message_canverter == None):
                    try:
                        message_canverter = canvtr.CANverter(message_dbc_file_input_text.value)
                    except Exception as ex:
                        pn.state.notifications.error("Importing Failed. Please provide a valid message .dbc file.", duration=ERROR_NOTIFICATION_MILLISECOND_DURATION)
                        raise ex
                build_current_project(log_file_path, project_name)
                project_name_select.options = get_projects()
                project_name_input_text.value = EMPTY_STRING
                time_series_dbc_file_input_text = EMPTY_STRING
                message_dbc_file_input_text = EMPTY_STRING
                project_name_input_text = EMPTY_STRING
            else:
                pn.state.notifications.error("Importing Failed. Please provide a valid .log file", duration=ERROR_NOTIFICATION_MILLISECOND_DURATION)
                raise Exception
            import_notification.destroy()
            pn.state.notifications.success("Importing Successful!", SUCCESS_NOTIFICATION_MILLISECOND_DURATION)
    except Exception as e:
        traceback.print_exc()
        import_notification.destroy()
        pn.state.notifications.error("Importing Failed!", duration=ERROR_NOTIFICATION_MILLISECOND_DURATION)

def choose_csv_file_btn_callback(event):
    global csv_file_path
    csv_file_path = asksaveasfilename(title = "Save Exported CSV File", filetypes = CSV_FILE_TYPES)
    csv_export_text.value = csv_file_path

def save_csv_button_callback(event):
    global curr_project
    global csv_file_path
    global current_project_name
    csv_file_path = csv_export_text.value
    pn.state.notifications.info("Exporting Data...", duration=INFO_NOTIFICATION_DURATION)
    try:
        if interpolate_csv_btn.value:
            curr_project.ts_dataframe.to_csv(csv_file_path)
        else:
            pd.read_pickle(PROJECTS_DIRECTORY_STRING+current_project_name+".project").to_csv(csv_file_path)
        csv_file_path = EMPTY_STRING
        pn.state.notifications.success("Export Successful!", duration=SUCCESS_NOTIFICATION_MILLISECOND_DURATION)
    except:
        pn.state.notifications.error("Export Failed!", duration=ERROR_NOTIFICATION_MILLISECOND_DURATION)
        
def group_save_float_btn_callback(event):
    global favorites_select
    signals = y_axes_field_multiselect.value
    pn.state.notifications.info("Saving Data...", duration=INFO_NOTIFICATION_DURATION)
    try:
        with open(FAVORITES_DIRECTORY_STRING+ group_name.value + '.pkl','wb') as f:
            pickle.dump(signals,f)
        pn.state.notifications.success("Saving Successful!", duration=SUCCESS_NOTIFICATION_MILLISECOND_DURATION)
    except:
        pn.state.notifications.error("Saving Failed!", duration=ERROR_NOTIFICATION_MILLISECOND_DURATION)

    favorites_select.options = get_favorites()
    favorites_delete.options = get_favorites()

def delete_grouping_float_btn_callback(event):
    global favorites_select
    pn.state.notifications.info("Deleting Data...", duration=INFO_NOTIFICATION_DURATION)
    try:
        os.remove(FAVORITES_DIRECTORY_STRING + favorites_delete.value + '.pkl')
        pn.state.notifications.success("Deleting Successful!", duration=SUCCESS_NOTIFICATION_MILLISECOND_DURATION)
    except:
        pn.state.notifications.error("Deleting Failed!", duration=ERROR_NOTIFICATION_MILLISECOND_DURATION)

    favorites_select.options = get_favorites()
    favorites_delete.options = get_favorites()
    
"""
############################ SIDEBAR CALLBACKS ##################################
"""
def export_project_float_btn_callback(event):
    csv_export_text.placeholder = USER_ROOT_PATH
    update_float_display(float_panel_display, create_float_panel(export_project_float_panel, 'Export to CSV', height=EXPORT_PROJECT_FLOAT_PANEL_HEIGHT))

def create_project_float_btn_callback(event):
    update_float_display(float_panel_display, create_float_panel(create_project_float_panel, name='Create Project', height=CREATE_PROJECT_FLOAT_PANEL_HEIGHT))
    project_name_input_text.placeholder = "Project Name..."
    time_series_dbc_file_input_text.placeholder = USER_ROOT_PATH
    log_file_input_text.placeholder = USER_ROOT_PATH
    update_message_log()
    
def clear_all_columns_btn_callback(event):
    y_axes_field_multiselect.value = []

def generate_plot_btn_callback(event):
    global curr_project
    plotly_pane.object = update_graph_figure(curr_project.ts_dataframe, y_axes_field_multiselect.value, x_axis_field_select.value, combine_axes_switch.value)
    final_filter = y_axes_field_multiselect.value.copy()
    final_filter.insert(0, TIME_MILLISECOND_FIELD)
    update_tabulator_display(tabulator_display, pn.widgets.Tabulator(curr_project.ts_dataframe[final_filter], show_index = False, page_size=TABULATOR_PAGE_SIZE, layout='fit_columns', sizing_mode='stretch_width'))

def favorites_save_btn_callback(event):
    update_float_display(float_panel_display, create_float_panel(save_groupings_float_panel, name='Save Signal Grouping', height=GROUPING_FLOAT_PANEL_HEIGHT))

def favorites_del_btn_callback(event):
    update_float_display(float_panel_display, create_float_panel(delete_groupings_float_panel, name='Save Signal Grouping', height=GROUPING_FLOAT_PANEL_HEIGHT))

"""
############################ SIDEBAR COMPONENTS ##################################
"""
project_name_select = pn.widgets.Select(name='Select Project',options=project_options, align="center")
@pn.depends(project_name_select.param.value, watch=True)
def update_project(project_name_select):
    global curr_project, current_project_name
    y_axes_field_multiselect.name = "Y axes fields for "+project_name_select
    x_axis_field_select.name = "X axis field for "+project_name_select
    y_axes_field_multiselect.value = []
    x_axis_field_select.value = TIME_MILLISECOND_FIELD
    x_axis_field_select.value = TIME_SECOND_FIELD
    with open(PROJECTS_DIRECTORY_STRING+project_name_select+".project", 'rb') as project:
        curr_project = pickle.load(project)
    interpolate_dataframe()
    current_project_name = project_name_select

favorites_select = pn.widgets.Select(name='Signal Groupings',options=favorites_options)
@pn.depends(favorites_select.param.value, watch=True)
def favorites_load(favorites_select):
    try:
        with open(FAVORITES_DIRECTORY_STRING+ favorites_select + '.pkl','rb') as f:
            y_axes_field_multiselect.value = pickle.load(f)
    except:
        y_axes_field_multiselect.value = []
        
clear_all_columns_btn = create_button(clear_all_columns_btn_callback, 'Clear all columns', SIDEBAR_BUTTON_HEIGHT, SIDEBAR_ROW_HEIGHT)
generate_plot_btn = create_button(generate_plot_btn_callback, 'Generate plot', SIDEBAR_BUTTON_HEIGHT, SIDEBAR_ROW_HEIGHT)
create_project_button = create_button(create_project_button_callback, 'Create Project', SIDEBAR_BUTTON_HEIGHT, SIDEBAR_ROW_HEIGHT)
create_project_float_btn = create_button(create_project_float_btn_callback, 'Create Project',  SIDEBAR_BUTTON_HEIGHT, SIDEBAR_ROW_HEIGHT)
export_project_float_btn = create_button(export_project_float_btn_callback, 'Export Project', SIDEBAR_BUTTON_HEIGHT, SIDEBAR_ROW_HEIGHT)
combine_axes_switch_name = pn.widgets.StaticText(name='Combine Y-Axes', value=EMPTY_STRING)
combine_axes_tooltip = pn.widgets.TooltipIcon(value="Click the \"Generate plot\" button below to implement changes", width=20)
y_axes_field_multiselect = pn.widgets.MultiChoice(name="Y Variables for "+project_name_select.value, value=[],options=[], align="center")
x_axis_field_select = pn.widgets.Select(name="X Variable for "+project_name_select.value,options=[])
favorites_save_btn = create_button(favorites_save_btn_callback, 'Save Grouping', SIDEBAR_BUTTON_HEIGHT, SIDEBAR_ROW_HEIGHT)
favorites_del_btn = create_button(favorites_del_btn_callback, 'Delete Grouping', SIDEBAR_BUTTON_HEIGHT, SIDEBAR_ROW_HEIGHT)
combine_axes_switch = pn.widgets.Switch(name='Switch')

main_sidebar = pn.Column(
    pn.Row(create_project_float_btn, export_project_float_btn, height=SIDEBAR_ROW_HEIGHT),
    pn.Row(project_name_select, height=SIDEBAR_ROW_HEIGHT),
    pn.Tabs(("Manual",
                pn.Column(
                    pn.Row(generate_plot_btn, clear_all_columns_btn, height = SIDEBAR_ROW_HEIGHT),
                    pn.Row(favorites_select,  height = SIDEBAR_ROW_HEIGHT),
                    pn.Row(favorites_save_btn, favorites_del_btn, height = SIDEBAR_ROW_HEIGHT),
                    pn.Row(combine_axes_switch_name, combine_axes_tooltip, combine_axes_switch, height = SIDEBAR_ROW_HEIGHT),
                    pn.Row(x_axis_field_select, height = SIDEBAR_ROW_HEIGHT),
                    pn.Row(y_axes_field_multiselect, height = SIDEBAR_ROW_HEIGHT),
                )
            ),
            ( "Groupings",
                pn.Column(
                    pn.Row(favorites_select, height = SIDEBAR_ROW_HEIGHT),
                    pn.Row(favorites_save_btn, favorites_del_btn, height = SIDEBAR_ROW_HEIGHT),
                ),
            )
    )
)

"""
############################ FLOAT COMPONENTS ################################### 
"""
#Delete Grouping Float Panel Components
delete_grouping_float_btn = create_button(delete_grouping_float_btn_callback, 'Delete', FLOAT_PANEL_BUTTON_HEIGHT)
favorites_delete = pn.widgets.Select(name='Signal Groupings', options=favorites_options, )

#Save Grouping Float Panel Components
group_save_float_btn = create_button(group_save_float_btn_callback, 'Save', FLOAT_PANEL_BUTTON_HEIGHT)
group_name = pn.widgets.TextInput(name=EMPTY_STRING, placeholder='Enter a name here...')

#Create New Project Float Panel Components
time_series_dbc_file_btn = create_button(time_series_dbc_file_btn_callback, 'Upload .dbc file',  FLOAT_PANEL_BUTTON_HEIGHT, FLOAT_PANEL_ROW_HEIGHT)
message_dbc_file_btn = create_button(message_dbc_file_btn_callback, 'Upload .dbc file',  FLOAT_PANEL_BUTTON_HEIGHT, FLOAT_PANEL_ROW_HEIGHT)
data_file_btn = create_button(data_file_btn_callback, 'Upload .log file',  FLOAT_PANEL_BUTTON_HEIGHT, FLOAT_PANEL_ROW_HEIGHT)
time_series_dbc_file_input_text = pn.widgets.TextInput(name="Time series .dbc file", placeholder=USER_ROOT_PATH, height = FLOAT_PANEL_TEXT_INPUT_HEIGHT, align='center')
message_dbc_file_input_text = pn.widgets.TextInput(name="Messages .dbc file", placeholder=USER_ROOT_PATH, height = FLOAT_PANEL_TEXT_INPUT_HEIGHT, align='center')
log_file_input_text = pn.widgets.TextInput(name="CAN data .log file", placeholder=USER_ROOT_PATH, height = FLOAT_PANEL_TEXT_INPUT_HEIGHT, align='center')
project_name_input_text = pn.widgets.TextInput(name="Project Name", placeholder = "Project Name...", height=FLOAT_PANEL_TEXT_INPUT_HEIGHT, align='center')

#Export Project Float Panel Components
csv_export_text = pn.widgets.TextInput(name="Choose output directory", placeholder=USER_ROOT_PATH, height = FLOAT_PANEL_TEXT_INPUT_HEIGHT, align='center')
choose_csv_file_btn = create_button(choose_csv_file_btn_callback, 'Create .csv', FLOAT_PANEL_BUTTON_HEIGHT, FLOAT_PANEL_ROW_HEIGHT)
save_csv_button = create_button(save_csv_button_callback, 'Save', FLOAT_PANEL_BUTTON_HEIGHT, FLOAT_PANEL_ROW_HEIGHT)
interpolate_csv_btn = pn.widgets.Checkbox(name='Interpolate Data')

#Delete Groupings Float Panel
delete_groupings_float_panel = pn.Column(
    pn.Row("Select a signal grouping to delete:", height=FLOAT_PANEL_TEXT_ROW_HEIGHT),
    pn.Row(favorites_delete, height = FLOAT_PANEL_ROW_HEIGHT),
    pn.Row(delete_grouping_float_btn, height = FLOAT_PANEL_ROW_HEIGHT),
)

#Save Groupings Float Panel
save_groupings_float_panel = pn.Column(
    pn.Row("Name your signal grouping. Be sure to use _ for spaces between words:", height=FLOAT_PANEL_TEXT_ROW_HEIGHT),
    pn.Row(group_name, height = FLOAT_PANEL_ROW_HEIGHT),
    pn.Row(group_save_float_btn, height = FLOAT_PANEL_ROW_HEIGHT)
)

#Create Project Float Panel
create_project_float_panel = pn.Column(
    pn.Row("Name your project, select .log file, and .dbc file", height=FLOAT_PANEL_TEXT_ROW_HEIGHT),
    pn.Row(project_name_input_text, height = FLOAT_PANEL_ROW_HEIGHT),
    pn.Row(time_series_dbc_file_input_text, time_series_dbc_file_btn, height = FLOAT_PANEL_ROW_HEIGHT),
    pn.Row(message_dbc_file_input_text, message_dbc_file_btn, height = FLOAT_PANEL_ROW_HEIGHT,),
    pn.Row(log_file_input_text, data_file_btn, height = FLOAT_PANEL_ROW_HEIGHT),
    pn.Row(create_project_button, height = FLOAT_PANEL_ROW_HEIGHT),
) 

#Export Project Float Panel
export_project_float_panel = pn.Column(
    pn.Row("Select the project you want to export into a .csv", height=FLOAT_PANEL_TEXT_ROW_HEIGHT),
    pn.Row(project_name_select, height = FLOAT_PANEL_ROW_HEIGHT),
    pn.Row(csv_export_text, choose_csv_file_btn, height = FLOAT_PANEL_ROW_HEIGHT),
    pn.Row(interpolate_csv_btn, height = FLOAT_PANEL_CHECKBOX_ROW_HEIGHT),
    pn.Row(save_csv_button, height = FLOAT_PANEL_ROW_HEIGHT)
)

"""
############################ MAIN COMPONENTS ##################################
"""
figure = update_graph_figure(curr_project.ts_dataframe, y_axes_field_multiselect.value, x_axis_field_select.value, combine_axes_switch.value)
plotly_pane = pn.pane.Plotly(figure, sizing_mode="stretch_both")
plot_display = pn.Row(plotly_pane, min_height=PLOT_MIN_HEIGHT, sizing_mode="stretch_both")
tabulator_display = EMPTY_TABULATOR_DISPLAY
float_panel_display = EMPTY_FLOAT_PANEL_DISPLAY
msg_json = pn.pane.JSON({'No messages':EMPTY_STRING}, name='message log', sizing_mode='stretch_width', theme='light') #, hover_preview=True)

template = pn.template.FastListTemplate(
    title="Dartmouth Formula Racing",
    logo=f"data:image/jpeg;base64,{LOGO_ENCODED_STRING}",
    accent=UI_THEME_COLOR,
    sidebar=main_sidebar,
    shadow=False
)

template.main.append(pn.Tabs(
    ("Visualize Projects", pn.Column(plot_display, tabulator_display, float_panel_display)), 
    ("Real-Time Plotting", pn.Column()),
    ("Message Log", pn.Column(msg_json))
    )
)

pn.config.raw_css.append(JSON_CSS)
template.servable()
