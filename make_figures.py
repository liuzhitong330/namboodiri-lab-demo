"""
make_figures.py — Namboodiri Lab Demo
Figure 1: Peri-event GCaMP traces — cue vs reward in learned session (Day 12)
           showing mesolimbic dopamine dynamics during associative learning
Figure 2: Inter-reward interval controls learning rate
           conceptual diagram of the 2026 Nat Neurosci finding
"""

import csv, os, math

OUT = os.path.dirname(os.path.abspath(__file__))

# Load traces
rows = []
with open(os.path.join(OUT, "traces_summary.tsv")) as f:
    for row in csv.DictReader(f, delimiter="\t"):
        rows.append({k: float(v) for k, v in row.items()})

# Load stats
stats = {}
with open(os.path.join(OUT, "stats.tsv")) as f:
    for row in csv.DictReader(f, delimiter="\t"):
        stats[row["metric"]] = row["value"]

times    = [r["time"]     for r in rows]
cue_m    = [r["cue_mean"] for r in rows]
cue_hi   = [r["cue_hi"]  for r in rows]
cue_lo   = [r["cue_lo"]  for r in rows]
rew_m    = [r["rew_mean"] for r in rows]
rew_hi   = [r["rew_hi"]  for r in rows]
rew_lo   = [r["rew_lo"]  for r in rows]

# ── Figure 1: Peri-event dopamine traces ─────────────────────────────────────
FW, FH  = 700, 430
PAD_L   = 80
PAD_R   = 30
PAD_T   = 80
PAD_B   = 70
AW = FW - PAD_L - PAD_R
AH = FH - PAD_T - PAD_B

t_min, t_max = -2.0, 5.0
all_vals = cue_hi + cue_lo + rew_hi + rew_lo
y_min = min(all_vals) - 0.05
y_max = max(all_vals) + 0.08

def px(t):
    return PAD_L + (t - t_min) / (t_max - t_min) * AW

def py(v):
    return PAD_T + AH - (v - y_min) / (y_max - y_min) * AH

# Shaded bands
def band_path(hi, lo):
    pts = [(px(times[i]), py(hi[i])) for i in range(len(times))]
    pts += [(px(times[i]), py(lo[i])) for i in range(len(times)-1, -1, -1)]
    return "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"

rew_band = f'<path d="{band_path(rew_hi, rew_lo)}" fill="#e67e22" opacity="0.18"/>'
cue_band = f'<path d="{band_path(cue_hi, cue_lo)}" fill="#1a5c8a" opacity="0.18"/>'

def polyline(ys, col, width=2.0):
    pts = " ".join(f"{px(times[i]):.1f},{py(ys[i]):.1f}" for i in range(len(times)))
    return f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{width}" stroke-linejoin="round"/>'

rew_line = polyline(rew_m, "#e67e22", 2.2)
cue_line = polyline(cue_m, "#1a5c8a", 2.2)

# Axes
ax1 = (f'<line x1="{PAD_L}" y1="{PAD_T}" x2="{PAD_L}" y2="{PAD_T+AH}" stroke="#ccc" stroke-width="1.2"/>'
       f'<line x1="{PAD_L}" y1="{PAD_T+AH}" x2="{PAD_L+AW}" y2="{PAD_T+AH}" stroke="#ccc" stroke-width="1.2"/>')

# Baseline (y=0) dashed line
y0 = py(0)
ax1 += f'<line x1="{PAD_L}" y1="{y0:.1f}" x2="{PAD_L+AW}" y2="{y0:.1f}" stroke="#bbb" stroke-width="1" stroke-dasharray="4,3"/>'

# Event onset line
x0_line = px(0)
ax1 += f'<line x1="{x0_line:.1f}" y1="{PAD_T}" x2="{x0_line:.1f}" y2="{PAD_T+AH}" stroke="#888" stroke-width="1" stroke-dasharray="3,3"/>'
ax1 += (f'<text x="{x0_line:.1f}" y="{PAD_T-8}" text-anchor="middle" font-size="9" fill="#666">event onset</text>')

# X-axis ticks
xticks = ""
for t in [-2, -1, 0, 1, 2, 3, 4, 5]:
    tx = px(t)
    xticks += (f'<line x1="{tx:.1f}" y1="{PAD_T+AH}" x2="{tx:.1f}" y2="{PAD_T+AH+4}" stroke="#aaa" stroke-width="1"/>'
               f'<text x="{tx:.1f}" y="{PAD_T+AH+16}" text-anchor="middle" font-size="10" fill="#888">{t}s</text>')
xticks += (f'<text x="{PAD_L+AW/2:.0f}" y="{PAD_T+AH+34}" text-anchor="middle" font-size="10" fill="#555">'
           f'Time from event onset (s)</text>')

# Y-axis ticks
yticks = ""
y_tick_vals = [-0.5, 0.0, 0.5, 1.0]
for v in y_tick_vals:
    if v < y_min or v > y_max: continue
    ty = py(v)
    yticks += (f'<line x1="{PAD_L-4}" y1="{ty:.1f}" x2="{PAD_L}" y2="{ty:.1f}" stroke="#aaa" stroke-width="1"/>'
               f'<text x="{PAD_L-8}" y="{ty+4:.1f}" text-anchor="end" font-size="9" fill="#888">{v:.1f}%</text>')
yticks += (f'<text transform="rotate(-90,18,{PAD_T+AH/2:.0f})" x="18" y="{PAD_T+AH/2:.0f}" '
           f'text-anchor="middle" font-size="10" fill="#555">GCaMP dF/F (% Δ)</text>')

# Legend
leg1 = (f'<rect x="{PAD_L+AW-170}" y="{PAD_T+12}" width="160" height="56" '
        f'rx="4" fill="white" stroke="#ddd" stroke-width="1"/>')
leg1 += (f'<line x1="{PAD_L+AW-158}" y1="{PAD_T+30}" x2="{PAD_L+AW-140}" y2="{PAD_T+30}" '
         f'stroke="#e67e22" stroke-width="2.2"/>'
         f'<text x="{PAD_L+AW-134}" y="{PAD_T+34}" font-size="9.5" fill="#e67e22" font-weight="700">'
         f'Reward (n={stats["reward_n_trials"]})</text>')
leg1 += (f'<line x1="{PAD_L+AW-158}" y1="{PAD_T+52}" x2="{PAD_L+AW-140}" y2="{PAD_T+52}" '
         f'stroke="#1a5c8a" stroke-width="2.2"/>'
         f'<text x="{PAD_L+AW-134}" y="{PAD_T+56}" font-size="9.5" fill="#1a5c8a" font-weight="700">'
         f'Cue (CS, n={stats["cue_n_trials"]})</text>')

# Peak annotations
cue_pk_t  = float(stats["cue_peak_time"])
cue_pk_v  = float(stats["cue_peak_dff"])
rew_pk_t  = float(stats["reward_peak_time"])
rew_pk_v  = float(stats["reward_peak_dff"])

ann1 = (f'<circle cx="{px(rew_pk_t):.1f}" cy="{py(rew_pk_v):.1f}" r="4" '
        f'fill="none" stroke="#e67e22" stroke-width="1.5"/>'
        f'<text x="{px(rew_pk_t)+8:.1f}" y="{py(rew_pk_v)-6:.1f}" '
        f'font-size="8.5" fill="#e67e22">+{rew_pk_v:.2f}%</text>')

svg1 = f"""<svg viewBox="0 0 {FW} {FH}" xmlns="http://www.w3.org/2000/svg"
     style="font-family:-apple-system,system-ui,sans-serif;background:white;">
  <text x="{FW//2}" y="22" text-anchor="middle" font-size="13" font-weight="700" fill="#222">
    Mesolimbic Dopamine Signals in a Learned Association (Day 12)
  </text>
  <text x="{FW//2}" y="40" text-anchor="middle" font-size="10" fill="#666">
    Fiber photometry · GCaMP6f in NAc · subject HJ-FP-F1 · DANDI 000351 (Jeong et al. 2022)
  </text>
  <text x="{FW//2}" y="57" text-anchor="middle" font-size="10" fill="#444">
    Dopamine rises to both reward and its predictive cue — signatures of a learned causal association
  </text>
  {ax1}{xticks}{yticks}{rew_band}{cue_band}{rew_line}{cue_line}{leg1}{ann1}
</svg>"""

with open(os.path.join(OUT, "dopamine_traces.svg"), "w") as f:
    f.write(svg1)
print("Wrote dopamine_traces.svg")


# ── Figure 2: Inter-reward interval controls learning rate ───────────────────
# Conceptual diagram showing the 2026 Nat Neurosci finding (Namboodiri et al.):
# Short IRI (many rewards per minute) → slow learning
# Long IRI (few rewards per minute) → fast learning
# Trials held constant, only inter-reward duration varies

FW2, FH2 = 700, 420
PAD_L2, PAD_R2, PAD_T2, PAD_B2 = 80, 40, 80, 70
AW2 = FW2 - PAD_L2 - PAD_R2
AH2 = FH2 - PAD_T2 - PAD_B2

# Schematic learning curves for three IRI conditions
# (y=acquisition speed, x=trial number — not real data, illustrative only)
# Short IRI: slow rise; Long IRI: fast rise; Medium IRI: intermediate
N_TRIALS = 40

def learning_curve(rate, n=N_TRIALS):
    """Exponential learning curve, range 0-1."""
    return [1 - math.exp(-rate * i / n) for i in range(n)]

curves = [
    ("Short IRI (5 s)", learning_curve(0.8),  "#c0392b", "slow"),
    ("Medium IRI (30 s)", learning_curve(2.5), "#e67e22", "medium"),
    ("Long IRI (90 s)", learning_curve(5.5),  "#27ae60", "fast"),
]

def px2(trial):
    return PAD_L2 + trial / (N_TRIALS-1) * AW2

def py2(perf):
    return PAD_T2 + AH2 - perf * AH2

# Axes
ax2  = (f'<line x1="{PAD_L2}" y1="{PAD_T2}" x2="{PAD_L2}" y2="{PAD_T2+AH2}" stroke="#ccc" stroke-width="1.2"/>'
        f'<line x1="{PAD_L2}" y1="{PAD_T2+AH2}" x2="{PAD_L2+AW2}" y2="{PAD_T2+AH2}" stroke="#ccc" stroke-width="1.2"/>')

xticks2 = ""
for t in [0, 10, 20, 30, 40]:
    tx = px2(t)
    xticks2 += (f'<line x1="{tx:.1f}" y1="{PAD_T2+AH2}" x2="{tx:.1f}" y2="{PAD_T2+AH2+4}" stroke="#aaa"/>'
                f'<text x="{tx:.1f}" y="{PAD_T2+AH2+16}" text-anchor="middle" font-size="9" fill="#888">{t}</text>')
xticks2 += (f'<text x="{PAD_L2+AW2/2:.0f}" y="{PAD_T2+AH2+34}" text-anchor="middle" font-size="10" fill="#555">'
            f'Training trial number (same across groups)</text>')

yticks2 = ""
for v in [0.0, 0.25, 0.5, 0.75, 1.0]:
    ty = py2(v)
    yticks2 += (f'<line x1="{PAD_L2-4}" y1="{ty:.1f}" x2="{PAD_L2}" y2="{ty:.1f}" stroke="#aaa"/>'
                f'<text x="{PAD_L2-8}" y="{ty+4:.1f}" text-anchor="end" font-size="9" fill="#888">{int(v*100)}%</text>')
yticks2 += (f'<text transform="rotate(-90,18,{PAD_T2+AH2/2:.0f})" x="18" y="{PAD_T2+AH2/2:.0f}" '
            f'text-anchor="middle" font-size="10" fill="#555">Association strength (schematic)</text>')

curves_svg = ""
for label, vals, col, speed in curves:
    pts = " ".join(f"{px2(i):.1f},{py2(v):.1f}" for i, v in enumerate(vals))
    curves_svg += f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.5" stroke-linejoin="round"/>'
    # End label
    x_end = px2(N_TRIALS - 1) + 6
    y_end = py2(vals[-1]) + 4
    curves_svg += (f'<text x="{x_end:.1f}" y="{y_end:.1f}" font-size="9" fill="{col}" font-weight="700">'
                   f'{label}</text>')

# Key insight callout
kx, ky = PAD_L2 + 20, PAD_T2 + 20
callout = (f'<rect x="{kx}" y="{ky}" width="230" height="62" rx="4" '
           f'fill="#f0fff4" stroke="#27ae60" stroke-width="1.2"/>'
           f'<text x="{kx+10}" y="{ky+18}" font-size="9.5" fill="#1a7a3a" font-weight="700">'
           f'Key finding (Namboodiri et al. 2026)</text>'
           f'<text x="{kx+10}" y="{ky+34}" font-size="8.5" fill="#333">'
           f'Longer duration between rewards →</text>'
           f'<text x="{kx+10}" y="{ky+47}" font-size="8.5" fill="#333">'
           f'faster learning, trial count held constant.</text>'
           f'<text x="{kx+10}" y="{ky+58}" font-size="8" fill="#777">'
           f'Nat Neurosci 2026 · DOI: 10.1038/s41593-026</text>')

svg2 = f"""<svg viewBox="0 0 {FW2} {FH2}" xmlns="http://www.w3.org/2000/svg"
     style="font-family:-apple-system,system-ui,sans-serif;background:white;">
  <text x="{FW2//2}" y="22" text-anchor="middle" font-size="13" font-weight="700" fill="#222">
    Duration Between Rewards Controls Learning Rate
  </text>
  <text x="{FW2//2}" y="40" text-anchor="middle" font-size="10" fill="#666">
    Schematic of the core result · Namboodiri lab, Nat Neurosci 2026
  </text>
  <text x="{FW2//2}" y="57" text-anchor="middle" font-size="10" fill="#444">
    Same number of trials, same reward — only inter-reward interval differs
  </text>
  {ax2}{xticks2}{yticks2}{curves_svg}{callout}
</svg>"""

with open(os.path.join(OUT, "iri_learning.svg"), "w") as f:
    f.write(svg2)
print("Wrote iri_learning.svg")
