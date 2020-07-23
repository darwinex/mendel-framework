# Use python 3.7 for runnning this application
FROM python:3.7

# Set working dir to 'D_Strategy1'
WORKDIR /DBaseImage

# Add all the scrips needed (all) for the aplication to run OK
ADD . /DBaseImage

# Install dependecies for this specific component (if it is python)
RUN pip install -r requirements.txt

# Expose TZ env:
# Docker timestamp is in UTC
ENV TZ=Europe/Madrid