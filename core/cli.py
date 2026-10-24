import argparse, json, sys
from .engine import validate_records

def main():
    p=argparse.ArgumentParser(description="Model Explanation Consistency Agent")
    p.add_argument("predictions")
    p.add_argument("explanations")
    p.add_argument("--config")
    p.add_argument("--output",default="explanation-report.json")
    args=p.parse_args()
    try:
        report=validate_records(args.predictions,args.explanations,args.config)
        with open(args.output,"w",encoding="utf-8") as f:
            json.dump(report,f,indent=2,ensure_ascii=False); f.write("\n")
        print(json.dumps({"status":report["status"],"output":args.output,"severity_counts":report["severity_counts"]},indent=2))
        return 1 if report["status"]=="error" else 0
    except (OSError,ValueError,json.JSONDecodeError) as exc:
        print(f"Error: {exc}",file=sys.stderr); return 2

if __name__=="__main__":
    raise SystemExit(main())
