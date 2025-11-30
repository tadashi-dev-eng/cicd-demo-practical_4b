#!/usr/bin/env python3
import json
import sys
import argparse

def convert_zap_to_sarif(zap_json_file, sarif_output_file):
    with open(zap_json_file, 'r') as f:
        zap_data = json.load(f)

    sarif = {
        "version": "2.1.0",
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "OWASP ZAP",
                    "version": "2.14.0",
                    "informationUri": "https://www.zaproxy.org/",
                    "rules": []
                }
            },
            "results": []
        }]
    }

    def map_risk_level(risk_code):
        mapping = {
            '3': 'error',    # High
            '2': 'warning',  # Medium
            '1': 'note',     # Low
            '0': 'none'      # Informational
        }
        return mapping.get(str(risk_code), 'warning')

    # Build a small set of rules metadata for the SARIF tool driver
    rules_index = {}
    for site in zap_data.get('site', []):
        for alert in site.get('alerts', []):
            pid = str(alert.get('pluginid', '0'))
            if pid not in rules_index:
                rules_index[pid] = {
                    "id": pid,
                    "name": alert.get('alert', pid),
                    "shortDescription": {"text": alert.get('alert', '')},
                    "fullDescription": {"text": alert.get('description', '')},
                    "helpUri": alert.get('reference', '') or f"https://www.zaproxy.org/",
                    "properties": {
                        "tags": ["owasp", "zap", alert.get('confidence', '')]
                    }
                }

    sarif['runs'][0]['tool']['driver']['rules'] = list(rules_index.values())

    for site in zap_data.get('site', []):
        for alert in site.get('alerts', []):
            pid = str(alert.get('pluginid', '0'))
            instances = alert.get('instances', []) or []
            loc_uri = alert.get('url', '')
            if instances:
                try:
                    loc_uri = instances[0].get('uri', loc_uri)
                except Exception:
                    pass

            message_text = alert.get('alert', '')
            if alert.get('evidence'):
                message_text += f"\nEvidence: {alert.get('evidence')}"

            result = {
                "ruleId": pid,
                "level": map_risk_level(alert.get('riskcode', '2')),
                "message": { "text": message_text },
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": { "uri": loc_uri }
                    }
                }],
                "properties": {
                    "confidence": alert.get('confidence', ''),
                    "riskcode": alert.get('riskcode', ''),
                    "param": alert.get('param', ''),
                    "solution": alert.get('solution', '')
                }
            }
            sarif['runs'][0]['results'].append(result)

    with open(sarif_output_file, 'w') as f:
        json.dump(sarif, f, indent=2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert ZAP JSON to SARIF')
    parser.add_argument('zap_json', help='ZAP JSON file (zap_report.json)')
    parser.add_argument('sarif_out', help='SARIF output file (zap_report.sarif)')
    args = parser.parse_args()
    convert_zap_to_sarif(args.zap_json, args.sarif_out)
