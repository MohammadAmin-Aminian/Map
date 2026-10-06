"""Generate a RHUM-RUM station and bathymetry map with PyGMT."""

import argparse
import math
from pathlib import Path

STATIONS = "RR28,RR29,RR34,RR36,RR38,RR40,RR50,RR52"
REGION = (45, 75, -35, -15)


def station_coordinates(inventory):
    """Read station metadata across all networks, deduplicating station epochs."""
    points = {}
    for network in inventory:
        for station in network:
            key = (network.code, station.code)
            lon, lat = float(station.longitude), float(station.latitude)
            if (
                not math.isfinite(lon)
                or not math.isfinite(lat)
                or not -180 <= lon <= 180
                or not -90 <= lat <= 90
            ):
                raise ValueError(f"Invalid coordinates for {key}")
            if key in points and points[key] != (lon, lat):
                raise ValueError(
                    f"Conflicting station epochs for {key}; narrow the query dates"
                )
            points[key] = (lon, lat)
    if not points:
        raise ValueError("No stations returned")
    return [
        (f"{net}.{sta}", lon, lat) for (net, sta), (lon, lat) in sorted(points.items())
    ]


def build_map(inventory, seamount_inventory, relief="@earth_relief_30s"):
    import pygmt

    points = station_coordinates(inventory)
    labels = [point[0].split(".", 1)[1] for point in points]
    lons = [point[1] for point in points]
    lats = [point[2] for point in points]
    seamount_points = station_coordinates(seamount_inventory)
    if len(seamount_points) != 1:
        raise ValueError("Expected exactly one seamount station")
    seamount = seamount_points[0]
    ridge_data = pygmt.datasets.load_sample_data(name="ocean_ridge_points")
    minlon, maxlon, minlat, maxlat = REGION

    topo_data = relief
    fig = pygmt.Figure()
    pygmt.makecpt(cmap="topo", series="-8000/8000/1000", continuous=True)

    fig.grdimage(
        grid=topo_data,
        region=[minlon, maxlon, minlat, maxlat],
        projection="M4i",
        shading=True,
        frame=True,
    )

    fig.plot(
        data=ridge_data,
        style="c0.05c",  # Small circle marker
        fill="red",
        pen="black",
    )

    fig.text(
        x=55.5,
        y=-21,
        text="La Réunion",
        offset="0.2c",
        font="10p,Times-Bold,black",
        justify="LM",
    )

    fig.text(
        x=66,
        y=-18,
        text="CIR",
        offset="0.2c",
        font="10p,Times-Bold,blue",
        justify="LM",
        angle=-65,
        fill="lightorange",  # Background fill color
    )

    fig.text(
        x=60,
        y=-29,
        text="SWIR",
        offset="0.2c",
        font="10p,Times-Bold,blue",
        justify="LM",
        angle=35,
        fill="lightorange",  # Background fill color
    )

    fig.text(
        x=72,
        y=-27,
        text="SEIR",
        offset="0.2c",
        font="10p,Times-Bold,blue",
        justify="LM",
        angle=-40,
        fill="lightorange",  # Background fill color
    )

    fig.text(
        x=53,
        y=-27,
        text="Somali Plate",
        offset="0.2c",
        font="10p,Times-Bold,purple",
        justify="LM",
        angle=0,
        fill="lightyellow",  # Background fill color
        pen="1p,black",
    )
    fig.text(
        x=70.5,
        y=-16.5,
        text="Australian Plate",
        offset="0.2c",
        font="10p,Times-Bold,purple",
        justify="LM",
        angle=-65,
        fill="lightyellow",  # Background fill color
        pen="1p,black",
    )
    fig.text(
        x=60,
        y=-35,
        text="Antarctic Plate",
        offset="0.2c",
        font="10p,Times-Bold,purple",
        justify="LM",
        angle=45,
        fill="lightyellow",  # Background fill color
        pen="1p,black",
    )

    with fig.inset(position="jBR+w2c+o0.5c/0.2c", box="+pgrey+p3p,black"):
        fig.coast(
            region=[5, 140, -40, 80],
            projection="M3c",
            borders=[1, 2],
            shorelines="1/thin",
            water="white",
            land="gray",
        )

        rectangle = [[minlon, minlat, maxlon, maxlat]]
        fig.plot(data=rectangle, style="r+s", pen="1p,red")
    fig.plot(
        x=lons,
        y=lats,
        style="t0.10i",  # Triangle marker with size 0.15 inches
        fill="red",
        pen="black",
        label="Broadband OBS",
    )

    fig.colorbar(frame='+l"Elevation (m)"')

    for label, lon, lat in zip(labels, lons, lats):
        if label == "RR40":
            fig.text(
                x=lon,
                y=lat - 1,
                text=label,
                offset="0.2c",
                font="10p,Times-Bold,black",
                justify="LM",
                no_clip=True,
                fill="lightblue",
            )
        else:
            fig.text(
                x=lon,
                y=lat,
                text=label,
                offset="0.2c",
                font="10p,Times-Bold,black",
                justify="LM",
                no_clip=True,
                fill="lightblue",
            )

    fig.plot(
        x=seamount[1],
        y=seamount[2],
        style="a0.3c",  # Triangle marker with size 0.15 inches
        fill="yellow",
        pen="black",
        label="Active Seamount",
    )

    fig.legend(
        position="JTL+jTL+o0.1c",  # Place legend at Top Right corner inside the map, with a slight offset
        box="+gwhite+p1p",  # White background with a black outline of 1 point thickness
    )
    return fig


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("MAP_RHUM1.jpg"))
    parser.add_argument("--relief", default="@earth_relief_30s")
    parser.add_argument("--provider", default="RESIF")
    parser.add_argument(
        "--inventory",
        type=Path,
        help="Local StationXML with YV stations including RR41",
    )
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error("output already exists; choose a new path")
    if args.inventory:
        from obspy import read_inventory

        all_stations = read_inventory(str(args.inventory))
        from obspy.core.inventory import Inventory

        inventory = Inventory([], source=all_stations.source)
        for station in STATIONS.split(","):
            inventory += all_stations.select(network="YV", station=station)
        seamount_inventory = all_stations.select(network="YV", station="RR41")
    else:
        from obspy.clients.fdsn import Client

        client = Client(args.provider)
        inventory = client.get_stations(network="YV", station=STATIONS, level="station")
        seamount_inventory = client.get_stations(
            network="YV", station="RR41", level="station"
        )
    returned = {p[0].split(".", 1)[1] for p in station_coordinates(inventory)}
    missing = set(STATIONS.split(",")) - returned
    if missing:
        raise ValueError(f"Missing requested stations: {sorted(missing)}")
    figure = build_map(inventory, seamount_inventory, args.relief)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(str(args.output), dpi=300)
    if args.show:
        figure.show(dpi=300)


if __name__ == "__main__":
    main()
