# 2a 公交站模型

主入口 `run_stage2.py`；参数不确定性入口 `sensitivity.py`。当前数值见 outputs/ 与 ../paper/key_results.md；完整报告及英文节选暂缓发布，等待用户批准。

主模型以候车位置效果解释题目额定值。A 调速限制 UTCI 改善但仍计全额功率；B/C 旁通调节供气并重算水耗。`rating_policy="outlet"` 是额外情景，`uncapped` 仅供诊断。有效范围以 `pythermalcomfort` UTCI 限制为准，缺失值不能视作无风险。

平均人数通过 Little 定律估计；Poisson 占用以 `E[min(N, coverage)]` 计算受益人数。按需控制要求有人、热需求、正向效益。日间 MRT 增量是随日照变化的假设，非现场标定。应测局部风速、辐射和射流覆盖再作部署决定。

图 7 为覆盖/混合指数，不是“冷量百分之多少到人身上”。权重是无量纲效用选择，不是死亡风险拟合。Monte Carlo 输出是所选参数范围下的获胜份额，不是现实概率；完整采样网格、有效份额及负效益比例均保存。

运行：

```bash
python stage2/run_stage2.py
python stage2/sensitivity.py
```

`--render-only` 只重新绘制/汇总已有完整采样 CSV，不能在修改参数后冒充重新采样。真实天气日检查另见 `tools/robustness.py`。
