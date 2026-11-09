# 4. Requirement 2a: Cooling Efficiency of an Open-Sided Bus Shelter

*Draft for the paper. Every number comes from `outputs/` (run `run_stage2.py` and `sensitivity.py`). Data provenance: `../data/README.md`.*

## 4.1 From the freezer case to the bus stop

The problem table compares the three systems with numbers that measure different things. The fan "makes the space feel up to 3 °C cooler" by moving air. The evaporative coolers "lower air temperature up to 5 °C and 8 °C" and add moisture while doing so. Dividing those numbers by power gives 12, 4.2 and 3.2 °C/kW.

Section 3 showed why a ratio like that misleads, and gave three principles. We apply each one here:

| Principle from the freezer case | Applied to the bus stop |
|---|---|
| Count only cooling that reaches its target (87 % of a freezer's cooling never touches the product) | The numerator counts heat-stress relief **received by people** |
| A device's effect depends on the surrounding air | Efficiency is reported at two **rating conditions**, mapped over all temperatures and humidities (Fig. 3), and integrated over **measured hot days** |
| Efficiency = service ÷ all resources, within a stated boundary | The denominator is **electricity plus the energy embedded in the water used**. Escaping cooling goes to the street and is not recovered |

$$
\eta \;=\; \frac{N_{\text{ben}} \cdot R}{P + e_w \dot V_w}
\qquad \left[\frac{\text{person}\cdot{}^\circ\text{C}\cdot\text{h}}{\text{kWh}}\right]
$$

- $N_{\text{ben}}$: people the device reaches.
- $R$: heat-stress relief each person receives (Section 4.3).
- $P$: electric power.
- $\dot V_w$: water use. $e_w = 0.53$ kWh/m³, because the average US water supply system uses almost 2,000 kWh per million gallons (Hamilton et al., 2009).

**Rating conditions:**

- **R-dry:** 42 °C, 15 % RH, wind 1.5 m/s, 4.17 people waiting.
- **R-humid:** 35 °C, 55 % RH, same wind and occupancy.

**Design days.** For each hour of the day we average the hottest 10 % of July days in 2020–2024, using hourly observations from Phoenix Sky Harbor (PHX) and Houston Bush Intercontinental (IAH) airports (Iowa Environmental Mesonet ASOS archive).

| Station | High / low | Dew point | Pedestrian wind |
|---|---|---|---|
| PHX | 46.4 / 34.2 °C | 8 °C in the afternoon | 1.4–4.1 m/s |
| IAH | 37.4 / 27.0 °C | 21–25 °C | 1.1–3.6 m/s |

Wind is converted from 10 m to 1.1 m height with a log profile.

## 4.2 Assumptions

| # | Assumption | Justification |
|---|---|---|
| A1 | The shelter is 6 × 1.8 × 2.5 m, with a roof, a back panel and three open sides. | Standard city shelter; the problem says "open-sided". |
| A2 | The "up to" values are outlet ratings at a wet-bulb depression $D_{\text{ref}} = 10$ °C. | Gives effectiveness $\varepsilon$ = 0.50 (B) and 0.80 (C), inside the 0.5–0.9 range of direct evaporative coolers. |
| A3 | The fan's "3 °C" is a felt-temperature reduction at 30 °C / 50 % RH. | Fan ratings are quoted for warm conditions; varied 28–33 °C. |
| A4 | Airflow follows commercial data sheets: B 5.0 m³/s at 1.2 kW; C 7.5 m³/s at 2.5 kW. | 18,000 m³/h at 1.1 kW; 30,000 m³/h at 3.0 kW. |
| A5 | Passengers arrive at random; bus headways have a coefficient of variation of 0.5. | Sets the mean wait. |
| A6 | Devices do not change the radiant environment; the roof does. | Fans and coolers act on air. |

## 4.3 Sub-models

**M1 Moist air.**

$$
p_{ws}=611.2\,e^{17.62T/(243.12+T)},\qquad
W=0.622\,\frac{p_w}{p-p_w},\qquad
h=1.006T+W(2501+1.86T).
$$

The wet-bulb temperature solves the ASHRAE adiabatic-saturation equation.

**M2 Devices.**

- Evaporative coolers: $T_s=T-\varepsilon(T-T_{wb})$, with $W_s$ from constant enthalpy.
- Sensible cooling made: $\rho c_pQ_s(T-T_s)$. Water used: $\rho Q_s(W_s-W)$.
- The fan raises air speed at the person. Calibrated to its 3 °C rating, that speed is 2.93 m/s.
- Above skin temperature, UTCI's heat-balance model makes the fan add heat.

**M3 Delivery: the open-freezer problem.**

*Volume mode (cool the whole shelter):*

$$
T_z=\varphi T_s+(1-\varphi)T+\frac{Nq_p}{\rho c_p(Q_s+Q_{\text{inf}})},\qquad
\varphi=\frac{Q_s}{Q_s+Q_{\text{inf}}},
$$

$$
Q_{\text{inf}}=\sqrt{Q_{\text{wind}}^2+Q_{\text{buoy}}^2},\qquad
Q_{\text{buoy}}=\tfrac{C_d}{3}W_{\text{open}}\sqrt{gH_z^3\,\Delta T/T}.
$$

$Q_{\text{buoy}}$ is cool air spilling out of the bottom of the open sides.

*Spot mode (aim the jet at people):*

$$
T_p=T-\theta(T-T_s),\qquad \theta=\frac{\theta_0}{1+v_{\text{in}}/u_{\text{jet}}}.
$$

**M4 People.** Little's law gives $N=\lambda W$, with mean wait $W=\tfrac{h}{2}(1+CV^2)$. A device covers $Q/0.8$ people.

**M5 Felt temperature.** UTCI combines air temperature, humidity, wind and mean radiant temperature (MRT).

- In shade, MRT = air temperature + 4 °C.
- In sun, MRT = air temperature + 30 °C at solar noon. Mean radiant temperatures up to 75.6 °C (168 °F) were measured at noon over a sunlit concrete walkway in Tempe (ASU News, 2019).

**M6 Relief.**

$$
D(U)=\int_{26}^{U}w(u)\,du,\qquad w = 1, 2, 3, 4 \text{ on the UTCI bands from 26, 32, 38 and 46 °C},\qquad R=D(U_{\text{before}})-D(U_{\text{after}}).
$$

**Where the cooling goes** (spot mode), as shares of the sensible cooling made:

| Fate | Share |
|---|---|
| Reaches people | $(N_{\text{ben}}/\text{cap})\,\theta$ |
| Diluted on the way | $(N_{\text{ben}}/\text{cap})(1-\theta)$ |
| Aimed where nobody stands | $1-N_{\text{ben}}/\text{cap}$ |

## 4.4 Results

**Table 1. Efficiency at the rating conditions** (spot mode).

| Condition | Device | UTCI before → after | $R$ | $\eta$ | Water (L/h) |
|---|---|---|---|---|---|
| R-dry | A | 42.6 → 42.7 | −0.30 | **−4.8** | 0 |
| | B | 42.6 → 38.6 | 11.87 | **39.7** | 85 |
| | C | 42.6 → 35.1 | 19.61 | 31.3 | 205 |
| R-humid | A | 38.0 → 36.0 | 4.23 | **67.7** | 0 |
| | B | 38.0 → 36.0 | 4.05 | 13.9 | 33 |
| | C | 38.0 → 34.6 | 6.95 | 11.4 | 80 |

At 30 °C / 50 % the fan scores 46.7 against 7.9 (B) and 6.5 (C); at 32 °C / 75 %, 87.9 against 10.8 and 8.6.

**Table 2. Measured design days** (06:00–22:00; smart control: run only when UTCI ≥ 32, the device helps, and someone is waiting).

| Day | Device | Electricity (kWh) | Water (L) | Total resource (kWh) | Relief (person·°C·h) | $\eta_{\text{day}}$ | UTCI ≥ 38 person-h: before → after |
|---|---|---|---|---|---|---|---|
| Hot-dry (PHX) | A | 1.7 | 0 | 1.7 | 49 | 28.3 | 55.5 → 55.5 |
| | B | 18.8 | 1337 | 19.6 | 655 | **33.5** | 55.5 → 47.7 |
| | C | 39.2 | 3223 | 41.0 | 1203 | 29.4 | 55.5 → **33.6** |
| Hot-humid (IAH) | A | 3.4 | 0 | 3.4 | 190 | **55.5** | 20.3 → 4.5 |
| | B | 16.5 | 487 | 16.7 | 245 | 14.7 | 20.3 → 0 |
| | C | 34.3 | 1172 | 34.9 | 406 | 11.6 | 20.3 → 0 |

**Findings.**

1. **Climate decides the winner (Fig. 3).** The fan wins everywhere except hot, dry air. Evaporative cooling wins at 36 °C or more once the wet-bulb depression exceeds about 20 °C (at 36 °C), 16 °C (40 °C), 15 °C (42 °C) or 14 °C (44 °C).
2. **On a real Phoenix hot day the fan is harmful from 12:00 to 21:00.**
   - Always on, its daily efficiency is negative (−1.8).
   - Run only in the 7 hours when it helps, it scores 28.3. This is the bus stop's night cover: switching off is part of the design.
3. **B or C?** At the 46.4 °C peak, B and C are almost tied for up to 6 waiting people (55.7 vs 54.6 at 6). From 8 people C is clearly ahead (72.8 vs 58.0). Over 3,000 random parameter sets C leads in 64 % and B in 36 %.
4. **Efficiency and effectiveness diverge.** At the 46.4 °C peak no device brings waiting passengers below the very-strong band:
   - B reaches UTCI 42.9 and C 38.8;
   - over the day, C removes 40 % of very-strong heat-stress person-hours (55.5 → 33.6) and B removes 14 %.

   Requirement 4 must therefore combine devices with shade and refuges.
5. **Most cooling never reaches anyone (Fig. 7).**
   - B delivers 27 % of its cooling to people; 45 % is diluted by entrained hot air on the way and 28 % is aimed at empty space.
   - C delivers 20 %; 52 % is aimed at empty space.
6. **Aim at people.** Spot mode beats volume mode by 16 % to about 5 times.

**Design levers (Table 6).** As with the freezer's doors and covers, design beats machinery:

- **Shade.** Standing under the shelter roof instead of in the sun gives 896 person·°C·h of relief on the hot-dry day (more than device B's 655, three-quarters of C's 1,203) and 404 on the hot-humid day (equal to C, twice the fan), with zero energy.
- **Wind screens.** Screens that halve the wind inside the shelter raise every device's $\eta_{\text{day}}$ by 7–21 %.

## 4.5 Validation and sensitivity

**Validation (Table 0, 14 checks pass):**

- Wet bulb agrees with Stull (2011) within 0.5 °C; energy closure is within 3 %.
- The fan reproduces its 3 °C rating.
- **The fan's predicted effect has the right sign at three conditions tested on people at rest:**

  | Condition | Measured | Model ΔUTCI |
  |---|---|---|
  | 40 °C / 50 % | fans helped (Morris et al., 2019) | +1.38 |
  | 47 °C / 10 % | fans harmed (Morris et al., 2019) | −1.39 |
  | 42 °C / 50 % | fans helped (Ravanelli et al., 2015) | +1.17 |

  A study of physical work capacity (Foster et al., 2022) found fans unhelpful above 35 °C when RH is below 50 %. That is stricter than our model for people at rest, and it argues for switching fans off earlier for anyone exerting themselves.
- The mixing model has correct limits.

**One-at-a-time sensitivity (Fig. 5, design-day peaks):**

- The heat-stress weights scale $\eta$ by 4.6–12 times. They never change the fan-versus-evaporative ranking, but they can swap B and C, which are nearly tied at the dry peak.
- Next come the fan's rating reference temperature, crowd size, the jet share $\theta_0$ (B: 25.2–49.2) and $D_{\text{ref}}$ (B: 28.0–46.9).
- Water energy from 0 to 2.64 kWh/m³ (five times the US average, the top of California's range) lowers C's dry-peak $\eta$ from 39.9 to 31.8 (−20 %).

**Monte Carlo (Fig. 6, 3,000 draws):**

- The fan is most efficient at the humid peak in 97.9 % of draws.
- At the dry peak C leads in 64 % and B in 36 %, and the fan's $\eta$ is negative in every draw.

## 4.6 Answer to Requirement 2a

- **Humid or moderately hot weather:** the fan (A). It delivers 3–10 times more relief per kWh than either cooler and uses no water.
- **Hot, dry weather** (≥ 36 °C and a wet-bulb depression of about 14–20 °C or more): evaporative cooling, with the fan switched off. B and C are nearly equal at quiet stops; use C at busy stops, where it is also the more effective.
- **On the hottest dry days** no single device keeps waiting passengers out of very strong heat stress. Shade, which costs no energy, comes first.

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

- Ravanelli, N. M., Hodder, S. G., Havenith, G., Jay, O. (2015). Heart rate and body temperature responses to extreme heat and humidity with and without electric fans. *JAMA* 313(7):724–725.
- Foster, J., Smallcombe, J. W., Hodder, S., Jay, O., Flouris, A. D., Havenith, G. (2022). Quantifying the impact of heat on human physical work capacity; part II. *Int J Biometeorol* 66(3):507–520 (citing Morris et al., 2019).
- Bröde, P., et al. (2012). Deriving the operational procedure for the Universal Thermal Climate Index (UTCI). *Int J Biometeorol* 56(3):481–494.
- Hamilton, G., Arzbaecher, C., Ehrhard, R., Murphy, J. (2009). Driving energy efficiency in the U.S. water & wastewater industry. ACEEE Summer Study on Energy Efficiency in Industry.
- Seckel, S. (2019). Devilishly hot. ASU News (MRT measurements by A. Middel and E. S. Krayenhoff).
- Iowa Environmental Mesonet, ASOS archive (PHX, IAH, 2020–2024).
- Tartarini & Schiavon (2020), pythermalcomfort.
- Stull (2011), wet-bulb formula.
- ASHRAE Handbook—Fundamentals, Ch. 1.
- EnergyPlus Engineering Reference, "Air Exchange".
- Manufacturer data sheets (Jinghui JH18AP; Puravent EC30-VS).
