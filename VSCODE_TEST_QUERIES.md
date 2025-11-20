# VS Code Test Queries

**Repository:** microsoft/vscode  
**Generated:** November 20, 2025  
**Test Cases:** 15  
**Commits Analyzed:** 50  

---

## Test Case 1: eligibleForAutoApproval support
**Query:** `eligibleForAutoApproval support for legacyToolReferenceFullNames`  
**Commit:** dc7a73af  
**Complexity:** Medium  
**Files:** 2

**Expected Files:**
1. `src/vs/workbench/contrib/chat/browser/languageModelToolsService.ts`
2. `src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts`

---

## Test Case 2: Agent Session Locking
**Query:** `Support locking agent session option item`  
**Commit:** 3bec25a5  
**Complexity:** Medium  
**Files:** 7

**Expected Files:**
1. `src/vs/workbench/api/browser/mainThreadChatSessions.ts`
2. `src/vs/workbench/api/common/extHost.protocol.ts`
3. `src/vs/workbench/contrib/chat/browser/chatInputPart.ts`
4. `src/vs/workbench/contrib/chat/browser/chatSessions.contribution.ts`
5. `src/vs/workbench/contrib/chat/browser/chatSessions/chatSessionPickerActionItem.ts`
6. `src/vs/workbench/contrib/chat/common/chatSessionsService.ts`
7. `src/vscode-dts/vscode.proposed.chatSessionsProvider.d.ts`

---

## Test Case 3: Mock Filesystem Simplification
**Query:** `Simplify mock filesystem setup`  
**Commit:** 1036deed  
**Complexity:** Medium  
**Files:** 3

**Expected Files:**
1. `src/vs/workbench/contrib/chat/test/common/promptSyntax/service/promptsService.test.ts`
2. `src/vs/workbench/contrib/chat/test/common/promptSyntax/testUtils/mockFilesystem.test.ts`
3. `src/vs/workbench/contrib/chat/test/common/promptSyntax/testUtils/mockFilesystem.ts`

---

## Test Case 4: Chat Timing Information
**Query:** `chat add additional timing information on the model`  
**Commit:** 39b5dc34  
**Complexity:** Medium  
**Files:** 8

**Expected Files:**
1. `src/vs/base/common/types.ts`
2. `src/vs/workbench/contrib/chat/common/chatModel.ts`
3. `src/vs/workbench/contrib/chat/test/common/__snapshots__/ChatService_can_deserialize.0.snap`
4. `src/vs/workbench/contrib/chat/test/common/__snapshots__/ChatService_can_deserialize_with_response.0.snap`
5. `src/vs/workbench/contrib/chat/test/common/__snapshots__/ChatService_can_serialize.1.snap`
6. `src/vs/workbench/contrib/chat/test/common/__snapshots__/ChatService_sendRequest_fails.0.snap`
7. `src/vs/workbench/contrib/chat/test/common/chatModel.test.ts`
8. `src/vs/workbench/contrib/chat/test/common/chatService.test.ts`

---

## Test Case 5: Skills Support
**Query:** `support skills`  
**Commit:** a3668d6b  
**Complexity:** Medium  
**Files:** 8

**Expected Files:**
1. `src/vs/workbench/contrib/chat/browser/chat.contribution.ts`
2. `src/vs/workbench/contrib/chat/common/promptSyntax/computeAutomaticInstructions.ts`
3. `src/vs/workbench/contrib/chat/common/promptSyntax/config/config.ts`
4. `src/vs/workbench/contrib/chat/common/promptSyntax/service/promptsService.ts`
5. `src/vs/workbench/contrib/chat/common/promptSyntax/service/promptsServiceImpl.ts`
6. `src/vs/workbench/contrib/chat/common/promptSyntax/utils/promptFilesLocator.ts`
7. `src/vs/workbench/contrib/chat/test/common/mockPromptsService.ts`
8. `src/vs/workbench/contrib/chat/test/common/promptSyntax/service/promptsService.test.ts`

---

## Test Case 6: TextEdit Composition
**Query:** `Implements TextEdit.compose`  
**Commit:** f0e31b98  
**Complexity:** Medium  
**Files:** 3

**Expected Files:**
1. `src/vs/editor/common/core/edits/textEdit.ts`
2. `src/vs/editor/test/common/core/stringEdit.test.ts`
3. `src/vs/editor/test/common/core/textEdit.test.ts`

---

## Test Case 7: Git Migrate Changes
**Query:** `Git - refactor migrate changes functionality`  
**Commit:** 7c999f6f  
**Complexity:** Medium  
**Files:** 4

**Expected Files:**
1. `extensions/git/src/api/api1.ts`
2. `extensions/git/src/api/git.d.ts`
3. `extensions/git/src/commands.ts`
4. `extensions/git/src/repository.ts`

---

## Test Case 8: MCP Tool Titles
**Query:** `make MCP titles look more like regular tool titles`  
**Commit:** 24f30d9d  
**Complexity:** Medium  
**Files:** 2

**Expected Files:**
1. `src/vs/workbench/contrib/chat/browser/chatContentParts/chatToolInputOutputContentPart.ts`
2. `src/vs/workbench/contrib/chat/browser/chatContentParts/media/chatConfirmationWidget.css`

---

## Test Case 9: Delete Resource Constant
**Query:** `Delete CHAT_WIDGET_VIEW_RESOURCE`  
**Commit:** 3efda633  
**Complexity:** Medium  
**Files:** 4

**Expected Files:**
1. `src/vs/workbench/contrib/chat/browser/chatSessions/localChatSessionsProvider.ts`
2. `src/vs/workbench/contrib/chat/browser/chatSessions/view/sessionsViewPane.ts`
3. `src/vs/workbench/contrib/chat/browser/chatWidgetService.ts`
4. `src/vs/workbench/contrib/chat/common/chatServiceImpl.ts`

---

## Test Case 10: Prompt File Names with Spaces
**Query:** `prompt files allow names to contain spaces`  
**Commit:** 5dbc14ff  
**Complexity:** Medium  
**Files:** 4

**Expected Files:**
1. `src/vs/workbench/contrib/chat/common/promptSyntax/languageProviders/promptValidator.ts`
2. `src/vs/workbench/contrib/chat/common/promptSyntax/promptFileParser.ts`
3. `src/vs/workbench/contrib/chat/common/promptSyntax/service/promptsServiceImpl.ts`
4. `src/vs/workbench/contrib/chat/test/browser/promptSytntax/promptValidator.test.ts`

---

## Test Case 11: Remove Chat Summary
**Query:** `remove chat summary`  
**Commit:** 0f481e07  
**Complexity:** Medium  
**Files:** 7

**Expected Files:**
1. `src/vs/workbench/api/browser/mainThreadChatAgents2.ts`
2. `src/vs/workbench/api/common/extHost.protocol.ts`
3. `src/vs/workbench/api/common/extHostChatAgents2.ts`
4. `src/vs/workbench/contrib/chat/common/chatAgents.ts`
5. `src/vs/workbench/contrib/chat/common/chatService.ts`
6. `src/vs/workbench/contrib/chat/common/chatServiceImpl.ts`
7. `src/vscode-dts/vscode.proposed.chatSessionsProvider.d.ts`

---

## Test Case 12: Chat Models Fix
**Query:** `fix`  
**Commit:** 24e43a08  
**Complexity:** Medium  
**Files:** 3

**Expected Files:**
1. `src/vs/workbench/contrib/chat/browser/chatManagement/chatModelsViewModel.ts`
2. `src/vs/workbench/contrib/chat/browser/chatManagement/chatModelsWidget.ts`
3. `src/vs/workbench/contrib/chat/test/browser/chatModelsViewModel.test.ts`

---

## Test Case 13: PII Redaction Tests
**Query:** `Add tests fix PII redaction`  
**Commit:** e493c80a  
**Complexity:** Medium  
**Files:** 2

**Expected Files:**
1. `src/vs/platform/telemetry/common/telemetryService.ts`
2. `src/vs/platform/telemetry/test/browser/telemetryService.test.ts`

---

## Test Case 14: Hide Agent Sessions Button
**Query:** `agent sessions - allow to hide button to aid selfhost in single view`  
**Commit:** d865a421  
**Complexity:** Medium  
**Files:** 2

**Expected Files:**
1. `src/vs/workbench/contrib/chat/browser/agentSessions/agentSessionsView.ts`
2. `src/vs/workbench/contrib/chat/browser/chat.contribution.ts`

---

## Test Case 15: Agent Sessions Icon
**Query:** `agent sessions - adopt new icon to forward`  
**Commit:** 614b50dc  
**Complexity:** Medium  
**Files:** 2

**Expected Files:**
1. `src/vs/workbench/contrib/chat/browser/actions/chatContinueInAction.ts`
2. `src/vs/workbench/contrib/chat/browser/agentSessions/agentSessionViewModel.ts`

---

## Query Characteristics

### By Feature Area:
- **Chat/AI Features:** 11 queries (73%)
- **Editor Core:** 1 query (7%)
- **Git Extension:** 1 query (7%)
- **Telemetry:** 1 query (7%)
- **Testing Infrastructure:** 1 query (7%)

### By File Count:
- **2 files:** 5 queries (33%)
- **3 files:** 3 queries (20%)
- **4 files:** 4 queries (27%)
- **7-8 files:** 3 queries (20%)

### Query Quality:
- **Specific:** 10 queries (67%) - Clear feature/component names
- **Vague:** 1 query (7%) - "fix"
- **Action-based:** 4 queries (27%) - "add", "delete", "refactor"

---

## Notes

**Strengths of this dataset:**
- Real software features (not config/infrastructure)
- TypeScript codebase (modern, well-structured)
- Mix of UI, core editor, and extension work
- Clear component boundaries
- Well-organized file structure

**Challenges:**
- Heavy focus on chat features (may bias results)
- Deep nested paths (long file names)
- Many files in similar directories
- Some vague commit messages ("fix")

**Comparison to Django:**
- More focused feature areas (chat vs broad framework)
- Clearer file organization (src/vs/workbench structure)
- Fewer documentation files
- More test files included
