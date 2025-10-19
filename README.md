# WAF-Bypass-Testing

A Python toolkit for generating and replaying HTTP requests for WAF / application testing.

> **Legal:** Only run these tools against targets you own or have explicit permission to test.

---

## Requirements

```bash
pip install -r requirements.txt
```

---

## 1) Replay / Main Script

Use the main script to replay HTTP requests stored in an Excel sheet. Features include proxy support, rate limiting, and ETA display.

1. Prepare `Payload-Requests.xlsx` with a column named `Http-Requests` (and optional `no` column).
2. Run the replay script:

```bash
python main.py
```

3. Follow prompts to set target domain, proxy, and rate limit.
4. Results are saved to `Output_Result.xlsx`.

---

## 2) Generate HTTP Requests from Payloads

If you don’t have HTTP requests yet, you can generate them from payloads saved in `payloads.txt`. The generated requests are saved to `Payload-Requests.xlsx` for later use in the main script.

1. Update `payloads.txt` with one payload per line. Example:

```
admin
' OR '1'='1
<script>alert(1)</script>
```

2. Run the generator script:

```bash
python request-generator.py
```

3. Choose which targets to generate when prompted:

* 1: URL path
* 2: Arguments at URL
* 3: Argument Names at URL
* 4: Cookie
* 5: Headers
* 6: Body (POST form)
* 7: Argument in Body
* 8: Argument Names at Body
* 9: JSON
* 10: XML
* 11: All

4. `Payload-Requests.xlsx` is created/updated with `no` and `Http-Requests` columns.
5. After generating requests, use `main.py` to simulate/replay the attacks.

---

## Example Workflow

```bash
# Generate requests from payloads
python request-generator.py

# Replay the generated requests
python main.py
```

---

## Notes

* The generator encodes payloads appropriately for each placement (URL, args, cookies, body, JSON, XML).
* Existing Excel columns are preserved; the generator appends new rows and continues numbering.

---

## requirements.txt

Save the following into `requirements.txt` in the repo root:

```
pandas
requests
tqdm
openpyxl
```
