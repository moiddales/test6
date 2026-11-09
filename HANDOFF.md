# 交接文档：2026 HiMCM B 题建模

接手的 AI 请先完整读完本文件再开始工作。前一个 AI 的对话上下文你看不到，项目背景、用户的全部指令、当前进度、剩余工作和工作规范都写在这里。

- 仓库：`moiddales/test6`
- 工作分支：`claude/modest-archimedes-khi35o`，所有提交都推送到这个分支；用户没有要求时不要开 PR
- 交接日期：2026-11-09
- 用户的项目准则（AGENTS.md）全文见附录 A，题面全文见附录 B

---

## 1. 项目是什么

用户正在参加 2026 年 HiMCM（高中生数学建模竞赛，主办方 COMAP），比赛正在进行。用户上传了 A、B 两道题的 PDF，前一个 AI 分析了两题并推荐 B 题，用户选定了 **B 题："Air Conditioning the Environment: Modeling Energy Waste in Public Cooling"**（开放与半开放公共空间的冷却能耗）。

B 题有 5 问：
1. 敞口冷柜的效率应包含哪些量；
2. 公交站效率模型（2a），以及半开放火车站候车区的修订模型（2b）；
3. 推广到至少两个真实场馆；
4. 从效率扩展到效果（舒适、安全、能耗、成本）；
5. 运营指南、给 COO 的 1–2 页备忘录、面向公众的博客。

提交物要求：PDF 不超过 25 页，包括摘要页、目录、完整解答、COO 备忘录、参考文献。如果用了 AI，需附 AI 使用报告，这部分不计入 25 页。

工作方式：用户逐阶段下指令，前一个 AI 每完成一个阶段就交付"代码 + 计算输出 + 中文说明 + 英文论文节草稿"。论文最终由用户团队整合提交。

---

## 2. 用户的全部指令（按时间顺序，原文照录）

> 引号里是用户原话；"说明"是前一个 AI 的执行记录或理解，"状态"表示这条指令现在是否还有效。

1. （附上 A、B 两题 PDF）「阅读以下内容，详细深度分析两个选题，用尽可能通俗易懂（说人话）的方式分析两个题目的解题思路，以及选择推荐；不允许为了通俗易懂而降低分析深度或者技术含量或者准确性。」
   - 说明：前一个 AI 在对话里给出了两题的分析，推荐"团队有热学基础就选 B"。
   - 状态：**"说人话但不降低深度、技术含量和准确性"是长期的表达要求。**
2. 「继续，注意同时阅读我的github仓库里面的qwerty仓库里的claude/affectionate-mayer-ihqczh知识库」
   - 说明：`moiddales/qwerty` 是用户自建的 HiMCM 知识库，整理了 2014–2024 年 92 篇 O 奖论文。它是公开仓库，可以匿名克隆，见第 8 节。
   - 状态：长期有效，**选方法、做检验、写论文时应参考这个知识库**。
3. 「假设选择方向B，简要介绍步骤阶段」
   - 说明：用户选定 B 题。前一个 AI 给出了分阶段计划（阶段 0–6），命名后来调整过，见第 3 节。
4. 「现在按照阶段二完成完整具体的实施方案」
5. （附上 AGENTS.md）「先阅读以下文档作为项目准则，之后继续完成完整阶段二，如果需要，可以深度使用联网搜索或者调用知识库去搜索需要的数学模型，也可以使用程序模拟。完成完整阶段二」
   - 状态：长期有效。
     - **AGENTS.md 是项目准则**，全文见附录 A；它的原始上传文件在新容器里可能不存在。
     - **允许深度联网搜索、调用知识库、做程序模拟。**
6. 「阶段一完成了吗」
   - 说明：当时没有完成，前一个 AI 如实回答了。
7. 「完成完整阶段一和阶段二」
8. 「继续，完成阶段一之后用阶段一的内容修改阶段二a，可能需要重做一些东西。之后完成阶段二b」
   - 状态：**后面的阶段要吸收前面阶段的结论，必要时回头修改已完成的部分。**
9. 「之后告诉我你的数据哪里来的」
   - 说明：前一个 AI 把数据来源分成五类列给了用户，见第 6 节。
   - 状态：**用户在意数据来源和可靠程度**，每个数字都要能说出出处。
10. 「生成交接文档」
    - 说明：也就是本文件（第一版）。
11. 「对于降温，湿度等数据，是否可以使用计算机程序仿真模拟来取得数据，结合数学物理来为项目增加其中一个亮点。分析这样做是否可以提高准确性」
    - 说明：前一个 AI 的分析结论是：仿真只能改善"模型结构"误差，改善不了"输入参数"误差；本项目里最值得仿真的是"冷风从出风口到人身上的稀释"（射流占比 θ0、风压换气系数 C_w、挡风系数），它们对效率影响很大；做法是先让仿真通过文献实验检验，再用来标定快速模型，并顺带产出冷热分布图作为亮点。
12. 「你刚刚提及的实验难道不能也用计算机模拟取得吗」
    - 说明：回答是不能——仿真结果再去"模拟实验"属于循环论证；检验必须对照独立于模型的真实测量，自己做不了实验时可以用文献实验数据。
13. 「你一开始刚刚关于仿真的分析太生僻，说人话」
    - 状态：再次强调表达要通俗（见第 1 条）。
14. 「一定要使用小规模仿真吗，我觉得规模可以变大，如果需要更多的算力可以把程序放到我的台式电脑上面跑」
15. 「i7 9700，32GB DDR4 RAM，3070显卡，windows系统」
    - 说明：前一个 AI 据此给出的 CFD 计划：在用户台式机上用 OpenFOAM（经 WSL2，`.wslconfig` 设 memory=28GB、processors=8）跑 RANS，候车亭 200–300 万格子、约 18 个算例；车站 400–600 万格子、6–8 个算例；先做三项文献实验对照和网格收敛；显卡对 OpenFOAM 没用。还向用户问了两件事——比赛截止时间、用哪种运行方式（本机自己跑，或开 Remote Control 让 AI 操作），**用户尚未回答**。
16. 「先不考虑仿真，尝试去搜索补充你之前缺失的数据」
    - 说明：仿真暂缓。前一个 AI 据此下载了实测气象、核对了文献原文，并据此修改了模型和全部文档，见第 4、5、6 节。
    - 状态：**CFD 仿真暂缓，用户重新提出前不要开始。**

### 从以上指令归纳出的长期规则

- 遵守附录 A 的 AGENTS.md：
  - 先把核心做通；
  - 结论直接陈述，不加没有依据的限定语；
  - 报告以结果开头，不罗列没做的事；
  - 不加用户没要求的工作。
- 对用户用中文，"说人话"但不降低深度和准确性。
- 论文草稿用英文。这是前一个 AI 的默认做法（HiMCM 论文用英文），用户没有提出异议。
- 每个阶段的交付物：
  - 可复现的代码；
  - `outputs/` 下的图表和 CSV；
  - 中文 `README.md`；
  - 英文论文节草稿 `section_*_draft.md`。
- **文档里的每个数字必须和输出文件一致**，前一个 AI 每次都逐项核对过。
- 可以联网搜索、读知识库、做程序模拟。查到的数据要写明来源，并标明是看过原文还是只看了搜索摘要。
- 只推送到工作分支。

---

## 3. 阶段命名（注意，前后改过）

前一个 AI 最初给的计划是：阶段 0 读题定框架；阶段 1 第 1 问；阶段 2 第 2a 问；阶段 3 第 2b 问；阶段 4 第 3 问；阶段 5 第 4 问；阶段 6 第 5 问。

用户后来把 2b 叫作"阶段二b"，仓库里现在统一用下面的名字：

| 需求 | 论文章节 | 阶段名 | 状态 | 目录 |
|---|---|---|---|---|
| 1 冷柜效率该包含什么 | 3 | 阶段一 | 完成 | `himcm2026B/stage1/` |
| 2a 公交站效率指标 | 4 | 阶段二a | 完成（已按阶段一修订） | `himcm2026B/stage2/` |
| 2b 火车站候车区修订模型 | 5 | 阶段二b | 完成 | `himcm2026B/stage2b/` |
| 3 推广到真实场馆 | 6 | 阶段三 | 未开始 | — |
| 4 效率 → 效果 | 7 | 阶段四 | 未开始 | — |
| 5 指南、备忘录、博客 | 8 + 附页 | 阶段五 | 未开始 | — |

阶段 0（读题、统一定义、需求表）的内容在 `himcm2026B/README.md`。

---

## 4. 当前进度

### 仓库结构

```
himcm2026B/
  README.md                    总览：统一的效率定义、需求与进度、运行命令、主要结论
  data/
    README.md                  全部数据的来源与核实等级（原文核实 / 摘要 / 未核实）
    weather/                   ASOS 实测逐时气象（PHX、IAH，2020–2024 夏季）和 hot_days.py（生成设计日）
  stage1/                      第 1 问：敞口冷柜
    freezer.py                 冷柜热平衡模型、检验、表 S0–S4、图 S1–S2
    README.md                  中文说明（结论、冷柜与公交站对照表、公式、结果、来源）
    section_1_draft.md         论文第 3 节英文草稿
    outputs/
  stage2/                      第 2a 问：公交站；这里的模块被所有阶段共用
    psychro.py                 湿空气：饱和水汽压、含湿量、湿球温度、蒸发冷却出风状态
    model.py                   设备、冷量稀释（体积 / 定点）、客流、UTCI、缓解量、效率、冷量去向、遮阳
    run_stage2.py              表 0 检验、表 1、表 2 设计日、表 5 决策规则、表 6 设计手段、图 1–4 和图 7
    sensitivity.py             表 3 单因素敏感性（图 5）、表 4 蒙特卡洛（图 6）
    plotstyle.py               统一图形样式与设备颜色
    requirements.txt           numpy, pandas, matplotlib, pythermalcomfort
    README.md、section_2a_draft.md（论文第 4 节）
    outputs/
  stage2b/                     第 2b 问：车站
    station.py                 随时间变化的热湿平衡模型（10 s 步长）
    run_2b.py                  检验、逐项修订对比、四种场景、开放度扫描、空调容量与送风方式、敏感性、图 8–11
    README.md、section_2b_draft.md（论文第 5 节）
    outputs/
```

### 统一的效率定义（各阶段共用）

> 冷却效率 = 送达目标的有用冷却服务 ÷ 投入的全部资源，系统边界须事先说明。

- **冷柜：**
  η_F =（可取货陈列面积 × 营业小时 × [商品 ≤ −18°C] × 取货便利系数）÷（冷柜用电 + 商场空调净变化），单位 m²·h/kWh。
- **公交站和车站：**
  η =（受益人数 × 按热应激等级加权的 UTCI 缓解量）÷（用电 + 水的隐含能耗 0.53 kWh/m³），单位 人·°C·h/kWh。
  - 加权剂量 D(U) = ∫₂₆^U w(u) du，权重 w = 1 / 2 / 3 / 4，对应 UTCI 26 / 32 / 38 / 46°C 起的四个热应激等级。
  - 每人缓解量 R = D(U_before) − D(U_after)。
  - 车站的 U_before 是"同一车站不开冷却"时的值，它可能比室外更热。

### 各阶段的结论与检验

| 阶段 | 主要结论 | 检验 |
|---|---|---|
| 一 | 敞口冷柜 87% 的冷量耗在开口上（渗入 75% + 辐射 12%）；除霜占用电 17%；商场从 21°C/40% 变到 27°C/70%，用电 ×1.50；夜帘省 22%，玻璃门省 58%；DOE 现行限值中卧式每平方英尺只有立式的 1/4；计入商场空调后，净能耗在制冷为主的商场 −27%、采暖为主的商场 +7%；加门的盈亏平衡点是每天 8.95 美元毛利 | 4/4 通过：加门降幅与 SCE、Hillphoenix 测试一致；低于 DOE 现行限值 145.5 kWh/天；结霜能量守恒 |
| 二a | 湿热天风扇最好，效率是蒸发冷却的 3–10 倍；干热天（≥ 36°C 且干湿球温差高于约 14–20°C）风扇有害（实测凤凰城高温日 12–21 时都有害）；干热高峰 B、C 在人少时几乎打平，人多（≥ 8）时 C 更好（蒙特卡洛 C 64%）；蒸发冷却器的冷量只有 20–28% 吹到人身上；遮阳顶棚的日缓解量（干热 896 人·°C·h）超过 B（655）且零能耗；46.4°C 高峰时 B、C 都无法让人脱离 UTCI ≥ 38 | 14/14 通过：湿球温度、能量守恒、风扇标定、风扇效果与 Morris 2019 和 Ravanelli 2015 的真人实验一致、混合模型极限等；蒙特卡洛 3000 组 |
| 二b | 开放度决定设备：湿热天开放度高于约 8% 时风扇最好；干热天开放站台 C 最好、封闭车站 B 最好；屏蔽门站台和封闭候车室里蒸发冷却的湿度达 66–97%，违反 ASHRAE 62.1-2022 附录 e §5.13.1（蒸发冷却运行时 ≤ 65%），所以只能用空调；封闭但不开冷却的车站比室外热 0.9–5.6°C；低位送风让空调效率高 36–50%；开放度 ≥ 50% 时 2a 模型对蒸发冷却效率的误差在 10% 以内，开放度 3% 时低估 17–36% | 4/4 通过：与 2a 嵌套一致（39.33 = 39.33°C）、时间步长收敛、空调 COP 与 AHRI 一致、密闭极限；6 个参数的敏感性分析不改变最优设备 |

完整数字见各目录的 `README.md` 和 `outputs/*.csv`。

### 关键代码接口（续做时会用到）

- `model.Params` / `model.DEVICES` / `model.devices_for(p)`：2a 的全部参数和设备；风扇风速在 `devices_for` 里按额定 3°C 标定。
- `model.evaluate(dev, T, RH, v_w, n_mean, p, mode)`：单工况计算，可以用数组批量算；返回效率、缓解量、耗水、冷量去向等。
- `model.utci`、`model.stress_dose`、`model.sun_factor`、`model.shade_relief`。
- `station.Station`（几何、开放度、各项修订开关）、`station.System`（风扇、蒸发冷却、空调）、`station.simulate(st, sysm, climate)`、`station.run(...)`，以及 `station.blend(t)`（开放度 0–1 连续插值）。
- 设计日：`stage2/run_stage2.py` 从 `data/weather/july_profiles.csv` 读取实测高温日；`weather(climate, hour)` 给出任意时刻的气温、相对湿度和人体高度风速，`peak(climate)` 给出最热时刻的状态。车站的 `station.outdoor()` 也调用 `weather()`。换城市时，先用 `data/weather/hot_days.py` 生成新曲线。

---

## 5. 剩余工作

开始前先确认用户的最新指令。用户习惯一次指定一个阶段；不清楚要做哪个阶段时，先问。

### 阶段三：第 3 问（推广到至少两个真实场馆）

题目要求：说明模型能否推广；至少用两个场馆，气候不同或冷却方式不同；比较各场馆的冷却效率，找出最影响效率的特征。

前一个 AI 的建议做法：
- 把 `station.py` 当作通用"场馆模型"复用：几何、开放度、客流、设备和气候都是参数。2b 已经证明它包含公交站这个特例。
- 候选场馆：
  - 干热地区的户外餐厅露台（喷雾或蒸发冷却），对比湿热地区的露台（风扇）；
  - 炎热地区体育场的座椅或通道定点送风，对比开放式车站。
- 场馆尺寸、客流和设备配置应查公开资料；查不到的要作为假设写明。
- "最关键特征"建议用全局敏感性分析（如 Sobol 方差分解）排序。候选特征有：开放度、射流是否对准人、干湿球温差、占用率、遮阳。二a 和 二b 已经显示这几项比设备型号更重要。
- 气象数据换成实测逐时数据（NOAA ISD 或 Meteostat）。

### 阶段四：第 4 问（效率 → 效果）

题目要求：高效率不等于最有效；要权衡冷却性能、访客体验、能耗和成本，并说明模型如何处理这些相互冲突的目标。

已有的素材：
- 安全指标：UTCI ≥ 38 的人·小时（各阶段表格里都有）；
- 湿度上限 65%；
- 耗电、耗水；
- 二a 里"效率与效果分歧"：46.4°C 高峰时 B、C 都无法让人脱离 UTCI ≥ 38，C 把全天"非常强热应激"人·小时减少 40%，B 只减少 14%；
- 二b 的空调容量表：凤凰城的屏蔽门站台 120 kW 也压不住高峰，封闭候车室需要 120 kW；休斯敦 30–60 kW 就够；
- 二b 的湿度约束：ASHRAE 62.1 §5.13.1 排除了封闭车站里的蒸发冷却。

还需要补的：
- 成本数据：电价、水价、设备投资、维护费，用资本回收系数把投资折算成年成本；
- 体验指标：湿闷、喷雾打湿衣服、噪声。

建议做法：
- 把安全作为硬约束，再画成本–舒适的帕累托前沿；
- 研究分级控制策略：遮阳 → 风扇 → 蒸发冷却 → 空调避暑点，按温湿度切换；
- 二b 里车站的风扇按高峰配置且全天开启，效率因此偏低，按人数分区开关可以作为一条策略。

### 阶段五：第 5 问（指南、备忘录、博客）

- 运营指南：讲清如何在舒适、可持续、成本和安全之间取舍，尤其是极端高温期间。
- 给 COO 的备忘录：1–2 页，针对一个场馆，包含主要发现和可执行建议。
- 面向公众的博客：回答"我们用的能量换来了多少凉快？"。现成素材有冷柜和开着的冰箱门类比、"冷量只有 20–28% 吹到人身上"、"干热天一个遮阳顶棚比一台蒸发冷却器 B 带来的缓解还多"。
- 写法参考知识库的 `himcm-modeling/guides/writing/non-technical-deliverables.md`。

### 论文整合

- 已有英文草稿：第 3 节（Q1）、第 4 节（2a）、第 5 节（2b）。
- 还缺：
  - 摘要页、目录；
  - 引言和问题重述；
  - 总的假设与符号表，可以按第 6 节的"设定的假设"逐条整理；
  - 第 6–8 节、优缺点、参考文献、AI 使用报告。
- 25 页上限很紧，要尽早压缩。
- 写完后用知识库的 `himcm-modeling/guides/review-checklist.md` 自查。

### 提交前必须处理的数据问题（第 16 条指令后的状态）

已经解决：

- 设计日已换成 ASOS 实测高温日，见 `himcm2026B/data/`；
- DOE 现行系数已核实为 2.2 / 0.55；
- 渗入比例、Hillphoenix 加门数据、新西兰试点、JAMA 引用信息、日晒平均辐射温度、水的隐含能耗、ASHRAE 62.1 的 65% 条款都已打开原文核实；
- "RH 20% 时 42 / 45°C"原文中不存在，已改用 Morris 2019 和 Ravanelli 2015 的真人实验数据点检验；
- ACEEE 2009 链接原来张冠李戴，已改为正确出处。

仍然未核实：

1. "负荷降 68%"只有 ProQuest 摘要（SCE 测试中心），没有读到原文。
2. ISO 23953 气候等级 3 = 25°C / 60%：标准样章里没有这张表。
3. UTCI 等级（Bröde 2012）、ASHRAE 72 开门程序、AHRI EER、蒸发冷却器规格只看过摘要或供应商页面。
4. 凭记忆写的引用信息：Tartarini & Schiavon 2020（SoftwareX 12:100578）、Stull 2011（JAMC 50:2267–2269）、Middel & Krayenhoff 2019 的期刊信息。
5. DOE 2025 年 1 月的新规则（联邦公报网站被拦截）。
6. 屏蔽门节能 15–30% 是二手说法，只能作背景。

逐条状态见 `himcm2026B/data/README.md`。

---

## 6. 数据来源（前一个 AI 回答用户第 9 条指令的内容）

**以 `himcm2026B/data/README.md` 为准**，它是最新、逐条标了核实等级的版本。下面是第 9 条指令时的五类划分，之后的变化是：设计日已换成 ASOS 实测数据；水的隐含能耗改为 0.53 kWh/m³（ACEEE 2009，原文核实）；风扇检验改为对照真人实验数据点。

输入分五类：

1. **题目给的：** 只有设备表（0.25 / 1.2 / 2.5 kW；体感降 3°C，气温降 5 / 8°C）。
2. **联网检索得到的**（只看过搜索摘要，链接在各 README 的"资料来源"一节）：
   - UTCI 热应激等级；
   - 风扇失效阈值；
   - 蒸发冷却器规格，来自供应商产品页；
   - NWS 气候常年值；
   - 冷柜渗入比例和加门效果；
   - DOE 2009 能效系数；
   - ASHRAE 72 开门程序；
   - Gosney–Olama 公式；
   - 水的隐含能耗；
   - 坦佩平均辐射温度实测；
   - AHRI 额定工况与 EER；
   - 屏蔽门节能，二手说法。
3. **凭已有知识直接用、本次没有联网核实的：**
   - 湿空气公式与物性常数，Stull 公式；
   - 门洞浮力换气公式的具体形式；
   - 射流稀释公式、利特尔定律、对数风廓线；
   - 用 45% 卡诺效率估算空调 COP；
   - ISO 23953 气候等级、−18°C、ASHRAE 62.1 的 65%、电价 0.13 美元/kWh；
   - UTCI 用 pythermalcomfort 计算。
4. **前一个 AI 设定的假设：** 尺寸、各种系数、客流、设计日温湿度等，完整清单和取值依据见各 README 的"参数表"，做过敏感性分析的都标了。
5. **标定出来的：**
   - 风扇风速 2.93 m/s（由额定 3°C 反推）；
   - 蒸发冷却效率 ε 0.50 / 0.80（由额定温降和 D_ref = 10°C 反推）；
   - 冷柜渗入流量 0.053 kg/s（由文献区间中值 75% 反推）。

---

## 7. 工作规范

- **代码：**
  - 参数集中放在 dataclass 里，共用模块放在 `stage2/`，后续阶段继续复用，不要另写一份；
  - 遵守 AGENTS.md：出错直接暴露原始报错，不加没有理由的兜底和防御代码；
  - 改完运行 `python3 -m pyflakes`，保持无警告。
- **检验：**
  - 每个阶段都有检验表（`table*0*.csv`），并打印 PASS / FAIL；
  - 一个模型数字只拿来标定一次，另找独立数据做检验；
  - 检验没通过时要找原因，不能为了通过去调参数。前一个 AI 遇到过两次，都是在找到建模问题后才修正：加门检验改用了与文献一致的开门程序；车站模型补上了开口高度，并修正了恒温器控制。
- **图：**
  - 用 matplotlib，调用 `stage2/plotstyle.py`，220 dpi；
  - 设备颜色固定：A `#2a78d6`（蓝）、B `#eb6834`（橙）、C `#1baf7a`（青绿）、D 空调 `#6250d6`（紫）；
  - 不用双 y 轴，网格线要淡；
  - 出图后一定打开看一遍，检查文字重叠和图例遮挡。
- **文档：**
  - 中文 README 以结论开头，再写模型、参数表、结果、检验、来源；
  - 英文草稿按论文章节编号；
  - 写完逐项核对数字和 CSV 是否一致。
- **复现：** 从头重跑全部阶段，预期 PASS 数为阶段一 4 项、二a 14 项、二b 4 项。

```bash
cd himcm2026B/stage1 && python3 freezer.py > outputs/freezer_log.txt
```

```bash
cd himcm2026B/stage2 && python3 run_stage2.py > outputs/run_stage2_log.txt && python3 sensitivity.py > outputs/sensitivity_log.txt
```

```bash
cd himcm2026B/stage2b && python3 run_2b.py > outputs/run_2b_log.txt
```

  耗时：阶段一约 2 秒，二a 约 25 秒，二b 约 90 秒。
- **提交：**
  - 按所在环境的署名要求写提交信息；
  - 不要在提交、文件或论文里写模型版本号；
  - 只推送到工作分支。

---

## 8. 环境说明

- 新容器需要先安装依赖：

```bash
pip install -r himcm2026B/stage2/requirements.txt
```

- **网络：**
  - 能连上：Iowa Environmental Mesonet（ASOS 实测数据，本项目在用）、NOAA NCEI 接口、Open-Meteo（早先被拦截，后来能用了）、govinfo.gov（联邦法规原文）、WebSearch；
  - 连不上：ecfr.gov 和 federalregister.gov 会被重定向到拦截页；core.ac.uk、RSC 返回 403；部分网站返回 503；
  - 网页读取工具读 PDF 常常只能读到前一部分。它把原始文件存到本地后，用 `pdftotext` 自己提取全文更可靠；
  - **不要用伪装浏览器标识的 curl 绕过网站的机器人限制**，自动模式会拒绝，也不应该这样做。
- **知识库：** `moiddales/qwerty` 是公开仓库，可以匿名克隆。

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 -b claude/affectionate-mayer-ihqczh https://github.com/moiddales/qwerty /home/user/moiddales/qwerty
```

  有用的入口：
  - `himcm-modeling/SKILL.md`；
  - `guides/problem-analysis-and-direction.md`、`guides/modeling-workflow.md`（检验与敏感性）；
  - `guides/model-catalog/`；
  - `guides/writing/`（摘要页、结构、非技术稿件）、`guides/review-checklist.md`；
  - 相关题卡：`problems/2018B.md`（智能温控）、`2021A.md`（传热）、`2024B.md`（能耗估算）、`2023B.md`（全生命周期成本）、`2019A.md`（公共设施成本效益）。
  - 知识库里没有 2026 年的论文，卡片是摘要，引用前要回原文核对。
- **题目 PDF：** 原始上传在 `/root/.claude/uploads/` 下，新容器里可能已经没有了。B 题全文见附录 B。A 题（为高中生评选最佳城市）用户没有选，不需要。

---

## 附录 A：用户的项目准则 AGENTS.md（原文照录）

用户在第 5 条指令里提供了这份文件，并要求作为项目准则遵守。

````markdown
# AGENTS.md

Working style for every task in this workspace. The user's explicit instructions in the current conversation take precedence over this file and over any skill file.

## The reader

The user is a collaborator who wants the problem solved and will act on your answer. Nobody scores you on how many risks, caveats, or checks you mention. Aim for the correct result by the shortest path, stated plainly.

When a request has an obvious most-likely reading, take it and proceed; state the assumption in one line only if it changes the result. For reversible local work (reading files, editing in-scope code, running tests), proceed without asking. Ask first only before external writes, destructive or irreversible actions, spending money, or expanding the scope.

## Solve the core problem first

1. Identify the one thing the request is about and make it work end to end before touching anything else.
2. Build the simplest approach that meets the requirement. Add an LLM call, a database, a server, a framework, or another moving part only when the requirement needs it.
3. Before writing new code, stop at the first option that works: not needed → skip it; already in the codebase → reuse it; standard library or platform feature → use it; installed dependency → use it; otherwise write the minimum that works.
4. Fix the done condition before you start: an observable fact such as "the failing test passes" or "the page lists the items". When it holds, run the ablation pass below, then report and stop. No extra polish pass, refactor, review round, or verification loop beyond that.

## Edge cases: three-question filter

Write code for an edge case only if at least one of these is true:

1. The user, a spec, an issue, or an existing test names it.
2. Existing code, data, or types show it actually happens, and you can point to the file, line, or record.
3. Leaving it unhandled would lose or corrupt data, expose secrets, or open a security hole at a real trust boundary (user input, network, external files, auth).

Every other edge case gets no code and no mention. One exception: if an unhandled case is likely to hit the user soon, name it in one line at the end of the report.

## Fail fast; skip speculative defenses

Silent fallbacks hide whether the real code path works and turn bugs into wrong answers.

- Let unexpected errors surface with their original message. Catch an exception only to add context and re-raise, or when the user asked for degraded behavior.
- No silent fallbacks: when the real path fails, do not switch to a simpler method, placeholder data, a cached value, or a hard-coded default.
- Validate at trust boundaries and trust internal invariants. Skip re-checking what the caller or the type system already guarantees: no `None` checks on values that cannot be `None`, no `getattr(obj, "x", None)` for attributes that always exist, no `isinstance` checks on your own function's arguments.
- Each of these needs a reason from the three-question filter before you add it: retries, checksum or SHA-256 verification, locks, allow/deny lists, approval gates, freezes, feature flags, config switches, rollback scripts, backward-compatibility shims, CI workflows, new abstraction layers, new dependencies.
- If you catch yourself adding guards around a race or a crash inside your own code, fix its cause in the design.

Ablation pass before you report: go through every guard, fallback, validation, abstraction, and test you added, and delete each one whose removal breaks nothing covered by the three-question filter.

## Tests and verification

- Run the existing tests and checks relevant to the files you changed.
- Add a test only for behavior the user cares about: the bug you fixed or the main path of a new feature. Skip tests that restate the implementation, and skip smoke tests and hash checks for small changes.
- Budget for a small change (one or two files, roughly under 50 changed lines): one verification run. Rerun only after a new edit or a new failure.
- If a check you would normally run could not run, write "not run: <check>" once in the report.

## When the user removes or rules out something

When the user says to drop, remove, or avoid something (an LLM call, a library, a feature, a step):

- Remove everything that existed only to serve it: code, imports, dependencies, config keys, flags, environment variables, tests, docs, and UI text. Keep no switch, stub, or fallback that could bring it back.
- Leave the product and plans (code, identifiers, comments, UI text, docs, plans, config) reading as if the thing had never been proposed. Name each part by what it does: `grade_by_rubric()`, 「作文批改」. Write nothing that points at the absence: `grade_without_llm()`, `USE_LLM = False`, `# LLM removed per user request`, "LLM-free mode", 「作文批改（无LLM版）」「纯规则版」「无依赖版」「本版本不使用……」.
- In your reply, confirm in one plain line that describes the new state (「评分改为按评分细则匹配；改了 scoring.py、gui.py」). In this and later messages, skip explaining why the removal is better, why the thing was there, or that it is now gone.

The removed thing was never a requirement. A label about its absence keeps it alive in the docs and UI, and later readers and agents take it as a default to restore.

## Say it straight

- State facts as plain declarative sentences. When a statement holds in every case the user will realistically meet, write it as a rule: "always", "never", "use X", "this is the cause". Rules of thumb that are right in the overwhelming majority of real cases and save the user time also go in as rules; add a known exception in one clause only if it would change what this user does.
- When you are unsure and can check (run the code, read the file, search), check first, then state the result.
- When asked for a gist or an estimate, give your best estimate with a number or a direction, plus the main reason. The absence of a study on the exact case does not justify withholding it.
- A qualification is allowed only when you can name its concrete source: a failing test, a missing input, a version difference, a documented exception, a measured limit. Put it once, next to the claim it limits, in one clause. Drop any qualification whose source you cannot name. Ungrounded qualifications make the text longer and the conclusion harder to find while telling the reader nothing.
- Unless the user is about to rely on exactly that unsupported inference, leave these out:
  - "not shown" statements: "this does not by itself establish…", "should not be read as…", 「这并不能说明……」「不应被理解为……」「不能当作……」;
  - scope phrases that soften a claim you would otherwise state as a rule: "in the tested settings", "in most cases", "generally", 「在一定程度上」「某种程度上」「通常情况下」 (a frequency that is the actual finding, such as "usually" or "in about 80% of runs", is fine);
  - stacked hedges: "may potentially", "could possibly", 「可能或许」「也许在某些情况下」;
  - warnings and disclaimers about hypothetical risks the user did not raise, including 「仅供参考」「请谨慎使用」.
- Real risk stays in. If an action can delete data, cost money, break production, or expose secrets, say so in one plain sentence before doing it.

Examples:
- 「在大多数较新的 Python 版本中，dict 通常会保持插入顺序，但这可能取决于具体实现。」→「Python 3.7 起 dict 保证插入顺序。」
- "Force-pushing might potentially cause issues for collaborators in some cases." → "`git push --force` replaces the remote branch with yours; commits on the remote that are missing from your local branch disappear from it."
- "There is insufficient evidence to establish a percentage improvement for this specific road." → "Widening usually relieves congestion at first; within about 5–10 years induced demand brings it back near the old level."

## Say what things are

Describe what something is. Use "not X, but Y" only when X was actually said or assumed by the user, the code, or a source you cite, so you are correcting a real misunderstanding. Otherwise delete the "not X" half and keep Y. An invented X makes the reader process a claim nobody made.

Rewrite these when they introduce an X nobody raised:
- English: "It's not X, it's Y" / "X, not Y" / "X — not Y" / "not just X but Y" / "rather than X" / "This isn't about X. It's about Y."
- 中文：「不是X，而是Y」「这不是X，是Y」「X，而不是Y」「与其说X，不如说Y」「不只是X，更是Y」「并非X」「X并不意味着Y」「不能简单地把X当作Y」「这不代表……」（繁體中文同理）

Examples:
- 「这不是性能问题，而是逻辑问题。」→「第 42 行的循环条件写反了。」
- "This isn't a parser bug; it's a config issue." → "`strict=false` in config.yaml causes it."

## Reviewing and revising

- Judge every finding against how the project is actually used (a single-user local script, an internal tool, a public service). Report what would cause a wrong result, data loss, or a security hole in that setting; drop findings that need a scenario the setting rules out. Rate severity by that setting.
- When revising someone's text, keep their claims at their strength. Change a claim only when you can point to the specific evidence that contradicts it, and name that evidence.
- A review or revision adds no new caveats, disclaimers, or "not shown" statements.

## Reports and final messages

- Lead with the result: the answer, or what changed and where. Then anything the user must do.
- Report what you did. Leave out what you did not do, what stayed unchanged, and what the change "is not", unless the user asked.
- Skip openers, closing summaries ("In short", 「总之」「一句话总结」), and offers of more help.
- Length follows content: a one-line fix gets a one-line report.

## Last step before sending: delete-only pass

Remove ungrounded qualifiers, invented "not X" halves, unrequested disclaimers, lists of things you did not do, and any trace of removed items. This pass only deletes and tightens; it adds no caveats, checks, or tests.

## If an instruction file gets in the way

If any instruction file (this one, another AGENTS.md, or a skill) makes you pause, ask for approval, or add work the user did not request, quote the line responsible in one sentence so the user can fix the file.
````

## 附录 B：2026 HiMCM Problem B 题面（从官方 PDF 提取的文本）

```text
2026 HiMCM
Problem B: Air Conditioning the Environment: Modeling Energy Waste in Public Cooling

Image Credit: Adobe Express

Background
Everyone knows it is wasteful to leave the door of the freezer open. As cold air escapes and
warm air enters, the freezer must use additional energy to maintain the desired temperature. Yet
many modern public spaces do not follow this principle, as they intentionally expend energy to
cool areas that are not fully enclosed. Open-air venues, like stadium concourses or concert
amphitheaters, and, semi-open public spaces, like transit stations, airport terminals, and public
waiting areas, use cooling systems to keep customers comfortable and safe, despite constant
exposure to the surrounding environment. In these settings, some of the cooling reaches its
intended audience, while some dissipates into the atmosphere.
As cities become warmer, energy costs increase, and extreme heat events become more frequent,
venue operators face a difficult challenge trying to provide comfortable and safe environments
while using energy responsibly. Determining whether a cooling strategy is effective requires
more than measuring temperature alone. Factors such as facility design, crowd size, weather
conditions, airflow, operating costs, and visitor comfort and safety all play a role.
The Heat impact Mitigation through Cooling Management (HiMCM) team that manages both
open-air venues and semi-open public spaces is reevaluating its cooling practices and wants to
understand how efficiently its systems deliver useful cooling to visitors. Because conditions vary
across facilities and climates, the company seeks a general framework that can be used to
compare different cooling approaches and identify opportunities for improvement.
Your team has been hired by HiMCM to investigate the problem. Develop a mathematical model
to evaluate the effectiveness of cooling systems in both open-air venues and semi-open public
spaces and provide recommendations for balancing comfort, safety, energy consumption, and
cost.

Requirements.
1. Understand the Problem. Open freezer cases in grocery stores continuously use energy
to remove heat from food and the surrounding air. What aspects of a freezer case should
be considered when measuring cooling efficiency? Should efficiency depend only on
energy use? Justify the quantities that should be included in a measure of cooling
efficiency. Use your response to motivate the design of your cooling efficiency models
below.
2. Create Your Model. A city is looking for ways to keep people comfortable while they
wait for public transportation by bus or rail on hot summer days.
a. For the bus, one proposal is to install a cooling system in an open-sided bus stop shelter.
City planners want to determine which system is the most efficient, but at this time, only
know the following:
Effect on Shelter

Energy Use

A. Fan System

Makes space feel up to 3°C cooler

0.25 kW

B. Evaporative Cooler

Lowers air temperature up to 5°C

1.2 kW

C. Large Evaporative Cooler

Lowers air temperature up to 8°C

2.5 kW

Cooling System

Develop a measure of cooling efficiency for the bus stop. You may want to consider
factors, including, but not limited to, the size of the cooled area, climate conditions,
energy use, and the number of people benefiting from the cooling.
b. For a semi-open rail-station waiting area, revise and improve your model as necessary to
measure cooling efficiency. Clearly explaining what changed, why the change was
necessary, and how the revision improved the model’s usefulness or accuracy.
3. Apply Your Model. Does your cooling efficiency model scale? Apply your model to at
least two specific venues. Ensure these venues are in different climates or that they use
different types of cooling systems to demonstrate the robustness of your model. Possible
case studies include:
•

Stadium concourses,

•

Concert amphitheaters,

•

Outdoor restaurant patios,

•

Open-air airport terminals in warm climates,

•

Open walkways in outdoor malls, or

•

Other open-air venues or semi-open public spaces.

You may use real-world data or reasonable estimates with assumptions when real-world data
is not available. Use your model to compare the efficiency of cooling strategies across venues
and identify the characteristics that contribute most to efficient cooling.
4. Expand Your Model and Reflect on Your Analysis. A cooling solution that is highly
efficient may not be the most effective overall. Extend your model to evaluate cooling
effectiveness by balancing cooling performance, visitor experience, energy consumption and
cost. Clearly describe how your model accounts for these competing objectives.
5. Share Your Model and its Results. Propose guidelines for the use of cooling systems in
your venues. Discuss strategies for how operators can balance visitor comfort, sustainability,
and cost while maintaining safe and effective environments during periods of extreme heat.
a. Prepare a one-to-two-page memorandum to the Chief Operations Officer of HiMCM
about one of your chosen venues. In your memorandum, summarize your major findings
and provide actionable recommendations regarding the use of cooling systems for that
venue. Your recommendations should address balancing the trade-offs of cooling
effectiveness.
b. Create a blog post that HiMCM can use to explain these results to the public. HiMCM
wants to educate the public surrounding the question of “How much cooling are we
getting for the energy we use in these open-air venue or semi-open public spaces?”.
Your PDF solution of no more than 25 total pages should include:
•
•
•
•
•
•

One-page Summary Sheet.
Table of Contents.
Your complete solution.
One-to-two-page memorandum to the Chief Operations Officer.
References list.
Report on Use of AI Tools (If used does not count toward the 25-page limit.).

Glossary:
Open-air venue – a place where events are held primarily outdoors and are exposed to the
surrounding environment rather than being enclosed by walls and a roof.
Semi-open public space – a publicly accessible area that is partially enclosed by roofs, walls or
other structures while still allowing for a significant air exchange with the outdoors.

Open freezer case – a refrigerated display used in grocery or convenient stores that keeps
products cold while remaining open to the surrounding air, allowing customers to easily view
and access items without opening a door.
Bus Stop – A designated roadside location where a bus briefly halts to let passengers get on or
off.
Evaporative cooler – cooling device that lowers air temperature by passing warm air through
water-soaked pads. As the water evaporates, it absorbs heat for the air, producing cooler air that
is then circulated by a fan, using less energy than traditional air conditioners.
Climate conditions – could include latitude or location, temperature, humidity, solar exposure or
wind.
Blog post – an article or piece of written content published on a website.
```
