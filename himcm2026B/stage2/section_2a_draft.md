# 4. Requirement 2a: Cooling Efficiency of an Open-Sided Bus Shelter

*Draft for the paper. Every number comes from `outputs/` (run `run_stage2.py` and `sensitivity.py`). Figure and table numbers are local to this section.*

## 4.1 What "efficiency" must measure

The problem table compares the three systems with numbers that measure different things. The fan "makes the space feel up to 3 °C cooler" by moving air; the evaporative coolers "lower air temperature up to 5 °C and 8 °C" and add moisture while doing so. Dividing those numbers by power gives 12, 4.2 and 3.2 °C/kW. That ratio ignores three facts that Section 3 (the open freezer case) already showed matter:

1. **Only cooling that reaches people counts.** In the freezer case 87 % of the cooling is spent on the opening and only 13 % protects the product; at a bus stop the target is the people waiting. Air cooled in an empty corner, or blown out of the open sides, is wasted.
2. **The device's effect depends on the weather.** An evaporative cooler can never cool air below its wet-bulb temperature. A fan delivers heat to the body once the air is hotter than skin.
3. **Relief is worth more when heat is dangerous.** Lowering felt temperature from 44 °C to 38 °C prevents harm; lowering it from 27 °C to 24 °C adds comfort only.

We therefore define

$$
\eta \;=\; \frac{N_{\text{ben}} \cdot R}{P}
\qquad \left[\frac{\text{person}\cdot{}^\circ\text{C}\cdot\text{h}}{\text{kWh}}\right],
$$

where $N_{\text{ben}}$ is the number of people the device actually reaches, $R$ is the heat-stress relief each one receives (Section 4.6) and $P$ is electric power. Over a day, $\eta_{\text{day}} = \sum_t N_{\text{ben}} R \,/\, \sum_t E$. Water use is reported beside $\eta$.

## 4.2 Assumptions

| # | Assumption | Justification |
|---|---|---|
| A1 | The shelter is 6 × 1.8 × 2.5 m, with a roof, a back panel and three open sides; people stand in the shade. | Standard city shelter; the problem says "open-sided". |
| A2 | The "up to" values in the problem table are outlet ratings at a reference condition. | Manufacturers rate coolers at the outlet. A2 is varied through $D_{\text{ref}}$ (A4). |
| A3 | The fan's "3 °C" is a felt-temperature reduction at 30 °C / 50 % RH. | Fan ratings are quoted for warm conditions where fans work; the reference is varied from 28 to 33 °C. |
| A4 | The coolers' rated drops hold at a wet-bulb depression $D_{\text{ref}} = 10$ °C. | This gives saturation effectiveness $\varepsilon = 0.50$ (B) and $0.80$ (C), inside the 0.5–0.9 range of direct evaporative coolers. |
| A5 | Airflow scales with power as in commercial data sheets: B 5.0 m³/s at 1.2 kW, C 7.5 m³/s at 2.5 kW. | 18,000 m³/h at 1.1 kW; 25,000 m³/h at 2.2 kW; 30,000 m³/h at 3.0 kW. |
| A6 | Passengers arrive at random; buses run with a headway coefficient of variation of 0.5. | Standard transit assumption; it sets the mean wait. |
| A7 | Devices do not change the radiant environment. | Coolers and fans act on air, not on the shade roof or the pavement. |

## 4.3 Sub-model M1: moist air

Saturation vapour pressure, humidity ratio and enthalpy follow ASHRAE Fundamentals:

$$
p_{ws}(T) = 611.2\, e^{17.62T/(243.12+T)},\qquad
W = 0.622\,\frac{p_w}{p-p_w},\qquad
h = 1.006\,T + W(2501 + 1.86\,T).
$$

The wet-bulb temperature $T_{wb}$ solves the adiabatic-saturation equation by bisection. It agrees with the empirical formula of Stull (2011) within 0.5 °C at all four test conditions (Table 0).

## 4.4 Sub-model M2: what each device does to the air

**Evaporative coolers (B, C).** The outlet temperature is

$$
T_s = T - \varepsilon\,(T - T_{wb}),\qquad \varepsilon = \Delta T_{\text{rated}}/D_{\text{ref}}.
$$

Evaporation is adiabatic, so enthalpy is conserved and $W_s = (h - 1.006\,T_s)/(2501 + 1.86\,T_s)$. The device produces sensible cooling $\rho c_p Q_s (T - T_s)$ and evaporates water at $\rho Q_s (W_s - W)$.

The rated drop is therefore a function of climate:

- At 42 °C / 15 % ($T - T_{wb} = 20.5$ °C), B's outlet is 10.2 °C below ambient.
- At 35 °C / 55 % ($T - T_{wb} = 7.8$ °C), B's outlet is 3.9 °C below ambient.

**Fan (A).** The fan raises air speed at the person and leaves temperature and humidity unchanged. We calibrate its air speed so that UTCI falls by exactly 3 °C at the reference condition (A3); the result is 2.93 m/s.

The fan's effect is not fixed: UTCI's human heat-balance model includes convective heat gain once air is hotter than skin. At 20 % RH the fan stops helping at 41.6 °C. Laboratory and modelling studies place this break-even near 42 °C for older adults and 45 °C for young adults (Ravanelli et al., 2015; review in PMC8850241). Bus riders include older adults, so the model's threshold is the one that matters.

## 4.5 Sub-model M3: how much cooling reaches people

This is the open-freezer problem. We compare two ways of delivering cooled air.

**Volume mode (cool the whole shelter).** The occupied zone is treated as well mixed:

$$
T_z = \varphi\,T_s + (1-\varphi)\,T + \frac{N q_p}{\rho c_p (Q_s + Q_{\text{inf}})},\qquad
\varphi = \frac{Q_s}{Q_s + Q_{\text{inf}}}.
$$

Ambient air enters by wind and by buoyancy, combined in quadrature as in ASHRAE infiltration models:

$$
Q_{\text{inf}} = \sqrt{Q_{\text{wind}}^2 + Q_{\text{buoy}}^2},\qquad
Q_{\text{wind}} = C_w A v,\qquad
Q_{\text{buoy}} = \frac{C_d}{3}\, W_{\text{open}} \sqrt{g H_z^3\, \frac{T - T_z}{T}}.
$$

$Q_{\text{buoy}}$ is the cold air that spills out of the bottom of the open sides, the same mechanism the Gosney–Olama family of equations describes for open cold-store doors. Because $Q_{\text{buoy}}$ depends on the temperature difference it creates, $T_z$ is found by fixed-point iteration.

**Spot mode (aim the jet at people).** A covered person receives a mix of jet air (share $\theta$) and entrained ambient air:

$$
T_p = T - \theta\,(T - T_s),\qquad
\theta = \frac{\theta_0}{1 + v_{\text{in}}/u_{\text{jet}}}.
$$

Cross-wind $v_{\text{in}}$ bends and dilutes the jet. The jet also raises air speed at the person to $\sqrt{v_{\text{in}}^2 + u_{\text{jet}}^2}$.

Figure 2 shows the waste. Device C at 42 °C / 15 % makes air 16.4 °C cooler at the outlet; where people stand, the drop is 11 °C in calm air and 5–6 °C at 4 m/s wind. At the base wind of 1.5 m/s, 47–51 % of the air reaching a person in spot mode is cooled air.

## 4.6 Sub-models M4–M6: people, felt temperature, relief

**People (M4).** By Little's law, the mean number waiting is $N = \lambda W$. With random arrivals the mean wait is $W = \tfrac{h}{2}(1 + CV^2)$. For 40 passengers/h and a 10-minute headway, $N = 4.17$.

A device covers at most $Q/q$ people, with $q = 0.8$ m³/s per person: 4 people for A, 6.25 for B and 9.4 for C. So $N_{\text{ben}} = \min(N, Q/q)$.

**Felt temperature (M5).** We use the Universal Thermal Climate Index (UTCI), computed with *pythermalcomfort*. UTCI is the standard outdoor index: it combines air temperature, humidity, wind and mean radiant temperature through a human heat-balance model. The fan's wind and the coolers' cooling and added moisture are therefore measured on one scale.

In shade, mean radiant temperature is set to air temperature + 4 °C. Wind at 1.1 m is converted to the 10 m reference speed UTCI expects by the log-wind profile (×1.47).

**Relief (M6).** UTCI's heat-stress bands begin at 26 (moderate), 32 (strong), 38 (very strong) and 46 °C (extreme) (Bröde et al., 2012). With band weights $w = 1, 2, 3, 4$,

$$
D(U) = \int_{26}^{U} w(u)\,du,\qquad R = D(U_{\text{before}}) - D(U_{\text{after}}).
$$

Cooling below UTCI 26 earns nothing. Cooling inside the very-strong band earns three times as much as cooling inside the moderate band. $R < 0$ means the device makes people hotter.

## 4.7 Results

**Table 1. Efficiency at four conditions** (wind 1.5 m/s, 4.17 people waiting; B and C in spot mode).

| Condition | Device | UTCI before → after | Relief $R$ | $\eta$ | Water (L/h) |
|---|---|---|---|---|---|
| Hot-dry 42 °C / 15 % | A | 42.6 → 42.7 | −0.30 | **−4.8** | 0 |
| | B | 42.6 → 38.6 | 11.87 | **41.2** | 85 |
| | C | 42.6 → 35.1 | 19.61 | 32.7 | 205 |
| Hot-humid 35 °C / 55 % | A | 38.0 → 36.0 | 4.23 | **67.7** | 0 |
| | B | 38.0 → 36.0 | 4.05 | 14.1 | 33 |
| | C | 38.0 → 34.6 | 6.95 | 11.6 | 80 |
| Warm 30 °C / 50 % | A | 31.3 → 28.4 | 2.92 | **46.7** | 0 |
| | B | 31.3 → 29.0 | 2.31 | 8.0 | 34 |
| | C | 31.3 → 27.3 | 3.98 | 6.6 | 81 |
| Very humid 32 °C / 75 % | A | 36.7 → 34.0 | 5.49 | **87.9** | 0 |
| | B | 36.7 → 35.1 | 3.14 | 10.9 | 16 |
| | C | 36.7 → 34.1 | 5.18 | 8.6 | 39 |

**Key findings.**

1. **Climate decides the winner.** Figure 3 maps the most efficient device over temperature and humidity. The fan wins everywhere except hot, dry air. Evaporative cooling wins when the air is at least 36 °C and the wet-bulb depression exceeds a threshold that falls as temperature rises: about 18 °C at 38 °C, about 15 °C at 42 °C and about 14 °C at 44 °C (Table 5).
2. **The fan can make things worse.** At 42 °C / 15 % the fan raises UTCI by 0.1 °C ($\eta < 0$). On the hot-dry design day it is harmful from 13:00 to 17:00 (Fig. 4).
3. **Crowd size decides between B and C.** At the hot-dry peak, B is more efficient for up to 6 waiting passengers ($\eta$ 58.5 vs 49.8 at 6 people). C is more efficient from 8 passengers on (66.4 vs 60.9), because C covers 9.4 people and B only 6.25.
4. **Aim the air at people.** Spot mode beats volume mode by 16 % to about 5 times. The air temperatures delivered are similar; the difference is the jet's air movement.
5. **Water is a real cost in dry heat.** At 42 °C / 15 % B evaporates 85 L/h and C 205 L/h. Data-sheet figures of 15–20 L/h for an 18,000 m³/h cooler correspond, by the energy balance, to only about 2 °C of cooling.

**Design days.** Figure 4 and Table 2 integrate the model over 06:00–22:00 on a hot-dry day (43/31 °C, dew point 12 °C) and a hot-humid day (36/26 °C, dew point 23 °C), with realistic peak and off-peak ridership. Climate assumptions are anchored to NWS 1991–2020 July normals for Phoenix (mean high 41.4 °C) and Houston (mean high about 35 °C).

| Design day | Device | Energy (kWh) | Water (L) | $\eta_{\text{day}}$ (always on / smart) | Person-h at UTCI ≥ 38: before → after |
|---|---|---|---|---|---|
| Hot-dry | A | 4.0 | 0 | 17.7 / 26.9 | 52.3 → 45.3 |
| | B | 19.2 | 1193 | **35.7 / 36.4** | 52.3 → 28.1 |
| | C | 40.0 | 2874 | 28.2 / 28.7 | 52.3 → **0** |
| Hot-humid | A | 4.0 | 0 | **63.5 / 66.3** | 18.0 → 2.2 |
| | B | 19.2 | 500 | 14.3 / 15.6 | 18.0 → 0 |
| | C | 40.0 | 1203 | 11.4 / 12.4 | 18.0 → 0 |

The smart rule runs a device only when UTCI ≥ 32, the device helps, and someone is waiting; the chance that someone is waiting is $1 - e^{-N}$ under Poisson arrivals. The rule raises the fan's hot-dry efficiency from 17.7 to 26.9 by switching it off in the hours when it adds heat.

Efficiency and effectiveness diverge. On the hot-dry day only C removes every person-hour of very strong heat stress, at 1.5 times B's water use per unit of relief. Requirement 4 builds on this trade-off.

## 4.8 Validation and sensitivity

**Validation (Table 0, 12 checks pass).**

- Wet-bulb temperatures agree with Stull (2011) within 0.5 °C.
- The cooler's sensible cooling equals the latent heat of the evaporated water within 3 % (energy closure).
- The calibrated fan reproduces its 3 °C rating at the reference condition.
- The fan's dry-air break-even (41.6 °C at 20 % RH) agrees with physiological evidence for older adults (about 42 °C).
- The mixing model returns the outlet temperature as $Q_s \to \infty$ and the ambient temperature as $Q_s \to 0$.

**One-at-a-time sensitivity (Fig. 5).** Each parameter is moved across its plausible range (README §4).

- The number of people waiting moves $\eta$ most for every device, because $\eta$ scales with the people covered.
- For the fan in dry heat, the reference temperature of its rating dominates: a fan rated at 33 °C needs more air speed, and that air speed delivers more heat at 43 °C ($\eta$ down to −122).
- For the coolers, the jet share $\theta_0$ and $D_{\text{ref}}$ come next.
- Changing the heat-stress weights from 1-1-1-1 to 1-3-9-27 scales $\eta$ by about 3.6–9 times but leaves the ranking unchanged in both climates.

**Monte Carlo (Fig. 6, 3,000 draws).** All parameters are sampled uniformly over their ranges, with a random weight scheme.

- The fan is the most efficient device at the hot-humid peak in 99.6 % of draws.
- At the hot-dry peak, B is most efficient in 52 % of draws and C in 48 %; the fan has $\eta < 0$ in 87 % of draws.

The climate-based ranking is therefore robust. The B-versus-C choice in dry heat depends on crowd size and is settled by the rule in finding 3.

## 4.9 Answer to Requirement 2a

The most efficient system depends on climate and use.

- **Humid or moderately hot weather (most US summer climates):** the fan (A). It delivers 4–10 times more relief per kWh than either cooler and uses no water.
- **Hot, dry weather** (≥ 36 °C with a wet-bulb depression of about 14–20 °C or more): evaporative cooling. Use B at quiet stops (up to about 6 people waiting) and C at busy stops. Only C keeps waiting passengers out of very strong heat stress at a 43 °C peak.
- **In every climate:** aim the air at the waiting area, and switch devices off when nobody is waiting or when the fan would add heat.

---

**Figures for this section:**

- `outputs/fig1_climate_dependence.png`
- `outputs/fig2_dilution_vs_wind.png`
- `outputs/fig3_winner_map.png`
- `outputs/fig4_design_days.png`
- `outputs/fig5_tornado.png`
- `outputs/fig6_monte_carlo.png`

**References used here:**

- Bröde et al. (2012) *Int J Biometeorol* 56:481–494
- Ravanelli et al. (2015) *JAMA* 313:724–725
- Tartarini & Schiavon (2020) *SoftwareX* 12:100578
- Stull (2011) *J Appl Meteor Climatol* 50:2267–2269
- ASHRAE Handbook—Fundamentals (2021), Ch. 1
- EnergyPlus Engineering Reference, "Air Exchange" (Gosney–Olama doorway model)
- NWS Phoenix and Houston 1991–2020 climate normals
- Manufacturer data sheets (Jinghui JH18AP; Puravent EC30-VS)
