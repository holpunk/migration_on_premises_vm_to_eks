import argparse
import json
import time
import os
from datetime import datetime

DB_FILE = "dora_metrics.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"deployments": []}
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"deployments": []}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

def track_event(args):
    db = load_db()
    
    timestamp = time.time()
    iso_time = datetime.fromtimestamp(timestamp).isoformat()
    
    event = {
        "timestamp": timestamp,
        "iso_time": iso_time,
        "commit_hash": args.commit,
        "event_type": args.event,
        "status": args.status
    }

    if args.event == "deployment":
        # Find if this deployment already exists (started)
        existing = next((d for d in db["deployments"] if d["commit_hash"] == args.commit), None)
        
        if args.status == "started":
            if not existing:
                db["deployments"].append({
                    "commit_hash": args.commit,
                    "start_time": timestamp,
                    "end_time": None,
                    "status": "in_progress"
                })
        elif args.status in ["success", "failure"]:
            if existing:
                existing["end_time"] = timestamp
                existing["status"] = args.status
            else:
                # Log a finished deployment even if we missed the start?
                db["deployments"].append({
                    "commit_hash": args.commit,
                    "start_time": timestamp, # Approximate
                    "end_time": timestamp,
                    "status": args.status
                })

    save_db(db)
    print(f"Tracked event: {args.event} - {args.status} for commit {args.commit}")

def calculate_metrics():
    db = load_db()
    deployments = db["deployments"]
    successful = [d for d in deployments if d["status"] == "success"]
    failed = [d for d in deployments if d["status"] == "failure"]
    total = len(deployments)
    
    if total == 0:
        print("No deployments found.")
        return

    # 1. Deployment Frequency
    print(f"Total Deployments: {total}")
    print(f"Successful Deployments: {len(successful)}")

    # 2. Lead Time for Changes (End - Start)
    lead_times = [d["end_time"] - d["start_time"] for d in successful if d["end_time"] and d["start_time"]]
    if lead_times:
        avg_lead_time = sum(lead_times) / len(lead_times)
        print(f"Average Lead Time: {avg_lead_time:.2f} seconds")
    else:
        print("Average Lead Time: N/A")

    # 3. Change Failure Rate
    failure_rate = (len(failed) / total) * 100 if total > 0 else 0
    print(f"Change Failure Rate: {failure_rate:.2f}%")

    # 4. Time to Restore (Simulated)
    # This assumes a subsequent success fixes a failure. 
    # For simulation, we'll just placeholder this.
    print("Time to Restore: Needs manual incident data")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    track_parser = subparsers.add_parser("track")
    track_parser.add_argument("--event", required=True, choices=["deployment"])
    track_parser.add_argument("--status", required=True, choices=["started", "success", "failure"])
    track_parser.add_argument("--commit", required=True)

    report_parser = subparsers.add_parser("report")

    args = parser.parse_args()

    if args.command == "track":
        track_event(args)
    elif args.command == "report":
        calculate_metrics()
    else:
        parser.print_help()
