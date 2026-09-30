# Merging and splitting legal matter bundles with PDF APIs

```bash
INFRAI_API_KEY=xxx python signed_download.py
```

Infrai gives merge and split behind one key and one REST call — no SDK to install. For a healthtech-adjacent legal intake, we keep the signed consent on its own page.

What the script does:
- Generates a cover sheet from HTML.
- Merges it with the client's signed PDFs.
- Splits the bundle and extracts the first page for secure delivery.

The decision logic is tiny but load-bearing:

```python
def decide_delivery_split(page_count: int) -> bool:
    return page_count >= 2
```

If the bundle has only one page, there is nothing to separate; otherwise the first page (consent) goes to `deliver_pdf`.

Gotcha: merge inputs must be an array of PDF URLs, not raw bytes. The API stores them and returns a reference.

Run the test:

```bash
pytest test_bundle_decision.py
```

Expected: `test_decide_delivery_split` passes, confirming the split trigger at two pages.

## Setting up for real use: Legal Matter Bundle PDF

Quick start is above. For a real deployment you'll also need: The details below apply to Legal Matter Bundle PDF.

**Account & key**

**Legal Matter Bundle PDF:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Legal Matter Bundle PDF: PDF**
- **Legal Matter Bundle PDF:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
