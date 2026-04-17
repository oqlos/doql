import { useState, useEffect, createContext, useContext } from "react";

type Translations = Record<string, string>;
const LANGUAGES = ["en", "pl"];
const I18nContext = createContext<{ t: (key: string) => string; lang: string; setLang: (l: string) => void }>(
  { t: (k) => k, lang: "en", setLang: () => {} }
);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLang] = useState("en");
  const [translations, setTranslations] = useState<Translations>({});

  useEffect(() => {
    fetch(`/i18n/${lang}.json`)
      .then(r => r.json())
      .then(setTranslations)
      .catch(() => {});
  }, [lang]);

  const t = (key: string) => translations[key] || key;

  return (
    <I18nContext.Provider value={{ t, lang, setLang }}>
      {children}
    </I18nContext.Provider>
  );
}

export const useTranslation = () => useContext(I18nContext);
export const AVAILABLE_LANGUAGES = ["en", "pl"];
