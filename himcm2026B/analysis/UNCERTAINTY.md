# Evidence and uncertainty ledger

These ranges are stress-test choices, not measured confidence intervals. Independent uniform sampling deliberately explores scenarios; its winning fractions are conditional on those choices, not real-world probabilities.

| Quantity | Main assumption | Stress range / alternative | Evidence status |
|---|---:|---|---|
| Evaporative reference depression | 10°C | 8.5–13°C; outlet-rating alternative | Device table gives maxima only; effectiveness is assumed |
| Jet air share at person | 0.70 | 0.50–0.85 | Unmeasured geometry/mixing surrogate |
| Evap jet speed | B 1.5, C 2.0 m/s | ×0.7–1.3 | Engineering scenario, not venue measurement |
| Airflow per covered person | 0.8 m³/s | 0.5–1.2 | Coverage assumption; occupancy is not thermal energy |
| Shelter wind factor | 0.50 | 0.30–0.80 | Airport-to-venue extrapolation plus shielding assumption |
| Outdoor wind | Observed ASOS; log profile | 0.5–4.5 m/s in parameter sampling | Airport measurement is not a local flow survey |
| Midday MRT excess under shade | 12°C | 8–16°C, multiplied by daylight factor | Assumption; cross-study differences are not a calibration |
| Interior MRT excess | 4°C | 2–8°C | Surface radiation surrogate |
| AC supply fraction to occupied zone | 1.0 | 0.40, 0.65, 0.85, 1.00 | Explicit sensitivity; outlet height alone does not establish it |
| Thermal mass / zone air | 3 | 1–6 | Lumped unmeasured heat capacity |
| Embedded water energy | Phoenix 1.93; Houston 0.53 kWh/m³ | 0–2.64 | Regional order estimate, not marginal utility-meter data |
| Humidistat limits | resume 60%, stop 65% | Optional facility constraint | Informed by ASHRAE 62.1-2022 Addendum e §5.13; exceptions and applicability matter |
| UTCI stress weights | 1,2,3,4 | 1,1,1,1 and 1,3,9,27 | Normative utility choice; no mortality calibration |

Measured weather comes from the archived IEM routine METAR records, PHX and IAH, July 2020–2024. “Top 10%” means maximum temperature ≥ the empirical 90th percentile, so ties can select more than 10%. Profiles average temperature, dew point and wind; a profile is not an actual observed day.

`actual_hot_days.csv` retains separate complete hourly days. `weather_quality.csv` lists every selected date and completeness decision. The bus model evaluates every complete selected day. The station control stress test uses five dates per city evenly spaced in sorted daily-maximum temperature, including both endpoints; it is neither random nor representative of all weather. No missing day is replaced with the mean profile.

No local passenger counts, globe-temperature measurements, anemometer transects, product temperature logs, or equipment performance tests were supplied. Before procurement, measure those quantities; site-specific rankings and absolute effects remain conditional.

Primary reference: https://www.ashrae.org/file%20library/technical%20resources/standards%20and%20guidelines/standards%20addenda/62_1_2022_e_20220930.pdf
