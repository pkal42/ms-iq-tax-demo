#!/bin/sh
set -eu

: "${AI_SEARCH_ENDPOINT:?AI_SEARCH_ENDPOINT is required}"
: "${AI_SEARCH_INDEX_NAME:?AI_SEARCH_INDEX_NAME is required}"

api_version="2024-07-01"
index_url="${AI_SEARCH_ENDPOINT}/indexes/${AI_SEARCH_INDEX_NAME}?api-version=${api_version}"
docs_url="${AI_SEARCH_ENDPOINT}/indexes/${AI_SEARCH_INDEX_NAME}/docs/index?api-version=${api_version}"

attempt=1
until az rest --method put --url "$index_url" --resource https://search.azure.com \
  --headers Content-Type=application/json --body @infra/search-index.json --output none; do
  if [ "$attempt" -ge 6 ]; then
    echo "Unable to create the AI Search index after RBAC propagation." >&2
    exit 1
  fi
  sleep $((10 * attempt))
  attempt=$((attempt + 1))
done

az rest --method post --url "$docs_url" --resource https://search.azure.com \
  --headers Content-Type=application/json --body @infra/search-documents.json --output none
echo "Seeded ${AI_SEARCH_INDEX_NAME} at ${AI_SEARCH_ENDPOINT}."
