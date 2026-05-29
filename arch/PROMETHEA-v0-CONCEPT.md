# Promethea v0 — Working Concept

**Status:** Concept only. No simulations have been run yet. Every number here is a target or starting assumption, not a result.

## Core idea
A community-scale, walk-away-safe, thorium-fueled molten chloride salt fast microreactor with an AI-driven control system.

## Top-level parameters (targets, not results)

| Parameter | Target |
|---|---|
| Electrical output | ~5 MWe |
| Thermal output | ~15 MWth |
| Thermal efficiency | ~33 % (sCO₂ Brayton aspirational at ~45 %) |
| Refueling interval | ≥ 8 years |
| Footprint | Transportable in standard shipping containers |
| Outlet temperature | 700–750 °C |
| Operating pressure | Near-atmospheric (low-pressure salt) |
| Spectrum | Fast (no moderator) |
| Safety class | Walk-away passive (negative temperature coefficient, freeze-plug equivalent) |

## Fuel & salt chemistry (working assumption)

- **Primary salt:** NaCl–MgCl₂ eutectic base
- **Fuel load:** ThCl₄ (fertile) + UCl₃ enriched with HALEU U-235 (~19.75 %) as starter
- **Chlorine isotope:** Cl-37 enriched (>99 %) in the published reference case; un-enriched comparison case run for reference
- **Long-term:** U-233 bred from Th-232 carries reactivity once equilibrium is approached

## Configuration

- **Primary loop:** Pumped fuel salt through the core
- **Secondary loop:** Heat-pipe array (eVinci-style), passive decay heat removal
- **Power conversion:** sCO₂ Brayton cycle
- **Containment:** Sealed canister, designed for factory build + sealed transport

## Why these choices

| Choice | Rationale |
|---|---|
| Chloride over fluoride | Higher actinide solubility, no Li-7 supply chain, simpler chemistry |
| Fast over thermal | No moderator needed, online actinide burnup, smaller core |
| Thorium fertile load | Abundant, US-domestic, proliferation-resistant relative to U/Pu |
| HALEU starter | Only realistic fissile starter available under current US regs |
| 5 MWe scale | Matches eVinci → direct comparison; community/data-center addressable |
| Heat-pipe secondary | Walk-away safe, transportable, no high-pressure water |

## Open questions to resolve in Phase 2

1. Salt eutectic exact composition vs. corrosion of structural alloy
2. Starter fissile mass — minimum for criticality at our geometry
3. Breeding ratio achievable in a small fast-spectrum core (this is genuinely hard)
4. Reflector material (BeO? Graphite? Stainless?)
5. Heat-pipe working fluid and alloy at sustained 750 °C
6. Drain tank geometry for freeze-plug-equivalent passive shutdown

## What we are explicitly NOT solving (Phase 1)
- Fuel reprocessing chemistry
- Licensing strategy
- Manufacturing process
- Public siting analysis

These are deferred to Phase 3.
