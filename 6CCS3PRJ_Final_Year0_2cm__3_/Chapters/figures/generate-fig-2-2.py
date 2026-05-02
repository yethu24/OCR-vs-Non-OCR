"""Generate fig-2-2-utility-bill-layouts.png.

Three stylised mock bill thumbnails showing the same five schema fields
in different positions, under different labels, and in different languages.
Schematic only; no real PII. Schema-field text is colour-highlighted and
a small legend maps visible text back to schema field names.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = Path(__file__).parent / "fig-2-2-utility-bill-layouts.png"

bill_w, bill_h = 3.4, 5.0

FIELD_COLOURS = {
    "provider_name":    "#9e1b32",
    "bill_date":        "#1f4e79",
    "billing_period":   "#7a5195",
    "account_number":   "#b06a00",
    "total_amount_due": "#2e7d32",
}


LAYOUTS = [
    {
        "title": "Issuer A (English)",
        "rows": [
            ("BRIGHTGRID UTILITIES", 0.15, bill_h - 0.30, 11, "bold",
             "provider_name"),
            ("Monthly Statement",    0.15, bill_h - 0.55, 8, "italic", None),
            ("Account no.: 4421-7782", 0.15, bill_h - 1.10, 9, "mono",
             "account_number"),
            ("Issued: 12 Mar 2024",    0.15, bill_h - 1.50, 9, "mono",
             "bill_date"),
            ("Period: 01-28 Feb 2024", 0.15, bill_h - 1.90, 9, "mono",
             "billing_period"),
            ("Amount due:  GBP 142.50", 0.15, 0.70, 10, "mono",
             "total_amount_due"),
        ],
        "footer_box": True,
    },
    {
        "title": "Issuer B (German)",
        "rows": [
            ("STADTWERKE NORDSTERN",   0.15, bill_h - 0.30, 11, "bold",
             "provider_name"),
            ("Stromrechnung",          0.15, bill_h - 0.55, 8, "italic", None),
            ("Rechnungsdatum: 04.04.2024", 0.15, bill_h - 1.15, 9, "mono",
             "bill_date"),
            ("Abrechnungszeitraum: Mar 2024", 0.15, bill_h - 1.55, 9, "mono",
             "billing_period"),
            ("Kundennummer: 998-3341", 0.15, bill_h - 1.95, 9, "mono",
             "account_number"),
            ("Gesamtbetrag:  EUR 97,30", 0.15, 0.70, 10, "mono",
             "total_amount_due"),
        ],
        "footer_box": True,
    },
    {
        "title": "Issuer C (Italian)",
        "rows": [
            ("AQUA ROMA SpA",         0.15, bill_h - 0.30, 11, "bold",
             "provider_name"),
            ("Bolletta dell'acqua",   0.15, bill_h - 0.55, 8, "italic", None),
            ("Totale:  EUR 56,20",    0.15, bill_h - 1.00, 11, "mono",
             "total_amount_due"),
            ("Utenza: 7731/A",        0.15, bill_h - 1.50, 9, "mono",
             "account_number"),
            ("Periodo: Feb 2024",     0.15, bill_h - 1.90, 9, "mono",
             "billing_period"),
            ("Emesso: 15-03-2024",    0.15, bill_h - 2.30, 9, "mono",
             "bill_date"),
        ],
        "footer_box": False,
    },
]


def draw_bill(ax, layout):
    ax.add_patch(Rectangle((0, 0), bill_w, bill_h,
                           facecolor="white", edgecolor="black",
                           linewidth=1.5))
    ax.add_patch(Rectangle((0, bill_h - 0.60), bill_w, 0.60,
                           facecolor="#ececec", edgecolor="black",
                           linewidth=0.8))

    for y in [bill_h - 2.35, bill_h - 2.75, bill_h - 3.15, bill_h - 3.55]:
        ax.plot([0.15, bill_w - 0.15], [y, y],
                color="#cccccc", linewidth=0.6)

    if layout["footer_box"]:
        ax.add_patch(Rectangle((0.08, 0.35), bill_w - 0.16, 0.70,
                               facecolor="none", edgecolor="black",
                               linewidth=1.2))

    for text, fx, fy, fs, style, field in layout["rows"]:
        kwargs = dict(fontsize=fs, va="center")
        if style == "bold":
            kwargs["fontweight"] = "bold"
        elif style == "italic":
            kwargs["style"] = "italic"
        elif style == "mono":
            kwargs["fontfamily"] = "monospace"
        if field is not None:
            kwargs["color"] = FIELD_COLOURS[field]
            kwargs["fontweight"] = "bold"
        ax.text(fx, fy, text, **kwargs)

    ax.set_title(layout["title"], fontsize=12, pad=8)
    ax.set_xlim(-0.2, bill_w + 0.2)
    ax.set_ylim(-0.1, bill_h + 0.3)
    ax.set_aspect("equal")
    ax.axis("off")


fig = plt.figure(figsize=(13.5, 7.2))
gs = fig.add_gridspec(2, 3, height_ratios=[7.0, 1.0], hspace=0.25)

for i, layout in enumerate(LAYOUTS):
    ax = fig.add_subplot(gs[0, i])
    draw_bill(ax, layout)

legend_ax = fig.add_subplot(gs[1, :])
legend_ax.axis("off")
legend_ax.set_xlim(0, 10)
legend_ax.set_ylim(0, 1)
names = list(FIELD_COLOURS.keys())
spacing = 10 / len(names)
for i, name in enumerate(names):
    cx = i * spacing + spacing / 2
    legend_ax.add_patch(Rectangle((cx - 0.18, 0.50), 0.36, 0.22,
                                  facecolor=FIELD_COLOURS[name],
                                  edgecolor="none"))
    legend_ax.text(cx, 0.35, name, ha="center", va="top",
                   fontsize=10, fontfamily="monospace",
                   color=FIELD_COLOURS[name], fontweight="bold")

legend_ax.text(5.0, 0.90, "schema field colour key",
               ha="center", va="top", fontsize=10, style="italic")

fig.tight_layout()
fig.savefig(OUT, dpi=200, bbox_inches="tight")
print(f"Wrote {OUT}")
