# Use dbaseimage for runnning this application
FROM dwxalphateam/mendelframework:dbaseimage

# Set working dir to '/'
WORKDIR /

# Add all the scrips needed (all) for the aplication to run OK
ADD . /

# Install dependecies for this specific component (if it is python)
RUN pip install -r requirements.txt

# Expose TZ env:
# Docker timestamp is in UTC
ENV TZ=Europe/Madrid

# Start running the python application
CMD ["./docker-entrypoint.sh"]