import PyPDF2
import pandas as pd
import re
import os
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False
SOURCE = "PDF/20200218.pdf"
FILENAME = "data_18022020"
DATE = "18/02/2020"
COLUMNS_NUMBER = 7
CONSIDERED_COLUMNS = [[0,1,6,7],[0,2,4,7]] # NON CHINA,  CHINA
TABLE_PAGES = [3,2]
COLLAPSE_BRACKETS = True
START_WORDS = ["Republic","Hubei"] # NON CHINA,  CHINA
END_WORDS = ["Subtotal","Total"] # NON CHINA,  CHINA
SKIP_WORDS = ["South-East", "Asia", "Region", "Western", "Pacific", "of", "the", "Americas", "European", "Eastern", "Mediterranean"]
HEADER = "Country,Confirmed,Deaths,Date"
pdfFileObj = open(SOURCE, 'rb')
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
if os.path.exists(FILENAME+".csv"):
    os.remove(FILENAME+".csv")
for page_index,page in enumerate(TABLE_PAGES):
    pageObj = pdfReader.getPage(page)
    raw = pageObj.extractText()

    if COLLAPSE_BRACKETS:
        raw = re.sub("[\(\[].*?[\)\]]", "", raw)

    raw = raw.split(" ")
    for index,row in enumerate(raw):
        raw[index] = raw[index].strip()
        raw[index] = raw[index].replace('\n', '')

    found = False

    tmpTableElements = []
    for element in raw:
        if element == START_WORDS[page_index]:
            found = True
        if found:
            tmpTableElements.append(element)
    tableElements = []

    for index,element in enumerate(tmpTableElements):
        if element == '' or element in SKIP_WORDS:
            continue
        tableElements.append(element)
        while index+1 < len(tmpTableElements) and not is_number(element) and not is_number(tmpTableElements[index+1]):
            tableElements[-1] += " "+tmpTableElements[index+1] 
            tmpTableElements.remove(tmpTableElements[index+1])
 
    csvFile = open(FILENAME+"-"+str(page_index)+".csv", 'w')
    for index,element in enumerate(tableElements):
        if END_WORDS[page_index] in element:
            break
        if (index+1) % COLUMNS_NUMBER == 0 and index != 0:
            csvFile.write(element+",")
            csvFile.write(DATE)
            csvFile.write("\n")
        else:
            csvFile.write(element+",")



    csvFile.close()


    df = pd.read_csv(FILENAME+"-"+str(page_index)+".csv", usecols = CONSIDERED_COLUMNS[page_index])
    csvFile = open(FILENAME+".csv", 'a+')
    if page_index == 0:
        csvFile.write(HEADER)
        csvFile.write("\n")
    os.remove(FILENAME+"-"+str(page_index)+".csv")
    csvFile.write(df.to_csv(index=False).replace("\n",""))


