import pandas as pd
import numpy as np

from bokeh.io import output_file, show
from bokeh.models import *
from bokeh.plotting import figure

from bokeh.transform import transform

#Layout
from bokeh.layouts import column
from bokeh.embed import components
#widgets
from bokeh.models import Slider,HoverTool, CustomJS, Button, RadioButtonGroup
#events
from bokeh.events import ButtonClick


#Node link
import networkx as nx
from bokeh.models import Plot, Range1d, MultiLine, Circle, HoverTool, TapTool, BoxSelectTool
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges, EdgesAndLinkedNodes
from bokeh.palettes import Spectral4


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

def createWidgets(df_similarity):

    #color mapper
    mapper = LinearColorMapper(palette= "Viridis256", low=df_similarity.sim.min(), high=df_similarity.sim.max())
    color_bar = ColorBar(color_mapper=mapper, location=(0, 0),
                        ticker=BasicTicker(desired_num_ticks=10))
    
    return mapper, color_bar
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
    figure_matrix = figure(plot_width = width, plot_height=height, sizing_mode = "scale_both",
            x_range=column_list_original, y_range=index_list_original, #feeding columns and range
            toolbar_location="below", tools=TOOLS, x_axis_location="above")

    r = figure_matrix.rect(x='AuthorX', y='AuthorY', width=1, height=1, source=source_normal,#feeding x,y for each square
        line_color=None, fill_color=transform('sim', mapper))

    figure_matrix.tools.append(hover)
    figure_matrix.add_layout(color_bar, 'right')
    figure_matrix.axis.axis_line_color = None
    figure_matrix.axis.major_tick_line_color = None
    figure_matrix.axis.major_label_text_font_size = "5pt"
    figure_matrix.axis.major_label_standoff = 0
    figure_matrix.xaxis.major_label_orientation = np.pi/2
    return figure_matrix




# ----------------------------------> Plotting the graph <---------------------------------- #
def nodeLink(df_data):
    plot_dimension = 800
    plot_range = (plot_dimension / 2)
    # TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom, point_draw"
    plot = Plot(x_range=Range1d(-plot_range, plot_range), y_range=Range1d(-plot_range, plot_range), output_backend="webgl", 
            width = plot_dimension, height = plot_dimension, sizing_mode = "scale_both")
    df_raw = pd.DataFrame(df_data.stack(), columns=['edge_weight'])
    df_refined = df_raw[df_raw['edge_weight'] > 0.3].reset_index()
    
    G = nx.from_pandas_dataframe(df_refined, 'AuthorY', 'AuthorX', 'edge_weight')
    
    graph = from_networkx(G, nx.circular_layout, scale=(plot_range * 0.8), center=(0,0))
    # formatting the dataframe into a stacked version that represents the start_node, end_node, and edge_weight
    # rendering the nodes in the graph
    graph.node_renderer.glyph = Circle(size=15, fill_color=Spectral4[0])            # Rendering every node as a circle
    graph.node_renderer.selection_glyph = Circle(size=15, fill_color=Spectral4[2])  # When you select the node, it become orange
    graph.node_renderer.hover_glyph = Circle(size=15, fill_color=Spectral4[1])      # When you hover the node, it become green

    # rendering the edges in the graph
    graph.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=5)   # Rendering every edge as a line
    graph.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=5)      # When you select a node, the connected egdes become orange
    graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=5)          # When you hover a node, the connected edges become green

    graph.selection_policy = NodesAndLinkedEdges()
    graph.inspection_policy = NodesAndLinkedEdges() #EdgesAndLinkedNodes() (<-- does not work) #NodesAndLinkedEdges()

    plot.add_tools(HoverTool(tooltips=[("Name", "@index")]), TapTool(), BoxSelectTool())
    plot.renderers.append(graph)

    return plot

