import os, sys
sys.path.append(os.path.join(os.getcwd(), "../matcher"))
from search import SearchService
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
app = Flask(__name__)

search_service = SearchService()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        file.save(os.path.join(os.getcwd() +'/imgs/', file.filename))
        matches = search_service.search(os.path.join(os.getcwd() + '/imgs/', file.filename))
        coordinates = [ list(m.location)  for m in matches ]
        print coordinates
        return redirect(url_for('uploaded_file', coordinates=coordinates))
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

if __name__ == '__main__':
    app.run(debug=True)
