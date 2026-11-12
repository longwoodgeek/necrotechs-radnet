"""LinkProbe 0.2-dev: offline synthetic evidence generator; NO RF transport."""
import argparse, csv, hashlib, json, random, statistics, time, uuid
from datetime import datetime, timezone
from pathlib import Path

FIELDS = ("schema_version","run_id","sequence","started_utc","elapsed_monotonic_s","payload_bytes","acknowledged","rtt_ms","error","mode")

def simulate(count=5, payload_bytes=64, seed=1, loss=0.0, latency_ms=450.0, timeout=15.0):
    if not 1 <= count <= 100000 or not 1 <= payload_bytes <= 65535 or not 0 <= loss <= 1 or latency_ms < 0 or timeout <= 0:
        raise ValueError("invalid simulation parameters")
    rng = random.Random(seed)
    run_id = str(uuid.uuid4())
    rows = []
    start = time.monotonic()
    for seq in range(1, count + 1):
        rtt = max(0.0, latency_ms * (1 + rng.uniform(-0.1, 0.1)))
        ack = rng.random() >= loss and rtt <= timeout * 1000
        rows.append(dict(schema_version=1, run_id=run_id, sequence=seq,
            started_utc=datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            elapsed_monotonic_s=round(time.monotonic()-start, 6),
            payload_bytes=payload_bytes, acknowledged=ack,
            rtt_ms=round(rtt, 3) if ack else "", error="" if ack else "synthetic_loss_or_timeout",
            mode="simulation"))
    return rows

def summarize(rows, elapsed_s=None):
    seen = set()
    for row in rows:
        key = (row["run_id"], int(row["sequence"]))
        if key in seen:
            raise ValueError("duplicate run_id/sequence")
        seen.add(key)
    acked = [r for r in rows if str(r["acknowledged"]).lower() in ("true","1","yes")]
    rtts = [float(r["rtt_ms"]) for r in acked if r["rtt_ms"] not in ("", None)]
    return dict(total=len(rows), acknowledged=len(acked),
        ack_rate=len(acked)/len(rows) if rows else None,
        median_rtt_ms=statistics.median(rtts) if rtts else None,
        max_rtt_ms=max(rtts) if rtts else None,
        paced_goodput_bps=8*sum(int(r["payload_bytes"]) for r in acked)/elapsed_s if elapsed_s and elapsed_s > 0 else None,
        modes=sorted(set(r.get("mode","unknown") for r in rows)),
        rtt_semantics="application round-trip, not one-way or raw RF throughput")

def export(rows, prefix):
    prefix = Path(prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    csv_path, json_path = prefix.with_suffix(".csv"), prefix.with_suffix(".json")
    if csv_path.exists() or json_path.exists():
        raise FileExistsError("evidence exists: choose another output prefix")
    with csv_path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    report = dict(schema_version=1, tool="LinkProbe", summary=summarize(rows),
        csv_sha256=hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        warning="SYNTHETIC DATA: no RF transmission; no measured RTT or link performance")
    with json_path.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return csv_path, json_path

def main(argv=None):
    parser = argparse.ArgumentParser(description="LinkProbe offline test-data tooling")
    sub = parser.add_subparsers(dest="command", required=True)
    sim = sub.add_parser("simulate", help="SYNTHETIC ONLY: no radio or network")
    sim.add_argument("--count", type=int, default=5)
    sim.add_argument("--payload-bytes", type=int, default=64)
    sim.add_argument("--seed", type=int, default=1)
    sim.add_argument("--loss", type=float, default=0)
    sim.add_argument("--latency-ms", type=float, default=450)
    sim.add_argument("--timeout", type=float, default=15)
    sim.add_argument("--output", required=True)
    summary = sub.add_parser("summarize", help="read schema-v1 CSV without changing it")
    summary.add_argument("csv_file")
    args = parser.parse_args(argv)
    try:
        if args.command == "simulate":
            rows = simulate(args.count, args.payload_bytes, args.seed, args.loss, args.latency_ms, args.timeout)
            paths = export(rows, args.output)
            print("SYNTHETIC DATA ONLY; NO RADIO TRANSMISSION")
            print("Saved:", *paths)
        else:
            with open(args.csv_file, newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                if not set(FIELDS).issubset(reader.fieldnames or []):
                    raise ValueError("requires LinkProbe schema-v1 CSV; legacy exports need an explicit adapter")
                rows = list(reader)
        print(json.dumps(summarize(rows), indent=2, sort_keys=True))
        return 0
    except (ValueError, OSError) as error:
        parser.exit(2, f"LinkProbe error: {error}\n")

if __name__ == "__main__":
    raise SystemExit(main())
