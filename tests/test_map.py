import sys
from types import SimpleNamespace

import pytest
from MAP_RHUM_RUM import build_map, station_coordinates
from obspy.core.inventory import Inventory, Network, Station


def inventory(code="YV", stations=None):
    return Inventory(
        [Network(code, stations=stations or [Station("RR38", -21, 55, 0)])], "test"
    )


def test_station_level_metadata_and_multiple_networks():
    points = station_coordinates(inventory() + inventory("XX"))
    assert len(points) == 2
    assert ("YV.RR38", 55, -21) in points
    assert len(station_coordinates(inventory() + inventory())) == 1


def test_conflicting_epochs_rejected():
    with pytest.raises(ValueError):
        station_coordinates(
            inventory(
                stations=[Station("RR38", -21, 55, 0), Station("RR38", -22, 55, 0)]
            )
        )


def test_inset_matches_main_region(monkeypatch):
    calls = []

    class Figure:
        def __getattr__(self, name):
            def call(**kwargs):
                calls.append((name, kwargs))
                return self

            return call

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setitem(
        sys.modules,
        "pygmt",
        SimpleNamespace(
            Figure=Figure,
            makecpt=lambda **kwargs: None,
            datasets=SimpleNamespace(load_sample_data=lambda **kwargs: []),
        ),
    )
    build_map(inventory(), inventory(stations=[Station("RR41", -21, 55, 0)]))
    rectangle = [
        kwargs["data"]
        for name, kwargs in calls
        if name == "plot" and kwargs.get("style") == "r+s"
    ]
    assert rectangle == [[[45, -35, 75, -15]]]
    assert all("color" not in kwargs for name, kwargs in calls)
