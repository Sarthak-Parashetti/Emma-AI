import json
import matplotlib.pyplot as plt

with open("benchmark_results.json", encoding="utf-8") as f:
    data = json.load(f)
s = data["summary"]
rows = data["rows"]

# Graph 1: accuracy by category
cats = [("Canonical", "canonical"), ("Paraphrased", "paraphrase"),
        ("Compound", "compound"), ("'and' in argument", "compound_arg"),
        ("Out-of-scope", "out_of_scope")]
labels = [c[0] for c in cats]
pct = [100 * s["per_category"][k][0] / s["per_category"][k][1] for _, k in cats]
fig, ax = plt.subplots(figsize=(6.2, 3.0), dpi=300)
bars = ax.bar(labels, pct, color="#2F4B9A", width=0.55)
for b, (_, k) in zip(bars, cats):
    ok, n = s["per_category"][k]
    ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 2,
            f"{ok}/{n}\n({100*ok/n:.0f}%)", ha="center", fontsize=8)
ax.set_ylim(0, 120)
ax.set_ylabel("Exact-match accuracy (%)")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("acc_category.png")
plt.close()

# Graph 2: accuracy by domain
dom = s["per_domain"]
names = list(dom.keys())
vals = [100 * dom[k][0] / dom[k][1] for k in names]
fig, ax = plt.subplots(figsize=(6.2, 3.2), dpi=300)
bars = ax.barh([k.replace("_action", "") for k in names][::-1], vals[::-1],
               color="#2F4B9A", height=0.6)
for b, k in zip(bars, names[::-1]):
    ok, n = dom[k]
    ax.text(b.get_width() + 1.5, b.get_y() + b.get_height() / 2,
            f"{ok}/{n}", va="center", fontsize=8)
ax.set_xlim(0, 115)
ax.set_xlabel("Exact-match accuracy (%)")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("acc_domain.png")
plt.close()

# Graph 3: latency histogram
lat = [r["us"] for r in rows]
fig, ax = plt.subplots(figsize=(6.2, 2.8), dpi=300)
ax.hist(lat, bins=18, color="#2F4B9A", edgecolor="white")
ax.axvline(s["latency_us"]["median"], color="#C0392B", ls="--", lw=1.2)
ax.text(s["latency_us"]["median"] + 2, ax.get_ylim()[1] * 0.88,
        f"median {s['latency_us']['median']} µs", color="#C0392B", fontsize=8)
ax.set_xlabel("Planner + normaliser + NLU time per utterance (µs)")
ax.set_ylabel("Number of utterances")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("latency_hist.png")
plt.close()

print("Saved acc_category.png, acc_domain.png, latency_hist.png")