$ErrorActionPreference = 'Stop'

if (-not $env:AI_SEARCH_ENDPOINT -or -not $env:AI_SEARCH_INDEX_NAME) {
    throw 'AI_SEARCH_ENDPOINT and AI_SEARCH_INDEX_NAME are required.'
}

$apiVersion = '2024-07-01'
$indexUrl = "$($env:AI_SEARCH_ENDPOINT)/indexes/$($env:AI_SEARCH_INDEX_NAME)?api-version=$apiVersion"
$docsUrl = "$($env:AI_SEARCH_ENDPOINT)/indexes/$($env:AI_SEARCH_INDEX_NAME)/docs/index?api-version=$apiVersion"

for ($attempt = 1; $attempt -le 6; $attempt++) {
    az rest --method put --url $indexUrl --resource 'https://search.azure.com' `
        --headers 'Content-Type=application/json' --body '@infra/search-index.json' --output none
    if ($LASTEXITCODE -eq 0) { break }
    if ($attempt -eq 6) { throw 'Unable to create the AI Search index after RBAC propagation.' }
    Start-Sleep -Seconds (10 * $attempt)
}

az rest --method post --url $docsUrl --resource 'https://search.azure.com' `
    --headers 'Content-Type=application/json' --body '@infra/search-documents.json' --output none
if ($LASTEXITCODE -ne 0) { throw 'Unable to seed the AI Search index.' }

Write-Host "Seeded $($env:AI_SEARCH_INDEX_NAME) at $($env:AI_SEARCH_ENDPOINT)."
