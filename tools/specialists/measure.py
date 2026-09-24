#!/usr/bin/env python3
"""Bounded closed-workload measurement for this disposable lab, not a general load generator."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import math
from pathlib import Path
import threading
import time
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import build_opener, HTTPRedirectHandler, ProxyHandler, Request


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_):
        return None


def get(url, timeout):
    opener = build_opener(ProxyHandler({}), NoRedirect())
    with opener.open(Request(url), timeout=timeout) as response:
        return response.status, json.loads(response.read(4097))


def percentile(values, percent):
    return sorted(values)[max(0, math.ceil(len(values) * percent / 100) - 1)] if values else None


def measure(identity, *, requests=50, concurrency=1, timeout=1.0, duration=10.0,
            max_errors=3, p95_ms=40.0, error_rate=0.0, warmup=3):
    url = identity["url"]
    parsed = urlsplit(url)
    if (parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or not parsed.port
            or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment):
        raise ValueError("only a literal loopback lab origin is supported")
    limits = ((requests, 1, 1000), (concurrency, 1, 16), (timeout, 0.01, 5),
              (duration, 0.05, 30), (max_errors, 1, 100), (warmup, 0, 20))
    if any(not math.isfinite(v) or not low <= v <= high for v, low, high in limits):
        raise ValueError("workload exceeds helper limits")
    if not (math.isfinite(p95_ms) and p95_ms > 0 and math.isfinite(error_rate) and 0 <= error_rate <= 1):
        raise ValueError("invalid thresholds")
    _, actual = get(url + "/__identity", timeout)
    if (actual.get("fixture") != "qadrillion-specialist-lab" or actual.get("role") != "test"
            or any(actual.get(k) != identity.get(k) for k in ("run_id", "build", "mode", "url"))):
        raise ValueError("lab identity mismatch")
    warmup_samples = []
    for _ in range(warmup):
        start = time.monotonic()
        code, body = get(url + "/work", timeout)
        warmup_samples.append({"ms": (time.monotonic() - start) * 1000, "status": code})
        if code != 200 or body != {"ok": True}:
            raise ValueError("warmup business check failed")
    samples = []
    lock = threading.Lock()
    begin = time.monotonic()
    issued = errors = 0
    stop_reason = None

    def worker():
        nonlocal issued, errors, stop_reason
        while True:
            with lock:
                if errors >= max_errors:
                    stop_reason = "error budget"
                    return
                if time.monotonic() - begin >= duration:
                    stop_reason = "duration ceiling"
                    return
                if issued >= requests:
                    return
                number = issued
                issued += 1
            start = time.monotonic()
            status = None
            diagnostic = None
            try:
                status, body = get(url + "/work", min(timeout, duration))
                ok = status == 200 and body == {"ok": True}
                if not ok:
                    diagnostic = "business response mismatch"
            except Exception as exc:
                ok = False
                status = exc.code if isinstance(exc, HTTPError) else None
                diagnostic = type(exc).__name__
            sample = {"sequence": number, "ms": (time.monotonic() - start) * 1000,
                      "status": status, "ok": ok, "diagnostic": diagnostic}
            with lock:
                samples.append(sample)
                errors += not ok

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        list(pool.map(lambda _: worker(), range(concurrency)))
    elapsed = time.monotonic() - begin
    values = [s["ms"] for s in samples]
    successful = [s["ms"] for s in samples if s["ok"]]
    rate = errors / len(samples) if samples else 1.0
    tail = percentile(values, 95)
    passed = bool(samples) and len(samples) == requests and not stop_reason and tail <= p95_ms and rate <= error_rate
    return {"identity": actual, "model": "closed: next request after previous completes; no think time",
            "limits": {"requests": requests, "concurrency": concurrency, "timeout_s": timeout,
                       "duration_s": duration, "max_errors": max_errors},
            "thresholds": {"p95_ms": p95_ms, "error_rate": error_rate},
            "warmup": warmup_samples, "samples": sorted(samples, key=lambda s: s["sequence"]),
            "summary": {"count": len(samples), "errors": errors, "error_rate": rate, "elapsed_s": elapsed,
                        "throughput_per_s": len(samples) / elapsed, "p50_ms": percentile(values, 50),
                        "p95_ms": tail, "p99_ms": percentile(values, 99),
                        "success_p95_ms": percentile(successful, 95), "stop_reason": stop_reason,
                        "verdict": "pass" if passed else "fail"},
            "limits_of_claim": "local closed-workload sample, no production capacity claim; resource telemetry not collected"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--identity", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--requests", type=int, default=50)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=1.0)
    parser.add_argument("--duration", type=float, default=10.0)
    parser.add_argument("--max-errors", type=int, default=3)
    parser.add_argument("--p95-ms", type=float, default=40.0)
    parser.add_argument("--error-rate", type=float, default=0.0)
    parser.add_argument("--warmup", type=int, default=3)
    args = parser.parse_args()
    options = vars(args).copy()
    options.pop("out")
    options["identity"] = json.loads(args.identity.read_text())
    try:
        result = measure(**options)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, f"Measurement blocked: {exc}\n")
    with args.out.open("x") as handle:
        json.dump(result, handle, indent=2)
    print(json.dumps(result["summary"]))
    return 0 if result["summary"]["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
