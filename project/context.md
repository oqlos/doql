# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/oqlos/doql
- **Primary Language**: shell
- **Languages**: shell: 2, python: 1
- **Analysis Mode**: static
- **Total Functions**: 14
- **Total Classes**: 1
- **Modules**: 3
- **Entry Points**: 9

## Architecture by Module

### doql.cli
- **Functions**: 14
- **Classes**: 1
- **File**: `cli.py`

## Key Entry Points

Main execution flows into the system:

### doql.cli.main
- **Calls**: argparse.ArgumentParser, p.add_argument, p.add_argument, p.add_argument, p.add_subparsers, sub.add_parser, s.add_argument, s.add_argument

### doql.cli.cmd_plan
- **Calls**: doql.cli._build_context, doql_parser.parse_file, print, print, print, print, print, print

### doql.cli.cmd_init
- **Calls**: pathlib.Path, target.exists, print, doql.cli._scaffold_from_template, print, print, print, print

### doql.cli.cmd_validate
- **Calls**: doql.cli._build_context, print, doql_parser.parse_file, doql_parser.parse_env, doql_parser.validate, print, print, any

### doql.cli.cmd_export
- **Calls**: doql.cli._build_context, doql_parser.parse_file, api_gen.export_openapi, export_postman.run, export_ts_sdk.run, print

### doql.cli.cmd_run
- **Calls**: doql.cli._build_context, subprocess.call, compose.exists, print, str

### doql.cli.cmd_docs
- **Calls**: doql.cli._build_context, doql_parser.parse_file, docs_gen.generate, print

### doql.cli.cmd_deploy
- **Calls**: doql.cli._build_context, print, deploy.run

### doql.cli.cmd_sync
- **Calls**: doql.cli._build_context, print, doql.cli.cmd_build

## Process Flows

Key execution flows identified:

### Flow 1: main
```
main [doql.cli]
```

### Flow 2: cmd_plan
```
cmd_plan [doql.cli]
  └─> _build_context
```

### Flow 3: cmd_init
```
cmd_init [doql.cli]
  └─> _scaffold_from_template
```

### Flow 4: cmd_validate
```
cmd_validate [doql.cli]
  └─> _build_context
```

### Flow 5: cmd_export
```
cmd_export [doql.cli]
  └─> _build_context
```

### Flow 6: cmd_run
```
cmd_run [doql.cli]
  └─> _build_context
```

### Flow 7: cmd_docs
```
cmd_docs [doql.cli]
  └─> _build_context
```

### Flow 8: cmd_deploy
```
cmd_deploy [doql.cli]
  └─> _build_context
```

### Flow 9: cmd_sync
```
cmd_sync [doql.cli]
  └─> _build_context
  └─> cmd_build
      └─> _build_context
```

## Key Classes

### doql.cli.BuildContext
- **Methods**: 0

## Data Transformation Functions

Key functions that process and transform data:

### doql.cli.cmd_validate
- **Output to**: doql.cli._build_context, print, doql_parser.parse_file, doql_parser.parse_env, doql_parser.validate

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `doql.cli.main` - 30 calls
- `doql.cli.cmd_plan` - 20 calls
- `doql.cli.cmd_build` - 14 calls
- `doql.cli.cmd_init` - 11 calls
- `doql.cli.cmd_validate` - 9 calls
- `doql.cli.cmd_export` - 6 calls
- `doql.cli.cmd_run` - 5 calls
- `doql.cli.cmd_docs` - 4 calls
- `doql.cli.cmd_deploy` - 3 calls
- `doql.cli.cmd_sync` - 3 calls

## System Interactions

How components interact:

```mermaid
graph TD
    main --> ArgumentParser
    main --> add_argument
    main --> add_subparsers
    cmd_plan --> _build_context
    cmd_plan --> parse_file
    cmd_plan --> print
    cmd_init --> Path
    cmd_init --> exists
    cmd_init --> print
    cmd_init --> _scaffold_from_templ
    cmd_validate --> _build_context
    cmd_validate --> print
    cmd_validate --> parse_file
    cmd_validate --> parse_env
    cmd_validate --> validate
    cmd_export --> _build_context
    cmd_export --> parse_file
    cmd_export --> export_openapi
    cmd_export --> run
    cmd_run --> _build_context
    cmd_run --> call
    cmd_run --> exists
    cmd_run --> print
    cmd_run --> str
    cmd_docs --> _build_context
    cmd_docs --> parse_file
    cmd_docs --> generate
    cmd_docs --> print
    cmd_deploy --> _build_context
    cmd_deploy --> print
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.