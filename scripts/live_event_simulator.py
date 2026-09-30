import os
import sys
import time
import json
import random
import argparse
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models.live_predictor import LivePredictor
from src.utils.config import SERVICE_CATEGORIES, BRANCHES, PROCESSED_DATA_DIR


def generate_live_events(surge: bool = False, count: int = 20, delay_seconds: float = 0.5):
    """Simulates real-time banking branch event stream with optional surge traffic."""

    predictor = LivePredictor()
    output_file = PROCESSED_DATA_DIR / "live_events.jsonl"

    print("==========================================")
    print(f"  LIVE EVENT STREAM SIMULATOR ({'SURGE MODE ACTIVE [CRITICAL TRAFFIC]' if surge else 'NORMAL MODE'})")
    print("==========================================")
    print(f"Streaming events to stdout and {output_file}...\n")

    event_counter = 1000

    with open(output_file, "a") as f:
        for i in range(count):
            event_counter += 1
            event_id = f"EVT-{event_counter}"
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            branch = random.choice(BRANCHES)
            b_id = branch["branch_id"]
            service = random.choice(SERVICE_CATEGORIES)

            event_type = random.choice([
                "CUSTOMER_ARRIVAL", "SERVICE_STARTED", "SERVICE_COMPLETED",
                "STAFF_AVAILABLE", "STAFF_ABSENT"
            ])

            if surge:
                # Surge Traffic: 30-50 queue length & recent arrivals
                queue_length = random.randint(30, 50)
                recent_arrivals = random.randint(40, 60)
                staff_available = random.randint(1, 3)  # Depleted staff
            else:
                # Normal Traffic: 5-10 queue length
                queue_length = random.randint(3, 10)
                recent_arrivals = random.randint(5, 12)
                staff_available = random.randint(4, 8)

            token_num = f"{service[0].upper()}{random.randint(100, 999)}"

            # Run live prediction for the event state
            prediction = predictor.predict_live(
                branch_id=b_id,
                service_category=service,
                current_queue=queue_length,
                staff_available=staff_available,
                recent_arrivals=recent_arrivals,
                timestamp=ts
            )

            event = {
                "event_id": event_id,
                "branch_id": b_id,
                "timestamp": ts,
                "event_type": event_type,
                "service_category": service,
                "token_number": token_num,
                "queue_length": queue_length,
                "staff_available": staff_available,
                "prediction_output": prediction
            }

            event_json = json.dumps(event)
            print(f"[EVENT {i+1}/{count}] {b_id} | {service} | Queue: {queue_length} | Risk: {prediction['bottleneck_risk']}")
            print(f"  -> Explanation: {prediction['explanation']}\n")

            f.write(event_json + "\n")
            f.flush()

            time.sleep(delay_seconds)

    print(f"\nSimulation completed. {count} live events written to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Live Banking Branch Event Simulator")
    parser.add_argument("--surge", action="store_true", help="Enable surge mode (30-50 arrivals per interval)")
    parser.add_argument("--count", type=int, default=15, help="Number of simulated events to generate")
    parser.add_argument("--delay", type=float, default=0.2, help="Delay in seconds between events")

    args = parser.parse_args()
    generate_live_events(surge=args.surge, count=args.count, delay_seconds=args.delay)


if __name__ == "__main__":
    main()
