# Use python 3.7 for runnning this application
FROM dwxalphateam/charlesframework:dbaseimage

# Set working dir to 'D_Strategy1'
WORKDIR /D_Strategy1

# Add all the scrips needed (all) for the aplication to run OK
ADD . /D_Strategy1

# Install dependecies for this specific component (if it is python)
RUN pip install -r requirements.txt

# Expose TZ env:
# Docker timestamp is in UTC
ENV TZ=Europe/Madrid

# Start running the python application
CMD ["./docker-entrypoint.sh"]