## On Home Server

This service, if VM is set up correctly, will run the service locally on port 8000. I will then have a shell script to run this a service on start up based off of a 'milo' boolean. This Will run the service and expose the port from within the connected WIFI.

## Must Activate Milo env to make code work
source ~/Documents/environments/milo-env/bin/activate

## Server located?

Currently Env is in ~/Documents/environments/milo-env

Where I will have all requirements installed and additionally in this local project - brought in all bigger shared resources from google drive - such as LLMs and TTS quantised models. As this Laptop acting as Home Server has limited CPU and GPU capabilities.

## Static IP Exposed in WiFi
ip = 192.168.4.39