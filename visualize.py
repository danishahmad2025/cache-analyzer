import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def plot_results(db_times, cache_times):
    queries = list(range(1, len(db_times) + 1))

    avg_db    = sum(db_times) / len(db_times)
    avg_cache = sum(cache_times) / len(cache_times)
    speedup   = avg_db / avg_cache if avg_cache > 0 else 0
    max_db    = max(db_times)
    max_cache = max(cache_times)

    # --- Layout: 2 rows, 3 columns ---
    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor("#F8F9FA")
    fig.suptitle("Medicare Claims — Cache vs Database Performance", 
                 fontsize=16, fontweight="bold", y=0.98, color="#2C2C2A")

    # --- Top row: main line chart (spans all 3 columns) ---
    ax_main = fig.add_subplot(2, 1, 1)
    ax_main.set_facecolor("#FFFFFF")

    # Shaded zones — help reader see hit vs miss visually
    # First query per state group = cache miss (every 5th starting at 1)
    miss_indices = [i for i in queries if (i - 1) % 5 == 0]
    hit_indices  = [i for i in queries if (i - 1) % 5 != 0]

    for mi in miss_indices:
        ax_main.axvspan(mi - 0.5, mi + 0.4, alpha=0.08, color="#D85A30", zorder=0)
    for hi in hit_indices:
        ax_main.axvspan(hi - 0.5, hi + 0.4, alpha=0.04, color="#1D9E75", zorder=0)

    # Main lines
    ax_main.plot(queries, db_times,
                 label="Database (no cache)", color="#378ADD",
                 alpha=0.85, linewidth=1.5, zorder=3)
    ax_main.plot(queries, cache_times,
                 label="Cache (Redis)", color="#1D9E75",
                 alpha=0.95, linewidth=1.5, zorder=4)

    # Scatter dots — miss points highlighted in orange
    for mi in miss_indices:
        idx = mi - 1
        ax_main.scatter(mi, cache_times[idx], color="#D85A30",
                        zorder=5, s=40, label="_nolegend_")
    for hi in hit_indices:
        idx = hi - 1
        ax_main.scatter(hi, cache_times[idx], color="#1D9E75",
                        zorder=5, s=20, label="_nolegend_")

    # Average lines
    ax_main.axhline(avg_db,    color="#378ADD", linestyle="--",
                    linewidth=1.2, alpha=0.7,
                    label=f"DB avg: {avg_db:.2f} ms")
    ax_main.axhline(avg_cache, color="#1D9E75", linestyle="--",
                    linewidth=1.2, alpha=0.7,
                    label=f"Cache avg: {avg_cache:.2f} ms")

    # Annotate speedup on chart
    ax_main.annotate(f"{speedup:.1f}x faster",
                     xy=(len(queries) * 0.75, avg_db),
                     xytext=(len(queries) * 0.75, avg_db + max_db * 0.05),
                     fontsize=10, fontweight="bold", color="#D85A30",
                     arrowprops=dict(arrowstyle="->", color="#D85A30"))

    # Custom legend with zone explanation
    miss_patch = mpatches.Patch(color="#D85A30", alpha=0.3, label="Cache miss (1st query per state)")
    hit_patch  = mpatches.Patch(color="#1D9E75", alpha=0.3, label="Cache hit (repeat queries)")
    handles, labels = ax_main.get_legend_handles_labels()
    ax_main.legend(handles=handles + [miss_patch, hit_patch],
                   loc="upper right", fontsize=9,
                   framealpha=0.9, edgecolor="#CCCCCC")

    ax_main.set_xlabel("Query number", fontsize=11, color="#444441")
    ax_main.set_ylabel("Response time (ms)", fontsize=11, color="#444441")
    ax_main.set_title("Response time per query — shaded orange = cache miss, green = cache hit",
                      fontsize=10, color="#888780", pad=8)
    ax_main.grid(axis="y", linestyle="--", alpha=0.4, color="#CCCCCC")
    ax_main.spines[["top", "right"]].set_visible(False)

    # --- Bottom row: 3 stat panels ---

    # Panel 1 — Bar chart: avg comparison
    ax_bar = fig.add_subplot(2, 3, 4)
    ax_bar.set_facecolor("#FFFFFF")
    bars = ax_bar.bar(["Database", "Cache"],
                      [avg_db, avg_cache],
                      color=["#378ADD", "#1D9E75"],
                      width=0.4, edgecolor="white", linewidth=0.5)
    for bar, val in zip(bars, [avg_db, avg_cache]):
        ax_bar.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.01,
                    f"{val:.2f} ms",
                    ha="center", va="bottom",
                    fontsize=10, fontweight="bold", color="#2C2C2A")
    ax_bar.set_title("Average response time", fontsize=10, color="#444441")
    ax_bar.set_ylabel("ms", fontsize=9)
    ax_bar.spines[["top", "right"]].set_visible(False)
    ax_bar.grid(axis="y", linestyle="--", alpha=0.3)
    ax_bar.set_facecolor("#FFFFFF")

    # Panel 2 — Speedup gauge (horizontal bar)
    ax_gauge = fig.add_subplot(2, 3, 5)
    ax_gauge.set_facecolor("#FFFFFF")
    max_speedup = max(speedup * 1.3, 10)
    ax_gauge.barh(["Speedup"], [max_speedup], color="#F0F0F0",
                  edgecolor="#CCCCCC", height=0.4)
    ax_gauge.barh(["Speedup"], [speedup], color="#D85A30",
                  edgecolor="white", height=0.4)
    ax_gauge.text(speedup + 0.2, 0,
                  f"{speedup:.1f}x",
                  va="center", fontsize=14,
                  fontweight="bold", color="#D85A30")
    ax_gauge.set_xlim(0, max_speedup)
    ax_gauge.set_title("Cache speedup factor", fontsize=10, color="#444441")
    ax_gauge.set_xlabel("Times faster than DB", fontsize=9)
    ax_gauge.spines[["top", "right", "left"]].set_visible(False)
    ax_gauge.set_yticks([])

    # Panel 3 — Hit vs Miss summary (pie chart)
    ax_pie = fig.add_subplot(2, 3, 6)
    ax_pie.set_facecolor("#FFFFFF")
    total        = len(cache_times)
    miss_count   = len(miss_indices)
    hit_count    = total - miss_count
    hit_rate     = (hit_count / total) * 100

    ax_pie.pie(
        [hit_count, miss_count],
        labels=[f"Cache hits\n{hit_count} queries", f"Cache misses\n{miss_count} queries"],
        colors=["#1D9E75", "#D85A30"],
        autopct="%1.0f%%",
        startangle=90,
        wedgeprops=dict(edgecolor="white", linewidth=2),
        textprops=dict(fontsize=9)
    )
    ax_pie.set_title(f"Hit rate: {hit_rate:.0f}%", fontsize=10,
                     color="#444441", fontweight="bold")

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig("results.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.show()
    print(f"\nChart saved as results.png")
    print(f"Cache hit rate : {hit_rate:.0f}%")
    print(f"Avg DB time    : {avg_db:.2f} ms")
    print(f"Avg cache time : {avg_cache:.2f} ms")
    print(f"Speedup        : {speedup:.1f}x faster")