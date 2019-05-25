import pandas as pd
import numpy as np

from bokeh.io import output_file, show, output_notebook
from bokeh.models import BasicTicker, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter, CustomJS
from bokeh.plotting import figure, curdoc

from bokeh.transform import transform

#Layout
from bokeh.layouts import column
from bokeh.embed import components
#widgets
from bokeh.models import Slider,HoverTool, CustomJS, Button, RadioButtonGroup
#events
from bokeh.events import ButtonClick


curdoc().clear()

# DATA EXTRACTION (.csv -> dataframe)

def extractData(filePath):
    df_data = pd.read_csv(filePath, sep=';', index_col = False, na_filter=False, skip_blank_lines=False)
    df_data.set_index('Unnamed: 0', inplace=True)
    #set column and row names
    df_data.columns.name = 'AuthorX'
    df_data.index.name = "AuthorY"
    return df_data

def sliceData(df, size):
    df_data_test = df.iloc[0:size, 0:size]
    return df_data_test

def stackDataframe(df):
    df_stacked =  pd.DataFrame(df.stack(), columns=['sim']).reset_index()
    return df_stacked

def toSource(df_stacked):
    source = ColumnDataSource(df_stacked)
    return source

def sortDataframe(df):
    df_sorted = df.sort_index(axis=0, level=None, ascending=True, inplace=False, kind='quicksort', na_position='last', sort_remaining=True, by=None)
    df_sorted = df_sorted.sort_index(axis=1, level=None, ascending=True, inplace=False, kind='quicksort', na_position='last', sort_remaining=True, by=None)
    return df_sorted

def generateRange(df):
    # Assure the order of the index and columns
    column_list = list(df.columns)
    index_list = list(df.index)
    index_list.reverse()
    return column_list, index_list

def callback_sort():
    df_sorted = sortDataframe(df_data)
    column_list_sorted, index_list_sorted = generateRange(df_sorted)
    matrixPlot.x_range.factors = column_list_sorted
    matrixPlot.y_range.factors = index_list_sorted
    # print(figure_matrix.x_range.factors)

def callback_unsort():
    matrixPlot.x_range.factors = column_list_original
    matrixPlot.y_range.factors = index_list_original
    # print(figure_matrix.x_range.factors)

def createWidgets(df_similarity):
    #interaction widgets
    button_sort = Button(label = "sort", button_type = "success")
    button_unsort = Button(label = "unsort", button_type = "warning")  

    #color mapper
    mapper = LinearColorMapper(palette= "Viridis256", low=df_similarity.sim.min(), high=df_similarity.sim.max())
    color_bar = ColorBar(color_mapper=mapper, location=(0, 0),
                        ticker=BasicTicker(desired_num_ticks=10))
    
    return button_sort, button_unsort, mapper, color_bar
def createMatrix(width, height, column_list_original, index_list_original, mapper, color_bar, source_normal):
    #Color mapper
    
    #Hover information
    hover = HoverTool()
    hover.tooltips = [
        ("(Author1, Author2)", "(@AuthorX, @AuthorY)"),
        ("Similarity rate", "@sim"),
        ("Index", "@index")
    ]
    #Basic interaction tools
    TOOLS = "save,pan,box_zoom,reset,wheel_zoom"
    #Graph grid and properties
    figure_matrix = figure(plot_width = width, plot_height=height,
            x_range=column_list_original, y_range=index_list_original, #feeding columns and range
            toolbar_location="right", tools=TOOLS, x_axis_location="above")

    r = figure_matrix.rect(x='AuthorX', y='AuthorY', width=1, height=1, source=source_normal,#feeding x,y for each square
        line_color=None, fill_color=transform('sim', mapper))
    figure_matrix.tools.append(hover)
    figure_matrix.add_layout(color_bar, 'right')
    figure_matrix.axis.axis_line_color = None
    figure_matrix.axis.major_tick_line_color = None
    figure_matrix.axis.major_label_text_font_size = "7pt"
    figure_matrix.axis.major_label_standoff = 0
    figure_matrix.xaxis.major_label_orientation = np.pi/2
    return figure_matrix


filePath = "uploads/GephiMatrix_author_similarity.csv"
	# Initialize
df_data = extractData(filePath)
df_data = sliceData(df_data, 5)

df_similarity = stackDataframe(df_data)
source_normal = toSource(df_similarity)
column_list_original, index_list_original = generateRange(df_data)

df_sorted = sortDataframe(df_data)
df_similarity_sorted = stackDataframe(df_sorted)
source_sorted = toSource(df_similarity_sorted)

button_sort, button_unsort, mapper, color_bar = createWidgets(df_similarity)
button_sort.on_click(callback_sort)
button_unsort.on_click(callback_unsort)

matrixPlot = createMatrix(600, 600, column_list_original, index_list_original, mapper, color_bar, source_normal)



curdoc().add_root(column(matrixPlot, width=400))

# print(df_similarity)
