import RPi.GPIO as GPIO #Importing Relevant Libraries
import time
from picamera import PiCamera
import os
import yagmail

pir_pin=4 # connect out of the pir Sensor to GPIO pin # 4 and VCC and GND to 5v and GND respectively
led_pin=17 # connect smaller leg of the LED to GND and and resistor of 1k in parallel with the larger leg . connect the other leg of resistor in parallel with GPIO pin # 17
log_file_name="/home/raspberry/camera/photos_log.txt" # This is the file where info about the latest pics will be uploaded
def take_photo(cam): ## function to take photo from Pi cam
    filename="/home/raspberry/camera/img_"+str(time.time())+".jpg" ## used time.time to save photo with the time as name
    cam.capture(filename)
    return filename

def update_log_file(photo_file): ## function to upload latest photo taken in the photos_log.txt
    with open(log_file_name,"a") as f:
        f.write(photo_file)
        f.write("\n")
        
def send_email(yag_client,filename):## function to send email with the object image which is detected to the authorized person whenever a movement near Pi is detected
    yag_client.send(to="aazhmeerchhapra@gmail.com",
                             subject="MOVEMENT DETECTED!!!!!!",
                             contents="here is the picture of the moving object",
                             attachments=filename)
#setup GPIO
GPIO.setmode(GPIO.BCM) # setting Mode
GPIO.setup(pir_pin,GPIO.IN) ## setting Up PIR sensor to take input from it
GPIO.setup(led_pin,GPIO.OUT) ## setting up LED to give output to it
GPIO.output(led_pin,GPIO.LOW)## setting the intitial state of LED to close

print("GPIO setup is done")
#remove log
if os.path.exists(log_file_name): ## checking if the log file already exists then deleting it in order to keep the record of only those photos which were captured during current program execution
    os.remove(log_file_name)
    print("Log file Removed")
#camera setup to take photo
cam=PiCamera() 
cam.resolution=(720,480)
cam.brightness=60
cam.sharpness=60
print("wait 2 seconds before camera inits") ## camera will wait 2 seconds before taking the picture in order to set the resolution
time.sleep(2)
print("camera setup is done")
#setting up timer. This whole block will define  the time contraints which will be used as conditions for image capturing. It will be explained later in code
last_state=GPIO.input(pir_pin) # taking The state of the PIR sensor to compare in the below section
movement_time=time.time()
movement_threshold=3.0
image_capture_threshold=5.0
last_time_photo_taken=0

# setting up Email
with open("/home/raspberry/password/pass","r") as f: 
    password=f.read()
yag=yagmail.SMTP("raspaazhmeer@gmail.com",password)
print("setup is done\n")

try:
    while True:
        time.sleep(0.1) ## loop willl run after 0.1 seconds
        pir_input=GPIO.input(pir_pin) ## recording state of PIR Sensor
        if pir_input==GPIO.HIGH:## if object is detected led will be turned on
            GPIO.output(led_pin,GPIO.HIGH) 
        else:
            GPIO.output(led_pin,GPIO.LOW)
        if last_state==GPIO.LOW and pir_input==GPIO.HIGH: ## if the last state recorded is off and now PIR sensor is ON then movement_time will be updated
            movement_time=time.time()
        if last_state==GPIO.HIGH and pir_input==GPIO.HIGH: ## if last state and current state both is ON then we will check whether time difference between since object was first detected and current time is greater than 3 seconds
            if time.time() - movement_time > movement_threshold:
                if time.time() - last_time_photo_taken > image_capture_threshold: ## checking the time difference between previously captured photo and the current time is greater than 5
                    print("Capturing Picture") ## if all the above requirements are met i.e object is detected for 3 seconds and it's been 5 seconds since the last photo was captured, then it will capture the photo
                    photo_filename=take_photo(cam) ## then it will take photo and update it in log file
                    update_log_file(photo_filename)
                    print("sending via email")
                    send_email(yag,photo_filename) ## sending photo via email
                    print("Email sent")
                    last_time_photo_taken=time.time() ## updating the last_time_photo_taken to current time in order to compare again
        last_state=pir_input ## updating the PIR state to the current PIR state       
except KeyboardInterrupt: ## Program will stop if any key is presseds
    print("program stopped")
    GPIO.cleanup()

