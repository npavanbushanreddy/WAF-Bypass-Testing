#!/usr/bin/env python3
"""
request-generator.py

Generates HTTP-request variants from payloads in payloads.txt and appends
them to an existing Excel file.

Targets can be chosen at runtime:
1. URL
2. Arguments at URL
3. Argument Names at URL
4. Cookie
5. Headers
6. Body (POST form)
7. Argument in Body
8. Argument Names at Body
9. Sample JSON
10. Sample XML
11. All

Requirements:
    pip install pandas openpyxl
"""
from pathlib import Path
import pandas as pd
import urllib.parse
import json

PAYLOADS_F = Path("payloads.txt")
EXCEL_F = Path("Payload-Requests.xlsx")
BASE_PREFIX = "/test"
NORMAL_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"


# ------------------- Payload Reading -------------------
def read_payloads():
    if not PAYLOADS_F.exists():
        raise FileNotFoundError(f"{PAYLOADS_F} not found.")
    with open(PAYLOADS_F, "r", encoding="utf-8", errors="ignore") as fh:
        return [line.strip() for line in fh if line.strip()]


# ------------------- HTTP Request Helpers -------------------
def make_get_request_line(path):
    return f"GET {path} HTTP/1.1"


def make_post_request_line(path):
    return f"POST {path} HTTP/1.1"


# ------------------- HTTP Request Variants -------------------
def variant_url_path(payload):
    path = f"{BASE_PREFIX}/url/{urllib.parse.quote(payload, safe='')}"
    return "\n".join([make_get_request_line(path), "Accept: */*", f"User-Agent: {NORMAL_UA}", "", ""])


def variant_url_arg(payload):
    path = f"{BASE_PREFIX}/arg?q={urllib.parse.quote_plus(payload)}"
    return "\n".join([make_get_request_line(path), "Accept: */*", f"User-Agent: {NORMAL_UA}", "", ""])


def variant_url_arg_name(payload):
    path = f"{BASE_PREFIX}/arg-name?{urllib.parse.quote_plus(payload)}=value"
    return "\n".join([make_get_request_line(path), "Accept: */*", f"User-Agent: {NORMAL_UA}", "", ""])


def variant_cookie(payload):
    path = f"{BASE_PREFIX}/cookie"
    cookie_val = urllib.parse.quote(payload, safe='')
    return "\n".join([make_get_request_line(path), "Accept: */*", f"User-Agent: {NORMAL_UA}", f"Cookie: session={cookie_val}", "", ""])


def variant_header(payload):
    path = f"{BASE_PREFIX}/header"
    hdr_val = payload.replace("\r", " ").replace("\n", " ")
    return "\n".join([make_get_request_line(path), "Accept: */*", f"User-Agent: {NORMAL_UA}", f"X-Injection: {hdr_val}", "", ""])


def variant_body(payload):
    path = f"{BASE_PREFIX}/body"
    body = payload
    return "\n".join([
        make_post_request_line(path),
        "Accept: */*",
        f"User-Agent: {NORMAL_UA}",
        "Content-Type: application/x-www-form-urlencoded",
        f"Content-Length: {len(body.encode())}",
        "",
        body
    ])


def variant_body_arg(payload):
    path = f"{BASE_PREFIX}/body-arg"
    body = f"arg={urllib.parse.quote_plus(payload)}"
    return "\n".join([
        make_post_request_line(path),
        "Accept: */*",
        f"User-Agent: {NORMAL_UA}",
        "Content-Type: application/x-www-form-urlencoded",
        f"Content-Length: {len(body.encode())}",
        "",
        body
    ])


def variant_body_arg_name(payload):
    path = f"{BASE_PREFIX}/body-arg-name"
    body = f"{urllib.parse.quote_plus(payload)}=value"
    return "\n".join([
        make_post_request_line(path),
        "Accept: */*",
        f"User-Agent: {NORMAL_UA}",
        "Content-Type: application/x-www-form-urlencoded",
        f"Content-Length: {len(body.encode())}",
        "",
        body
    ])


def variant_json(payload):
    path = f"{BASE_PREFIX}/json"
    data = json.dumps({"test": payload})
    return "\n".join([
        make_post_request_line(path),
        "Accept: */*",
        f"User-Agent: {NORMAL_UA}",
        "Content-Type: application/json",
        f"Content-Length: {len(data.encode())}",
        "",
        data
    ])


def variant_xml(payload):
    path = f"{BASE_PREFIX}/xml"
    data = f"<root><test>{payload}</test></root>"
    return "\n".join([
        make_post_request_line(path),
        "Accept: */*",
        f"User-Agent: {NORMAL_UA}",
        "Content-Type: application/xml",
        f"Content-Length: {len(data.encode())}",
        "",
        data
    ])


# ------------------- Excel Handling -------------------
def load_existing_excel(path: Path):
    if path.exists():
        try:
            return pd.read_excel(path, engine="openpyxl")
        except Exception as e:
            raise RuntimeError(f"Failed reading Excel '{path}': {e}")
    return pd.DataFrame()


def append_rows_preserve(df_existing: pd.DataFrame, new_rows: list):
    df_new = pd.DataFrame(new_rows)
    if df_existing.empty:
        return df_new[["no", "Http-Requests"]]
    cols = list(df_existing.columns)
    aligned_new = [{c: (r[c] if c in r.index else pd.NA) for c in cols} for _, r in df_new.iterrows()]
    df_aligned_new = pd.DataFrame(aligned_new, columns=cols)
    combined = pd.concat([df_existing, df_aligned_new], ignore_index=True, sort=False)
    if "no" not in combined.columns: combined["no"] = pd.NA
    if "Http-Requests" not in combined.columns: combined["Http-Requests"] = pd.NA
    return combined


# ------------------- Main -------------------
def choose_targets():
    print("Choose targets to generate HTTP requests:")
    print("1. URL\n2. Arguments at URL\n3. Argument Names at URL\n4. Cookie\n5. Headers")
    print("6. Body\n7. Argument in Body\n8. Argument Names at Body\n9. JSON\n10. XML\n11. All")
    choices = input("Enter comma-separated numbers (e.g., 1,3,5): ")
    selected = set(int(c.strip()) for c in choices.split(",") if c.strip().isdigit() and 1 <= int(c.strip()) <= 11)
    mapping = {
        1: variant_url_path,
        2: variant_url_arg,
        3: variant_url_arg_name,
        4: variant_cookie,
        5: variant_header,
        6: variant_body,
        7: variant_body_arg,
        8: variant_body_arg_name,
        9: variant_json,
        10: variant_xml
    }
    return list(mapping.values()) if 11 in selected else [mapping[i] for i in selected]


def main():
    payloads = read_payloads()
    if not payloads:
        print("[!] No payloads found in payloads.txt")
        return

    df_exist = load_existing_excel(EXCEL_F)
    current_no = int(pd.to_numeric(df_exist["no"], errors="coerce").max(skipna=True)) if "no" in df_exist.columns and not df_exist["no"].isna().all() else 0

    variants = choose_targets()
    new_rows = []

    for payload in payloads:
        for fn in variants:
            current_no += 1
            new_rows.append({"no": current_no, "Http-Requests": fn(payload)})

    combined = append_rows_preserve(df_exist, new_rows)
    combined.to_excel(EXCEL_F, index=False, engine="openpyxl")
    print(f"[+] Appended {len(new_rows)} request rows to '{EXCEL_F}' (starting from no {current_no - len(new_rows) + 1})")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[!] Error: {e}")
