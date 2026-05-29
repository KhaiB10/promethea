#!/usr/bin/env python3
"""
MSRE geometry verification plots.

Produces three PNG plots of the het_critical configuration:
  1. Single stringer unit cell, looking down the z-axis at the active-core
     midplane. Used to verify half-channel orientation (Phase 1.1.d step 1).
  2. Lattice tile (3x3 stringers) at the same z-elevation, showing how
     adjacent stringer half-channels combine into full fuel channels.
  3. Full active-core cross-section at z=0 (active-core midplane), showing
     vessel + can + lattice + control-rod thimbles + sample basket.
  4. Vertical cross-section through y=0 (cuts through 2 rods), showing
     the full vertical extent: lower head -> active core -> upper plenum.

Outputs go to ``out/plots/`` so the CI artifact upload picks them up.

Usage::

    python plot_geometry.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless

import openmc

# Make the local package importable when invoked as a script.
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))  # repo root

from benchmarks.msre.materials import build_all
from benchmarks.msre.geometry_het import (
    build_geometry_het_critical,
    STRINGER_PITCH,
    ACTIVE_CORE_HEIGHT,
)


BENCHMARK_TEMP_K = 922.04


def main():
    out_dir = Path("out/plots")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("[plot_geometry] building het_critical model...")
    mats_dict, mats = build_all(temperature_K=BENCHMARK_TEMP_K, irphe=True)
    geometry, extra_mats = build_geometry_het_critical(mats_dict)

    # OpenMC's plot API needs a Model with materials + geometry + settings.
    settings = openmc.Settings()
    settings.run_mode = "plot"
    materials_obj = openmc.Materials(list(mats) + list(extra_mats))
    model = openmc.Model(
        geometry=geometry,
        materials=materials_obj,
        settings=settings,
    )

    # ------------------------------------------------------------------ #
    # Plot 1: single stringer unit cell, 5.5 cm window at z = 0
    # ------------------------------------------------------------------ #
    plot1 = openmc.Plot()
    plot1.filename = "01_stringer_unit_cell"
    plot1.basis = "xy"
    plot1.origin = (0.0, 0.0, 0.0)
    plot1.width = (5.5, 5.5)
    plot1.pixels = (1200, 1200)
    plot1.color_by = "material"
    plot1.colors = _material_palette(materials_obj)

    # ------------------------------------------------------------------ #
    # Plot 2: 3x3 lattice tile (3 * 5.08 = 15.24 cm window)
    # ------------------------------------------------------------------ #
    plot2 = openmc.Plot()
    plot2.filename = "02_lattice_3x3"
    plot2.basis = "xy"
    plot2.origin = (0.0, 0.0, 0.0)
    plot2.width = (3 * STRINGER_PITCH + 0.5, 3 * STRINGER_PITCH + 0.5)
    plot2.pixels = (1500, 1500)
    plot2.color_by = "material"
    plot2.colors = _material_palette(materials_obj)

    # ------------------------------------------------------------------ #
    # Plot 3: full active-core cross-section at z = 0
    # ------------------------------------------------------------------ #
    plot3 = openmc.Plot()
    plot3.filename = "03_core_xy_midplane"
    plot3.basis = "xy"
    plot3.origin = (0.0, 0.0, 0.0)
    plot3.width = (160.0, 160.0)  # vessel OD is ~150 cm, give a margin
    plot3.pixels = (2000, 2000)
    plot3.color_by = "material"
    plot3.colors = _material_palette(materials_obj)

    # ------------------------------------------------------------------ #
    # Plot 4: full active-core cross-section at z = +50 cm
    # This slice intersects the inserted control rod (rod tip at z=+35.139
    # cm). At z=+50 cm the poison column is present, so this plot shows
    # the inserted-rod thimble distinct from the three withdrawn thimbles.
    # ------------------------------------------------------------------ #
    plot4 = openmc.Plot()
    plot4.filename = "04_core_xy_above_rod_tip"
    plot4.basis = "xy"
    plot4.origin = (0.0, 0.0, 50.0)
    plot4.width = (40.0, 40.0)  # zoom on the rod cluster + nearby lattice
    plot4.pixels = (1600, 1600)
    plot4.color_by = "material"
    plot4.colors = _material_palette(materials_obj)

    # ------------------------------------------------------------------ #
    # Plot 5: vertical xz cross-section through y = +7.62 cm
    # (passes through the two rods at +y, including the inserted one at
    # x=-7.62 y=+7.62). Shows the full vertical extent: lower head ->
    # active core -> upper plenum, and the rod tip position at z=+35.139.
    # ------------------------------------------------------------------ #
    plot5 = openmc.Plot()
    plot5.filename = "05_core_xz_y_rod_row"
    plot5.basis = "xz"
    plot5.origin = (0.0, 7.62, 0.0)
    plot5.width = (50.0, ACTIVE_CORE_HEIGHT + 80.0)
    plot5.pixels = (1200, 2400)
    plot5.color_by = "material"
    plot5.colors = _material_palette(materials_obj)

    model.plots = openmc.Plots([plot1, plot2, plot3, plot4, plot5])

    # Export and run the OpenMC plot command from a clean working subdir.
    workdir = Path("out/plot_run")
    workdir.mkdir(parents=True, exist_ok=True)

    cwd = Path.cwd()
    try:
        os.chdir(workdir)
        model.export_to_xml()
        print(f"[plot_geometry] exported XML to {workdir}")
        openmc.plot_geometry(output=True)
        print("[plot_geometry] OpenMC plot run complete")

        # Convert .ppm to .png and copy to out/plots/
        png_dir = cwd / "out" / "plots"
        png_dir.mkdir(parents=True, exist_ok=True)
        for plot in [plot1, plot2, plot3, plot4, plot5]:
            name = Path(plot.filename).name
            ppm_path = Path(f"{name}.ppm")
            if not ppm_path.exists():
                # OpenMC sometimes writes .png natively; check both.
                png_path = Path(f"{name}.png")
                if png_path.exists():
                    target = png_dir / f"{name}.png"
                    target.write_bytes(png_path.read_bytes())
                    print(f"[plot_geometry] copied {png_path.name} -> {target}")
                    continue
                print(f"[plot_geometry] WARNING: no output for {name}")
                continue
            png_target = png_dir / f"{name}.png"
            _ppm_to_png(ppm_path, png_target)
            print(f"[plot_geometry] converted {ppm_path.name} -> {png_target}")
    finally:
        os.chdir(cwd)

    print("[plot_geometry] done. Outputs in out/plots/")


def _material_palette(materials_obj: openmc.Materials):
    """Assign distinct colors to materials by name. Returns dict suitable
    for openmc.Plot.colors."""
    # Color scheme picked so salt (yellow), graphite (dark gray),
    # INOR-8 (steel blue), poison (red), vessel/can (slate) are all
    # visually distinct.
    # Order matters: more specific keys first because matching is substring-
    # based and stops at the first hit. "inconel" must be checked before
    # "inor" since "inor" is a substring of "inconel-600".
    name_colors = [
        ("inconel",     (170, 100, 60)),    # copper/brown (Inconel rod cladding)
        ("lower-head",  (170, 145, 90)),    # tan (lower-head mix)
        ("basket",      (210, 180, 110)),   # tan (sample basket mix)
        ("gd",          (200, 30, 30)),     # red (Gd2O3 poison bushing)
        ("poison",      (200, 30, 30)),
        ("mix",         (170, 145, 90)),    # tan (other mixes)
        ("helium",      (220, 220, 250)),   # pale blue
        ("salt",        (255, 215, 0)),     # gold
        ("graph",       (40, 40, 40)),      # dark gray
        ("inor",        (90, 110, 140)),    # steel blue
    ]
    fallback = (180, 180, 180)
    palette = {}
    for mat in materials_obj:
        name_lc = (mat.name or "").lower()
        chosen = None
        for key, rgb in name_colors:
            if key in name_lc:
                chosen = rgb
                break
        palette[mat] = chosen if chosen else fallback
    return palette


def _ppm_to_png(ppm_path: Path, png_path: Path):
    """Convert a P6 PPM file to PNG. Avoids needing PIL/Pillow.

    OpenMC writes simple P6 binary PPMs: 'P6\n<w> <h>\n<maxval>\n<rgb bytes>'
    """
    from PIL import Image  # Pillow is in scientific Python container
    img = Image.open(ppm_path)
    img.save(png_path, "PNG")


if __name__ == "__main__":
    main()
