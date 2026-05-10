from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]
BUILD_RECEIPT_URL = "https://nicdunz.gumroad.com/l/smrimu"
AGENT_BROWSER_OS_URL = "https://nicdunz.gumroad.com/l/agent-browser-operator-os"


def test_support_routes_and_boundaries_are_documented():
    readme = (ROOT / "README.md").read_text()
    normalized_readme = " ".join(readme.split())
    funding = (ROOT / ".github" / "FUNDING.yml").read_text()

    assert BUILD_RECEIPT_URL in readme
    assert BUILD_RECEIPT_URL in funding
    assert AGENT_BROWSER_OS_URL in readme
    assert AGENT_BROWSER_OS_URL in funding
    assert "does not unlock Med Explain features" in normalized_readme
    assert "does not include account access" in normalized_readme
    assert "guaranteed automation" in normalized_readme
    assert "PHI handling" in normalized_readme
    assert "medical advice" in normalized_readme


def test_project_metadata_exposes_patch_release_and_routes():
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text())
    project = metadata["project"]

    assert project["version"] == "0.1.1"
    assert project["urls"]["Funding"] == BUILD_RECEIPT_URL
    assert project["urls"]["Agent Browser Operator OS"] == AGENT_BROWSER_OS_URL
