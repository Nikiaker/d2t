"""Domain-specific human-readable renderers for the original input data."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from matplotlib.figure import Figure

from matplotlib.backends.backend_qtagg import FigureCanvas


def _fmt(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, float, str)):
        return str(value).strip()
    return json.dumps(value, ensure_ascii=False)


def _section(title: str) -> QLabel:
    label = QLabel(f"<b>{title}</b>")
    label.setStyleSheet("font-size: 14px; margin-top: 10px;")
    return label


def _kv_table(rows: list[tuple[str, str]], headers=("Key", "Value")) -> QTableWidget:
    return _grid_table([list(r) for r in rows], list(headers))


def _grid_table(rows: list[list[str]], headers: list[str]) -> QTableWidget:
    table = QTableWidget(len(rows), len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setSelectionMode(QTableWidget.ContiguousSelection)
    table.setFocusPolicy(Qt.NoFocus)
    table.setWordWrap(True)
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            table.setItem(r, c, QTableWidgetItem(val))
    table.resizeColumnsToContents()
    header = table.horizontalHeader()
    for c in range(len(headers) - 1):
        header.setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
    header.setSectionResizeMode(len(headers) - 1, QHeaderView.ResizeMode.Stretch)
    height = 34 + min(len(rows), 24) * 26 + 4
    table.setFixedHeight(height)
    return table


def _chart_canvas(draw, width=8.0, height=3.4) -> FigureCanvas:
    fig = Figure(figsize=(width, height), dpi=100, tight_layout=True)
    canvas = FigureCanvas(fig)
    canvas.setMinimumHeight(int(height * 100))
    canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    draw(fig)
    return canvas


class SourceWidget(QWidget):
    """Wrapper: builds a per-domain human-readable view of one input_data dict."""

    def __init__(self, domain: str, data, parent: QWidget | None = None):
        super().__init__(parent)
        self.renderer_error: Exception | None = None
        self.layout_ = QVBoxLayout(self)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        builder = _BUILDERS.get(domain)
        built = False
        if builder is not None:
            try:
                builder(self.layout_, data)
                built = True
            except Exception as exc:  # fall back to raw JSON on any renderer bug
                self.renderer_error = exc
        if not built:
            self.renderer_error = self.renderer_error or ValueError(f"no renderer for domain {domain!r}")
            self.layout_.addWidget(
                QLabel(f"<i>Renderer failed ({self.renderer_error!r}); showing raw JSON.</i>")
            )
            text = json.dumps(data, indent=2, ensure_ascii=False)
            pre = QLabel(f"<pre>{text.replace('&', '&amp;').replace('<', '&lt;')}</pre>")
            pre.setTextInteractionFlags(Qt.TextSelectableByMouse)
            pre.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.layout_.addWidget(pre)


# ----------------------------------------------------------------------------- wikidata

def _render_wikidata(layout, data: dict):
    entity = _fmt(data.get("entity", "(unknown entity)"))
    props = data.get("properties") or []
    rows = [(_fmt(p[0]), _fmt(p[1])) for p in props if isinstance(p, (list, tuple)) and len(p) >= 2]
    table = _kv_table(rows, headers=(entity, "value"))
    layout.addWidget(_section(f"Wikidata entity: {entity}  ({len(rows)} properties)"))
    layout.addWidget(table)


# ------------------------------------------------------------------ mobile_phone (gsmarena)

def _render_gsmarena(layout, data: dict):
    details = data.get("details") or {}
    name = _fmt(details.get("name") or data.get("name"))
    layout.addWidget(_section(f"Device: {name}"))
    quick = details.get("quickSpec") or []
    if quick:
        layout.addWidget(QLabel("<b>Quick specifications</b>"))
        layout.addWidget(_kv_table([(_fmt(s.get("name")), _fmt(s.get("value"))) for s in quick]))
    for group in details.get("detailSpec") or []:
        category = _fmt(group.get("category"))
        specs = group.get("specifications") or []
        layout.addWidget(QLabel(f"<b>{category}</b>"))
        layout.addWidget(_kv_table([(_fmt(s.get("name")), _fmt(s.get("value"))) for s in specs]))


# --------------------------------------------------------------------- weather_forecast

def _render_openweather(layout, data: dict):
    city = data.get("city") or {}
    meta = [
        ("City", _fmt(city.get("name"))),
        ("Country", _fmt(city.get("country"))),
        ("Coordinates", f"{city.get('coord', {}).get('lat')}, {city.get('coord', {}).get('lon')}" if city.get("coord") else ""),
        ("Population", _fmt(city.get("population"))),
    ]
    for key in ("sunrise", "sunset"):
        ts = city.get(key)
        if ts:
            meta.append((key.capitalize(), datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")))
    layout.addWidget(_section("Forecast " + _fmt(f"for {city.get('name', '')}".strip())))
    layout.addWidget(_kv_table(meta))

    entries = data.get("list") or []

    def draw(fig: Figure):
        ax = fig.add_subplot(111)
        times = []
        for e in entries:
            txt = e.get("dt_txt")
            try:
                times.append(datetime.strptime(txt, "%Y-%m-%d %H:%M:%S"))
            except (TypeError, ValueError):
                times.append(len(times))
        temp = [e.get("main", {}).get("temp") for e in entries]
        feels = [e.get("main", {}).get("feels_like") for e in entries]
        pop = [e.get("pop", 0) for e in entries]
        ax.plot(times, temp, marker="o", ms=3, color="#d62728", label="Temperature (°C)")
        ax.plot(times, feels, ls="--", color="#ff9896", label="Feels like (°C)")
        ax.set_ylabel("°C")
        ax2 = ax.twinx()
        ax2.bar(times, [p * 100 for p in pop], width=0.05, color="#1f77b4", alpha=0.35, label="Precip. chance (%)")
        ax2.set_ylabel("Precip. chance (%)")
        ax2.set_ylim(0, 100)
        fig.autofmt_xdate()
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)
        ax.set_title("Temperature and precipitation probability (3-hour steps)")

    layout.addWidget(_chart_canvas(draw, height=3.8))

    rows = []
    for e in entries:
        main = e.get("main", {})
        weather = (e.get("weather") or [{}])[0]
        rows.append([
            _fmt(e.get("dt_txt")),
            _fmt(main.get("temp")),
            _fmt(weather.get("description") or weather.get("main")),
            _fmt(e.get("wind", {}).get("speed")),
        ])
    layout.addWidget(QLabel("<b>Hourly entries</b>"))
    layout.addWidget(_grid_table(rows, ["Time", "Temp (°C)", "Weather", "Wind (m/s)"]))


# ------------------------------------------------------------------------------ owid

def _render_owid(layout, data: dict):
    meta = [
        ("Country", _fmt(data.get("country"))),
        ("Metric", _fmt(data.get("metric"))),
        ("Title", _fmt(data.get("title"))),
        ("Unit", _fmt(data.get("unit"))),
        ("Description", _fmt(data.get("description"))),
    ]
    layout.addWidget(_section("Metadata"))
    layout.addWidget(_kv_table(meta))

    points = data.get("data") or []
    xs = [p.get("date") for p in points]
    ys = [p.get("value") for p in points]

    def draw(fig: Figure):
        ax = fig.add_subplot(111)
        numeric = all(isinstance(x, (int, float)) for x in xs) and xs
        try:
            xs_cast = [int(x) for x in xs]
            numeric = True
        except (TypeError, ValueError):
            xs_cast = xs
        ax.plot(xs_cast, ys, marker=".", ms=4, color="#1f77b4")
        ax.set_title(f"{_fmt(data.get('title'))} — {_fmt(data.get('country'))}")
        ax.set_xlabel("Date")
        ax.set_ylabel(_fmt(data.get("unit")) or "Value")
        ax.grid(alpha=0.3)

    layout.addWidget(_section("Data"))
    layout.addWidget(_chart_canvas(draw))

    rows = [[_fmt(p.get("date")), _fmt(p.get("value"))] for p in points[:400]]
    table = _grid_table(rows, ["Date", f"Value ({_fmt(data.get('unit')) or 'n/a'})"])
    table.setFixedHeight(34 + min(len(rows), 14) * 26 + 4)
    note = "" if len(points) <= 400 else f" (first 400 of {len(points)} rows)"
    layout.addWidget(QLabel(f"<b>Data points{note}</b>"))
    layout.addWidget(table)


# -------------------------------------------------------------------------- ice_hockey

def _render_icehockey(layout, data: dict):
    tournament = data.get("tournament") or {}
    category = tournament.get("category") or {}
    home, away = data.get("homeTeam") or {}, data.get("awayTeam") or {}
    status = data.get("status") or {}
    home_score = data.get("homeScore") or {}
    away_score = data.get("awayScore") or {}
    winner_code = data.get("winnerCode")
    winner = {1: home.get("name"), 2: away.get("name")}.get(winner_code, "Draw / none")

    start = data.get("startTimestamp")
    start_str = datetime.fromtimestamp(start, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC") if start else ""

    meta = [
        ("Sport", _fmt((category.get("sport") or {}).get("name"))),
        ("Category", _fmt(category.get("name"))),
        ("Tournament", _fmt(tournament.get("name"))),
        ("Season", _fmt((data.get("season") or {}).get("name"))),
        ("Round", _fmt((data.get("roundInfo") or {}).get("round"))),
        ("Status", _fmt(status.get("description"))),
        ("Start time", start_str),
        ("Home team", _fmt(home.get("name"))),
        ("Away team", _fmt(away.get("name"))),
        ("Final score", f"{_fmt(home_score.get('display', home_score.get('current')))} : "
                        f"{_fmt(away_score.get('display', away_score.get('current')))}"),
        ("Winner", _fmt(winner)),
    ]
    layout.addWidget(_section(f"Match: {_fmt(home.get('name'))} vs {_fmt(away.get('name'))}"))
    layout.addWidget(_kv_table(meta))

    periods = data.get("periods") or {}
    period_keys = [k for k in periods if k != "current"] + ["normaltime"]
    if period_keys:
        rows = []
        for k in period_keys:
            label = _fmt(periods.get(k, k))
            rows.append([label, _fmt(home_score.get(k)), _fmt(away_score.get(k))])
        layout.addWidget(QLabel("<b>Score by period</b>"))
        layout.addWidget(_grid_table(rows, ["Period", _fmt(home.get("shortName") or home.get("name")),
                                            _fmt(away.get("shortName") or away.get("name"))]))

    time_info = data.get("time") or {}
    if time_info:
        layout.addWidget(QLabel("<b>Timing</b>"))
        layout.addWidget(_kv_table([(_fmt(k), _fmt(v)) for k, v in time_info.items()]))


_BUILDERS = {
    "wikidata": _render_wikidata,
    "mobile_phone": _render_gsmarena,
    "weather_forecast": _render_openweather,
    "owid": _render_owid,
    "ice_hockey": _render_icehockey,
}
