"""
Dashboard Graphic Asset Generator
Produces an executive-grade dashboard preview banner for README and documentation.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Set dark background styling
plt.style.use("dark_background")
fig = plt.figure(figsize=(14, 8), dpi=150)
fig.patch.set_facecolor("#0F172A")

# Title Bar
plt.suptitle(
    "Sales Intelligence & Executive Analytics Platform | Google-Grade Data Analyst Suite",
    fontsize=16,
    fontweight="bold",
    color="#F8FAFC",
    y=0.96,
)

# 1. Monthly Revenue & Profit Trend
ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=2, rowspan=2)
ax1.set_facecolor("#1E293B")
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
sales = [142, 130, 155, 140, 168, 175, 160, 190, 210, 195, 275, 290]
profit = [18, 14, 22, 19, 25, 28, 22, 31, 35, 29, 48, 52]

ax1.plot(months, sales, marker="o", color="#3B82F6", linewidth=2.5, label="Gross Revenue ($k)")
ax1.fill_between(months, sales, color="#3B82F6", alpha=0.15)
ax1.plot(months, profit, marker="s", color="#10B981", linewidth=2.5, label="Net Profit ($k)")
ax1.set_title("Revenue vs. Profit Seasonality (Q4 Surge)", color="#F8FAFC", fontsize=11, fontweight="bold")
ax1.grid(color="#334155", linestyle="--", alpha=0.6)
ax1.legend(loc="upper left", facecolor="#0F172A", edgecolor="#334155")

# 2. RFM Customer Segments (Donut Chart)
ax2 = plt.subplot2grid((3, 3), (0, 2), rowspan=2)
ax2.set_facecolor("#1E293B")
sizes = [53.6, 23.5, 21.3, 1.6]
labels = ["Champions ($1.23M)", "Loyal ($540K)", "At-Risk ($490K)", "Hibernating ($36K)"]
colors = ["#10B981", "#3B82F6", "#F59E0B", "#EF4444"]
wedges, _, autotexts = ax2.pie(
    sizes,
    labels=labels,
    colors=colors,
    autopct="%1.1f%%",
    pctdistance=0.75,
    startangle=140,
    textprops=dict(color="#F8FAFC", fontsize=8),
)
centre_circle = plt.Circle((0, 0), 0.55, fc="#1E293B")
ax2.add_artist(centre_circle)
ax2.set_title("RFM Customer Value Distribution", color="#F8FAFC", fontsize=11, fontweight="bold")

# 3. Discount Elasticity vs Margin
ax3 = plt.subplot2grid((3, 3), (2, 0))
ax3.set_facecolor("#1E293B")
tiers = ["0% (Full)", "1-20%", "21-40%", ">40%"]
margins = [28.4, 18.2, 3.5, -42.8]
bar_colors = ["#10B981", "#3B82F6", "#F59E0B", "#EF4444"]
ax3.bar(tiers, margins, color=bar_colors, width=0.6)
ax3.axhline(0, color="#EF4444", linestyle="--", linewidth=1)
ax3.set_title("Margin Erosion by Discount Tier (%)", color="#F8FAFC", fontsize=10, fontweight="bold")
ax3.tick_params(axis="x", labelsize=8)
ax3.grid(color="#334155", linestyle="--", alpha=0.5)

# 4. Holt-Winters 6-Month Forward Forecast
ax4 = plt.subplot2grid((3, 3), (2, 1), colspan=2)
ax4.set_facecolor("#1E293B")
hist_time = np.arange(1, 13)
hist_val = [45, 52, 49, 61, 58, 67, 72, 70, 85, 82, 105, 112]
future_time = np.arange(12, 19)
future_val = [112, 118, 115, 128, 132, 140, 148]
ci_lower = [112, 105, 98, 108, 110, 116, 122]
ci_upper = [112, 131, 132, 148, 154, 164, 174]

ax4.plot(hist_time, hist_val, color="#3B82F6", linewidth=2, label="Historical GMV")
ax4.plot(future_time, future_val, color="#10B981", linewidth=2.5, linestyle="-", label="6-Mo Forecast")
ax4.fill_between(future_time, ci_lower, ci_upper, color="#10B981", alpha=0.2, label="95% Confidence Interval")
ax4.set_title("Predictive Revenue Forecasting (Accuracy: 82.9%, MAPE: 17.1%)", color="#F8FAFC", fontsize=10, fontweight="bold")
ax4.grid(color="#334155", linestyle="--", alpha=0.5)
ax4.legend(loc="upper left", facecolor="#0F172A", edgecolor="#334155", fontsize=8)

plt.tight_layout(rect=[0, 0.03, 1, 0.94])

output_file = Path(__file__).resolve().parent / "dashboard_preview.png"
plt.savefig(output_file, dpi=150, facecolor=fig.get_facecolor(), edgecolor="none")
plt.close()
print(f"Generated dashboard preview graphic at {output_file}")
