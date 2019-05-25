import os
from os import *
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
from plot import *

UPLOAD_FOLDER = 'uploads/'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = "csv"
# ROUTING
@app.route('/')
def homePage():
	return render_template('index.html')

@app.route("/filelist")
def plot(dataset = ""):
	filePath = UPLOAD_FOLDER
	files = os.listdir(filePath)
	# No files were uploaded
	if not files:
		tip = "No dataset was uploaded"
		return render_template("fileList.html", heading = tip)
	#Exists uploaded file
	return render_template("fileList.html", files = files, heading = "")

@app.route("/visualization/<string:dataset>")
def visualization(dataset = ""):
	#getting required file name from URL
	uploadedFile = dataset
	filePath = UPLOAD_FOLDER + uploadedFile
	df_data = extractData(filePath)
	df_data = sliceData(df_data, 50)
	

	df_similarity = stackDataframe(df_data)
	source_normal = toSource(df_similarity)
	column_list_original, index_list_original = generateRange(df_data)

	df_sorted = sortDataframe(df_data)
	df_similarity_sorted = stackDataframe(df_sorted)
	source_sorted = toSource(df_similarity_sorted)
	
	def callback_sort(df_data):
		df_sorted = sortDataframe(df_data)
		column_list_sorted, index_list_sorted = generateRange(df_sorted)
		return column_list_sorted, index_list_sorted

	mapper, color_bar = createWidgets(df_similarity)

	reorder_method = request.args.get("reorder_method")
	if reorder_method == "sortByAuthor":
		column_list_sorted, index_list_sorted = callback_sort(df_data)
		matrixPlot = createMatrix(800, 800, column_list_sorted, index_list_sorted, mapper, color_bar, source_normal)
	else:
		matrixPlot = createMatrix(800, 800, column_list_original, index_list_original, mapper, color_bar, source_normal)
	
	nodelinkPlot = nodeLink(df_data)

	script, divs = components((matrixPlot, nodelinkPlot))	
	return render_template("visualization.html", script = script, divs = divs)



@app.route('/documentation')
def about():
    return render_template("doc.html")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS\


#FORM HANDLER
@app.route('/', methods=['POST'])
def upload_file():
	if request.method == 'POST':
        # check if the post request has the file part
		if 'userDataset' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['userDataset']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			flash('File(s) successfully uploaded')
			return redirect('/visualization/' + filename)



if __name__ == "__main__":
    app.run(debug = True)