#!/usr/bin/env bash
set -euo pipefail

# Helper script to run ZAP baseline or full scans locally using Docker.
# Usage: ./scripts/run_zap_local.sh baseline|full

MODE=${1:-baseline}
PORT=3000
APP_IMAGE=cicd-demo:test

function ensure_app() {
  mvn clean package -DskipTests
  docker build -t ${APP_IMAGE} .
  docker run -d -p ${PORT}:${PORT} --name cicd-demo-app ${APP_IMAGE}
  echo "Waiting for app to be ready on http://localhost:${PORT} ..."
  timeout 60 bash -c "until curl -fsS http://localhost:${PORT}/; do sleep 2; done"
}

function cleanup() {
  docker stop cicd-demo-app >/dev/null 2>&1 || true
  docker rm cicd-demo-app >/dev/null 2>&1 || true
}

trap cleanup EXIT

ensure_app

if [ "${MODE}" = "baseline" ]; then
  docker run -v $(pwd):/zap/wrk/:rw -t ghcr.io/zaproxy/zaproxy:stable \
    zap-baseline.py -t http://localhost:${PORT} -r report_html.html -J report_json.json -a
  echo "Baseline report: report_html.html, report_json.json"
  # Convert to SARIF and screenshot HTML
  if command -v python3 >/dev/null 2>&1; then
    python3 scripts/convert-zap-to-sarif.py report_json.json zap_report.sarif || true
    if command -v node >/dev/null 2>&1; then
      (cd $(pwd) && npm install puppeteer --no-audit --no-fund) || true
      node scripts/screenshot_report.js report_html.html zap_report.png || true
      echo "Generated zap_report.sarif and zap_report.png"
    fi
  fi
else
  docker run -v $(pwd):/zap/wrk/:rw -t ghcr.io/zaproxy/zaproxy:stable \
    zap-full-scan.py -t http://localhost:${PORT} -r report_html.html -J report_json.json -a
  echo "Full report: report_html.html, report_json.json"
  if command -v python3 >/dev/null 2>&1; then
    python3 scripts/convert-zap-to-sarif.py report_json.json zap_report.sarif || true
    if command -v node >/dev/null 2>&1; then
      (cd $(pwd) && npm install puppeteer --no-audit --no-fund) || true
      node scripts/screenshot_report.js report_html.html zap_report.png || true
      echo "Generated zap_report.sarif and zap_report.png"
    fi
  fi
fi
