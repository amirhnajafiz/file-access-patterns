#!/usr/bin/env sh

# ./cleanup.sh
# removing the docker containers/images

set -e

# remove any existing docker container with the image name file-access-patterns:test
docker rm -f $(docker ps -a --filter "ancestor=file-access-patterns:test" --format "{{.ID}}") || true

# remove the docker image file-access-patterns:test
docker rmi -f file-access-patterns:test || true

echo "Cleanup over."
