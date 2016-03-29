from boto3 import client
import os

DOCKER_ECR_URL = os.environ.get("DOCKER_ECR_URL")
DOCKER_REPO = os.environ.get("DOCKER_REPO")
CURRENT_BRANCH = os.environ.get("BRANCH")


def tag_to_pull():
    available_branches = [i.get('imageTag', '') for i in ecr_client.list_images(repositoryName=DOCKER_REPO)['imageIds']]
    # image for given branch already exists
    if CURRENT_BRANCH in available_branches:
        return CURRENT_BRANCH
    # it is most likely first build so pull master one
    if 'master' in available_branches:
        return 'master'


def pull():
    tag = tag_to_pull()
    # it is possible that master hasn't been build yet and there's noting to pull
    if tag:
        os.system('docker pull {}/{}:{}'.format(DOCKER_ECR_URL, DOCKER_REPO, tag))


if __name__ == "__main__":
    ecr_client = client('ecr', region_name='us-east-1')
    pull()
