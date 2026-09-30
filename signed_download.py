#!/usr/bin/env python3
import os
from matter_bundle import InfraiClient, MatterIntake, build_matter_bundle

def main():
    infrai = InfraiClient()
    source = infrai.pdf.generate(
        html="<h1>Sample consent</h1><p>Demo PDF for bundle verification.</p>",
        store=True,
    )
    intake = MatterIntake(
        client_name="Jane Doe",
        intake_html="<h1>Health Matter Intake</h1><p>Consent to treatment.</p>",
        source_pdfs=[source.get("pdf") or source.get("url")],
    )
    result = build_matter_bundle(infrai, intake)
    print("Merged bundle:", result.merged_pdf)
    print("Delivery page:", result.deliver_pdf)
    print("Deadline follow-up set for 30 days.")

if __name__ == "__main__":
    main()
