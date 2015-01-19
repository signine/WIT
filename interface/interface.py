import os
import cv2
import numpy
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from matcher import create_repo_and_match_image, Descriptor_Type
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        file.save(os.path.join('C:\Code\DesignProject', file.filename))
        input_img = cv2.imread(file.filename)
        best_match = create_repo_and_match_image(input_img, Descriptor_Type.ORB)
        return redirect(url_for('uploaded_file',  match=best_match))
    return '''
    <!doctype html>
        <title>Where is this? Photo Location Finder</title>
        <h1>Upload a photo to retrieve the coordinates.</h1>
        <form action="" method=post enctype=multipart/form-data>
            <p><input type=file name=file>
            <input type=submit value=Upload>
        </form>
    '''
	
@app.route('/uploads/<match>')
def uploaded_file(match):
    coordinateList = [[43.6592, -79.3935 ]] #[43.6584115,-79.3976985], [43.6592653, -79.3959926]]
    return render_template('drawmaps.html', coordinateList = coordinateList)#send_from_directory('C:\Code\DesignProject\Test\database',match)

if __name__ == '__main__':
    app.run(debug=True)