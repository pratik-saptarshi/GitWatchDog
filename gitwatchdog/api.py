"""
API & Extensibility: Export analysis results in JSON/CSV for research integration.
"""
import json
import pandas as pd

def export_json(results, filename):
    with open(filename, 'w') as f:
        json.dump(results, f, default=str, indent=2)

def export_csv(results, filename):
    # Flatten results for CSV export
    flat = {}
    for k, v in results.items():
        if isinstance(v, dict):
            for subk, subv in v.items():
                flat[f"{k}_{subk}"] = subv
        else:
            flat[k] = v
    df = pd.DataFrame([flat])
    df.to_csv(filename, index=False)
