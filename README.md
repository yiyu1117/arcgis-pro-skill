# arcgis-pro — 地理数据处理技能

用本机 **ArcGIS Pro**（或 **GeoScene Pro**）自带的 Python（arcpy）处理地理数据的 Claude Code 技能。

## 安装

```bash
# 克隆到 Claude Code 技能目录（多台机器可各自克隆一份）
git clone https://github.com/yiyu1117/arcgis-pro-skill.git ~/.claude/skills/arcgis-pro
```

要求：已安装 ArcGIS Pro 或 GeoScene Pro（自带 arcpy；空间分析工具需要 Spatial Analyst 扩展许可，网络分析等同理）。

## 首次运行

技能自动检测本机的 arcpy 解释器路径（ArcGIS Pro 与 GeoScene Pro **互斥，单机至多一个**），检测结果写入技能目录下的 `config.json`（该文件是本机配置，不提交到仓库）。若路径失效，按 `SKILL.md`「解释器路径」一节重新检测。配置格式见 `config.json.template`。

## 工作方式

技能按三条铁律工作，保证每步可排查、结果可复现：

1. **一次只执行一步** —— 每个 arcpy 操作单独内联执行，不写长脚本（长脚本一出错就退出码 -1 且无 traceback，无法定位）
2. **声明先行** —— 每次操作前先显示【工具名】+ 参数供核对，无需确认
3. **确认后动手** —— 拆解出的计划先整体确认，每个 To Do 项完成后暂停确认

执行流程：拆解 → 计划确认 → 逐项执行（单步）→ 每项确认 → 快进（可合并中间步骤省 import 开销）。

产物组织：`过程/`（中间产物，语义命名子文件夹如"镶嵌后DEM"）+ `结果/`（最终成果）+ `_运行记录/`（audit + 跨会话决策日志）。

## 文件说明

- `SKILL.md` — 技能主文件：流程、工具签名速查、错误处理（含修复循环与修复伦理）、产物组织
- `CONTEXT.md` — 领域模型与设计动机
- `verify_sigs.py` — 用本机 arcpy 官方 doc 核对工具签名的脚本
- `config.json.template` — 解释器配置文件模板
