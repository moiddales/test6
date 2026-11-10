# 5. Requirement 2b: Revising the Model for a Semi-Open Rail-Station Waiting Area

*Draft for the paper. Numbers come from `outputs/` (run `run_2b.py`). Outdoor conditions are the measured hot design days of Section 4 (PHX peak 46.4 °C, IAH peak 37.4 °C).*

## 5.1 Why the bus-stop model is not enough

The efficiency measure of Section 4 stays the same: heat-stress relief delivered to people per kWh of electricity plus embedded water energy. What has to change is the model that predicts the relief.

The bus-stop model rests on four facts about an open shelter:

1. Without cooling, the air people stand in is outdoor air.
2. Conditions are steady over minutes.
3. Coolers draw outdoor air.
4. Only fans and evaporative coolers make sense.

A semi-open waiting area breaks all four. It has walls, glazing and a roof that trap heat. Passengers build up between trains and leave in a block. Coolers draw air that is already cooled and humidified. With enough enclosure, air conditioning becomes an option.

This is the freezer lesson of Section 3 in reverse: a closed design keeps cooling in, but it also keeps heat and moisture in.

## 5.2 The station model

**Geometry.** A waiting area 30 m long and 8 m deep; the occupied zone is 2.5 m high. Closed wall areas are glass with a solar heat gain coefficient (SHGC) of 0.4. The 240 m² roof is a lightly insulated metal deck ($U$ = 1.0 W/m²K, varied 0.3–5.0).

| Scenario | Track side | Street side | Ends | Train arrival | Openness |
|---|---|---|---|---|---|
| Open-sided platform | open | open | open | gust replaces 30 % of zone air | 100 % |
| Semi-open waiting area (base) | open | 20 % | 50 % | gust replaces 30 % | 58 % |
| Platform screen doors | closed; 50 % open while a train dwells | 20 % | 20 % | doors only | 12 % |
| Enclosed waiting room | closed; 15 % open while a train dwells | 5 % | 5 % | doors only | 3 % |

A continuous sweep blends the enclosed room into the open platform.

**People and trains.**

- Peak hours (7–9 and 16–19): 400 passengers/h and a train every 6 min.
- Off-peak: 150 passengers/h every 10 min; 100 passengers/h after 19:00.
- Passengers accumulate between trains and board on arrival, so the count is a sawtooth. Dwell time is 40 s.

**Heat and moisture balance of the occupied zone:**

$$
C\frac{dT}{dt}=\rho c_p\big[Q_x(T_o-T)+Q_s(T_s-T)\big]+G-Q_{ac},\qquad
M\frac{dW}{dt}=\rho\big[Q_x(W_o-W)+Q_s(W_s-W)\big]+\dot m_p-\dot m_{ac}
$$

- Exchange with outdoors: $Q_x=\sqrt{Q_{\text{wind}}^2+Q_{\text{buoy}}^2}$, using the measured hourly wind, plus train gusts.
- Gains: $G = 75\,\text{W}\cdot N+\text{SHGC}\cdot A_{\text{glass}}\cdot I(t)\cdot 0.6+U_{\text{roof}}A\,(T_{\text{sa}}-T)+5\,\text{W/m}^2\cdot A+P_{\text{motors}}$.
- Roof: sol-air temperature $T_{\text{sa}} = T_o + \alpha I_{\text{hor}}/h_o - 3.9$ K (ASHRAE Fundamentals), with absorptance $\alpha$ = 0.6, peak horizontal irradiance 950 W/m² and $h_o$ = 17 W/m²K.
- Each 10-s step uses the exact solution of the linear balance.

**Cooling systems**, each sized for 40 waiting passengers:

| System | Configuration | Power |
|---|---|---|
| A | 10 fans | 2.5 kW |
| B | 8 evaporative coolers, 40 m³/s | 9.6 kW |
| C | 5 large coolers, 37.5 m³/s | 12.5 kW |
| D | 60 kW air conditioner | COP varies with outdoor temperature |

- Evaporative coolers draw zone air.
- For the air conditioner, $\mathrm{COP} = 0.45\,T_e/(T_c - T_e)$, which gives 3.19 at 35 °C, consistent with AHRI-rated EER 10–12.5. It has a sensible heat ratio of 0.75 (1.0 when the air is too dry to condense on the coil, as in Phoenix) and a 26 °C thermostat.
- Fans follow the smart rule of Section 4: each hour they run only if heat stress is at least strong and they lower it for the people they reach.

**Comfort and relief.** Mean radiant temperature is weighted by openness $f$: $T_{\text{mrt}} = f\,(T_o + 12) + (1-f)(T + 4)$. The open part of the view sees the outdoors, as under the bus-shelter roof; the enclosed part sees walls and roof that follow the zone air, so an air conditioner cools them too. Relief is measured against the same station without cooling, which can be hotter than outdoors.

## 5.3 What changed, why, and what it bought

The revisions are switched on one at a time (Table 2b-1). The platform-screen-door station shows the effects most clearly.

| Revision | Why it was necessary | Effect (platform screen doors) |
|---|---|---|
| **R0** Bus-stop model applied to the station | — | baseline |
| **R1** Heat gains: people, sun through glazing and roof, lights, motors | Walls and roof trap heat | Uncooled zone at 15:00 rises from 45.9 to 47.3 °C (hot-dry) and from 37.0 to 39.0 °C (hot-humid). Hot-dry fan $\eta$ falls from 13.8 to 7.7. Hot-humid fans leave 80.5 person-h of very strong heat stress where R0 predicted 10.9 |
| **R2** Train-driven dynamics | Crowds peak just before a train; open doors flush the zone | Evaporative $\eta$ falls 3–5 %; each 40-s door opening lifts zone air by 2.4–2.8 °C (dry) or 0.8–1.0 °C (humid) for a few minutes (Fig. 10) |
| **R3** Coolers recirculate zone air | Moisture added by evaporative cooling stays until ventilation removes it | Zone RH rises 8–14 points (hot-dry B: 26 → 39 %); $\eta$ changes by −2 % to +21 % |
| **R4** Air conditioning with outdoor-dependent COP and supply placement | Enclosure makes a vapour-compression system worth considering | Under the humidity limit, AC becomes the only admissible option in enclosed stations; low-level supply raises its $\eta$ by 36–49 % |

In the semi-open base case (58 % open), R0 and the full model agree closely: the uncooled zone is only 0.2–0.3 °C warmer, and B and C differ by under 10 %. Figure 11 maps this across openness:

- At 76 % open or more, the bus-stop model predicts evaporative-cooler efficiency within 11 %; at 52 % open, within about 14 %.
- At 3 % open, it underestimates evaporative cooling by 32–47 % and overestimates the humid-climate fan about 1.7 times (22.8 vs 13.8).

**The revision matters exactly where stations are enclosed.**

## 5.4 Results

**Table 2b-2. Efficiency $\eta$ (person·°C·h per kWh) by scenario.**

| Scenario | Climate | A fans | B evap | C large evap | D AC | UTCI ≥ 38 person-h: uncooled → with cooling |
|---|---|---|---|---|---|---|
| Open-sided platform | Hot-dry | 11.5 | 24.8 | **26.6** | 1.4 | 195.3 → C 52.7; B 121.7 |
| | Hot-humid | **24.8** | 9.7 | 10.4 | 1.1 | 107.8 → A 69.2; B, C 0 |
| Semi-open | Hot-dry | 10.7 | 26.0 | **27.1** | 1.4 | 186.2 → C 0; B 99.5 |
| | Hot-humid | **26.1** | 10.3 | 11.1 | 1.2 | 104.7 → A 57.7; B, C 0 |
| Screen doors | Hot-dry | 8.3 | **40.2** | 34.0 | 6.4 | 186.8 → B, C 0; D 141.9 |
| | Hot-humid | **20.3** | 15.7 | 14.2 | 5.3 | 108.9 → A 75.9; B, C, D 0 |
| Enclosed room | Hot-dry | — (never on) | **53.8** | 43.0 | 20.2 | 206.2 → B, C 0; D 59.2 |
| | Hot-humid | 13.8 | **23.6** | 19.7 | 18.4 | 144.1 → B, C, D 0 |

**Findings.**

1. **Enclosure decides the technology (Fig. 9).**
   - In humid heat, fans are most efficient above about 10 % openness.
   - In dry heat, C is most efficient on open platforms (≥ 76 % open) and B in more enclosed stations (≤ 52 %). Under the smart rule fans run only in the mornings and evenings (η 4–12) and never in the enclosed room.
2. **Enclosure without cooling makes the station hotter than outdoors.** At 15:00, screen doors add 1.2 °C (dry) and 1.9 °C (humid); the glazed enclosed room adds 4.9 °C and 7.0 °C. A sun-heated roof is a large part of this: replacing a well-insulated roof ($U$ = 0.3) with an uninsulated one ($U$ = 5.0) adds 1.6–2.1 °C at the screen-door station.
3. **The humidity limit, not efficiency, rules out evaporative cooling in enclosed stations.** ASHRAE 62.1-2022 Addendum e (§5.13.1) limits each HVAC zone to 65 % RH whenever evaporative cooling operates.
   - With screen doors or an enclosed room, B and C exceed it: peak RH 66–89 % in dry heat and 94–97 % in humid heat.
   - The air conditioner keeps the enclosed humid room at 50 % RH at 15:00 and clears very strong heat stress, so it is the admissible choice there even though B scores higher on $\eta$.
4. **At a 46 °C peak, only C comes close in open stations.** In the semi-open waiting area C removes all very strong heat stress while B leaves 99.5 person-h; on the windier open platform C leaves 52.7 and B 121.7.
5. **Cool the occupied zone, not the hall (Table 2b-4).** Low-level supply raises the air conditioner's $\eta$ by 36–49 % compared with mixing the whole volume (enclosed, hot-dry: 20.2 vs 14.5).
6. **Capacity and climate (Table 2b-5).**
   - In Phoenix heat, a screen-door station is too leaky for air conditioning: even 120 kW leaves 99.9 person-h. The enclosed room needs 120 kW.
   - In Houston, both the screen-door station and the enclosed room need 60 kW; 30 kW is not enough.

## 5.5 Validation and sensitivity

**Validation (Table 2b-0, 4 checks pass):**

1. **Nesting.** With the bus shelter's geometry and Section 4's assumptions, at the same measured wind, the station model reproduces the 2a volume-mode zone temperature (39.33 °C both).
2. **Time step.** $\eta$ with a 10-s step differs from a 2-s step by 1.4 %.
3. **AC efficiency.** COP 3.19 at the AHRI rating point, within the EER-implied 2.9–3.7.
4. **Sealed limit.** A nearly sealed room with ample capacity holds 26.0 °C.

**Sensitivity (Table 2b-6, screen-door station).** Each parameter was set to its low and high value:

- peak irradiance on glazing 200–600 W/m²;
- SHGC 0.25–0.6;
- door opening during dwell 0.3–0.8;
- wind exchange coefficient 0.15–0.5;
- thermal mass factor 1–6;
- street-side openness 0.1–0.4;
- roof $U$-value 0.3–5.0 W/m²K;
- radiant excess of the outdoor view 8–16 °C and of enclosed surfaces 2–8 °C.

In dry heat B is always the most efficient. In humid heat the fan is, except in the two lowest-exchange cases (wind coefficient 0.15, street-side openness 0.1), where B edges ahead; but there B drives the zone far above 65 % RH, so the admissible choice is still the fan or air conditioning. Exchange uncertainty moves the air conditioner's $\eta$ the most (3.4–11.0 in dry heat).

## 5.6 How the revision improved the model

The revised model answers questions the bus-stop model could not:

- **when** a station becomes hotter than the street;
- **which** technology fits a given degree of enclosure;
- **when** a building-code humidity limit overrides efficiency;
- **how much** capacity a station needs in each climate.

It contains the bus-stop model as its open-air limit, so one framework covers bus shelters, open platforms, screen-door stations and enclosed waiting rooms. Section 6 relies on that to scale up.

---

**Figures for this section:**

- `outputs/fig8_zone_timeseries.png`
- `outputs/fig9_eta_vs_openness.png`
- `outputs/fig10_train_dynamics.png`
- `outputs/fig11_2a_model_error.png`

**References (in addition to Section 4):**

- ANSI/ASHRAE Addendum e to ANSI/ASHRAE Standard 62.1-2022, §5.13 Direct Evaporatively Cooled Buildings.
- AHRI 210/240 and 390 rating conditions; 10 CFR 431.96.
- EnergyPlus Engineering Reference, "Air Exchange".
- ASHRAE Handbook—Fundamentals, sol-air temperature.
