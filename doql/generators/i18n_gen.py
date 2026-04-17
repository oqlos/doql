"""Generate i18n translation files from DoqlSpec.

Produces:
  build/i18n/
  ├── en.json
  ├── pl.json
  ├── de.json   (etc., per language in spec)
  └── README.md

Each JSON file contains auto-generated keys for:
  - Entity names (singular + plural)
  - Field labels
  - Page titles
  - Common UI strings
"""
from __future__ import annotations

import json
import pathlib

from ..parser import DoqlSpec, Entity
from ..utils.naming import snake as _snake


def _humanize(name: str) -> str:
    return _snake(name).replace("_", " ").title()


# Basic translations for common UI strings
_COMMON: dict[str, dict[str, str]] = {
    "en": {
        "app.dashboard": "Dashboard",
        "app.settings": "Settings",
        "app.logout": "Log out",
        "app.login": "Log in",
        "app.register": "Register",
        "app.save": "Save",
        "app.cancel": "Cancel",
        "app.delete": "Delete",
        "app.edit": "Edit",
        "app.create": "Create new",
        "app.search": "Search…",
        "app.no_results": "No results found",
        "app.confirm_delete": "Are you sure you want to delete this?",
        "app.loading": "Loading…",
        "app.error": "An error occurred",
    },
    "pl": {
        "app.dashboard": "Panel główny",
        "app.settings": "Ustawienia",
        "app.logout": "Wyloguj",
        "app.login": "Zaloguj",
        "app.register": "Rejestracja",
        "app.save": "Zapisz",
        "app.cancel": "Anuluj",
        "app.delete": "Usuń",
        "app.edit": "Edytuj",
        "app.create": "Utwórz nowy",
        "app.search": "Szukaj…",
        "app.no_results": "Brak wyników",
        "app.confirm_delete": "Czy na pewno chcesz usunąć?",
        "app.loading": "Ładowanie…",
        "app.error": "Wystąpił błąd",
    },
    "de": {
        "app.dashboard": "Übersicht",
        "app.settings": "Einstellungen",
        "app.logout": "Abmelden",
        "app.login": "Anmelden",
        "app.register": "Registrieren",
        "app.save": "Speichern",
        "app.cancel": "Abbrechen",
        "app.delete": "Löschen",
        "app.edit": "Bearbeiten",
        "app.create": "Neu erstellen",
        "app.search": "Suchen…",
        "app.no_results": "Keine Ergebnisse",
        "app.confirm_delete": "Möchten Sie dies wirklich löschen?",
        "app.loading": "Wird geladen…",
        "app.error": "Ein Fehler ist aufgetreten",
    },
}


def _gen_translations(spec: DoqlSpec, lang: str) -> dict:
    """Generate translation dict for a given language."""
    t: dict[str, str] = {}

    # Common UI strings
    common = _COMMON.get(lang, _COMMON["en"])
    t.update(common)

    # Entity translations
    for ent in spec.entities:
        key = _snake(ent.name)
        t[f"entity.{key}.name"] = _humanize(ent.name)
        t[f"entity.{key}.plural"] = _humanize(ent.name) + "s"
        for f in ent.fields:
            t[f"entity.{key}.field.{f.name}"] = _humanize(f.name)

    # Page translations
    for iface in spec.interfaces:
        for page in iface.pages:
            t[f"page.{page.name}.title"] = _humanize(page.name)

    # Workflow translations
    for wf in spec.workflows:
        t[f"workflow.{wf.name}.name"] = _humanize(wf.name)

    return t


def generate(spec: DoqlSpec, env_vars: dict[str, str], out: pathlib.Path) -> None:
    """Generate i18n translation files."""
    languages = spec.languages if spec.languages and spec.languages != ["(default)"] else ["en"]

    for lang in languages:
        translations = _gen_translations(spec, lang)
        path = out / f"{lang}.json"
        path.write_text(json.dumps(translations, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"    → i18n/{lang}.json ({len(translations)} keys)")

    # i18n hook for React (useTranslation)
    hook = (
        'import { useState, useEffect, createContext, useContext } from "react";\n'
        '\n'
        'type Translations = Record<string, string>;\n'
        f'const LANGUAGES = {json.dumps(languages)};\n'
        'const I18nContext = createContext<{ t: (key: string) => string; lang: string; setLang: (l: string) => void }>(\n'
        '  { t: (k) => k, lang: "en", setLang: () => {} }\n'
        ');\n'
        '\n'
        'export function I18nProvider({ children }: { children: React.ReactNode }) {\n'
        f'  const [lang, setLang] = useState("{languages[0]}");\n'
        '  const [translations, setTranslations] = useState<Translations>({});\n'
        '\n'
        '  useEffect(() => {\n'
        '    fetch(`/i18n/${lang}.json`)\n'
        '      .then(r => r.json())\n'
        '      .then(setTranslations)\n'
        '      .catch(() => {});\n'
        '  }, [lang]);\n'
        '\n'
        '  const t = (key: string) => translations[key] || key;\n'
        '\n'
        '  return (\n'
        '    <I18nContext.Provider value={{ t, lang, setLang }}>\n'
        '      {children}\n'
        '    </I18nContext.Provider>\n'
        '  );\n'
        '}\n'
        '\n'
        'export const useTranslation = () => useContext(I18nContext);\n'
        f'export const AVAILABLE_LANGUAGES = {json.dumps(languages)};\n'
    )
    (out / "useTranslation.tsx").write_text(hook, encoding="utf-8")
    print(f"    → i18n/useTranslation.tsx")

    (out / "README.md").write_text(
        f"# {spec.app_name} — i18n\n\n"
        f"Languages: {', '.join(languages)}\n\n"
        f"## Usage (React)\n\n"
        f"```tsx\nimport {{ useTranslation }} from '../i18n/useTranslation';\n"
        f"const {{ t, lang, setLang }} = useTranslation();\n"
        f"<h1>{{t('app.dashboard')}}</h1>\n```\n",
        encoding="utf-8",
    )
    print(f"    → i18n/README.md")
