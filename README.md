# arcgis-pro — ArcGIS Pro 地理数据处理技能

> 一个让 [Claude Code](https://claude.com/claude-code) 用本机 **ArcGIS Pro / GeoScene Pro** 自带的 Python（**arcpy**）直接处理地理数据的技能，主打 **声明先行、三种执行模式、按模式确认**，把 GIS 批量处理从"手动点工具"变成"自然语言对话"。

---

## 目录

- [安装](#安装)
- [总体介绍](#总体介绍)
- [快速开始](#快速开始)
- [支持的能力范围](#支持的能力范围)
- [仓库文件说明](#仓库文件说明)

---

## 安装

### 前置要求

| 依赖 | 说明 |
|------|------|
| **ArcGIS Pro** 或 **GeoScene Pro** | 自带 `arcpy` 解释器。 |
| **Spatial Analyst 扩展许可** | 仅使用栅格空间分析工具（坡度、掩膜提取、重分类、欧氏距离等）时需要；纯数据管理/格式转换不需要 |
| **Claude Code或其他AI Agent** | 用于加载并运行本技能 |

### 克隆技能

将仓库克隆到 Claude Code 的技能目录：

```bash
git clone https://github.com/yiyu1117/arcgis-pro-skill.git ~/.claude/skills/arcgis-pro
```

### 首次安装配置（一次性）

安装后**首次使用前**，搜索本机 arcpy 解释器路径并填入技能目录的 `config.json`：

1. 查询注册表 `HKLM\SOFTWARE\ESRI\ArcGIS Pro`；
2. 检索常见安装路径下的 `*Pro/bin/Python/envs/*/python.exe`；
3. 将找到的 `python.exe` 完整路径写入 `config.json` 的 `python_path`（可复制 [`config.json.template`](config.json.template) 后修改）。

**之后每次运行直接读取 `config.json`，不再重复检测。** 仅当路径失效（文件不存在 / `import arcpy` 失败）时重新检测。`config.json` 已被 `.gitignore` 忽略，不会进入仓库。

---


## 总体介绍

### 这是什么？

`arcgis-pro` 是安装在 Claude Code 里的一个技能（Skill）。当你用自然语言描述一个 GIS 任务——比如"把这 20 个 shp 转成 geojson"、"按这个行政区边界裁剪 DEM"、"算一下每个学校的 500 米缓冲区"——Claude 会调用本机 ArcGIS Pro（或**GeoScene Pro**）自带的 `arcpy` 解释器，在磁盘上直接完成数据处理，全程不需要手动打开 Pro 界面点工具。

它面向的是**数据层面的自动化**：格式转换、坐标系转换、叠加分析、栅格处理、批量处理，一切能使用arcpy或写成脚本的活。

### 设计理念

技能把 ArcGIS 批处理的最佳实践固化成几条硬规则，让每次执行又快、又稳、又可复现：

1. **三种执行模式** —— 任务开始时由你选择：**单步**（每步停下确认，最稳）、**连续**（每步独立执行、阶段结束确认，常规推荐）、**合并（PTC）**（把一个阶段合成一个脚本跑，最快）；从其他任务唤起时默认连续，不打断父流程；
2. **声明先行** —— 每步操作前先显示 `【工具名】输入=…，参数=…`，你随时能核对它在干什么；
3. **计划先确认** —— 拆解出的计划先整体确认；之后按模式在每步或每个阶段暂停，不会闷头跑偏；
4. **多机器自适应** —— 解释器路径**首次安装时搜索一次并写入 `config.json`**，之后每次直接读取、不重复检测；ArcGIS Pro 与 GeoScene Pro 都支持（两者互斥、单机至多一个）；
5. **内置错误知识库** —— 常见 arcpy 报错的处置方法直接预存在技能内，报错即查即修；
6. **修复有伦理** —— 报错必须根治，禁止换工具凑合、跳过失败数据、降低精度让任务"通过"。

### 适用场景

- 格式互转：`shp / geojson / kml / gpx / csv / excel / gdb`
- 坐标系与投影：WGS84 / Web Mercator / CGCS2000（含 3 度分带）
- 矢量分析：缓冲、裁剪、属性选择、合并、空间连接
- 栅格处理：裁剪、镶嵌、重采样、坡度、按掩膜提取、重分类、欧氏距离
- 批量与脚本化：多文件循环处理、游标逐行读写、NumPy 数组运算
- 字段管理：添加字段、字段计算（含面积、长度等几何属性）

### 适用对象

- 用 Claude Code 工作、需要频繁处理地理数据的 **GIS 工程师 / 测绘 / 规划 / 环境 / 农业** 从业者；
- 本地已安装 **ArcGIS Pro** 或 **GeoScene Pro**，希望省去繁琐点击、把批处理交给对话完成的人。

---

## 快速开始

装好技能后，直接在 Claude Code 里用自然语言描述任务。技能会先拆解任务、给出 To Do 计划等你确认，然后询问执行模式：

- **单步**：每执行一步就停下报告，适合高风险操作；
- **连续**：每步独立执行但不逐步暂停，每个阶段结束停下确认，适合常规任务；
- **合并（PTC）**：把一个阶段合成一个脚本连续跑，速度最快，适合步骤多、逻辑明确的任务。

执行中随时可以说「切单步 / 切连续 / 切合并」切换模式。如果本技能是被其他任务中途唤起（例如别的流程里顺手处理地理数据），会默认连续执行、不打断父流程。具体规则见 `SKILL.md`。

**示例 1：格式转换**
> 把 `中国_省.geojson` 里的转为 shapefile ,提取河北省+投影到CGCS20003度带117E（图中为多任务处理的to do 1）。
> <p align="center">
  <img width="48%" alt="示例图1" src="https://github.com/user-attachments/assets/225f7850-c254-46e9-9ad8-159c6fae6232" />
  <img width="48%" alt="示例图2" src="https://github.com/user-attachments/assets/8dc655ac-537d-4192-95f8-a0e0e463b4c6" />
</p>

**示例 2：矢量分析**
> 对 `schools.shp` 做 500 米缓冲区，融合方式 ALL，输出到 `D:/data/过程/学校缓冲区`。

**示例 3：栅格分析**
> 把38幅DEM镶嵌之后，使用河北边界裁剪，并计算坡度。
> <img width="60%" alt="d7a7304f57c67cee501aad9a03dd66b9" src="https://github.com/user-attachments/assets/65838422-8fe9-4206-afc0-80ed8d4c7dd6" />


**示例 4：批量数据处理**
> 对于多项任务，技能会先读取数据确定文件和处理情况，拆分为多个To Do 计划来处理
> <img width="60%" alt="d1a38ee713fa7ed0eff7e04cb55173a7" src="https://github.com/user-attachments/assets/20f39387-4f36-4de5-a12a-ca1df7f87bdd" />


**示例 5：数据下载+处理**
> 对于需要下载的数据，技能会先在后台下载，下载完成后自动开始处理
> <img width="60%" height="1020" alt="image" src="https://github.com/user-attachments/assets/2ea8d77b-735a-46bd-926b-5ca7ff5277bd" />


---

## 支持的能力范围

技能内置了覆盖三大类约 30 个常用工具的**签名速查表**；冷门工具会通过联网搜索查官方文档（`site:pro.arcgis.com`）。

### 数据管理

缓冲、裁剪（矢量/栅格）、属性选择、投影（矢量/栅格）、定义投影、重采样、合并要素、镶嵌栅格、添加字段、字段计算、XY 转点、建文件 GDB 等。

### 格式转换

`shp → gdb`、要素 → geojson、geojson → 要素、`excel → 表`、`表 → excel`、`kml → 图层` 等。

### 空间分析（需 Spatial 扩展）

坡度、按掩膜提取、重分类、欧氏距离、栅格取整等。

### 游标 / NumPy

`SearchCursor` 逐行读取；`TableToNumPyArray` / `NumPyArrayToTable` / `NumPyArrayToFeatureClass` 完成表与数组互转，支持多行复杂逻辑。

**常用坐标系预置**：`4326 WGS84`、`3857 Web Mercator`、`4490 CGCS2000`、`4548 CGCS2000_3度带_117E`、`4549 CGCS2000_3度带_120E`（注意：4547=114°E、4550=123°E；编码一律以 `arcpy.SpatialReference(code).name` 实测为准）。

---

## 仓库文件说明

| 文件 | 作用 |
|------|------|
| `SKILL.md` | **技能主文件**：触发描述、执行流程、工具签名速查、错误处理、产物组织 |
| `CONTEXT.md` | **领域模型与设计动机**：解释器跨机器配置、核心概念术语表 |
| `verify_sigs.py` | 用本机 arcpy 官方 doc 核对 `SKILL.md` 工具签名表的脚本 |
| `config.json.template` | 解释器配置文件模板（本机实际配置写入 `config.json`，被 `.gitignore` 忽略） |


