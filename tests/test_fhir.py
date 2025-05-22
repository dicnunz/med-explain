import base64
import os
import sys
from jsonschema import validate

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fhir import build_diagnostic_report


# Minimal schema fragment for DiagnosticReport
SCHEMA = {
    "type": "object",
    "required": [
        "resourceType",
        "meta",
        "status",
        "category",
        "code",
        "subject",
        "effectiveDateTime",
        "issued",
        "presentedForm",
    ],
    "properties": {
        "resourceType": {"const": "DiagnosticReport"},
        "meta": {
            "type": "object",
            "required": ["profile"],
            "properties": {
                "profile": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                }
            },
        },
        "status": {"type": "string"},
        "category": {"type": "array"},
        "code": {"type": "object"},
        "subject": {"type": "object"},
        "effectiveDateTime": {"type": "string"},
        "issued": {"type": "string"},
        "presentedForm": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["contentType", "data"],
                "properties": {
                    "contentType": {"type": "string"},
                    "data": {"type": "string"},
                },
            },
        },
    },
}


def test_build_diagnostic_report_schema():
    summary = "Example summary"
    report = build_diagnostic_report(summary)
    # validate against minimal schema derived from HL7 FHIR R4
    validate(instance=report, schema=SCHEMA)
    # ensure that presentedForm contains the summary encoded in base64
    data = report["presentedForm"][0]["data"]
    assert base64.b64decode(data).decode() == summary
