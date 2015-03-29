import os, sys
import numpy as np
sys.path.append(os.path.join(os.getcwd(), "../matcher"))
from search import SearchService
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
app = Flask(__name__)

IMG_DIR = os.path.join(os.getcwd(), "imgs/")
search_service = SearchService()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = os.path.join(IMG_DIR, file.filename)
        file.save(filename)
        matches = search_service.search(filename)
        coordinates = [ list(m.location) for m in matches ]
        print coordinates
        return redirect(url_for('uploaded_file', coordinates=coordinates))
    return '''
    <!doctype html>
    <link rel="stylesheet" media="screen" href="http://openfontlibrary.org/face/gen-light" rel="stylesheet" type="text/css"/> 
        <body>
        <title>Where is this? Photo Location Finder</title>
        <br><br><br><br>
        <div id="header">
        Where is this? Photo Location Finder
        </div>
        <div id="section">
        <h3>Upload a photo to retrieve the coordinates.</h3>
        <form action="" method=post enctype=multipart/form-data >
            <input type=file name=file ">
            <input type=submit value=Upload ">
        </form><br>
        </div><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
        <div id="footer">
        Camilla Tabis and Shamil Ishraq
        </div>
        </body>
        <style>
            @font-face {
                font-family: myFirstFont;
                src: bb.otf;
            }

           body {
                background-image:url('imgs/bg.png');
                background-size:100%;
            }

            #header {
                background-color:black;
                color:white;
                width:500px;
                margin: 0 auto;
                text-align:center;
                font-family: 'GenW01Light'; 
                padding:20px;
            }
            #nav {
                line-height:30px;
                background-color:#eeeeee;
                height:300px;
                width:100px;
                float:left;
                padding:5px;
            }
            #section {
                background-color:#DEEFFF;
                width:500px;
                margin: 0 auto;
                padding:20px;
                text-align:center;
                font-family: 'GenW01Light'; 
            }
            #footer {
                float: right;

                font-family: 'GenW01Light'; 
                text-align: right;
                width: 259px;
            }
        </style>    
    '''
	
@app.route('/uploads/<coordinates>')
def uploaded_file(coordinates):
    coordinateList = coordinates #[43.6584115,-79.3976985], [43.6592653, -79.3959926]]
    return render_template('drawmap.html', coordinateList = coordinateList)#send_from_directory('C:\Code\DesignProject\Test\database',match)

@app.route('/imgs/<path:path>')
def serve_img(path):
  return send_from_directory('imgs', path)

@app.route('/warmcache/')
def warm_cache():
  search_service.warm_cache()
  return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True)
