import networkx as nx
import pandas as pd

from bokeh.io import show, output_file, curdoc
from bokeh.models import Plot, Range1d, MultiLine, Circle, HoverTool, TapTool, BoxSelectTool
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges, EdgesAndLinkedNodes
from bokeh.palettes import Spectral4

# importing the CSV file and create a complete DataFrame
data = pd.read_csv('GephiMatrix_author_similarity.csv', sep=';', index_col=False, na_filter=False, skip_blank_lines=False)
data.set_index('Unnamed: 0', inplace=True)
data.columns.name = 'AuthorX'
data.index.name = "AuthorY"
data = data.iloc[0:5,0:5]

# ----------------------------------> Plotting the graph <---------------------------------- #
plot_dimension = 800
plot_range = (plot_dimension / 2)

# Creating the plot in wich the graph will be present
TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"
plot = Plot(x_range=Range1d(-plot_range, plot_range), y_range=Range1d(-plot_range, plot_range), output_backend="webgl", 
            width = plot_dimension, height = plot_dimension)
# tools=TOOLS)
    
# formatting the dataframe into a stacked version that represents the start_node, end_node, and edge_weight
df_raw = pd.DataFrame(data.stack(), columns=['edge_weight'])

# df with nodes that have edges_weight >= value
df_refined = df_raw[df_raw['edge_weight'] >= 0.1].reset_index()

G = nx.from_pandas_dataframe(df_refined, 'AuthorY', 'AuthorX', 'edge_weight')

plot.title.text = "Graph Interaction Demonstration"
plot.add_tools(HoverTool(tooltips=[("Name", "@index")]), TapTool(), BoxSelectTool())

graph = from_networkx(G, nx.circular_layout, scale=(plot_range * 0.8), center=(0,0))

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

plot.renderers.append(graph)
# output_file("NetworkGraph.html")

# inputs = column(range_slider, weight_slider)
# add to document
# curdoc().add_root(row(inputs, plot))
curdoc().add_root(plot)
# curdoc().title = "Clustering"
# show(plot)

# pip install networkx==1.11