# 3. Requirement 1: Understanding Cooling Efficiency Through the Open Freezer Case

*Draft for the paper. Numbers come from `outputs/` (run `freezer.py`). Section 4 (Requirement 2a) builds directly on the three principles at the end of this section.*

## 3.1 What an open freezer case does

An open freezer case has two jobs:

- keep frozen food at or below −18 °C (0 °F), the food-safety storage temperature;
- let shoppers see and take the food without opening anything.

These jobs conflict. The opening that lets customers reach in also lets warm, moist store air in. A vertical case protects its opening with an air curtain, a thin jet of cold air blown downward across the front. A horizontal (island) case relies on the fact that cold air is heavy and stays in the well.

To see which quantities an efficiency measure needs, we follow the heat that a typical case removes. The reference case is a 12-ft (3.66 m) low-temperature vertical open multideck case:

- opening 3.66 × 1.6 m, total display area (TDA) 63 ft²;
- case air at −25 °C, product surface at −20 °C;
- remote condensing;
- store at 25 °C / 60 % RH, which is climate class 3 of the display-case test standard ISO 23953.

## 3.2 A heat balance of the case

The refrigeration system must remove every watt that enters the case:

$$
Q = \underbrace{\dot m \big[c_p (T_s - T_c) + (W_s - W_c)(h_{fg} + h_{if})\big]}_{\text{infiltration (sensible + latent)}}
+ \underbrace{\varepsilon F \sigma A (T_s^4 - T_p^4)}_{\text{radiation through the opening}}
+ \underbrace{U A_w (T_s - T_c)}_{\text{conduction}}
+ \underbrace{P_{\text{fans}} + P_{\text{lights}} + \tfrac12 P_{\text{heaters}}}_{\text{internal heat}}
$$

- Infiltrated water vapour first condenses and then freezes on the coil, so its latent load includes both the heat of condensation $h_{fg}$ and the heat of fusion $h_{if} = 334$ kJ/kg.
- The frost must be melted off by electric defrost. We take 30 % of defrost heat to reach the frost.
- Electricity is

$$
E = \frac{Q}{\mathrm{COP}} + E_{\text{fans, lights, heaters}} + E_{\text{defrost}},
$$

with COP = 1.6 for a low-temperature system.

**Calibration.** Published measurements put infiltration at 67–81 % of the total load of open vertical cases. We set the infiltration mass flow so that infiltration is 75 % at class 3. The result is $\dot m = 0.053$ kg/s, equivalent to store air crossing the whole opening at only 0.8 cm/s.

**Independent checks** (Table S0):

1. **Door retrofit.** Under the ASHRAE 72 door-opening protocol (each door opened about 6 times per hour for 8 of 24 hours), adding glass doors cuts the modelled refrigeration load by 75.9 % and electricity by 68.5 %. Laboratory tests report load reductions of 68–80 % and electricity reductions of 61 % (ISO 23953 test) to 71 % (manufacturer test).
2. **DOE limit.** The modelled open case uses 119.0 kWh/day, below the DOE limit for its class (VOP.RC.L: 2.27·TDA + 6.85 = 149.9 kWh/day).
3. **Energy closure.** The latent load equals the frost mass times the heat of condensation plus fusion.

## 3.3 Where the cooling goes

**Table S1. Three designs of the same case** (store 25 °C / 60 %).

| Design | Load (kWh/day) | Share entering through the opening | Frost (kg/day) | Electricity (kWh/day) | Service (m²·h per kWh) |
|---|---|---|---|---|---|
| Open, air curtain | 141.6 | **87 %** | 52.3 | 119.0 | 0.79 |
| + night covers (8 h) | 108.7 | 83 % | 38.3 | 93.2 | 1.01 |
| Glass doors (store traffic) | 49.8 | 37 % | 9.1 | 50.1 | 1.87 |

The load of the open case breaks down as follows (Fig. S1): infiltration 64.3 kWh sensible plus 41.8 kWh latent, radiation 16.9, conduction 8.9, internal 9.6.

**87 % of the cooling an open freezer case produces is spent fighting the opening**: warm air sliding through the air curtain and heat radiated from the store. Only 13 % offsets the wall heat leak and the case's own fans and lights. The latent part also forms 52 kg of frost per day, and melting it costs another 19.7 kWh of electricity, 17 % of the case's total.

## 3.4 Should efficiency depend only on energy use? No.

Energy use alone fails for four reasons, each of which the model quantifies.

**1. Energy use is not the output.** An unplugged case uses no energy and fails its only purpose. The numerator of an efficiency must be the service delivered: display area that shoppers can reach during trading hours, with every product at or below −18 °C. The DOE standard already reflects this: it normalises the energy limit by display area (kWh/day per ft² of TDA), not by case size.

**2. The same case uses different energy in different air.**

- With products, temperatures and service unchanged, moving the store from 21 °C / 40 % to 27 °C / 70 % raises consumption from 91.1 to 136.8 kWh/day (×1.50, Fig. S2). Each additional 10 points of relative humidity costs 6–9 kWh/day, mostly through frost.
- An efficiency comparison must therefore state the ambient conditions. Test standards fix them for this reason: ISO 23953 tests at defined climate classes.

**3. Design matters more than the refrigeration machinery.**

- Night covers on the 8 closed hours save 22 % at no cost to service.
- Glass doors save 58 % with store traffic (20 openings per door per hour) and 74 % with test-protocol traffic.
- Geometry matters even more. DOE allows a horizontal open low-temperature case 0.57 kWh/day per ft² of display area against 2.27 for a vertical one, a factor of 4.0. Cold air pools in a horizontal well, but it drains out of a vertical opening, the same buoyant spill that limits any opening on its vertical side.

**4. The system boundary changes the answer.**

- Heat and moisture that the case pulls out of the store air are cooling the store would otherwise have to provide in summer. In a cooling-dominated store (Houston-like, 85 % of the year in cooling), counting that credit lowers the open case's net cost from 119.0 to 87.0 kWh/day (−27 %).
- In a heating-dominated store (Minneapolis-like) it raises the cost to 127.0 kWh/day (+7 %), because the store must re-heat the air the case chills.
- Doors remain the lower-energy design in both stores (41.3 and 53.7 kWh/day).

**Access has a value too.** Doors save 69 kWh/day, or $3,268 per case per year at $0.13/kWh. They pay off unless they cost more than $8.95 of gross margin per day, about nine fewer items sold at $1 margin each. A New Zealand supermarket pilot found no lasting change in purchases after doors were fitted. Retailers still weigh this, which is why access belongs in the efficiency measure as a factor rather than being assumed away.

## 3.5 The quantities a cooling-efficiency measure must include

$$
\eta_F \;=\; \frac{A_{\text{display}} \cdot t_{\text{trading}} \cdot \mathbb{1}\!\left[T_{\text{product}} \le -18\,^\circ\text{C}\right] \cdot a}{E_{\text{case}} + \Delta E_{\text{store HVAC}}}
\qquad \left[\frac{\text{m}^2\cdot\text{h}}{\text{kWh}}\right],
$$

where $a \le 1$ is an access factor (1 for an open case). For the three designs, $\eta_F$ = 0.79, 1.01 and 1.87 m²·h/kWh with $a = 1$.

| Quantity | Why it belongs | Size in the reference case |
|---|---|---|
| Product temperature (safety) | The purpose of the case; a hard constraint | ≤ −18 °C |
| Service delivered (display area × hours) | Energy alone rewards switching off | 5.86 m² × 16 h |
| Where cooling goes (useful vs. lost through the opening) | Reveals what can be saved | 87 % lost through the opening |
| All energy inputs (compressor, fans, lights, heaters, defrost) | Defrost alone is 17 % | 119 kWh/day |
| Ambient conditions (store T and RH) | Same case, ×1.50 energy | 91–137 kWh/day |
| Design (curtain, covers, doors, geometry) | Largest lever | −22 % to −58 %; ×1/4 for horizontal |
| System boundary (store HVAC interaction) | Changes net cost by −27 % to +7 % | 87–127 kWh/day |
| Customer access | The reason the case is open | break-even $8.95/day |

## 3.6 From the freezer to open-air public spaces

| Freezer case | Bus stop / station |
|---|---|
| Frozen product | Waiting passengers |
| −18 °C safety limit | UTCI heat-stress bands |
| Opening needed for access | Open sides needed for boarding |
| Air curtain | Wind screens, jets aimed at people |
| Cold air spills out of the bottom; warm air enters | Cooled air spills out of the open sides; wind carries it away |
| Moisture becomes frost | Evaporative cooling adds moisture |
| Store temperature and humidity | Outdoor temperature, humidity, wind |
| Night covers | Switch off when nobody is waiting |
| Lost cooling partly recovered by store HVAC | Lost cooling lost to the street: no recovery |
| Horizontal well holds cold air | Enclosed or sunken waiting areas |

Three principles carry into Section 4:

1. **Count only cooling that reaches its target**: the product here, people at the bus stop.
2. **A device's effect depends on the surrounding air**: store humidity here, outdoor wet-bulb temperature for evaporative coolers.
3. **Efficiency = service delivered ÷ all resources used, within a stated boundary.** Open-air venues have no store HVAC to recover lost cooling, so delivery to people matters even more there.

---

**Figures for this section:**

- `outputs/figS1_load_breakdown.png`
- `outputs/figS2_store_climate.png`

**References used here:**

- ASHRAE Handbook—Refrigeration (display cases; Gosney–Olama door infiltration)
- ISO 23953-2 (refrigerated display cabinets, climate classes)
- ANSI/ASHRAE Standard 72-2022 and DOE test procedure final rule (Federal Register, Sept. 26, 2023)
- DOE energy conservation standards (74 FR, Jan. 2009), 10 CFR 431.66
- NREL (2025) report on display-case infiltration
- Amin, Dabiri & Navaz (2008, 2011) tracer-gas infiltration studies
- DOE Better Buildings door-retrofit case study
- Hillphoenix door-retrofit case study
- LSBU ICR 2019 paper 280
