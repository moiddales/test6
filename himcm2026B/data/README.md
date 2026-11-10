# 数据来源与核实状态

**核实等级：**

- **原文核实**：打开原文，找到了对应句子或表格；下表附原文摘录。
- **摘要**：只看到搜索结果或文章摘要，没有读到原文。
- **未核实**：找过，但原文打不开或找不到。

## 1. 实测数据（本项目自己下载和处理）

| 数据 | 来源 | 用在哪 |
|---|---|---|
| 凤凰城 Sky Harbor 机场（PHX）、休斯敦 Bush 机场（IAH）2020–2024 年夏季逐时观测：气温、露点、相对湿度、风速 | Iowa Environmental Mesonet ASOS 存档（例行逐时 METAR），文件 `weather/PHX_raw.csv`、`weather/IAH_raw.csv` | 2a 和 2b 的设计日 |

**设计日的做法**（`weather/hot_days.py`）：取 2020–2024 年 7 月日最高气温在第 90 百分位以上的日子（每站 25 天），逐小时求平均。风速按对数风廓线从 10 m 高度折算到人体高度 1.1 m（乘以 0.68）。结果在 `weather/july_profiles.csv`、`weather/july_summary.csv`：

| 站点 | 7 月平均：最高 / 最低 | 7 月高温日：最高 / 最低 | 高温日最热时刻的露点 | 高温日 6–22 时人体高度平均风速 |
|---|---|---|---|---|
| PHX | 42.1 / 31.8°C | **46.4 / 34.2°C**（15 时） | 8.4°C（RH 11%） | 2.7 m/s |
| IAH | 33.3 / 25.7°C | **37.4 / 27.0°C**（16 时） | 21.0°C（RH 39%） | 2.4 m/s |

原先设定的设计日（43 / 31°C，36 / 26°C，风速 1.5 m/s）已全部换成上面的实测曲线。

## 2. 文献与标准

| 数据 | 数值 | 等级 | 出处与原文摘录 |
|---|---|---|---|
| 风扇对静坐者的效果 | 36°C 时湿度 80% 以下有益，42°C 时 50% 以下有益 | 原文核实 | Ravanelli, Hodder, Havenith, Jay. *JAMA* 2015;313(7):724–725, doi:10.1001/jama.2015.153。"electric fans prevent heat-related elevations in HR and core temperature in healthy young men up to approximately 80% RH at 36°C and 50% RH at 42°C" |
| 风扇在干热 / 湿热下的效果 | 40°C / 50% 有益；47°C / 10% 有害 | 原文核实（转引） | Foster et al. *Int J Biometeorol* 2022;66(3):507–520，转引 Morris et al. 2019："electric fans provided a net cooling effect in a hot humid environment (40 °C Ta, 50% relative humidity) but were detrimental in very hot and arid conditions (47 °C Ta, 10% relative humidity)" |
| 风扇与劳动能力 | ≥ 35°C 且湿度 < 50% 时无效甚至有害 | 原文核实 | 同上 Foster 2022 摘要。该研究针对体力劳动，候车属于静坐，2a 以静坐实验为检验依据 |
| ~~RH 20% 时老年人约 42°C、年轻人约 45°C~~ | — | **原文中没有，已弃用** | 之前引用 PMC8850241（即 Foster 2022），原文里找不到这句话 |
| UTCI 热应激等级 | 26 / 32 / 38 / 46°C | 摘要（元数据已核实） | Bröde et al. 2012, *Int J Biometeorol* 56(3):481–494 |
| 日晒下的平均辐射温度 | 峰值 168°F（75.6°C），正午测量，混凝土步道 | 原文核实 | ASU News "Devilishly hot"（Seckel, 2019-06-14），Middel 与 Krayenhoff 实测。"The peak mean radiant temperature Middel and Krayenhoff measured there was 168 F." 原文没给当时气温 |
| 水的隐含能耗 | 美国平均"近 2,000 kWh/百万加仑"（≈ 0.53 kWh/m³）；加州是平均值的 2–5 倍 | 原文核实 | Hamilton, Arzbaecher, Ehrhard, Murphy, "Driving Energy Efficiency in the U.S. Water & Wastewater Industry…", ACEEE Summer Study on Energy Efficiency in Industry 2009, p. 6-32。"The average U.S. water supply system uses almost 2,000 kWh per million gallons (MG) of treated water" |
| ~~1,809 kWh/百万加仑（100 多家供水公司调查）~~ | — | **未核实，已弃用** | 原文（RSC 论文）返回 403 |
| 冷柜渗入负荷占比 | 中温敞口立式柜 70–80%，该文测试为 73% | 原文核实 | Sarhadian, Faramarzi, Coburn, Lutton (SCE), Navaz, Walker, "Paving the Path for a New Generation of High-Efficiency Supermarket Refrigerated Display Cases", ACEEE Summer Study 2004。"infiltration load, which comprises roughly 70% to 80% of the total cooling load" |
| 加门：负荷 −80%，能耗 −71% | 每英尺 1576 → 315 Btu/h；33.3 → 9.6 kWh/天 | 原文核实 | Hillphoenix 案例研究"Adding Glass Doors to Multi-Deck Meat Case"，按 ASHRAE 72 测试 |
| 加门：负荷 −68%（五层乳品/熟食柜） | 68% | 摘要 | SCE Irwindale 制冷与热工测试中心的实验室测试，ProQuest 文档 192523679 的摘要。ACHR News "Closing an Open Case" 里**没有**这个数字 |
| 加门：能耗 −42%，无持续销售影响 | 42% | 原文核实 | HVAC&R News "Improving cooling efficiency in the dairy aisle"（Aliento），新西兰 Countdown Pukekohe South 门店试点 |
| ~~加门后能耗为敞口的 39.4%（ISO 23953 测试）~~ | — | **未核实，已从检验中移除** | LSBU ICR 2019 论文，返回 503 |
| DOE 能效限值（2017-03-27 以后生产） | VOP.RC.L = 2.2·TDA + 6.85；HZO.RC.L = 0.55·TDA + 6.88（TDA 单位 ft²） | 原文核实 | 10 CFR 431.66(e)，2025 年版，govinfo.gov。2012–2017 年的旧值是 2.27 和 0.57。2025 年 1 月的新规则未能读取（联邦公报网站被拦截） |
| ASHRAE 62.1 湿度上限 | 蒸发冷却运行时区域相对湿度 ≤ 65% | 原文核实 | ANSI/ASHRAE 62.1-2022 附录 e，新增第 5.13.1 条："Air in each HVAC zone shall be limited to a maximum relative humidity of 65% whenever evaporative cooling equipment is operating." |
| ASHRAE 72 开门程序 | 8 小时，每扇门约每 10 分钟开一次 | 摘要 | NREL 2023 报告的描述 |
| 空调额定工况 | 室外 95°F；EER 10–12.5 | 摘要 | AHRI 210/240 和 390；10 CFR 431.96 |
| 蒸发冷却器规格 | 18,000 m³/h 对 1.1 kW、耗水 15–20 L/h；30,000 对 3 kW；25,000 对 2.2 kW | 摘要（供应商页面） | Jinghui JH18AP、Puravent EC30-VS、made-in-china 产品页 |
| ISO 23953 气候等级 3 = 25°C / 60% | — | **未核实** | 标准的公开样章里没有这张表。阶段一把它当作商场环境的假设，并做了 21–27°C、30–70% 的敏感性分析 |
| 凤凰城 / 休斯敦 7 月常年值 | 41.4°C / 约 35°C | 摘要 | NWS。已被第 1 节的实测数据取代，只作背景 |
| 屏蔽门节能 | 15–30% | 摘要（二手） | 维基百科、Railway News，只作背景 |

## 3. 凭已有知识使用的公式与常数

湿空气公式（Magnus、ASHRAE 绝热饱和方程）、物性常数、Stull (2011) 湿球公式、门洞浮力换气公式、射流稀释公式、利特尔定律、对数风廓线、卡诺效率法估算 COP、食品冷冻 −18°C。引用信息已用 Crossref 核对元数据（2026-11-09 审计）：Tartarini & Schiavon 2020（*SoftwareX* 12:100578）、Stull 2011（*J Appl Meteor Climatol* 50:2267–2269）、Bröde, Fiala, Błażejczyk, Holmér 等（*Int J Biometeorol* 56:481–494，2011 年在线、2012 年刊印）。

## 4. 假设参数

每个假设的取值、依据和敏感性范围见各阶段 README 的"参数表"。

## 5. 2026-11-09 审计新增的数据（2026-11-10 已用进模型）

下表最后一列是这些数据在模型里的用途；它们优先于上面各节的旧取值。

| 数据 | 数值 | 等级 | 出处与原文摘录 | 用途 |
|---|---|---|---|---|
| 凤凰城输水能耗 | CAP 平均 5.5 kWh/千加仑（≈ 1.45 kWh/m³）；自来水约 1.8 kWh/千加仑（≈ 0.48 kWh/m³） | 原文核实 | Arroyo 2010, "Water–Energy Nexus"，亚利桑那大学 WRRC。"On average, CAP uses 5.5 kilowatt-hours of electricity for each thousand gallons (kgal) of water it delivers." | 凤凰城的水隐含能耗取 1.93 kWh/m³（`model.E_WATER`） |
| 低温柜 EER（AHRI 计算 DOE 电耗所用） | 调整露点 −36°F 时 5.48，−1°F 时 8.95 Btu/Wh（COP 1.6–2.6） | 原文核实 | ANSI/AHRI Standard 1200-2023 (I-P)，表 1 "EER for Remote Commercial Refrigerated Display Merchandisers and Storage Cabinets"（law.resource.org 法规引用版） | 阶段一：说明 COP 1.6 位于最低端，DOE 检验偏保守 |
| 低温玻璃门柜的冷负荷 | 冷冻食品 AHRI 额定 910–1,010 Btu/h/门（267–290 W） | 原文核实 | Hussmann RL 数据表 P/N 0510175，"BTU/h (W) per door … 955 (280 W)" | 阶段一新检验：模型 308 W/门（高 10%） |
| 低温玻璃门的防凝露加热 | 5 门：门加热 260–455 W + 门框 236 W；风扇 90 W | 原文核实 | 同上，"Component Specifications"表；注："Maximum door watts without anti-sweat cycling controls shown." | 玻璃门防凝露加热从 0.3 kW 改为 0.5 kW，敏感性范围 0.3–0.7 |
| 低温门防凝露加热（佐证） | 每扇门 100–200 W | 检索 | ACCA HVAC 博客；SCE 防凝露加热报告 | 同上 |
| 日晒下的平均辐射温度 | 气温 48.5°C 时 MRT 最高 76.4°C（15:00，东西向街谷） | 摘要 | Middel & Krayenhoff 2019, *Sci Total Environ* 687:137–151 | 支持日晒比气温高 +30°C |
| 不同遮阳的效果 | 轻质遮阳结构的效果排在建筑阴影和树荫之后；ΔMRT 相差可达 50°C | 摘要 | Middel et al. 2021, "50 Grades of Shade", *BAMS* 102:E1805–E1820 | 同上 |
| 候车亭的辐射降温 | 候车亭平均让 MRT 比全日晒低 15°C；建筑阴影低 23°C | 检索（原文 403） | 亚利桑那大学图森 MaRTy 报告，repository.arizona.edu/handle/10150/679953 | 顶棚下 MRT 取气温 + 12°C，敏感性范围 8–16°C |
| 风对热应激的作用与 UTCI | 超过 35°C 时，水汽压 > 2 kPa（心率、核心体温）或 > 3 kPa（皮温、出汗）风才有益；UTCI 与实测相关系数 r = 0.9 | 摘要 | Bröde & Kampmann 2023, *Biology* 12(6):802（Europe PMC，PMC10295525） | 2a 表 7 |
| 风扇无害的温度上限 | 年轻人 39°C、老年人 38°C、服抗胆碱药的老年人 37°C | 摘要 | Morris et al. 2021, *Lancet Planet Health* 5:e368–e377 | 2a 表 7 |
| 35°C 以上风扇的作用 | 对核心体温没有有意义的降低 | 摘要 | Meade et al. 2024, *Lancet Planet Health* 8:e256–e269 | 2a 表 7：按此截断后风扇的设计日结果 |
| UTCI 与死亡风险 | UTCI > 32°C 时死亡相对风险上升 10–20%，> 38°C 时上升 25–30% | 摘要 | Kuchcik 2021, *Int J Biometeorol* 65:1529–1541 | 热应激权重的依据 |
| 喷雾降温实测 | 气温降 8.2°C、UTCI 降 7.9°C；1–2 m/s 微风下效果最好 | 摘要 | Ulpiani et al. 2019, *Build Environ* 156:46–61 | 送到人身上的降温量级检验 |
| 乘客随机到站的班距上限 | 约 12 分钟以内随机到达 | 检索 | Kaparias et al., TRB 2015（综述 Seddon & Day） | 平峰候车人数 |
