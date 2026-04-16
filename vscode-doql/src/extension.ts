import * as path from "path";
import { workspace, ExtensionContext, window } from "vscode";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  TransportKind,
} from "vscode-languageclient/node";

let client: LanguageClient;

export function activate(context: ExtensionContext) {
  const config = workspace.getConfiguration("doql");
  const serverPath = config.get<string>("serverPath", "doql-lsp");

  const serverOptions: ServerOptions = {
    command: serverPath,
    args: [],
    transport: TransportKind.stdio,
  };

  const clientOptions: LanguageClientOptions = {
    documentSelector: [
      { scheme: "file", language: "doql" },
      { scheme: "untitled", language: "doql" },
    ],
    synchronize: {
      fileEvents: workspace.createFileSystemWatcher("**/.env"),
    },
    outputChannel: window.createOutputChannel("doql Language Server"),
  };

  client = new LanguageClient(
    "doql",
    "doql Language Server",
    serverOptions,
    clientOptions
  );

  client.start().catch((err) => {
    window.showErrorMessage(
      `Failed to start doql-lsp (${serverPath}): ${err}. ` +
        `Install with: pip install 'doql[lsp]'`
    );
  });
}

export function deactivate(): Thenable<void> | undefined {
  if (!client) return undefined;
  return client.stop();
}
