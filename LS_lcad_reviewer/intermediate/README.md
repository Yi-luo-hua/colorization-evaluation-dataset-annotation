# 过程与中间产物目录架构说明 (intermediate)

本目录用于统一归集图像上色评价工作流（V4 标准体系）执行过程中的所有初筛、看板、定物与辅助分析产物，严格禁止产物散落在项目根目录下。

---

## 目录结构索引

```
intermediate/
├── audits/                     # 批次初筛与定物映射数据（纯净 JSON）
│   ├── audit_needs_grounding_{start}_{end}.json   # CV 物理初筛报警待定物任务集
│   ├── audit_pass_{start}_{end}.json              # 物理自洽放行任务集
│   ├── grounding_reviews_{start}_{end}.json       # AI 视觉多模态直审与具象定物映射字典
│   ├── sheets_meta_{start}_{end}.json             # 高清三联看板卡片与任务元数据映射
│   └── scans/                                     # 历史批次底层色度扫描与物理采样归档
├── inspection_sheets/          # 高清三联对比看板图片（按批次分文件夹归集）
│   ├── inspection_sheets_{start}_{end}/           # 待改判高危样本三联看板 (sheet_*.jpg)
│   └── inspection_sheets_{start}_{end}_pass/      # Double Check 物理自洽样本复核看板
└── scripts/                    # 历史批次辅助分析、色度扫描与定物构建 Python 脚本
    ├── analyze_*.py                               # 批次特征与异常统计脚本
    ├── build_grounding_*.py                       # 批次具象定物字典构建脚本
    ├── find_severe_*.py                           # 高危硬伤快速初筛脚本
    ├── fix_grounding_*.py                         # 历史空缺陷样本专项修复脚本
    └── verify_deliverable_*.py                    # 批次交付成品完整性断言脚本
```

---

## 职责划分与规范准则

1. **`audits/` 纯净数据原则**：
   - 仅存放与下游 `build_stream_batch.py` 强依赖的 JSON 映射文件；
   - 严禁在此目录下混放临时 Python 脚本或日志文本。
2. **`inspection_sheets/` 批次隔离原则**：
   - 每张看板包含 6 组卡片（GT + LCAD + 2x 差分放大图）；
   - 图片按批次存入对应子目录，严禁在 `inspection_sheets/` 根目录平铺散落图片。
3. **`scripts/` 辅助工具归档原则**：
   - 记录各批次专项处理的代码逻辑，确保全流程具备可追溯性与复现性。
