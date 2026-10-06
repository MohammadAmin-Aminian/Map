"""Render with the real GMT engine using entirely local synthetic input."""

import numpy as np
import pytest
from MAP_RHUM_RUM import build_map
from obspy.core.inventory import Inventory, Network, Station


def test_real_gmt_png(tmp_path, monkeypatch):
    pygmt = pytest.importorskip("pygmt")
    import xarray as xr

    lon = np.linspace(45, 75, 61)
    lat = np.linspace(-35, -15, 41)
    heights = -4000 + 500 * np.sin(lon[None, :] / 3) * np.cos(lat[:, None] / 3)
    relief = xr.DataArray(heights, coords={"lat": lat, "lon": lon}, dims=("lat", "lon"))
    monkeypatch.setattr(
        pygmt.datasets,
        "load_sample_data",
        lambda **kwargs: np.array([[60.0, -25.0], [61.0, -24.0]]),
    )
    stations = Inventory(
        [Network("YV", stations=[Station("RR38", -21, 55, 0)])], "synthetic"
    )
    seamount = Inventory(
        [Network("YV", stations=[Station("RR41", -22, 56, 0)])], "synthetic"
    )
    figure = build_map(stations, seamount, relief=relief)
    output = tmp_path / "map.png"
    figure.savefig(output, dpi=80)
    assert output.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert output.stat().st_size > 1000
