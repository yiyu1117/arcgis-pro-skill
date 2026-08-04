---
name: arcgis-pro
description: 使用本机 ArcGIS Pro / GeoScene Pro 自带的 Python(arcpy) 处理地理数据。当用户提及 GIS 数据处理、空间分析、shapefile(.shp)、geodatabase(.gdb)、要素类、坐标系、投影、缓冲区、裁剪、镶嵌、重分类、空间连接、栅格分析、DEM、坡度、字段计算、格式转换(shp/geojson/kml/gpx/csv/excel/gdb 互转)、arcpy、ArcGIS Pro、GeoScene、批量处理或任何地理/空间数据操作时触发。
---

# ArcGIS Pro 地理数据处理技能

用本机 **ArcGIS Pro**（或 **GeoScene Pro**）自带的 arcpy 处理磁盘上的地理数据。核心工作方式：**单步执行、声明先行、逐步确认**。

## 三条铁律（违反任何一条 = 返工重来）

1. **一次只执行一步**。每个执行单元单独执行，**禁止**写一个大脚本一次跑完——长脚本一出错就是退出码 -1 且无 traceback，完全无法定位。
2. **声明先行**。调用任何操作前，必须先以正文输出声明，格式：
   `【工具名】输入=…，参数=…`
   例：`【缓冲区】输入=schools.shp，距离=500米，融合=ALL`
   声明仅供你核对，**不需要等确认**。
3. **确认后动手**。计划先整体确认；每个 To Do 项完成后强制停下等你确认。

## 执行流程（顺序执行，不可跳步）

```
拆解任务 → 计划确认 → 逐项执行 → 每项确认 → 完成
```

### ① 拆解
- 复杂任务先拆成 **To Do 项**，每项用内置任务工具（TaskCreate）创建，随执行更新状态（TaskUpdate）。
- 每个 To Do 项内部再分成若干**执行单元**（一次一步）。
- 拆解时评估**计算量**：能否先裁剪/选择缩小范围再算，避免数据量爆炸卡死。

### ② 计划确认
展示 To Do 清单 + 每项关键步骤。**等用户确认后才开始第一个 To Do**。

### ③ 逐项执行（每个执行单元）
1. 输出步骤声明【工具名】+参数
2. 执行：`"{python}" -c "代码"`（python 路径读 config.json）
3. 检查结果：
   - 成功 → 用 `arcpy.management.GetCount` / `Describe` 抽查结果
   - 退出码非 0 / 崩溃 / 卡住 → 进入【错误处理】

### ④ 每项确认
一个 To Do 完成 → 报告成果（输出路径、要素数/文件大小）→ **停下等用户确认** → 下一项。

### 快进
用户说"这几步连跑" → 中间步骤合并一次执行（省 import 开销），但每步声明仍要显示。

## 解释器路径（config.json）

- 路径存在技能目录 `config.json` 中，直接读。
- **首次运行**：检测后写入。
- **报错找不到**（路径不存在 / import arcpy 失败）才重新检测并更新。

检测命令（Git Bash）：
```bash
# 1. 注册表（最可靠）
reg query "HKLM\SOFTWARE\ESRI\ArcGIS Pro" /s 2>/dev/null | grep -i "PythonConda"
# 2. 常见安装路径（ArcGIS Pro 与 GeoScene Pro 互斥，单机至多一个）
find "/d/Program Files" "/c/Program Files" -maxdepth 6 -path "*Pro/bin/Python/envs/*/python.exe" 2>/dev/null
```
验证：`"{python}" -c "import arcpy; print(arcpy.GetInstallInfo()['Version'])"`

## 工具签名速查

> **参数必须照抄签名，禁止凭记忆。** 不确定的工具 → 联网查 `site:pro.arcgis.com`。

### 环境设置（每个脚本开头）
```python
import arcpy
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"D:/.../过程/..."   # 路径用正斜杠
```
常用坐标系：4326 WGS84 / 3857 Web Mercator / 4490 CGCS2000 / 4547 CGCS2000_3度带_117E / 4523 CGCS2000_3度带_120E

### 数据管理
| 工具 | 签名 |
|------|------|
| 缓冲 | `arcpy.analysis.Buffer(in_features, out_fc, "500 Meters", dissolve_option="ALL")` |
| 裁剪(矢量) | `arcpy.analysis.Clip(in_features, clip_features, out_fc)` |
| 裁剪(栅格) | `arcpy.management.Clip(in_raster, "", out_raster, in_template_dataset, "", "ClippingGeometry")` |
| 属性选择→新文件 | `arcpy.analysis.Select(in_features, out_fc, "省='河北'")` |
| 复制要素 | `arcpy.management.CopyFeatures(in_features, out_fc)` |
| 投影(矢量) | `arcpy.management.Project(in_fc, out_fc, arcpy.SpatialReference(4547))` |
| 投影(栅格) | `arcpy.management.ProjectRaster(in_raster, out_raster, arcpy.SpatialReference(4547), "BILINEAR", 30)` |
| 定义投影 | `arcpy.management.DefineProjection(in_fc, arcpy.SpatialReference(4547))` |
| 重采样 | `arcpy.management.Resample(in_raster, out_raster, 30, "BILINEAR")` |
| 合并要素 | `arcpy.management.Merge(inputs=[fc1, fc2], output=out_fc)` |
| 镶嵌栅格 | `arcpy.management.MosaicToNewRaster(input_rasters=[t1, t2], output_location, raster_name, pixel_type, cellsize, number_of_bands)` |
| 添加字段 | `arcpy.management.AddField(in_table, "area_ha", "DOUBLE")` |
| 字段计算 | `arcpy.management.CalculateField(in_table, "area_ha", "!SHAPE.AREA@HECTARES!", "PYTHON3")` |
| XY转点(csv→shp) | `arcpy.management.XYTableToPoint(in_table=csv, out_feature_class=out_fc, x_field="lon", y_field="lat", coordinate_system=arcpy.SpatialReference(4326))` |
| 建文件gdb | `arcpy.management.CreateFileGDB(out_folder, "temp.gdb")` |

### 格式转换
| 工具 | 签名 |
|------|------|
| 要素→gdb | `arcpy.conversion.FeatureClassToGeodatabase([fc1, fc2], r"D:/.../x.gdb")` |
| 要素→geojson | `arcpy.conversion.FeaturesToJSON(in_fc, out.json, "FORMATTED", "NO_Z_VALUES", "NO_M_VALUES", "GEOJSON")` |
| geojson→要素 | `arcpy.conversion.JSONToFeatures(in.json, out_fc)` |
| excel→表 | `arcpy.conversion.ExcelToTable(r"x.xlsx", out_table, "Sheet1$")` |
| 表→excel | `arcpy.conversion.TableToExcel(in_table, r"x.xlsx")` |
| kml→图层 | `arcpy.conversion.KMLToLayer(in_kml, out_folder, out_name)` |

### 空间分析（先 CheckOutExtension）
```python
if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.CheckOutExtension("Spatial")
```
| 坡度 | `arcpy.sa.Slope(in_dem, "DEGREE", 1)` |
| 按掩膜提取 | `arcpy.sa.ExtractByMask(in_raster, mask_fc)` |
| 重分类 | `arcpy.sa.Reclassify(in_raster, "VALUE", arcpy.sa.RemapValue([[1,1],[2,1],[3,2]]))` |
| 欧氏距离 | `arcpy.sa.EucDistance(source_fc, maximum_distance, cell_size)` |
| 栅格取整 | `arcpy.sa.Int(in_raster)` |

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
- 用 Bash 自带超时：默认 **10 分钟**，大数据 **20~30 分钟**
- 超时 → **转后台任务**继续，用内置等待/通知机制等结果
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
| "任务简单，一次写完更快" | 长脚本一出错就 -1 无原因，返工更慢 |
| "我记得这个工具的参数" | 参数错 → 原生崩溃。必须照签名 |
| "跳过这条记录继续" | 改变语义，结果不可信 |
| "用 sleep 等一会" | 用后台任务等待机制 |
| "先全量算完再裁剪" | 数据量爆炸 → 卡死。先缩小范围 |
| "换个简单工具能出结果" | 违反修复伦理，结果不对 |
