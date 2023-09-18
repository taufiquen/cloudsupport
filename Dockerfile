# Deriving the latest base image
FROM python:latest

# Creating Application Source Code Directory
RUN mkdir -p /cloud_support/src

# Working Directory
WORKDIR /cloud_support/src

# Setting Email Addresses
ENV EMAIL_ADDRESSES="email_1@gmail.com","email_2@gmail.com"

# Installing Python Dependencies
COPY requirements.txt /cloud_support/src
RUN pip install --no-cache-dir -r requirements.txt

# Copying src code to Container
COPY organization.py service_account.json /cloud_support/src/

# Run the program
ENTRYPOINT [ "python", "organization.py"]