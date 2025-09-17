# YAML Data Dictionary

Below are the canonical keys, types, meanings, and examples. Types use simple
JSON-style primitives plus small enums.

## Shared primitives

- **string** (non-empty text)
- **int** (integer)
- **bool** (true/false)
- **list[T]** (ordered list of T)
- **map{K: V}** (key/value object)
- **enum** (one of a fixed set)

---

## 1) `preferences/general.md` (document_type: `general_preferences`)

| Key | Type | Meaning | Example |
|-----|------|---------|---------|
| document_type | enum | Must be `general_preferences` | `general_preferences` |
| version | string | Schema/version of standards | `1.0` |
| tooling.language | string | Default language/runtime | `python3.11` |
| tooling.frameworks | list[string] | Default frameworks | `["fastapi","sqlalchemy","pytest"]` |
| tooling.database | list[string] | Supported DBs (pref order) | `["postgresql","sqlite"]` |
| tooling.infrastructure | list[string] | Platforms / orchestrators | `["docker","kubernetes","gcp"]` |
| tooling.environment | list[string] | Dev environment/tools | `["vscode","ruff","black","mypy"]` |
| coding_standards.type_hints | enum | Hinting approach | `modern` |
| coding_standards.docstrings | enum | Docstring style | `google` |
| coding_standards.line_length | int | Max line length | `88` |
| coding_standards.imports | enum | Import policy | `sorted_preserve_unused` |
| coding_standards.error_handling | enum | Error strategy | `custom_exceptions` |
| testing.framework | enum | Test framework | `pytest` |
| testing.coverage_goal | int | % coverage target | `90` |
| testing.fixtures | enum | Fixture guidance | `pytest_fixtures` |
| testing.mocking | enum | Mocking preference | `pytest_mock` |
| bug_fixes.require_failing_test | bool | Repro before fix | `true` |
| bug_fixes.regression_tests | enum | Require regression tests | `required` |
| bug_fixes.commit_explanation | enum | Root-cause in PRs | `required` |
| features.acceptance_criteria | enum | Feature AC req | `required` |
| features.feature_flags | enum | Disruptive change toggle | `recommended` |
| features.documentation | enum | Doc updates req | `required` |
| features.pr_size | enum | PR size guidance | `small_incremental` |
| documentation.readme | enum | README required | `required` |
| documentation.api_docs | enum | API doc posture | `auto_generated` |
| documentation.changelog | enum | Changelog policy | `required` |
| ci_cd.tests_required | bool | Tests must pass | `true` |
| ci_cd.linting_formatting | enum | CI enforcement | `enforced` |
| ci_cd.deployments | enum | Build reproducibility | `reproducible` |
| best_practices.security | enum | Secrets & least privilege | `least_privilege_env` |
| best_practices.scalability | enum | Scalability posture | `stateless_horizontal` |
| best_practices.maintainability | enum | Maintainability | `dry_solid` |
| best_practices.observability | enum | Observability posture | `logging_metrics_tracing` |
| workflow.branching | enum | Branch model | `gitflow_or_trunk` |
| workflow.commits | enum | Commit style | `conventional_commits` |
| workflow.issues | enum | Issue templates | `templates_required` |
| workflow.reviews | enum | Review policy | `one_reviewer_min` |

---

## 2) `preferences/project.md` (document_type: `project_spec`)

> Carries **context** and **overrides**. Only specify overrides that differ
> from `general.md`.

| Key | Type | Meaning | Example |
|-----|------|---------|---------|
| document_type | enum | Must be `project_spec` | `project_spec` |
| project_name | string | Human project name | `Coffee Roast Tracker` |
| description | string | One-paragraph summary | `Track coffee roast metrics…` |
| status | enum | idea/active/maintenance/archived | `active` |
| goals | list[string] | Top-level goals | `["MVP logging","CSV export"]` |
| deliverables | list[string] | Tangible outputs | `["FastAPI service","CLI"]` |
| stakeholders | list[string] or map | People/teams | `["Ops","Data Eng"]` |
| dependencies | list[string] | External libs/services | `["GBQ","Auth0"]` |
| tech_stack.language | string | Effective language | `python3.11` |
| tech_stack.frameworks | list[string] | Chosen frameworks | `["fastapi","sqlalchemy"]` |
| tech_stack.database | list[string] | DBs used | `["sqlite"]` |
| tech_stack.infrastructure | list[string] | Infra used | `["docker"]` |
| tech_stack.environment | list[string] | Local dev tools | `["vscode"]` |
| constraints.performance | string\|null | Perf constraints | `p95 < 200ms` |
| constraints.compliance | string\|null | Compliance reqs | `HIPAA data segregation` |
| constraints.cost | string\|null | Budget constraints | `Serverless tier` |
| overrides.* | mixed | Any key from general that differs | `coding_standards.line_length: 100` |
| risks | list[string] | Risks | `["SQLite contention"]` |
| open_questions | list[string] | Unknowns | `["Auth provider?"]` |
| llm_usage | list[string] | Intended assistance | `["documentation","review"]` |

---

## 3) `requirements/requirements.md` (document_type: `software_requirements`)

| Key | Type | Meaning | Example |
|-----|------|---------|---------|
| document_type | enum | `software_requirements` | `software_requirements` |
| project_name | string | Name | `Coffee Roast Tracker` |
| summary | string | 1–3 sentence summary | `A FastAPI service…` |
| status | enum | idea/active/maintenance/archived | `active` |
| primary_goals | list[string] | Goals | `["MVP logging"]` |
| out_of_scope | list[string] | Explicit exclusions | `["Payments"]` |
| stakeholders.owners | list[string] | Owners | `["Dan"]` |
| stakeholders.users | list[string] | End users/roles | `["Barista","Roaster"]` |
| stakeholders.others | list[string] | Other stakeholders | `["Ops"]` |
| problem_statement | string | Why now / value | `Paper logs are brittle…` |
| functional_requirements | list[string] | “The system must…” | `["Create roast"]` |
| non_functional_requirements.performance | string\|null | Perf targets | `p95 < 200ms` |
| non_functional_requirements.scalability | string\|null | Scale posture | `Stateless` |
| non_functional_requirements.security | string\|null | Sec posture | `AuthN/Z` |
| non_functional_requirements.compliance | string\|null | Compliance | `PHI: no` |
| system_context.external_systems | list[string] | Ext systems | `["GBQ"]` |
| system_context.data_sources | list[string] | Data providers | `["REST API"]` |
| system_context.apis.consumed | list[string] | APIs used | `["Auth0"]` |
| system_context.apis.exposed | list[string] | APIs provided | `["/roasts"]` |
| technical_constraints.languages | list[string] | Langs | `["python3.11"]` |
| technical_constraints.frameworks | list[string] | Frameworks | `["fastapi"]` |
| technical_constraints.deployment | list[string] | Deploy envs | `["docker"]` |
| technical_constraints.database | list[string] | DBs | `["sqlite"]` |
| technical_constraints.observability | list[string] | Observability | `["logging","metrics"]` |
| data_model | string or link | ERD link or brief text | `docs/erd.png` |
| user_stories | list[string] | As a X, I want Y | `["As a roaster…"]` |
| acceptance_criteria | list[string] | Measurable checks | `["POST /roasts 201"]` |
| risks | list[string] | Risks | `["Data loss"]` |
| assumptions | list[string] | Assumptions | `["Single user"]` |
| glossary | map{string:string} | Terms | `{ "charge": "…" }` |

---

## 4) `requirements/understanding.md` (document_type: `project_understanding`)

| Key | Type | Meaning | Example |
|-----|------|---------|---------|
| document_type | enum | `project_understanding` | `project_understanding` |
| project_name | string | Name | `Coffee Roast Tracker` |
| summary | string | Short description | `Tracks roasts` |
| domain | string | Domain/problem area | `Coffee roasting` |
| primary_purpose | string | Why this exists | `Log & analyze roasts` |
| current_state.architecture | enum\|string | Monolith/microservices/etc. | `layered` |
| current_state.components | list[string] | Major modules | `["api","db","cli"]` |
| current_state.dependencies | list[string] | Libs | `["fastapi","sqlalchemy"]` |
| current_state.integrations | list[string] | Ext systems | `["GBQ"]` |
| current_state.deployment | list[string] | Deploy setup | `["docker","gha ci"]` |
| features.current | list[string] | Shipped features | `["Create roast"]` |
| features.desired | list[string] | Wishlist | `["Charts"]` |
| issues.bugs | list[string] | Known bugs | `["CSV export fails"]` |
| issues.technical_debt.maintainability | list[string] | Hotspots | `["God module"]` |
| issues.technical_debt.outdated_dependencies | list[string] | Old deps | `["Starlette < 0.3"]` |
| issues.technical_debt.style_consistency | list[string] | Style issues | `["mix of sync/async"]` |
| documentation_gaps | list[string] | Missing docs | `["No README quickstart"]` |
| data_model.entities | list[string] | Entities | `["Roast","User"]` |
| data_model.schema | string or link | Schema/diagram | `docs/db.sql` |
| context_diagram | string or link | Diagram or note | `docs/context.mmd` |
| glossary | map{string:string} | Terms | `{ "first crack": "…" }` |

---

## 5) `prompts/generator_prompt.md` (document_type: `llm_generator_prompt`)

| Key | Type | Meaning | Example |
|-----|------|---------|---------|
| document_type | enum | `llm_generator_prompt` | `llm_generator_prompt` |
| project_name | string | Name | `Coffee Roast Tracker` |
| summary | string | One-paragraph summary | `…` |
| problem_statement | string | Why now | `…` |
| functional_requirements | list[string] | Must-haves | `["Create roast"]` |
| non_functional_requirements | list[string] or map | NFRs | `["p95<200ms"]` |
| system_context.integrations | list[string] | Integrations | `["GBQ"]` |
| system_context.apis | list[string] | APIs | `["Auth0"]` |
| technical_constraints.languages | list[string] | Langs | `["python3.11"]` |
| technical_constraints.frameworks | list[string] | Frameworks | `["fastapi"]` |
| technical_constraints.infrastructure | list[string] | Infra | `["docker"]` |
| data_model.entities | list[string] | Entities | `["Roast"]` |
| data_model.fields | list[string] | Fields (flat) | `["roast_at:datetime"]` |
| user_stories | list[string] | Stories | `["As a roaster…"]` |
| acceptance_criteria | list[string] | ACs | `["201 on POST"]` |
| risks | list[string] | Risks | `["Data loss"]` |
| assumptions | list[string] | Assumptions | `["Single user"]` |
| requested_outputs | list[string] | What to generate | `["code_skeletons","unit_tests"]` |

---

## 6) `prompts/analyzer_prompt.md` (document_type: `llm_analyzer_prompt`)

| Key | Type | Meaning | Example |
|-----|------|---------|---------|
| document_type | enum | `llm_analyzer_prompt` | `llm_analyzer_prompt` |
| project_name | string | Name | `Coffee Roast Tracker` |
| inputs | list[string] | Required docs | `["understanding.md","general.md"]` |
| requested_outputs | list[string] | What to produce | `["documentation_update","bug_fix_suggestions"]` |

---

## Allowed `requested_outputs` (for both prompts)

```text
architecture_summary
code_skeletons
database_schema
unit_tests
readme_snippet
pr_checklist
mvp_plan
system_summary
documentation_update
outdated_docs_cleanup
bug_fix_suggestions
feature_implementation_steps
standards_alignment
risks_and_inconsistencies
maintainability_improvements
```
