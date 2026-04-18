# Rodzina OQL — paczka kompletna

Declarative OQL — build complete applications from a single .doql file

## Metadata

- **name**: `doql`
- **version**: `0.1.2`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Taskfile.yml, testql(3), app.doql.less, app.doql.css, pyqual.yaml, goal.yaml, .env.example, src(4 mod)

## Intent

Declarative OQL — build complete applications from a single .doql file

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`, `app.doql.css`)

```less
// LESS format — define @variables here as needed

app {
  name: doql;
  version: 0.1.1;
}

entity[name="Post"] {
  id: uuid! auto;
  title: string!;
  slug: string! unique;
  content: text!;
  excerpt: text;
  author: ref(Author)!;
  category: ref(Category);
  tags: json;
  featured_image: string;
  published_at: datetime;
  created: datetime auto;
  updated: datetime auto;
}

entity[name="Author"] {
  id: uuid! auto;
  name: string!;
  email: string! unique;
  bio: text;
  avatar: string;
  created: datetime auto;
}

entity[name="Category"] {
  id: uuid! auto;
  name: string! unique;
  slug: string! unique;
  description: text;
  parent: ref(Category);
  sort_order: int default=0;
}

entity[name="Comment"] {
  id: uuid! auto;
  post: ref(Post)!;
  author_name: string!;
  author_email: string!;
  content: text!;
  approved: bool default=false;
  parent: ref(Comment);
  created: datetime auto;
}

entity[name="MediaFile"] {
  id: uuid! auto;
  filename: string!;
  mime_type: string!;
  size: int!;
  url: string!;
  alt_text: string;
  uploaded_by: ref(Author);
  created: datetime auto;
}

entity[name="Node"] {
  id: uuid! auto;
  hostname: string! unique;
  location: geo;
  tags: [string];
  hardware_type: enum["rpi4", "rpi5", "jetson_nano", "x86"];
  firmware_version: string;
  last_seen: datetime;
  status: enum[online, offline, updating, error] computed;
  peripherals: json;
}

entity[name="Telemetry"] {
  node: ref(Node);
  timestamp: datetime auto;
  cpu_load: float;
  memory_used: float;
  temperature_c: float;
  data: json;
}

entity[name="Deployment"] {
  name: string!;
  scenario: oql;
  target_filter: string;
  schedule: cron;
  last_run: datetime;
  next_run: datetime computed;
  success_rate: float computed;
}

entity[name="FirmwareBuild"] {
  version: string!;
  release_notes: text;
  image_url: url;
  signature: string;
  targets: [string];
  tested: bool;
}

entity[name="OTAUpdate"] {
  firmware: ref(FirmwareBuild);
  targets: [Node];
  status: enum[pending, rolling, paused, completed, failed];
  started_at: datetime;
  progress: float computed;
}

entity[name="Notebook"] {
  id: uuid! auto;
  name: string!;
  color: string default=sky;
  created: datetime auto;
}

entity[name="Note"] {
  id: uuid! auto;
  notebook: ref(Notebook);
  title: string!;
  body: text;
  pinned: bool default=false;
  created: datetime auto;
  updated: datetime auto;
}

entity[name="Tag"] {
  id: uuid! auto;
  name: string! unique;
  color: string default=slate;
}

entity[name="Todo"] {
  id: uuid! auto;
  title: string!;
  done: bool default=false;
  priority: enum[low, normal, high] default=normal;
  due: date;
  created: datetime auto;
}

entity[name="Product"] {
  id: uuid! auto;
  name: string!;
  slug: string! unique;
  description: text;
  price: decimal!;
  currency: enum[USD, EUR, PLN] default=EUR;
  stock: int default=0;
  category: string;
  images: json;
  active: bool default=true;
  created: datetime auto;
  updated: datetime auto;
}

entity[name="Customer"] {
  id: uuid! auto;
  email: string! unique;
  name: string!;
  phone: string;
  address: json;
  created: datetime auto;
}

entity[name="Order"] {
  id: uuid! auto;
  customer: ref(Customer)!;
  status: enum[pending, paid, shipped, delivered, cancelled] default=pending;
  items: json!;
  total: decimal!;
  currency: enum[USD, EUR, PLN];
  shipping_address: json;
  payment_method: string;
  paid_at: datetime;
  shipped_at: datetime;
  created: datetime auto;
}

entity[name="CartItem"] {
  id: uuid! auto;
  session_id: string!;
  product: ref(Product)!;
  quantity: int default=1;
  created: datetime auto;
}

entity[name="Operator"] {
  id: uuid! auto;
  name: string!;
  email: email unique;
  qualification: enum[technician, metrologist, quality_manager];
  active: bool default=true;
}

entity[name="Instrument"] {
  serial: string! unique;
  manufacturer: string!;
  model: string!;
  category: enum[scale, pressure_gauge, thermometer, multimeter, torque];
  range_min: decimal(20,6);
  range_max: decimal(20,6);
  unit: string!;
  uncertainty_class: string;
  owner_organization: string;
  last_calibration: date;
  next_calibration: date computed;
  certificate_valid_until: date;
}

entity[name="ReferenceStandard"] {
  instrument: ref(Instrument);
  traceability_chain: text!;
  uncertainty_budget: json;
  certificate_pdf: pdf!;
  valid_until: date!;
}

entity[name="Calibration"] {
  id: uuid! auto;
  instrument: ref(Instrument);
  performed_by: ref(Operator);
  reviewed_by: ref(Operator);
  reference_used: ref(ReferenceStandard);
  scenario: oql;
  date: datetime auto;
  measurements: json;
  uncertainty_calculation: json;
  result: enum[pass, fail, out_of_tolerance];
  certificate_pdf: pdf computed;
  certificate_number: string auto;
}

entity[name="CalibrationOrder"] {
  customer: ref(Customer);
  instruments: [Instrument];
  received_date: date;
  due_date: date;
  priority: enum[normal, rush, urgent];
  status: enum[received, in_progress, review, ready, shipped];
  total_price: decimal(10,2);
  invoice_number: string;
}

entity[name="Contact"] {
  id: uuid! auto;
  first_name: string!;
  last_name: string!;
  email: string unique;
  phone: string;
  company: ref(Company);
  position: string;
  tags: json;
  notes: text;
  source: enum[web, referral, cold, event] default=web;
  created: datetime auto;
  updated: datetime auto;
}

entity[name="Company"] {
  id: uuid! auto;
  name: string! unique;
  domain: string;
  industry: string;
  size: enum[startup, small, medium, enterprise];
  website: string;
  address: json;
  created: datetime auto;
}

entity[name="Deal"] {
  id: uuid! auto;
  title: string!;
  contact: ref(Contact)!;
  company: ref(Company);
  value: decimal;
  currency: enum[USD, EUR, PLN] default=EUR;
  stage: enum[lead, qualified, proposal, negotiation, won, lost] default=lead;
  probability: int default=0;
  expected_close: date;
  assigned_to: string;
  notes: text;
  created: datetime auto;
  updated: datetime auto;
}

entity[name="Activity"] {
  id: uuid! auto;
  type: enum[call, email, meeting, note, task]!;
  contact: ref(Contact);
  deal: ref(Deal);
  subject: string!;
  description: text;
  due_date: datetime;
  completed: bool default=false;
  assigned_to: string;
  created: datetime auto;
}

entity[name="User"] {
  id: uuid! auto;
  name: string!;
  email: email unique;
  role: enum[admin, manager, operator];
  active: bool default=true;
}

entity[name="Station"] {
  id: uuid! auto;
  name: string!;
  address: text;
  manager: ref(User);
}

entity[name="Qualification"] {
  name: string!;
  level: enum[basic, advanced, instructor];
  valid_until: date;
  certificate_file: pdf;
}

entity[name="Device"] {
  id: uuid! auto;
  serial: string! unique;
  model: string!;
  manufacturer: string!;
  device_type: enum[scba, mask, cylinder, regulator, harness];
  station: ref(Station);
  purchase_date: date;
  warranty_until: date;
  photo: image;
  barcode: string unique;
  status: enum[ready, in_use, failed, retired, overdue] default=ready;
  last_inspection: date;
  next_inspection: date computed;
  total_uses: int default=0;
}

entity[name="Inspection"] {
  id: uuid! auto;
  device: ref(Device);
  operator: ref(Operator);
  scenario_id: oql;
  started_at: datetime auto;
  completed_at: datetime;
  result: enum[pass, fail, incomplete, cancelled];
  measurements: json;
  notes: text;
  report_pdf: pdf computed;
  signed_by: ref(Operator);
}

entity[name="CylinderFill"] {
  id: uuid! auto;
  cylinder: ref(Device);
  filled_at: datetime auto;
  pressure_bar: decimal(10,1);
  operator: ref(Operator);
  quality_check: bool;
  air_quality_cert: pdf;
}

entity[name="Exercise"] {
  id: uuid! auto;
  operator: ref(Operator);
  date: date!;
  type: enum[training, live_exercise, annual_mandatory];
  duration_minutes: int;
  equipment_used: [Device];
  pass: bool;
  notes: text;
}

interface[type="cli"] {
  framework: click;
}
interface[type="cli"] page[name="doql"] {

}

workflow[name="install"] {
  trigger: manual;
  step-1: run cmd=pip install -e .[dev];
}

workflow[name="quality"] {
  trigger: manual;
  step-1: run cmd=pyqual run;
}

workflow[name="quality:fix"] {
  trigger: manual;
  step-1: run cmd=pyqual run --fix;
}

workflow[name="quality:report"] {
  trigger: manual;
  step-1: run cmd=pyqual report;
}

workflow[name="build"] {
  trigger: manual;
  step-1: run cmd=python -m build;
}

workflow[name="clean"] {
  trigger: manual;
  step-1: run cmd=rm -rf build/ dist/ *.egg-info;
}

workflow[name="structure"] {
  trigger: manual;
  step-1: run cmd=echo "📁 Analyzing project structure..."
python3 -m doql.cli adopt {{.PWD}} --output app.doql.css --force
echo "🎨 Exporting to LESS format..."
doql export --format less -o {{.DOQL_OUTPUT}}
echo "✅ Structure generated: app.doql.css + {{.DOQL_OUTPUT}}";
}

workflow[name="doql:adopt"] {
  trigger: manual;
  step-1: run cmd=python3 -m doql.cli adopt {{.PWD}} --output app.doql.css --force;
  step-2: run cmd=echo "✅ Captured in app.doql.css";
}

workflow[name="doql:export"] {
  trigger: manual;
  step-1: run cmd=if [ ! -f "app.doql.css" ]; then
echo "❌ app.doql.css not found. Run: task structure"
exit 1
fi;
  step-2: run cmd=doql export --format less -o {{.DOQL_OUTPUT}};
  step-3: run cmd=echo "✅ Exported to {{.DOQL_OUTPUT}}";
}

workflow[name="doql:validate"] {
  trigger: manual;
  step-1: run cmd=if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
echo "❌ {{.DOQL_OUTPUT}} not found. Run: task doql:adopt"
exit 1
fi;
  step-2: run cmd=python3 -m doql.cli validate;
}

workflow[name="doql:doctor"] {
  trigger: manual;
  step-1: run cmd=python3 -m doql.cli doctor {{.PWD}};
}

workflow[name="doql:build"] {
  trigger: manual;
  step-1: run cmd=if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
echo "❌ {{.DOQL_OUTPUT}} not found. Run: task doql:adopt"
exit 1
fi;
  step-2: run cmd=# Regenerate LESS from CSS if CSS exists
if [ -f "app.doql.css" ]; then
doql export --format less -o {{.DOQL_OUTPUT}}
fi;
  step-3: run cmd=python3 -m doql.cli build app.doql.css --out build/;
}

workflow[name="help"] {
  trigger: manual;
  step-1: run cmd=task --list;
}

deploy {
  target: docker;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
}
```

```css
app {
  name: "doql";
  version: "0.1.1";
}

/* ─── Blog CMS ─── */

entity[name="Post"] {
  id: uuid! auto;
  title: string!;
  slug: string! unique;
  content: text!;
  excerpt: text;
  author: ref(Author)!;
  category: ref(Category);
  tags: json;
  featured_image: string;
  published_at: datetime;
  created: datetime auto;
  updated: datetime auto;
}

entity[name="Author"] {
  id: uuid! auto;
  name: string!;
  email: string! unique;
  bio: text;
  avatar: string;
  created: datetime auto;
}

entity[name="Category"] {
  id: uuid! auto;
  name: string! unique;
  slug: string! unique;
  description: text;
  parent: ref(Category);
  sort_order: int default=0;
}

entity[name="Comment"] {
  id: uuid! auto;
  post: ref(Post)!;
  author_name: string!;
  author_email: string!;
  content: text!;
  approved: bool default=false;
  parent: ref(Comment);
  created: datetime auto;
}

entity[name="MediaFile"] {
  id: uuid! auto;
  filename: string!;
  mime_type: string!;
  size: int!;
  url: string!;
  alt_text: string;
  uploaded_by: ref(Author);
  created: datetime auto;
}

/* ─── IoT Fleet ─── */

entity[name="Node"] {
  id: uuid! auto;
  hostname: string! unique;
  location: geo;
  tags: [string];
  hardware_type: enum["rpi4", "rpi5", "jetson_nano", "x86"];
  firmware_version: string;
  last_seen: datetime;
  status: enum[online, offline, updating, error] computed;
  peripherals: json;
}

entity[name="Telemetry"] {
  node: ref(Node);
  timestamp: datetime auto;
  cpu_load: float;
  memory_used: float;
  temperature_c: float;
  data: json;
}

entity[name="Deployment"] {
  name: string!;
  scenario: oql;
  target_filter: string;
  schedule: cron;
  last_run: datetime;
  next_run: datetime computed;
  success_rate: float computed;
}

entity[name="FirmwareBuild"] {
  version: string!;
  release_notes: text;
  image_url: url;
  signature: string;
  targets: [string];
  tested: bool;
}

entity[name="OTAUpdate"] {
  firmware: ref(FirmwareBuild);
  targets: [Node];
  status: enum[pending, rolling, paused, completed, failed];
  started_at: datetime;
  progress: float computed;
}

/* ─── Notes App ─── */

entity[name="Notebook"] {
  id: uuid! auto;
  name: string!;
  color: string default=sky;
  created: datetime auto;
}

entity[name="Note"] {
  id: uuid! auto;
  notebook: ref(Notebook);
  title: string!;
  body: text;
  pinned: bool default=false;
  created: datetime auto;
  updated: datetime auto;
}

entity[name="Tag"] {
  id: uuid! auto;
  name: string! unique;
  color: string default=slate;
}

/* ─── Todo PWA ─── */

entity[name="Todo"] {
  id: uuid! auto;
  title: string!;
  done: bool default=false;
  priority: enum[low, normal, high] default=normal;
  due: date;
  created: datetime auto;
}

/* ─── E-Commerce Shop ─── */

entity[name="Product"] {
  id: uuid! auto;
  name: string!;
  slug: string! unique;
  description: text;
  price: decimal!;
  currency: enum[USD, EUR, PLN] default=EUR;
  stock: int default=0;
  category: string;
  images: json;
  active: bool default=true;
  created: datetime auto;
  updated: datetime auto;
}

entity[name="Customer"] {
  id: uuid! auto;
  email: string! unique;
  name: string!;
  phone: string;
  address: json;
  created: datetime auto;
}

entity[name="Order"] {
  id: uuid! auto;
  customer: ref(Customer)!;
  status: enum[pending, paid, shipped, delivered, cancelled] default=pending;
  items: json!;
  total: decimal!;
  currency: enum[USD, EUR, PLN];
  shipping_address: json;
  payment_method: string;
  paid_at: datetime;
  shipped_at: datetime;
  created: datetime auto;
}

entity[name="CartItem"] {
  id: uuid! auto;
  session_id: string!;
  product: ref(Product)!;
  quantity: int default=1;
  created: datetime auto;
}

/* ─── Calibration Lab ─── */

entity[name="Operator"] {
  id: uuid! auto;
  name: string!;
  email: email unique;
  qualification: enum[technician, metrologist, quality_manager];
  active: bool default=true;
}

entity[name="Instrument"] {
  serial: string! unique;
  manufacturer: string!;
  model: string!;
  category: enum[scale, pressure_gauge, thermometer, multimeter, torque];
  range_min: decimal(20,6);
  range_max: decimal(20,6);
  unit: string!;
  uncertainty_class: string;
  owner_organization: string;
  last_calibration: date;
  next_calibration: date computed;
  certificate_valid_until: date;
}

entity[name="ReferenceStandard"] {
  instrument: ref(Instrument);
  traceability_chain: text!;
  uncertainty_budget: json;
  certificate_pdf: pdf!;
  valid_until: date!;
}

entity[name="Calibration"] {
  id: uuid! auto;
  instrument: ref(Instrument);
  performed_by: ref(Operator);
  reviewed_by: ref(Operator);
  reference_used: ref(ReferenceStandard);
  scenario: oql;
  date: datetime auto;
  measurements: json;
  uncertainty_calculation: json;
  result: enum[pass, fail, out_of_tolerance];
  certificate_pdf: pdf computed;
  certificate_number: string auto;
}

entity[name="CalibrationOrder"] {
  customer: ref(Customer);
  instruments: [Instrument];
  received_date: date;
  due_date: date;
  priority: enum[normal, rush, urgent];
  status: enum[received, in_progress, review, ready, shipped];
  total_price: decimal(10,2);
  invoice_number: string;
}

/* ─── CRM Contacts ─── */

entity[name="Contact"] {
  id: uuid! auto;
  first_name: string!;
  last_name: string!;
  email: string unique;
  phone: string;
  company: ref(Company);
  position: string;
  tags: json;
  notes: text;
  source: enum[web, referral, cold, event] default=web;
  created: datetime auto;
  updated: datetime auto;
}

/* ─── CRM (continued) ─── */

entity[name="Company"] {
  id: uuid! auto;
  name: string! unique;
  domain: string;
  industry: string;
  size: enum[startup, small, medium, enterprise];
  website: string;
  address: json;
  created: datetime auto;
}

entity[name="Deal"] {
  id: uuid! auto;
  title: string!;
  contact: ref(Contact)!;
  company: ref(Company);
  value: decimal;
  currency: enum[USD, EUR, PLN] default=EUR;
  stage: enum[lead, qualified, proposal, negotiation, won, lost] default=lead;
  probability: int default=0;
  expected_close: date;
  assigned_to: string;
  notes: text;
  created: datetime auto;
  updated: datetime auto;
}

entity[name="Activity"] {
  id: uuid! auto;
  type: enum[call, email, meeting, note, task]!;
  contact: ref(Contact);
  deal: ref(Deal);
  subject: string!;
  description: text;
  due_date: datetime;
  completed: bool default=false;
  assigned_to: string;
  created: datetime auto;
}

/* ─── Asset Management ─── */

entity[name="User"] {
  id: uuid! auto;
  name: string!;
  email: email unique;
  role: enum[admin, manager, operator];
  active: bool default=true;
}

entity[name="Station"] {
  id: uuid! auto;
  name: string!;
  address: text;
  manager: ref(User);
}

entity[name="Qualification"] {
  name: string!;
  level: enum[basic, advanced, instructor];
  valid_until: date;
  certificate_file: pdf;
}

entity[name="Device"] {
  id: uuid! auto;
  serial: string! unique;
  model: string!;
  manufacturer: string!;
  device_type: enum[scba, mask, cylinder, regulator, harness];
  station: ref(Station);
  purchase_date: date;
  warranty_until: date;
  photo: image;
  barcode: string unique;
  status: enum[ready, in_use, failed, retired, overdue] default=ready;
  last_inspection: date;
  next_inspection: date computed;
  total_uses: int default=0;
}

entity[name="Inspection"] {
  id: uuid! auto;
  device: ref(Device);
  operator: ref(Operator);
  scenario_id: oql;
  started_at: datetime auto;
  completed_at: datetime;
  result: enum[pass, fail, incomplete, cancelled];
  measurements: json;
  notes: text;
  report_pdf: pdf computed;
  signed_by: ref(Operator);
}

entity[name="CylinderFill"] {
  id: uuid! auto;
  cylinder: ref(Device);
  filled_at: datetime auto;
  pressure_bar: decimal(10,1);
  operator: ref(Operator);
  quality_check: bool;
  air_quality_cert: pdf;
}

entity[name="Exercise"] {
  id: uuid! auto;
  operator: ref(Operator);
  date: date!;
  type: enum[training, live_exercise, annual_mandatory];
  duration_minutes: int;
  equipment_used: [Device];
  pass: bool;
  notes: text;
}

interface[type="cli"] {
  framework: click;
}
interface[type="cli"] page[name="doql"] {

}

workflow[name="install"] {
  trigger: "manual";
  step-1: run cmd=pip install -e .[dev];
}

workflow[name="quality"] {
  trigger: "manual";
  step-1: run cmd=pyqual run;
}

workflow[name="quality:fix"] {
  trigger: "manual";
  step-1: run cmd=pyqual run --fix;
}

workflow[name="quality:report"] {
  trigger: "manual";
  step-1: run cmd=pyqual report;
}

workflow[name="build"] {
  trigger: "manual";
  step-1: run cmd=python -m build;
}

workflow[name="clean"] {
  trigger: "manual";
  step-1: run cmd=rm -rf build/ dist/ *.egg-info;
}

workflow[name="structure"] {
  trigger: "manual";
  step-1: run cmd=echo "📁 Analyzing project structure..."
python3 -m doql.cli adopt {{.PWD}} --output app.doql.css --force
echo "🎨 Exporting to LESS format..."
doql export --format less -o {{.DOQL_OUTPUT}}
echo "✅ Structure generated: app.doql.css + {{.DOQL_OUTPUT}}";
}

workflow[name="doql:adopt"] {
  trigger: "manual";
  step-1: run cmd=python3 -m doql.cli adopt {{.PWD}} --output app.doql.css --force;
  step-2: run cmd=echo "✅ Captured in app.doql.css";
}

workflow[name="doql:export"] {
  trigger: "manual";
  step-1: run cmd=if [ ! -f "app.doql.css" ]; then
  echo "❌ app.doql.css not found. Run: task structure"
  exit 1
fi;
  step-2: run cmd=doql export --format less -o {{.DOQL_OUTPUT}};
  step-3: run cmd=echo "✅ Exported to {{.DOQL_OUTPUT}}";
}

workflow[name="doql:validate"] {
  trigger: "manual";
  step-1: run cmd=if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
  echo "❌ {{.DOQL_OUTPUT}} not found. Run: task doql:adopt"
  exit 1
fi;
  step-2: run cmd=python3 -m doql.cli validate;
}

workflow[name="doql:doctor"] {
  trigger: "manual";
  step-1: run cmd=python3 -m doql.cli doctor {{.PWD}};
}

workflow[name="doql:build"] {
  trigger: "manual";
  step-1: run cmd=if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
  echo "❌ {{.DOQL_OUTPUT}} not found. Run: task doql:adopt"
  exit 1
fi;
  step-2: run cmd=# Regenerate LESS from CSS if CSS exists
if [ -f "app.doql.css" ]; then
  doql export --format less -o {{.DOQL_OUTPUT}}
fi;
  step-3: run cmd=python3 -m doql.cli build app.doql.css --out build/;
}

workflow[name="help"] {
  trigger: "manual";
  step-1: run cmd=task --list;
}

deploy {
  target: docker;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: ".env";
}
```

### Source Modules

- `doql.cli`
- `doql.lsp_server`
- `doql.parser`
- `doql.plugins`

## Interfaces

### CLI Entry Points

- `doql`
- `doql-lsp`

### testql Scenarios

#### `testql-scenarios/generated-api-integration.testql.toon.yaml`

```toon
# SCENARIO: API Integration Tests
# TYPE: api
# GENERATED: true

CONFIG[3]{key, value}:
  base_url, http://localhost:8101
  timeout_ms, 30000
  retry_count, 3

API[4]{method, endpoint, expected_status}:
  GET, /health, 200
  GET, /api/v1/status, 200
  POST, /api/v1/test, 201
  GET, /api/v1/docs, 200

ASSERT[2]{field, operator, expected}:
  status, ==, ok
  response_time, <, 1000
```

#### `testql-scenarios/generated-api-smoke.testql.toon.yaml`

```toon
# SCENARIO: Auto-generated API Smoke Tests
# TYPE: api
# GENERATED: true
# DETECTORS: ConfigEndpointDetector

CONFIG[4]{key, value}:
  base_url, http://localhost:8101
  timeout_ms, 10000
  retry_count, 3
  detected_frameworks, ConfigEndpointDetector

ASSERT[2]{field, operator, expected}:
  status, <, 500
  response_time, <, 2000

# Summary by Framework:
#   docker: 1 endpoints
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

LOG[8]{message}:
  "Test: test_fastapi_dependency_alone_does_not_create_api_interface"
  "Test: test_fastapi_with_main_py_creates_api"
  "Test: test_api_entry_point_in_scripts_creates_api"
  "Test: test_api_boot_and_health"
  "Test: test_fastapi_dependency_alone_does_not_create_api_interface"
  "Test: test_fastapi_with_main_py_creates_api"
  "Test: test_api_entry_point_in_scripts_creates_api"
  "Test: test_api_boot_and_health"
```

## Workflows

### Taskfile Tasks (`Taskfile.yml`)

```yaml
tasks:
  install:
    desc: "Install Python dependencies (editable)"
    cmds:
      - pip install -e .[dev]
  quality:
    desc: "Run pyqual quality pipeline"
    cmds:
      - pyqual run
  quality:fix:
    desc: "Run pyqual with auto-fix"
    cmds:
      - pyqual run --fix
  quality:report:
    desc: "Generate pyqual quality report"
    cmds:
      - pyqual report
  build:
    desc: "Build wheel + sdist"
    cmds:
      - python -m build
  clean:
    desc: "Remove build artefacts"
    cmds:
      - rm -rf build/ dist/ *.egg-info
  all:
    desc: "Run install, quality check"
  structure:
    desc: "Generate project structure (app.doql.css + app.doql.less)"
    cmds:
      - echo "📁 Analyzing project structure..."
python3 -m doql.cli adopt {{.PWD}} --output app.doql.css --force
echo "🎨 Exporting to LESS format..."
doql export --format less -o {{.DOQL_OUTPUT}}
echo "✅ Structure generated: app.doql.css + {{.DOQL_OUTPUT}}"
  doql:adopt:
    desc: "Reverse-engineer doql project structure (CSS only)"
    cmds:
      - python3 -m doql.cli adopt {{.PWD}} --output app.doql.css --force
  doql:export:
    desc: "Export to LESS format"
    cmds:
      - if [ ! -f "app.doql.css" ]; then
  echo "❌ app.doql.css not found. Run: task structure"
  exit 1
fi
  doql:validate:
    desc: "Validate app.doql.less syntax"
    cmds:
      - if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
  echo "❌ {{.DOQL_OUTPUT}} not found. Run: task doql:adopt"
  exit 1
fi
  doql:doctor:
    desc: "Run doql health checks"
    cmds:
      - python3 -m doql.cli doctor {{.PWD}}
  doql:build:
    desc: "Generate code from app.doql.less"
    cmds:
      - if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
  echo "❌ {{.DOQL_OUTPUT}} not found. Run: task doql:adopt"
  exit 1
fi
  analyze:
    desc: "Full doql analysis (adopt + validate + doctor)"
  help:
    desc: "Show available tasks"
    cmds:
      - task --list
```

## Quality Pipeline (`pyqual.yaml`)

```yaml
pipeline:
  name: doql-quality

  metrics:
    cc_max: 15
    vallm_pass_min: 55   # current: 58% - 3 vallm errors
    # coverage disabled - pytest_cov reports null (no data collected)

  stages:
    - name: analyze
      tool: code2llm-filtered

    - name: validate
      tool: vallm-filtered

    - name: prefact
      tool: prefact
      optional: true
      when: any_stage_fail
      timeout: 900

    - name: fix
      tool: llx-fix
      optional: true
      when: any_stage_fail
      timeout: 1800

    - name: security
      tool: bandit
      optional: true
      timeout: 120

    - name: test
      tool: pytest
      timeout: 600

    - name: push
      tool: git-push
      optional: true
      timeout: 120

  loop:
    max_iterations: 3
    on_fail: report
    ticket_backends:
      - markdown

  env:
    LLM_MODEL: openrouter/qwen/qwen3-coder-next
```

## Configuration

```yaml
project:
  name: doql
  version: 0.1.2
  env: local
```

## Dependencies

### Runtime

- `click>=8.1`
- `pydantic>=2.0`
- `pyyaml>=6.0`
- `jinja2>=3.1`
- `rich>=13.0`
- `httpx>=0.25`
- `goal>=2.1.0`
- `costs>=0.1.20`
- `pfix>=0.1.60`
- `tomli>=2.0; python_version < '3.11'`
- `testql>=0.1.1`

### Development

- `pytest>=7.4`
- `pytest-asyncio`
- `ruff`
- `mypy`
- `goal>=2.1.0`
- `costs>=0.1.20`
- `pfix>=0.1.60`

## Deployment

```bash
pip install doql

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `*(not set)*` | Required: OpenRouter API key (https://openrouter.ai/keys) |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | Model (default: openrouter/qwen/qwen3-coder-next) |
| `PFIX_AUTO_APPLY` | `true` | true = apply fixes without asking |
| `PFIX_AUTO_INSTALL_DEPS` | `true` | true = auto pip/uv install |
| `PFIX_AUTO_RESTART` | `false` | true = os.execv restart after fix |
| `PFIX_MAX_RETRIES` | `3` |  |
| `PFIX_DRY_RUN` | `false` |  |
| `PFIX_ENABLED` | `true` |  |
| `PFIX_GIT_COMMIT` | `false` | true = auto-commit fixes |
| `PFIX_GIT_PREFIX` | `pfix:` | commit message prefix |
| `PFIX_CREATE_BACKUPS` | `false` | false = disable .pfix_backups/ directory |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`doql`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `doql/__init__.py:__version__`
