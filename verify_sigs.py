# 一次性核对 SKILL.md 工具速查表中所有工具的真实签名
import arcpy

def sig(name, fn):
    doc = (fn.__doc__ or "").strip().split("\n")
    # arcpy 工具 doc 第一行就是完整签名
    line = doc[0] if doc else "(无 doc)"
    print(f"{name}: {line}")

# 数据管理
print("=== 数据管理 ===")
for name, fn in [
    ("Buffer", arcpy.analysis.Buffer),
    ("Clip(vec)", arcpy.analysis.Clip),
    ("Select", arcpy.analysis.Select),
    ("Clip(raster)", arcpy.management.Clip),
    ("CopyFeatures", arcpy.management.CopyFeatures),
    ("Project", arcpy.management.Project),
    ("ProjectRaster", arcpy.management.ProjectRaster),
    ("DefineProjection", arcpy.management.DefineProjection),
    ("Resample", arcpy.management.Resample),
    ("Merge", arcpy.management.Merge),
    ("MosaicToNewRaster", arcpy.management.MosaicToNewRaster),
    ("AddField", arcpy.management.AddField),
    ("CalculateField", arcpy.management.CalculateField),
    ("XYTableToPoint", arcpy.management.XYTableToPoint),
    ("CreateFileGDB", arcpy.management.CreateFileGDB),
]:
    sig(name, fn)

# 格式转换
print("\n=== 格式转换 ===")
for name, fn in [
    ("FeatureClassToGeodatabase", arcpy.conversion.FeatureClassToGeodatabase),
    ("FeaturesToJSON", arcpy.conversion.FeaturesToJSON),
    ("JSONToFeatures", arcpy.conversion.JSONToFeatures),
    ("ExcelToTable", arcpy.conversion.ExcelToTable),
    ("TableToExcel", arcpy.conversion.TableToExcel),
    ("KMLToLayer", arcpy.conversion.KMLToLayer),
]:
    sig(name, fn)

# 空间分析
print("\n=== 空间分析 ===")
for name, fn in [
    ("Slope", arcpy.sa.Slope),
    ("ExtractByMask", arcpy.sa.ExtractByMask),
    ("Reclassify", arcpy.sa.Reclassify),
    ("EucDistance(欧氏距离)", arcpy.sa.EucDistance),
    ("Int", arcpy.sa.Int),
]:
    sig(name, fn)

# 游标/NumPy
print("\n=== 游标/NumPy ===")
sig("SearchCursor", arcpy.da.SearchCursor)
sig("TableToNumPyArray", arcpy.da.TableToNumPyArray)
sig("NumPyArrayToTable", arcpy.da.NumPyArrayToTable)
sig("NumPyArrayToFeatureClass", arcpy.da.NumPyArrayToFeatureClass)
