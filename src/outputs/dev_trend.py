"""
outputs/dev_trend.py
Simplest output: plots average brightness over time for the whole region.
Answers: "is this area actually developing?"

Uses Plotly instead of matplotlib -- Plotly is pure Python and writes an
HTML file that your browser renders, so it has no compiled DLL for
Windows security policies to block.
"""

import os
import numpy as np
import plotly.graph_objects as go

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def run():
    brightness_2019 = np.load(os.path.join(DATA_DIR, "brightness_2019.npy"))
    brightness_2024 = np.load(os.path.join(DATA_DIR, "brightness_2024.npy"))

    # with only 2 years of real data we just connect two points --
    # once you export more years, add them to this list
    years = [2019, 2024]
    avg_brightness = [brightness_2019.mean(), brightness_2024.mean()]

    pct_change = (avg_brightness[-1] - avg_brightness[0]) / avg_brightness[0] * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=avg_brightness,
        mode="lines+markers",
        line=dict(width=3),
        marker=dict(size=10),
        fill="tozeroy",
    ))
    fig.update_layout(
        title=f"Development trend ({pct_change:+.1f}% change)",
        yaxis_title="Average night-light brightness",
        xaxis=dict(tickmode="array", tickvals=years),
        template="plotly_white",
    )

    out_path = os.path.join(DATA_DIR, "dev_trend.html")
    fig.write_html(out_path)
    print(f"Saved chart to {out_path}")
    print(f"Change: {pct_change:+.1f}% over the period")
    print("Open this .html file in any browser to view the chart.")


if __name__ == "__main__":
    run()