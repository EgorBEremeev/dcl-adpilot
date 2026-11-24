"""Render a square 720x720 SVG bubble/range chart from a snapshot JSON dataset."""
from __future__ import annotations

import html
import json
import math
import sys
from pathlib import Path


def bubble_radius(count: int | float) -> float:
    """Map listing count to a readable SVG circle radius (5..16 px)."""
    c = max(1.0, float(count))
    return round(min(16.0, 4.0 + 2.0 * math.sqrt(c)), 1)


def render_svg(data: dict) -> str:
    """Build square 720x720 SVG markup from parsed snapshot JSON."""
    meta = data["meta"]
    clusters = data["clusters"]

    x0, x1 = 115.0, 650.0
    x_max = float(meta.get("x_max_eur", 130))
    scale = (x1 - x0) / x_max

    def x_px(eur: float) -> float:
        return round(x0 + min(eur, x_max) * scale, 1)

    # Two contiguous bands separated by a crisp horizontal axis line at y=385
    y_top, y_mid, y_bot = 105.0, 385.0, 665.0
    band_lanes = {
        "bg": [155.0, 212.0, 275.0, 338.0],
        "varna": [435.0, 488.0, 545.0, 610.0],
    }

    styles = {
        "used": ("#bae6fd", "#0284c7", "#0369a1"),
        "new": ("#fecaca", "#dc2626", "#b91c1c"),
        "target": ("#bbf7d0", "#16a34a", "#15803d"),
    }

    parts: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 720" width="720" height="720" font-family="Segoe UI, Arial, sans-serif">',
        '  <rect width="720" height="720" fill="#ffffff" rx="10"/>',
        f'  <text x="360" y="34" text-anchor="middle" font-size="16" font-weight="700" fill="#0f172a">Товарные кластеры и ориентиры цены ({html.escape(meta.get("platform", "OLX.bg"))})</text>',
        f'  <text x="360" y="54" text-anchor="middle" font-size="12" fill="#64748b">Категория: {html.escape(meta.get("category_id", ""))} · Валюта: {html.escape(meta.get("currency", "EUR"))} за 1 шт. · Размер круга ~ число объявлений</text>',
        '  <g transform="translate(65, 74)" font-size="11.5" fill="#334155">',
        '    <circle cx="8" cy="6" r="6" fill="#0284c7" fill-opacity="0.85"/>',
        '    <text x="20" y="10">Б/У и реставрация [B*]</text>',
        '    <circle cx="185" cy="6" r="6" fill="#dc2626" fill-opacity="0.85"/>',
        '    <text x="197" y="10">Новые [N*]</text>',
        '    <polygon points="285,0 292,6 285,12 278,6" fill="#16a34a"/>',
        '    <text x="298" y="10">Ориентиры [P*]</text>',
        '    <line x1="408" y1="6" x2="432" y2="6" stroke="#dc2626" stroke-width="1.8" stroke-dasharray="4,3"/>',
        f'    <text x="438" y="10">{html.escape(meta.get("threshold_label", "Порог нового"))}</text>',
        '  </g>',
        f'  <rect x="{x0}" y="{y_top}" width="{x1 - x0}" height="{y_bot - y_top}" fill="#f8fafc" stroke="#cbd5e1" rx="6"/>',
        f'  <line x1="{x0}" y1="{y_mid}" x2="{x1}" y2="{y_mid}" stroke="#94a3b8" stroke-width="1.5"/>',
        '  <text x="60" y="237" text-anchor="middle" font-size="13" font-weight="700" fill="#1e293b">Вся</text>',
        '  <text x="60" y="254" text-anchor="middle" font-size="13" font-weight="700" fill="#1e293b">Болгария</text>',
        '  <text x="60" y="271" text-anchor="middle" font-size="11" fill="#64748b">(доставка)</text>',
        '  <text x="60" y="520" text-anchor="middle" font-size="13" font-weight="700" fill="#1e293b">г. Варна</text>',
        '  <text x="60" y="537" text-anchor="middle" font-size="11" fill="#64748b">(самовывоз)</text>',
        '  <g stroke="#e2e8f0" stroke-width="1">',
    ]

    step = 20 if x_max >= 80 else (10 if x_max >= 40 else 5)
    ticks = list(range(0, int(x_max) + 1, step))
    for t in ticks:
        tx = x_px(t)
        parts.append(f'    <line x1="{tx}" y1="{y_top}" x2="{tx}" y2="{y_bot}"/>')
    parts.append('  </g>')

    thr = meta.get("threshold_eur")
    if thr is not None:
        tx = x_px(float(thr))
        parts.append(f'  <line x1="{tx}" y1="98" x2="{tx}" y2="672" stroke="#dc2626" stroke-width="1.8" stroke-dasharray="5,4"/>')

    parts.append('  <g font-size="11.5" fill="#475569" text-anchor="middle">')
    for t in ticks:
        parts.append(f'    <text x="{x_px(t)}" y="690">{t} €</text>')
    overflow = meta.get("x_overflow_label")
    if overflow:
        parts.append(f'    <text x="668" y="690" text-anchor="start" font-size="10.5" fill="#64748b">{html.escape(overflow)}</text>')
    parts.append('  </g>')

    for c in clusters:
        geo = c["geo"]
        grp = c["group"]
        lane = int(c.get("lane", 0))
        cy = band_lanes[geo][lane]
        cx_min = x_px(float(c["min"]))
        cx_max = x_px(float(c["max"]))
        cx_peak = x_px(float(c["peak"]))
        range_col, fill_col, text_col = styles[grp]

        if cx_max > cx_min:
            w = 7 if grp == "target" else 6
            parts.append(
                f'  <line x1="{cx_min}" y1="{cy}" x2="{cx_max}" y2="{cy}" stroke="{range_col}" stroke-width="{w}" stroke-linecap="round"/>'
            )

        if grp == "target":
            d = 9
            pts = f"{cx_peak},{cy - d} {cx_peak + d},{cy} {cx_peak},{cy + d} {cx_peak - d},{cy}"
            parts.append(f'  <polygon points="{pts}" fill="{fill_col}" stroke="{text_col}" stroke-width="1.5"/>')
            ly = cy + 26
        else:
            r = bubble_radius(c.get("count", 1))
            parts.append(
                f'  <circle cx="{cx_peak}" cy="{cy}" r="{r}" fill="{fill_col}" fill-opacity="0.85" stroke="{text_col}" stroke-width="1.5"/>'
            )
            ly = cy - r - 8 if lane < 2 else cy + r + 15

        lx = cx_peak + float(c.get("label_dx", 0))
        anchor = c.get("label_anchor", "middle")
        fw = "700" if grp == "target" or c["code"] == "N2" else "600"
        parts.append(
            f'  <text x="{lx}" y="{ly}" text-anchor="{anchor}" font-size="11" font-weight="{fw}" fill="{text_col}">{html.escape(c["label"])}</text>'
        )

    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: render_snapshot_svg.py <snapshot.json> [output.svg]", file=sys.stderr)
        return 1
    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else in_path.with_suffix(".svg")
    data = json.loads(in_path.read_text(encoding="utf-8"))
    out_path.write_text(render_svg(data), encoding="utf-8")
    print(f"Rendered {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
