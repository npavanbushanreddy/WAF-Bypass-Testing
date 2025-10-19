# WAF-Bypass-Testing

A Python utility to replay HTTP requests stored in an Excel sheet, supporting proxying (e.g. BurpSuite), randomized rate limiting, and real-time request insights with ETA.

## Requirements

```bash
pip install -r requirements.txt
```

## Usage

1. Prepare `Payload-Requests.xlsx` with a column named `Http-Requests`.
2. Run:

```bash
python main.py
```

Follow prompts to set the target domain, proxy, and rate limit. Results saved to `Output_Result.xlsx`.
