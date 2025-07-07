user_input="${1:-input message}"



export AWS_ACCESS_KEY_ID=$(curl -s -H "Authorization: Bearer $WM_TOKEN" \
  "$BASE_INTERNAL_URL/api/w/$WM_WORKSPACE/variables/get_value/u/jjbonillatroncoso/AWS_ACCESS_KEY_ID" | jq -r .)

export AWS_SECRET_ACCESS_KEY=$(curl -s -H "Authorization: Bearer $WM_TOKEN" \
  "$BASE_INTERNAL_URL/api/w/$WM_WORKSPACE/variables/get_value/u/jjbonillatroncoso/AWS_SECRET_ACCESS_KEY" | jq -r .)

export LANGSMITH_API_KEY=$(curl -s -H "Authorization: Bearer $WM_TOKEN" \
  "$BASE_INTERNAL_URL/api/w/$WM_WORKSPACE/variables/get_value/u/jjbonillatroncoso/LANGSMITH_API_KEY" | jq -r .)

export LANGSMITH_PROJECT=$(curl -s -H "Authorization: Bearer $WM_TOKEN" \
  "$BASE_INTERNAL_URL/api/w/$WM_WORKSPACE/variables/get_value/u/jjbonillatroncoso/LANGSMITH_PROJECT" | jq -r .)


IMAGE="juanjbon/travel-agency:latest"

docker pull $IMAGE

docker run \
  --name "$WM_JOB_ID" \
  -e AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY \
  -e LANGSMITH_TRACING=true \
  -e LANGSMITH_ENDPOINT=https://api.smith.langchain.com \
  -e LANGSMITH_API_KEY \
  -e LANGSMITH_PROJECT \
  -e LANGCHAIN_TRACING_V2=true \
  --entrypoint python \
  "$IMAGE" runner.py "$user_input"

