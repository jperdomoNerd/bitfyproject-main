# -*- coding: utf-8 -*-
"""
Created on Sun May  7 11:37:31 2023

@author: SANTI
"""

#import datetime as dt
#import random
#from docx2pdf import convert
#import matplotlib.pyplot as plt
from docxtpl import DocxTemplate

# create a document object
doc = DocxTemplate("reportTmpl.docx")

# create data for reports
salesTblRows = [{'sNo': 1, 'name': 'Item 1', 'cPu': 12, 'nUnits': 458, 'revenue': 5496}, {'sNo': 2, 'name': 'Item 2', 'cPu': 9, 'nUnits': 375, 'revenue': 3375}, {'sNo': 3, 'name': 'Item 3', 'cPu': 11, 'nUnits': 259, 'revenue': 2849}, {'sNo': 4, 'name': 'Item 4', 'cPu': 1, 'nUnits': 464, 'revenue': 464}, {'sNo': 5, 'name': 'Item 5', 'cPu': 8, 'nUnits': 235, 'revenue': 1880}]

topItems = ['Item 1', 'Item 2', 'Item 3']
topItems2 = ['172.18.25.1','172.18.26.2','172.18.27.3']


todayStr = "test"

print (salesTblRows)
print (topItems)
# create context to pass data to template
context = {
    "reportDtStr": todayStr,
    "salesTblRows": salesTblRows,
    "topItemsRows": topItems,
    "topItemsRows2": topItems2
}



# render context into the document object
doc.render(context)

# save the document object as a word file
reportWordPath = 'reports/report_{0}.docx'.format(todayStr)
doc.save(reportWordPath)

# convert the word file as pdf file
# convert(reportWordPath, reportWordPath.replace(".docx", ".pdf"))