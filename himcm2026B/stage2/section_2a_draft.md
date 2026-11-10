# 4. Requirement 2a: Cooling Efficiency of an Open-Sided Bus Shelter

*Draft for the paper. Every number comes from `outputs/` (run `run_stage2.py` and `sensitivity.py`). Data provenance: `../data/README.md`.*

## 4.1 From the freezer case to the bus stop

The problem table compares the three systems with numbers that measure different things. The fan "makes the space feel up to 3 °C cooler" by moving air. The evaporative coolers "lower air temperature up to 5 °C and 8 °C" and add moisture while doing so. Dividing those numbers by power gives 12, 4.2 and 3.2 °C/kW.

Section 3 showed why a ratio like that misleads, and gave three principles. We apply each one here:

| Principle from the freezer case | Applied to the bus stop |
|---|---|
| Count only cooling that reaches its target (88 % of a freezer's cooling load is caused by its opening) | The numerator counts heat-stress relief **received by people** |
| A device's effect depends on the surrounding air | Efficiency is reported at two **rating conditions**, mapped over all temperatures and humidities (Fig. 3), and integrated over **measured hot days** |
| Efficiency = service ÷ all resources, within a stated boundary | The denominator is **electricity plus the energy embedded in the water used**. Escaping cooling goes to the street and is not recovered |

$$
\eta \;=\; \frac{N_{\text{ben}} \cdot R}{P + e_w \dot V_w}
\qquad \left[\frac{\text{person}\cdot{}^\circ\text{C}\cdot\text{h}}{\text{kWh}}\right]
$$

- $N_{\text{ben}}$: people the device reaches.
- $R$: heat-stress relief each person receives (Section 4.3).
- $P$: electric power.
- $\dot V_w$: water use. $e_w$ is the energy embedded in each cubic metre of water, set by city. The average US water supply system uses almost 2,000 kWh per million gallons, 0.53 kWh/m³ (Hamilton et al., 2009); we use it for Houston and the rating conditions. Phoenix water is pumped up to 2,900 ft by the Central Arizona Project (5.5 kWh per 1,000 gallons) before city supply (about 1.8 kWh per 1,000 gallons; WRRC *Arroyo*, 2010), so $e_w$ = 1.93 kWh/m³ there.

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
| A5 | Passengers arrive at random; bus headways have a coefficient of variation of 0.5. | Sets the mean wait. Arrivals are close to random for headways up to about 12 minutes (Kaparias et al., 2015). |
| A6 | Devices do not change the radiant environment; the roof does. | Fans and coolers act on air. |
| A7 | Under the roof, MRT is 12 °C above air temperature. | Sun raises MRT about 28 °C above air temperature in Tempe (Middel & Krayenhoff, 2019); bus shelters remove only about 15 °C of that, less than building or tree shade (Middel et al., 2021; Tucson MaRTy survey). Varied 8–16 °C. |

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
- The fan raises air speed at the person. Calibrated to its 3 °C rating, that speed is 2.74 m/s.
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

**M4 People.** Little's law gives the mean number waiting, $\bar N=\lambda W$, with mean wait $W=\tfrac{h}{2}(1+CV^2)$. A device can cover at most $\text{cap}=Q/0.8$ people. The number waiting varies at random (Poisson), so the people a device reaches are $N_{\text{ben}}=E[\min(N,\text{cap})]$. Using $\min(\bar N,\text{cap})$ instead would overstate the fan's reach by 15 %, because whenever more people wait than it covers, the extra people get nothing.

**M5 Felt temperature.** UTCI combines air temperature, humidity, wind and mean radiant temperature (MRT).

- Under the shelter roof, MRT = air temperature + 12 °C (A7).
- In sun, MRT = air temperature + 30 °C at solar noon. In Tempe, MRT reached 76.4 °C at an air temperature of 48.5 °C (Middel & Krayenhoff, 2019).

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
| R-dry | A | 44.5 → 44.3 | 0.41 | 5.4 | 0 |
| | B | 44.5 → 40.5 | 11.92 | **38.0** | 85 |
| | C | 44.5 → 36.9 | 21.48 | 34.2 | 205 |
| R-humid | A | 39.9 → 37.7 | 6.33 | **83.3** | 0 |
| | B | 39.9 → 37.8 | 6.16 | 20.1 | 33 |
| | C | 39.9 → 36.3 | 9.16 | 15.0 | 80 |

At 30 °C / 50 % the fan scores 55.9 against 12.1 (B) and 8.8 (C); at 32 °C / 75 %, 79.2 against 12.5 and 9.8.

**Table 2. Measured design days** (06:00–22:00; smart control: run only when UTCI ≥ 32, the device helps, and someone is waiting).

| Day | Device | Electricity (kWh) | Water (L) | Total resource (kWh) | Relief (person·°C·h) | $\eta_{\text{day}}$ | UTCI ≥ 38 person-h: before → after |
|---|---|---|---|---|---|---|---|
| Hot-dry (PHX) | A | 2.2 | 0 | 2.2 | 59 | 26.6 | 61.7 → 61.7 |
| | B | 18.8 | 1337 | 21.4 | 672 | **31.4** | 61.7 → 52.7 |
| | C | 39.2 | 3223 | 45.5 | 1311 | 28.8 | 61.7 → **40.8** |
| Hot-humid (IAH) | A | 3.9 | 0 | 3.9 | 242 | **61.5** | 34.4 → 24.2 |
| | B | 18.8 | 504 | 19.1 | 312 | 16.3 | 34.4 → 12.6 |
| | C | 39.2 | 1212 | 39.9 | 530 | 13.3 | 34.4 → **0.5** |

**Findings.**

1. **Climate decides the winner (Fig. 3).** The fan wins everywhere except hot, dry air. Evaporative cooling wins at 36 °C or more once the wet-bulb depression exceeds about 19 °C (at 36 °C), 16 °C (40 °C), 15 °C (42 °C) or 14 °C (44 °C).
2. **On a real Phoenix hot day the fan is harmful from 13:00 to 20:00.**
   - Always on, its daily efficiency is only 8.8.
   - Run only in the 9 hours when it helps, it scores 26.6. This is the bus stop's night cover: switching off is part of the design.
3. **B or C?** At the 46.4 °C peak (measured wind 3.7 m/s), B is slightly ahead or level for up to 6 waiting people (42.9 vs 42.1 at 6). From 8 people C is clearly ahead (53.1 vs 48.7). Over 3,000 random parameter sets C leads in 61 % and B in 39 %.
4. **Efficiency and effectiveness diverge.**
   - At the 46.4 °C peak no device brings waiting passengers below the very-strong band: B reaches UTCI 46.1 and C 42.9. Over the day, C removes 34 % of very-strong heat-stress person-hours (61.7 → 40.8) and B removes 15 %.
   - On the humid day the most efficient device is the least protective: the fan leaves 24.2 of 34.4 very-strong person-hours, while C leaves 0.5.

   Requirement 4 must therefore combine devices with shade and refuges.
5. **Most cooling never reaches anyone (Fig. 7).**
   - B delivers 24–26 % of its cooling to people; 40–41 % is diluted by entrained hot air on the way and 34 % is aimed at empty space.
   - C delivers 20–21 %; 52–53 % is aimed at empty space.
6. **Aim at people.** Spot mode beats volume mode by 19 % to about 3.7 times.

**Design levers (Table 6).** All relief figures share one baseline: an open shelter with no device. This matters because a lever such as a wind screen changes the felt temperature of everyone waiting, not only of those a device reaches.

| Lever (relief in person·°C·h per day) | Hot-dry | Hot-humid |
|---|---|---|
| Shelter roof (shade vs full sun), 0 kWh | 638 | 208 |
| Side wind screens alone, 0 kWh | +57 | −87 |
| Screens + fan (fan alone) | 102 (59) | 200.5 (242) |
| Screens + B (B alone) | 817 (672) | 284 (312) |
| Screens + C (C alone) | 1,539 (1,311) | 536 (530) |

- **Shade.** Standing under the shelter roof instead of in the sun gives 638 person·°C·h of relief on the hot-dry day (close to device B's 672, half of C's 1,311) and 208 on the hot-humid day (86 % of the fan's 242), with zero energy.
- **Wind screens help only in dry heat.** Above skin temperature, wind heats people, so halving it helps everyone waiting (+57) and every device does more. In humid heat, wind helps people shed heat by sweating, so screens make everyone hotter (−87); they cancel more than the fan or B adds. Humid-climate shelters should stay open to the breeze.

## 4.5 Validation and sensitivity

**Validation (Table 0, 14 checks pass):**

- Wet bulb agrees with Stull (2011) within 0.5 °C; energy closure is within 3 %.
- The fan reproduces its 3 °C rating.
- **The fan's predicted effect has the right sign at three conditions tested on people at rest:**

  | Condition | Measured | Model ΔUTCI |
  |---|---|---|
  | 40 °C / 50 % | fans helped (Morris et al., 2019) | +1.6 |
  | 47 °C / 10 % | fans harmed (Morris et al., 2019) | −1.0 |
  | 42 °C / 50 % | fans helped (Ravanelli et al., 2015) | +1.4 |

  The evidence above skin temperature is contested, so we compare the model's help-or-harm boundary with three further studies (Table 7):

  | Study | Finding | Model |
  |---|---|---|
  | Morris et al. (2021), biophysical model | Fans never harmful below 39 °C (young), 38 °C (older), 37 °C (older on anticholinergic drugs) at any humidity | Fan harms from 38.6 °C at 5 % RH: consistent |
  | Bröde & Kampmann (2023), 198 walking trials | Above 35 °C, wind helps only above 2 kPa (heart rate, core temperature) or 3 kPa (skin temperature, sweat) vapour pressure; UTCI tracks the measured wind effects (r = 0.9) | Fan helps above 0.74 kPa at 40 °C and 2.16 kPa at 44 °C: more favourable to fans than these trials of people walking |
  | Meade et al. (2024), critical review | Above 35 °C fans do not lower core temperature meaningfully | Most pessimistic reading, tested below |

  Under the Meade et al. reading (no fan benefit above 35 °C), the Houston fan runs 10 hours instead of 16, its relief falls from 242 to 145 person·°C·h and 31.2 instead of 24.2 very-strong person-hours remain. The fan is still the most efficient device ($\eta_{\text{day}}$ 59.5), but the hottest hours then need evaporative cooling or a cooled refuge. For older passengers we recommend this cautious reading.
- **Order-of-magnitude checks.** Read as "air-temperature drop delivered at the hottest dry hour", the ratings imply saturation effectiveness 0.44 (B) and 0.65 (C), close to the 0.50 and 0.80 of A2. At the dry peak the model lowers air temperature at a covered person by 3.8 °C (B) and 7.1 °C (C), under a third of the 24 °C wet-bulb depression; field tests of outdoor misting report 8.2 °C in a light breeze (Ulpiani et al., 2019).
- The mixing model has correct limits.

**One-at-a-time sensitivity (Fig. 5, design-day peaks):**

- Wind and water energy start from each city's measured or local value (Phoenix peak wind 3.7 m/s, Houston 2.2 m/s).
- The heat-stress weights change $\eta$ by a factor of 7–27 between equal weights (1-1-1-1) and the steepest scheme (1-3-9-27). They never change the fan-versus-evaporative ranking, but they can swap B and C, which are close at the dry peak. Mortality data support weights that rise with the band: in eight Polish cities the relative risk of death rose 10–20 % above UTCI 32 °C and 25–30 % above 38 °C (Kuchcik, 2021).
- Next come crowd size (C at the dry peak: 14.3–64.3), wind and the fan's rating reference temperature, the jet share $\theta_0$ (B: 22.7–39.5) and $D_{\text{ref}}$ (B: 25.5–37.5).
- Water energy from 0 to 2.64 kWh/m³ (five times the US average, the top of California's range) lowers C's dry-peak $\eta$ from 35.4 to 28.2 (−20 %).

**Monte Carlo (Fig. 6, 3,000 draws):**

- The fan is most efficient at the humid peak in 93.2 % of draws.
- At the dry peak C leads in 61 % and B in 39 %, and the fan's $\eta$ is negative in every draw.

## 4.6 Answer to Requirement 2a

- **Humid or moderately hot weather:** the fan (A). It delivers about 4–8 times more relief per kWh than either cooler and uses no water. Above 35 °C its benefit is contested (Table 7), so the hottest humid hours also need evaporative cooling or a cooled refuge, especially for older passengers.
- **Hot, dry weather** (≥ 36 °C and a wet-bulb depression of about 14–19 °C or more): evaporative cooling, with the fan switched off. B and C are close at quiet stops; use C at busy stops, where it is also the more effective.
- **On the hottest dry days** no single device keeps waiting passengers out of very strong heat stress. Shade, which costs no energy, comes first, and side screens help there; in humid climates the shelter should stay open to the breeze.

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
- Water Resources Research Center, University of Arizona (2010). Water–energy nexus. *Arroyo* (annual newsletter).
- Middel, A., Krayenhoff, E. S. (2019). Micrometeorological determinants of pedestrian thermal exposure during record-breaking heat in Tempe, Arizona. *Sci Total Environ* 687:137–151.
- Middel, A., et al. (2021). 50 grades of shade. *Bull Amer Meteor Soc* 102:E1805–E1820.
- Morris, N. B., et al. (2021). Electric fan use for cooling during hot weather: a biophysical modelling study. *Lancet Planet Health* 5:e368–e377.
- Bröde, P., Kampmann, B. (2023). Temperature–humidity-dependent wind effects on physiological heat strain of moderately exercising individuals reproduced by the UTCI. *Biology* 12:802.
- Meade, R. D., et al. (2024). A critical review of the effectiveness of electric fans as a personal cooling intervention in hot weather and heatwaves. *Lancet Planet Health* 8:e256–e269.
- Kuchcik, M. (2021). Mortality and thermal environment (UTCI) in Poland—long-term, multi-city study. *Int J Biometeorol* 65:1529–1541.
- Ulpiani, G., et al. (2019). Thermal comfort improvement in urban spaces with water spray systems: field measurements and survey. *Build Environ* 156:46–61.
- Kaparias, I., et al. (2015). Analysing passenger arrival rates and waiting time at bus stops. TRB Annual Meeting.
- Seckel, S. (2019). Devilishly hot. ASU News (MRT measurements by A. Middel and E. S. Krayenhoff).
- Iowa Environmental Mesonet, ASOS archive (PHX, IAH, 2020–2024).
- Tartarini & Schiavon (2020), pythermalcomfort.
- Stull (2011), wet-bulb formula.
- ASHRAE Handbook—Fundamentals, Ch. 1.
- EnergyPlus Engineering Reference, "Air Exchange".
- Manufacturer data sheets (Jinghui JH18AP; Puravent EC30-VS).
