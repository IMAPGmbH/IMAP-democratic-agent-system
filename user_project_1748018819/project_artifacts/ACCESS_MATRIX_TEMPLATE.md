# Access Matrix Template: Meta-IMAP Landing Page

**Purpose:** To define and manage access permissions for project artifacts and code repositories across different project phases and agent roles. This ensures clarity and organized collaboration.

**Legend:**
*   **C:** Create
*   **R:** Read
*   **U:** Update
*   **D:** Delete
*   **O:** Own (Primary responsibility for maintaining and updating)
*   **N/A:** Not Applicable

## I. Project Management & Planning Artifacts

| Artifact / Directory                                  | PM (Gemini 2.5 Pro) | Researcher (Gemini 1.5 Flash) | Dev Team (Claude, Codestral) | Tester (Mistral M.) | Reflector (Grok) | All Agents (Read-Only) |
| :---------------------------------------------------- | :------------------: | :----------------------------: | :---------------------------: | :-----------------: | :---------------: | :---------------------: |
| `user_project_XXXX/project_artifacts/` (Root)       |         O,CRUD       |              R                 |               R               |          R          |         R         |            R            |
| `.../user_requirements/initial_brief.md`            |         O,R          |              R                 |               R               |          R          |         R         |            R            |
| `.../REQUIREMENTS_ANALYSIS.md`                      |         O,CRU        |              R                 |               R               |          R          |         R         |            R            |
| `.../RESEARCH_PLAN.md`                              |         O,CRU        |             CRU                |               R               |          R          |         R         |            R            |
| `.../WORK_PLAN.md`                                  |         O,CRU        |              R                 |               R               |          R          |         R         |            R            |
| `.../STEP_BREAKDOWN.md`                             |         O,CRU        |              R                 |               R               |          R          |         R         |            R            |
| `.../ACCESS_MATRIX_TEMPLATE.md` (This file)         |         O,CRU        |              R                 |               R               |          R          |         R         |            R            |
| `.../research_outputs/` (e.g., summaries, moodboards) |          R           |             O,CRU              |               R               |          R          |         R         |            R            |
| `.../democratic_decisions/` (Decision logs)         |         O,CRU        |              R                 |               R               |          R         |        CRU        |            R            |

## II. Development Artifacts (To be defined post-architecture decision)

*This section will be populated once the technical architecture is chosen. It will include source code directories, asset folders, build scripts, etc.* 

| Artifact / Directory Path (Example) | PM (Gemini 2.5 Pro) | Dev Team (Claude, Codestral) | Debugger (Codestral) | Tester (Mistral M.) | All Agents (Read-Only) |
| :---------------------------------- | :------------------: | :---------------------------: | :-------------------: | :-----------------: | :---------------------: |
| `/src/`                             |          R           |             O,CRU             |          CRU          |          R          |            R            |
| `/src/components/`                  |          R           |             O,CRU             |          CRU          |          R          |            R            |
| `/src/assets/`                      |          R           |             CRU               |           R           |          R          |            R            |
| `/public/` or `/dist/` (Build output) |          R           |              R                |           R           |         CRU         |            R            |
| `content/` (If using CMS-like structure) |          R           |             CRU               |           R           |          R          |            R            |

## III. Testing & QA Artifacts

| Artifact / Directory Path         | PM (Gemini 2.5 Pro) | Tester (Mistral M.) | Dev Team (Claude, Codestral) | All Agents (Read-Only) |
| :-------------------------------- | :------------------: | :-----------------: | :---------------------------: | :---------------------: |
| `test_plans/`                     |          R           |        O,CRU        |               R               |            R            |
| `bug_reports/`                    |          R           |        O,CRU        |              CRU              |            R            |
| `test_results/`                   |          R           |        O,CRU        |               R               |            R            |

## Notes:

*   This matrix is a living document and can be updated by the PM as the project evolves and new artifacts are created.
*   Specific file paths within directories will generally inherit the directory's permissions unless specified otherwise.
*   The principle of least privilege should be applied: agents only get the access they need to perform their roles.
*   All agents are expected to respect these access controls to maintain project integrity and organization.