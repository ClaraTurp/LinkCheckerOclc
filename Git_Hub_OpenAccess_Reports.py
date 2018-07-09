## The following code queries OCLC's Knowledge Base API for a particular collection (using the collection ID) and sends a report (Kbart as attachment) by email of all the broken links.
## This code has been designed to check Open Access collections.
## 2018-07-06 Clara Turp, for McGill University Library.


import csv
import re
import requests
import urllib3
import urllib.request
import codecs
import smtplib
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


###################
#    Functions
###################

#KB API Functions
def queryBuilder(collectionName):

    parameters = "&link@rel=enclosure"
    myKey = "wskey=ThisIsMyWsApiKey"
    myQuery = "https://worldcat.org/webservices/kb/rest/collections/" + collectionName + myKey + parameters

    return myQuery


def callQuery(myUrl):
    response = requests.get(myUrl)
    xmlOutput = response.content.decode("utf-8")

    return xmlOutput

#Find, download and read Kbart
def matchKbartFilePattern(xmlOutput):

    kbartUrl = re.findall('<link\shref=\"([^\s]*_kbart.txt)\"\srel="enclosure"\stype="text\/csv;\scharset=UTF-8\"\stitle=\"kbart\sfile\"\slength=\".*\"\s\/>', xmlOutput)

    return kbartUrl


def kbartDownloadUrl(kbartUrl):

    myUrl = kbartUrl +"?"
    myKey = "wskey=ThisIsMyWsApiKey"
    myKbartUrl = myUrl + myKey

    return myKbartUrl

def kbartReader(myUrl):
   
    urlOutput = urllib.request.urlopen(myUrl)
    csvfile = csv.reader(codecs.iterdecode(urlOutput, 'utf-8'))

    return csvfile

#String cleaners
def lineCleaner(line):

    lineArray = []
    line = "".join(line)
    lineArray = line.split("\t")

    return lineArray

def stringCleaner(string):

    string = string.rstrip("\n")
    string = string.strip()

    return string

#Link checker
def testUrl(currentUrl):

    status = ""
    try:
        r = requests.get(currentUrl, timeout = 30 )
        code = r.status_code
        newUrl = r.url
        if code == 404:
            status = "error"
        elif code == 400:
            status = "error"
        else:
            try:
                matchFound = re.match(newUrl, currentUrl)
                currentUrlWithSlash = currentUrl + "/"
                matchCurrentUrlWithSlash = re.match(newUrl, currentUrlWithSlash)
                newUrlWithSlash = newUrl + "/"
                matchNewUrlWithSlash = re.match(newUrlWithSlash, line)
                if matchFound or matchCurrentUrlWithSlash or matchNewUrlWithSlash:
                    status = "ok"
                else:
                    status = "redirects"
            except re.error:
                status = "redirects"

    except requests.exceptions.RequestException:
        status = "error"

    except urllib3.exceptions.LocationValueError:
        status = "error"
    
    except UnicodeError:
        status = "error"

    return status

def statusSorting(status, currentLine, currentUrl, errorFoundArray, redirectsArray):

    if status == "error":
        errorFoundArray.append(currentLine)
    elif status == "redirects":
        if not re.match("^(https|http)://doi.org", currentUrl):
            r = requests.get(currentUrl, timeout = 30 )
            newUrl = r.url
            currentLine[9] = newUrl
            redirectsArray.append(currentLine)
            
#Print in file
def printFile(myArray, filename):

    myPrintFile = open(filename, "w", newline = "", encoding="utf-8", errors= "ignore")
    writerFile = csv.writer(myPrintFile)
    for line in myArray:
        writerFile.writerow(line)

#Send emails
        
# The following two email functions have been adapted from a code shared by Rob (user:8747) on stack overflow. 
# https://stackoverflow.com/questions/41469952/sending-an-email-via-the-python-email-library-throws-error-expected-string-or-b

def email(fromEmail, toEmail, filename, message):

    msg = MIMEMultipart()
    msg['Subject'] = 'Report| Problematic links in Open Access Collection'
    msg['From'] = fromEmail
    msg['To'] = toEmail
    msg.preamble = 'preamble'

    body = MIMEText(message)
    msg.attach(body)

    with open(filename) as fp:
        record = MIMEText(fp.read())
        record['Content-Disposition'] = 'attachment; filename=' + filename
        msg.attach(record)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(fromEmail, "myPassword")
    server.sendmail(fromEmail, toEmail, msg.as_string())
    server.quit()

    
 def noReportsEmail(fromEmail, toEmail, message):

    msg = MIMEMultipart()
    msg['Subject'] = 'Report| Problematic links in Open Access Collection'
    msg['From'] = fromEmail
    msg['To'] = toEmail

    body = MIMEText(message)
    msg.attach(body)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(fromEmail, "myPassword")
    server.sendmail(fromEmail, toEmail, msg.as_string())
    server.quit()


###################
#    Main Code   
###################

collectionsArray = ["ThisIsMyCollectionID", "ThisIsMyCollectionID2", "ThisIsMyCollectionID3"]

for collection in collectionsArray:

    errorFoundArray = []
    redirectsArray = []

    myUrl = queryBuilder(collection + "?")
    xmlOutput = callQuery(myUrl)
    myKbartUrl = matchKbartFilePattern(xmlOutput)

    myKbart = kbartDownloadUrl(myKbartUrl[0])
    csvfile = kbartReader(myKbart)
    
    for line in csvfile:
        cleanedLineArray = lineCleaner(line)
       
        if cleanedLineArray[0] != "publication_title":
            cleanedCurrentUrl = stringCleaner(cleanedLineArray[9])
            urlStatus = testUrl(cleanedCurrentUrl)
            statusSorting(urlStatus, cleanedLineArray, cleanedCurrentUrl, errorFoundArray, redirectsArray)

            
    if len(redirectsArray) > 0:
        printFileName = "openAccess_redirects_results_" + collection + ".csv"
        message = "Report of redirecting links in collection " + collection+ ". The links have been corrected in the attached file."

        printFile(redirectsArray, printFileName)
        email("fromEmail@gmail.com", "toEmail@email.ca", printFileName, message)

    if len(errorFoundArray) > 0:
        printFileName = "openAccess_errors_results_" + collection + ".csv"
        message = "Report of broken links in collection " + collection + "."

        printFile(errorFoundArray, printFileName)
        email("fromEmail@gmail.com", "toEmail@email.ca", printFileName, message)
    
    elif len(errorFoundArray) == 0 and len(redirectsArray) == 0:
        message = "No broken or redirecting links were found in collection: " + collection + "." 

        noReportsEmail("fromEmail@gmail.com", "toEmail@email.ca", message)




