# EXIM Backend — API Documentation

**Framework:** Django 6.0.2 + Django REST Framework
**Auth:** JWT (SimpleJWT)
**API Docs (live):** `/api/docs/` (Swagger) | `/api/redoc/` (ReDoc)

---

## Table of Contents

1. [Authentication](#1-authentication)
2. [User Management](#2-user-management)
3. [SAP Sync](#3-sap-sync)
4. [Tank Management](#4-tank-management)
5. [Stock Status](#5-stock-status)
6. [Stock Variance (Debit Entries)](#6-stock-variance-debit-entries)
7. [Daily Prices](#7-daily-prices)
8. [License Management](#8-license-management)
   - [Advance License](#advance-license)
   - [DFIA License](#dfia-license)
9. [Permissions Reference](#9-permissions-reference)
10. [Data Models](#10-data-models)

---

## 1. Authentication

Base path: `/account/`

All endpoints except login and token refresh require a valid JWT access token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Login

```
POST /account/login/
```

**Request body:**
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Response `200`:**
```json
{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>",
  "name": "John Doe",
  "email": "user@example.com",
  "role": "ADM",
  "id": 1
}
```

---

### Refresh Token

```
POST /account/login/refresh/
```

**Request body:**
```json
{
  "refresh": "<refresh_token>"
}
```

**Response `200`:**
```json
{
  "access": "<new_access_token>"
}
```

---

### Logout

```
POST /account/logout/
```

Blacklists the refresh token, invalidating the session.

**Request body:**
```json
{
  "refresh": "<refresh_token>"
}
```

---

## 2. User Management

Base path: `/account/`
Permission: **Admin only**

### Register User

```
POST /account/register/
```

**Request body:**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "securepassword",
  "role": "MNG"
}
```

**Roles:** `ADM` (Admin), `MNG` (Manager), `FTR` (Factory)

---

### List Users

```
GET /account/users/
```

**Response `200`:**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "ADM",
    "is_active": true
  }
]
```

---

### Get / Update / Delete User

```
GET    /account/user/<id>/
PUT    /account/user/<id>/
DELETE /account/user/<id>/
```

---

## 3. SAP Sync

SAP data is synced from an external SQL Server (Jivo_All_Branches_Live). Sync endpoints pull data and upsert into the local PostgreSQL database.

Permission: **Admin only** (unless stated otherwise)

### Sync Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sap_sync/rm/items/` | Sync all Raw Material products |
| GET | `/sap_sync/rm/item/<itemCode>/` | Sync single RM product |
| GET | `/sap_sync/fg/items/` | Sync all Finished Goods products |
| GET | `/sap_sync/fg/item/<itemCode>/` | Sync single FG product |

### Sync Parties (Vendors)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sap_sync/party/<cardCode>/` | Sync single party/vendor |

### Sync Purchase Orders

| Method | Endpoint | Permission | Description |
|--------|----------|-----------|-------------|
| GET | `/sap-sync/po/` | Admin, Manager | Sync all POs |
| GET | `/sap-sync/po/<grpo_no>/` | Admin, Manager | Sync single PO |

### Sync Balance Sheet

```
GET /sap-sync/balance-sheet/
```

Permission: Admin, Manager

---

### Local Data Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/items/rm/` | List all RM products |
| GET | `/items/rm/summary/` | RM summary statistics |
| GET | `/items/rm/varieties/` | List all RM varieties |
| GET, DELETE | `/item/rm/<item_code>/` | Get or delete RM product |
| GET | `/items/fg/` | List all FG products |
| GET, DELETE | `/item/fg/<item_code>/` | Get or delete FG product |
| GET | `/parties/` | List all parties/vendors |
| GET, DELETE | `/party/<card_code>/` | Get or delete a party |
| GET | `/pos/` | List all purchase orders |
| GET, PUT, DELETE | `/po/<id>/` | Get, update, or delete a PO |
| GET | `/sync_logs/` | View sync logs |

---

### Sync Log Object

```json
{
  "id": 1,
  "type": "RM_SYNC",
  "status": "SUCCESS",
  "started_at": "2026-03-14T10:00:00Z",
  "completed_at": "2026-03-14T10:00:05Z",
  "records_created": 45,
  "records_updated": 10,
  "error_message": null
}
```

> **Note:** `/sap_sync/` (underscore) and `/sap-sync/` (hyphen) prefixes are used inconsistently across endpoints. This is a known backend inconsistency.

---

## 4. Tank Management

Base path: `/tank/`
Permission: Authenticated (write actions require Admin or Factory role)

### Tanks

| Method | Endpoint | Permission | Description |
|--------|----------|-----------|-------------|
| GET, POST | `/tank/` | Authenticated | List or create tanks |
| GET, DELETE | `/tank/<tank_code>/` | Admin | Get or delete a tank |
| PUT | `/tank/update-capacity/<tank_code>/` | Admin, Factory | Update tank capacity |

**Tank object:**
```json
{
  "tank_code": "TK-001",
  "item_code": "OIL-001",
  "tank_capacity": "50000.000",
  "current_capacity": "32000.000",
  "is_active": true,
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

---

### Tank Items (Commodities)

| Method | Endpoint | Permission | Description |
|--------|----------|-----------|-------------|
| GET, POST | `/tank/items/` | Authenticated | List or create tank items |
| GET, DELETE | `/tank/item/<tank_item_code>/` | Admin | Get or delete a tank item |
| PUT | `/tank/item/update-color/<tank_item_code>/` | Admin, Manager | Update item color tag + name |

---

### Tank Analytics

| Endpoint | Description |
|----------|-------------|
| `GET /tank/tank-summary/` | Total and per-tank capacity summary |
| `GET /tank/capacity-insights/` | Capacity utilization insights |
| `GET /tank/item-wise-summary/` | Breakdown by commodity |
| `GET /tank/tank-rates/` | FIFO-based rate breakdown per tank |
| `GET /tank/layers/<tank_code>/` | Rate breakdown layers for a specific tank |

> **Note:** `tank-rates` uses a FIFO algorithm to compute cost-weighted rates per tank based on stock completion dates.

---

### Tank Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tank/inward/` | Add stock to a tank |
| POST | `/tank/outward/` | Remove stock from a tank |
| GET | `/tank/log/` | Tank operation history with consumptions |

---

## 5. Stock Status

Base path: `/stock-status/`
Permission: Admin or Manager

### CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET, POST | `/stock-status/` | List or create stock entries |
| GET, PUT | `/stock-status/<id>/` | Get or update a stock entry |
| PATCH | `/stock-status/<id>/` | Soft-delete (send `{ "deleted": true }`) |

**Query filters on `GET /stock-status/`:**

| Filter | Type | Description |
|--------|------|-------------|
| `status` | string | Filter by status code |
| `vendor` | string | Filter by vendor/party code |
| `item` | string | Filter by item code |

**Stock status choices:**

| Code | Description |
|------|-------------|
| `PENDING` | Order placed, not dispatched |
| `ON_THE_WAY` | In transit to factory |
| `UNDER_LOADING` | Being loaded |
| `AT_REFINERY` | At refinery |
| `OTW_TO_REFINERY` | On the way to refinery |
| `KANDLA_STORAGE` | At Kandla storage |
| `MUNDRA_PORT` | At Mundra port |
| `ON_THE_SEA` | In sea transit |
| `IN_CONTRACT` | Allocated to a contract |
| `IN_TANK` | Stored in tank |
| `DELIVERED` | Delivered to destination |
| `IN_TRANSIT` | In general transit |
| `COMPLETED` | Fully processed |
| `OUT_SIDE_FACTORY` | Outside factory |
| `PROCESSING` | Being processed |

**Stock entry object:**
```json
{
  "id": 573,
  "item_code": "OIL-001",
  "vendor_code": "VENDA000004",
  "status": "IN_TANK",
  "rate": "100.00",
  "quantity": "1500.00",
  "total": "150000.00",
  "vehicle_number": "DL10AC3612",
  "transporter_name": null,
  "job_work_vendor": null,
  "arrival_date": null,
  "created_at": "2026-04-16T10:00:00Z",
  "created_by": "user@example.com",
  "deleted": false
}
```

---

### Stock Movement Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/stock-status/move/` | Move stock to a new status/quantity |
| POST | `/stock-status/dispatch/` | Dispatch stock to a destination status |
| POST | `/stock-status/arrive-batch/` | Record batch arrival with weighed quantity |
| POST | `/stock-status/opening-stock/` | Create an opening stock entry |
| GET | `/stock-status/out/` | List stocks currently outside factory |
| GET | `/stock-status/vehicle-report/` | Vehicle report filtered by `?status=` |

---

### Update Logs

```
GET /stock-status/stock-logs/
```

Returns a full history of all field changes on stock entries.

**Log object:**
```json
{
  "id": "uuid",
  "stock": 573,
  "action": "UPDATE",
  "changed_by_label": "user@example.com",
  "note": "Status changed",
  "timestamp": "2026-04-16T10:05:00Z",
  "field_logs": [
    { "field_name": "status", "old_value": "PENDING", "new_value": "IN_TANK" }
  ]
}
```

---

### Stock Analytics

| Endpoint | Description |
|----------|-------------|
| `GET /stock-status/stock-insights/` | Filterable insights (supports `status`, `vendor`, `item`) |
| `GET /stock-status/stock-summary/` | Aggregate summary of all stock |
| `GET /stock-status/stock-dashboard/` | Combined dashboard view |
| `GET /stock-status/get-unique-rm/` | List of unique RM item codes in stock |
| `GET /stock-status/get-stock-entry-by-rm/` | All stock entries for an item (`?item_code=`) |

---

## 6. Stock Variance (Debit Entries)

Base path: `/stock-status/`
Permission: Admin or Manager

When a stock batch is moved to `IN_TANK` and the received quantity differs from the expected quantity, a debit entry is automatically created recording the gain or loss.

### List Variance Entries

```
GET /stock-status/debit-entries/
```

Returns all gain/loss records.

**Response `200`:**
```json
[
  {
    "id": 13,
    "type": "GAIN",
    "quantity": "-500.00",
    "rate": "100.00",
    "total": "-50000.00",
    "vehicle_number": "DL10AC3612",
    "responsible_transporter": null,
    "reason": "Quantity gain on IN_TANK transition (was 1000.00, now 1500)",
    "created_at": "2026-04-16T10:15:11.709929Z",
    "created_by": "super@test.com",
    "stock": 573,
    "responsible_party": "VENDA000004"
  },
  {
    "id": 14,
    "type": "LOSS",
    "quantity": "10.00",
    "rate": "110.00",
    "total": "1100.00",
    "vehicle_number": "DL10AC3616",
    "responsible_transporter": null,
    "reason": "Quantity loss on IN_TANK transition (was 1000.00, now 990)",
    "created_at": "2026-04-16T10:20:01.746666Z",
    "created_by": "super@test.com",
    "stock": 575,
    "responsible_party": "VENDA000004"
  }
]
```

**Field notes:**
- `type`: `"GAIN"` (received more than expected) or `"LOSS"` (received less)
- `quantity`: Negative for GAIN, positive for LOSS
- `total`: Negative for GAIN, positive for LOSS
- `responsible_party`: Vendor `card_code` — resolve to `card_name` via `GET /parties/`

---

### Variance Insights

```
GET /stock-status/debit-insights/
```

Returns aggregated totals grouped by type.

**Response `200`:**
```json
[
  {
    "type": "GAIN",
    "total_qty": -500.0,
    "total_records": 13.0,
    "total_value": -50000.0
  },
  {
    "type": "LOSS",
    "total_qty": 110.0,
    "total_records": 29.0,
    "total_value": 12100.0
  }
]
```

Returns an empty array `[]` if no debit entries exist (frontend shows default zeroes).

---

## 7. Daily Prices

Base path: `/daily-price/`
Permission: Authenticated + (Admin or Manager)

### Fetch Prices from SAP

```
GET  /daily-price/fetch/       # Preview: returns data without saving
POST /daily-price/fetch/       # Fetch and store prices in the database
```

**Optional query param:** `?date=YYYY-MM-DD`

---

### Stored Prices

```
GET /daily-price/db-list/
```

Lists all stored daily prices. Optional: `?date=YYYY-MM-DD`

```
GET /daily-price/range/
```

Lists prices within a date range. Query params: `?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD`

**Daily price object:**
```json
{
  "id": 1,
  "commodity_name": "Palm Oil",
  "factory_price": "88.50",
  "packing_cost_kg": "2.10",
  "with_gst_kg": "92.30",
  "with_gst_ltr": "84.10",
  "date": "2026-03-14",
  "created_by": "user@example.com"
}
```

> Prices are unique per `(commodity_name, date)` combination.

---

### Price Trends

```
GET /daily-price/trends/
```

Returns the last 7 days of price data per commodity in chart-friendly format.

**Response `200`:**
```json
{
  "labels": ["2026-04-10", "2026-04-11", "2026-04-12"],
  "datasets": [
    { "label": "Palm Oil", "data": [88.50, 89.00, 88.75] }
  ]
}
```

Returns `{ "labels": [], "datasets": [] }` if no price data exists. At least 2 days of saved data are needed for a meaningful trend chart.

---

## 8. License Management

Base path: `/license/`
Permission: Authenticated + (Admin or Manager)

### Advance License

Advance Licenses track import/export authorizations with CIF and FOB valuations. Each header has separate import lines (BOE-based) and export lines (shipping bill-based).

#### Headers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/license/advance-license-headers/` | List all headers |
| POST | `/license/advance-license-headers/` | Create a header |
| GET | `/license/advance-license-header/<license_no>/` | Get header with nested import + export lines |
| PUT | `/license/advance-license-header/<license_no>/` | Update header |
| DELETE | `/license/advance-license-header/<license_no>/` | Delete header |

**Header object:**
```json
{
  "license_no": "ADV-2026-001",
  "import_lines": [...],
  "export_lines": [...],
  "issue_date": "2026-01-01",
  "import_validity": "2027-01-01",
  "export_validity": "2027-06-01",
  "cif_value_inr": "5000000.000",
  "cif_value_usd": "60000.000",
  "cif_exchange_rate": "83.330",
  "fob_value_inr": "4800000.000",
  "fob_value_usd": "57600.000",
  "fob_exhange_rate": "83.330",
  "status": "OPEN",
  "total_import": "125.000",
  "total_export": "120.000",
  "to_be_exported": "380.000",
  "balance": "380.000"
}
```

**Payload (create/update):** Send `license_no`, `issue_date`, `import_validity`, `export_validity`, `cif_value_inr`, `cif_exchange_rate`, `fob_value_inr`, `fob_exhange_rate`, `status`. The `_usd` and computed fields are returned by the backend.

> **Note:** `fob_exhange_rate` is a typo in the backend — the `h` and `c` are swapped. Match exactly.

---

#### Import Lines

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/license/advance-license-import-lines/` | Create an import line |
| PUT | `/license/advance-license-import-lines/<id>/` | Update an import line |
| DELETE | `/license/advance-license-import-lines/<id>/` | Delete an import line |

**Import line payload:**
```json
{
  "license_no": "ADV-2026-001",
  "boe_No": "BOE-001",
  "boe_value_usd": "15000.000",
  "boe_date": "2026-02-15",
  "import_in_mts": "125.000"
}
```

> **Note:** The field is `boe_No` (camelCase `N`) — match exactly.

---

#### Export Lines

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/license/advance-license-export-lines/` | Create an export line |
| PUT | `/license/advance-license-export-lines/<id>/` | Update an export line |
| DELETE | `/license/advance-license-export-lines/<id>/` | Delete an export line |

**Export line payload:**
```json
{
  "license_no": "ADV-2026-001",
  "shipping_bill_no": "SB-001",
  "sb_value_usd": "14800.000",
  "export_in_mts": "120.000"
}
```

---

### DFIA License

DFIA (Duty Free Import Authorization) licenses follow the same header + lines pattern. The header uses `file_no` as the primary key. Import/export MTS quantities on the header are computed from the lines — **do not send them in the payload**.

#### Headers

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/license/dfia-license-header/create/` | Create a DFIA header |
| GET | `/license/dfia-license-header/list/` | List all DFIA headers |
| GET | `/license/dfia-license-header/<file_no>/` | Get header with nested import + export lines |
| PUT | `/license/dfia-license-header/<file_no>/` | Update header |
| DELETE | `/license/dfia-license-header/<file_no>/` | Delete header |

**Header payload (create/update):**
```json
{
  "file_no": "DFIA-2026-001",
  "issue_date": "2026-01-15",
  "export_validity": "2027-01-15",
  "fob_value_inr": "4200000.000",
  "fob_exchange_rate": "83.500",
  "import_validity": "2027-07-15",
  "cif_value_inr": "3900000.000",
  "cif_exchange_rate": "83.500",
  "status": "OPEN"
}
```

> `export_in_mts` and `import_in_mts` are **not** sent in the payload. They are computed server-side from the associated lines.

**Status values:** `OPEN`, `CLOSE`, `Active`

---

#### DFIA Import Lines

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/license/dfia-license-import-lines/create/` | Create an import line |
| PUT | `/license/dfia-license-import-lines/<id>/` | Update an import line |
| DELETE | `/license/dfia-license-import-lines/<id>/` | Delete an import line |

**Import line payload:**
```json
{
  "license_no": "DFIA-2026-001",
  "boe_no": "BOE-DFIA-001",
  "boe_value_usd": "12000.000",
  "boe_date": "2026-03-10",
  "import_in_mts": "100.000"
}
```

---

#### DFIA Export Lines

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/license/dfia-license-export-lines/create/` | Create an export line |
| PUT | `/license/dfia-license-export-lines/<id>/` | Update an export line |
| DELETE | `/license/dfia-license-export-lines/<id>/` | Delete an export line |

**Export line payload:**
```json
{
  "license_no": "DFIA-2026-001",
  "shipping_bill_no": "SB-DFIA-001",
  "sb_value_usd": "11500.000",
  "export_in_mts": "95.000"
}
```

---

## 9. Permissions Reference

| Permission Class | Role Required | Code |
|-----------------|---------------|------|
| `IsAdminUser` | Admin | `ADM` |
| `IsManagerUser` | Manager | `MNG` |
| `IsFactoryUser` | Factory | `FTR` |

Most write operations are restricted to Admin or Manager. Factory users have write access only to tank capacity updates and tank inward/outward operations.

---

## 10. Data Models

### User

| Field | Type | Notes |
|-------|------|-------|
| `id` | int | Primary key |
| `email` | string | Unique, used as username |
| `name` | string | Display name |
| `role` | string | `ADM`, `MNG`, or `FTR` |
| `is_active` | bool | |
| `is_staff` | bool | Django admin access |

---

### Party (Vendor)

| Field | Type | Notes |
|-------|------|-------|
| `card_code` | string | Unique, primary key |
| `card_name` | string | Display name |
| `state` | string | |
| `u_main_group` | string | |
| `country` | string | |

---

### StockStatus

| Field | Type | Notes |
|-------|------|-------|
| `id` | int | |
| `item_code` | FK → RMProducts | |
| `vendor_code` | FK → Party | |
| `status` | string | Status choice |
| `rate` | decimal | Per-unit rate |
| `quantity` | decimal | |
| `total` | decimal | Auto-calculated |
| `vehicle_number` | string | |
| `arrival_date` | date | |
| `job_work_vendor` | string | |
| `deleted` | bool | Soft delete flag |

---

### DebitEntry (Variance)

| Field | Type | Notes |
|-------|------|-------|
| `id` | int | |
| `type` | string | `GAIN` or `LOSS` |
| `quantity` | decimal | Negative for GAIN, positive for LOSS |
| `rate` | decimal | Rate at time of entry |
| `total` | decimal | Negative for GAIN, positive for LOSS |
| `vehicle_number` | string | |
| `responsible_transporter` | string | Nullable |
| `reason` | string | Auto-generated description |
| `stock` | FK → StockStatus | The stock entry this applies to |
| `responsible_party` | FK → Party | Vendor card_code |
| `created_at` | datetime | |
| `created_by` | string | Email of creating user |

---

### DailyPrice

| Field | Type | Notes |
|-------|------|-------|
| `commodity_name` | string | |
| `factory_price` | decimal | |
| `packing_cost_kg` | decimal | |
| `with_gst_kg` | decimal | |
| `with_gst_ltr` | decimal | |
| `date` | date | |
| Unique together | | `(commodity_name, date)` |

---

### AdvanceLicenseHeader

| Field | Type | Notes |
|-------|------|-------|
| `license_no` | string | Unique, primary key |
| `issue_date` | date | |
| `import_validity` | date | |
| `export_validity` | date | |
| `cif_value_inr` | decimal | |
| `cif_value_usd` | decimal | Computed: `cif_value_inr / cif_exchange_rate` |
| `cif_exchange_rate` | decimal | |
| `fob_value_inr` | decimal | |
| `fob_value_usd` | decimal | Computed: `fob_value_inr / fob_exhange_rate` |
| `fob_exhange_rate` | decimal | Typo in field name (missing `c`) |
| `status` | string | `OPEN` or `CLOSE` |
| `total_import` | decimal | Sum of import line quantities |
| `total_export` | decimal | Sum of export line quantities |
| `to_be_exported` | decimal | Computed remaining |
| `balance` | decimal | Computed balance |

---

### DFIALicenseHeader

| Field | Type | Notes |
|-------|------|-------|
| `file_no` | string | Unique, primary key |
| `issue_date` | date | |
| `export_validity` | date | |
| `import_validity` | date | |
| `fob_value_inr` | decimal | |
| `fob_value_usd` | decimal | Computed |
| `fob_exchange_rate` | decimal | |
| `cif_value_inr` | decimal | |
| `cif_value_usd` | decimal | Computed |
| `cif_exchange_rate` | decimal | |
| `export_in_mts` | decimal | Computed from export lines |
| `import_in_mts` | decimal | Computed from import lines |
| `status` | string | `OPEN`, `CLOSE`, or `Active` |
| `total_import` | decimal | |
| `total_export` | decimal | |
| `to_be_imported` | decimal | Computed |
| `balance` | decimal | Computed |

---

*For live, interactive API docs visit `/api/docs/` (Swagger UI) when the server is running.*
