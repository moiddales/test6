# Two named-venue applications

The cases are Phoenix Zoo's Plaza de los Ninos shade area and the shaded veranda at Discovery Green's Grove Market and Park Provisions in Houston. Official operator pages establish the existence and outdoor/shaded character of these places. They do not establish dimensions, local weather, visitor counts or equipment performance.

`cases.json` separates verified facts from assumed 8 × 5 m study patches, 24 occupants and a common 10:00–16:00 window. PHX/IAH weather is a regional proxy. All equipment configurations are hypothetical interventions, not claims about installed systems or measured savings. Geometries are intentionally simplified; enclosure fractions and mass require field survey before a design decision.

Run `python venues/run_venues.py`. The same dynamic heat/moisture engine is used with train effects disabled. Six A units, four B units or three C units approximately cover the assumed crowd. A 15 kW AC case tests loss through open boundaries. An improved-shade scenario reduces assumed midday MRT excess from 12°C to 6°C without pretending to know a construction specification. It is compared against the original shade-only reference, so its benefit is counted explicitly; zero operating energy is not assigned infinite efficiency.

The scale test halves or doubles area and crowd together while retaining equipment. Coverage saturation prevents interpreting total relief as proportional to floor area. Costs and passive investment are handled in `tradeoffs.py`, separate from thermal-resource efficiency.
