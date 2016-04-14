#!/bin/bash

# --------------------------------------------------------- #
# Naive provisioning and deploy script for AWS.             #
#                                                           #
#  - Uses production-compose.yml to run the www and nginx   #
#    services in an Ec2 instance (hosted data storage       #
#    services are favoured over persistent production DB    #
#    containers)                                            #
#  - Expects a local .env_prod present containing the       #
#    following keys:                                        #
#     - DJANGO_ENV=production                               #
#     - SECRET_KEY={{some new key}}                         #
#     - DB_NAME={{name}}                                    #
#     - DB_USER={{user}}                                    #
#     - DB_PASS={{pass}}                                    #
#     - DB_SERVICE={{RDS endpoint}}                         #
#     - DB_PORT={{port}}                                    #
#     - IMG_BASE_S3_ACCESS_KEY={{access_key}}               #
#     - IMG_BASE_S3_SECRET_KEY={{secret_key}}               #
#     - IMG_BASE_S3_BUCKET={{bucket}}                       #
#     - IMG_BASE_S3_PREFIX={{prefix}}                       #
#     - IMG_BASE_S3_REGION={{region}}                       #
#  - Can just provision the machine and build the app       #
#    - Requires having a precreated VPC                     #
#    - Requires MACHINE, VPC_ID, REGION and ZONE env params #
#  - Can just deploy the app                                #
#    - Requires MACHINE env param                           #
#                                                           #
#  $ chmod +x deploy.sh && sh deploy.sh -p (just provision) #
#  $ chmod +x deploy.sh && sh deploy.sh (just deploy)       #
#                                                           #
# --------------------------------------------------------- #
set -e

[ -z "$NAME" ] && echo "Err: var NAME not set" && exit 1;


while getopts ":p" opt; do
  case $opt in
    p)
      echo "Running provisioning...";
      [ -z "$VPC_ID" ] && echo "Err: var VPC_ID not set" && exit 1;
      [ -z "$ZONE" ] && echo "Err: var ZONE not set" && exit 1;
      [ -z "$REGION" ] && echo "Err: var REGION not set" && exit 1;

      docker-machine -D create -d amazonec2 --amazonec2-vpc-id $VPC_ID \
                                            --amazonec2-zone $ZONE \
                                            --amazonec2-region $REGION \
                                            --amazonec2-instance-type "t2.medium" \
                                            $NAME && \
        eval $(docker-machine env $NAME) && \
        echo "...machine provisioned";

      exit 0
      ;;
    *)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

echo "Running deploy...";
eval $(docker-machine env $NAME) && \
  docker-compose -f production-compose.yml build && \
  docker-compose -f production-compose.yml down && \
  docker-compose -f production-compose.yml up -d --force-recreate && \
  docker-compose -f production-compose.yml run www /usr/local/bin/python manage.py migrate && \
  echo "Deployed to: http://$(docker-machine ip $NAME)";
