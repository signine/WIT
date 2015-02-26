import os, sys
import numpy as np
import simplejson as json
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
        return redirect(url_for('uploaded_file', coordinates=json.dumps(coordinates)))
    return '''
    <!doctype html>
        <title>Where is this? Photo Location Finder</title>
        <h1>Upload a photo to retrieve the coordinates.</h1>
        <form action="" method=post enctype=multipart/form-data>
            <p><input type=file name=file>
            <input type=submit value=Upload>
        </form>
    '''
	
@app.route('/uploads/<coordinates>')
def uploaded_file(coordinates):
    coordinateList = coordinates #[43.6584115,-79.3976985], [43.6592653, -79.3959926]]
    return render_template('drawmap.html', coordinateList = coordinateList)#send_from_directory('C:\Code\DesignProject\Test\database',match)

@app.route('/warmcache/')
def warm_cache():
  search_service.warm_cache()
  return redirect(url_for('upload_file'))

if __name__ == '__main__':
  if len(sys.argv) > 1:
    env = sys.argv[1]
  else:
    env = 'dev'

  if env == 'live':
    app.run(host='0.0.0.0', port=80)
  # dev
  else:
    app.run(debug=True)
