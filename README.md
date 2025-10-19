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
#### References :

###### Cross-site Scripting (XSS)

* 👉 https://www.owasp.org/index.php/Cross-site_Scripting_(XSS)

###### XSS (Cross Site Scripting) Prevention Cheat Sheet

* 👉 https://www.owasp.org/index.php/XSS_(Cross_Site_Scripting)_Prevention_Cheat_Sheet

###### DOM based XSS Prevention Cheat Sheet

* 👉 https://www.owasp.org/index.php/DOM_based_XSS_Prevention_Cheat_Sheet

###### Testing for Reflected Cross site scripting (OTG-INPVAL-001)

* 👉 https://www.owasp.org/index.php/Testing_for_Reflected_Cross_site_scripting_(OTG-INPVAL-001)

###### Testing for Stored Cross site scripting (OTG-INPVAL-002)

* 👉 https://www.owasp.org/index.php/Testing_for_Stored_Cross_site_scripting_(OTG-INPVAL-002)

###### Testing for DOM-based Cross site scripting (OTG-CLIENT-001)

* 👉 https://www.owasp.org/index.php/Testing_for_DOM-based_Cross_site_scripting_(OTG-CLIENT-001)

###### DOM Based XSS

* 👉 https://www.owasp.org/index.php/DOM_Based_XSS

###### Cross-Site Scripting (XSS) Cheat Sheet | Veracode

* 👉 https://www.veracode.com/security/xss

#### Recommended books :

* [XSS Attacks: Cross-site Scripting Exploits and Defense](https://books.google.com.tr/books/about/XSS_Attacks.html?id=dPhqDe0WHZ8C)

* [XSS Cheat Sheet](https://leanpub.com/xss)


### Cloning an Existing Repository ( Clone with HTTPS )
```
root@ismailtasdelen:~# git clone https://github.com/ismailtasdelen/xss-payload-list.git
```

### Cloning an Existing Repository ( Clone with SSH )
```
root@ismailtasdelen:~# git clone git@github.com:ismailtasdelen/xss-payload-list.git
```

### Published Website :

##### Kitploit - https://www.kitploit.com/2018/05/xss-payload-list-cross-site-scripting.html

* SQL Injection ( OWASP )

👉 https://www.owasp.org/index.php/SQL_Injection

* Blind SQL Injection

👉 https://www.owasp.org/index.php/Blind_SQL_Injection

* Testing for SQL Injection (OTG-INPVAL-005)

👉 https://www.owasp.org/index.php/Testing_for_SQL_Injection_(OTG-INPVAL-005)

* SQL Injection Bypassing WAF

👉 https://www.owasp.org/index.php/SQL_Injection_Bypassing_WAF

* Reviewing Code for SQL Injection

👉 https://www.owasp.org/index.php/Reviewing_Code_for_SQL_Injection

* PL/SQL:SQL Injection

👉 https://www.owasp.org/index.php/PL/SQL:SQL_Injection

* Testing for NoSQL injection

👉 https://www.owasp.org/index.php/Testing_for_NoSQL_injection

* SQL Injection Injection Prevention Cheat Sheet 

👉 https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html

* SQL Injection Query Parameterization Cheat Sheet 

👉 https://cheatsheetseries.owasp.org/cheatsheets/Query_Parameterization_Cheat_Sheet.html
