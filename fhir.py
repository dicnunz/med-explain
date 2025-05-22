from __future__ import annotations

import base64
import uuid
from datetime import datetime, timezone


def build_diagnostic_report(summary_text: str) -> dict:
    """Return a minimal US Core DiagnosticReport JSON for the given summary."""
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return {
        "resourceType": "DiagnosticReport",
        "id": str(uuid.uuid4()),
        "meta": {
            "profile": [
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-diagnosticreport-note"
            ]
        },
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                        "code": "LAB",
                        "display": "Laboratory",
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "11506-3",
                    "display": "Clinical summary note",
                }
            ],
            "text": "Summary",
        },
        "subject": {"reference": "Patient/example"},
        "effectiveDateTime": now,
        "issued": now,
        "presentedForm": [
            {
                "contentType": "text/plain",
                "data": base64.b64encode(summary_text.encode()).decode(),
            }
        ],
    }
