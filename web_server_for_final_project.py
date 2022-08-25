from flask import Flask ## This code is to create a web server for the latest photo captured
import os

camera_folder_path="/home/raspberry/camera" ## defining this path to display photos in this folder on web server
log_file_name="/home/raspberry/camera/photos_log.txt" ## defining this path to take name of the photos
photo_counter=0
app=Flask(__name__, static_url_path=camera_folder_path, static_folder=camera_folder_path)
@app.route("/") ## for homepage
def index(): ## homepage text
    return "Hello! Welcome back to raspberry pi Web server"
@app.route("/check-movement") ## if we write /check-movement after URL it will execute the below function
def check_movement(): ## defining this function to check for the latest photos and displaying it on web server
    message="" 
    line_counter=0 ## This line counter will count no of lines in log file i.e number of photos taken
    last_photo="" ## as we will show only last photo
    if os.path.exists(log_file_name): ## checking whether log file exists or not
        with open(log_file_name,"r") as f: 
            for lines in f: ## counting no of photos in LOG FILE
                line_counter += 1
                last_photo=lines ## when the loop will terminate the last photo will have last line i.e the latest photo captured
        global photo_counter
        Difference=line_counter-photo_counter ## displaying last photo and number of photos since the web server was last checked
        message=str(Difference)+" new photos were taken since you last checked. <br/><br/>"
        message += "Last Photo captured: "+str(last_photo)+"<br/>"
        message += "<img src=\""+last_photo+"\">"
        photo_counter=line_counter
    else:
        message="nothing new"
    return message

app.run(host="0.0.0.0")