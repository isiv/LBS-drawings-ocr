from flask import Flask, flash, request, redirect, url_for, render_template, Blueprint
from werkzeug.utils import secure_filename

from azure.storage.blob import BlobServiceClient
from azure.storage.blob import BlobClient

from azure.cognitiveservices.vision import computervision
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
#from azure.storage.blob import BlobClient

from array import array
import os
import csv
from PIL import Image
import sys
import time
from datetime import datetime
import socket

#Blob storage connection string


## Define static variables and paths
UPLOAD_FOLDER = 'website/static/'

##Global variables
CVfile = "file.png"
blobfile = "blob.png"

#current date and time
curDT = datetime.now()
day = curDT.strftime("%d.%m.%Y")
hour = curDT.strftime("%H:%M:%S")

## Define the blueprint
views = Blueprint('views', __name__)

## Define the allowed file extensions
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'tif'])
def allowed_filename(name):
    return '.' in name and name.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

## Define the route for the home page
@views.route('/', methods=['GET'])
def home():
    return render_template("index.html")

##Upload image locally and send it to the blob storage
@views.route('/', methods=['POST'])
def upload_image():

    if 'file' not in request.files:
        flash('No file was uploaded.')
        return redirect(request.url) 
   
    file = request.files['file']

    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)

    if file and allowed_filename(file.filename):

        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        
        #IP of the submitter
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        
        ###Uploading to blob storage
        blobfile = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            service = BlobServiceClient.from_connection_string(connection_string)
            blob_client=service.get_blob_client(container="2023-01-19_124352_UTC",blob=filename)
            with open(blobfile, "rb") as data:
                blob_client.upload_blob(data)
        
        except Exception as e:
            print(e)  
    
        computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

        # Get URL of the image with text
        #read_image_url = "https://kbfilesforocr.blob.core.windows.net/drawings/UI/2023-01-19_124352_UTC" + filename
        read_image_url = "https://kbfilesforocr.blob.core.windows.net/drawings/UI/2023-01-19_124352_UTC/drawing2.jpg"

        #Write filename into log https://coating-values.azurewebsites.net/static/filelog.txt
        #myFile = open("website/static/filelog.txt", mode="a")
        #myFile.write(day + "\t" + hour + "\t" + IPAddr + "\t" + hostname + "\t" + filename + "\n")
        #myFile.close()
        
        # Call API with URL and raw response (allows you to get the operation location)
        read_response = computervision_client.read(read_image_url,  raw=True)

        # Get the operation location (URL with an ID at the end) from the response
        read_operation_location = read_response.headers["Operation-Location"]
    
        # Grab the ID from the URL
        operation_id = read_operation_location.split("/")[-1]

        # Call the "GET" API and wait for it to retrieve the results 
        while True:
            read_result = computervision_client.get_read_result(operation_id)
            if read_result.status not in ['notStarted', 'running']:
                break
            time.sleep(1)

        def has_numbers(inputString):
            return any(char.isdigit() for char in inputString)
                     
                     
                     
        """for drawing2.jpg
        sketches: [933.388, 350.714, 1047.451, 685.025], 0.994
        sketches: [2437.801, 678.825, 300.116, 338.413], 0.961
        sketches: [1037.657, 1229.139, 556.317, 437.341], 0.891
        sketches: [1819.478, 1010.46, 1269.438, 712.122], 0.856"""  
        box_x1 = 933.388
        box_y1 = 350.714
        box_x3 = box_x1 + 1047.451
        box_y3 = box_y1 + 685.025
                           
        if read_result.status == OperationStatusCodes.succeeded:
            outfile = open('output.csv', 'w')
            outfile.close()
            
            #if read_result.status == OperationStatusCodes.succeeded:
            for text_result in read_result.analyze_result.read_results:
                for line in text_result.lines:
                    x1 = line.bounding_box[0]
                    y1 = line.bounding_box[1]
                    x3 = line.bounding_box[4]
                    y3 = line.bounding_box[5]
                    
                    if x1 > box_x1 and y1 > box_y1 and x3 < box_x3 and y3 < box_y3:
                        if has_numbers(line.text, ):
                            # with open("output.csv", "a", newline="") as writeline:
                            #     csv_writer = csv.writer(writeline)
                            #     csv_writer.writerow(line.text)
                            file = open("output.csv",'a')
                            file.write(line.text + '\n')
                            file.close()
                            
                            
                            #flash(line.text)
                            """flash(x1)
                            flash(y1)
                            flash(x3)
                            flash(y3)
                            #flash(line.bounding_box)"""
                            #https://learn.microsoft.com/en-us/azure/cognitive-services/Computer-vision/quickstarts-sdk/client-library?pivots=programming-language-python&tabs=visual-studio
                            #-get bounding boxes - prepare for comparison - if is fits and has numbers > data frame - store df to csv
                            #filename - object number - value
            flash("done")






            # upper_limit="None"
            # coating="None"

            # #iterating (maybe) the pages of the file
            # for text_result in read_result.analyze_result.read_results:

            #     #iterating every line found within the page
            #     for line in text_result.lines:

            #         #restricting with nesting "if"s the target
            #         if has_numbers(line.text):

            #             coating= (line.text)

                        # if (line.text[line.text.index('um')-3]) == "-":
                        #     upper_limit= (line.text[line.text.index('um')-2]) + (line.text[line.text.index('um')-1]) + "um"
                        #     coating=(line.text[line.text.index('um')-5]) + (line.text[line.text.index('um')-4])+ "um"

                       
            #            flash("____" + coating)

                    # elif has_numbers(line.text) and "mm" in line.text and line.text[line.text.index('mm')-1].isdigit():

                    #     coating= (line.text[line.text.index('mm')-2]) + (line.text[line.text.index('mm')-1]) + "um"

                    #     if (line.text[line.text.index('mm')-3]) == "-":
                    #         upper_limit= (line.text[line.text.index('mm')-2]) + (line.text[line.text.index('mm')-1]) + "um"
                    #         coating=(line.text[line.text.index('mm')-5]) + (line.text[line.text.index('mm')-4])+ "um"

                    #     flash("Upper limit: " + upper_limit)
                    #     flash("Lower limit: " + coating)

                    # #shows dot for each line with numbers
                    # else:
                    #     flash(".") 
                       
        
            # try:
            #     service = BlobServiceClient.from_connection_string(connection_string)
            #     blob_client=service.get_blob_client(container="drawings",blob=filename)
            #     blob_client.delete_blob()
        
            # except Exception as e:
            #     print(e)  
            
            return render_template('index.html')
        
        else:
            try:
                service = BlobServiceClient.from_connection_string(connection_string)
                blob_client=service.get_blob_client(container="drawings",blob=filename)
                blob_client.delete_blob()
        
            except Exception as e:
                print(e) 
            
            return render_template('index.html')
        
    

    else:
        flash('Not an allowed file type, please use png, jpg, jpeg, tif, gif, pdf.')
        return redirect(request.url)



@views.route('/display/<filename>', methods=['GET'])
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)