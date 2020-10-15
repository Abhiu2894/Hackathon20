from flask import Flask, render_template,request
from watson_developer_cloud import NaturalLanguageClassifierV1
import os
import xlrd
import json
import numpy
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
import config

app = Flask(__name__)
uploadedfile=""
UPLOAD_FOLDER='/Users/arunasreej/PycharmProjects/TestP'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def meth1():
    return render_template("index.html")

@app.route("/uploadFile", methods = ['GET', 'POST'])
def uploadFile():
    if request.method == 'POST':
        f = request.files['file']
        global uploadedfile
        uploadedfile=os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
        f.save(uploadedfile)
        return 'file uploaded successfully'
@app.route("/processData")
def processData():
    natural_language_classifier = NaturalLanguageClassifierV1(iam_apikey=config.api_key)
    # Give the location of the file
    global uploadedfile
    loc=uploadedfile
    print(uploadedfile)
    # To open Workbook
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)
    # To hold all top-classes
    topclass = []
    result = []
    text = []
    finalresult = []

    for i in range(sheet.nrows):
        # print(sheet.cell_value(i, 0))
        if sheet.cell_type(i, 0) != xlrd.XL_CELL_EMPTY:
            classes = natural_language_classifier.classify(config.nlc_key, sheet.cell_value(i, 0))
            resp = json.loads(str(classes))
            print(sheet.row_values(i), resp['result'])
            topclass.append(resp['result']['top_class'])
            txt = {'class': resp['result']['top_class'], 'text': resp['result']['text']}
            text.append(txt)
    ungrpPieData = numpy.array(topclass)
    unique, counts = numpy.unique(ungrpPieData, return_counts=True)
    pieData = dict(zip(unique, counts))
   # plt.switch_backend('Agg')
    #plt.pie(pieData.values(), labels=pieData.keys())
    #plt.savefig('static/images/4Aruna.png')  # save to the images directory
    #return 'static/images/4Aruna.png'
    for k, v in pieData.items():
        result.append({"class": k, "count": int(v)})

    finalresult.append(result)
    finalresult.append(text)
    return (json.dumps(finalresult))


if __name__ == "__main__":        # on running python app.py
    app.run()                     # run the flask app