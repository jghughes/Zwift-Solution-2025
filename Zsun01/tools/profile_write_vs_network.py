"""
profile_write_vs_network.py
============================
Measures network-fetch time and aiofiles disk-write time independently
across the real ZwiftID URL pool, at the empirically optimal concurrency (20).

Three passes are timed:
  PASS 1  – Network only     (HTTP GET, response discarded — no write)
  PASS 2  – Write only       (pre-fetched bytes written to temp dir, no network)
  PASS 3  – Combined         (HTTP GET then aiofiles write, mirrors production)

The before/after split shows exactly which phase dominates per-task time.
A 10 % write:total ratio would mean disk is not the bottleneck.
A > 40 % ratio signals that aiofiles is worth optimising.

Usage:
	python tools/profile_write_vs_network.py

Writes temporary files under %TEMP%\\zwift_write_probe\\ and cleans up after.
No production directories are touched.
"""

import asyncio
import json
import os
import random
import shutil
import tempfile
import time
from typing import List, Tuple

import aiofiles
import httpx

# ---------------------------------------------------------------------------
# Configuration  (mirrors production values)
# ---------------------------------------------------------------------------

MEMBERSHIP_URL  = "https://data.zsunr.com/riders/json/active_members.json"
URL_ROOT        = "https://data.zsunr.com/riders/json/zwift/"
CONCURRENCY     = 20          # empirically tuned optimum
SAMPLE_SIZE     = 60          # enough for stable averages; finishes quickly
REQUEST_TIMEOUT = 20

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _fetch_only(
	client: httpx.AsyncClient,
	url: str,
	sem: asyncio.Semaphore,
	timings: List[float],
) -> bytes | None:
	"""GET url, record elapsed, return raw bytes."""
	async with sem:
		t0 = time.perf_counter()
		try:
			r = await client.get(url, timeout=REQUEST_TIMEOUT)
			r.raise_for_status()
		except Exception:
			return None
		finally:
			timings.append(time.perf_counter() - t0)
		return r.content


async def _write_only(
	dest_dir: str,
	filename: str,
	payload: bytes,
	sem: asyncio.Semaphore,
	timings: List[float],
) -> None:
	"""Write pre-fetched bytes to a temp file, record elapsed."""
	path = os.path.join(dest_dir, filename)
	async with sem:
		t0 = time.perf_counter()
		async with aiofiles.open(path, "wb") as f:
			await f.write(payload)
		timings.append(time.perf_counter() - t0)


async def _combined(
	client: httpx.AsyncClient,
	url: str,
	dest_dir: str,
	filename: str,
	sem: asyncio.Semaphore,
	net_timings: List[float],
	write_timings: List[float],
) -> None:
	"""Production path: fetch then write, recording each phase separately."""
	path = os.path.join(dest_dir, filename)
	async with sem:
		t_net0 = time.perf_counter()
		try:
			r = await client.get(url, timeout=REQUEST_TIMEOUT)
			r.raise_for_status()
		except Exception:
			return
		net_timings.append(time.perf_counter() - t_net0)

		t_write0 = time.perf_counter()
		async with aiofiles.open(path, "wb") as f:
			await f.write(r.content)
		write_timings.append(time.perf_counter() - t_write0)


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def _stats(values: List[float], label: str) -> dict:
	if not values:
		return {}
	total   = sum(values)
	avg     = total / len(values)
	mx      = max(values)
	mn      = min(values)
	print(f"  {label:<22} total={total*1000:8.1f} ms   avg={avg*1000:6.2f} ms   "
		  f"min={mn*1000:6.2f} ms   max={mx*1000:6.2f} ms   n={len(values)}")
	return {"total": total, "avg": avg, "max": mx, "min": mn, "n": len(values)}


# ---------------------------------------------------------------------------
# Pass runners
# ---------------------------------------------------------------------------

async def pass_network_only(
	client: httpx.AsyncClient,
	urls: List[str],
) -> Tuple[List[float], List[bytes]]:
	sem      = asyncio.Semaphore(CONCURRENCY)
	timings: List[float] = []
	payloads = await asyncio.gather(*[
		_fetch_only(client, url, sem, timings) for url in urls
	])
	return timings, [p for p in payloads if p is not None]


async def pass_write_only(
	dest_dir: str,
	payloads: List[bytes],
) -> List[float]:
	sem      = asyncio.Semaphore(CONCURRENCY)
	timings: List[float] = []
	await asyncio.gather(*[
		_write_only(dest_dir, f"f{i}.json", p, sem, timings)
		for i, p in enumerate(payloads)
	])
	return timings


async def pass_combined(
	client: httpx.AsyncClient,
	urls: List[str],
	dest_dir: str,
) -> Tuple[List[float], List[float]]:
	sem         = asyncio.Semaphore(CONCURRENCY)
	net_t: List[float]   = []
	write_t: List[float] = []
	filenames = [f"c{i}.json" for i in range(len(urls))]
	await asyncio.gather(*[
		_combined(client, url, dest_dir, fname, sem, net_t, write_t)
		for url, fname in zip(urls, filenames)
	])
	return net_t, write_t


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
	# --- load membership list ---
	print(f"Fetching membership list ...")
	with httpx.Client(timeout=30) as c:
		ids: List[str] = json.loads(c.get(MEMBERSHIP_URL).text)
	sample_ids = random.sample(ids, min(SAMPLE_SIZE, len(ids)))
	urls = [f"{URL_ROOT}{id}.json" for id in sample_ids]
	print(f"  {len(urls)} URLs sampled   concurrency={CONCURRENCY}\n")

	# --- temp directory ---
	tmp_dir = os.path.join(tempfile.gettempdir(), "zwift_write_probe")
	os.makedirs(tmp_dir, exist_ok=True)

	limits = httpx.Limits(
		max_connections=CONCURRENCY + 10,
		max_keepalive_connections=CONCURRENCY,
	)
	async with httpx.AsyncClient(limits=limits) as client:

		# ── PASS 1: network only ──────────────────────────────────────────
		print("PASS 1 — network only (fetch, discard payload, no disk write)")
		t_wall0 = time.perf_counter()
		net_timings, payloads = await pass_network_only(client, urls)
		wall_net = time.perf_counter() - t_wall0
		net_stats = _stats(net_timings, "network/task")
		print(f"  {'wall-clock total':<22} {wall_net*1000:8.1f} ms\n")

		if not payloads:
			print("ERROR: no payloads returned — check network / URL.")
			return

		# ── PASS 2: write only ────────────────────────────────────────────
		print(f"PASS 2 — write only (aiofiles, {len(payloads)} pre-fetched payloads)")
		t_wall0 = time.perf_counter()
		write_timings = await pass_write_only(tmp_dir, payloads)
		wall_write = time.perf_counter() - t_wall0
		write_stats = _stats(write_timings, "write/task")
		avg_bytes = sum(len(p) for p in payloads) / len(payloads)
		print(f"  {'wall-clock total':<22} {wall_write*1000:8.1f} ms")
		print(f"  {'avg payload':<22} {avg_bytes:8.0f} bytes\n")

		# ── PASS 3: combined (production path) ────────────────────────────
		print("PASS 3 — combined (production path: fetch + aiofiles write)")
		t_wall0 = time.perf_counter()
		comb_net_t, comb_write_t = await pass_combined(client, urls, tmp_dir)
		wall_combined = time.perf_counter() - t_wall0
		c_net_stats   = _stats(comb_net_t,   "network/task (combined)")
		c_write_stats = _stats(comb_write_t, "write/task   (combined)")
		print(f"  {'wall-clock total':<22} {wall_combined*1000:8.1f} ms\n")

	# --- cleanup ---
	shutil.rmtree(tmp_dir, ignore_errors=True)

	# ── Summary ───────────────────────────────────────────────────────────
	total_net_ms   = sum(comb_net_t)   * 1000
	total_write_ms = sum(comb_write_t) * 1000
	total_task_ms  = total_net_ms + total_write_ms
	write_pct      = 100 * total_write_ms / total_task_ms if total_task_ms else 0
	net_pct        = 100 * total_net_ms   / total_task_ms if total_task_ms else 0

	print("=" * 70)
	print("DIAGNOSIS")
	print(f"  Cumulative task time  network : {total_net_ms:8.1f} ms  ({net_pct:.1f} %)")
	print(f"  Cumulative task time  write   : {total_write_ms:8.1f} ms  ({write_pct:.1f} %)")
	print()

	if write_pct < 10:
		verdict = "NETWORK-BOUND — aiofiles write is negligible (<10 %). No write optimisation needed."
		action  = "Focus further tuning on concurrency, connection reuse, or server-side latency."
	elif write_pct < 30:
		verdict = "MOSTLY NETWORK-BOUND — write overhead is minor (10–30 %). aiofiles is acceptable."
		action  = "Consider buffered writes or Path.write_bytes() only if you need marginal gains."
	elif write_pct < 50:
		verdict = "MIXED — write overhead is significant (30–50 %). Worth investigating."
		action  = "Try replacing aiofiles with run_in_executor(None, path.write_bytes, data) to use a thread pool."
	else:
		verdict = "WRITE-BOUND — aiofiles write dominates (>50 %). Disk is the bottleneck."
		action  = "Replace aiofiles with loop.run_in_executor(None, path.write_bytes, data) and/or batch writes."

	print(f"  Verdict : {verdict}")
	print(f"  Action  : {action}")
	print("=" * 70)


if __name__ == "__main__":
	asyncio.run(main())
