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

**Geometry.** A waiting area 30 m long and 8 m deep; the occupied zone is 2.5 m high. Closed wall areas are glass with a solar heat gain coefficient (SHGC) of 0.4.

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
- Gains: $G = 75\,\text{W}\cdot N+\text{SHGC}\cdot A_{\text{glass}}\cdot I(t)\cdot 0.6+5\,\text{W/m}^2\cdot A+P_{\text{motors}}$.
- Each 10-s step uses the exact solution of the linear balance.

**Cooling systems**, each sized for 40 waiting passengers:

| System | Configuration | Power |
|---|---|---|
| A | 10 fans | 2.5 kW |
| B | 8 evaporative coolers, 40 m³/s | 9.6 kW |
| C | 5 large coolers, 37.5 m³/s | 12.5 kW |
| D | 60 kW air conditioner | COP varies with outdoor temperature |

- Evaporative coolers draw zone air.
- For the air conditioner, $\mathrm{COP} = 0.45\,T_e/(T_c - T_e)$, which gives 3.19 at 35 °C, consistent with AHRI-rated EER 10–12.5. It has a sensible heat ratio of 0.75 and a 26 °C thermostat.

**Comfort and relief.** Relief is measured against the same station without cooling, which can be hotter than outdoors.

## 5.3 What changed, why, and what it bought

The revisions are switched on one at a time (Table 2b-1). The platform-screen-door station shows the effects most clearly.

| Revision | Why it was necessary | Effect (platform screen doors) |
|---|---|---|
| **R0** Bus-stop model applied to the station | — | baseline |
| **R1** Heat gains: people, sun through glazing, lights, motors | Walls and roof trap heat | Uncooled zone at 15:00 rises from 45.9 to 46.9 °C (hot-dry) and from 37.0 to 38.5 °C (hot-humid). Hot-dry fan $\eta$ falls from −11.5 to −19.8. Hot-humid fans leave 61 person-h of very strong heat stress where R0 predicted none |
| **R2** Train-driven dynamics | Crowds peak just before a train; open doors flush the zone | $\eta$ falls 3–4 %; each arrival lifts zone air by 3–4 °C for a few minutes (Fig. 10) |
| **R3** Coolers recirculate zone air | Moisture added by evaporative cooling stays until ventilation removes it | Zone RH rises 7–14 points (hot-dry B: 26 → 40 %); $\eta$ changes by −3 % to +14 % |
| **R4** Air conditioning with outdoor-dependent COP and supply placement | Enclosure makes a vapour-compression system worth considering | Under the humidity limit, AC becomes the only admissible option in enclosed stations; low-level supply raises its $\eta$ by 36–50 % |

In the semi-open base case (58 % open), R0 and the full model agree: the uncooled zone is only 0.1–0.2 °C warmer, and B and C differ by under 6 %. Figure 11 maps this across openness:

- At 50 % open or more, the bus-stop model predicts evaporative-cooler efficiency within 10 %.
- At 3 % open, it underestimates evaporative cooling by 17–36 % and overestimates the humid-climate fan about three times (24.2 vs 7.5).

**The revision matters exactly where stations are enclosed.**

## 5.4 Results

**Table 2b-2. Efficiency $\eta$ (person·°C·h per kWh) by scenario.**

| Scenario | Climate | A fans | B evap | C large evap | D AC | UTCI ≥ 38 person-h: uncooled → with cooling |
|---|---|---|---|---|---|---|
| Open-sided platform | Hot-dry | −1.5 | 24.3 | **25.7** | 1.3 | 173.8 → C 0; B 96.4 |
| | Hot-humid | **19.3** | 7.8 | 8.6 | 0.9 | 60.3 → A 0 |
| Semi-open | Hot-dry | −4.3 | 24.8 | **26.1** | 1.2 | 173.2 → C 0; B 90.1 |
| | Hot-humid | **22.9** | 8.6 | 9.5 | 0.9 | 72.0 → A 0 |
| Screen doors | Hot-dry | −18.9 | **34.7** | 30.7 | 5.1 | 180.3 → B, C 0; D 151.3 |
| | Hot-humid | **20.7** | 12.1 | 11.6 | 3.9 | 92.0 → A 56.5; B, C, D 0 |
| Enclosed room | Hot-dry | −39.6 | **43.3** | 35.6 | 16.9 | 197.9 → B, C 0; D 102.3 |
| | Hot-humid | 7.5 | **16.5** | 14.3 | 13.9 | 128.2 → B, C, D 0 |

**Findings.**

1. **Enclosure decides the technology (Fig. 9).**
   - In humid heat, fans are most efficient above about 8 % openness.
   - In dry heat, C is most efficient on open platforms (≥ 76 % open) and B in more enclosed stations (≤ 52 %). Fans add heat at every openness.
2. **Enclosure without cooling makes the station hotter than outdoors.** At 15:00, screen doors add 0.9 °C (dry) and 1.4 °C (humid); the glazed enclosed room adds 3.8 °C and 5.6 °C.
3. **The humidity limit, not efficiency, rules out evaporative cooling in enclosed stations.** ASHRAE 62.1-2022 Addendum e (§5.13.1) limits each HVAC zone to 65 % RH whenever evaporative cooling operates.
   - With screen doors or an enclosed room, B and C exceed it: peak RH 66–89 % in dry heat and 94–97 % in humid heat.
   - The air conditioner keeps the enclosed humid room at 57 % RH at 15:00 and clears very strong heat stress, so it is the admissible choice there even though B scores higher on $\eta$.
4. **At a 46 °C peak, only C is enough for open stations.** On open and semi-open platforms B leaves 90–96 person-h of very strong heat stress; C removes all of it.
5. **Cool the occupied zone, not the hall (Table 2b-4).** Low-level supply raises the air conditioner's $\eta$ by 36–50 % compared with mixing the whole volume (enclosed, hot-dry: 16.9 vs 11.8).
6. **Capacity and climate (Table 2b-5).**
   - In Phoenix heat, a screen-door station is too leaky for air conditioning: even 120 kW leaves 123 person-h. The enclosed room needs 120 kW.
   - In Houston, 60 kW clears the screen-door station and 30 kW clears the enclosed room.

## 5.5 Validation and sensitivity

**Validation (Table 2b-0, 4 checks pass):**

1. **Nesting.** With the bus shelter's geometry and Section 4's assumptions, at the same measured wind, the station model reproduces the 2a volume-mode zone temperature (39.33 °C both).
2. **Time step.** $\eta$ with a 10-s step differs from a 2-s step by 1.7 %.
3. **AC efficiency.** COP 3.19 at the AHRI rating point, within the EER-implied 2.9–3.7.
4. **Sealed limit.** A nearly sealed room with ample capacity holds 26.0 °C.

**Sensitivity (Table 2b-6, screen-door station).** Each parameter was set to its low and high value:

- peak irradiance on glazing 200–600 W/m²;
- SHGC 0.25–0.6;
- door opening during dwell 0.3–0.8;
- wind exchange coefficient 0.15–0.5;
- thermal mass factor 1–6;
- street-side openness 0.1–0.4.

The most efficient system never changes: B in dry heat, fans in humid heat. Exchange uncertainty moves the air conditioner's $\eta$ the most (2.7–9.0 in dry heat).

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
