---
title: "Format doql.css — deklaratywna konfiguracja aplikacji w składni CSS"
date: 2026-04-17
categories: [doql, oqlos, css, dsl]
tags: [DOQL, CSS, IoT, Fleet, OqlOS, Softreck]
status: publish
excerpt: "Pełny przykład formatu [projekt].doql.css dla projektu IoT Fleet Manager. Pokazujemy jak przenieść deklaratywną konfigurację DOQL do składni CSS z selektorami atrybutowymi dla platform, środowisk i metod."
---

# Format `.doql.css` — przykład dla IoT Fleet Manager

Format `[projekt].doql.css` jest **formatem podstawowym (SSOT)** w ekosystemie DOQL CSS-like. Używa składni identycznej ze stylizowanym CSS — selektor + blok deklaracji — ale zamiast opisywać wygląd stron, opisuje **architekturę aplikacji**.

Plik: `iot-fleet-manager.doql.css`

---

## Metadane aplikacji

```css
/* ─── App Definition ─── */

app {
  name: "IoT Fleet Manager";
  version: "0.5.0";
  domain: "iot-fleet";
  description: "Fleet management for 100–10000 IoT nodes with oqlos-agent";
}
```

---

## Model danych — encje

```css
/* ─── Data Model ─── */

entity[name="Node"] {
  id:               uuid!;
  hostname:         string! unique;
  location:         geo;
  tags:             [string];
  hardware_type:    enum[rpi4, rpi5, jetson_nano, x86];
  firmware_version: string;
  last_seen:        datetime;
  status:           enum[online, offline, updating, error] computed;
  peripherals:      json;
}

entity[name="Node"] computed[name="status"] {
  when: last_seen > now - 60s;
  result: "online";
}

entity[name="Node"] computed[name="status"][fallback] {
  when: last_seen < now - 5min;
  result: "offline";
}

entity[name="Telemetry"] {
  node:          Node ref;
  timestamp:     datetime auto;
  cpu_load:      float;
  memory_used:   float;
  temperature_c: float;
  data:          json;
  index:         [node, timestamp];
}

entity[name="FirmwareBuild"] {
  version:       string!;
  release_notes: text;
  image_url:     url;
  signature:     string;
  targets:       [string];
  tested:        bool;
}

entity[name="OTAUpdate"] {
  firmware:   FirmwareBuild ref;
  targets:    [Node];
  status:     enum[pending, rolling, paused, completed, failed];
  started_at: datetime;
  progress:   float computed;
}
```

---

## Interfejsy — web, API

```css
/* ─── Interfaces ─── */

interface[type="web"] {
  framework: react;
  theme:     tailwind;
}

interface[type="web"] page[name="fleet_map"] {
  layout: fullscreen;
  map:    leaflet;
  markers: Node;
  markers-colored-by: status;
  on-click: show_popup(node_info);
}

interface[type="web"] page[name="fleet_list"] {
  from:    Node;
  filters: [status, hardware_type, location.country, tags];
}

interface[type="web"] page[name="fleet_list"] bulk-action[name="run_scenario"] {
  label:  "Run Scenario";
  action: SELECT scenario → ENQUEUE;
}

interface[type="web"] page[name="fleet_list"] bulk-action[name="ota_update"] {
  label:  "OTA Update";
  action: SELECT firmware → ENQUEUE;
}

interface[type="api"] {
  auth:       api-key;
  rate-limit: 10000/min;
}

interface[type="api"] endpoint[method="POST"][path="/nodes/{id}/heartbeat"] {
  body:    { telemetry: json };
  returns: { pending_commands: [] };
  auth:    node_key;
}

interface[type="api"] endpoint[method="POST"][path="/nodes/{id}/execute"] {
  body:    { scenario_id: string, args: json };
  returns: { execution_id: string };
  roles:   [operator, admin];
}

interface[type="api"] endpoint[method="WEBSOCKET"][path="/nodes/{id}/stream"] {
  description: "Bi-directional telemetry + commands";
}
```

---

## Integracje

```css
/* ─── Integrations ─── */

integration[name="monitoring"] provider[name="prometheus"] {
  scrape-interval: 15s;
  targets:         auto;
}

integration[name="monitoring"] provider[name="grafana"] {
  auto-provision-dashboards: true;
  dashboards: [fleet_overview, node_detail, sla_compliance];
}

integration[name="alerting"] provider[name="pagerduty"] {
  config: env.PAGERDUTY_*;
}

integration[name="alerting"] rule[trigger="node_offline_warning"] {
  condition: "Node offline > 10 min";
  severity:  warning;
}

integration[name="alerting"] rule[trigger="node_offline_critical"] {
  condition: "Node offline > 1 hour";
  severity:  critical;
}

integration[name="alerting"] rule[trigger="temperature_critical"] {
  condition: "Temperature > 80°C";
  severity:  critical;
}

integration[name="storage"] {
  telemetry: influxdb;
  config:    env.INFLUXDB_*;
  retention: 90days;
}

integration[name="ota"] {
  strategy:   canary;
  rollback-on: failure_rate > 1%;
  signed:     true;
}
```

---

## Workflow automation

```css
/* ─── Workflows ─── */

workflow[name="heartbeat_check"] {
  trigger: schedule "*/1 * * * *";
}

workflow[name="heartbeat_check"] step[order="1"] {
  action: find;
  query:  "Node WHERE last_seen < now - 5min AND status=online";
}

workflow[name="heartbeat_check"] step[order="2"] {
  action: foreach node;
  do:     [update_status_offline, alert_pagerduty_warning];
}

workflow[name="ota_canary"] {
  trigger: manual;
  input:   { firmware: FirmwareBuild, target_filter: string };
}

workflow[name="ota_canary"] step[order="1"] {
  action: select;
  sample: 5%;
  label:  canary;
}

workflow[name="ota_canary"] step[order="2"] {
  action: push_update;
  target: canary;
}

workflow[name="ota_canary"] step[order="3"] {
  action: wait;
  duration: 1h;
}

workflow[name="ota_canary"] step[order="4"] condition[if="failure_rate < 1%"] {
  action: push_update;
  target: next 20%;
}
```

---

## Role i uprawnienia

```css
/* ─── Roles ─── */

role[name="operator"] {
  can: [run_scenario, view_telemetry];
}

role[name="ops"] {
  can: [ota_update, node_restart, view_logs];
}

role[name="admin"] {
  can: [*];
}
```

---

## Deployment

```css
/* ─── Deploy ─── */

deploy {
  target:       kubernetes;
  helm-chart:   true;
  ingress:      traefik;
  service-mesh: optional;
}

deploy autoscale[service="api"] {
  min-replicas: 2;
  max-replicas: 10;
}

deploy autoscale[service="worker"] {
  min-replicas: 1;
  max-replicas: 5;
}
```

---

## Dlaczego ten format działa?

Format `iot-fleet-manager.doql.css` jest w pełni parserowalny standardowymi bibliotekami CSS (np. `postcss`, `css-tree` w JS lub `tinycss2` w Pythonie) — bez pisania własnej gramatyki od zera. Każdy blok to węzeł AST z selektorem i deklaracjami. Parser może wygenerować z niego `docker-compose.yml`, `Taskfile.yml`, `k8s-manifest.yaml` i `README.md` automatycznie.

---

*Następny artykuł: ten sam projekt w formacie `.doql.less` — z zmiennymi i zagnieżdżeniami.*
