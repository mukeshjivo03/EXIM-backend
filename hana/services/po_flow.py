"""SAP document flow ("relationship map") for purchase orders.

Read-only: every statement here is a SELECT. Starting from PO numbers (OPOR.DocNum)
it walks the documents SAP itself links to them:

    PO ─► GRPO ─┬─► Landed Cost          (IPF1.BaseType = 20)
                ├─► Inventory Transfer   (batch traceability: GRPO batch → OWTR)
                ├─► A/P Invoice ─► Credit Memo   (PCH1.BaseType = 20, RPC1.BaseType = 18)
                └─► Credit Memo          (RPC1.BaseType = 20)
    PO ─► A/P Invoice                    (PCH1.BaseType = 22, invoice without GRPO)

Documents whose CANCELED = 'C' are SAP's own cancellation postings and are skipped;
CANCELED = 'Y' documents are returned with cancelled=True.
"""
from collections import defaultdict

from .connection import HANAConnection, Queries

# SAP object types used in BaseType / OITL.DocType
PO, GRPO, AP_INVOICE, TRANSFER = 22, 20, 18, 67


def _in(values):
    return ",".join("?" * len(values))


def _doc(row, **extra):
    return {
        "doc_entry": row["DocEntry"],
        "doc_num": row["DocNum"],
        "doc_date": row["DocDate"],
        "status": "CANCELLED" if row.get("Canceled") == "Y" else ("CLOSED" if row["DocStatus"] == "C" else "OPEN"),
        "cancelled": row.get("Canceled") == "Y",
        **extra,
    }


def _fetch(conn, schema, po_numbers):
    s = schema
    pos = conn.execute(f"""
        SELECT H."DocEntry", H."DocNum", H."DocDate", H."DocStatus", H."CANCELED" AS "Canceled",
               H."CardCode", H."CardName", H."DocTotal",
               L."ItemCode", L."Dscription", L."unitMsr",
               SUM(L."Quantity") AS "Quantity", SUM(L."OpenQty") AS "OpenQty"
        FROM {s}."OPOR" H
        JOIN {s}."POR1" L ON L."DocEntry" = H."DocEntry"
        WHERE H."DocNum" IN ({_in(po_numbers)}) AND H."CANCELED" <> 'C'
        GROUP BY H."DocEntry", H."DocNum", H."DocDate", H."DocStatus", H."CANCELED",
                 H."CardCode", H."CardName", H."DocTotal", L."ItemCode", L."Dscription", L."unitMsr"
    """, po_numbers)
    po_entries = sorted({r["DocEntry"] for r in pos})
    if not po_entries:
        return pos, [], [], [], [], []

    grpos = conn.execute(f"""
        SELECT H."DocEntry", H."DocNum", H."DocDate", H."DocStatus", H."CANCELED" AS "Canceled",
               H."NumAtCard", H."U_VehicleNoM", H."U_BilltyNumber", H."DocTotal",
               L."BaseEntry", L."unitMsr", L."WhsCode", SUM(L."Quantity") AS "Quantity"
        FROM {s}."PDN1" L
        JOIN {s}."OPDN" H ON H."DocEntry" = L."DocEntry"
        WHERE L."BaseType" = {PO} AND L."BaseEntry" IN ({_in(po_entries)}) AND H."CANCELED" <> 'C'
        GROUP BY H."DocEntry", H."DocNum", H."DocDate", H."DocStatus", H."CANCELED",
                 H."NumAtCard", H."U_VehicleNoM", H."U_BilltyNumber", H."DocTotal", L."BaseEntry", L."unitMsr", L."WhsCode"
        ORDER BY H."DocDate", H."DocNum"
    """, po_entries)
    grpo_entries = sorted({r["DocEntry"] for r in grpos}) or [-1]

    landed = conn.execute(f"""
        SELECT DISTINCT H."DocEntry", H."DocNum", H."DocDate", H."DocStatus", H."Canceled",
               H."DocTotal", L."BaseEntry"
        FROM {s}."IPF1" L
        JOIN {s}."OIPF" H ON H."DocEntry" = L."DocEntry"
        WHERE L."BaseType" = {GRPO} AND L."BaseEntry" IN ({_in(grpo_entries)}) AND H."Canceled" <> 'C'
    """, grpo_entries)

    # Transfers carry no base-document link; follow the GRPO's batches instead.
    transfers = conn.execute(f"""
        SELECT O1."DocEntry" AS "GrpoEntry", H."DocEntry", H."DocNum", H."DocDate", H."DocStatus",
               H."CANCELED" AS "Canceled", H."Filler" AS "FromWhs", H."ToWhsCode" AS "ToWhs",
               SUM(I2."Quantity") AS "Quantity"
        FROM {s}."OITL" O1
        JOIN {s}."ITL1" I1 ON I1."LogEntry" = O1."LogEntry"
        JOIN {s}."ITL1" I2 ON I2."ItemCode" = I1."ItemCode" AND I2."SysNumber" = I1."SysNumber"
        JOIN {s}."OITL" O2 ON O2."LogEntry" = I2."LogEntry" AND O2."DocType" = {TRANSFER}
        JOIN {s}."OWTR" H ON H."DocEntry" = O2."DocEntry"
        WHERE O1."DocType" = {GRPO} AND O1."DocEntry" IN ({_in(grpo_entries)})
          AND I2."Quantity" > 0 AND H."CANCELED" <> 'C'
        GROUP BY O1."DocEntry", H."DocEntry", H."DocNum", H."DocDate", H."DocStatus", H."CANCELED",
                 H."Filler", H."ToWhsCode"
        ORDER BY H."DocDate", H."DocNum"
    """, grpo_entries)

    invoices = conn.execute(f"""
        SELECT DISTINCT H."DocEntry", H."DocNum", H."DocDate", H."DocStatus", H."CANCELED" AS "Canceled",
               H."DocTotal", H."NumAtCard", L."BaseType", L."BaseEntry"
        FROM {s}."PCH1" L
        JOIN {s}."OPCH" H ON H."DocEntry" = L."DocEntry"
        WHERE ((L."BaseType" = {GRPO} AND L."BaseEntry" IN ({_in(grpo_entries)}))
            OR (L."BaseType" = {PO} AND L."BaseEntry" IN ({_in(po_entries)})))
          AND H."CANCELED" <> 'C'
    """, grpo_entries + po_entries)
    invoice_entries = sorted({r["DocEntry"] for r in invoices}) or [-1]

    credit_memos = conn.execute(f"""
        SELECT DISTINCT H."DocEntry", H."DocNum", H."DocDate", H."DocStatus", H."CANCELED" AS "Canceled",
               H."DocTotal", L."BaseType", L."BaseEntry"
        FROM {s}."RPC1" L
        JOIN {s}."ORPC" H ON H."DocEntry" = L."DocEntry"
        WHERE ((L."BaseType" = {AP_INVOICE} AND L."BaseEntry" IN ({_in(invoice_entries)}))
            OR (L."BaseType" = {GRPO} AND L."BaseEntry" IN ({_in(grpo_entries)})))
          AND H."CANCELED" <> 'C'
    """, invoice_entries + grpo_entries)

    return pos, grpos, landed, transfers, invoices, credit_memos


def get_po_flows(po_numbers):
    """Return {po_number: flow} for the given PO numbers (OIL company).

    A PO number SAP doesn't know is returned as {"found": False}.
    """
    po_numbers = sorted({str(p).strip() for p in po_numbers if str(p or "").strip()})
    if not po_numbers:
        return {}

    # OPOR.DocNum is numeric; anything else can't exist in SAP and falls through as not found.
    numeric = [int(p) for p in po_numbers if p.isdigit()]
    if numeric:
        with HANAConnection() as conn:
            pos, grpos, landed, transfers, invoices, credit_memos = _fetch(conn, Queries.OIL_SCHEMA, numeric)
    else:
        pos = grpos = landed = transfers = invoices = credit_memos = []

    def money(v):
        return float(v) if v is not None else None

    cm_by_invoice, cm_by_grpo = defaultdict(list), defaultdict(list)
    for r in credit_memos:
        target = cm_by_invoice if r["BaseType"] == AP_INVOICE else cm_by_grpo
        target[r["BaseEntry"]].append(_doc(r, total=money(r["DocTotal"])))

    inv_by_grpo, inv_by_po = defaultdict(list), defaultdict(list)
    for r in invoices:
        target = inv_by_grpo if r["BaseType"] == GRPO else inv_by_po
        target[r["BaseEntry"]].append(_doc(
            r, total=money(r["DocTotal"]), vendor_ref=r["NumAtCard"],
            credit_memos=cm_by_invoice.get(r["DocEntry"], []),
        ))

    lc_by_grpo = defaultdict(list)
    for r in landed:
        lc_by_grpo[r["BaseEntry"]].append(_doc(r, total=money(r["DocTotal"])))

    # Only the first hop counts as "transferred": the move out of the warehouse the GRPO
    # received into. Later onward moves of the same batch are not this GRPO's step.
    receiving_whs = defaultdict(set)
    for r in grpos:
        receiving_whs[r["DocEntry"]].add(r["WhsCode"])

    tr_by_grpo = defaultdict(list)
    for r in transfers:
        if r["FromWhs"] not in receiving_whs[r["GrpoEntry"]]:
            continue
        tr_by_grpo[r["GrpoEntry"]].append(_doc(
            r, from_whs=r["FromWhs"], to_whs=r["ToWhs"], quantity=money(r["Quantity"]),
        ))

    grpos_by_po, seen_grpos = defaultdict(list), {}
    for r in grpos:
        key = (r["BaseEntry"], r["DocEntry"])
        if key in seen_grpos:  # same GRPO, another warehouse/UoM line: just add the quantity
            seen_grpos[key]["quantity"] = (seen_grpos[key]["quantity"] or 0) + (money(r["Quantity"]) or 0)
            continue
        seen_grpos[key] = _doc(
            r,
            quantity=money(r["Quantity"]), uom=r["unitMsr"], total=money(r["DocTotal"]),
            vendor_ref=r["NumAtCard"], vehicle_number=r["U_VehicleNoM"], bilty_number=r["U_BilltyNumber"],
            landed_costs=lc_by_grpo.get(r["DocEntry"], []),
            inventory_transfers=tr_by_grpo.get(r["DocEntry"], []),
            ap_invoices=inv_by_grpo.get(r["DocEntry"], []),
            credit_memos=cm_by_grpo.get(r["DocEntry"], []),
        )
        grpos_by_po[r["BaseEntry"]].append(seen_grpos[key])

    flows = {}
    for r in pos:
        key = str(r["DocNum"])
        flow = flows.get(key)
        if flow is None:
            flow = flows[key] = _doc(
                r, found=True, vendor_code=r["CardCode"], vendor_name=r["CardName"],
                total=money(r["DocTotal"]), lines=[],
                grpos=grpos_by_po.get(r["DocEntry"], []),
                ap_invoices=inv_by_po.get(r["DocEntry"], []),
            )
        flow["lines"].append({
            "item_code": r["ItemCode"], "item_name": r["Dscription"], "uom": r["unitMsr"],
            "quantity": money(r["Quantity"]), "open_quantity": money(r["OpenQty"]),
        })

    for p in po_numbers:
        flows.setdefault(p, {"found": False, "doc_num": p})
    return flows
