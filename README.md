# RHUM-RUM bathymetry map — version 2

Plot YV ocean-bottom stations, RR41, bathymetry, ocean ridges and regional plate
labels using PyGMT and ObsPy.

![Historical RHUM-RUM map](MAP_RHUM1_Ridges.jpg)

The image above is the original illustration, not a newly validated v2 output.

## Install and run

PyGMT requires the native GMT library; a conda-forge environment installs both:

```bash
git clone https://github.com/MohammadAmin-Aminian/Map.git
cd Map
conda env create -f environment.yml
conda activate rhum-map
python MAP_RHUM_RUM.py --output rhum-rum.jpg
```

Use `--show` to open the figure. The default region is 45–75°E, 35–15°S and the
relief grid is `@earth_relief_30s`. Choose `--relief @earth_relief_01m` for a smaller
download, or provide a local GMT-compatible grid path. High-resolution relief can
require substantial network traffic and memory.

Station metadata comes from the RESIF FDSN service; `--provider` selects another
provider. Supply `--inventory stations.xml` to use local StationXML containing the
listed YV stations and RR41. GMT relief and ridge datasets may still need downloading
on their first use. Service availability and dataset retrieval are external dependencies.
Existing output files are refused. No downloads or plotting occur on import.

## Version 2 fixes

The inset rectangle now matches the actual map region. Station coordinates come
from station metadata rather than assuming every station has a first channel.
All networks are traversed, duplicate epochs are collapsed, conflicting epochs and
missing stations produce explicit errors, and plotting uses PyGMT's `fill` option.
Output paths, relief resolution and figure display are configurable.

## Tests and references

```bash
python -m pytest -q
```

Tests check metadata traversal, duplicate/conflicting epochs and inset coordinates
with a simulated plotting interface. Full rendering requires GMT and its datasets;
remote service access and a publication-ready rendered map are not covered by these tests.

[PyGMT documentation](https://www.pygmt.org/latest/) ·
[ObsPy station metadata](https://docs.obspy.org/packages/obspy.clients.fdsn.html)

Author: Mohammad Amin Aminian. No license was present in the original repository;
no additional reuse rights are asserted here.
