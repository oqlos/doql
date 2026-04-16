# doql — VS Code Extension

Language support for `.doql` files:

- **Syntax highlighting** (TextMate grammar)
- **Diagnostics** via `doql-lsp` language server (errors + warnings)
- **Hover** — entity/field info, keyword help
- **Go-to-definition** — jump to `ENTITY` declarations from `ref:` fields
- **Completions** — keywords, entity names, field attributes
- **Document symbols** — outline view shows entities, interfaces, workflows

## Requirements

Install the doql LSP server globally:

```bash
pip install 'doql[lsp]'
```

This provides the `doql-lsp` binary that the extension spawns.

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `doql.serverPath` | `doql-lsp` | Path to the doql-lsp executable |
| `doql.trace.server` | `off` | LSP trace level (`off`, `messages`, `verbose`) |

## Build & install locally

```bash
cd vscode-doql
npm install
npm run compile
# Package as .vsix:
npx @vscode/vsce package
# Install:
code --install-extension vscode-doql-0.1.0.vsix
```

## Development

```bash
npm run watch   # in one terminal
# Press F5 in VS Code to launch Extension Development Host
```
