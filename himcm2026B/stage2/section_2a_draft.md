# 4. Requirement 2a: Cooling Efficiency of an Open-Sided Bus Shelter

*Draft for the paper. Every number comes from `outputs/` (run `run_stage2.py` and `sensitivity.py`).*

## 4.1 From the freezer case to the bus stop

The problem table compares the three systems with numbers that measure different things. The fan "makes the space feel up to 3 °C cooler" by moving air. The evaporative coolers "lower air temperature up to 5 °C and 8 °C" and add moisture while doing so. Dividing those numbers by power gives 12, 4.2 and 3.2 °C/kW.

Section 3 showed why a ratio like that misleads, and gave three principles. We apply each one here:

| Principle from the freezer case | Applied to the bus stop |
|---|---|
| Count only cooling that reaches its target (87 % of a freezer's cooling never touches the product) | The numerator counts heat-stress relief **received by people** |
| A device's effect depends on the surrounding air (the same case uses 1.5× more energy in humid store air) | Efficiency is reported at two **rating conditions** and mapped over all temperatures and humidities (Fig. 3) |
| Efficiency = service ÷ all resources, within a stated boundary | The denominator is **electricity plus the energy embedded in the water used**. Cooling that escapes goes to the street: unlike a store, nothing recovers it |

$$
\eta \;=\; \frac{N_{\text{ben}} \cdot R}{P + e_w \dot V_w}
\qquad \left[\frac{\text{person}\cdot{}^\circ\text{C}\cdot\text{h}}{\text{kWh}}\right]
$$

- $N_{\text{ben}}$: people the device reaches.
- $R$: heat-stress relief each person receives (Section 4.6).
- $P$: electric power.
- $\dot V_w$: water use; $e_w = 0.48$ kWh/m³ is the US average energy intensity of public water supply.

**Rating conditions.** Like the climate classes of display-case test standards:

- **R-dry:** 42 °C, 15 % RH, wind 1.5 m/s, 4.17 people waiting.
- **R-humid:** 35 °C, 55 % RH, same wind and occupancy.

## 4.2 Assumptions

| # | Assumption | Justification |
|---|---|---|
| A1 | The shelter is 6 × 1.8 × 2.5 m, with a roof, a back panel and three open sides. | Standard city shelter; the problem says "open-sided". |
| A2 | The "up to" values are outlet ratings at a reference wet-bulb depression $D_{\text{ref}} = 10$ °C. | Gives effectiveness $\varepsilon$ = 0.50 (B) and 0.80 (C), inside the 0.5–0.9 range of direct evaporative coolers. |
| A3 | The fan's "3 °C" is a felt-temperature reduction at 30 °C / 50 % RH. | Fan ratings are quoted for warm conditions; the reference is varied from 28 to 33 °C. |
| A4 | Airflow follows commercial data sheets: B 5.0 m³/s at 1.2 kW; C 7.5 m³/s at 2.5 kW. | 18,000 m³/h at 1.1 kW; 25,000 m³/h at 2.2 kW; 30,000 m³/h at 3.0 kW. |
| A5 | Passengers arrive at random; bus headways have a coefficient of variation of 0.5. | Sets the mean wait. |
| A6 | Devices do not change the radiant environment; the roof does. | Fans and coolers act on air. |

## 4.3 Sub-models

**M1 Moist air.**

$$
p_{ws} = 611.2\,e^{17.62T/(243.12+T)},\qquad
W = 0.622\,\frac{p_w}{p - p_w},\qquad
h = 1.006\,T + W(2501 + 1.86\,T).
$$

The wet-bulb temperature solves the ASHRAE adiabatic-saturation equation.

**M2 Devices.**

- Evaporative coolers: $T_s = T - \varepsilon(T - T_{wb})$, with $W_s$ from constant enthalpy.
- Sensible cooling made: $\rho c_p Q_s (T - T_s)$. Water used: $\rho Q_s (W_s - W)$.
- The fan raises air speed at the person. Calibrated to its 3 °C rating, that speed is 2.93 m/s.
- Above skin temperature, UTCI's heat-balance model makes the fan add heat. At 20 % RH the break-even is 41.6 °C. Physiological studies place it near 42 °C for older adults and 45 °C for young adults.

**M3 Delivery: the open-freezer problem.**

*Volume mode (cool the whole shelter):*

$$
T_z = \varphi T_s + (1-\varphi)T + \frac{N q_p}{\rho c_p(Q_s+Q_{\text{inf}})},\qquad
\varphi=\frac{Q_s}{Q_s+Q_{\text{inf}}}.
$$

$$
Q_{\text{inf}}=\sqrt{Q_{\text{wind}}^2+Q_{\text{buoy}}^2},\qquad
Q_{\text{buoy}}=\tfrac{C_d}{3}W_{\text{open}}\sqrt{gH_z^3\,\Delta T/T}.
$$

$Q_{\text{buoy}}$ is cool air spilling out of the bottom of the open sides, the mechanism that dominates an open vertical freezer.

*Spot mode (aim the jet at people):*

$$
T_p = T - \theta(T - T_s),\qquad \theta = \frac{\theta_0}{1 + v_{\text{in}}/u_{\text{jet}}}.
$$

**M4 People.** Little's law gives $N = \lambda W$, with mean wait $W = \tfrac{h}{2}(1 + CV^2)$; that is 4.17 people for 40 passengers/h and a 10-min headway. A device covers $Q/0.8$ people.

**M5 Felt temperature.** UTCI combines air temperature, humidity, wind and mean radiant temperature (MRT). In shade MRT = air temperature + 4 °C; in sun MRT = air temperature + 30 °C at solar noon. Measurements in Tempe recorded MRT up to 76 °C over sunlit concrete.

**M6 Relief.**

$$
D(U)=\int_{26}^{U}w(u)\,du,\qquad w = 1, 2, 3, 4 \text{ on the UTCI bands from 26, 32, 38 and 46 °C},\qquad R = D(U_{\text{before}})-D(U_{\text{after}}).
$$

**Where the cooling goes** (spot mode), as shares of the sensible cooling made:

| Fate | Share |
|---|---|
| Reaches people | $(N_{\text{ben}}/\text{cap})\,\theta$ |
| Diluted by entrained hot air on the way | $(N_{\text{ben}}/\text{cap})(1-\theta)$ |
| Aimed where nobody stands | $1 - N_{\text{ben}}/\text{cap}$ |

## 4.4 Results

**Table 1. Efficiency at the rating conditions** (spot mode).

| Condition | Device | UTCI before → after | $R$ | $\eta$ | Water (L/h) |
|---|---|---|---|---|---|
| R-dry | A | 42.6 → 42.7 | −0.30 | **−4.8** | 0 |
| | B | 42.6 → 38.6 | 11.87 | **39.9** | 85 |
| | C | 42.6 → 35.1 | 19.61 | 31.4 | 205 |
| R-humid | A | 38.0 → 36.0 | 4.23 | **67.7** | 0 |
| | B | 38.0 → 36.0 | 4.05 | 13.9 | 33 |
| | C | 38.0 → 34.6 | 6.95 | 11.4 | 80 |

At 30 °C / 50 % the fan scores 46.7 against 7.9 (B) and 6.5 (C); at 32 °C / 75 %, 87.9 against 10.8 and 8.6.

**Findings.**

1. **Climate decides the winner (Fig. 3).** The fan wins everywhere except hot, dry air. Evaporative cooling wins when air is at least 36 °C and the wet-bulb depression exceeds a threshold that falls as temperature rises: about 20 °C at 36 °C, 16 °C at 40 °C, 15 °C at 42 °C and 14 °C at 44 °C (Table 5).
2. **The fan can make things worse.** On the hot-dry design day it adds heat from 13:00 to 17:00.
3. **Crowd size decides between B and C.** At the hot-dry peak B is more efficient up to 6 people (56.5 vs 47.9). C is more efficient from 8 people (63.9 vs 58.9), because it covers 9.4 people and B covers 6.25.
4. **Most cooling never reaches anyone (Fig. 7).** Over the design day:
   - B delivers 34 % of its cooling to people; 38 % is diluted on the way and 28 % is aimed at empty space.
   - C delivers 24 %; 52 % of its larger airflow is aimed at empty space.
   - This is the bus stop's version of the freezer's 87 % lost through the opening.
5. **Aim at people.** Spot mode beats volume mode by 16 % to about 5 times.
6. **Water is a real cost in dry heat.** B uses 85 L/h and C 205 L/h at R-dry. Data-sheet figures of 15–20 L/h correspond, by the energy balance, to only about 2 °C of cooling.

**Table 2. Design days** (06:00–22:00; smart control: run only when UTCI ≥ 32, the device helps, and someone is waiting).

| Day | Device | Electricity (kWh) | Water (L) | Total resource (kWh) | Relief (person·°C·h) | $\eta_{\text{day}}$ | UTCI ≥ 38 person-h: before → after |
|---|---|---|---|---|---|---|---|
| Hot-dry | A | 2.9 | 0 | 2.9 | 79 | 26.9 | 52.3 → 45.3 |
| | B | 18.8 | 1170 | 19.4 | 685 | **35.3** | 52.3 → 28.1 |
| | C | 39.2 | 2820 | 40.6 | 1127 | 27.8 | 52.3 → **0** |
| Hot-humid | A | 3.4 | 0 | 3.4 | 227 | **66.3** | 18.0 → 2.2 |
| | B | 16.5 | 457 | 16.7 | 256 | 15.4 | 18.0 → 0 |
| | C | 34.3 | 1099 | 34.8 | 424 | 12.2 | 18.0 → 0 |

Smart control raises the fan's hot-dry efficiency from 17.7 (always on) to 26.9 by switching it off when it adds heat. It is the bus stop's night cover.

**Design levers (Table 6).** The freezer case showed that doors, covers and geometry beat the refrigeration machinery. The same holds at the bus stop:

- **Shade.** Standing under the shelter roof instead of in the sun gives 801 person·°C·h of relief on the hot-dry day and 529 on the hot-humid day, with zero energy. That is more than device B delivers all day (685).
- **Wind screens.** Side screens that halve wind inside the shelter raise every device's $\eta_{\text{day}}$ by 2–6 %.

## 4.5 Validation and sensitivity

**Validation (Table 0, 12 checks pass):**

- Wet bulb agrees with Stull (2011) within 0.5 °C.
- Energy closure within 3 %.
- The fan reproduces its 3 °C rating.
- The fan's dry-air break-even matches physiological evidence for older adults.
- The mixing model has correct limits.

**One-at-a-time sensitivity (Fig. 5):**

- The heat-stress weights scale $\eta$ by 3.6–9 times and leave the ranking unchanged.
- Next come the fan's rating reference temperature, crowd size, the jet share $\theta_0$ and $D_{\text{ref}}$.
- Water energy intensity from 0.07 to 3.0 kWh/m³ lowers C's peak $\eta$ from 34.4 to 27.8 (−17 %), which matters where water is pumped long distances.

**Monte Carlo (Fig. 6, 3,000 draws):**

- The fan is most efficient at the hot-humid peak in 99.7 % of draws.
- At the hot-dry peak B leads in 51 % and C in 49 %, and the fan has $\eta < 0$ in 86 %.

## 4.6 Answer to Requirement 2a

- **Humid or moderately hot weather:** the fan (A). It delivers 4–10 times more relief per kWh than either cooler and uses no water.
- **Hot, dry weather** (≥ 36 °C and a wet-bulb depression of about 14–20 °C or more): evaporative cooling. Use B at quiet stops (≤ 6 waiting) and C at busy stops. Only C keeps waiting passengers out of very strong heat stress at a 43 °C peak.
- **Always:**
  - shade the stop first;
  - aim the air at the waiting area;
  - switch devices off when nobody is waiting or when the fan would add heat.

---

**Figures for this section:**

- `outputs/fig1_climate_dependence.png`
- `outputs/fig2_dilution_vs_wind.png`
- `outputs/fig3_winner_map.png`
- `outputs/fig4_design_days.png`
- `outputs/fig5_tornado.png`
- `outputs/fig6_monte_carlo.png`
- `outputs/fig7_cooling_fate.png`

**References:**

- Bröde et al. (2012) *Int J Biometeorol* 56:481–494
- Ravanelli et al. (2015) *JAMA* 313:724–725
- Tartarini & Schiavon (2020) *SoftwareX* 12:100578
- Stull (2011) *J Appl Meteor Climatol* 50:2267–2269
- ASHRAE Handbook—Fundamentals, Ch. 1
- EnergyPlus Engineering Reference, "Air Exchange"
- ACEEE (2009), energy intensity of US water supply
- Middel & Krayenhoff (2019), Tempe MRT measurements, via ASU News
- NWS 1991–2020 climate normals
- Manufacturer data sheets (Jinghui JH18AP; Puravent EC30-VS)
