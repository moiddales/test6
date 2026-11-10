# 5. Requirement 2b: Revising the Model for a Semi-Open Rail-Station Waiting Area

*Draft for the paper. Numbers come from `outputs/` (run `run_2b.py`). Outdoor conditions are the measured hot design days of Section 4 (PHX peak 46.4 °C, IAH peak 37.4 °C).*

## 5.1 Why the bus-stop model is not enough

The efficiency measure of Section 4 stays the same: heat-stress relief delivered to people per kWh of electricity plus embedded water energy. What has to change is the model that predicts the relief.

The bus-stop model rests on four facts about an open shelter:

1. Without cooling, the air people stand in is outdoor air.
2. Conditions are steady over minutes.
3. Moisture added by a cooler is carried away at once.
4. Only fans and evaporative coolers make sense.

A semi-open waiting area breaks all four. It has walls, glazing and a roof that trap heat. Passengers build up between trains and leave in a block. Moisture from evaporative cooling stays until ventilation removes it. With enough enclosure, air conditioning becomes an option.

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

- Evaporative coolers are ducted to draw outdoor air. Free-standing units that recirculate zone air are evaluated as an alternative (Table 2b-7).
- For the air conditioner, $\mathrm{COP} = 0.45\,T_e/(T_c - T_e)$, which gives 3.19 at 35 °C, consistent with AHRI-rated EER 10–12.5. It has a sensible heat ratio of 0.75 (1.0 when the air is too dry to condense on the coil, as in Phoenix) and a 26 °C thermostat.
- Fans follow the smart rule of Section 4: each hour they run only if heat stress is at least strong and they lower it for the people they reach.

**Comfort and relief.** Mean radiant temperature is weighted by openness $f$: $T_{\text{mrt}} = f\,(T_o + 12) + (1-f)(T + 4)$. The open part of the view sees the outdoors, as under the bus-shelter roof; the enclosed part sees walls and roof that follow the zone air, so an air conditioner cools them too. Relief is measured against the same station without cooling, which can be hotter than outdoors.

## 5.3 What changed, why, and what it bought

R1 and R2 are switched on one at a time (Table 2b-1); R3 compares the two cooler intakes (Table 2b-7). The platform-screen-door station shows the effects most clearly.

| Revision | Why it was necessary | Effect (platform screen doors) |
|---|---|---|
| **R0** Bus-stop model applied to the station | — | baseline |
| **R1** Heat gains: people, sun through glazing and roof, lights, motors | Walls and roof trap heat | Uncooled zone at 15:00 rises from 45.9 to 47.3 °C (hot-dry) and from 37.0 to 39.0 °C (hot-humid). Hot-dry fan $\eta$ falls from 13.8 to 7.7. Hot-humid fans leave 80.5 person-h of very strong heat stress where R0 predicted 10.9 |
| **R2** Train-driven dynamics | Crowds peak just before a train; open doors flush the zone | Evaporative $\eta$ falls 3–4 %; each 40-s door opening lifts zone air by 2.8–3.3 °C (dry) or 1.0–1.2 °C (humid) for a few minutes (Fig. 10) |
| **R3** Zone moisture balance, with a choice of cooler intake (outdoor air or recirculated zone air) | Moisture added by evaporative cooling stays until ventilation removes it; the bus-stop model does not track it | Hot-dry zone RH at 15:00 with B: 25 % with outdoor intake, 39 % recirculating. Recirculation scores higher (40.1 vs 29.7) but breaks the 65 % humidity limit in enclosed stations |
| **R4** Air conditioning with outdoor-dependent COP and supply placement | Enclosure makes a vapour-compression system worth considering | AC is the only admissible cooling for an enclosed room in humid heat; low-level supply raises its $\eta$ by 36–49 % |

In the semi-open base case (58 % open), R0 and the full model agree closely: the uncooled zone is only 0.2–0.3 °C warmer, and B and C differ by under 2 %. Figure 11 maps this across openness:

- At 52 % open or more, the bus-stop model predicts evaporative-cooler efficiency within 6 %; at 37 % open, within 10 %.
- At 3 % open, it underestimates evaporative cooling by 26–58 % and overestimates the humid-climate fan about 1.7 times (22.8 vs 13.8).

**The revision matters exactly where stations are enclosed.**

## 5.4 Results

**Table 2b-2. Efficiency $\eta$ (person·°C·h per kWh) by scenario.**

| Scenario | Climate | A fans | B evap | C large evap | D AC | UTCI ≥ 38 person-h: uncooled → with cooling |
|---|---|---|---|---|---|---|
| Open-sided platform | Hot-dry | 11.5 | 20.4 | **24.4** | 1.4 | 195.3 → C 73.0; B 143.9 |
| | Hot-humid | **24.8** | 8.7 | 10.0 | 1.1 | 107.8 → A 69.2; B, C 0 |
| Semi-open | Hot-dry | 10.7 | 21.2 | **24.9** | 1.4 | 186.2 → C 0; B 120.0 |
| | Hot-humid | **26.1** | 9.3 | 10.8 | 1.2 | 104.7 → A 57.7; B, C 0 |
| Screen doors | Hot-dry | 8.3 | 29.7 | **30.0** | 6.4 | 186.8 → B 0.6; C 0; D 141.9 |
| | Hot-humid | **20.3** | 13.7 | 14.3 | 5.3 | 108.9 → A 75.9; B, C, D 0 |
| Enclosed room | Hot-dry | — (never on) | **41.9** | 38.6 | 20.2 | 206.2 → B, C 0; D 59.2 |
| | Hot-humid | 13.8 | **26.4** | 23.8 | 18.4 | 144.1 → B, C, D 0 |

Evaporative coolers draw outdoor air.

**Table 2b-7. Cooler intake in the two enclosed stations:** $\eta$ / peak zone RH / hours above 65 % RH.

| Scenario | Climate | Device | Outdoor-air intake | Recirculating zone air |
|---|---|---|---|---|
| Screen doors | Hot-dry | B | 29.7 / 46 % / 0 | 40.1 / 66 % / 0.2 |
| | | C | 30.0 / 62 % / 0 | 34.0 / 73 % / 4.3 |
| | Hot-humid | B | 13.7 / 91 % / 8.4 | 15.7 / 94 % / 15.6 |
| | | C | 14.3 / 94 % / 15.4 | 14.2 / 96 % / 16.0 |
| Enclosed room | Hot-dry | B | 41.9 / 50 % / 0 | 53.8 / 85 % / 12.5 |
| | | C | 38.6 / 71 % / 3.6 | 43.0 / 89 % / 15.5 |
| | Hot-humid | B | 26.4 / 91 % / 10.0 | 23.6 / 96 % / 16.0 |
| | | C | 23.8 / 95 % / 16.0 | 19.7 / 97 % / 16.0 |

**Comparing stations needs one baseline.** The $\eta$ values above measure each device against the same station without cooling, which answers "which device for this station". An enclosure changes how everyone waiting feels before any device is switched on, just as the wind screens did in Section 4, so comparing stations needs a common reference. Against the uncooled open-sided platform (person·°C·h per day):

| Station | Enclosure alone: dry / humid | Enclosure + device (dry: B; humid: fans, AC) |
|---|---|---|
| Open-sided platform | 0 / 0 | B 3,555; fans 994, AC 311 |
| Semi-open | +674 / +165 | B 4,377; fans 1,209, AC 501 |
| Screen doors | +1,049 / +65 | B 6,229; fans 879, AC 1,493 |
| Enclosed room | −589 / −1,738 | B 6,720; fans −1,357, AC 2,790 |

In dry heat partial enclosure helps on its own, because walls block wind hotter than skin and sun-heated outdoor surfaces; the fully enclosed room traps heat and is worse than the open platform. In humid heat the enclosed room is a heat trap: of the 4,528 the air conditioner relieves there, 1,738 only undoes what the enclosure added, leaving 2,790 for 245.5 kWh, against 994 for 40 kWh from fans on the open platform.

**Findings.**

1. **Enclosure decides the technology (Fig. 9).**
   - In humid heat, fans are most efficient above about 10 % openness.
   - In dry heat, evaporative cooling is most efficient at every openness: C from 22 % open upward (η 24–29), B at 8 % or less (35–42), and the two tie near 13 %. Under the smart rule fans run only in the mornings and evenings (η 4–12) and never in the enclosed room.
2. **Enclosure without cooling makes the station hotter than outdoors.** At 15:00, screen doors add 1.2 °C (dry) and 1.9 °C (humid); the glazed enclosed room adds 4.9 °C and 7.0 °C. A sun-heated roof is a large part of this: replacing a well-insulated roof ($U$ = 0.3) with an uninsulated one ($U$ = 5.0) adds 1.6–2.1 °C at the screen-door station.
3. **Whether an enclosed station can use evaporative cooling depends on the climate and on where the cooler takes its air (Table 2b-7).** ASHRAE 62.1-2022 Addendum e (§5.13.1) limits each HVAC zone to 65 % RH whenever evaporative cooling operates.
   - **Dry heat, outdoor-air intake: admissible, and far better than air conditioning.** B peaks at 37–50 % RH in all four stations. C peaks at 62 % with screen doors and 71 % in the enclosed room (3.6 h above the limit). With screen doors B scores $\eta$ = 29.7 and leaves 0.6 person-h of very strong heat stress; the 60 kW air conditioner scores 6.4 and leaves 141.9. In the enclosed room B scores 41.9 and leaves none; the air conditioner scores 20.2 and leaves 59.2.
   - **Dry heat, recirculating units: the more enclosed, the further over the limit.** Humidifying the same air again raises $\eta$ and more than halves water use (screen doors, B: 40.1; 4,753 L against 10,900 L), but B reaches 66 % RH with screen doors (0.2 h above the limit) and 85 % in the enclosed room (12.5 h); C reaches 73 % and 89 %. Coolers in an enclosed room must be ducted to outdoor air.
   - **Humid heat: no evaporative cooling in enclosed stations.** Houston's morning air is already above 65 % RH (3.4 h at the uncooled screen-door station, 2.0 h in the enclosed room). Coolers stretch that to 8.4–10.0 h (B) and 15.4–16.0 h (C). The admissible choices are fans or air conditioning: with screen doors the fans score 20.3 but leave 75.9 person-h of very strong heat stress, which the 60 kW air conditioner ($\eta$ = 5.3) clears; the enclosed room needs the air conditioner ($\eta$ = 18.4, 50 % RH at 15:00).
4. **At a 46 °C peak, only C comes close in open stations.** In the semi-open waiting area C removes all very strong heat stress while B leaves 120.0 person-h; on the windier open platform C leaves 73.0 and B 143.9.
5. **Cool the occupied zone, not the hall (Table 2b-4).** Low-level supply raises the air conditioner's $\eta$ by 36–49 % compared with mixing the whole volume (enclosed, hot-dry: 20.2 vs 14.5).
6. **Capacity and climate (Table 2b-5).**
   - In Phoenix heat, a screen-door station is too leaky for air conditioning: even 120 kW leaves 99.9 person-h. The enclosed room needs 120 kW.
   - In Houston, both the screen-door station and the enclosed room need 60 kW; 30 kW is not enough.

## 5.5 Validation and sensitivity

**Validation (Table 2b-0, 4 checks pass):**

1. **Nesting.** With the bus shelter's geometry and Section 4's assumptions, at the same measured wind, the station model reproduces the 2a volume-mode zone temperature (39.33 °C both). Its efficiency for that shelter is 25–48 % above Section 4's spot-mode values (Table 2b-8: dry B 49.8 vs 33.6), because it also counts the cooled zone air that everyone stands in and that the jet entrains; with the zone air left uncooled the two agree within 3–5 %. Section 4 is therefore the conservative lower bound.
2. **Time step.** $\eta$ with a 10-s step (14.3) differs from a 2-s step (14.5) by 1.4 %.
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

In dry heat an evaporative cooler is always the most efficient: B and C stay within 2 units of each other, C ahead in 15 of 18 cases and B in 3. B's peak RH is 43–48 %, always inside the limit; C's is 55–67 %, above 65 % only in the two lowest-exchange cases (wind coefficient 0.15, street-side openness 0.1). In humid heat the fan leads in 17 cases; at wind coefficient 0.15 B ties it (17.3 vs 17.2) but breaks the humidity limit. Exchange uncertainty moves the air conditioner's $\eta$ the most (3.4–11.0 in dry heat).

## 5.6 How the revision improved the model

The revised model answers questions the bus-stop model could not:

- **when** a station becomes hotter than the street;
- **which** technology fits a given degree of enclosure;
- **when** a humidity limit overrides efficiency, and how the cooler's intake decides it;
- **how much** capacity a station needs in each climate.

One framework now covers bus shelters, open platforms, screen-door stations and enclosed waiting rooms. Section 6 runs every venue, the bus shelter included, through this station model and compares them on the common baseline above.

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
