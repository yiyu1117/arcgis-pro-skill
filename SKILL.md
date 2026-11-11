---
name: arcgis-pro
description: 使用本机 ArcGIS Pro / GeoScene Pro 自带的 Python(arcpy) 处理地理数据。当用户提及 GIS 数据处理、空间分析、shapefile(.shp)、geodatabase(.gdb)、要素类、坐标系、投影、缓冲区、裁剪、镶嵌、重分类、空间连接、栅格分析、DEM、坡度、字段计算、格式转换(shp/geojson/kml/gpx/csv/excel/gdb 互转)、arcpy、ArcGIS Pro、GeoScene、批量处理或任何地理/空间数据操作时触发。
---

# ArcGIS Pro 地理数据处理技能

用本机 **ArcGIS Pro**（或 **GeoScene Pro**）自带的 arcpy 处理磁盘上的地理数据。核心工作方式：**声明先行、按模式执行、按模式确认**。

## 三条铁律（违反任何一条 = 返工重来）

1. **声明先行**。调用任何操作前，必须先以正文输出声明，格式：
   `【工具名】输入=…，参数=…`
   例：`【缓冲区】输入=schools.shp，距离=500米，融合=ALL`
   声明后立即执行；单步模式在该步**结果报告后**暂停确认（不在声明与执行之间插停）。
2. **一次只执行一步**。单步/连续模式下，每个执行单元单独执行，**禁止**写一个大脚本一次跑完——长脚本把多个步骤混在一起，普通异常虽有 traceback 也难以定位到具体数据/步骤，原生崩溃时更只有退出码 -1、无 traceback。合并模式（PTC）是唯一例外：允许把一个 To Do 阶段写成一个脚本，但必须逐步骤标记、逐步骤异常捕获（见【执行模式】）。
3. **按模式确认**。计划在所有模式下都先整体确认（被其他任务唤起时除外）；之后按用户选择的模式暂停：单步 = 每步停，连续/合并 = 每 To Do 停。

## 执行模式（任务开始前确定）

| 模式 | 执行粒度 | 暂停点 | 适用 |
|------|----------|--------|------|
| **单步** | 每个执行单元独立进程 | 每个执行单元后停下等确认 | 高风险、需逐步核对 |
| **连续** | 每个执行单元独立进程 | 每个 To Do 阶段后停下等确认 | 常规任务，安全与速度平衡 |
| **合并（PTC）** | 一个 To Do 阶段合并成一个脚本 | 每个 To Do 阶段后停下等确认 | 步骤多、追求速度 |

### 如何选择模式

- **用户直接发起任务**：
  - 执行单元总数 ≥2 → 用 AskUserQuestion 提问（问题：执行模式；选项：单步 / 连续 / 合并（PTC）），**不预设默认值，用户选择后才开始**。
  - 执行单元总数 =1 → 不询问模式，计划确认后按单步执行，完成后确认结果并说明「单步任务，无需选择模式」。
  - 用户明确说「不用问，直接跑」→ 按连续模式。
- **从其他任务唤起**（本技能不是用户当前消息直接请求，而是被其他技能 / 工作流 / 子代理 / 执行计划调用，例如某个任务途中需要处理地理数据）：
  - 默认**连续模式**，不询问；
  - 输出简洁计划与每步声明后直接执行，**不阻塞等待计划确认或阶段确认**；
  - 完成后一次性报告；出错立即停下报告；
  - 父流程若有自己的确认点，以父流程为准。
- **中途切换**：用户说「切单步 / 切连续 / 切合并」时，从下一步生效。「切到合并」从下一个 To Do 阶段开始，当前阶段已执行部分不重写；「切走合并」立即生效。

### 各模式的执行要求

- **单步**：每步后报告（输出路径、要素数/文件大小/关键值），停下等用户确认，再走下一步。To Do 的最后一步确认即视为阶段确认，不重复暂停。
- **连续**：每步仍独立进程、仍输出声明，但**不逐步暂停**；每个 To Do 阶段结束报告并停下等确认（被其他任务唤起时不阻塞）。
- **合并（PTC）**：
  1. 阶段开始时，把该 To Do 的所有执行单元写成一个脚本：`{任务目录}/_运行记录/run_<阶段名>.py`；同时在正文列出该脚本的 `[STEP n]` 声明（脚本内 `print` 作为运行日志）。
  2. 脚本内每步先 `print("[STEP n] 【工具名】输入=…，参数=…")`，再用 `try/except` 包住该步；失败时打印 `[STEP n] FAILED: <错误>` 并 `sys.exit(1)`；
  3. 每步成功后打印校验信息（`arcpy.management.GetCount` / `arcpy.Describe`），便于阶段结束核对；
  4. 用 `"{python}" "<脚本路径>"` 执行，超时规则同【错误处理】；
  5. 脚本保留在 `_运行记录/` 作为可复现记录；
  6. 失败不自动回退：报告失败步骤，用户决定「重跑 / 转单步 / 转连续」。
- **口头「快进」**：用户说「这几步连跑」等价于切到合并模式（从下一个 To Do 阶段开始合并，当前阶段已执行部分不重写）。

## 执行流程（顺序执行，不可跳步）

```
拆解任务 → 计划确认 → 选择模式 → 逐项执行 → 按模式确认 → 完成
```

### ① 拆解
- 复杂任务先拆成 **To Do 项**，每项用内置任务工具（TaskCreate）创建，随执行更新状态（TaskUpdate）。
- 每个 To Do 项内部再分成若干**执行单元**（一次一步）。
- 统计执行单元总数，决定是否需要询问模式（见【执行模式】）。
- 拆解时评估**计算量**：能否先裁剪/选择缩小范围再算，避免数据量爆炸卡死。

### ② 计划确认
展示 To Do 清单 + 每项关键步骤。**等用户确认后才开始第一个 To Do**（被其他任务唤起时不阻塞，见【执行模式】）。

### ③ 选择模式
按【执行模式】的规则询问或默认。

### ④ 逐项执行
- 单步 / 连续：每个执行单元
  1. 输出步骤声明【工具名】+参数
  2. 执行：`"{python}" -c "代码"`（python 路径读 config.json）
  3. 检查结果：
     - 成功 → 用 `arcpy.management.GetCount` / `arcpy.Describe` 抽查结果
     - 退出码非 0 / 崩溃 / 卡住 → 进入【错误处理】
- 合并（PTC）：按【执行模式】生成并执行阶段脚本。

### ⑤ 按模式确认
- **单步**：每步确认；To Do 的最后一步确认即阶段确认。
- **连续 / 合并**：一个 To Do 完成 → 报告成果（输出路径、要素数/文件大小）→ 停下等确认 → 下一项；被其他任务唤起时不阻塞，继续下一项，最终统一报告。

## 解释器路径（config.json）

> 📌 **本机 arcpy 位置**：见技能目录 `config.json` 的 `python_path` 字段。
> **首次安装此技能请先搜索 arcpy 解释器位置并填入 `config.json`；之后每次直接读取，不再重复检测。**

- **首次安装**：搜索解释器 → 填入 `config.json`（可复制 `config.json.template` 后修改）→ 按下面命令验证一次。
- **之后每次运行**：直接读取 `config.json`，**禁止重复检测安装位置**。
- **仅当路径失效**（文件不存在 / `import arcpy` 失败）才重新检测并更新 `config.json`。
- `config.json` 已被 `.gitignore` 忽略，不会推送到仓库。

检测命令（Git Bash，仅首次安装或路径失效时执行）：
```bash
# 1. 注册表（覆盖 ArcGIS Pro；Git Bash 中 /s 要写成 //s，避免被 MSYS 当成路径转换）
reg query "HKLM\SOFTWARE\ESRI\ArcGISPro" //s 2>/dev/null | grep -i "PythonConda"
#    输出 PythonCondaRoot 与 PythonCondaEnv，拼出：
#    <PythonCondaRoot>\envs\<PythonCondaEnv>\python.exe
# 2. 常见安装路径（同时覆盖 ArcGIS Pro 与 GeoScene Pro；两者互斥，单机至多一个）
find "/d/Program Files" "/c/Program Files" -maxdepth 7 -path "*Pro/bin/Python/envs/*/python.exe" 2>/dev/null
```
验证：`"{python}" -c "import arcpy; print(arcpy.GetInstallInfo()['Version'])"`

## 工具签名速查

> **参数必须照抄签名，禁止凭记忆。** 不确定的工具 → 联网查 `site:pro.arcgis.com`。
> 下表已于 **2026-11-11 用本机 ArcGIS Pro 3.5.4 的 arcpy 实测核对**；修改本表后运行 `verify_sigs.py` 复核。
> ⚠ 标有「就地修改」的工具会直接改动输入数据；执行前先把目标复制到 `过程/`，严禁对原始数据执行。

### 环境设置（每个脚本开头）
```python
import arcpy
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"D:/.../过程/..."   # 路径用正斜杠
```
常用坐标系：4326 WGS84 / 3857 Web Mercator / 4490 CGCS2000 / 4548 CGCS2000_3度带_117E / 4549 CGCS2000_3度带_120E

> ⚠️ **CGCS2000 3 度带编码易错**（2026-10-21 实测、2026-11-11 修正）：中央经线版自 **4534(75°E)** 起、中央经线每 3° 递增一个码，即
> 114°E=4547、**117°E=4548**、120°E=4549、123°E=4550。带号版（坐标含带号前缀）为 4513(zone 25) 起。
> 用 arcpy 时**必须先验证**：`print(arcpy.SpatialReference(code).name)`，看名字里的中央经线是否与预期一致，勿凭记忆写码。

### 数据管理
| 工具 | 签名 |
|------|------|
| 缓冲 | `arcpy.analysis.Buffer(in_features, out_fc, "500 Meters", dissolve_option="ALL")` |
| 裁剪(矢量) | `arcpy.analysis.Clip(in_features, clip_features, out_fc)` |
| 裁剪(栅格) | `arcpy.management.Clip(in_raster, "", out_raster, in_template_dataset, "", "ClippingGeometry")` |
| 属性选择→新文件 | `arcpy.analysis.Select(in_features, out_fc, "省='河北'")` |
| 复制要素 | `arcpy.management.CopyFeatures(in_features, out_fc)` |
| 投影(矢量) | `arcpy.management.Project(in_fc, out_fc, arcpy.SpatialReference(4548))`  # 4548=117°E，见上 |
| 投影(栅格) | `arcpy.management.ProjectRaster(in_raster, out_raster, arcpy.SpatialReference(4548), "BILINEAR", 30)` |
| 定义投影 ⚠就地修改 | `arcpy.management.DefineProjection(in_fc, arcpy.SpatialReference(4548))` |
| 重采样 | `arcpy.management.Resample(in_raster, out_raster, 30, "BILINEAR")` |
| 合并要素 | `arcpy.management.Merge(inputs=[fc1, fc2], output=out_fc)` |
| 镶嵌栅格 | `arcpy.management.MosaicToNewRaster(input_rasters=[t1, t2], output_location=gdb, raster_dataset_name_with_extension="mosaic.tif", coordinate_system_for_the_raster=None, pixel_type="32_BIT_FLOAT", cellsize=30, number_of_bands=1)` |
| 追加 ⚠就地修改 | `arcpy.management.Append(inputs=[fc1, fc2], target=target_fc, schema_type="NO_TEST")` |
| 添加字段 ⚠就地修改 | `arcpy.management.AddField(in_table, "area_ha", "DOUBLE")` |
| 字段计算 ⚠就地修改 | `arcpy.management.CalculateField(in_table, "area_ha", "!SHAPE.AREA@HECTARES!", "PYTHON3")` |
| XY转点(csv→shp) | `arcpy.management.XYTableToPoint(in_table=csv, out_feature_class=out_fc, x_field="lon", y_field="lat", coordinate_system=arcpy.SpatialReference(4326))` |
| 建文件gdb | `arcpy.management.CreateFileGDB(out_folder, "temp.gdb")` |
| 修复几何 ⚠就地修改 | `arcpy.management.RepairGeometry(in_features, "DELETE_NULL", "ESRI")` |
| 多部件转单部件 | `arcpy.management.MultipartToSinglepart(in_features, out_fc)` |

### 矢量分析
| 工具 | 签名 |
|------|------|
| 空间连接 | `arcpy.analysis.SpatialJoin(target_features, join_features, out_fc, join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_ALL", match_option="INTERSECT")` |
| 融合 | `arcpy.management.Dissolve(in_features, out_fc, dissolve_field=["省"], statistics_fields=[["面积", "SUM"]], multi_part="MULTI_PART")` |
| 要素转点 | `arcpy.management.FeatureToPoint(in_features, out_fc, "INSIDE")` |
| 面转线 | `arcpy.management.PolygonToLine(in_features, out_fc, "IDENTIFY_NEIGHBORS")` |
| 邻近分析 ⚠就地修改 | `arcpy.analysis.Near(in_features, near_features, search_radius="1000 Meters", location="LOCATION", angle="ANGLE", method="PLANAR")` |
| 按位置选择 | `lyr = arcpy.management.MakeFeatureLayer(fc, "lyr")[0]; arcpy.management.SelectLayerByLocation(lyr, "INTERSECT", mask_fc, selection_type="NEW_SELECTION"); arcpy.management.CopyFeatures(lyr, out_fc)` |
| 汇总统计 | `arcpy.analysis.Statistics(in_table, out_table, [["面积", "SUM"], ["人口", "MEAN"]], case_field=["省"])` |
| 排序 | `arcpy.management.Sort(in_dataset, out_dataset, [["面积", "DESCENDING"]])` |

### 格式转换
| 工具 | 签名 |
|------|------|
| 要素→gdb | `arcpy.conversion.FeatureClassToGeodatabase([fc1, fc2], r"D:/.../x.gdb")` |
| 要素→geojson | `arcpy.conversion.FeaturesToJSON("in_fc", "out.json", "FORMATTED", "NO_Z_VALUES", "NO_M_VALUES", "GEOJSON")` |
| geojson→要素 | `arcpy.conversion.JSONToFeatures("in.json", out_fc)` |
| excel→表 | `arcpy.conversion.ExcelToTable(r"x.xlsx", out_table, "Sheet1$")` |
| 表→excel | `arcpy.conversion.TableToExcel(in_table, r"x.xlsx")` |
| 表→表/CSV | `arcpy.conversion.TableToTable(in_rows, out_path, "out.csv")` |
| kml→图层 | `arcpy.conversion.KMLToLayer(in_kml, out_folder, "KMLToLayerOutput.gdb")`  # 第3参数=输出 gdb 或 .lyrx 名 |
| 面→栅格 | `arcpy.conversion.PolygonToRaster(in_features, "value_field", out_raster, "MAXIMUM_AREA", cellsize=30)` |
| 栅格→面 | `arcpy.conversion.RasterToPolygon(in_raster, out_fc, "SIMPLIFY", "VALUE", "MULTIPLE_OUTER_PART")` |
| 复制栅格 | `arcpy.management.CopyRaster(in_raster, out_rasterdataset, pixel_type="32_BIT_FLOAT", format="TIFF")` |

### 空间分析（先 CheckOutExtension）

> `arcpy.sa.*` 工具返回 Raster 对象，必须 `.save(out_raster)` 才落盘；`ExtractValuesToPoints` / `Sample` 是工具，直接写输出路径。

```python
if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.CheckOutExtension("Spatial")
```
| 坡度 | `arcpy.sa.Slope(in_dem, "DEGREE", 1).save(out_raster)` |
| 坡向 | `arcpy.sa.Aspect(in_dem).save(out_raster)`  # 无 z_factor 参数 |
| 山影 | `arcpy.sa.Hillshade(in_dem, azimuth=315, altitude=45, model_shadows="NO_SHADOWS", z_factor=1).save(out_raster)` |
| 按掩膜提取 | `arcpy.sa.ExtractByMask(in_raster, mask_fc).save(out_raster)` |
| 重分类 | `arcpy.sa.Reclassify(in_raster, "VALUE", arcpy.sa.RemapValue([[1,1],[2,1],[3,2]])).save(out_raster)` |
| 欧氏距离 | `arcpy.sa.EucDistance(source_fc, maximum_distance, cell_size).save(out_raster)` |
| 条件 | `arcpy.sa.Con(in_conditional_raster, in_true_raster_or_constant=1, in_false_raster_or_constant=0, where_clause="VALUE > 100").save(out_raster)` |
| 栅格计算器 | `arcpy.sa.RasterCalculator([dem, slope], ["dem", "slope"], "dem > 100 & slope < 15").save(out_raster)` |
| 提取值至点 | `arcpy.sa.ExtractValuesToPoints(in_point_features, in_raster, out_point_features, "INTERPOLATE", "ALL")` |
| 采样 | `arcpy.sa.Sample(in_rasters, in_location_data, out_table, "NEAREST")` |
| 栅格取整 | `arcpy.sa.Int(in_raster).save(out_raster)` |

### 游标 / NumPy（多行逻辑 → 写脚本文件执行）
- 读：`for r in arcpy.da.SearchCursor(fc, ["f1", "f2"], where_clause):`
- 表转数组：`arcpy.da.TableToNumPyArray(table, ["f1", "f2"])`
- 数组转表/要素：`arcpy.da.NumPyArrayToTable(arr, out_table)` / `arcpy.da.NumPyArrayToFeatureClass(arr, out_fc, ["SHAPE@X", "SHAPE@Y"])`

## 错误处理

### 错误分类与预置处理
| 症状 | 处理 |
|------|------|
| 退出码 `-1` / 无 traceback | **原生崩溃**，多因参数错 → 逐项核对签名/官方文档 → 修复重跑 |
| `ERROR 000732` 数据集不存在 | 检查路径，`arcpy.ListFeatureClasses()` 模糊匹配 |
| `ERROR 000210` 无法创建输出 | 检查 overwriteOutput、输出目录存在性 |
| `ERROR 000725` 输出工作空间不存在 | 先 `CreateFileGDB` / 建目录 |
| `ERROR 000728` 字段不存在 | `ListFields()` 核对字段名 |
| `ERROR 000840` 值无效 | 参数值不在合法范围 → 核对签名参数位置与可选值 |
| `ERROR 999999` 未指定错误 | 通常是参数类型错 → 核对签名 |
| 文件锁定/无法打开 | 提示用户关闭 Pro 中打开该数据的图层 |
| 卡住长时间无输出 | 数据量过大 → 检查"是否该先裁剪再算"；或数据被 Pro 锁定 |
| 中文路径报错 | 路径统一正斜杠 `D:/...`，Python 字符串前加 `r` |

### 修复循环（≤3 次）
1. 出错 → 联网查（`site:pro.arcgis.com`、`site:gis.stackexchange.com`）→ 修复 → 重跑
2. 每次尝试必须基于新信息，禁止重复同一修法
3. **3 次仍失败 → 中断整个任务**，报告已尝试的方案

### 修复伦理（硬规则）
**禁止用简易方式替代根治**：
- 禁止换用语义不同的工具"凑过去"
- 禁止跳过失败的数据
- 禁止用近似代替精确、降低范围/精度来让任务"通过"
- 修复结果必须与计划确认的语义一致

### 超时
- 前台命令超时上限 **10 分钟**；预计更久的任务**直接以后台方式启动**（`run_in_background`）
- 前台超时后进程会被**终止**，不是继续跑：需重新以后台方式启动，用内置等待/通知机制等结果
- **禁止用 sleep 轮询**

## 产物组织

```
{任务目录}/
├── 过程/                  # 中间产物：每个产物一个语义命名子文件夹
│   └── 镶嵌后DEM/          # 如"镶嵌后DEM"、"用于裁剪的矢量"
├── 结果/                  # 最终成果：每个产物一个子文件夹
│   └── 裁剪后DEM/
└── _运行记录/
    ├── audit.md           # 轻量运行记录
    └── decisions.md       # 决策日志：报错采用的处理方式（跨会话复用，重点保留）
```

- 命名 = 处理后状态 + 内容（"镶嵌后DEM"，不是"镶嵌后的"）
- **原始数据留在原位，只读，绝不修改**

## 红线提醒（出现即返工）

| 借口 | 现实 |
|------|------|
| "任务简单，一次写完更快" | 长脚本混步，异常难定位；原生崩溃更无 traceback，返工更慢 |
| "我记得这个工具的参数" | 参数错 → 原生崩溃。必须照签名 |
| "跳过这条记录继续" | 改变语义，结果不可信 |
| "用 sleep 等一会" | 用后台任务等待机制 |
| "先全量算完再裁剪" | 数据量爆炸 → 卡死。先缩小范围 |
| "换个简单工具能出结果" | 违反修复伦理，结果不对 |
