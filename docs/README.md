<!-- code2docs:start --># doql

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.10-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-2256-green)
> **2256** functions | **46** classes | **288** files | CC̄ = 3.6

> Auto-generated project documentation from source code analysis.

**Author:** Softreck  
**License:** Apache-2.0[(LICENSE)](./LICENSE)  
**Repository:** [https://github.com/oqlos/doql](https://github.com/oqlos/doql)

## Installation

### From PyPI

```bash
pip install doql
```

### From Source

```bash
git clone https://github.com/oqlos/doql
cd doql
pip install -e .
```

### Optional Extras

```bash
pip install doql[dev]    # development tools
pip install doql[api]    # api features
pip install doql[lsp]    # lsp features
pip install doql[deploy]    # deploy features
pip install doql[device-adopt]    # device-adopt features
```

## Quick Start

### CLI Usage

```bash
# Generate full documentation for your project
doql ./my-project

# Only regenerate README
doql ./my-project --readme-only

# Preview what would be generated (no file writes)
doql ./my-project --dry-run

# Check documentation health
doql check ./my-project

# Sync — regenerate only changed modules
doql sync ./my-project
```

### Python API

```python
from doql import generate_readme, generate_docs, Code2DocsConfig

# Quick: generate README
generate_readme("./my-project")

# Full: generate all documentation
config = Code2DocsConfig(project_name="mylib", verbose=True)
docs = generate_docs("./my-project", config=config)
```




## Architecture

```
doql/
├── SUMR
├── goal
├── doql/
├── SUMD
├── GLOSSARY
├── pyqual
├── pyproject
├── tree
├── PARSER_AUDIT
    ├── testql
├── OQLOS-REQUIREMENTS
├── TODO
├── test_playbook
├── test_all_desktop
├── CHANGELOG
├── Taskfile
├── project
├── ROADMAP
├── Jenkinsfile
├── SPEC
├── README
    ├── README
    ├── refactoring-plan
        ├── context
        ├── context
            ├── toon
            ├── toon
        ├── context
            ├── toon
            ├── toon
        ├── context
            ├── toon
            ├── toon
            ├── toon
    ├── SUMR
    ├── EXAMPLES-TEST-REPORT
    ├── SUMD
    ├── sumd
    ├── Taskfile
        ├── pyqual
        ├── app
        ├── Taskfile
        ├── README
        ├── app
        ├── Taskfile
        ├── README
        ├── app
        ├── Taskfile
        ├── README
        ├── app
        ├── Taskfile
        ├── README
            ├── customers
            ├── organization
            ├── toon
        ├── app
        ├── Taskfile
        ├── README
        ├── app
        ├── Taskfile
        ├── README
        ├── app
        ├── Taskfile
        ├── README
        ├── app
        ├── Taskfile
        ├── README
            ├── index
        ├── app
        ├── Taskfile
        ├── README
    ├── 05-doql-migration-guide
    ├── 03-doql-less-calibration-lab-example
    ├── 04-doql-sass-notes-app-example
    ├── 01-doql-format-migration-analysis
    ├── README
    ├── 02-doql-css-iot-fleet-example
        ├── context
            ├── toon
            ├── toon
        ├── SUMR
        ├── SUMD
        ├── sumd
        ├── pyproject
                ├── toon
            ├── readme
            ├── base
        ├── doql_plugin_shared/
        ├── SUMR
        ├── SUMD
        ├── sumd
        ├── pyproject
        ├── README
                ├── toon
        ├── doql_plugin_fleet/
            ├── metrics
            ├── device_registry
            ├── ota
            ├── migration
            ├── tenant
        ├── SUMR
        ├── SUMD
        ├── sumd
        ├── pyproject
        ├── README
        ├── doql_plugin_gxp/
                ├── toon
        ├── SUMR
        ├── SUMD
        ├── sumd
        ├── pyproject
        ├── README
                ├── toon
        ├── doql_plugin_erp/
        ├── SUMR
        ├── SUMD
        ├── sumd
        ├── pyproject
        ├── README
            ├── traceability
        ├── doql_plugin_iso17025/
            ├── certificate
            ├── migration
            ├── uncertainty
            ├── drift_monitor
                ├── toon
            ├── infra-local-9dd2f59b
        ├── toon
        ├── toon
            ├── toon
            ├── toon
            ├── toon
    ├── serve
    ├── pyodide-bridge
    ├── renderers
    ├── README
    ├── app
    ├── SUMR
    ├── SUMD
    ├── tsconfig
    ├── sumd
    ├── language-configuration
    ├── package
    ├── README
            ├── tmLanguage
            ├── tmLanguage
        ├── extension
            ├── toon
    ├── cli/
    ├── plugins
    ├── parser
    ├── lsp_server
        ├── detector
    ├── drift/
    ├── importers/
        ├── yaml_importer
        ├── lockfile
        ├── context
        ├── __main__
        ├── sync
        ├── main
            ├── render
            ├── plan
            ├── validate
            ├── export
            ├── init
            ├── query
            ├── workspace
            ├── doctor
            ├── kiosk
            ├── generate
            ├── drift
        ├── commands/
            ├── adopt
            ├── quadlet
            ├── deploy
            ├── import_cmd
            ├── run
            ├── publish
            ├── docs
            ├── app
            ├── app
            ├── app
            ├── app
        ├── css_exporter
    ├── exporters/
        ├── yaml_exporter
        ├── markdown_exporter
            ├── format_convert
            ├── helpers
            ├── renderers
        ├── css/
            ├── writers
        ├── markdown/
            ├── sections
        ├── docs_gen
        ├── infra_gen
        ├── integrations_gen
        ├── ci_gen
        ├── export_postman
        ├── desktop_gen
    ├── generators/
        ├── document_gen
        ├── export_ts_sdk
        ├── workflow_gen
        ├── deploy
        ├── i18n_gen
        ├── mobile_gen
        ├── api_gen/
        ├── vite_gen
        ├── web_gen/
        ├── report_gen
            ├── codegen
            ├── config
            ├── pwa
            ├── common
            ├── components
            ├── router
            ├── pages
            ├── core
            ├── common
            ├── alembic
            ├── routes
            ├── schemas
            ├── auth
            ├── database
            ├── models
            ├── main
        ├── clean
    ├── utils/
        ├── naming
    ├── adopt/
        ├── scanner/
        ├── emitter
        ├── device_scanner
            ├── interfaces
            ├── metadata
            ├── databases
            ├── integrations
            ├── deploy
            ├── workflows
            ├── utils
            ├── roles
            ├── environments
            ├── entities
        ├── css_tokenizer
        ├── css_parser
        ├── blocks
        ├── extractors
        ├── css_transformers
        ├── registry
    ├── parsers/
        ├── css_utils
        ├── validators
        ├── models
        ├── css_mappers
    ├── integrations/
        ├── op3_bridge
    ├── 02-testql-status-2026-q2
    ├── 06-doql-v02-dokumenty-kiosk
    ├── 05-wizja-ekosystemu-oqlos
    ├── 04-doql-ogloszenie
    ├── 03-saas-www-status-2026-q2
    ├── 01-oqlos-status-2026-q2
    ├── README
    ├── prompt
        ├── toon
        ├── toon
    ├── context
        ├── toon
    ├── README
        ├── toon
    ├── calls
        ├── toon
```

## API Overview

### Classes

- **`Plugin`** — —
- **`Plugin`** — —
- **`Scenario`** — —
- **`Execution`** — —
- **`User`** — —
- **`Role`** — —
- **`Workflow`** — —
- **`Storage`** — —
- **`NotificationService`** — —
- **`AuditEntry`** — —
- **`WebhookDispatcher`** — —
- **`DiagnosticCheck`** — —
- **`BraceConverter`** — —
- **`FormatExtractor`** — —
- **`LessYamlAdapter`** — —
- **`Plugin`** — —
- **`BuildContext`** — Build context for doql commands.
- **`DoqlProject`** — Minimal project descriptor (used when taskfile is not installed).
- **`Check`** — —
- **`DoctorReport`** — —
- **`CssBlock`** — Single CSS-like rule: selector + key-value declarations.
- **`ParsedSelector`** — Decomposed CSS selector.
- **`DoqlParseError`** — Raised when a .doql file cannot be parsed.
- **`ValidationIssue`** — —
- **`EntityField`** — —
- **`Entity`** — —
- **`DataSource`** — —
- **`Template`** — —
- **`Document`** — —
- **`Report`** — —
- **`Database`** — —
- **`ApiClient`** — —
- **`Webhook`** — —
- **`Page`** — —
- **`Interface`** — —
- **`Integration`** — —
- **`WorkflowStep`** — —
- **`Workflow`** — —
- **`Role`** — —
- **`Deploy`** — —
- **`Environment`** — —
- **`Infrastructure`** — —
- **`Ingress`** — —
- **`CiConfig`** — —
- **`Subproject`** — A named sub-project inside a monorepo DOQL manifest.
- **`DoqlSpec`** — —

### Functions

- `did_open()` — —
- `did_change()` — —
- `did_save()` — —
- `completion()` — —
- `hover()` — —
- `definition()` — —
- `document_symbols()` — —
- `main()` — —
- `discover_plugins()` — —
- `run_plugins()` — —
- `usage()` — —
- `adopt_from_device_to_snapshot()` — —
- `adopt_from_device()` — —
- `emit_css()` — —
- `emit_spec()` — —
- `scan_project()` — —
- `scan_databases()` — —
- `scan_deploy()` — —
- `scan_entities()` — —
- `scan_environments()` — —
- `scan_integrations()` — —
- `scan_interfaces()` — —
- `scan_metadata()` — —
- `scan_roles()` — —
- `load_yaml()` — —
- `find_compose()` — —
- `find_dockerfiles()` — —
- `camel_to_kebab()` — —
- `snake_to_pascal()` — —
- `normalize_python_type()` — —
- `normalize_sqlalchemy_type()` — —
- `normalize_sql_type()` — —
- `scan_workflows()` — —
- `should_generate_interface()` — —
- `run_core_generators()` — —
- `run_document_generators()` — —
- `run_report_generators()` — —
- `run_i18n_generators()` — —
- `run_integration_generators()` — —
- `run_workflow_generators()` — —
- `run_ci_generator()` — —
- `run_vite_generator()` — —
- `run_plugins()` — —
- `cmd_build()` — —
- `cmd_adopt()` — —
- `cmd_deploy()` — —
- `cmd_docs()` — —
- `cmd_doctor()` — —
- `cmd_drift()` — —
- `cmd_export()` — —
- `cmd_generate()` — —
- `cmd_import()` — —
- `cmd_init()` — —
- `cmd_kiosk()` — —
- `cmd_plan()` — —
- `cmd_publish()` — —
- `cmd_quadlet()` — —
- `cmd_query()` — —
- `cmd_render()` — —
- `cmd_run()` — —
- `cmd_validate()` — —
- `cmd_workspace()` — —
- `register_parser()` — —
- `build_context()` — —
- `load_spec()` — —
- `scaffold_from_template()` — —
- `estimate_file_count()` — —
- `spec_section_hashes()` — —
- `read_lockfile()` — —
- `diff_sections()` — —
- `write_lockfile()` — —
- `create_parser()` — —
- `main()` — —
- `determine_regeneration_set()` — —
- `run_generators()` — —
- `cmd_sync()` — —
- `find_intended_file()` — —
- `parse_intended()` — —
- `detect_drift()` — —
- `export_css()` — —
- `export_less()` — —
- `export_sass()` — —
- `export_css_file()` — —
- `export_markdown()` — —
- `export_markdown_file()` — —
- `spec_to_dict()` — —
- `export_yaml()` — —
- `export_yaml_file()` — —
- `generate()` — —
- `export_openapi()` — —
- `gen_alembic_ini()` — —
- `gen_alembic_env()` — —
- `gen_initial_migration()` — —
- `gen_auth()` — —
- `sa_type()` — —
- `py_type()` — —
- `py_default()` — —
- `safe_name()` — —
- `snake()` — —
- `gen_database()` — —
- `gen_main()` — —
- `gen_requirements()` — —
- `gen_models()` — —
- `gen_routes()` — —
- `gen_schemas()` — —
- `run()` — —
- `write_code_block()` — —
- `generate_file_from_template()` — —
- `import_yaml()` — —
- `import_yaml_text()` — —
- `import_yaml_file()` — —
- `build_layer_tree()` — —
- `snapshot_to_less()` — —
- `did_open()` — —
- `did_change()` — —
- `did_save()` — —
- `completion()` — —
- `hover()` — —
- `definition()` — —
- `document_symbols()` — —
- `detect_doql_file()` — —
- `parse_file()` — —
- `parse_text()` — —
- `parse_env()` — —
- `split_blocks()` — —
- `apply_block()` — —
- `parse_css_file()` — —
- `parse_css_text()` — —
- `extract_val()` — —
- `extract_list()` — —
- `extract_yaml_list()` — —
- `extract_pages()` — —
- `extract_entity_fields()` — —
- `collect_env_refs()` — —
- `register()` — —
- `get_handler()` — —
- `list_registered()` — —
- `validate()` — —
- `discover_plugins()` — —
- `kebab()` — —
- `build()` — —
- `plugin_generate()` — —
- `generate_readme()` — —
- `check_api()` — —
- `check_web()` — —
- `check_mobile()` — —
- `check_desktop()` — —
- `check_infra()` — —
- `process_example()` — —
- `render_text()` — —
- `render_json()` — —
- `test_adopt_from_device_returns_less_text()` — —
- `test_adopt_from_device_writes_output()` — —
- `test_adopt_from_device_to_snapshot_contains_layer_data()` — —
- `test_adopt_output_is_parsable_by_doql()` — —
- `test_adopt_from_rpi5_podman_quadlet_returns_less_text()` — —
- `test_adopt_from_rpi5_to_snapshot_contains_all_services()` — —
- `test_adopt_from_rpi5_to_snapshot_contains_all_containers()` — —
- `test_adopt_from_rpi5_output_is_parsable_by_doql()` — —
- `test_cmd_adopt_from_device_writes_file()` — —
- `test_cmd_adopt_rejects_non_less_format()` — —
- `test_cmd_adopt_without_target_or_device_errors()` — —
- `test_cmd_adopt_refuses_to_overwrite()` — —
- `test_scan_device_writes_app_doql_less_in_root()` — —
- `test_scan_device_honours_global_file_flag()` — —
- `test_scan_device_refuses_to_overwrite_without_force()` — —
- `test_scan_device_force_overwrites()` — —
- `test_cmd_build_from_device_runs_full_pipeline()` — —
- `test_cmd_build_refuses_to_clobber_without_force()` — —
- `test_cmd_build_without_from_device_skips_scan()` — —
- `test_parse_intended_attaches_source_path()` — —
- `test_parse_intended_missing_file()` — —
- `test_detect_drift_no_changes()` — —
- `test_detect_drift_service_state_mismatch()` — —
- `test_detect_drift_missing_file_raises()` — —
- `test_cmd_drift_returns_drift_exit_code()` — —
- `test_cmd_drift_json_output_is_valid()` — —
- `test_cmd_drift_missing_from_device()` — —
- `test_cmd_drift_missing_file()` — —
- `test_cmd_drift_unsupported_format_gives_actionable_hint()` — —
- `test_cmd_drift_explicit_missing_file()` — —
- `test_cmd_drift_no_drift_exit_code_zero()` — —
- `test_op3_importable()` — —
- `test_op3_enabled_reads_env()` — —
- `test_should_use_op3_requires_both()` — —
- `test_require_op3_noop_when_available()` — —
- `test_build_layer_tree_defaults()` — —
- `test_build_layer_tree_explicit_leaf_pulls_deps()` — —
- `test_build_layer_tree_rejects_unknown()` — —
- `test_scanner_runs_against_mock_context()` — —
- `test_snapshot_to_less_produces_parsable_less()` — —
- `serve()` — —
- `step()` — —
- `test_jwt_secret_does_not_crash_renderer()` — —
- `test_pydantic_dtos_are_excluded_from_entities()` — —
- `test_generic_db_service_name_is_normalised()` — —
- `test_fastapi_dependency_alone_does_not_create_api_interface()` — —
- `test_fastapi_with_main_py_creates_api()` — —
- `test_api_entry_point_in_scripts_creates_api()` — —
- `test_cmd_adopt_returns_zero_on_success()` — —
- `test_cmd_adopt_returns_nonzero_on_render_failure()` — —
- `test_cmd_adopt_refuses_to_overwrite_without_force()` — —
- `test_cmd_adopt_rejects_non_directory()` — —
- `test_makefile_targets_become_workflows()` — —
- `test_makefile_workflows_round_trip_to_css()` — —
- `test_taskfile_yml_tasks_become_workflows()` — —
- `test_dependency_only_targets_emit_depend_steps()` — —
- `test_empty_target_without_deps_is_skipped()` — —
- `test_makefile_variable_assignments_are_not_workflows()` — —
- `test_workflows_are_deduplicated_across_makefile_and_taskfile()` — —
- `test_adopt_e2e_real_project_oqlos()` — —
- `test_discover_subprojects()` — —
- `test_click_not_inferred_from_comment_or_changelog()` — —
- `test_fastapi_detected_from_server_py()` — —
- `test_css_parse_minimal()` — —
- `test_css_parse_entity()` — —
- `test_css_parse_interface()` — —
- `test_css_parse_role()` — —
- `test_css_parse_deploy()` — —
- `test_less_variable_expansion()` — —
- `test_sass_basic_parsing()` — —
- `test_parses_css_example_file()` — —
- `test_detect_doql_file_prefers_less()` — —
- `test_detect_doql_file_prefers_sass()` — —
- `test_detect_doql_file_falls_back_to_classic()` — —
- `test_iot_fleet_less_has_entities()` — —
- `test_notes_app_sass_has_all_interfaces()` — —
- `test_css_parse_error_has_line_info()` — —
- `test_css_unknown_selector_gives_warning()` — —
- `test_less_syntax_error_recovery()` — —
- `test_doql_vs_less_regression()` — —
- `test_css_parse_project_blocks()` — —
- `sample_spec()` — —
- `test_yaml_roundtrip_real_example()` — —
- `test_css_export_real_example()` — —
- `test_markdown_export_real_example()` — —
- `test_css_export_project_blocks()` — —
- `test_css_exporter_shim_re_exports_public_api()` — —
- `test_css_exporter_shim_re_exports_renderers()` — —
- `test_css_exporter_shim_re_exports_format_helpers()` — —
- `test_markdown_exporter_shim_re_exports_public_api()` — —
- `test_markdown_exporter_shim_re_exports_writers()` — —
- `test_markdown_exporter_shim_re_exports_helpers()` — —
- `test_css_shim_roundtrip_matches_direct_subpackage()` — —
- `test_build_example()` — —
- `test_init_and_build_template()` — —
- `test_sync_no_changes_is_noop()` — —
- `test_list_templates_includes_all()` — —
- `test_parse_doc_handles_valid_input()` — —
- `test_parse_doc_returns_none_on_crash()` — —
- `test_find_line_col_finds_needle()` — —
- `test_word_at_extracts_word()` — —
- `test_diagnostics_on_asset_management_example()` — —
- `test_keyword_completion_includes_common_top_level()` — —
- `test_parse_text_minimal()` — —
- `test_parse_text_full_entity()` — —
- `test_parse_text_languages_list()` — —
- `test_parse_text_workflow_with_schedule_and_inline_comment()` — —
- `test_parse_text_recovers_from_broken_block()` — —
- `test_parse_errors_is_a_list()` — —
- `test_parses_example_file()` — —
- `test_asset_management_entities()` — —
- `test_validate_detects_missing_env_ref()` — —
- `test_validation_issue_has_line_field()` — —
- `test_validate_detects_dangling_entity_ref()` — —
- `test_calibration_lab_has_no_dangling_refs()` — —
- `test_deprecated_docker_compose_strategy_warns()` — —
- `test_deprecated_quadlet_strategy_warns()` — —
- `test_canonical_strategy_no_warning()` — —
- `test_css_parser_cold_start_under_threshold()` — —
- `test_less_parser_variable_resolution_under_threshold()` — —
- `test_real_example_parse_under_threshold()` — —
- `test_css_vs_classic_parse_time_parity()` — —
- `test_large_file_parse_under_threshold()` — —
- `test_entrypoint_discovery_finds_all_four()` — —
- `test_doql_plugins_module_import()` — —
- `test_iso17025_uncertainty_budget_numerical()` — —
- `test_iso17025_drift_monitor_detects_stable()` — —
- `test_iso17025_drift_monitor_flags_excessive_drift()` — —
- `test_fleet_ota_canary_advances_on_success()` — —
- `test_gxp_audit_log_hash_is_deterministic()` — —
- `test_api_boot_and_health()` — —
- `test_build_produces_expected_targets()` — —
- `get_schema()` — —
- `advance()` — —
- `put()` — —
- `get()` — —
- `delete()` — —
- `presigned_url()` — —
- `send()` — —
- `generate_report()` — —
- `register()` — —
- `dispatch()` — —
- `convert()` — —
- `detect()` — —
- `extract_page()` — —
- `extract_blocks()` — —
- `less_to_yaml()` — —
- `yaml_to_less()` — —
- `tests()` — —
- `stage()` — —
- `dir()` — —
- `cleanWs()` — —
- `generate_readme()` — —
- `cmd_deploy()` — —
- `test_doql_vs_less_regression()` — —
- `plugin_generate()` — —
- `generate_readme()` — —
- `plugin_generate()` — —
- `generate_readme()` — —
- `generate_readme(plugin_name, modules, description, usage_extra)` — Generate standard README.md content for a doql plugin.
- `plugin_generate(out, modules, readme_content)` — Common plugin generate() — iterates over modules dict and writes files.
- `generate()` — —
- `generate()` — —
- `generate(spec, env_vars, out, project_root)` — Entry point called by doql's plugin runner.
- `generate()` — —
- `generate(spec, env_vars, out, project_root)` — Entry point called by doql's plugin runner.
- `generate()` — —
- `generate()` — —
- `generate()` — —
- `generate(spec, env_vars, out, project_root)` — Entry point called by doql's plugin runner.
- `generate()` — —
- `generate()` — Generate traceability.py module content.
- `generate(spec, env_vars, out, project_root)` — Entry point called by doql's plugin runner.
- `generate()` — Generate certificate.py module content.
- `generate()` — Generate migration.py module content.
- `generate()` — Generate uncertainty.py module content.
- `generate()` — Generate drift_monitor.py module content.
- `generate()` — —
- `pyodide()` — —
- `buildFn()` — —
- `debounceTimer()` — —
- `initElements()` — —
- `isReady()` — —
- `debouncedBuild()` — —
- `executeBuild()` — —
- `r()` — —
- `resp()` — —
- `src()` — —
- `bootPyodide()` — —
- `version()` — —
- `escapeHtml()` — —
- `renderFatal()` — —
- `renderDiagnostics()` — —
- `loc()` — —
- `renderAst()` — —
- `renderEnv()` — —
- `refs()` — —
- `keys()` — —
- `marker()` — —
- `renderFiles()` — —
- `Pyodide()` — —
- `TAB_NAMES()` — —
- `activateTab()` — —
- `tabFromHash()` — —
- `name()` — —
- `initial()` — —
- `key()` — —
- `updateStats()` — —
- `lines()` — —
- `chars()` — —
- `activate()` — —
- `config()` — —
- `serverPath()` — —
- `deactivate()` — —
- `discover_plugins(project_root)` — Discover all plugins — entry-point + local.
- `run_plugins(spec, env_vars, build_dir, project_root)` — Run all discovered plugins. Returns count of plugins executed.
- `did_open(ls, params)` — —
- `did_change(ls, params)` — —
- `did_save(ls, params)` — —
- `completion(ls, params)` — —
- `hover(ls, params)` — —
- `definition(ls, params)` — —
- `document_symbols(ls, params)` — —
- `main()` — —
- `find_intended_file(directory)` — Locate the canonical ``.doql.less`` under ``directory``.
- `parse_intended(path)` — Parse a ``.doql.less`` file into an :class:`opstree.PartialSnapshot`.
- `detect_drift(target)` — Compare ``file`` (or auto-detected ``app.doql.less``) against ``target``.
- `import_yaml(data)` — Build a DoqlSpec from a YAML-style dictionary.
- `import_yaml_text(text)` — Parse YAML text and return a DoqlSpec.
- `import_yaml_file(path)` — Read a YAML file and return a DoqlSpec.
- `spec_section_hashes(spec, ctx)` — Compute per-section hashes for diff detection.
- `read_lockfile(ctx)` — Read and parse lockfile if it exists.
- `diff_sections(old_hashes, new_hashes)` — Return dict of changed/added/removed section keys.
- `write_lockfile(spec, ctx)` — Write current spec hashes to lockfile.
- `build_context(args)` — Create BuildContext from CLI arguments.
- `load_spec(ctx)` — Parse spec and env, return (spec, env_vars).
- `scaffold_from_template(template, target)` — Copy scaffold template to target directory.
- `estimate_file_count(iface)` — Rough estimate of file count per interface type.
- `determine_regeneration_set(diff_result, spec)` — Determine which generators need to re-run based on diff.
- `run_generators(regen, spec, env_vars, ctx)` — Run selected generators based on regen set. Returns count of generators run.
- `cmd_sync(args)` — Selective rebuild — only regenerate sections that changed since last build.
- `create_parser()` — Create and configure the argument parser with all subcommands.
- `main()` — Main entry point for doql CLI.
- `cmd_render(args)` — Render a template with DATA sources.
- `cmd_plan(args)` — Show dry-run plan of what would be generated.
- `cmd_validate(args)` — Validate .doql file and .env configuration.
- `cmd_export(args)` — Export project specification to various formats.
- `cmd_init(args)` — Create new project from template.
- `cmd_query(args)` — Query a DATA source and output as JSON.
- `cmd_workspace(args)` — Dispatch to the right workspace subcommand.
- `register_parser(sub)` — Register `workspace` subcommands on the main doql parser.
- `cmd_doctor(args)` — Run comprehensive project health check.
- `cmd_kiosk(args)` — Manage kiosk appliance installation.
- `cmd_generate(args)` — Generate a single document/artifact.
- `cmd_drift(args)` — Entry point for ``doql drift``.
- `cmd_adopt(args)` — Scan *target* directory (or --from-device), produce app.doql.{css|less|sass}.
- `cmd_quadlet(args)` — Manage Podman Quadlet containers.
- `cmd_deploy(args)` — Deploy project to target environment.
- `cmd_import(args)` — Import a YAML spec file and convert to DOQL format.
- `cmd_run(args)` — Run project locally in dev mode.
- `cmd_publish(args)` — Publish project artifacts to registries.
- `cmd_docs(args)` — Generate documentation site from .doql spec.
- `spec_to_dict(spec)` — Convert DoqlSpec to a cleaned dictionary suitable for YAML/JSON.
- `export_yaml(spec, out)` — Write DoqlSpec as YAML to the given stream.
- `export_yaml_file(spec, path)` — Write DoqlSpec as YAML to a file.
- `export_css(spec, out)` — Write DoqlSpec as .doql.css format.
- `export_less(spec, out)` — Write DoqlSpec as .doql.less format.
- `export_sass(spec, out)` — Write DoqlSpec as .doql.sass format.
- `export_css_file(spec, path, fmt)` — Write DoqlSpec to a CSS-like file. fmt is 'css', 'less', or 'sass'.
- `export_markdown(spec, out)` — Write DoqlSpec as Markdown documentation to the given stream.
- `export_markdown_file(spec, path)` — Write DoqlSpec as Markdown to a file.
- `generate(spec, out)` — Generate documentation files into *out* directory.
- `generate(spec, env_vars, out)` — Generate infra layer files into *out* directory.
- `generate(spec, env_vars, out)` — Generate integration service modules.
- `generate(spec, env_vars, out)` — Generate CI configuration files based on ci_configs or fallback to GitHub Actions.
- `run(spec, out)` — Write Postman collection JSON to the given stream.
- `generate(spec, env_vars, out)` — Generate desktop (Tauri) layer files into *out* directory.
- `generate(spec, env_vars, out, project_root)` — Generate document rendering pipeline into *out* directory.
- `run(spec, out)` — Write TypeScript SDK to the given stream.
- `generate(spec, env_vars, out)` — Generate workflow engine modules.
- `run(ctx, target_env)` — Deploy the built application.
- `generate(spec, env_vars, out)` — Generate i18n translation files.
- `generate(spec, env_vars, out)` — Generate mobile PWA into *out* directory.
- `generate(spec, env_vars, out)` — Generate Vite tooling config into *out* directory.
- `generate(spec, env_vars, out)` — Generate report scripts into *out* directory.
- `write_code_block(content, path)` — Write a code block to file, creating parent directories if needed.
- `generate_file_from_template(template_name, variables, output_path)` — Generate a file from a template with variable substitution.
- `generate(spec, env_vars, out)` — Generate React + Vite + TailwindCSS frontend into *out* directory.
- `sa_type(f)` — Get SQLAlchemy type for a field.
- `py_type(f)` — Get Python/Pydantic type for a field.
- `py_default(f)` — Get default value assignment for a field.
- `safe_name(name)` — Return a valid Python identifier from *name*.
- `snake(name)` — Convert CamelCase to snake_case.
- `gen_alembic_ini()` — Generate alembic.ini configuration file.
- `gen_alembic_env()` — Generate alembic/env.py migration environment.
- `gen_initial_migration(spec)` — Generate initial Alembic migration with all tables.
- `gen_routes(spec)` — Generate CRUD routes for all entities in the spec.
- `gen_schemas(spec)` — Generate Pydantic schemas from DoqlSpec using delegation pattern.
- `gen_auth(spec)` — Generate JWT authentication module.
- `generate(spec, env_vars, out)` — Generate API layer files into *out* directory.
- `export_openapi(spec, out)` — Write OpenAPI 3.1 JSON to the given stream.
- `gen_database(spec, env_vars)` — Generate database.py with SQLAlchemy engine and session.
- `gen_models(spec)` — Generate SQLAlchemy ORM models from DoqlSpec.
- `gen_main(spec)` — Generate FastAPI main application file.
- `gen_requirements(has_auth)` — Generate requirements.txt with pinned dependencies.
- `snake(name)` — Convert CamelCase to snake_case (also handles spaces).
- `kebab(name)` — Convert CamelCase or snake_case to kebab-case.
- `emit_css(spec, output)` — Write *spec* as `app.doql.css` to *output* path.
- `emit_spec(spec, output, fmt)` — Write *spec* to *output* path in given format (css/less/sass).
- `adopt_from_device_to_snapshot(target)` — Scan ``target`` via op3 and return a raw :class:`Snapshot`.
- `adopt_from_device(target)` — Scan ``target`` and return ``.doql.less`` text (optionally writing it).
- `scan_interfaces(root, spec)` — Detect service interfaces from project structure.
- `scan_metadata(root, spec)` — Extract app name, version, domain from config files.
- `scan_databases(root, spec)` — Detect database setup from docker-compose, .env, config files.
- `scan_project(root)` — Scan *root* directory and return a reverse-engineered DoqlSpec.
- `scan_integrations(root, spec)` — Detect external integrations from .env and code.
- `scan_deploy(root, spec)` — Detect deployment infrastructure.
- `scan_workflows(root, spec)` — Promote Makefile / Taskfile.yml targets and Python CLI commands to ``WORKFLOW`` blocks.
- `load_yaml(path)` — Safely load a YAML file.
- `find_compose(root)` — Find docker-compose file.
- `find_dockerfiles(root)` — Find all Dockerfiles.
- `camel_to_kebab(name)` — Convert CamelCase/PascalCase to kebab-case.
- `snake_to_pascal(name)` — Convert snake_case to PascalCase.
- `normalize_python_type(t)` — Normalize Python type annotations to DOQL types.
- `normalize_sqlalchemy_type(t)` — Normalize SQLAlchemy Column types to DOQL types.
- `normalize_sql_type(t)` — Normalize SQL column types to DOQL types using pattern matching.
- `scan_roles(root, spec)` — Detect roles from env vars or code patterns.
- `scan_environments(root, spec)` — Detect environments from .env files and docker-compose variants.
- `scan_entities(root, spec)` — Detect entities from Python models / schemas or SQL files.
- `parse_css_file(path)` — Parse a .doql.css / .doql.less / .doql.sass file into DoqlSpec.
- `parse_css_text(text, format)` — Parse CSS-like DOQL source text into a DoqlSpec.
- `split_blocks(text)` — Split .doql text into (keyword, rest_of_header, body, start_line) blocks.
- `apply_block(spec, keyword, header, body)` — Apply a single parsed block to *spec* using the registry dispatch.
- `extract_val(body, key)` — Extract 'key: value' from an indented block body.
- `extract_list(body, key)` — Extract 'key: [a, b, c]' or 'key: value' from body.
- `extract_yaml_list(body, key)` — Extract YAML-style list items under a key: header.
- `extract_pages(body)` — Extract PAGE definitions from INTERFACE body.
- `extract_entity_fields(body)` — Extract field definitions from ENTITY body.
- `collect_env_refs(text)` — Find all env.VAR_NAME references in the text.
- `register(keyword)` — Decorator to register a block handler for a keyword.
- `get_handler(keyword)` — Get the handler for a keyword, or None if not registered.
- `list_registered()` — Return list of registered keywords.
- `detect_doql_file(root)` — Auto-detect the DOQL spec file in a project directory.
- `parse_file(path)` — Parse a .doql / .doql.css / .doql.less / .doql.sass file into a DoqlSpec.
- `parse_text(text)` — Parse .doql source text into a DoqlSpec (in-memory, no disk I/O).
- `parse_env(path)` — Parse a .env file into a dict. Missing file → empty dict.
- `validate(spec, env_vars, project_root)` — Validate a parsed DoqlSpec against env vars and internal consistency.
- `build_layer_tree(layer_ids)` — Build an :class:`opstree.LayerTree` populated with the given layers.
- `snapshot_to_less(snapshot, scope)` — Render an op3 :class:`Snapshot` as ``.doql.less`` text.
- `scan_interfaces()` — —
- `cmd_drift()` — —
- `cmd_deploy()` — —
- `generate()` — —
- `cmd_doctor()` — —
- `did_open()` — —
- `did_change()` — —
- `did_save()` — —
- `completion()` — —
- `hover()` — —
- `definition()` — —
- `document_symbols()` — —
- `main()` — —
- `determine_regeneration_set()` — —
- `run_generators()` — —
- `cmd_sync()` — —
- `cmd_workspace()` — —
- `register_parser()` — —
- `gen_alembic_ini()` — —
- `gen_alembic_env()` — —
- `gen_initial_migration()` — —
- `gen_schemas()` — —
- `gen_models()` — —
- `scan_deploy()` — —
- `cmd_adopt()` — —
- `spec_section_hashes()` — —
- `read_lockfile()` — —
- `diff_sections()` — —
- `write_lockfile()` — —
- `cmd_generate()` — —
- `cmd_quadlet()` — —
- `cmd_run()` — —
- `scan_workflows()` — —
- `scan_roles()` — —
- `scan_entities()` — —
- `discover_plugins()` — —
- `run_plugins()` — —
- `cmd_validate()` — —
- `cmd_init()` — —
- `cmd_publish()` — —
- `parse_css_file()` — —
- `parse_css_text()` — —
- `pyodide()` — —
- `buildFn()` — —
- `debounceTimer()` — —
- `initElements()` — —
- `isReady()` — —
- `debouncedBuild()` — —
- `executeBuild()` — —
- `r()` — —
- `resp()` — —
- `src()` — —
- `bootPyodide()` — —
- `version()` — —
- `escapeHtml()` — —
- `renderFatal()` — —
- `renderDiagnostics()` — —
- `loc()` — —
- `renderAst()` — —
- `renderEnv()` — —
- `refs()` — —
- `keys()` — —
- `marker()` — —
- `renderFiles()` — —
- `cmd_export()` — —
- `cmd_query()` — —
- `cmd_import()` — —
- `export_css()` — —
- `export_less()` — —
- `export_sass()` — —
- `export_css_file()` — —
- `gen_auth()` — —
- `scan_environments()` — —
- `sa_type()` — —
- `py_type()` — —
- `py_default()` — —
- `safe_name()` — —
- `snake()` — —
- `scan_databases()` — —
- `extract_val()` — —
- `extract_list()` — —
- `extract_yaml_list()` — —
- `extract_pages()` — —
- `extract_entity_fields()` — —
- `collect_env_refs()` — —
- `register()` — —
- `get_handler()` — —
- `list_registered()` — —
- `detect_doql_file()` — —
- `parse_file()` — —
- `parse_text()` — —
- `parse_env()` — —
- `validate()` — —
- `scan_metadata()` — —
- `TAB_NAMES()` — —
- `activateTab()` — —
- `tabFromHash()` — —
- `name()` — —
- `initial()` — —
- `key()` — —
- `updateStats()` — —
- `lines()` — —
- `chars()` — —
- `build_context()` — —
- `load_spec()` — —
- `scaffold_from_template()` — —
- `estimate_file_count()` — —
- `load_yaml()` — —
- `find_compose()` — —
- `find_dockerfiles()` — —
- `camel_to_kebab()` — —
- `snake_to_pascal()` — —
- `normalize_python_type()` — —
- `normalize_sqlalchemy_type()` — —
- `normalize_sql_type()` — —
- `find_intended_file()` — —
- `parse_intended()` — —
- `detect_drift()` — —
- `cmd_render()` — —
- `cmd_plan()` — —
- `adopt_from_device_to_snapshot()` — —
- `adopt_from_device()` — —
- `scan_integrations()` — —
- `split_blocks()` — —
- `apply_block()` — —
- `generate_readme()` — —
- `plugin_generate()` — —
- `import_yaml()` — —
- `import_yaml_text()` — —
- `import_yaml_file()` — —
- `cmd_docs()` — —
- `export_openapi()` — —
- `activate()` — —
- `config()` — —
- `serverPath()` — —
- `deactivate()` — —
- `cmd_kiosk()` — —
- `run()` — —
- `write_code_block()` — —
- `generate_file_from_template()` — —
- `gen_routes()` — —
- `gen_main()` — —
- `gen_requirements()` — —
- `build_layer_tree()` — —
- `snapshot_to_less()` — —
- `create_parser()` — —
- `spec_to_dict()` — —
- `export_yaml()` — —
- `export_yaml_file()` — —
- `export_markdown()` — —
- `export_markdown_file()` — —
- `gen_database()` — —
- `kebab()` — —
- `scan_project()` — —
- `emit_css()` — —
- `emit_spec()` — —
- `get_schema()` — —
- `advance()` — —
- `put()` — —
- `get()` — —
- `delete()` — —
- `presigned_url()` — —
- `send()` — —
- `generate_report()` — —
- `dispatch()` — —
- `convert()` — —
- `detect()` — —
- `extract_page()` — —
- `extract_blocks()` — —
- `less_to_yaml()` — —
- `yaml_to_less()` — —
- `stage()` — —
- `dir()` — —
- `cleanWs()` — —
- `test_doql_vs_less_regression()` — —
- `Pyodide()` — —
- `tests()` — —
- `should_generate_interface()` — —
- `run_core_generators()` — —
- `run_document_generators()` — —
- `run_report_generators()` — —
- `run_i18n_generators()` — —
- `run_integration_generators()` — —
- `run_workflow_generators()` — —
- `run_ci_generator()` — —
- `run_vite_generator()` — —
- `cmd_build()` — —
- `build()` — —
- `check_api()` — —
- `check_web()` — —
- `check_mobile()` — —
- `check_desktop()` — —
- `check_infra()` — —
- `process_example()` — —
- `render_text()` — —
- `render_json()` — —
- `test_adopt_from_device_returns_less_text()` — —
- `test_adopt_from_device_writes_output()` — —
- `test_adopt_from_device_to_snapshot_contains_layer_data()` — —
- `test_adopt_output_is_parsable_by_doql()` — —
- `test_adopt_from_rpi5_podman_quadlet_returns_less_text()` — —
- `test_adopt_from_rpi5_to_snapshot_contains_all_services()` — —
- `test_adopt_from_rpi5_to_snapshot_contains_all_containers()` — —
- `test_adopt_from_rpi5_output_is_parsable_by_doql()` — —
- `test_cmd_adopt_from_device_writes_file()` — —
- `test_cmd_adopt_rejects_non_less_format()` — —
- `test_cmd_adopt_without_target_or_device_errors()` — —
- `test_cmd_adopt_refuses_to_overwrite()` — —
- `test_scan_device_writes_app_doql_less_in_root()` — —
- `test_scan_device_honours_global_file_flag()` — —
- `test_scan_device_refuses_to_overwrite_without_force()` — —
- `test_scan_device_force_overwrites()` — —
- `test_cmd_build_from_device_runs_full_pipeline()` — —
- `test_cmd_build_refuses_to_clobber_without_force()` — —
- `test_cmd_build_without_from_device_skips_scan()` — —
- `test_parse_intended_attaches_source_path()` — —
- `test_parse_intended_missing_file()` — —
- `test_detect_drift_no_changes()` — —
- `test_detect_drift_service_state_mismatch()` — —
- `test_detect_drift_missing_file_raises()` — —
- `test_cmd_drift_returns_drift_exit_code()` — —
- `test_cmd_drift_json_output_is_valid()` — —
- `test_cmd_drift_missing_from_device()` — —
- `test_cmd_drift_missing_file()` — —
- `test_cmd_drift_unsupported_format_gives_actionable_hint()` — —
- `test_cmd_drift_explicit_missing_file()` — —
- `test_cmd_drift_no_drift_exit_code_zero()` — —
- `test_op3_importable()` — —
- `test_op3_enabled_reads_env()` — —
- `test_should_use_op3_requires_both()` — —
- `test_require_op3_noop_when_available()` — —
- `test_build_layer_tree_defaults()` — —
- `test_build_layer_tree_explicit_leaf_pulls_deps()` — —
- `test_build_layer_tree_rejects_unknown()` — —
- `test_scanner_runs_against_mock_context()` — —
- `test_snapshot_to_less_produces_parsable_less()` — —
- `serve()` — —
- `step()` — —
- `test_jwt_secret_does_not_crash_renderer()` — —
- `test_pydantic_dtos_are_excluded_from_entities()` — —
- `test_generic_db_service_name_is_normalised()` — —
- `test_fastapi_dependency_alone_does_not_create_api_interface()` — —
- `test_fastapi_with_main_py_creates_api()` — —
- `test_api_entry_point_in_scripts_creates_api()` — —
- `test_cmd_adopt_returns_zero_on_success()` — —
- `test_cmd_adopt_returns_nonzero_on_render_failure()` — —
- `test_cmd_adopt_refuses_to_overwrite_without_force()` — —
- `test_cmd_adopt_rejects_non_directory()` — —
- `test_makefile_targets_become_workflows()` — —
- `test_makefile_workflows_round_trip_to_css()` — —
- `test_taskfile_yml_tasks_become_workflows()` — —
- `test_dependency_only_targets_emit_depend_steps()` — —
- `test_empty_target_without_deps_is_skipped()` — —
- `test_makefile_variable_assignments_are_not_workflows()` — —
- `test_workflows_are_deduplicated_across_makefile_and_taskfile()` — —
- `test_adopt_e2e_real_project_oqlos()` — —
- `test_discover_subprojects()` — —
- `test_click_not_inferred_from_comment_or_changelog()` — —
- `test_fastapi_detected_from_server_py()` — —
- `test_css_parse_minimal()` — —
- `test_css_parse_entity()` — —
- `test_css_parse_interface()` — —
- `test_css_parse_role()` — —
- `test_css_parse_deploy()` — —
- `test_less_variable_expansion()` — —
- `test_sass_basic_parsing()` — —
- `test_parses_css_example_file()` — —
- `test_detect_doql_file_prefers_less()` — —
- `test_detect_doql_file_prefers_sass()` — —
- `test_detect_doql_file_falls_back_to_classic()` — —
- `test_iot_fleet_less_has_entities()` — —
- `test_notes_app_sass_has_all_interfaces()` — —
- `test_css_parse_error_has_line_info()` — —
- `test_css_unknown_selector_gives_warning()` — —
- `test_less_syntax_error_recovery()` — —
- `test_css_parse_project_blocks()` — —
- `sample_spec()` — —
- `test_yaml_roundtrip_real_example()` — —
- `test_css_export_real_example()` — —
- `test_markdown_export_real_example()` — —
- `test_css_export_project_blocks()` — —
- `test_css_exporter_shim_re_exports_public_api()` — —
- `test_css_exporter_shim_re_exports_renderers()` — —
- `test_css_exporter_shim_re_exports_format_helpers()` — —
- `test_markdown_exporter_shim_re_exports_public_api()` — —
- `test_markdown_exporter_shim_re_exports_writers()` — —
- `test_markdown_exporter_shim_re_exports_helpers()` — —
- `test_css_shim_roundtrip_matches_direct_subpackage()` — —
- `test_build_example()` — —
- `test_init_and_build_template()` — —
- `test_sync_no_changes_is_noop()` — —
- `test_list_templates_includes_all()` — —
- `test_parse_doc_handles_valid_input()` — —
- `test_parse_doc_returns_none_on_crash()` — —
- `test_find_line_col_finds_needle()` — —
- `test_word_at_extracts_word()` — —
- `test_diagnostics_on_asset_management_example()` — —
- `test_keyword_completion_includes_common_top_level()` — —
- `test_parse_text_minimal()` — —
- `test_parse_text_full_entity()` — —
- `test_parse_text_languages_list()` — —
- `test_parse_text_workflow_with_schedule_and_inline_comment()` — —
- `test_parse_text_recovers_from_broken_block()` — —
- `test_parse_errors_is_a_list()` — —
- `test_parses_example_file()` — —
- `test_asset_management_entities()` — —
- `test_validate_detects_missing_env_ref()` — —
- `test_validation_issue_has_line_field()` — —
- `test_validate_detects_dangling_entity_ref()` — —
- `test_calibration_lab_has_no_dangling_refs()` — —
- `test_deprecated_docker_compose_strategy_warns()` — —
- `test_deprecated_quadlet_strategy_warns()` — —
- `test_canonical_strategy_no_warning()` — —
- `test_css_parser_cold_start_under_threshold()` — —
- `test_less_parser_variable_resolution_under_threshold()` — —
- `test_real_example_parse_under_threshold()` — —
- `test_css_vs_classic_parse_time_parity()` — —
- `test_large_file_parse_under_threshold()` — —
- `test_entrypoint_discovery_finds_all_four()` — —
- `test_doql_plugins_module_import()` — —
- `test_iso17025_uncertainty_budget_numerical()` — —
- `test_iso17025_drift_monitor_detects_stable()` — —
- `test_iso17025_drift_monitor_flags_excessive_drift()` — —
- `test_fleet_ota_canary_advances_on_success()` — —
- `test_gxp_audit_log_hash_is_deterministic()` — —
- `test_api_boot_and_health()` — —
- `test_build_produces_expected_targets()` — —


## Project Structure

📄 `.redeploy.state.infra-local-9dd2f59b`
📄 `CHANGELOG` (1 functions)
📄 `GLOSSARY`
📄 `Jenkinsfile` (7 functions)
📄 `OQLOS-REQUIREMENTS` (10 functions, 9 classes)
📄 `PARSER_AUDIT`
📄 `README`
📄 `ROADMAP`
📄 `SPEC`
📄 `SUMD` (800 functions, 1 classes)
📄 `SUMR` (19 functions, 1 classes)
📄 `TODO` (11 functions, 4 classes)
📄 `TODO.01-doql-format-migration-analysis`
📄 `TODO.02-doql-css-iot-fleet-example`
📄 `TODO.03-doql-less-calibration-lab-example`
📄 `TODO.04-doql-sass-notes-app-example`
📄 `TODO.05-doql-migration-guide`
📄 `TODO.README`
📄 `Taskfile`
📄 `Taskfile.testql`
📄 `analysis-20260421.doql_playground.analysis.toon`
📄 `analysis-20260421.doql_playground.context`
📄 `analysis.doql_playground.analysis.toon`
📄 `articles.01-oqlos-status-2026-q2`
📄 `articles.02-testql-status-2026-q2`
📄 `articles.03-saas-www-status-2026-q2`
📄 `articles.04-doql-ogloszenie`
📄 `articles.05-wizja-ekosystemu-oqlos`
📄 `articles.06-doql-v02-dokumenty-kiosk`
📄 `articles.README`
📄 `code2llm_output.doql_playground.analysis.toon`
📄 `code2llm_output.doql_playground.context`
📄 `code2llm_output.doql_playground.evolution.toon`
📄 `code2llm_output.doql_playground.flow.toon`
📄 `code2llm_output.plugins.context`
📄 `code2llm_output.plugins.evolution.toon`
📄 `code2llm_output.plugins.flow.toon`
📄 `docs.README` (1 functions)
📄 `docs.doql_playground.analysis.toon`
📄 `docs.doql_playground.context`
📄 `docs.doql_playground.evolution.toon`
📄 `docs.plugins.context`
📄 `docs.refactoring-plan` (4 functions)
📦 `doql`
📦 `doql.adopt`
📄 `doql.adopt.device_scanner` (3 functions)
📄 `doql.adopt.emitter` (2 functions)
📦 `doql.adopt.scanner` (1 functions)
📄 `doql.adopt.scanner.databases` (4 functions)
📄 `doql.adopt.scanner.deploy` (9 functions)
📄 `doql.adopt.scanner.entities` (11 functions)
📄 `doql.adopt.scanner.environments` (6 functions)
📄 `doql.adopt.scanner.integrations` (1 functions)
📄 `doql.adopt.scanner.interfaces` (16 functions)
📄 `doql.adopt.scanner.metadata` (8 functions)
📄 `doql.adopt.scanner.roles` (2 functions)
📄 `doql.adopt.scanner.utils` (8 functions)
📄 `doql.adopt.scanner.workflows` (15 functions)
📦 `doql.cli`
📄 `doql.cli.__main__`
📦 `doql.cli.commands`
📄 `doql.cli.commands.adopt` (11 functions)
📄 `doql.cli.commands.deploy` (4 functions)
📄 `doql.cli.commands.docs` (1 functions)
📄 `doql.cli.commands.doctor` (20 functions, 2 classes)
📄 `doql.cli.commands.drift` (6 functions)
📄 `doql.cli.commands.export` (1 functions)
📄 `doql.cli.commands.generate` (1 functions)
📄 `doql.cli.commands.import_cmd` (1 functions)
📄 `doql.cli.commands.init` (1 functions)
📄 `doql.cli.commands.kiosk` (1 functions)
📄 `doql.cli.commands.plan` (10 functions)
📄 `doql.cli.commands.publish` (5 functions)
📄 `doql.cli.commands.quadlet` (3 functions)
📄 `doql.cli.commands.query` (1 functions)
📄 `doql.cli.commands.render` (1 functions)
📄 `doql.cli.commands.run` (7 functions)
📄 `doql.cli.commands.validate` (2 functions)
📄 `doql.cli.commands.workspace` (25 functions, 1 classes)
📄 `doql.cli.context` (4 functions, 1 classes)
📄 `doql.cli.lockfile` (5 functions)
📄 `doql.cli.main` (2 functions)
📄 `doql.cli.sync` (4 functions)
📦 `doql.drift`
📄 `doql.drift.detector` (4 functions)
📦 `doql.exporters`
📦 `doql.exporters.css` (9 functions)
📄 `doql.exporters.css.format_convert` (3 functions)
📄 `doql.exporters.css.helpers` (3 functions)
📄 `doql.exporters.css.renderers` (19 functions)
📄 `doql.exporters.css_exporter`
📦 `doql.exporters.markdown` (2 functions)
📄 `doql.exporters.markdown.sections` (8 functions)
📄 `doql.exporters.markdown.writers` (11 functions)
📄 `doql.exporters.markdown_exporter`
📄 `doql.exporters.yaml_exporter` (3 functions)
📦 `doql.generators`
📦 `doql.generators.api_gen` (5 functions)
📄 `doql.generators.api_gen.alembic` (4 functions)
📄 `doql.generators.api_gen.auth` (1 functions)
📄 `doql.generators.api_gen.common` (5 functions)
📄 `doql.generators.api_gen.database` (1 functions)
📄 `doql.generators.api_gen.main` (2 functions)
📄 `doql.generators.api_gen.models` (2 functions)
📄 `doql.generators.api_gen.routes` (7 functions)
📄 `doql.generators.api_gen.schemas` (5 functions)
📄 `doql.generators.ci_gen` (4 functions)
📄 `doql.generators.deploy` (1 functions)
📄 `doql.generators.desktop_gen` (7 functions)
📄 `doql.generators.docs_gen` (1 functions)
📄 `doql.generators.document_gen` (4 functions)
📄 `doql.generators.export_postman` (1 functions)
📄 `doql.generators.export_ts_sdk` (1 functions)
📄 `doql.generators.i18n_gen` (3 functions)
📄 `doql.generators.infra_gen` (10 functions)
📄 `doql.generators.integrations_gen` (11 functions)
📄 `doql.generators.mobile_gen` (8 functions)
📄 `doql.generators.report_gen` (2 functions)
📄 `doql.generators.utils.codegen` (2 functions)
📄 `doql.generators.vite_gen` (5 functions)
📦 `doql.generators.web_gen` (8 functions)
📄 `doql.generators.web_gen.common`
📄 `doql.generators.web_gen.components` (1 functions)
📄 `doql.generators.web_gen.config` (6 functions)
📄 `doql.generators.web_gen.core` (3 functions)
📄 `doql.generators.web_gen.pages` (4 functions)
📄 `doql.generators.web_gen.pwa` (3 functions)
📄 `doql.generators.web_gen.router` (1 functions)
📄 `doql.generators.workflow_gen` (8 functions)
📦 `doql.importers`
📄 `doql.importers.yaml_importer` (22 functions)
📦 `doql.integrations`
📄 `doql.integrations.op3_bridge` (2 functions)
📄 `doql.lsp_server` (15 functions)
📄 `doql.parser`
📦 `doql.parsers` (5 functions)
📄 `doql.parsers.blocks` (2 functions)
📄 `doql.parsers.css_mappers` (28 functions)
📄 `doql.parsers.css_parser` (5 functions)
📄 `doql.parsers.css_tokenizer` (5 functions)
📄 `doql.parsers.css_transformers` (14 functions)
📄 `doql.parsers.css_utils` (4 functions, 2 classes)
📄 `doql.parsers.extractors` (14 functions)
📄 `doql.parsers.models` (24 classes)
📄 `doql.parsers.registry` (30 functions)
📄 `doql.parsers.validators` (11 functions)
📄 `doql.plugins` (4 functions, 1 classes)
📄 `doql.scaffolds.calibration-lab.app`
📄 `doql.scaffolds.iot-fleet.app`
📄 `doql.scaffolds.minimal.app`
📄 `doql.scaffolds.saas-multi-tenant.app`
📦 `doql.utils`
📄 `doql.utils.clean` (1 functions)
📄 `doql.utils.naming` (2 functions)
📄 `examples.EXAMPLES-TEST-REPORT`
📄 `examples.SUMD`
📄 `examples.SUMR`
📄 `examples.Taskfile`
📄 `examples.asset-management.README`
📄 `examples.asset-management.Taskfile`
📄 `examples.asset-management.app`
📄 `examples.asset-management.pyqual`
📄 `examples.blog-cms.README`
📄 `examples.blog-cms.Taskfile`
📄 `examples.blog-cms.app`
📄 `examples.blog-cms.docs.index`
📄 `examples.calibration-lab.README`
📄 `examples.calibration-lab.Taskfile`
📄 `examples.calibration-lab.app`
📄 `examples.crm-contacts.README`
📄 `examples.crm-contacts.Taskfile`
📄 `examples.crm-contacts.app`
📄 `examples.document-generator.README`
📄 `examples.document-generator.Taskfile`
📄 `examples.document-generator.app`
📄 `examples.document-generator.data.customers`
📄 `examples.document-generator.data.organization`
📄 `examples.e-commerce-shop.README`
📄 `examples.e-commerce-shop.Taskfile`
📄 `examples.e-commerce-shop.app`
📄 `examples.iot-fleet.README`
📄 `examples.iot-fleet.Taskfile`
📄 `examples.iot-fleet.app`
📄 `examples.kiosk-station.README`
📄 `examples.kiosk-station.Taskfile`
📄 `examples.kiosk-station.app`
📄 `examples.project.map.toon`
📄 `examples.sumd`
📄 `examples.todo-pwa.README`
📄 `examples.todo-pwa.Taskfile`
📄 `examples.todo-pwa.app`
📄 `goal`
📄 `playground.README` (1 functions)
📄 `playground.app` (9 functions)
📄 `playground.pyodide-bridge` (15 functions)
📄 `playground.renderers` (10 functions)
📄 `playground.serve`
📄 `plugins.doql-plugin-erp.README`
📄 `plugins.doql-plugin-erp.SUMD` (6 functions)
📄 `plugins.doql-plugin-erp.SUMR`
📦 `plugins.doql-plugin-erp.doql_plugin_erp` (6 functions)
📄 `plugins.doql-plugin-erp.project.map.toon` (6 functions)
📄 `plugins.doql-plugin-erp.pyproject`
📄 `plugins.doql-plugin-erp.sumd`
📄 `plugins.doql-plugin-fleet.README`
📄 `plugins.doql-plugin-fleet.SUMD` (7 functions)
📄 `plugins.doql-plugin-fleet.SUMR`
📦 `plugins.doql-plugin-fleet.doql_plugin_fleet` (2 functions)
📄 `plugins.doql-plugin-fleet.doql_plugin_fleet.device_registry` (1 functions)
📄 `plugins.doql-plugin-fleet.doql_plugin_fleet.metrics` (1 functions)
📄 `plugins.doql-plugin-fleet.doql_plugin_fleet.migration` (1 functions)
📄 `plugins.doql-plugin-fleet.doql_plugin_fleet.ota` (1 functions)
📄 `plugins.doql-plugin-fleet.doql_plugin_fleet.tenant` (1 functions)
📄 `plugins.doql-plugin-fleet.project.map.toon` (7 functions)
📄 `plugins.doql-plugin-fleet.pyproject`
📄 `plugins.doql-plugin-fleet.sumd`
📄 `plugins.doql-plugin-gxp.README`
📄 `plugins.doql-plugin-gxp.SUMD` (6 functions)
📄 `plugins.doql-plugin-gxp.SUMR`
📦 `plugins.doql-plugin-gxp.doql_plugin_gxp` (6 functions)
📄 `plugins.doql-plugin-gxp.project.map.toon` (6 functions)
📄 `plugins.doql-plugin-gxp.pyproject`
📄 `plugins.doql-plugin-gxp.sumd`
📄 `plugins.doql-plugin-iso17025.README`
📄 `plugins.doql-plugin-iso17025.SUMD` (6 functions)
📄 `plugins.doql-plugin-iso17025.SUMR`
📦 `plugins.doql-plugin-iso17025.doql_plugin_iso17025` (1 functions)
📄 `plugins.doql-plugin-iso17025.doql_plugin_iso17025.certificate` (1 functions)
📄 `plugins.doql-plugin-iso17025.doql_plugin_iso17025.drift_monitor` (1 functions)
📄 `plugins.doql-plugin-iso17025.doql_plugin_iso17025.migration` (1 functions)
📄 `plugins.doql-plugin-iso17025.doql_plugin_iso17025.traceability` (1 functions)
📄 `plugins.doql-plugin-iso17025.doql_plugin_iso17025.uncertainty` (1 functions)
📄 `plugins.doql-plugin-iso17025.project.map.toon` (6 functions)
📄 `plugins.doql-plugin-iso17025.pyproject`
📄 `plugins.doql-plugin-iso17025.sumd`
📄 `plugins.doql-plugin-shared.SUMD` (2 functions)
📄 `plugins.doql-plugin-shared.SUMR`
📦 `plugins.doql-plugin-shared.doql_plugin_shared`
📄 `plugins.doql-plugin-shared.doql_plugin_shared.base` (1 functions)
📄 `plugins.doql-plugin-shared.doql_plugin_shared.readme` (1 functions)
📄 `plugins.doql-plugin-shared.project.map.toon` (2 functions)
📄 `plugins.doql-plugin-shared.pyproject`
📄 `plugins.doql-plugin-shared.sumd`
📄 `project`
📄 `project.README`
📄 `project.analysis.toon`
📄 `project.calls`
📄 `project.calls.toon`
📄 `project.context`
📄 `project.duplication.toon`
📄 `project.evolution.toon`
📄 `project.map.toon` (2307 functions)
📄 `project.project.toon`
📄 `project.prompt`
📄 `project.validation.toon`
📄 `pyproject`
📄 `pyqual`
📄 `test_all_desktop`
📄 `test_playbook`
📄 `testql-scenarios.generated-api-integration.testql.toon`
📄 `testql-scenarios.generated-api-smoke.testql.toon`
📄 `testql-scenarios.generated-from-pytests.testql.toon`
📄 `tree`
📄 `vscode-doql.README`
📄 `vscode-doql.SUMD`
📄 `vscode-doql.SUMR`
📄 `vscode-doql.language-configuration`
📄 `vscode-doql.package`
📄 `vscode-doql.project.map.toon`
📄 `vscode-doql.src.extension` (4 functions)
📄 `vscode-doql.sumd`
📄 `vscode-doql.syntaxes.doql-css.tmLanguage`
📄 `vscode-doql.syntaxes.doql.tmLanguage`
📄 `vscode-doql.tsconfig`

## Requirements

- Python >= >=3.10
- click >=8.1- pydantic >=2.0- pyyaml >=6.0- jinja2 >=3.1- rich >=13.0- httpx >=0.25- goal >=2.1.0- costs >=0.1.20- pfix >=0.1.60- tomli >=2.0; python_version < '3.11'- testql >=0.1.1

## Contributing

**Contributors:**
- Tom Sapletta

We welcome contributions! Open an issue or pull request to get started.
### Development Setup

```bash
# Clone the repository
git clone https://github.com/oqlos/doql
cd doql

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## Documentation

- 💡 [Examples](./examples) — Usage examples and code samples

### Generated Files

| Output | Description | Link |
|--------|-------------|------|
| `README.md` | Project overview (this file) | — |
| `examples` | Usage examples and code samples | [View](./examples) |

<!-- code2docs:end -->