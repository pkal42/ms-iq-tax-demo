# Meridian IQ Demo Deployment Plan

> **Status:** Validated

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
