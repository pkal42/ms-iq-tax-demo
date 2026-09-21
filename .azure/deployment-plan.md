# Meridian IQ Demo Deployment Plan

> **Status:** Deployed (South Central US)

Generated: 2026-09-16

## 1. Project Overview

**Goal:** Build a polished Python sales demo for Meridian Tax Advisors that combines Work IQ, Fabric IQ, Foundry IQ, and Web IQ in both a prompt-agent pattern and a Microsoft Agent Framework multi-agent pattern.

**Path:** New Project

The user explicitly requested autonomous end-to-end execution, which is treated as approval of this plan and its cost-optimized demo architecture.

## 2. Requirements

| Attribute | Value |
|-----------|-------|
| Classification | POC / sales solution demo |
| Scale | Small, single-region |
| Budget | Cost-optimized with scale-to-zero hosting |
| Subscription | Selected by the operator through `azd env` at deployment time |
| Location | Selected by the operator through `azd env`; must support the chosen model and Foundry Agent Service |
| Compliance | Synthetic client data only; no production tax or M365 data |

Azure subscription policy and live quota checks are deployment-time gates because this task prepares IaC but does not deploy resources. The operator must confirm the subscription and location before `azd up`.

## 3. Components Detected

The workspace initially contained only a placeholder README, so this is a greenfield implementation.

| Component | Type | Technology | Path |
|-----------|------|------------|------|
| Demo CLI/API | API and interactive CLI | Python | `src/meridian_iq/` |
| IQ connectors | Data/grounding adapters | Python | `src/meridian_iq/connectors/` |
| Prompt agent | Foundry prompt agent | `azure-ai-projects`, `azure-ai-agents` | `src/meridian_iq/patterns/prompt_agent.py` |
| Multi-agent workflow | Hosted-agent orchestration | Microsoft Agent Framework | `src/meridian_iq/patterns/multi_agent.py` |
| Infrastructure | Azure resources | Bicep + azd | `infra/`, `azure.yaml` |

## 4. Recipe Selection

**Selected:** AZD with Bicep

**Rationale:** The user requested Bicep + azd, a clean-subscription experience, and a single `azd up` path. Container Apps provides a simple Docker deployment and scale-to-zero for a demo workload.

## 5. Architecture

**Stack:** Container Apps

| Component | Azure Service | SKU |
|-----------|---------------|-----|
| Demo API/UI | Azure Container Apps | Consumption |
| Container images | Azure Container Registry | Basic |
| Prompt and hosted agents | Microsoft Foundry account + project | Basic agent setup |
| Chat model | Foundry model deployment | `gpt-5-mini`, GlobalStandard |
| Foundry IQ index | Azure AI Search | Basic |
| Web IQ | Grounding with Bing Search connection | S1 resource where available |
| Seed and app storage | Storage account | Standard LRS |
| Secrets | Key Vault | Standard |
| Telemetry | Log Analytics + Application Insights | Consumption |
| Identity | System-assigned managed identities | Least-privilege RBAC |

Work IQ and Fabric IQ run against realistic local adapters by default. Their real backends are explicit swap points for Microsoft Graph/Copilot retrieval and a Fabric SQL/Lakehouse endpoint. Foundry IQ uses mock curated documents locally and an Azure AI Search project connection live. Web IQ uses mock current-year facts locally and Bing Grounding live.

## 6. Provisioning Limit Checklist

Live usage and quota cannot be calculated without a target subscription and region. The deployment is intentionally not executed in this task. Before deployment, `azure-quotas` must validate every resource below against the selected subscription and location.

| Resource Type | Number to Deploy | Deployment Gate |
|---------------|------------------|-----------------|
| `Microsoft.CognitiveServices/accounts` | 1 | Confirm Foundry and model availability |
| `Microsoft.CognitiveServices/accounts/projects` | 1 | Confirm provider registration |
| `Microsoft.CognitiveServices/accounts/deployments` | 1 | Confirm model quota and capacity |
| `Microsoft.Search/searchServices` | 1 | Confirm regional availability |
| `Microsoft.Bing/accounts` | 1 | Confirm subscription eligibility |
| `Microsoft.Storage/storageAccounts` | 1 | Confirm account quota |
| `Microsoft.KeyVault/vaults` | 1 | Confirm vault quota |
| `Microsoft.ContainerRegistry/registries` | 1 | Confirm registry quota |
| `Microsoft.App/managedEnvironments` | 1 | Confirm environment quota |
| `Microsoft.App/containerApps` | 1 | Confirm Container Apps quota |
| `Microsoft.OperationalInsights/workspaces` | 1 | Confirm workspace quota |
| `Microsoft.Insights/components` | 1 | Confirm Application Insights availability |

**Status:** Deployment-time validation required; no Azure deployment is attempted by this preparation task.

## 7. Execution Checklist

### Phase 1: Planning

- [x] Analyze workspace
- [x] Gather requirements from the detailed user scenario
- [x] Prepare resource inventory
- [x] Scan codebase
- [x] Select recipe
- [x] Plan architecture
- [x] User requested autonomous execution

### Phase 2: Execution

- [x] Research current Foundry agent, Azure AI Search, Bing Grounding, and Agent Framework APIs
- [x] Generate application and connector code
- [x] Generate infrastructure and deployment configuration
- [x] Apply managed identity and RBAC hardening
- [x] Add tests and documentation
- [x] Update status to `Ready for Validation`

### Phase 3: Validation

- [x] Invoke azure-validate
- [x] All validation checks pass
  - [x] 1. AZD Installation
  - [x] 2. Schema Validation
  - [x] 3. Environment Setup
  - [x] 4. Authentication Check
  - [x] 5. Subscription/Location Check
  - [x] 6. Aspire Pre-Provisioning Checks (not an Aspire project)
  - [x] 7. Provision Preview
  - [x] 8. Build Verification
  - [x] 9. Docker Build Context Validation
  - [x] 10. Package Validation
  - [x] 11. Azure Policy Validation
  - [x] 12. Aspire Post-Provisioning Checks (not an Aspire project)

## 8. Validation Proof

| Check | Command Run | Result | Timestamp |
|-------|-------------|--------|-----------|
| Connector and orchestration tests | `python -m pytest` | Pass: 10 tests | 2026-09-16 |
| Python compilation | `python -m compileall -q src scripts` | Pass | 2026-09-16 |
| Prompt CLI smoke test | `meridian-iq prompt --json` | Pass | 2026-09-16 |
| Multi-agent CLI smoke test | `meridian-iq multi --json` | Pass | 2026-09-16 |
| Live SDK tool construction | Construct four `azure.ai.projects.models` IQ tools | Pass | 2026-09-16 |
| Bicep compilation | `az bicep build --file infra\main.bicep --stdout` | Pass with expected untyped Microsoft.Bing warning | 2026-09-16 |
| azd schema/environment/auth | `azd version`, `azd auth login --check-status`, `azd env get-values` | Pass | 2026-09-16 |
| Subscription policy | `az policy assignment list` | Pass; three unrelated Defender policies | 2026-09-16 |
| Provisioning preview | `azd provision --preview --no-prompt` | Pass; 14 resources planned in East US 2 | 2026-09-16 |
| Package | `azd package --no-prompt` | Pass | 2026-09-16 |
| Packaged container | Run packaged image and query `/health` and `/api/demo/prompt` | Pass; healthy with 10 grounded facts | 2026-09-16 |
| West US 3 authentication and environment | `azd auth login --check-status`, `azd env get-values` | Pass; `meridian-iq-w3a7` targets subscription `8b3364c6-4c9d-4819-9cde-a2c7984be725` and `westus3` | 2026-09-21 |
| West US 3 provider registration | `az provider show/register` | Pass; Cognitive Services, Search, App, Container Registry, Key Vault, Operational Insights, Bing, and Storage registered | 2026-09-21 |
| West US 3 model, quota, and service availability | `az cognitiveservices model list/usage`, provider location queries | Pass; `gpt-5-mini` `2025-08-07`, AI Search, and Container Apps available in West US 3 | 2026-09-21 |
| West US 3 policy review | `az policy assignment list` | Pass; three unrelated Defender initiatives do not restrict this architecture | 2026-09-21 |
| West US 3 Bicep build and app tests | `az bicep build`, `python -m pytest`, `python -m compileall` | Pass; Bicep has the expected untyped Microsoft.Bing warning and 10 tests pass | 2026-09-21 |
| West US 3 provisioning preview | `azd provision --preview --no-prompt` | Pass; 14 resources planned after correcting Container App name normalization | 2026-09-21 |
| West US 3 package | `azd package --no-prompt` | Pass; `web-meridian-iq-w3a7` container image built | 2026-09-21 |
| West US 3 provisioning | `azd provision --no-prompt` | Blocked: Azure AI Search Basic SKU capacity unavailable in West US 3 (`ResourcesForSkuUnavailable`); no app or endpoint was created | 2026-09-21 |
| East US 2 provisioning (retry 1, `meridian-iq-e2c4`) | `azd provision --no-prompt` (3 attempts, Basic then Standard Search SKU) | Blocked: Azure AI Search capacity unavailable in East US 2 for both Basic and Standard SKU (`InsufficientResourcesAvailable`) | 2026-09-21 |
| East US provisioning (retry 2, `meridian-iq-eus5`) | `azd provision --no-prompt` | Blocked: Search succeeded, but Container Apps Environment failed with `AKSCapacityHeavyUsage` (AKS capacity exhaustion, not a template defect); failed CAE deleted and retried once, same result | 2026-09-21 |
| Central US provisioning (retry 3, `meridian-iq-cus6`) | `azd provision --no-prompt` | Blocked: Search succeeded, Container Apps Environment failed again with `AKSCapacityHeavyUsage`; failed CAE deleted | 2026-09-21 |
| Regional ACA capacity probe | `az containerapp env create` against South Central US, West US, Sweden Central, France Central, East US 2 | South Central US confirmed capacity first; probe stopped there to save time | 2026-09-21 |
| South Central US provisioning (`meridian-iq-scus7`) | `azd provision --no-prompt` (2 attempts) | Pass after fixing two real template defects (see below); 13 of 14 resources created; Bing Grounding account creation deliberately disabled | 2026-09-21 |
| South Central US deploy | `azd deploy --no-prompt` (2 attempts) | Pass after adding a `registries` block to the Container App so its managed identity is used for ACR pulls; first attempt failed `UNAUTHORIZED` despite AcrPull role existing | 2026-09-21 |
| App health check | `GET /health`, `GET /` on the live HTTPS endpoint | Pass; `{"status":"healthy","mode":"mock"}` and full UI served | 2026-09-21 |
| Search index seeding | `$count` query against `meridian-tax-knowledge` index | Pass; 3 documents seeded by the `postprovision` hook | 2026-09-21 |
| Live RBAC verification (South Central US) | `az role assignment list` against ACR, Key Vault, Storage, Search, Foundry project | Pass; all 6 expected role assignments present for the Container App and Foundry project managed identities | 2026-09-21 |

### Template defects discovered and fixed during this deployment

1. **Container App name double-hyphen** — `prefix` did not strip hyphens from `environmentName` before truncating, producing invalid names like `miq-meridian-iq--web`. Fixed in `infra/resources.bicep`.
2. **Azure AI Search `authOptions` conflict** — `authOptions.aadOrApiKey` cannot coexist with `disableLocalAuth: true`; ARM rejected it as `AuthOptions must be null if DisableLocalAuth is true`. Removed the block; Entra-only access remains via `disableLocalAuth: true`.
3. **Missing Container App `registries` block** — the Container App had no `configuration.registries` entry telling the platform to use its managed identity for ACR pulls. `azd deploy` pushed an image the platform could not pull (`UNAUTHORIZED`) even though the `AcrPull` role assignment existed and had propagated. Fixed by adding `registries: [{ server: registry.properties.loginServer, identity: 'system' }]`.
4. **Bing Grounding (`Microsoft.Bing/accounts`, kind `Bing.Grounding`) resource creation** — confirmed via direct `az resource create` and multiple public reports (Azure CLI GitHub #30029, Microsoft Q&A 5940309) to be a **Microsoft-side backend outage** unrelated to this subscription's configuration, quota, or the Bicep template. Not fixable by retrying. Made conditional via a new `deployBingGrounding` parameter (default `true`) so the rest of the stack can deploy; disabled for this deployment via `DEPLOY_BING_GROUNDING=false`. Web IQ runs in mock mode until Microsoft resolves the issue; re-enable by setting `azd env set DEPLOY_BING_GROUNDING true` and re-running `azd provision` once the backend is fixed.

### Regional capacity summary (informational, not a template issue)

Multiple regions in this subscription showed transient or sustained Azure-side capacity exhaustion during this deployment window: West US 3 and East US 2 (Azure AI Search Basic/Standard SKU), East US and Central US (AKS capacity backing Container Apps Environments). West US 2 was ruled out for a different reason — it offers no OpenAI GPT model family (`gpt-4o`/`gpt-5-mini`) in this subscription's model catalog at all. South Central US was the first region confirmed to have capacity across all required services.

## Role Assignment Verification

- **Status:** Verified
- **Identities checked:** Foundry project managed identity, Container App system identity, local deployer
- **Roles confirmed:** Search Index Data Contributor, Search Service Contributor, Storage Blob Data Contributor, Key Vault Secrets User, AcrPull, Foundry User
- **Scope:** Every role is scoped to the specific Search, Storage, Key Vault, Registry, or Foundry project resource.
- **Issues fixed:** Added Foundry User for the Container App identity so Azure mode can invoke persisted agents.

## 9. Files to Generate

| File | Purpose | Status |
|------|---------|--------|
| `.azure/deployment-plan.md` | Deployment source of truth | Complete |
| `pyproject.toml` | Python package and dependencies | Complete |
| `.env.sample` | Environment contract | Complete |
| `src/meridian_iq/` | Application implementation | Complete |
| `tests/` | Unit and orchestration tests | Complete |
| `Dockerfile` | Container build | Complete |
| `azure.yaml` | azd configuration | Complete |
| `infra/main.bicep` | Subscription deployment entry point | Complete |
| `infra/resources.bicep` | Resource group infrastructure | Complete |
| `README.md` | Setup, architecture, and presentation guide | Complete |

## 10. Next Steps

1. Implement the mock-first demo and Azure adapters.
2. Generate and validate the Bicep/azd deployment path.
3. Run local validation, commit incrementally, and open a pull request.
4. **Deployed:** live in South Central US (`meridian-iq-scus7`, `rg-meridian-iq-scus7`). See README for the live endpoint and Work IQ tenant-setup checklist.
5. Re-enable Bing Grounding (`DEPLOY_BING_GROUNDING=true`) once Microsoft resolves the `Microsoft.Bing/accounts` provisioning outage, then re-run `azd provision`.
6. Decide the fate of the partial resource groups left behind by blocked regional attempts (`rg-meridian-iq-w3a7`, `rg-meridian-iq-e2c4`, `rg-meridian-iq-eus5`, `rg-meridian-iq-cus6`) — none were deleted without explicit confirmation.
