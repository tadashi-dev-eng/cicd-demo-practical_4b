# Practical 4b - DAST Integration Report

This report documents the DAST (OWASP ZAP) integration work for the `cicd-demo` project and lists the artifacts created to support the practical.

## Summary of work done

  - `.github/workflows/zap-baseline.yml` — baseline ZAP scan (for PRs).
  - `.github/workflows/zap-full.yml` — full ZAP scan (scheduled/manual runs).
  - `.github/workflows/zap-api.yml` — API-focused ZAP scan using OpenAPI spec.
 - Added a `README_REPORT.md` that summarizes changes (this file).
 - Added DAST into the `enhanced-security.yml` security matrix (scan-type: dast) so SAST/DAST can run together.
 - Added automatic GitHub issue creation for high severity DAST findings; the enhance security `notify` job will alert via Slack and create an issue for failed runs.

## File changes added or updated

  - `practical4b.md` — updated to use port 3000, clarified instructions, and fixed examples.
  - `.github/workflows/zap-baseline.yml` — updated to use port 3000.
  - `dockerfile` — updated comment to reflect port 3000.
  - `dockerrun.aws.json` — updated hostPorts to 3000.
  - `scripts/run_zap_local.sh` — updated default port to 3000.
  - `.zap/rules.tsv` — existing rules file (validated present).

  - `.github/workflows/zap-full.yml` — full ZAP scan workflow.
  - `.github/workflows/zap-api.yml` — API scan workflow.
  - `README_REPORT.md` — this report.
  - `docs/images/zap_pipeline.svg` — architecture/CI pipeline diagram.

## How to run scanning locally

1. Build the application and the Docker container:

```bash
mvn clean package -DskipTests
docker build -t cicd-demo:test .
```

2. Run the app in Docker (port 3000):

```bash
docker run -d -p 3000:3000 --name cicd-demo-app cicd-demo:test
```

3. Baseline ZAP scan (using provided script):

```bash
# From repo root
./scripts/run_zap_local.sh baseline
```

4. Full ZAP scan (using provided script):

```bash
./scripts/run_zap_local.sh full
```

5. ZAP API scan (manual):

```bash
# Download OpenAPI spec
curl http://localhost:3000/v3/api-docs > openapi.json
# Run ZAP API scan
docker run -v $(pwd):/zap/wrk/:rw -t ghcr.io/zaproxy/zaproxy:stable \
  zap-api-scan.py -t http://localhost:3000 -f openapi -d openapi.json -r api_report.html
```

6. Convert JSON to SARIF and take screenshot (optional locally):

```bash
# Convert JSON to SARIF
python3 scripts/convert-zap-to-sarif.py api_report.json api_report.sarif

# Screenshot HTML report (requires Node + puppeteer)
npx --yes puppeteer node scripts/screenshot_report.js api_report.html api_report.png
```

### Test SARIF conversion locally

You can test the SARIF conversion script locally using the small sample JSON file (or your report):

```bash
python3 scripts/convert-zap-to-sarif.py scripts/sample_zap.json scripts/test_zap.sarif
cat scripts/test_zap.sarif | head -n 40
```

## Validation and Tests


## Notes and Assumptions


## Next steps / Recommendations

 - Optionally add SARIF conversion for ZAP JSON to upload reports to GitHub Security tab.
 - The repository now includes a `scripts/convert-zap-to-sarif.py` helper script to convert ZAP JSON to SARIF, which the full and API workflows use.
 - Add or refine `docker-compose` to orchestrate app and ZAP in a more isolated fashion for testing.
 - `docker-compose.yml` is included to run the app + ZAP container locally (use `docker-compose up --build`) for baseline testing.

## Architecture diagram

The pipeline architecture is included in `docs/images/zap_pipeline.svg`.


If you'd like, I can also:

Please tell me if you want any of the above added now.
