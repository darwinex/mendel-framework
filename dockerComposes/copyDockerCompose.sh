### Execute like: bash copyDockerComposeBareMetal.sh 149.81.144.99
### It has to be in the same directory of the docker-compose.yml
### NOTE: WE NEED TO HAVE THE SSH KEY OR IT WILL ASK FOR THE PASSWORD.

# IP ADDRESS FROM PARAMETER
MASTER_IP=$1

# COPYING THE FILES - https://www.computerhope.com/unix/scp.htm
scp -i ~/.ssh/iddarwinex docker-compose.yml root@${MASTER_IP}:
