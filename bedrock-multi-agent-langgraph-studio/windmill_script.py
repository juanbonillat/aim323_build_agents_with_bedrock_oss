user_input="${1:-input message}"


IMAGE="$DOCKER_IMAGE"

docker pull $IMAGE

docker run \
  --name "$WM_JOB_ID" \
  -e AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY \
  --entrypoint python \
  "$IMAGE" runner.py "$user_input"

