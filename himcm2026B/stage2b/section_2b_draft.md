# 5. Requirement 2b: Revising the Model for a Semi-Open Rail-Station Waiting Area

*Draft for the paper. Numbers come from `outputs/` (run `run_2b.py`).*

## 5.1 Why the bus-stop model is not enough

The efficiency measure of Section 4 stays the same: heat-stress relief delivered to people per kWh of electricity plus embedded water energy. What has to change is the model that predicts the relief.

The bus-stop model rests on four facts about an open shelter:

1. Without cooling, the air people stand in is outdoor air.
2. Conditions are steady over minutes.
3. Coolers draw outdoor air.
4. Only fans and evaporative coolers make sense.

A semi-open waiting area breaks all four. It has walls, glazing and a roof that trap heat. Passengers build up between trains and leave in a block. Coolers draw air that is already cooled and humidified. With enough enclosure, air conditioning becomes an option.

This is the freezer lesson of Section 3 in reverse. A closed design keeps cooling in, but it also keeps heat and moisture in.

## 5.2 The station model

**Geometry.** A waiting area 30 m long and 8 m deep; the occupied zone is 2.5 m high. Openness is set by the open fraction of each wall band. Closed areas are glass with a solar heat gain coefficient (SHGC) of 0.4.

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
- Passengers accumulate linearly and board when the train arrives, so the count is a sawtooth (Fig. 10). Dwell time is 40 s.

**Heat and moisture balance of the occupied zone:**

$$
C\frac{dT}{dt} = \rho c_p\big[Q_x(T_o - T) + Q_s(T_s - T)\big] + G - Q_{ac},
\qquad
M\frac{dW}{dt} = \rho\big[Q_x(W_o - W) + Q_s(W_s - W)\big] + \dot m_p - \dot m_{ac}
$$

- Exchange with outdoors: $Q_x = \sqrt{Q_{\text{wind}}^2 + Q_{\text{buoy}}^2}$, plus train gusts.
- Gains: $G = 75\,\text{W}\cdot N + \text{SHGC}\cdot A_{\text{glass}}\cdot I(t)\cdot 0.6 + 5\,\text{W/m}^2\cdot A + P_{\text{motors}}$.
- People add 45 W of latent heat each.
- Fast thermal mass is $C = 3\rho c_p V$.
- Each 10-s step uses the exact solution of the linear balance, so the scheme is stable for any step size.

**Cooling systems**, each sized for 40 waiting passengers:

| System | Configuration | Power |
|---|---|---|
| A | 10 fans | 2.5 kW |
| B | 8 evaporative coolers, 40 m³/s | 9.6 kW |
| C | 5 large coolers, 37.5 m³/s | 12.5 kW |
| D | 60 kW air conditioner | COP varies with outdoor temperature |

- Evaporative coolers draw zone air.
- For the air conditioner, $\mathrm{COP} = 0.45\,T_e/(T_c - T_e)$, with evaporator at 10 °C and condenser 15 K above outdoor air. That gives 3.19 at 35 °C, consistent with AHRI-rated EER 10–12.5 (COP 2.9–3.7).
- The air conditioner has a sensible heat ratio of 0.75 and a 26 °C thermostat that pulls the zone to the setpoint within capacity.

**Comfort and relief** follow Section 4. Relief is measured against the same station without cooling, which can be hotter than outdoors. People covered by fans or jets feel the jet; the rest feel zone air.

## 5.3 What changed, why, and what it bought

We switch the revisions on one at a time (Table 2b-1). The platform-screen-door station shows the effects most clearly.

| Revision | Why it was necessary | Effect (platform screen doors) |
|---|---|---|
| **R0** Bus-stop model applied to the station | — | baseline |
| **R1** Heat gains: people, sun through glazing, lights, motors | Walls and roof trap heat; air without cooling is no longer outdoor air | Uncooled zone at 15:00 rises from 43.0 to 45.0 °C (hot-dry) and from 36.0 to 38.0 °C (hot-humid). Hot-dry fan $\eta$ changes sign, +1.4 → −9.9. Hot-humid fans leave 54 person-h of very strong heat stress where R0 predicted none |
| **R2** Train-driven dynamics | Crowds peak just before a train; open doors flush the zone | $\eta$ falls 3–5 %; each arrival raises zone air by about 2 °C for a few minutes (Fig. 10) |
| **R3** Coolers recirculate zone air | Moisture added by evaporative cooling stays until ventilation removes it | Zone RH rises 7–23 points (hot-dry B: 34 → 57 %); $\eta$ changes by −6 % to +13 % |
| **R4** Air conditioning with outdoor-dependent COP and supply placement | Enclosure makes a vapour-compression system worth considering | Reveals the technology crossover and the value of low-level supply (+36–47 % $\eta$) |

In the semi-open base case (58 % open), the full model and R0 agree closely: the uncooled zone is only 0.2 °C warmer, and B and C differ by under 8 %. Figure 11 maps this across openness:

- At 50 % open or more, the bus-stop model predicts evaporative-cooler efficiency within 11 %.
- At 3 % open, it is 25–43 % too low.
- Below about 50 % open, it gets the sign of the fan's hot-dry efficiency wrong.

**The revision therefore matters exactly where stations are enclosed.**

## 5.4 Results

**Table 2b-2. Efficiency $\eta$ (person·°C·h per kWh) by scenario.**

| Scenario | Climate | A fans | B evap | C large evap | D AC | UTCI ≥ 38 person-h: uncooled → best |
|---|---|---|---|---|---|---|
| Open-sided platform | Hot-dry | 5.3 | **22.9** | 22.3 | 2.0 | 154.8 → 0 |
| | Hot-humid | **22.3** | 8.2 | 8.9 | 1.2 | 43.9 → 0 |
| Semi-open | Hot-dry | 1.1 | **23.2** | 22.4 | 2.0 | 153.4 → 0 |
| | Hot-humid | **23.1** | 8.6 | 9.3 | 1.2 | 53.9 → 0 |
| Screen doors | Hot-dry | −8.7 | **31.0** | 26.1 | 8.5 | 162.1 → 0 |
| | Hot-humid | **20.3** | 11.9 | 11.2 | 5.3 | 90.0 → 44.3 (A); 0 with B, C or D |
| Enclosed room | Hot-dry | −40.6 | **39.1** | 31.8 | 25.0 | 187.9 → 0 (B leaves the room at 80–87 % RH) |
| | Hot-humid | 0.4 | 16.9 | 14.1 | **20.4** | 142.2 → 0 |

**Findings.**

1. **Enclosure decides the technology (Fig. 9).**
   - In humid heat, fans are most efficient above about 8 % openness ($\eta$ 18–23 from 13 % up); in the enclosed room the air conditioner wins (20.4 vs 16.9 for B).
   - In dry heat, B is most efficient at every openness, from 22.9 to 39.1.
2. **Enclosure without cooling makes the station hotter than outdoors.**
   - Screen doors add 1.8 °C; the glazed enclosed room adds 7.2 °C (50.2 °C on the hot-dry day) from sun, people, lights and motors.
   - Fans in that room make heat stress worse ($\eta$ −40.6).
3. **Evaporative cooling and enclosure do not mix in humid air.** With 12 % openness or less, evaporative coolers drive zone RH to 69–96 %, above the 65 % limit ASHRAE 62.1 sets for mechanically cooled spaces. In enclosed stations this constraint, rather than $\eta$, rules out evaporative cooling and points to air conditioning.
4. **Cool the occupied zone, not the hall (Table 2b-4).** Low-level supply raises the air conditioner's $\eta$ by 36–47 % compared with mixing the whole volume (enclosed, hot-dry: 25.0 vs 18.0). This is the cold-air pool of the horizontal freezer case.
5. **Capacity matters for screen doors (Table 2b-5).**
   - The screen-door station needs about 120 kW of air conditioning to clear very strong heat stress on the hot-dry day (0.4 person-h left vs 106 with 60 kW), at a lower $\eta$ (7.2).
   - The enclosed room needs 60 kW.

## 5.5 Validation and sensitivity

**Validation (Table 2b-0, 4 checks pass):**

1. **Nesting.** Given the bus shelter's geometry and Section 4's assumptions, the station model reproduces the 2a volume-mode zone temperature exactly (34.72 °C both).
2. **Time step.** $\eta$ with a 10-s step differs by 1.8 % from a 2-s step.
3. **AC efficiency.** COP 3.19 at the AHRI rating point, within the EER-implied 2.9–3.7.
4. **Sealed limit.** A nearly sealed room with ample capacity holds 26.0 °C.

**Sensitivity (Table 2b-6, screen-door station).** Each parameter was set to its low and high value:

- peak irradiance on glazing 200–600 W/m²;
- SHGC 0.25–0.6;
- door opening during dwell 0.3–0.8;
- wind exchange coefficient 0.15–0.5;
- thermal mass factor 1–6;
- street-side openness 0.1–0.4.

The most efficient system never changes: B in dry heat, fans in humid heat. Exchange uncertainty (the wind coefficient and street-side openness) moves the air conditioner's $\eta$ the most, from 3.0 to 13.1.

## 5.6 How the revision improved the model

The revised model answers questions the bus-stop model could not:

- **when** a station becomes hotter than the street;
- **which** technology fits a given degree of enclosure;
- **whether** a humidity limit overrides efficiency;
- **how much** capacity a station needs.

It contains the bus-stop model as its open-air limit, so one framework now covers bus shelters, open platforms, screen-door stations and enclosed waiting rooms. Section 6 relies on that to scale up.

---

**Figures for this section:**

- `outputs/fig8_zone_timeseries.png`
- `outputs/fig9_eta_vs_openness.png`
- `outputs/fig10_train_dynamics.png`
- `outputs/fig11_2a_model_error.png`

**References (in addition to Section 4):**

- AHRI 210/240 rating conditions and EER; 10 CFR 431.96
- ASHRAE Standard 62.1, §5.9 (65 % RH limit)
- Platform screen door cooling savings reported for Seoul and Hong Kong (context for underground stations)
- EnergyPlus Engineering Reference, "Air Exchange"
