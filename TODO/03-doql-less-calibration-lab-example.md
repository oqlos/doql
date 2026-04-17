---
title: "Format doql.less — zmienne i zagnieżdżenia w konfiguracji DOQL"
date: 2026-04-17
categories: [doql, oqlos, less, dsl]
tags: [DOQL, LESS, IoT, Calibration, OqlOS, Softreck]
status: publish
excerpt: "Format .doql.less rozszerza CSS-like DOQL o zmienne (@var), zagnieżdżenia i operacje. Idealny dla projektów z wieloma środowiskami (dev/staging/prod) i wieloma platformami sprzętowymi."
---

# Format `.doql.less` — zmienne i zagnieżdżenia dla projektów multi-env

Format `[projekt].doql.less` rozszerza czysty `doql.css` o mechanizmy znane z preprocesora **LESS**:

- **Zmienne** (`@nazwa: wartość`) — dla wspólnych ustawień środowiska
- **Zagnieżdżenia** — entity, interfejsy i workflow opisane w hierarchii
- **Operacje i interpolacja** — `@base-url + "/api/v1"`

Plik: `calibration-lab.doql.less`

---

## Zmienne globalne — Single Source of Truth dla środowiska

```less
/* ─── Variables ─── */

@app-name:        "Calibration Lab Manager";
@app-version:     "0.4.2";
@app-domain:      env.DOMAIN;

@env-dev:         dev;
@env-staging:     staging;
@env-prod:        prod;

@auth-method:     jwt;
@db-backend:      sqlite;          /* dev */
@db-backend-prod: postgresql;      /* prod override */

@retention-certs:  10years;
@retention-telemetry: 90days;

@signing-method:  pades;

@deploy-target:   docker-compose;
@ingress:         traefik;

/* Palette — hardware types */
@hw-drager:       "Dräger";
@hw-msa:          "MSA Safety";
@hw-honeywell:    "Honeywell";
```

---

## Model danych z zagnieżdżeniami

```less
/* ─── Data Model ─── */

entity[name="Instrument"] {
  id:             uuid!;
  serial:         string! unique;
  model:          string!;
  manufacturer:   string;
  category:       enum[breathing_apparatus, gas_detector, pressure_gauge];
  last_calibrated: datetime;
  next_calibration: datetime computed;
  status:         enum[active, recalled, retired];

  /* Nested computed fields */
  computed[name="next_calibration"] {
    formula: last_calibrated + calibration_interval;
  }

  /* Nested index */
  index[fields="serial, manufacturer"] {
    unique: true;
  }
}

entity[name="CalibrationRecord"] {
  id:           uuid!;
  instrument:   Instrument ref;
  execution_id: string!;
  operator:     User ref;
  reviewer:     User ref;
  performed_at: datetime auto;
  result:       enum[pass, fail, conditional];
  certificate:  Document ref nullable;

  /* Retention policy nested inside entity */
  retention {
    duration: @retention-certs;
    immutable: true;
    reason:   "ISO/IEC 17025 compliance";
  }
}

entity[name="Customer"] {
  id:      uuid!;
  name:    string!;
  email:   email;
  address: text;
  contact: string;
}
```

---

## Interfejsy z dziedziczeniem zmiennych

```less
/* ─── Interfaces ─── */

interface[type="api"] {
  auth:       @auth-method;
  rate-limit: 1000/min;

  /* Nested endpoints */
  endpoint[method="POST"][path="/calibrations"] {
    body:    { instrument_id: string!, execution_id: string!, operator: string, reviewer: string };
    returns: { id: uuid, cert_url: string, signed: bool };
    roles:   [metrologist, admin];
  }

  endpoint[method="GET"][path="/calibrations/{id}/verify"] {
    public:  true;
    returns: { valid: bool, issued: datetime, instrument: object };
  }

  endpoint[method="POST"][path="/certificates/{id}/sign"] {
    method-signing: @signing-method;
    roles:          [reviewer, admin];
  }
}

interface[type="web"] {
  framework: react;
  theme:     tailwind;

  page[name="calibration_form"] {
    layout: split-panel;

    form[name="generate_cert"] {
      fields: [instrument_id, execution_id, customer_id, operator, reviewer];
      submit: "Generuj świadectwo";
      action: GENERATE DOCUMENT calibration_certificate;
    }

    preview[type="pdf"] {
      mode: live;
      trigger: form-change;
    }
  }

  page[name="certificate_verify"][public="true"] {
    path:    "/verify/{cert_id}";
    content: [issued_date, instrument, status, signature_valid];
    action[label="Pobierz PDF"] {
      type: download;
    }
  }
}
```

---

## Dokumenty z template'ami (zagnieżdżone)

```less
/* ─── Documents ─── */

document[name="calibration_certificate"] {
  type:     pdf;
  template: "templates/cert_iso17025.html";

  /* Nested data bindings */
  data[field="organization"]  { source: DATA organization; }
  data[field="instrument"]    { source: DATA instruments WHERE id = @args.instrument_id; }
  data[field="customer"]      { source: DATA customers WHERE id = @args.customer_id; }
  data[field="measurements"]  { source: DATA measurements WHERE execution_id = @args.execution_id; }

  styling {
    paper:  A4;
    margin: 2.5cm;
    font[family="Inter"]         { source: "assets/fonts/Inter.ttf"; }
    font[family="JetBrains Mono"] { source: "assets/fonts/JetBrainsMono.ttf"; }
  }

  signature {
    enabled: true;
    method:  @signing-method;
    key:     env.SIGNING_KEY_PATH;
    reason:  "ISO 17025 compliance";
  }

  output {
    path:    "certs/@{instrument.serial}_@{date}.pdf";
    storage: local;
  }

  /* Nested hooks */
  hook[event="on_generate"] {
    action[type="audit_log"] {
      message: "Cert @{id} generated for @{instrument.serial}";
    }
    action[type="email"][condition="customer.email IS NOT NULL"] {
      template: cert_delivery;
      attach:   @self;
    }
  }
}

document[name="non_conformance_report"] {
  type:     pdf;
  template: "templates/ncr.html";

  output {
    path: "ncr/@{instrument.serial}_@{date}.pdf";
  }
}
```

---

## Workflow z zmiennymi

```less
/* ─── Workflows ─── */

workflow[name="auto_generate_on_calibration_done"] {
  trigger:   webhook oqlos.scenario.completed;
  condition: "@payload.scenario_type == 'calibration'";

  step[order="1"][action="generate_cert"] {
    document:     calibration_certificate;
    instrument_id: @payload.instrument_id;
    execution_id:  @payload.execution_id;
    operator:      @payload.operator;
  }

  step[order="2"][condition="success"] {
    action: email;
    to:     @payload.customer_email;
    attach: @generated;
  }

  step[order="2"][condition="failure"] {
    action:   generate_ncr;
    notify:   env.QUALITY_MANAGER_EMAIL;
  }
}

workflow[name="calibration_due_reminder"] {
  trigger: schedule "0 8 * * 1";   /* every Monday 8:00 */

  step[order="1"] {
    action: find;
    query:  "Instrument WHERE next_calibration < now + 14days";
  }

  step[order="2"] {
    action:  notify;
    channel: email;
    template: calibration_reminder;
  }
}
```

---

## Deploy z overridami per środowisko

```less
/* ─── Deploy ─── */

deploy {
  target:  @deploy-target;
  ingress: @ingress;

  /* Default: dev */
  container[name="api"] {
    db: @db-backend;
    replicas: 1;
  }

  /* Override for prod */
  container[name="api"][env="prod"] {
    db:       @db-backend-prod;
    replicas: 3;
  }

  backup {
    paths:     [certs/, data/];
    schedule:  daily;
    retention: @retention-certs;
  }
}
```

---

## Kluczowa różnica między .doql.css a .doql.less

| Cecha | `.doql.css` | `.doql.less` |
|---|---|---|
| Zmienne | ❌ inline hardcoded | ✅ `@var: value` |
| Zagnieżdżenia | płaskie selektory | ✅ struktury hierarchiczne |
| Reuse | kopiowanie bloków | ✅ zmienne + dziedziczenie |
| Docelowe projekty | proste, jednoenv | wieloenv, wieloplatformowe |
| Złożoność parsera | standardowy CSS | LESS-preprocessor |

Format `.doql.less` jest rekomendowany dla projektów takich jak **Calibration Lab Manager** gdzie istnieje wiele środowisk (dev/staging/prod), wiele typów dokumentów i złożone workflow ISO 17025.

---

*Następny artykuł: format `.doql.sass` — whitespace-based dla minimalnej składni, idealny do bibliotek komponentów OqlOS.*
