"""
tune_concurrency.py
====================
Empirically finds the optimal asyncio concurrency value for the DaveK file-fetch
pipeline by sweeping concurrency levels against the real remote server and
measuring throughput (requests/second) at each level.

Usage:
	python tune_concurrency.py

The script prints a results table and a plain-text throughput chart, then writes
the recommendation to stdout so you can paste the value directly into
brute10_fetch_files_from_dk.py / zwiftid_file_fetcher_async.py.

Dependencies: httpx (already used by the production pipeline)
No files are written to disk — only HTTP HEAD requests are used so the
measurement is pure network latency / concurrency, not disk speed.
"""

import asyncio
import json
import random
import time
from typing import List

import httpx

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MEMBERSHIP_URL = "https://data.zsunr.com/riders/json/active_members.json"
URL_ROOT = "https://data.zsunr.com/riders/json/zwift/"

# Number of URLs to sample per sweep step.
# Large enough to be statistically stable; small enough to finish quickly.
SAMPLE_SIZE = 120

# Concurrency levels to probe.
CONCURRENCY_LEVELS = [1, 5, 10, 20, 30, 50, 75, 100, 150, 200]

# HTTP request timeout (seconds)
REQUEST_TIMEOUT = 20

# ---------------------------------------------------------------------------
# Core measurement
# ---------------------------------------------------------------------------

async def _probe(client: httpx.AsyncClient, url: str, semaphore: asyncio.Semaphore) -> bool:
	"""Issue one HEAD request; return True on 2xx/3xx, False otherwise."""
	async with semaphore:
		try:
			r = await client.head(url, timeout=REQUEST_TIMEOUT)
			return r.status_code < 400
		except Exception:
			return False


async def measure_concurrency(urls: List[str], concurrency: int) -> dict:
	"""
	Fire all URLs with the given concurrency cap and return timing stats.
	"""
	semaphore = asyncio.Semaphore(concurrency)
	limits = httpx.Limits(max_connections=concurrency + 10,
						  max_keepalive_connections=concurrency)
	t0 = time.perf_counter()
	async with httpx.AsyncClient(limits=limits) as client:
		results = await asyncio.gather(*[_probe(client, u, semaphore) for u in urls])
	elapsed = time.perf_counter() - t0
	successes = sum(results)
	return {
		"concurrency": concurrency,
		"elapsed_s": round(elapsed, 2),
		"successes": successes,
		"failures": len(urls) - successes,
		"rps": round(len(urls) / elapsed, 1),
	}


# ---------------------------------------------------------------------------
# Membership list fetch
# ---------------------------------------------------------------------------

def fetch_zwift_ids() -> List[str]:
	print(f"Fetching membership list from {MEMBERSHIP_URL} ...")
	with httpx.Client(timeout=30) as client:
		r = client.get(MEMBERSHIP_URL)
		r.raise_for_status()
		ids: List[str] = json.loads(r.text)
	print(f"  {len(ids)} ZwiftIDs loaded.")
	return ids


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------

BAR_WIDTH = 40

def _bar(value: float, max_value: float) -> str:
	filled = int(round(BAR_WIDTH * value / max_value)) if max_value else 0
	return "█" * filled + "░" * (BAR_WIDTH - filled)


def print_table(rows: List[dict]) -> None:
	print()
	print(f"{'Concurrency':>11}  {'Elapsed (s)':>11}  {'Successes':>9}  {'Failures':>8}  {'RPS':>7}")
	print("-" * 58)
	for r in rows:
		print(f"{r['concurrency']:>11}  {r['elapsed_s']:>11.2f}  {r['successes']:>9}  {r['failures']:>8}  {r['rps']:>7.1f}")


def print_chart(rows: List[dict]) -> None:
	max_rps = max(r["rps"] for r in rows) or 1
	print()
	print("Throughput chart (requests / second)")
	print(f"  {'Conc':>5}  {'RPS':>7}  Chart")
	print(f"  {'----':>5}  {'---':>7}  {'─' * BAR_WIDTH}")
	for r in rows:
		marker = " ◄ peak" if r["rps"] == max_rps else ""
		print(f"  {r['concurrency']:>5}  {r['rps']:>7.1f}  {_bar(r['rps'], max_rps)}{marker}")


def recommend(rows: List[dict]) -> int:
	"""
	Return the concurrency value where throughput first reaches >= 95 % of peak
	(the 'knee of the curve' — adding more connections beyond this gives < 5 %
	gain while increasing server load and error risk).
	"""
	max_rps = max(r["rps"] for r in rows)
	threshold = 0.95 * max_rps
	for r in rows:
		if r["rps"] >= threshold:
			return r["concurrency"]
	return rows[-1]["concurrency"]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
	ids = fetch_zwift_ids()

	if len(ids) < SAMPLE_SIZE:
		sample_ids = ids
	else:
		sample_ids = random.sample(ids, SAMPLE_SIZE)

	urls = [f"{URL_ROOT}{id}.json" for id in sample_ids]
	print(f"\nSweeping {len(CONCURRENCY_LEVELS)} concurrency levels using {len(urls)} sampled URLs ...\n")

	rows = []
	for level in CONCURRENCY_LEVELS:
		print(f"  concurrency={level:>3} ...", end="", flush=True)
		result = await measure_concurrency(urls, level)
		rows.append(result)
		print(f"  {result['elapsed_s']:.2f}s  {result['rps']:.1f} rps  ({result['failures']} failed)")

	print_table(rows)
	print_chart(rows)

	best = recommend(rows)
	peak_row = max(rows, key=lambda r: r["rps"])

	print()
	print("=" * 60)
	print(f"  Peak throughput : {peak_row['rps']:.1f} rps  at concurrency={peak_row['concurrency']}")
	print(f"  Recommended     : concurrency={best}  (first level reaching ≥95 % of peak)")
	print()
	print("  Set this value in:")
	print("    brute10_fetch_files_from_dk.py  →  fetch_and_save_files(..., concurrency=<value>)")
	print("    zwiftid_file_fetcher_async.py   →  download_and_save_many_files_to_hard_drive default")
	print("=" * 60)


if __name__ == "__main__":
	asyncio.run(main())
