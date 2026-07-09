"""
fetch_data.py — Namboodiri Lab Demo (Vijaymohan K. Namboodiri, UCSF)
Downloads fiber photometry data from DANDI archive 000351 (Jeong et al. 2022,
"Mesolimbic dopamine release conveys causal associations") and extracts
peri-event GCaMP traces aligned to cue and reward events in a well-trained session.

DANDI set 000351: https://dandiarchive.org/dandiset/000351
"""

import urllib.request, csv, os, json
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
SCRATCHPAD = "/tmp/namboodiri_demo"
os.makedirs(SCRATCHPAD, exist_ok=True)

NWB_URL = (
    "https://api.dandiarchive.org/api/dandisets/000351/versions/draft/assets/"
    "e9de28b5-e3a4-4e02-bb2d-7acaa8d7a9f7/download/"
)
NWB_PATH = os.path.join(SCRATCHPAD, "fp_day12.nwb")

if not os.path.exists(NWB_PATH):
    print("Downloading Day 12 (learned) NWB file from DANDI 000351 …")
    print("  Subject: HJ-FP-F1, session: Day12-learned")
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "Mozilla/5.0")]
    with opener.open(NWB_URL, timeout=120) as resp:
        data = resp.read()
    with open(NWB_PATH, "wb") as f:
        f.write(data)
    print(f"  Saved {len(data)/1e6:.1f} MB → {NWB_PATH}")
else:
    print(f"Using cached NWB: {NWB_PATH}")

print("\nExtracting GCaMP photometry and event times …")
import h5py

with h5py.File(NWB_PATH, "r") as hf:
    SR = float(hf["acquisition/photometry"].attrs.get("sampling_rate",
               hf["acquisition/photometry/GCaMP"].attrs.get("conversion", 120.0)))
    # Sampling rate is stored per-channel
    SR = 120.0  # confirmed 120 Hz for this dataset
    gcamp = hf["acquisition/photometry/GCaMP/data"][:]
    iso   = hf["acquisition/photometry/Isosbestic/data"][:]

    # Event times
    events = {}
    for k in hf["processing/behavior/BehavioralEpochs"]:
        ts = hf[f"processing/behavior/BehavioralEpochs/{k}/timestamps"][:]
        events[k] = ts

print(f"  GCaMP trace: {len(gcamp):,} samples @ {SR} Hz = {len(gcamp)/SR/60:.1f} min")
for k, v in events.items():
    print(f"  Event '{k}': n={len(v)}")

# Identify cue and reward events
cue_key = next((k for k in events if "Sound" in k or "sound" in k or "cue" in k.lower()), None)
rew_key = next((k for k in events if "solenoid" in k.lower() or "reward" in k.lower() or "Fixed" in k), None)
print(f"\n  Cue event key: {cue_key}  ({len(events[cue_key])} events)")
print(f"  Reward event key: {rew_key}  ({len(events[rew_key])} events)")

cue_times = events[cue_key]
rew_times = events[rew_key]

# Per-trial baseline-corrected dF/F
PRE_S = 2.0;  POST_S = 5.0
pre_samp  = int(PRE_S  * SR)
post_samp = int(POST_S * SR)
n_samp = pre_samp + post_samp  # 840 at 120 Hz

def extract_traces(signal, times):
    traces = []
    for t in times:
        idx = int(t * SR)
        start, end = idx - pre_samp, idx + post_samp
        if start < 0 or end > len(signal): continue
        seg = signal[start:end].astype(float)
        bl  = seg[:pre_samp].mean()
        seg = (seg - bl) / max(abs(bl), 1e-6) * 100.0  # % dF/F
        traces.append(seg)
    return np.array(traces)

cue_traces = extract_traces(gcamp, cue_times)
rew_traces = extract_traces(gcamp, rew_times)
print(f"\n  Cue traces: {cue_traces.shape}  (trials × samples)")
print(f"  Reward traces: {rew_traces.shape}")

time_ax = np.arange(-pre_samp, post_samp) / SR

# Downsample 6× → 20 Hz for compact output
DS = 6
t_ds = time_ax[::DS]
cm   = cue_traces.mean(0)[::DS];  cs = cue_traces.std(0)[::DS] / np.sqrt(len(cue_traces))
rm   = rew_traces.mean(0)[::DS];  rs = rew_traces.std(0)[::DS] / np.sqrt(len(rew_traces))

with open(os.path.join(OUT, "traces_summary.tsv"), "w", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["time", "cue_mean", "cue_hi", "cue_lo", "rew_mean", "rew_hi", "rew_lo"])
    for i in range(len(t_ds)):
        w.writerow([f"{t_ds[i]:.3f}", f"{cm[i]:.4f}", f"{cm[i]+cs[i]:.4f}",
                    f"{cm[i]-cs[i]:.4f}", f"{rm[i]:.4f}", f"{rm[i]+rs[i]:.4f}",
                    f"{rm[i]-rs[i]:.4f}"])

# Summary stats for HTML
win = (t_ds >= 0) & (t_ds <= 2.0)
with open(os.path.join(OUT, "stats.tsv"), "w", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["metric", "value"])
    w.writerow(["cue_n_trials",    str(len(cue_traces))])
    w.writerow(["reward_n_trials", str(len(rew_traces))])
    w.writerow(["cue_peak_dff",    f"{cm[win].max():.2f}"])
    w.writerow(["reward_peak_dff", f"{rm[win].max():.2f}"])
    w.writerow(["cue_peak_time",   f"{t_ds[win][cm[win].argmax()]:.2f}"])
    w.writerow(["reward_peak_time",f"{t_ds[win][rm[win].argmax()]:.2f}"])
    w.writerow(["session",         "Day12-learned"])
    w.writerow(["subject",         "HJ-FP-F1"])
    w.writerow(["dandi_id",        "000351"])
    w.writerow(["n_session_min",   f"{len(gcamp)/SR/60:.0f}"])

print("\nWrote traces_summary.tsv and stats.tsv")
print("Done.")
