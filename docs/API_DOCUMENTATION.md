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
6. [Daily Prices](#6-daily-prices)
7. [License Management](#7-license-management)
   - [Advance License](#advance-license)
   - [DFIA License](#dfia-license)
8. [Permissions Reference](#8-permissions-reference)
9. [Data Models](#9-data-models)

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
| GET | `/item/rm/<item_code>/` | Get or delete RM product |
| GET | `/items/fg/` | List all FG products |
| GET | `/item/fg/<item_code>/` | Get or delete FG product |
| GET | `/parties/` | List all parties/vendors |
| GET | `/party/<card_code>/` | Get or delete a party |
| GET | `/pos/` | List all purchase orders |
| GET/PUT/DELETE | `/po/<id>/` | Get, update, or delete a PO |
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
  "capacity": 50000,
  "current_capacity": 32000,
  "is_active": true,
  "created_at": "2026-01-01T00:00:00Z",
  "created_by": 1
}
```

---

### Tank Items (Commodities)

| Method | Endpoint | Permission | Description |
|--------|----------|-----------|-------------|
| GET, POST | `/tank/items/` | Authenticated | List or create tank items |
| GET, DELETE | `/tank/item/<tank_item_code>/` | Admin | Get or delete a tank item |
| PUT | `/tank/item/update-color/<tank_item_code>/` | Admin, Manager | Update item color tag |

---

### Tank Analytics

| Endpoint | Description |
|----------|-------------|
| `GET /tank/tank-summary/` | Total and per-tank capacity summary |
| `GET /tank/capacity-insights/` | Capacity utilization insights |
| `GET /tank/item-wise-summary/` | Breakdown by commodity |
| `GET /tank/tank-rates/` | FIFO-based rate breakdown per tank |

**Tank summary response:**
```json
{
  "total_capacity": 200000,
  "total_current": 120000,
  "utilization_percent": 60.0,
  "tanks": [...]
}
```

> **Note:** `tank-rates` uses a FIFO algorithm to compute cost-weighted rates per tank based on stock completion dates.

---

## 5. Stock Status

Base path: `/stock-status/`
Permission: Admin or Manager

### CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET, POST | `/stock-status/` | List or create stock entries |
| GET, PUT, DELETE | `/stock-status/<id>/` | Get, update, or delete a stock entry |

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
| `ON_THE_WAY` | In transit |
| `COMPLETED` | Received and stored |
| *(and more)* | See API schema for full list |

**Stock entry object:**
```json
{
  "id": 1,
  "item_code": "OIL-001",
  "vendor_code": "V-100",
  "status": "ON_THE_WAY",
  "rate": 95.50,
  "quantity": 1000,
  "total": 95500.00,
  "created_at": "2026-03-01T10:00:00Z",
  "created_by": 1
}
```

---

### Update Logs

```
GET /stock-status/stock-logs/
```

Returns a history of all field changes (status, rate, quantity) on stock entries.

**Log object:**
```json
{
  "stock_id": 1,
  "field_name": "status",
  "old_value": "PENDING",
  "new_value": "ON_THE_WAY",
  "updated_at": "2026-03-05T09:00:00Z",
  "updated_by": 2
}
```

---

### Stock Analytics

| Endpoint | Description |
|----------|-------------|
| `GET /stock-status/stock-insights/` | Filterable insights (supports `status`, `vendor`, `item`) |
| `GET /stock-status/stock-summary/` | Aggregate summary of all stock |
| `GET /stock-status/stock-dashboard/` | Combined dashboard view |

---

## 6. Daily Prices

Base path: `/daily-price/`
Permission: Authenticated + (Admin or Manager)

### Fetch Prices from SAP

```
GET  /daily-price/fetch/       # Preview: returns data without saving
POST /daily-price/fetch/       # Fetch and store prices in the database
```

**Optional query param:** `?date=YYYY-MM-DD`

---

### Price Trends

```
GET /daily-price/trends/
```

Returns the last 7 days of price data per commodity.

**Optional query param:** `?date=YYYY-MM-DD`

---

### Stored Prices

```
GET /daily-price/db-list/
```

Lists all stored daily prices.

**Optional query param:** `?date=YYYY-MM-DD`

**Daily price object:**
```json
{
  "id": 1,
  "commodity_name": "Palm Oil",
  "factory_price": 88.50,
  "packing_cost_kg": 2.10,
  "with_gst_kg": 92.30,
  "with_gst_ltr": 84.10,
  "date": "2026-03-14",
  "created_by": 1
}
```

> Prices are unique per `(commodity_name, date)` combination.

---

## 7. License Management

Base path: `/license/`
Permission: Authenticated + (Admin or Manager)

### Advance License

Advance Licenses track import/export authorizations with CIF and FOB valuations.

#### Headers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET, POST | `/license/advance-license-headers/` | List or create license headers |
| GET, PUT, DELETE | `/license/advance-license-header/<license_no>/` | Get, update, or delete |

**Header object:**
```json
{
  "license_no": "ADV-2026-001",
  "issue_date": "2026-01-01",
  "import_validity": "2027-01-01",
  "export_validity": "2027-06-01",
  "import_in_mts": 500.0,
  "export_in_mts": 480.0,
  "cif_value_inr": 5000000.0,
  "cif_value_usd": 60000.0,
  "cif_exchange_rate": 83.33,
  "fob_value_inr": 4800000.0,
  "fob_value_usd": 57600.0,
  "fob_exchange_rate": 83.33,
  "status": "OPEN"
}
```

**Status values:** `OPEN`, `CLOSE`

---

#### Lines

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET, POST | `/license/advance-license-lines/` | List or create license lines |
| GET, PUT, DELETE | `/license/advance-license-lines/<id>/` | Get, update, or delete |

**Line object:**
```json
{
  "id": 1,
  "license_no": "ADV-2026-001",
  "boe_no": "BOE-001",
  "shipping_bill_no": "SB-001",
  "date": "2026-02-15",
  "boe_value_usd": 15000.0,
  "sb_value_usd": 14800.0,
  "import_in_mts": 125.0,
  "export_in_mts": 120.0,
  "balance": 5.0
}
```

---

### DFIA License

DFIA (Duty Free Import Authorization) licenses follow the same pattern as Advance Licenses with separate header and line endpoints.

#### Headers

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/license/dfia-license-header/create/` | Create a DFIA header |
| GET | `/license/dfia-license-header/list/` | List all DFIA headers |
| GET, PUT, DELETE | `/license/dfia-license-header/<file_no>/` | Get, update, or delete |

---

#### Lines

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/license/dfia-license-lines/create/` | Create DFIA lines |
| GET | `/license/dfia-license-lines/list/` | List all DFIA lines |
| GET, PUT, DELETE | `/license/dfia-license-lines/<id>/` | Get, update, or delete |

---

## 8. Permissions Reference

| Permission Class | Role Required | Code |
|-----------------|---------------|------|
| `IsAdminUser` | Admin | `ADM` |
| `IsManagerUser` | Manager | `MNG` |
| `IsFactoryUser` | Factory | `FTR` |

Most write operations are restricted to `Admin` or `Manager`. Factory users have write access only to tank capacity updates.

---

## 9. Data Models

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

### RMProducts / FGProducts

| Field | Type | Notes |
|-------|------|-------|
| `item_code` | string | Unique, primary key |
| `item_name` | string | |
| `category` | string | |
| `variety` | string | |
| `unit` | string | Unit of measure |
| `brand` | string | |
| `sub_group` | string | |
| `rate` | decimal | Current rate |

---

### Party (Vendor)

| Field | Type | Notes |
|-------|------|-------|
| `card_code` | string | Unique, primary key |
| `card_name` | string | |
| `state` | string | |
| `u_main_group` | string | |
| `country` | string | |

---

### TankData

| Field | Type | Notes |
|-------|------|-------|
| `tank_code` | string | Auto-generated |
| `item_code` | FK → TankItem | |
| `capacity` | decimal | Total capacity |
| `current_capacity` | decimal | Current fill |
| `is_active` | bool | |

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
| `deleted` | bool | Soft delete flag |

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

### AdvanceLicenseHeaders

| Field | Type | Notes |
|-------|------|-------|
| `license_no` | string | Unique, primary key |
| `issue_date` | date | |
| `import_validity` | date | |
| `export_validity` | date | |
| `import_in_mts` | decimal | |
| `export_in_mts` | decimal | |
| `cif_value_inr/usd` | decimal | |
| `cif_exchange_rate` | decimal | |
| `fob_value_inr/usd` | decimal | Auto-calculated |
| `fob_exchange_rate` | decimal | |
| `status` | string | `OPEN` or `CLOSE` |

---

*For live, interactive API docs visit `/api/docs/` (Swagger UI) when the server is running.*
