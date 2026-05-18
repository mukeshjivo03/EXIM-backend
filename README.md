# EXIM Backend

Django REST backend for EXIM operations, SAP sync, tank inventory, stock movement, licenses, contracts, and rates.

## API Documentation

Full API documentation is maintained in [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md).

When the server is running, interactive docs are available at:

| Tool | Endpoint |
|------|----------|
| Swagger UI | `/api/docs/` |
| ReDoc | `/api/redoc/` |
| OpenAPI schema | `/api/schema/` |

## Recently Documented APIs

The API docs include the active tank, SAP sync, and stock APIs currently registered in the URL configs, including:

| Area | Endpoints |
|------|-----------|
| Tank analytics | `/tank/tank-summary/`, `/tank/capacity-insights/`, `/tank/item-wise-summary/`, `/tank/tank-rates/`, `/tank/item-wise-average/`, `/tank/in-tank-items/` |
| Tank operations | `/tank/empty-tank/`, `/tank/log/` |
| SAP financial sync | `/sap-sync/balance-sheet/`, `/sap-sync/balance-sheet-insights/`, `/sap-sync/open-ap/`, `/sap-sync/open-ar/`, customer/vendor ledgers and balances |
| SAP inventory sync | `/sap_sync/open-grpos/`, `/sap-sync/open-pos/`, `/sap-sync/inventory/`, `/sap-sync/finished-inventory/`, `/sap-sync/warehouses/` |
| Stock operations | `/stock-status/move/`, `/stock-status/dispatch/`, `/stock-status/arrive-batch/`, `/stock-status/opening-stock/`, `/stock-status/contractual-history/` |

All protected endpoints expect:

```http
Authorization: Bearer <access_token>
```

## Route Notes

Some SAP routes currently use `/sap_sync/` and others use `/sap-sync/`. The docs preserve the exact registered paths from the backend.
