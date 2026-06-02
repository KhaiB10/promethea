"""
benchmarks/msbr/plot_geometry.py

Geometry-verification PNGs for the v0.4.0 MSBR scaffold. Renders:
  - unit cell, radial slice (z = 0)
  - full core + blanket + reflector + vessel, radial slice (z = 0)
  - full core, axial slice (y = 0)

No simulation, no cross-section dependency. Quick visual sanity check
to catch topology bugs (interleaved-vs-annulus mistakes, vessel
swallowing the core, etc.).

Outputs written to out/plots/msbr/.
"""
from __future__ import annotations

import os
import pathlib

import openmc

from .geometry_unit_cell import build_unit_cell_geometry, EQUAL_AREA_R_CM
from .geometry_lattice import (
    build_core_geometry,
    VESSEL_OUTER_RADIUS_CM,
    CORE_HEIGHT_CM,
)


def _plot(geometry: openmc.Geometry, *, name: str, basis: str,
          width: tuple[float, float], pixels: tuple[int, int],
          colors: dict[openmc.Material, tuple[int, int, int]] | None = None,
          out_dir: pathlib.Path) -> pathlib.Path:
    plot = openmc.Plot()
    plot.basis = basis
    plot.width = width
    plot.pixels = pixels
    plot.filename = name
    if colors:
        plot.colors = colors
    plot.color_by = "material"
    plots = openmc.Plots([plot])
    plots.export_to_xml()
    geometry.export_to_xml()
    geometry.materials.export_to_xml() if hasattr(geometry, "materials") else None
    openmc.plot_geometry(output=False)
    src = pathlib.Path(f"{name}.png")
    if not src.exists():
        # OpenMC sometimes emits .ppm; convert
        ppm = pathlib.Path(f"{name}.ppm")
        if ppm.exists():
            src = ppm
    dst = out_dir / src.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        src.replace(dst)
    return dst


def main() -> int:
    out_dir = pathlib.Path("out/plots/msbr").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    work = pathlib.Path("sims/openmc/msbr_plot").resolve()
    work.mkdir(parents=True, exist_ok=True)
    os.chdir(work)

    # ---- Unit cell -------------------------------------------------------
    geom_uc, mats_uc = build_unit_cell_geometry()
    mats_uc.export_to_xml()
    geom_uc.export_to_xml()
    w_uc = 2.0 * EQUAL_AREA_R_CM * 1.05
    _plot(geom_uc, name="msbr_unit_cell_xy", basis="xy",
          width=(w_uc, w_uc), pixels=(800, 800), out_dir=out_dir)

    # ---- Full core, radial slice ----------------------------------------
    geom_full, mats_full = build_core_geometry()
    mats_full.export_to_xml()
    geom_full.export_to_xml()
    w_full = 2.0 * VESSEL_OUTER_RADIUS_CM * 1.05
    _plot(geom_full, name="msbr_core_xy", basis="xy",
          width=(w_full, w_full), pixels=(1200, 1200), out_dir=out_dir)

    # ---- Full core, axial slice -----------------------------------------
    _plot(geom_full, name="msbr_core_xz", basis="xz",
          width=(w_full, CORE_HEIGHT_CM * 1.10),
          pixels=(1200, int(1200 * CORE_HEIGHT_CM / (2.0 * VESSEL_OUTER_RADIUS_CM))),
          out_dir=out_dir)

    print(f"[msbr] plots written to {out_dir}")
    for p in sorted(out_dir.glob("*.png")):
        print(f"  {p.name}  ({p.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
