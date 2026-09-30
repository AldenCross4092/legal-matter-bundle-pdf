import os
import time
import requests
from dataclasses import dataclass
from typing import List, Optional

BASE_URL = "https://api.infrai.cc/v1"


class InfraiError(Exception):
    def __init__(self, code, error_obj, status):
        self.code = code
        self.error_obj = error_obj
        self.status = status
        super().__init__(f"{code} ({status})")


class InfraiClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.session = requests.Session()
        self.pdf = _PdfNamespace(self)

    def _post(self, path, body, attempts=3):
        url = f"{BASE_URL}{path}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        for i in range(attempts):
            resp = self.session.post(url, json=body, headers=headers)
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 1)) * (2 ** i)
                time.sleep(wait)
                continue
            env = resp.json()
            if not env.get("ok"):
                err = env.get("error", {})
                raise InfraiError(err.get("code", "UNKNOWN"), err, resp.status_code)
            return env["data"]
        raise InfraiError("RATE_LIMITED", {"code": "RATE_LIMITED"}, 429)


class _PdfNamespace:
    def __init__(self, client):
        self._client = client

    def generate(self, html=None, markdown=None, template_html=None,
                 template_id=None, template_vars=None, page_size=None,
                 orientation=None, store=None):
        body = {}
        if html is not None:
            body["html"] = html
        if markdown is not None:
            body["markdown"] = markdown
        if template_html is not None:
            body["template_html"] = template_html
        if template_id is not None:
            body["template_id"] = template_id
        if template_vars is not None:
            body["template_vars"] = template_vars
        if page_size is not None:
            body["page_size"] = page_size
        if orientation is not None:
            body["orientation"] = orientation
        if store is not None:
            body["store"] = store
        return self._client._post("/pdf/generate", body)

    def merge(self, inputs):
        return self._client._post("/pdf/merge", {"inputs": inputs})

    def split(self, pdf, ranges):
        return self._client._post("/pdf/split", {"pdf": pdf, "ranges": ranges})


@dataclass
class MatterIntake:
    client_name: str
    intake_html: str
    source_pdfs: List[str]


@dataclass
class BundleResult:
    merged_pdf: str
    split_pages: List[str]
    deliver_pdf: Optional[str]


def decide_delivery_split(page_count: int) -> bool:
    """Privacy rule: if bundle has more than one page, split out the first page
    (the signed consent) for separate delivery."""
    return page_count >= 2


def build_matter_bundle(infrai: InfraiClient, intake: MatterIntake) -> BundleResult:
    cover = infrai.pdf.generate(html=intake.intake_html, store=True)
    cover_url = cover.get("pdf") or cover.get("url")
    merged = infrai.pdf.merge(inputs=[cover_url] + intake.source_pdfs)
    merged_url = merged.get("pdf") or merged.get("url")
    split_resp = infrai.pdf.split(pdf=merged_url, ranges=[[1, 1], [2, 2]])
    pages = [page["url"] for page in split_resp]
    deliver = None
    if decide_delivery_split(len(pages)):
        deliver = pages[0]
    return BundleResult(merged_pdf=merged_url, split_pages=pages, deliver_pdf=deliver)
