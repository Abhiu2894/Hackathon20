import xlrd
import json
import numpy
import matplotlib.pyplot as plt
import os, pandas as pd
import seaborn as sns
import config
from datetime import date, timedelta
from watson_developer_cloud import NaturalLanguageClassifierV1
#natural_language_classifier = NaturalLanguageClassifierV1(iam_apikey='5MkcCE3a8-yQS1RcAXmNTYXvUiwWOqMBIDhw3MLaQb5d')
natural_language_classifier = NaturalLanguageClassifierV1(iam_apikey= config.api_key)
# Give the location of the file
loc = "Incident_latest.xls"
# To open Workbook
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)
#To hold all top-classes and all months
topclass=[];
pyMON=[];
for i in range(sheet.nrows):
    print(sheet.cell_value(i, 0))
    #define a function to convert the date
    def from_excel_ordinal(ordinal, epoch=date(1900, 1, 1)):
 
      if ordinal > 59:
        ordinal -= 1  # Excel leap year bug, 1900 is not a leap year!
      inDays = int(ordinal)
      frac = ordinal - inDays
      inSecs = int(round(frac * 86400.0))
      return epoch + timedelta(days=inDays - 1, seconds=inSecs) # epoch is day 1

    #convert into date
    pyDT = from_excel_ordinal(sheet.cell_value(i, 1))
    #print year
    print(pyDT.strftime("%Y"))
    #print month
    py_MON = pyDT.strftime("%m")
    #pyMON = pyMON.astype(str)
    print(py_MON)
    #print day
    #print(pyDT.strftime("%d"))
    if sheet.cell_type(i, 0) != xlrd.XL_CELL_EMPTY:
        classes = natural_language_classifier.classify(config.nlc_key, sheet.cell_value(i, 0))
        resp=json.loads(str(classes))
        print (resp['result']['top_class'])
        topclass.append(resp['result']['top_class'])
        pyMON.append(py_MON)


ungrpPieData=numpy.array(topclass)
unique, counts = numpy.unique(ungrpPieData, return_counts=True)
pieData=dict(zip(unique, counts))
plt.pie(pieData.values(), labels=pieData.keys(),autopct="%.1f%%")
plt.show()

# aggregate data 
pyMONARR = numpy.array(pyMON)
print(pyMONARR)
pyCATARR = ungrpPieData
print(pyCATARR)

data = {'CATEGORY': pyCATARR, 'MONTH': pyMONARR}
df = pd.DataFrame(data=data)
print(df)

dfgrpby = df.groupby(['MONTH','CATEGORY']).size().reset_index(name='COUNT')
print(dfgrpby )
uniuqecat = dfgrpby['CATEGORY'].unique()
print(uniuqecat)

sns.barplot(data=dfgrpby.dropna(), x='CATEGORY',y='COUNT',hue='MONTH',ci=None)

plt.show(block='false');