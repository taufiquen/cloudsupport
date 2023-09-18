# Cloud Support

The purpose of this Python script is to provide our customer the ability to add CC email addresses to their support cases after they are created. 

## How does it work?
The script will go through all the NEW cases (not old cases) and update the CC list with the email defined under DockerFile.

## How To Use This Script:

* Please create a clone of this repo to your local machine
* Please go through the Getting Started [https://cloud.google.com/support/docs/reference/v2#getting-started] section
* Please make sure to create a Service Account as mentioned above and download the JSON key file
* Rename the file to service_account.json and put the file under the same directory step #1
* Edit the DockerFile and enter email addresses that you'd like to CC in each case
* After making the changes, build the docker image from the same directory by using `docker build -t cloudsupport .`
* Now you can deploy this image to Cloud Run [https://cloud.google.com/run/docs/deploying] or GKE CronJob [https://cloud.google.com/kubernetes-engine/docs/how-to/cronjobs] according to your need (1 min, 5 min, or any interval)
