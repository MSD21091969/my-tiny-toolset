# Tool Engineering Workflow - AI + Human Collaboration

**Last Updated:** 2025-10-16  
**Purpose:** Structured Q&A workflow for designing, implementing, testing, and documenting new tools in my-tiny-data-collider

---

## Workflow Overview

**Pattern:** Human initiates → AI asks clarifying questions → Design → Implement → Test → Document

**Equipment Available:**
- **Application Code:** `my-tiny-data-collider/` (34 methods, 37 models, validation framework)
- **Analysis Tools:** `my-tiny-toolset/TOOLSET/` (17 meta-tools for code analysis)
- **Knowledge Base:** `my-tiny-toolset/REFERENCE/` (patterns, architecture, specifications)
- **Prompts Library:** `my-tiny-toolset/PROMPTS/` (prompt engineering patterns)
- **Schemas:** `my-tiny-toolset/SCHEMAS/` (JSON/YAML validation schemas)
- **Templates:** `my-tiny-toolset/TEMPLATES/` (project templates, integration patterns)
- **Examples:** `my-tiny-toolset/EXAMPLES/` (public API patterns)

---

## Phase 1: Discovery & Requirements (AI Questions)

### When Human Says: "I want to build a tool to [goal]..."

**AI Asks:**

#### 1. Domain & Capability Classification
- **Question:** "What domain does this tool belong to? (workspace, communication, data-processing, integration, automation)"
- **Follow-up:** "What's the primary capability? (create, read, update, delete, transform, extract, sync)"
- **Why:** Determines service location and method registration pattern

#### 2. Data Flow & Dependencies
- **Question:** "What's the input data source and format?"
  - Example answers: "Gmail message ID", "Casefile ID + filters", "Google Drive file URL"
- **Question:** "What's the output destination and format?"
  - Example answers: "Store in casefile as attachment metadata", "Update Drive file properties", "Create new Sheets row"
- **Question:** "Does this depend on existing methods/models?"
  - **AI Action:** Run `python $env:MY_TOOLSET\analysis-tools\method_search.py "[keyword]"` to find related methods
  - **AI Action:** Check `my-tiny-data-collider/config/methods_inventory_v1.yaml` for existing capabilities

#### 3. Validation Requirements
- **Question:** "What fields need validation? What are the constraints?"
  - Example: "Gmail message ID (min 10 chars), file size limit (max 50MB), timestamp ordering"
- **AI Action:** Check `my-tiny-data-collider/docs/VALIDATION_PATTERNS.md` for existing types
- **AI Action:** List relevant custom types from `src/pydantic_models/base/custom_types.py`

#### 4. Error Handling & Edge Cases
- **Question:** "What happens if the Gmail message doesn't exist? If Drive quota is exceeded?"
- **Question:** "Should this be idempotent? (Safe to retry on failure)"
- **Question:** "What's the timeout/rate limit strategy?"

#### 5. Testing Strategy
- **Question:** "What test scenarios are critical?"
  - Example: "Happy path, missing message, no attachments, oversized file, permission denied"
- **Question:** "Do you need mock data or live API testing?"

#### 6. Documentation Requirements
- **Question:** "Who's the primary user? (developer, AI agent, end-user via UI)"
- **Question:** "What examples would clarify usage?"

---

## Phase 2: Design (AI Proposes Architecture)

### AI Output Template:

```markdown
## Tool Design: [Tool Name]

### Classification
- **Domain:** workspace | communication | data-processing | integration
- **Capability:** create | read | update | delete | transform | extract | sync
- **Service:** CasefileService | CommunicationService | [New]Service
- **Method Name:** `extract_gmail_attachments_to_drive`

### Request Model
**File:** `src/pydantic_models/operations/gmail_attachment_extract.py`

```python
from pydantic import BaseModel
from src.pydantic_models.base.custom_types import (
    CasefileId, GmailMessageId, ResourceId
)

class ExtractGmailAttachmentsRequest(BaseModel):
    casefile_id: CasefileId
    message_id: GmailMessageId
    drive_folder_id: ResourceId  # Optional, defaults to casefile folder
    max_size_mb: int = 50  # Max attachment size
```

### Response Model
```python
class ExtractGmailAttachmentsResponse(BaseModel):
    casefile_id: CasefileId
    extracted_count: int
    attachments: list[AttachmentMetadata]
    skipped: list[dict]  # Files skipped due to size/type
```

### Implementation Plan
1. **Existing Methods to Reuse:**
   - `gmail_client.get_message_details(message_id)` → Extract attachments list
   - `drive_client.upload_file(file_data, folder_id)` → Upload to Drive
   - `casefile_service.add_attachment_metadata()` → Update casefile

2. **New Logic Needed:**
   - Attachment filtering (size, mime type)
   - Drive folder creation (if not exists)
   - Metadata mapping (Gmail → Drive → Casefile)

3. **Validation:**
   - Use `GmailMessageId` (≥10 chars)
   - Use `ResourceId` for Drive folder
   - Use `validate_range()` for file size check

4. **Error Handling:**
   - Gmail API: MessageNotFound → 404 response
   - Drive API: QuotaExceeded → 507 response
   - Partial success: Return extracted + skipped lists

### Test Plan
**File:** `tests/integration/test_gmail_attachment_extraction.py`

- Test 1: Happy path (2 attachments, both under limit)
- Test 2: Size filter (1 under, 1 over limit)
- Test 3: No attachments (empty list response)
- Test 4: Invalid message ID (404 error)
- Test 5: Drive permission denied (403 error)

### Tool YAML Registration
**File:** `config/methodtools_v1/CommunicationService_extract_gmail_attachments_tool.yaml`

```yaml
name: extract_gmail_attachments_tool
method_name: extract_gmail_attachments_to_drive
service_name: CommunicationService
description: Extract attachments from Gmail message and store in Google Drive
classification:
  domain: communication
  capability: extract
parameters:
  casefile_id:
    type: string
    required: true
  message_id:
    type: string
    required: true
  drive_folder_id:
    type: string
    required: false
  max_size_mb:
    type: integer
    required: false
    default: 50
```

### Documentation Checklist
- [ ] Update `config/methods_inventory_v1.yaml` (via decorator auto-registration)
- [ ] Add example to `docs/VALIDATION_PATTERNS.md` (if new types added)
- [ ] Update `ROUNDTRIP_ANALYSIS.md` (new method count)
- [ ] Capture pattern in `my-tiny-toolset/WORKSPACE/FIELDNOTES.md`
```

**AI Then Asks:** "Does this design match your requirements? Any changes needed?"

---

## Phase 3: Implementation (AI + Human Collaboration)

### AI Actions (Sequential):

1. **Create Request/Response Models**
   - File: `src/pydantic_models/operations/gmail_attachment_extract.py`
   - Use existing custom types from `base/custom_types.py`
   - Add validators from `base/validators.py` if cross-field validation needed

2. **Implement Service Method**
   - File: `src/communicationservice/gmail_attachment_service.py` (or existing service file)
   - Add `@register_service_method` decorator
   - Implement method logic, reusing existing clients

3. **Create Test File**
   - File: `tests/integration/test_gmail_attachment_extraction.py`
   - Use fixtures from `tests/fixtures/` for mock data
   - Cover happy path + error cases

4. **Generate Tool YAML**
   - Run: `python scripts/generate_method_tools.py --dry-run`
   - Verify tool YAML generation
   - Run: `python scripts/generate_method_tools.py` (actually generate)

5. **Validate Implementation**
   - Run: `python scripts/validate_registries.py --strict`
   - Run: `python -m pytest tests/integration/test_gmail_attachment_extraction.py -v`
   - Fix any issues discovered

### Human Reviews:
- Code implementation
- Test coverage
- YAML correctness

---

## Phase 4: Testing & Validation

### AI Runs Analysis Tools:

```bash
# Set environment
$env:MY_TOOLSET = "C:\Users\HP\my-tiny-toolset\TOOLSET"

# Quick structure check
python $env:MY_TOOLSET\analysis-tools\code_analyzer.py c:\Users\HP\my-tiny-data-collider --json

# Validate registries
cd c:\Users\HP\my-tiny-data-collider
python scripts\validate_registries.py --strict --verbose

# Run specific tests
python -m pytest tests/integration/test_gmail_attachment_extraction.py -v

# Run full test suite
python -m pytest tests/ -v --ignore=tests/integration/test_tool_execution_modes.py --ignore=tests/integration/test_tool_method_integration.py

# Check for regressions
python scripts\validate_parameter_mappings.py --verbose
```

### Success Criteria:
- ✅ All new tests passing
- ✅ No regression in existing tests (236/236 Pydantic tests still pass)
- ✅ Registry validation clean
- ✅ Tool YAML generates correctly
- ✅ Parameter mapping validated

---

## Phase 5: Documentation

### AI Updates Documentation:

1. **Application Repo (my-tiny-data-collider):**
   - `ROUNDTRIP_ANALYSIS.md` → Update method count, test count
   - `config/methods_inventory_v1.yaml` → Auto-updated by decorator
   - `docs/VALIDATION_PATTERNS.md` → Add example if new types used

2. **Toolset Repo (my-tiny-toolset):**
   - `WORKSPACE/FIELDNOTES.md` → Capture pattern/insight from implementation
   - Example: "Gmail attachment extraction pattern: metadata mapping Gmail→Drive→Casefile"

3. **If New Pattern Discovered:**
   - Document in `WORKSPACE/FIELDNOTES.md` first
   - After validation across 3+ use cases → Move to `REFERENCE/SUBJECTS/[domain]/`
   - Update relevant folder README.md with date stamp

### Human Reviews:
- Documentation accuracy
- Pattern extraction appropriateness

---

## Phase 6: Knowledge Capture (Long-term)

### When Pattern Proven (3+ implementations):

**AI Asks:** "This pattern has been used successfully in [method A], [method B], [method C]. Should we extract to REFERENCE?"

**If Yes:**
1. Create `REFERENCE/SUBJECTS/[domain]/[pattern-name].md`
2. Document pattern with examples from all implementations
3. Update `REFERENCE/SUBJECTS/[domain]/README.md` with index entry + date stamp
4. Cross-reference from `my-tiny-data-collider/docs/README.md`

**Example Patterns Worth Extracting:**
- Gmail→Drive→Casefile metadata flow
- Error handling strategies for Google Workspace APIs
- Attachment size filtering patterns
- Idempotent sync operations

---

## AI Quick Reference Card

### Before Starting Any Tool Design:

```bash
# 1. Check existing methods
python $env:MY_TOOLSET\workflow-tools\method_search.py "[keyword]"

# 2. Review validation framework
cat c:\Users\HP\my-tiny-data-collider\docs\VALIDATION_PATTERNS.md | Select-String -Pattern "[type-name]"

# 3. Check for similar patterns
cat c:\Users\HP\my-tiny-toolset\WORKSPACE\FIELDNOTES.md | Select-String -Pattern "[pattern]"

# 4. Review existing models
cat c:\Users\HP\my-tiny-data-collider\config\models_inventory_v1.yaml | Select-String -Pattern "[domain]"
```

### Key Files to Reference:

| Need | File Location | Purpose |
|------|---------------|---------|
| **Existing methods** | `my-tiny-data-collider/config/methods_inventory_v1.yaml` | 34 registered methods |
| **Validation types** | `my-tiny-data-collider/src/pydantic_models/base/custom_types.py` | 30 custom types |
| **Validators** | `my-tiny-data-collider/src/pydantic_models/base/validators.py` | 12 reusable validators |
| **Test patterns** | `my-tiny-data-collider/tests/fixtures/` | Mock data fixtures |
| **Architecture** | `my-tiny-toolset/REFERENCE/SYSTEM/architecture/` | System design |
| **Patterns** | `my-tiny-toolset/REFERENCE/SUBJECTS/shared-patterns/` | Validated patterns |
| **Field notes** | `my-tiny-toolset/WORKSPACE/FIELDNOTES.md` | Research & discoveries |
| **Prompts** | `my-tiny-toolset/PROMPTS/awesome-prompts/` | Prompt engineering |

### When Stuck:

1. **Can't find existing method?** → Run `code_analyzer.py` to get full structure
2. **Unsure about validation?** → Check `VALIDATION_PATTERNS.md` examples
3. **Need similar implementation?** → Search `WORKSPACE/FIELDNOTES.md` for patterns
4. **Complex workflow?** → Check `REFERENCE/SYSTEM/guides/request-flow.md`

---

## Example Workflow Execution

### Human: "I want to build a tool to extract attachments from Gmail, store in Drive, and link to casefile"

### AI Response:

**Discovery Questions:**

1. **Classification Confirmation:**
   - Domain: communication (Gmail) + workspace (casefile integration)
   - Capability: extract + sync
   - Service: CommunicationService (owns Gmail operations)
   - ✅ Correct?

2. **Data Flow Clarification:**
   - Input: casefile_id + message_id
   - Output: list of Drive file IDs + attachment metadata in casefile
   - ✅ Correct?

3. **Existing Method Check:**
   - Found: `gmail_client.get_message_details()` (can extract attachments)
   - Found: `drive_client.upload_file()` (can upload to Drive)
   - Found: `casefile_service.add_attachment_metadata()` (can link metadata)
   - **Reuse these?** ✅ Yes

4. **Validation Requirements:**
   - casefile_id: Use `CasefileId` (UUID validation) ✅
   - message_id: Use `GmailMessageId` (≥10 chars) ✅
   - File size limit: Need new validator or use `validate_range()`? **Your preference?**

5. **Error Scenarios:**
   - Gmail message not found → Return 404? ✅
   - Attachment too large → Skip + report in response? ✅
   - Drive quota exceeded → Return 507? ✅
   - **Retry logic needed?** Idempotent safe?

6. **Testing:**
   - Happy path: 2 attachments extracted
   - Edge case: No attachments (empty list)
   - Edge case: 1 attachment oversized (skip)
   - Error case: Invalid message_id
   - **Mock Gmail API or need live testing?**

**Next:** Based on your answers, I'll propose full design (models, method signature, test plan, YAML config).

---

## Continuous Improvement

### After Each Tool Implementation:

**AI Asks:** "What went well? What was unexpected? Any pattern to capture?"

**Examples of Valuable Captures:**
- "Gmail API returns base64-encoded attachment data → needs decode before Drive upload"
- "Drive folder creation requires parent casefile folder lookup → add caching"
- "Attachment metadata should include Gmail message_id for traceability"

**These Go To:** `WORKSPACE/FIELDNOTES.md` → Eventually `REFERENCE/SUBJECTS/` when validated

---

## Success Metrics

**Per Tool Implementation:**
- ⏱️ **Time:** Design (30min) + Implementation (2-4h) + Testing (1h) + Documentation (30min)
- ✅ **Quality:** 100% test coverage for new code, no regressions
- 📚 **Knowledge:** Pattern captured in FIELDNOTES, 3+ patterns → REFERENCE

**Continuous:**
- Tool velocity increases as patterns accumulate in REFERENCE
- Question count decreases as AI learns common patterns
- Documentation quality improves with cross-references

---

**Last Updated:** 2025-10-16  
**Status:** Ready for use  
**Next Review:** After 5 tool implementations, evaluate workflow efficiency
