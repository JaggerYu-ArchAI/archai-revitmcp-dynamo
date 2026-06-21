# -*- coding: utf-8 -*-
# 固定导入内容
# 1. 加载Python Standard和DesignScript库
import sys
import os
import math
import json
import clr

clr.AddReference('ProtoGeometry')  # Dynamo核心几何库
from Autodesk.DesignScript.Geometry import *

clr.AddReference('DSCoreNodes')  # Dynamo核心基础库
import DSCore  # 为避免冲突，使用DSCore.List.XX

clr.AddReference('RevitNodes')  # Dynamo Revit专属节点库
import Revit   # 为避免冲突，使用Revit.Elements.XX
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)

# 2. 导入Revit API
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference("System.Collections")
import System
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from System.Collections.Generic import *

# 3. 导入Revit管理服务
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# 4. 全局文档对象
doc = DocumentManager.Instance.CurrentDBDocument
app = doc.Application
uiApp = DocumentManager.Instance.CurrentUIApplication
uidoc = uiApp.ActiveUIDocument

# 5. 导入配置文件（统一单位常量）
from revit_mcp_tools.config import FEET_TO_MM, METERS_TO_FEET

# ======================================
# 全局缓存：存储最后一次函数执行结果
# ======================================
LAST_EXEC_RESULT = None



# ==============================================
# Python列表 → .NET List<string>
# 使用 BimorphNodes 节点包中节点
# ==============================================
def _to_net(py_list):
    """将Python列表转换为.NET字符串泛型列表"""
    net_list = List[System.String]()
    for item in py_list:
        net_list.Add(str(item))
    return net_list

def _cad_curves_from_cad_layers(layer_names, create_model_curves = False, line_style_map = None):
    """
    根据链接CAD文件，批量生成结构框架（结构柱或结构梁）
    :param layer_names: 链接CAD文件中结构框架的图层名称列表
    :param create_model_curves: 默认不创建模型线条
    :param line_style_map: 默认不映射线条类型
    :return: 字典，包含"Curve[][]" 与 "layerKeys[]"
    使用 BimorphNodes 节点包中节点，默认选择第一个链接CAD文件
    """
    collector = FilteredElementCollector(doc).OfClass(ImportInstance).ToElements()
    import_instance = collector[0].ToDSType(True)
    ln = _to_net(layer_names)
    lsm = _to_net(line_style_map or [])
    
    # ==============================================
    # 查找 CAD 类
    # ==============================================
    Cad = None
    for asm in System.AppDomain.CurrentDomain.GetAssemblies():
        if "Bimorph" in asm.GetName().Name:
            for t in asm.GetTypes():
                if t.Name == "CAD":
                    Cad = t
            if Cad: break
            
    # ==============================================
    # 查找目标方法
    # ==============================================
    method = None
    if Cad:
        for m in Cad.GetMethods():
            if "CurvesFromCADLayers" in m.Name:
                method = m
                break
    
    # ==============================================
    # 使用方法
    # ==============================================
    try:
        # 4个参数：ImportInstance, LayerNames, create_model_curves, line_style_map
        param_list = [import_instance, ln, create_model_curves, lsm]
        # 调用静态方法
        result = method.Invoke(None, param_list)
        return result
    
    except Exception as e:
        return f"错误：{str(e)}"
        
def _cad_text_data_from_layers(layer_names = None):
    """
    根据链接CAD文件，批量生成结构框架（结构柱或结构梁）
    :param layer_names: 链接CAD文件中文字的图层名称列表
    :return: 字典，包含"layerKeys[]"与"CADTextData[][]" 
    使用 BimorphNodes 节点包中节点，默认选择第一个链接CAD文件
    """
    collector = FilteredElementCollector(doc).OfClass(ImportInstance).ToElements()
    import_instance = collector[0].ToDSType(True)
    ln = _to_net(layer_names or [])
    
    # ==============================================
    # 查找 CADTextData 类
    # ==============================================
    CadTextData = None
    for asm in System.AppDomain.CurrentDomain.GetAssemblies():
        if "Bimorph" in asm.GetName().Name:
            for t in asm.GetTypes():
                if t.Name == "CADTextData":
                    CadTextData = t
            if CadTextData: break
            
    # ==============================================
    # 查找目标方法
    # ==============================================
    method = None
    if CadTextData:
        for m in CadTextData.GetMethods():
            if "FromLayers" in m.Name:
                method = m
                break
    
    # ==============================================
    # 使用方法
    # ==============================================
    try:
        # 2个参数：ImportInstance, LayerNames
        param_list = [import_instance, ln]
        # 调用静态方法
        result = method.Invoke(None, param_list)
        return result
    
    except Exception as e:
        return f"错误：{str(e)}"
        
        
def _cad_text_data_origin_point(cad_text_data):
    """
    根据链接CAD文件，批量生成结构框架（结构柱或结构梁）
    :param cad_text_data: 由函数_cad_text_data_from_layers()返回，使用"CADTextData[][]"键值
    :return: 点列表
    使用 BimorphNodes 节点包中节点
    """
    
    # ==============================================
    # 查找 CADTextData 类
    # ==============================================
    CadTextData = None
    for asm in System.AppDomain.CurrentDomain.GetAssemblies():
        if "Bimorph" in asm.GetName().Name:
            for t in asm.GetTypes():
                if t.Name == "CADTextData":
                    CadTextData = t
            if CadTextData: break
            
    # ==============================================
    # 查找目标方法
    # ==============================================
    method = None
    if CadTextData:
        for m in CadTextData.GetMethods():
            if "OriginPoint" in m.Name:
                method = m
                break
    
    # ==============================================
    # 使用方法
    # ==============================================
    try:
        # 单个对象
        if not isinstance(cad_text_data, list):
            return method.Invoke(cad_text_data, [])
        # 二维列表
        elif not isinstance(cad_text_data[0], list):
            res = []
            for row in cad_text_data:
                row_res = [method.Invoke(item, []) for item in row]
                res.append(row_res)
            return res
        # 一维列表
        else:
            return [method.Invoke(item, []) for item in cad_text_data]
    
    except Exception as e:
        return f"错误：{str(e)}"
        
def _cad_text_data_text_value(cad_text_data):
    """
    根据链接CAD文件，批量生成结构框架（结构柱或结构梁）
    :param cad_text_data: 由函数_cad_text_data_from_layers()返回，使用"CADTextData[][]"键值
    :return: 点列表
    使用 BimorphNodes 节点包中节点
    """
    
    # ==============================================
    # 查找 CADTextData 类
    # ==============================================
    CadTextData = None
    for asm in System.AppDomain.CurrentDomain.GetAssemblies():
        if "Bimorph" in asm.GetName().Name:
            for t in asm.GetTypes():
                if t.Name == "CADTextData":
                    CadTextData = t
            if CadTextData: break
            
    # ==============================================
    # 查找目标方法
    # ==============================================
    method = None
    if CadTextData:
        for m in CadTextData.GetMethods():
            if "TextValue" in m.Name:
                method = m
                break
    
    # ==============================================
    # 使用方法
    # ==============================================
    try:
        # 单个对象
        if not isinstance(cad_text_data, list):
            return method.Invoke(cad_text_data, [])
        # 二维列表
        elif not isinstance(cad_text_data[0], list):
            res = []
            for row in cad_text_data:
                row_res = [method.Invoke(item, []) for item in row]
                res.append(row_res)
            return res
        # 一维列表
        else:
            return [method.Invoke(item, []) for item in cad_text_data]
    
    except Exception as e:
        return f"错误：{str(e)}"




# ==================================================
# 第一部分：选择查询工具（收集器）
# ==================================================
# 类别映射表（统一管理所有支持的类别）
CATEGORY_MAP = {
    "标高": BuiltInCategory.OST_Levels, "levels": BuiltInCategory.OST_Levels,
    "墙体": BuiltInCategory.OST_Walls, "walls": BuiltInCategory.OST_Walls,
    "房间": BuiltInCategory.OST_Rooms, "rooms": BuiltInCategory.OST_Rooms,
    "门": BuiltInCategory.OST_Doors, "doors": BuiltInCategory.OST_Doors,
    "窗": BuiltInCategory.OST_Windows, "windows": BuiltInCategory.OST_Windows,
    "楼板": BuiltInCategory.OST_Floors, "floors": BuiltInCategory.OST_Floors,
    "屋面": BuiltInCategory.OST_Roofs, "roofs": BuiltInCategory.OST_Roofs,
    "结构柱": BuiltInCategory.OST_StructuralColumns, "columns": BuiltInCategory.OST_StructuralColumns,
    "结构梁": BuiltInCategory.OST_StructuralFraming, "framing": BuiltInCategory.OST_StructuralFraming,
    "轴网": BuiltInCategory.OST_Grids, "grids": BuiltInCategory.OST_Grids
}

def get_elements_by_category(category_name: str, active_view_only: bool = False):
    global LAST_EXEC_RESULT
    """
    按类别名称获取元素
    :param category_name: 类别名称（如"墙"、"门"、"窗"、"结构柱"）
    :param active_view_only: 是否仅获取当前视图中的元素（默认False：获取整个项目）
    """
    if category_name not in CATEGORY_MAP:
        raise Exception(f"不支持的类别：{category_name}，支持的类别：{list(CATEGORY_MAP.keys())}")

    # 构建收集器
    if active_view_only:
        collector = FilteredElementCollector(doc, doc.ActiveView.Id)
    else:
        collector = FilteredElementCollector(doc)

    # 获取元素
    elements = collector.OfCategory(CATEGORY_MAP[category_name]).WhereElementIsNotElementType().ToElements()

    # 特殊处理：房间需要过滤有效房间
    if category_name in ["房间", "rooms"]:
        valid_elements = []
        for elem in elements:
            if elem is not None and elem.Location is not None and elem.Area > 0:
                valid_elements.append(elem)
        elements = valid_elements

    # 选中元素
    if elements:
        elem_id_list = List[ElementId]()
        for elem in elements:
            elem_id_list.Add(elem.Id)
        uidoc.Selection.SetElementIds(elem_id_list)

    LAST_EXEC_RESULT = elements
    return elements

def get_elements_by_family(family_name: str, type_name: str):
    global LAST_EXEC_RESULT
    """
    按 族名称+族类型名称 获取元素
    :param family_name: 族名称
    :param type_name: 族类型名
    :return: 匹配的实例元素列表
    """
    fam_type = Revit.Elements.FamilyType.ByFamilyNameAndTypeName(family_name, type_name)
    dyn_elements = Revit.Elements.FamilyInstance.ByFamilyType(fam_type)
    elements = [UnwrapElement(elem) for elem in dyn_elements]
    # 选中元素
    if elements:
        elem_id_list = List[ElementId]()
        for elem in elements:
            elem_id_list.Add(elem.Id)
        uidoc.Selection.SetElementIds(elem_id_list)

    LAST_EXEC_RESULT = elements
    return elements

def get_elements_by_parameter(
    category_name: str,
    parameter_name: str,
    parameter_value,
    match_mode: str = "exact",
    active_view_only: bool = False
):
    global LAST_EXEC_RESULT
    """
    按类别名称与参数值获取元素（增强版：支持精确匹配/开头匹配/包含匹配）
    :param category_name: 类别名称（如"墙"、"门"、"窗"、"结构柱"）
    :param parameter_name: 参数名称
    :param parameter_value: 参数值（支持字符串、数值、整数）
    :param match_mode: 匹配模式：exact=精确匹配（默认）、start_with=开头匹配、contains=包含匹配
    :param active_view_only: 是否仅获取当前视图中的元素（默认False：获取整个项目）
    """
    # 1. 类别合法性校验
    if category_name not in CATEGORY_MAP:
        raise Exception(f"不支持的类别：{category_name}，支持的类别：{list(CATEGORY_MAP.keys())}")
    
    # 2. 匹配模式合法性校验
    if match_mode not in ["exact", "start_with", "contains"]:
        raise Exception(f"不支持的匹配模式：{match_mode}，支持的模式：exact（精确）、start_with（开头匹配）、contains（包含）")

    # 3. 构建元素收集器
    if active_view_only:
        collector = FilteredElementCollector(doc, doc.ActiveView.Id)
    else:
        collector = FilteredElementCollector(doc)

    # 4. 获取原生Revit元素
    raw_elements = collector.OfCategory(CATEGORY_MAP[category_name]).WhereElementIsNotElementType().ToElements()

    # 5. 特殊处理：房间过滤有效房间
    if category_name in ["房间", "rooms"]:
        valid_raw_elements = []
        for elem in raw_elements:
            if elem is not None and elem.Location is not None and elem.Area > 0:
                valid_raw_elements.append(elem)
        raw_elements = valid_raw_elements

    # 6. 按参数值过滤（支持多匹配模式）
    filtered_raw_elements = []
    for raw_elem in raw_elements:
        dyn_elem = raw_elem.ToDSType(True)
        try:
            elem_param_value = dyn_elem.GetParameterValueByName(parameter_name)
            # 转字符串统一处理匹配逻辑
            param_value_str = str(elem_param_value).strip()
            target_value_str = str(parameter_value).strip()

            # 按匹配模式判断
            if match_mode == "exact" and param_value_str == target_value_str:
                filtered_raw_elements.append(raw_elem)
            elif match_mode == "start_with" and param_value_str.startswith(target_value_str):
                filtered_raw_elements.append(raw_elem)
            elif match_mode == "contains" and target_value_str in param_value_str:
                filtered_raw_elements.append(raw_elem)
        except:
            continue

    # 7. 选中过滤后的元素
    if filtered_raw_elements:
        elem_id_list = List[ElementId]()
        for raw_elem in filtered_raw_elements:
            elem_id_list.Add(raw_elem.Id)
        uidoc.Selection.SetElementIds(elem_id_list)

    LAST_EXEC_RESULT = filtered_raw_elements
    return filtered_raw_elements

def get_selected_elements(limit: int = 100):
    global LAST_EXEC_RESULT
    """
    获取当前选中的元素（支持缓存）
    :param limit: 返回的最大元素数量，默认100
    :return: 选中的原生Revit元素列表
    """
    try:
        selection = uidoc.Selection.GetElementIds()
        elements = []
        count = 0
        
        for elem_id in selection:
            if count >= limit:
                break
            elem = doc.GetElement(elem_id)
            if elem and elem.IsValidObject:
                elements.append(elem)
            count += 1

        if elements:
            elem_id_list = List[ElementId]()
            for elem in elements:
                elem_id_list.Add(elem.Id)
            uidoc.Selection.SetElementIds(elem_id_list)

        LAST_EXEC_RESULT = elements
        return elements

    except Exception as e:
        LAST_EXEC_RESULT = None
        raise Exception(f"获取选中元素失败：{str(e)}")


# ==================================================
# 第二部分：建筑方案设计工具
# ==================================================
def architecture_design_rectangle(length: float, width: float, floor_h: float, floors: int):
    global LAST_EXEC_RESULT
    """
    建筑方案设计（矩形）
    :param length: 建筑长度（米）
    :param width: 建筑宽度（米）
    :param floor_h: 单层高度（米）
    :param floors: 建筑层数
    """
    total_area = length * width * floors
    total_h = floor_h * floors
    length_ft = length * METERS_TO_FEET
    width_ft = width * METERS_TO_FEET
    floor_h_ft = floor_h * METERS_TO_FEET
    total_h_ft = total_h * METERS_TO_FEET

    output = []
    created_elements = []
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)

        # ------------------------- 创建楼层标高 ----------------------
        levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
        level_dict = {}

        current_elevation = 0.0
        for i in range(floors + 1):
            level_name = f"标高 {i}" if i > 0 else "标高 0"
            existing_level = next((lv for lv in levels if lv.Name == level_name), None)

            if not existing_level:
                new_level = Level.Create(doc, current_elevation)
                new_level.Name = level_name
                level_dict[i] = new_level
                created_elements.append(new_level)
            else:
                existing_level.Elevation = current_elevation
                level_dict[i] = existing_level

            current_elevation += floor_h_ft

        # ------------------------- 获取墙体类型 ----------------------
        wall_types = list(FilteredElementCollector(doc).OfClass(WallType).ToElements())
        if not wall_types:
            raise Exception("项目中没有找到可用的墙体类型，请先加载项目模板")
        # 优先使用基本墙，没有则用第一个可用的
        wall_type = next((wt for wt in wall_types if wt.Kind == WallKind.Basic), wall_types[0])

        # ------------------------ 创建外围护墙体 ----------------------
        p0 = XYZ(0, 0, 0)
        p1 = XYZ(length_ft, 0, 0)
        p2 = XYZ(length_ft, width_ft, 0)
        p3 = XYZ(0, width_ft, 0)
        wall_points = [p0, p1, p2, p3, p0]

        for floor_idx in range(floors):
            base_level = level_dict[floor_idx]
            top_level = level_dict[floor_idx + 1]

            for j in range(4):
                start_pt = wall_points[j]
                end_pt = wall_points[j + 1]
                wall_line = Line.CreateBound(start_pt, end_pt)

                # 简化墙体创建，直接使用标高约束
                wall = Wall.Create(
                    doc,
                    wall_line,
                    wall_type.Id,
                    base_level.Id,
                    floor_h_ft,
                    0.0,
                    False,
                    False
                )
                created_elements.append(wall)

        # ---------------------- 获取楼板类型 ----------------------
        floor_types = list(FilteredElementCollector(doc).OfClass(FloorType).ToElements())
        if not floor_types:
            raise Exception("项目中没有找到可用的楼板类型，请先加载项目模板")
        floor_type = floor_types[0]

        # ---------------------- 创建每层楼板 ----------------------
        floor_curve_loop = CurveLoop()
        floor_curve_loop.Append(Line.CreateBound(p0, p1))
        floor_curve_loop.Append(Line.CreateBound(p1, p2))
        floor_curve_loop.Append(Line.CreateBound(p2, p3))
        floor_curve_loop.Append(Line.CreateBound(p3, p0))

        for floor_idx in range(floors):
            base_level = level_dict[floor_idx]
            floor = Floor.Create(
                doc,
                [floor_curve_loop],
                floor_type.Id,
                base_level.Id
            )
            created_elements.append(floor)

        # ---------------------- 整理输出 ----------------------
        output = [
            "✅AI辅助建模成功！",
            f"体块参数：长{length}m×宽{width}m×总高{total_h}m，层高{floor_h}m，层数{floors}层",
            f"总建筑面积：{total_area}㎡",
            f"已创建元素数量：{len(created_elements)}"
        ] + created_elements

        TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = output
        return output

    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        output = [f"❌Revit建模失败：{str(e)}"]
        LAST_EXEC_RESULT = output
        return output

def architecture_design_circle(diameter: float, floor_h: float, floors: int):
    global LAST_EXEC_RESULT
    """
    建筑方案设计（圆形）
    :param diameter: 建筑直径（米）
    :param floor_h: 单层高度（米）
    :param floors: 建筑层数
    :return: 执行结果日志 + 所有创建的图元列表
    """
    radius_ft = (diameter / 2) * METERS_TO_FEET
    floor_h_ft = floor_h * METERS_TO_FEET
    total_h = floor_h * floors
    total_h_ft = total_h * METERS_TO_FEET
    total_area = math.pi * (diameter / 2) ** 2 * floors

    output = []
    created_elements = []

    try:
        # 开启事务
        TransactionManager.Instance.EnsureInTransaction(doc)

        # --------------------------
        # 1. 标高创建与管理
        # --------------------------
        levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
        level_dict = {}
        current_elevation = 0.0

        # 循环创建/更新对应层数的标高
        for i in range(floors + 1):
            level_name = f"标高 {i}" if i > 0 else "标高 0"
            # 查找项目中已存在的同名标高
            existing_level = next((lv for lv in levels if lv.Name == level_name), None)

            if not existing_level:
                # 新建标高
                new_level = Level.Create(doc, current_elevation)
                new_level.Name = level_name
                level_dict[i] = new_level
                created_elements.append(new_level)
            else:
                # 更新已有标高的高程，避免重复创建
                existing_level.Elevation = current_elevation
                level_dict[i] = existing_level

            # 累加层高
            current_elevation += floor_h_ft

        # --------------------------
        # 2. 墙体类型获取
        # --------------------------
        wall_types = list(FilteredElementCollector(doc).OfClass(WallType).ToElements())
        if not wall_types:
            raise Exception("项目中没有找到可用的墙体类型，请先加载项目模板")
        # 优先取基本墙，无则取项目中第一个墙体类型
        wall_type = next((wt for wt in wall_types if wt.Kind == WallKind.Basic), wall_types[0])

        # --------------------------
        # 3. 圆弧几何创建
        # --------------------------
        center_point = XYZ(0, 0, 0)
        normal_vector = XYZ(0, 0, 1)  # Z轴向上，建筑垂直方向
        x_axis = XYZ(1, 0, 0)
        y_axis = XYZ(0, 1, 0)

        # 拆分为两个半圆弧，解决闭合曲线API不兼容问题
        arc_up = Arc.Create(center_point, radius_ft, 0, math.pi, x_axis, y_axis)  # 上半圆 0→π
        arc_down = Arc.Create(center_point, radius_ft, math.pi, math.pi * 2, x_axis, y_axis)  # 下半圆 π→2π

        # --------------------------
        # 4. 墙体创建
        # --------------------------
        for floor_idx in range(floors):
            base_level = level_dict[floor_idx]
            # 双圆弧拼接成完整圆形墙体，兼容所有Revit版本
            wall1 = Wall.Create(
                doc, arc_up, wall_type.Id, base_level.Id,
                floor_h_ft, 0.0, False, False
            )
            wall2 = Wall.Create(
                doc, arc_down, wall_type.Id, base_level.Id,
                floor_h_ft, 0.0, False, False
            )
            created_elements.extend([wall1, wall2])

        # --------------------------
        # 5. 楼板类型获取
        # --------------------------
        floor_types = list(FilteredElementCollector(doc).OfClass(FloorType).ToElements())
        if not floor_types:
            raise Exception("项目中没有找到可用的楼板类型，请先加载项目模板")
        floor_type = floor_types[0]

        # --------------------------
        # 6. 楼板闭合轮廓创建
        # --------------------------
        floor_loop = CurveLoop()
        # 双圆弧拼接成闭合轮廓，完全符合Revit API规范
        floor_loop.Append(arc_up)
        floor_loop.Append(arc_down)

        # --------------------------
        # 7. 楼板创建
        # --------------------------
        for floor_idx in range(floors):
            base_level = level_dict[floor_idx]
            new_floor = Floor.Create(
                doc,
                [floor_loop],
                floor_type.Id,
                base_level.Id
            )
            created_elements.append(new_floor)

        # --------------------------
        # 8. 结果输出
        # --------------------------
        output = [
            "✅AI辅助圆形建筑建模成功！",
            f"体块参数：直径{diameter}m × 总高{total_h}m，层高{floor_h}m，层数{floors}层",
            f"总建筑面积：{total_area:.2f}㎡",
            f"已创建图元数量：{len(created_elements)}个"
        ] + created_elements

        # 提交事务
        TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = output
        return output

    except Exception as e:
        # 异常时强制关闭事务，避免锁文档
        TransactionManager.Instance.TransactionTaskDone()
        output = [f"❌Revit建模失败：{str(e)}"]
        LAST_EXEC_RESULT = output
        return output

# ==================================================
# 第三部分：常用构件创建工具
# ==================================================
def create_wall(start_x: float, start_y: float, end_x: float, end_y: float, wall_height: float, level_name: str):
    global LAST_EXEC_RESULT
    """
    创建直线墙体（指定起点和终点坐标）
    :param start_x: 起点X坐标（毫米）
    :param start_y: 起点Y坐标（毫米）
    :param end_x: 终点X坐标（毫米）
    :param end_y: 终点Y坐标（毫米）
    :param wall_height: 墙体高度（毫米）
    :param level_name: 标高名称
    """
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)
        # 获取目标标高
        levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
        target_level = next((lvl for lvl in levels if lvl.Name.strip() == level_name.strip()), None)

        if not target_level:
            raise Exception(f"未找到标高：{level_name}")

        # 创建墙体（使用config中的统一单位常量）
        start_point = XYZ(start_x / FEET_TO_MM, start_y / FEET_TO_MM, 0)
        end_point = XYZ(end_x / FEET_TO_MM, end_y / FEET_TO_MM, 0)
        wall_line = Line.CreateBound(start_point, end_point)
        created_wall = Wall.Create(doc, wall_line, target_level.Id, False)
        created_wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(wall_height / FEET_TO_MM)

        TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = created_wall
        return created_wall
    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = None
        raise Exception(f"墙体创建失败：{str(e)}")

def create_levels(level_names: list, elevations: list):
    global LAST_EXEC_RESULT
    """
    批量创建标高
    :param level_names: 标高名称列表
    :param elevations: 标高高程列表(mm)
    """
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)
        existing_names = [lvl.Name.strip() for lvl in FilteredElementCollector(doc).OfClass(Level).ToElements()]
        created_levels = []

        # 参数校验
        if len(level_names) != len(elevations):
            raise Exception("标高名称与高程列表长度不匹配")

        for name, elev in zip(level_names, elevations):
            if name.strip() in existing_names:
                raise Exception(f"标高已存在：{name}")
            # 创建标高（使用config中的统一单位常量）
            new_level = Level.Create(doc, elev / FEET_TO_MM)
            new_level.Name = name
            created_levels.append(new_level)

        TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = created_levels
        return created_levels
    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = None
        raise Exception(f"标高创建失败：{str(e)}")

def create_door(wall_id: int = None, x: float = None, y: float = None):
    global LAST_EXEC_RESULT
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)

        # AI传0 → 强制用缓存
        if wall_id == 0: wall_id = None

        wall = None
        # 正确读取：查询返回的是原生元素，不拆包
        if isinstance(LAST_EXEC_RESULT, list) and len(LAST_EXEC_RESULT) > 0:
            wall = LAST_EXEC_RESULT[0]

        if wall is None and wall_id is not None:
            wall = doc.GetElement(ElementId(wall_id))

        if not wall:
            raise Exception("未找到墙体")

        # 门类型
        door_types = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).OfClass(FamilySymbol).ToElements()
        target_type = door_types[0]
        if not target_type.IsActive:
            target_type.Activate()

        # 插入点
        if x is not None and y is not None:
            pt = XYZ(x/FEET_TO_MM, y/FEET_TO_MM, 0)
        else:
            pt = wall.Location.Curve.Evaluate(0.5, True)

        door = doc.Create.NewFamilyInstance(pt, target_type, wall, 0)
        TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = [door]
        return door

    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        raise Exception("创建门失败：" + str(e))

def create_window(wall_id: int = None, x: float = None, y: float = None):
    global LAST_EXEC_RESULT
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)

        if wall_id == 0: wall_id = None

        wall = None
        if isinstance(LAST_EXEC_RESULT, list) and len(LAST_EXEC_RESULT) > 0:
            wall = LAST_EXEC_RESULT[0]

        if wall is None and wall_id is not None:
            wall = doc.GetElement(ElementId(wall_id))

        if not wall:
            raise Exception("未找到墙体")

        win_types = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).OfClass(FamilySymbol).ToElements()
        target_type = win_types[0]
        if not target_type.IsActive:
            target_type.Activate()

        if x is not None and y is not None:
            pt = XYZ(x/FEET_TO_MM, y/FEET_TO_MM, 0)
        else:
            pt = wall.Location.Curve.Evaluate(0.5, True)

        win = doc.Create.NewFamilyInstance(pt, target_type, wall, 0)
        TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = [win]
        return win

    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        raise Exception("创建窗失败：" + str(e))

def create_room(name: str, x: float, y: float, z: float = 0, number: str = None, department: str = None, comments: str = None):
    global LAST_EXEC_RESULT
    """
    在指定位置创建房间
    :param name: 房间名称
    :param x: X坐标（毫米）
    :param y: Y坐标（毫米）
    :param z: Z坐标（毫米），默认0
    :param number: 房间编号（可选）
    :param department: 部门（可选）
    :param comments: 注释（可选）
    :return: 创建的原生Room元素
    """
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)

        pt = XYZ(x / FEET_TO_MM, y / FEET_TO_MM, z / FEET_TO_MM)

        levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
        nearest_level = None
        min_dist = float('inf')
        for level in levels:
            dist = abs(level.Elevation - pt.Z)
            if dist < min_dist:
                min_dist = dist
                nearest_level = level
        if not nearest_level:
            raise Exception("项目中未找到有效标高")

        room = doc.Create.NewRoom(nearest_level, UV(pt.X, pt.Y))
        if not room or not room.IsValidObject:
            raise Exception("房间创建失败，请确保坐标位于封闭区域内")

        room.Name = name
        if number:
            room.Number = number
        if department:
            param = room.LookupParameter("部门") or room.LookupParameter("Department")
            if param and not param.IsReadOnly:
                param.Set(department)
        if comments:
            param = room.LookupParameter("注释") or room.LookupParameter("Comments")
            if param and not param.IsReadOnly:
                param.Set(comments)

        TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = [room]
        return room

    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = None
        raise Exception(f"房间创建失败：{str(e)}")

def create_project_parameter(category_name: str, param_name: str, shared_group: str = "Common", is_instance: bool = True, spec_type = SpecTypeId.String.Text, group_type = GroupTypeId.IdentityData):
    global LAST_EXEC_RESULT
    """
    创建项目参数（项目参数默认作为共享参数存储）
    :param category_name: 类别名称（"房间"、"门"、"窗"）
    :param param_name: 项目参数名称
    :param shared_group: 共享参数分组，默认为"Common"
    :param is_instance: 是否为实例参数（True=实例参数，False=类型参数）
    :param spec_type: 文字类型，默认是文字类型 SpecTypeId.String.Text
    :param group_type: 参数分组，默认是标识数据GroupTypeId.IdentityData 
    """
    # 开启事务
    TransactionManager.Instance.EnsureInTransaction(doc)

    try:
        # 1. 打开共享参数文件
        shared_file = app.OpenSharedParameterFile()
        # ===================== 核心修复：仅加这3行 =====================
        # AI环境无共享文件时，自动创建新的共享参数文件
        if shared_file is None:
            shared_file = app.CreateSharedParameterFile()

        # 2. 获取/创建参数分组
        if shared_file.Groups.get_Item(shared_group):
            param_group = shared_file.Groups.get_Item(shared_group)
        else:
            param_group = shared_file.Groups.Create(shared_group)
            param_group = shared_file.Groups.get_Item(shared_group)

        # 3. 创建参数定义（自动处理重名）
        if not param_group.Definitions.get_Item(param_name):
            opt = ExternalDefinitionCreationOptions(param_name, spec_type)
            param_def = param_group.Definitions.Create(opt)
        else:
            param_def = param_group.Definitions.get_Item(param_name)

        # 4. 绑定门类
        category_set = CategorySet()
        door_category = Category.GetCategory(doc, CATEGORY_MAP[category_name])
        category_set.Insert(door_category)

        # 5. 创建绑定（修正变量名错误）
        binding = InstanceBinding(category_set) if is_instance else TypeBinding(category_set)

        # 6. 写入项目
        doc.ParameterBindings.Insert(param_def, binding, group_type)

        res = "✅ 门类项目参数创建成功，可在「管理→项目参数」中查看"
        LAST_EXEC_RESULT = res
        return res

    except Exception as e:
        res = f"❌ 失败，错误详情: {str(e)}"
        LAST_EXEC_RESULT = res
        return res
    finally:
        # 关闭事务
        TransactionManager.Instance.TransactionTaskDone()


# ==================================================
# 第四部分：常用构件修改工具
# ==================================================

def operate_elements(action: str, element_ids: list = None, transparency_value: int = 50, color: str = "red", rgb: list = None, **kwargs):
    """
    Revit元素批量操作核心函数（隐藏/删除/着色/隔离/透明度）
    优先级：传入ID → 当前选中元素 → 缓存元素 | 自动事务管理 | 异常捕获
    支持中文/英文颜色名：红色/red、绿色/green、蓝色/blue、黄色/yellow...
    """
    global LAST_EXEC_RESULT
    old_cache = LAST_EXEC_RESULT if isinstance(LAST_EXEC_RESULT, list) else []
    
    # 同时兼容 中文 + 英文 颜色键
    COLOR_MAP = {
        "红色": (255, 0, 0), "red": (255, 0, 0),
        "绿色": (0, 255, 0), "green": (0, 255, 0),
        "蓝色": (0, 0, 255), "blue": (0, 0, 255),
        "黄色": (255, 255, 0), "yellow": (255, 255, 0),
        "青色": (0, 255, 255), "cyan": (0, 255, 255),
        "紫色": (128, 0, 128), "purple": (128, 0, 128),
        "白色": (255, 255, 255), "white": (255, 255, 255),
        "黑色": (0, 0, 0), "black": (0, 0, 0),
        "橙色": (255, 165, 0), "orange": (255, 165, 0),
        "灰色": (128, 128, 128), "gray": (128, 128, 128), "grey": (128, 128, 128)
    }
    
    try:
        target_elements = []
        if element_ids == 0:
            element_ids = None

        # 1. 传入ID
        if element_ids and len(element_ids) > 0:
            for eid in element_ids:
                try:
                    elem = doc.GetElement(ElementId(int(eid)))
                    if elem and elem.IsValidObject:
                        target_elements.append(elem)
                except:
                    continue
        # 2. 当前手动选中
        elif len(uidoc.Selection.GetElementIds()) > 0:
            selection_ids = uidoc.Selection.GetElementIds()
            for elem_id in selection_ids:
                elem = doc.GetElement(elem_id)
                if elem and elem.IsValidObject:
                    target_elements.append(elem)
        # 3. 缓存元素
        elif isinstance(old_cache, list) and len(old_cache) > 0:
            target_elements = [elem for elem in old_cache if elem and elem.IsValidObject]

        if not target_elements and action != "ResetIsolate":
            raise Exception("未找到可操作元素，请先选中元素")

        view = doc.ActiveView
        TransactionManager.Instance.EnsureInTransaction(doc)
        result_msg = ""

        if action == "Select":
            elem_id_list = List[ElementId]([elem.Id for elem in target_elements])
            uidoc.Selection.SetElementIds(elem_id_list)
            result_msg = f"✅ 选中成功：{len(target_elements)} 个元素"

        elif action == "Delete":
            delete_list = List[ElementId]([elem.Id for elem in target_elements])
            deleted_count = doc.Delete(delete_list).Count
            result_msg = f"✅ 删除成功：{deleted_count} 个元素"
            target_elements = []

        elif action == "Hide":
            hide_list = List[ElementId]([elem.Id for elem in target_elements])
            view.HideElements(hide_list)
            result_msg = f"✅ 隐藏成功：{len(target_elements)} 个元素"

        elif action == "Isolate":
            isolate_list = List[ElementId]([elem.Id for elem in target_elements])
            view.IsolateElementsTemporary(isolate_list)
            result_msg = f"✅ 隔离成功：{len(target_elements)} 个元素"

        elif action == "Unhide":
            unhide_list = List[ElementId]([elem.Id for elem in target_elements])
            view.UnhideElements(unhide_list)
            result_msg = f"✅ 取消隐藏成功：{len(target_elements)} 个元素"

        elif action == "ResetIsolate":
            view.DisableTemporaryViewMode(TemporaryViewMode.TemporaryHideIsolate)
            result_msg = "✅ 重置隔离/隐藏完成"

        elif action == "SetColor":
            if rgb and len(rgb) == 3 and all(0 <= x <= 255 for x in rgb):
                color_rgb = rgb
                color_name = f"自定义RGB{rgb}"
            else:
                # 统一转小写、去空格，兼容 Yellow / YELLOW / 黄色 各种写法
                color_key = color.strip().lower()
                # 匹配不到默认红色
                color_rgb = COLOR_MAP.get(color_key, COLOR_MAP["red"])
                color_name = color_key

            fill_patterns = FilteredElementCollector(doc).OfClass(FillPatternElement).ToElements()
            solid_fill = next((fp for fp in fill_patterns if fp.GetFillPattern().IsSolidFill), None)
            if not solid_fill:
                raise Exception("未找到实体填充图案")
            fill_pattern_id = solid_fill.Id

            target_color = Color(color_rgb[0], color_rgb[1], color_rgb[2])
            ogs = OverrideGraphicSettings()
            ogs.SetSurfaceForegroundPatternId(fill_pattern_id)
            ogs.SetSurfaceForegroundPatternColor(target_color)
            ogs.SetCutForegroundPatternId(fill_pattern_id)
            ogs.SetCutForegroundPatternColor(target_color)
            ogs.SetProjectionLineColor(target_color)

            success_count = 0
            for elem in target_elements:
                try:
                    view.SetElementOverrides(elem.Id, ogs)
                    success_count += 1
                except:
                    continue
            result_msg = f"✅ 着色成功：{success_count} 个元素，颜色：{color_name}"

        elif action == "SetTransparency":
            ogs = OverrideGraphicSettings()
            ogs.SetSurfaceTransparency(transparency_value)
            success_count = 0
            for elem in target_elements:
                try:
                    view.SetElementOverrides(elem.Id, ogs)
                    success_count += 1
                except:
                    continue
            result_msg = f"✅ 透明度设置成功：{success_count} 个元素，值：{transparency_value}%"

        else:
            raise Exception(f"不支持的操作：{action}")

        TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = target_elements
        return result_msg

    except Exception as e:
        try:
            TransactionManager.Instance.TransactionTaskDone()
        except:
            pass
        LAST_EXEC_RESULT = old_cache
        raise Exception(f"元素操作失败：{str(e)}")

def batch_modify_element_param_text(
    category_name: str,
    operation: str,
    target_param_name: str,
    old_text: str = None,
    new_text: str = None,
    position: int = 0,
    count: int = 0,
    active_view_only: bool = False,
    replace_mode: str = "all"  # 新增：替换模式 默认全部替换
):
    global LAST_EXEC_RESULT
    """
    批量修改元素参数文本（增强版：支持插入/删除/替换，替换可指定模式）
    :param category_name: 类别名称（"房间"、"门"、"窗"）
    :param operation: 操作类型（"insert"：插入文本，"remove"：删除文本，"replace"：替换文本）
    :param target_param_name: 要修改的目标参数名称
    :param old_text: 【replace必填】要替换的旧文本
    :param new_text: 【insert/replace必填】要插入/替换的新文本
    :param position: 【insert/remove必填】文本插入/删除的索引位置（0表示开头）
    :param count: 【remove必填】删除的字符数
    :param active_view_only: 是否仅获取当前视图中的元素（默认False：获取整个项目）
    :param replace_mode: 【replace选填】替换模式，all=全部替换(默认)，first=替换第一个，last=替换最后一个
    """
    # 校验操作类型
    if operation not in ["insert", "remove", "replace"]:
        res = f"❌ 不支持的操作类型：{operation}，支持的操作：insert（插入）、remove（删除）、replace（替换）"
        LAST_EXEC_RESULT = res
        return res

    # 校验替换模式（仅replace生效）
    if operation == "replace" and replace_mode not in ["all", "first", "last"]:
        res = f"❌ 不支持的替换模式：{replace_mode}，支持：all(全部)、first(第一个)、last(最后一个)"
        LAST_EXEC_RESULT = res
        return res

    # 校验类别
    if category_name not in CATEGORY_MAP:
        res = f"❌ 不支持的类别：{category_name}，支持的类别：房间、门、窗"
        LAST_EXEC_RESULT = res
        return res

    # 校验操作必填参数
    if operation == "insert":
        if new_text is None or not isinstance(new_text, str):
            res = f"❌ insert操作必须传入new_text（字符串格式）"
            LAST_EXEC_RESULT = res
            return res
    elif operation == "remove":
        if count <= 0 or not isinstance(count, int):
            res = f"❌ remove操作必须传入count（正整数格式）"
            LAST_EXEC_RESULT = res
            return res
    elif operation == "replace":
        if old_text is None or new_text is None:
            res = f"❌ replace操作必须传入old_text和new_text"
            LAST_EXEC_RESULT = res
            return res

    try:
        TransactionManager.Instance.EnsureInTransaction(doc)

        # 1. 构建收集器
        if active_view_only:
            collector = FilteredElementCollector(doc, doc.ActiveView.Id)
        else:
            collector = FilteredElementCollector(doc)

        # 2. 获取并过滤元素
        elements = collector.OfCategory(CATEGORY_MAP[category_name]).WhereElementIsNotElementType().ToElements()
        valid_elements = []

        if category_name in ["房间", "rooms"]:
            # 房间过滤：有位置、面积>0
            for elem in elements:
                if elem is not None and elem.Location is not None and elem.Area > 0:
                    valid_elements.append(elem)
        elif category_name in ["门", "窗", "doors", "windows"]:
            # 门/窗过滤：有宿主墙
            for elem in elements:
                if elem is not None and elem.Host is not None:
                    valid_elements.append(elem)

        if not valid_elements:
            TransactionManager.Instance.TransactionTaskDone()
            res = f"❌ 未找到有效{category_name}元素"
            LAST_EXEC_RESULT = res
            return res

        # 3. 转成Dynamo兼容类型
        dyn_elements = [elem.ToDSType(True) for elem in valid_elements]

        # 4. 遍历元素，修改参数
        updated_param_values = []

        try:
            # 首先尝试实例参数
            for elem in dyn_elements:
                original_value = elem.GetParameterValueByName(target_param_name)
                original_str = str(original_value)
                updated_value = original_value

                if operation == "insert":
                    updated_value = DSCore.String.Insert(original_str, position, new_text)
                elif operation == "remove":
                    updated_value = DSCore.String.Remove(original_str, position, count)
                elif operation == "replace":
                    # 核心修复：根据替换模式执行
                    if replace_mode == "first":
                        # 替换第一个匹配项
                        updated_value = original_str.replace(old_text, new_text, 1)
                    elif replace_mode == "last":
                        # 替换最后一个匹配项（反转字符串→替换第一个→反转回来）
                        updated_value = original_str[::-1].replace(old_text[::-1], new_text[::-1], 1)[::-1]
                    else:
                        # 默认全部替换
                        updated_value = original_str.replace(old_text, new_text)
                
                elem.SetParameterByName(target_param_name, updated_value)
                updated_param_values.append(updated_value)
        except:
            # 再次尝试类型参数
            elem_types = [elem.ElementType for elem in dyn_elements]
            dyn_elements = DSCore.List.UniqueItems(elem_types)
            for elem in dyn_elements:
                original_value = elem.GetParameterValueByName(target_param_name)
                original_str = str(original_value)
                updated_value = original_value

                if operation == "insert":
                    updated_value = DSCore.String.Insert(original_str, position, new_text)
                elif operation == "remove":
                    updated_value = DSCore.String.Remove(original_str, position, count)
                elif operation == "replace":
                    # 核心修复：根据替换模式执行
                    if replace_mode == "first":
                        updated_value = original_str.replace(old_text, new_text, 1)
                    elif replace_mode == "last":
                        updated_value = original_str[::-1].replace(old_text[::-1], new_text[::-1], 1)[::-1]
                    else:
                        updated_value = original_str.replace(old_text, new_text)
                
                elem.SetParameterByName(target_param_name, updated_value)
                updated_param_values.append(updated_value)

        TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = updated_param_values
        return f"✅ 批量修改成功，共修改{len(updated_param_values)}个元素"

    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        res = f"❌ 批量修改失败: {str(e)}"
        LAST_EXEC_RESULT = res
        return res

def batch_modify_element_param_text_by_family(
    family_name: str,
    type_name: str,
    operation: str,
    target_param_name: str,
    old_text: str = None,
    new_text: str = None,
    position: int = 0,
    count: int = 0,
    replace_mode: str = "all" 
):
    global LAST_EXEC_RESULT
    """
    批量修改元素参数文本（按族+类型，支持插入/删除/替换）
    :param family_name: 族名称
    :param type_name: 类型名称
    :param operation: 操作类型（insert：插入，remove：删除，replace：替换）
    :param target_param_name: 要修改的目标参数名称
    :param old_text: 【replace必填】要替换的旧文本
    :param new_text: 【insert/replace必填】要插入/替换的新文本
    :param position: 【insert/remove必填】文本插入/删除的索引位置
    :param count: 【remove必填】删除的字符数
    :param replace_mode: 替换模式，all=全部，first=第一个，last=最后一个
    """
    # 校验操作类型
    if operation not in ["insert", "remove", "replace"]:
        res = f"❌ 不支持的操作类型：{operation}，支持：insert、remove、replace"
        LAST_EXEC_RESULT = res
        return res

    # 校验替换模式
    if operation == "replace" and replace_mode not in ["all", "first", "last"]:
        res = f"❌ 替换模式仅支持：all、first、last"
        LAST_EXEC_RESULT = res
        return res

    # 校验必填参数
    if operation == "insert":
        if not new_text:
            res = "❌ insert必须传入new_text"
            LAST_EXEC_RESULT = res
            return res
    elif operation == "remove":
        if count <= 0:
            res = "❌ remove必须传入正整数count"
            LAST_EXEC_RESULT = res
            return res
    elif operation == "replace":
        if not old_text or not new_text:
            res = "❌ replace必须传入old_text和new_text"
            LAST_EXEC_RESULT = res
            return res

    try:
        TransactionManager.Instance.EnsureInTransaction(doc)

        # 获取族类型+实例
        fam_type = Revit.Elements.FamilyType.ByFamilyNameAndTypeName(family_name, type_name)
        dyn_elements = Revit.Elements.FamilyInstance.ByFamilyType(fam_type)

        updated_param_values = []
        # 修改实例参数
        try:
            for elem in dyn_elements:
                original_str = str(elem.GetParameterValueByName(target_param_name))
                if operation == "insert":
                    val = DSCore.String.Insert(original_str, position, new_text)
                elif operation == "remove":
                    val = DSCore.String.Remove(original_str, position, count)
                else:
                    if replace_mode == "first":
                        val = original_str.replace(old_text, new_text, 1)
                    elif replace_mode == "last":
                        val = original_str[::-1].replace(old_text[::-1], new_text[::-1], 1)[::-1]
                    else:
                        val = original_str.replace(old_text, new_text)
                elem.SetParameterByName(target_param_name, val)
                updated_param_values.append(val)
        # 修改类型参数
        except:
            elem_types = DSCore.List.UniqueItems([elem.ElementType for elem in dyn_elements])
            for elem in elem_types:
                original_str = str(elem.GetParameterValueByName(target_param_name))
                if operation == "insert":
                    val = DSCore.String.Insert(original_str, position, new_text)
                elif operation == "remove":
                    val = DSCore.String.Remove(original_str, position, count)
                else:
                    if replace_mode == "first":
                        val = original_str.replace(old_text, new_text, 1)
                    elif replace_mode == "last":
                        val = original_str[::-1].replace(old_text[::-1], new_text[::-1], 1)[::-1]
                    else:
                        val = original_str.replace(old_text, new_text)
                elem.SetParameterByName(target_param_name, val)
                updated_param_values.append(val)

        TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = updated_param_values
        return f"✅ 批量修改成功，共修改{len(updated_param_values)}个元素"

    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        res = f"❌ 批量修改失败: {str(e)}"
        LAST_EXEC_RESULT = res
        return res


def move_element(element_id=None, dx=0, dy=0, dz=0):
    global LAST_EXEC_RESULT
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)

        # AI传0 → 强制无视
        if element_id == 0:
            element_id = None

        elem = None
        # 正确读取原生元素
        if isinstance(LAST_EXEC_RESULT, list) and len(LAST_EXEC_RESULT) > 0:
            elem = LAST_EXEC_RESULT[0]

        if elem is None and element_id is not None:
            elem = doc.GetElement(ElementId(element_id))

        if not elem or not elem.Location:
            raise Exception("未找到可移动元素")

        vec = XYZ(dx/FEET_TO_MM, dy/FEET_TO_MM, dz/FEET_TO_MM)
        elem.Location.Move(vec)

        TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = [elem]
        return elem

    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        raise Exception("移动失败：" + str(e))

def rotate_element(element_id=None, x=0, y=0, angle=0):
    global LAST_EXEC_RESULT
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)

        if element_id == 0:
            element_id = None

        elem = None
        if isinstance(LAST_EXEC_RESULT, list) and len(LAST_EXEC_RESULT) > 0:
            elem = LAST_EXEC_RESULT[0]

        if elem is None and element_id is not None:
            elem = doc.GetElement(ElementId(element_id))

        if not elem:
            raise Exception("未找到可旋转元素")

        center = XYZ(x/FEET_TO_MM, y/FEET_TO_MM, 0)
        axis = Line.CreateBound(center, XYZ(center.X, center.Y, center.Z+1))
        ElementTransformUtils.RotateElement(doc, elem.Id, axis, math.radians(angle))

        TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = [elem]
        return elem

    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        raise Exception("旋转失败：" + str(e))

def delete_element(element_id=None):
    global LAST_EXEC_RESULT
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)

        if element_id == 0:
            element_id = None

        elem = None
        if isinstance(LAST_EXEC_RESULT, list) and len(LAST_EXEC_RESULT) > 0:
            elem = LAST_EXEC_RESULT[0]

        if elem is None and element_id is not None:
            elem = doc.GetElement(ElementId(element_id))

        if not elem:
            raise Exception("未找到可删除元素")

        doc.Delete(elem.Id)
        TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = []
        return "删除成功"

    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        raise Exception("删除失败：" + str(e))

def set_element_parameter(element_id: int = None, param_name: str = None, param_value: str = None):
    global LAST_EXEC_RESULT
    """
    智能设置元素参数（批量+按需单位转换）
    规则：字符串/整数参数直接赋值 | 长度类浮点参数自动转换mm→英尺
    """
    try:
        if not param_name:
            raise Exception("❌ 必须传入 param_name 参数名称")

        TransactionManager.Instance.EnsureInTransaction(doc)
        
        target_elems = []
        # 获取要修改的元素（批量缓存元素）
        if element_id is None:
            if LAST_EXEC_RESULT and len(LAST_EXEC_RESULT) > 0:
                target_elems = LAST_EXEC_RESULT
            else:
                raise Exception("❌ 未查询到任何元素，请先执行查询工具")
        else:
            elem = doc.GetElement(ElementId(element_id))
            if not elem:
                raise Exception(f"❌ 未找到元素：{element_id}")
            target_elems = [elem]

        success_count = 0
        error_msgs = []
        
        for elem in target_elems:
            try:
                param = elem.LookupParameter(param_name)
                if not param:
                    error_msgs.append(f"元素{elem.Id}：未找到参数 {param_name}")
                    continue

                # ==============================================
                # 核心规则：按需赋值，智能单位转换
                # ==============================================
                # 1. 字符串参数（数字文本/普通文本）：直接赋值，不转换
                if param.StorageType == StorageType.String:
                    param.Set(param_value.strip())

                # 2. 整数参数：直接赋值
                elif param.StorageType == StorageType.Integer:
                    param.Set(int(float(param_value)))

                # 3. 浮点参数（长度/尺寸）：毫米 → Revit内部单位（英尺）
                elif param.StorageType == StorageType.Double:
                    # 清理输入值（去掉 mm / 空格 等单位符号）
                    clean_val = float(''.join(filter(lambda x: x.isdigit() or x == '.', param_value)))
                    # 单位转换：毫米 → 内部单位
                    final_val = UnitUtils.ConvertToInternalUnits(clean_val, ForgeTypeId('autodesk.unit.unit:millimeters-1.0.1'))
                    param.Set(final_val)

                success_count += 1

            except Exception as e:
                error_msgs.append(f"元素{elem.Id}：{str(e)}")

        TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = target_elems

        # 返回结果
        if error_msgs:
            return f"⚠️ 完成：成功{success_count}个，失败{len(error_msgs)}个"
        return f"✅ 批量设置成功：{success_count}个元素 | {param_name} = {param_value}"

    except Exception as e:
        if TransactionManager.Instance.HasTransactionStarted():
            TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = None
        raise Exception(f"❌ 设置失败：{str(e)}")
        

# ==================================================
# 第五部分：消防疏散路径工具
# ==================================================
def evacuation_paths_door2exit():
    global LAST_EXEC_RESULT
    """创建从房间疏散门到安全出口的消防疏散路线"""
    collector = FilteredElementCollector(doc, doc.ActiveView.Id)
    doors = list(collector.OfCategory(BuiltInCategory.OST_Doors)\
            .WhereElementIsNotElementType().ToElements())

    param_name = "DEvacuationSign"
    # 毫秒级检查参数（替代原低效遍历）
    try:
        # 直接取一个门测试参数，最快方式
        test_door = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().FirstElement()
        if test_door and test_door.LookupParameter(param_name):
            exist = True
        else:
            exist = False
    except:
        exist = False

    if not exist:
        create_project_parameter(category_name = "doors", param_name = "DEvacuationSign", shared_group = "Evacuation", is_instance = True, spec_type = SpecTypeId.String.Text, group_type = GroupTypeId.IdentityData)

        tip_text = f"""【参数已自动创建成功！】
已为门创建项目参数：{param_name}
请按以下步骤赋值后重新运行脚本：
1. 选中【房间疏散门】→ 属性面板赋值：EvacuationDoor
2. 选中【安全出口门】→ 属性面板赋值：EvacuationExit
3. 赋值完成后重新运行"""
        TaskDialog.Show("参数创建完成", tip_text)
        LAST_EXEC_RESULT = tip_text
        return tip_text

    dyn_doors = [door.ToDSType(True) for door in doors]
    active_view = doc.ActiveView.ToDSType(True)
    door_mask_start = []
    door_mask_end = []
    for door in dyn_doors:
        door_mask_start.append(door.GetParameterValueByName("DEvacuationSign")=="EvacuationDoor")
        door_mask_end.append(door.GetParameterValueByName("DEvacuationSign")=="EvacuationExit")

    filter_doors_start_dict = DSCore.List.FilterByBoolMask(dyn_doors, door_mask_start)
    filter_doors_start = filter_doors_start_dict["in"]
    filter_doors_end_dict = DSCore.List.FilterByBoolMask(dyn_doors, door_mask_end)
    filter_doors_end = filter_doors_end_dict["in"]

    # ====================== 新增：空值提示优化 ======================
    # 检查房间疏散门数量
    if len(filter_doors_start) == 0:
        tip_text = """未找到【DEvacuationSign】为「EvacuationDoor」的门！
请检查门参数设置，步骤如下：
1. 选中房间疏散门
2. 在属性面板找到【DEvacuationSign】参数
3. 赋值为：EvacuationDoor
4. 确认赋值完成

设置完成后重新运行脚本！"""
        TaskDialog.Show("参数缺失提示", tip_text)
        LAST_EXEC_RESULT = tip_text
        return tip_text

    # 检查安全出口门数量
    if len(filter_doors_end) == 0:
        tip_text = """未找到【DEvacuationSign】为「EvacuationExit」的门！
请检查门参数设置，步骤如下：
1. 选中安全出口门
2. 在属性面板找到【DEvacuationSign】参数
3. 赋值为：EvacuationExit
4. 确认赋值完成

设置完成后重新运行脚本！"""
        TaskDialog.Show("参数缺失提示", tip_text)
        LAST_EXEC_RESULT = tip_text
        return tip_text

    elements_start = DSCore.List.Flatten(filter_doors_start)
    # 获取行进路径的起点与终点
    start_pts = []
    for element in elements_start:
        try:
            start_pts.append(element.GetLocation())
        except:
            start_pts.append(element.BoundingBox.ContextCoordinateSystem.Origin)
    end_pts = []
    for door in filter_doors_end:
        try:
            end_pts.append(door.GetLocation())
        except:
            end_pts.append(door.BoundingBox.ContextCoordinateSystem.Origin)

    # 创建行进路径
    paths = []
    for start_pt in start_pts:
        for end_pt in end_pts:
            paths.append(Revit.Elements.PathOfTravel.ByFloorPlanPoints(active_view, [start_pt], [end_pt], False))
    paths_flatten = DSCore.List.Flatten(paths)

    # 分组路径
    path_to_group = DSCore.List.Chop(paths, [len(end_pts)])
    for i in range(len(path_to_group)):
        path_to_group[i] = DSCore.List.Flatten(path_to_group[i])

    # 筛选路径
    path_to_del = []
    path_of_travel = []
    for path in path_to_group:
        values = []
        for i in range(len(path)):
            print(path)
            values.append(path[i].GetParameterValueByName("长度"))
        j = values.index(min(values))
        path_of_travel.append(path[j])
    path_to_del = [x for x in paths_flatten if x not in path_of_travel]
    for path in path_to_del:
        Revit.Elements.Element.Delete(path)

    LAST_EXEC_RESULT = path_of_travel
    return path_of_travel

def evacuation_paths_room2exit():
    global LAST_EXEC_RESULT
    """创建从房间内部最远点到安全出口的消防疏散路线"""
    # --------------------------
    # 独立的收集器，分别收集
    # --------------------------
    room_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType()
    rooms_all = list(room_collector.ToElements())

    door_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType()
    doors_all = list(door_collector.ToElements())

    dyn_doors = [door.ToDSType(True) for door in doors_all]
    dyn_rooms = [room.ToDSType(True) for room in rooms_all]
    active_view = doc.ActiveView.ToDSType(True)

    param_door = "DEvacuationSign"
    # 毫秒级检查参数（替代原低效遍历）
    try:
        # 直接取一个门测试参数，最快方式
        test_door = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().FirstElement()
        if test_door and test_door.LookupParameter(param_door):
            exist = True
        else:
            exist = False
    except:
        exist = False

    if not exist:
        create_project_parameter(category_name = "doors", param_name = "DEvacuationSign", shared_group = "Evacuation", is_instance = True, spec_type = SpecTypeId.String.Text, group_type = GroupTypeId.IdentityData)
        
        tip_text = f"""【参数已自动创建成功！】
1. 已为门创建项目参数：{param_door}
2. 请赋值安全出口门为：EvacuationExit
3. 赋值完成后重新运行脚本！"""
        TaskDialog.Show("参数创建完成", tip_text)
        LAST_EXEC_RESULT = tip_text
        return tip_text
        
    param_room = "REvacuationSign"
    # 毫秒级检查参数（替代原低效遍历）
    try:
        # 直接取一个房间测试参数，最快方式
        test_room = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().FirstElement()
        if test_room and test_room.LookupParameter(param_room):
            exist = True
        else:
            exist = False
    except:
        exist = False

    if not exist:
        create_project_parameter(category_name = "rooms", param_name = "REvacuationSign", shared_group = "Evacuation", is_instance = True, spec_type = SpecTypeId.String.Text, group_type = GroupTypeId.IdentityData)
        
        tip_text = f"""【参数已自动创建成功！】
1. 已为房间创建项目参数：{param_room}
2. 请赋值需要计算疏散的房间为：EvacuationRoute
3. 赋值完成后重新运行脚本！"""
        TaskDialog.Show("参数创建完成", tip_text)
        LAST_EXEC_RESULT = tip_text
        return tip_text
        
    # --------------------------
    # 参数过滤
    # --------------------------
    mask = []
    for room in dyn_rooms:
        mask.append(room.GetParameterValueByName('REvacuationSign') == "EvacuationRoute")
    rooms = DSCore.List.FilterByBoolMask(dyn_rooms, mask)['out']
    rooms_check = DSCore.List.FilterByBoolMask(dyn_rooms, mask)['in']

    mask = []
    for door in dyn_doors:
        mask.append(door.GetParameterValueByName('DEvacuationSign') == "EvacuationExit")
    doors = DSCore.List.FilterByBoolMask(dyn_doors, mask)['in']

    # --------------------------
    # 【新增优化】空值检查 + TaskDialog提示
    # --------------------------
    if len(doors) == 0:
        warning_messages = """未找到【DEvacuationSign】参数为「EvacuationExit」的门！
请检查门参数设置，步骤如下：
1. 选中项目中的安全出口门
2. 在属性面板中找到【DEvacuationSign】参数
3. 赋值为：EvacuationExit
4. 确认参数赋值完成
提示：
房间【REvacuationSign】参数为「EvacuationRoute」，不计算疏散路径！

设置完成后重新运行脚本！"""
        TaskDialog.Show("参数设置提示", warning_messages)
        LAST_EXEC_RESULT = warning_messages
        return warning_messages

    # --------------------------
    # 原有逻辑：获取房间的边界点
    # --------------------------
    room_curves = []
    for room in rooms:
        room_curves.append(room.FinishBoundary)

    poly_curves = []
    for item in room_curves:
        poly_curves.append(PolyCurve.ByJoinedCurves(item[0]))

    # 此处偏移值默认为-300，可根据需要适当调整.
    room_pts = []
    for item in poly_curves:
        room_pts.append(item.Offset(-300).Points)

    # --------------------------
    # 原有逻辑：获取门的定位点
    # --------------------------
    door_pts = []
    for door in doors:
        try:
            door_pts.append(door.GetLocation())
        except:
            bounding_box = door.BoundingBox
            door_pts.append(bounding_box.ContextCoordinateSystem.Origin)

    # --------------------------
    # 原有逻辑：生成路径,删除多余路径
    # --------------------------
    path_of_travel = []
    # 仅在房间和门都不为空时执行路径生成
    if len(rooms) > 0 and len(doors) > 0:
        for room_pt in room_pts:
            filter_paths = []
            for door_pt in door_pts:
                paths = []
                lens = []
                for pt in room_pt:
                    path = Revit.Elements.PathOfTravel.ByFloorPlanPoints(active_view, [pt], [door_pt], False)
                    if not DSCore.Object.IsNull(path[0]):
                        length = path[0].GetParameterValueByName('长度')
                        if length is not None:
                            lens.append(length)
                            paths.append(path[0])
                # 检查是否有效路径
                if not lens:
                    continue
                index = lens.index(max(lens))
                path_to_del = DSCore.List.RemoveItemAtIndex(paths, [index])

                for path in path_to_del:
                    Revit.Elements.Element.Delete(path)
                filter_paths.append(paths[index])
            if not filter_paths:
                continue
            lens = []
            for path in filter_paths:
                lens.append(path.GetParameterValueByName('长度'))
            index = lens.index(min(lens))
            path_of_travel.append(filter_paths[index])
            path_to_del = DSCore.List.RemoveItemAtIndex(filter_paths, [index])
            for path in path_to_del:
                Revit.Elements.Element.Delete(path)

    # --------------------------
    # 输出结果
    # --------------------------
    OUT = doors, rooms, path_of_travel
    LAST_EXEC_RESULT = OUT
    return OUT

# ==================================================
# 第六部分：房间管理优化工具
# ==================================================
def center_rooms():
    global LAST_EXEC_RESULT
    """当前视图中所有房间位置基于几何形心（中心）"""
    # 收集当前视图的房间，提前过滤无效元素
    collector = FilteredElementCollector(doc, doc.ActiveView.Id)
    rooms = list(collector
                 .OfCategory(BuiltInCategory.OST_Rooms)
                 .WhereElementIsNotElementType()
                 .ToElements())

    if not rooms:
        print("⚠️ 当前视图未找到任何有效房间")
        res = []
        LAST_EXEC_RESULT = res
        return res

    # 事务初始化
    TransactionManager.Instance.EnsureInTransaction(doc)
    modified_count = 0
    failed_count = 0
    try:
        for room in rooms:
            # 单个房间异常隔离：单个房间出错不打断整体循环
            try:
                # --------------------------
                # 第一层校验：房间基础有效性
                # --------------------------
                if not room:
                    print(f"跳过空房间对象，ID：{room.Id if room else '未知'}")
                    failed_count += 1
                    continue

                # 拆解链式访问，避免属性读取报错
                room_level = room.Level
                if not room_level:
                    print(f"跳过无标高房间，ID：{room.Id}")
                    failed_count += 1
                    continue

                room_location = room.Location
                if not room_location or not isinstance(room_location, LocationPoint):
                    print(f"跳过无有效位置的房间，ID：{room.Id}")
                    failed_count += 1
                    continue

                current_point = room_location.Point
                if not current_point:
                    print(f"跳过无坐标点的房间，ID：{room.Id}")
                    failed_count += 1
                    continue

                # --------------------------
                # 第二层校验：房间几何有效性（全版本兼容，移除IsEmpty）
                # --------------------------
                # 配置几何选项，兼容全版本Revit
                geo_options = Options()
                geo_options.ComputeReferences = True
                geo_options.DetailLevel = ViewDetailLevel.Fine
                geo_options.IncludeNonVisibleObjects = False

                # 读取房间几何，仅做空值判断，移除不兼容的IsEmpty
                geo_elem = room.get_Geometry(geo_options)
                if not geo_elem:
                    print(f"跳过无有效几何的房间，ID：{room.Id}")
                    failed_count += 1
                    continue

                # 遍历几何，找到有效实心实体（兼容全版本）
                room_centroid = None
                for geo_obj in geo_elem:
                    # 增加非空校验，避免无效几何对象
                    if geo_obj and isinstance(geo_obj, Solid) and geo_obj.Volume > 1e-6:
                        room_centroid = geo_obj.ComputeCentroid()
                        break

                # 遍历后无有效实体，判定为无效房间
                if not room_centroid:
                    room_num = room.Number if hasattr(room, "Number") else "无编号"
                    room_name = room.Name if hasattr(room, "Name") else "无名称"
                    print(f"跳过无有效实体的房间：{room_num} - {room_name}，ID：{room.Id}")
                    failed_count += 1
                    continue

                # --------------------------
                # 坐标计算与位置修正
                # --------------------------
                level_elevation = room_level.Elevation
                # 用完全限定名创建XYZ，确保类型统一
                new_center = XYZ(room_centroid.X, room_centroid.Y, level_elevation)

                # 手动计算位移向量，彻底避开类型冲突
                move_vector = XYZ(
                    new_center.X - current_point.X,
                    new_center.Y - current_point.Y,
                    new_center.Z - current_point.Z
                )

                # 仅当位移超过阈值时执行移动，避免无效操作
                if move_vector.GetLength() > 0.001:
                    room_location.Move(move_vector)
                    modified_count += 1
                    room_num = room.Number if hasattr(room, "Number") else "无编号"
                    room_name = room.Name if hasattr(room, "Name") else "无名称"
                    print(f"✅ 已修正房间位置：{room_num} - {room_name}")

            except Exception as room_err:
                # 单个房间的异常捕获，不影响整体循环
                failed_count += 1
                print(f"❌ 处理房间ID {room.Id} 失败：{str(room_err)}")
                continue

        # 提交事务
        TransactionManager.Instance.TransactionTaskDone()
        print(f"🎉 执行完成：共扫描{len(rooms)}个房间，成功修正{modified_count}个，处理失败{failed_count}个")

    except Exception as global_err:
        # 全局异常捕获，事务回滚
        if t.HasStarted():
            t.RollBack()
        error_msg = f"全局执行失败：{str(global_err)}"
        print(error_msg)
        UI.TaskDialog.Show("错误", error_msg)
        LAST_EXEC_RESULT = None
        raise

    LAST_EXEC_RESULT = rooms
    return rooms

def room_tags_move_to_room_location():
    global LAST_EXEC_RESULT
    """当前视图中所有房间标记与房间位置对齐"""
    collector = FilteredElementCollector(doc, doc.ActiveView.Id)
    tags = collector.OfClass(SpatialElementTag).ToElements()

    TransactionManager.Instance.EnsureInTransaction(doc)
    processed_tags = []
    for tag in tags:
        # 仅处理房间标签
        if not hasattr(tag, "Room") or tag.Room is None:
            continue
        room_center = tag.Room.Location.Point
        tag_current_pos = tag.Location.Point
        move_vector = room_center.Subtract(tag_current_pos)
        tag.Location.Move(move_vector)
        processed_tags.append(tag)

    TransactionManager.Instance.TransactionTaskDone()
    LAST_EXEC_RESULT = processed_tags
    return processed_tags


# ==================================================
# 第七部分：可视化与标记工具
# ==================================================
# ----------------------
# 房间标记函数
# ----------------------
def tag_rooms():
    global LAST_EXEC_RESULT
    """
    为当前视图中的所有房间添加标记
    :return: 执行结果提示
    """
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)

        # 1. 获取有效房间
        rooms = FilteredElementCollector(doc, doc.ActiveView.Id)\
            .OfCategory(BuiltInCategory.OST_Rooms)\
            .WhereElementIsNotElementType()\
            .ToElements()
        valid_rooms = [r for r in rooms if r.Location and r.Area > 0]
        if not valid_rooms:
            raise Exception("当前视图无有效房间")

        # 2. 获取房间标记类型
        room_tag_types = FilteredElementCollector(doc)\
            .OfCategory(BuiltInCategory.OST_RoomTags)\
            .OfClass(FamilySymbol)\
            .ToElements()
        if not room_tag_types:
            raise Exception("项目中无房间标记族，请先加载")
        tag_type = room_tag_types[0]

        # 3. 批量创建标记
        count = 0
        for room in valid_rooms:
            room_ref = Reference(room)
            room_point = room.Location.Point
            tag = IndependentTag.Create(
                doc, tag_type.Id, doc.ActiveView.Id,
                room_ref, True, TagOrientation.Horizontal, room_point
            )
            count += 1

        TransactionManager.Instance.TransactionTaskDone()
        res = f"✅ 房间标记完成，共创建{count}个"
        LAST_EXEC_RESULT = res
        return res
    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        res = f"❌ 房间标记失败：{str(e)}"
        LAST_EXEC_RESULT = res
        return res

# ----------------------
# 门标记函数
# ----------------------
def tag_doors():
    global LAST_EXEC_RESULT
    """
    为当前视图中的所有门添加标记
    :return: 执行结果提示
    """
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)

        doors = FilteredElementCollector(doc, doc.ActiveView.Id)\
            .OfCategory(BuiltInCategory.OST_Doors)\
            .WhereElementIsNotElementType()\
            .ToElements()
        valid_doors = [d for d in doors if d.Location]
        if not valid_doors:
            raise Exception("当前视图无有效门构件")

        door_tag_types = FilteredElementCollector(doc)\
            .OfCategory(BuiltInCategory.OST_DoorTags)\
            .OfClass(FamilySymbol)\
            .ToElements()
        if not door_tag_types:
            raise Exception("项目中无门标记族，请先加载")
        tag_type = door_tag_types[0]

        count = 0
        for door in valid_doors:
            door_ref = Reference(door)
            door_point = door.Location.Point
            tag = IndependentTag.Create(
                doc, tag_type.Id, doc.ActiveView.Id,
                door_ref, True, TagOrientation.Horizontal, door_point
            )
            count += 1

        TransactionManager.Instance.TransactionTaskDone()
        res = f"✅ 门标记完成，共创建{count}个"
        LAST_EXEC_RESULT = res
        return res
    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        res = f"❌ 门标记失败：{str(e)}"
        LAST_EXEC_RESULT = res
        return res

# ----------------------
# 窗标记函数
# ----------------------
def tag_windows():
    global LAST_EXEC_RESULT
    """
    为当前视图中的所有窗添加标记
    :return: 执行结果提示
    """
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)

        windows = FilteredElementCollector(doc, doc.ActiveView.Id)\
            .OfCategory(BuiltInCategory.OST_Windows)\
            .WhereElementIsNotElementType()\
            .ToElements()
        valid_windows = [w for w in windows if w.Location]
        if not valid_windows:
            raise Exception("当前视图无有效窗构件")

        window_tag_types = FilteredElementCollector(doc)\
            .OfCategory(BuiltInCategory.OST_WindowTags)\
            .OfClass(FamilySymbol)\
            .ToElements()
        if not window_tag_types:
            raise Exception("项目中无窗标记族，请先加载")
        tag_type = window_tag_types[0]

        count = 0
        for window in valid_windows:
            window_ref = Reference(window)
            window_point = window.Location.Point
            tag = IndependentTag.Create(
                doc, tag_type.Id, doc.ActiveView.Id,
                window_ref, True, TagOrientation.Horizontal, window_point
            )
            count += 1

        TransactionManager.Instance.TransactionTaskDone()
        res = f"✅ 窗标记完成，共创建{count}个"
        LAST_EXEC_RESULT = res
        return res
    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        res = f"❌ 窗标记失败：{str(e)}"
        LAST_EXEC_RESULT = res
        return res

# ----------------------
# 墙标记函数
# ----------------------
def tag_all_walls():
    global LAST_EXEC_RESULT
    """
    为当前视图中的所有墙体添加标记
    :return: 执行结果提示
    """
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)
        view = doc.ActiveView

        wall_tag_types = FilteredElementCollector(doc)\
            .OfCategory(BuiltInCategory.OST_WallTags).OfClass(FamilySymbol).ToElements()
        if not wall_tag_types:
            raise Exception("项目中没有找到可用的墙体标记族，请先加载")
        tag_type = wall_tag_types[0]
        if not tag_type.IsActive:
            tag_type.Activate()

        walls = FilteredElementCollector(doc, view.Id)\
            .OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
        valid_walls = [w for w in walls if w.Location and w.IsValidObject]
        if not valid_walls:
            raise Exception("当前视图未找到有效墙体")

        count = 0
        for wall in valid_walls:
            try:
                wall_ref = Reference(wall)
                wall_curve = wall.Location.Curve
                tag_pt = wall_curve.Evaluate(0.5, True)
                IndependentTag.Create(
                    doc, tag_type.Id, view.Id,
                    wall_ref, True, TagOrientation.Horizontal, tag_pt
                )
                count += 1
            except:
                continue

        TransactionManager.Instance.TransactionTaskDone()
        res = f"✅ 墙体标记完成，共创建{count}个标记"
        LAST_EXEC_RESULT = res
        return res

    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        LAST_EXEC_RESULT = None
        raise Exception(f"墙体标记失败：{str(e)}")


# ==================================================
# 第八部分：轴网管理工具
# ==================================================
def create_grids(vertical_grid_spacings: list, horizontal_grid_spacings: list):
    global LAST_EXEC_RESULT
    """
    批量创建轴网
    param vertical_grid_spacings: 垂直轴网（数字1、2、3...）之间的间距列表（单位：毫米）
    param horizontal_grid_spacings: 水平轴网（字母A、B、C...）之间的间距列表（单位：毫米）
    """
    start_offset_mm = 5000  # 第一个轴网距起点的距离（mm）
    grid_length_mm = 50000   # 轴网总长度（mm）

    # 辅助函数：单位转换
    def mm_to_ft(mm):
        return UnitUtils.ConvertToInternalUnits(mm, UnitTypeId.Millimeters)

    # 辅助函数：生成轴网名称
    def get_grid_names(count, is_vertical=True):
        if is_vertical:
            return [str(i+1) for i in range(count)]
        else:
            valid_letters = []
            ascii_code = 65  # 'A'
            while len(valid_letters) < count:
                char = chr(ascii_code)
                if char not in ['I', 'O']:
                    valid_letters.append(char)
                ascii_code += 1
            return valid_letters

    # 转换单位
    start_offset = mm_to_ft(start_offset_mm)
    grid_length = mm_to_ft(grid_length_mm)

    # 计算轴网总数：1个初始偏移轴网 + 间距列表长度
    total_vertical_grids = 1 + len(vertical_grid_spacings)
    total_horizontal_grids = 1 + len(horizontal_grid_spacings)

    # 预生成轴网名称
    vertical_grid_names = get_grid_names(total_vertical_grids, is_vertical=True)
    horizontal_grid_names = get_grid_names(total_horizontal_grids, is_vertical=False)

    created_grids = []
    # --------------------------
    # 事务包裹
    # --------------------------
    t = Transaction(doc, "创建轴网")
    try:
        t.Start()
        origin = XYZ(0, 0, 0)

        # ==========================================
        # 1. 创建垂直轴网（纵向，数字命名）
        # ==========================================
        vertical_x_positions = [origin.X + start_offset]
        current_x = vertical_x_positions[0]
        for s_mm in vertical_grid_spacings:
            current_x += mm_to_ft(s_mm)
            vertical_x_positions.append(current_x)

        for idx, x in enumerate(vertical_x_positions):
            p1 = XYZ(x, origin.Y, origin.Z)
            p2 = XYZ(x, origin.Y + grid_length, origin.Z)
            line = Line.CreateBound(p1, p2)
            grid = Grid.Create(doc, line)
            grid.Name = vertical_grid_names[idx]
            created_grids.append(grid)

        # ==========================================
        # 2. 创建水平轴网（横向，字母命名）
        # ==========================================
        horizontal_y_positions = [origin.Y + start_offset]
        current_y = horizontal_y_positions[0]
        for s_mm in horizontal_grid_spacings:
            current_y += mm_to_ft(s_mm)
            horizontal_y_positions.append(current_y)

        for idx, y in enumerate(horizontal_y_positions):
            p1 = XYZ(origin.X, y, origin.Z)
            p2 = XYZ(origin.X + grid_length, y, origin.Z)
            line = Line.CreateBound(p1, p2)
            grid = Grid.Create(doc, line)
            grid.Name = horizontal_grid_names[idx]
            created_grids.append(grid)

        t.Commit()
        print(f"🎉 轴网创建完成：共{len(created_grids)}个")

    except Exception as e:
        if t.HasStarted():
            t.RollBack()
        print(f"❌ 失败：{str(e)}")

    LAST_EXEC_RESULT = created_grids
    return created_grids

def create_single_grid(grid_name: str, start_x: float, start_y: float, end_x: float, end_y: float):
    global LAST_EXEC_RESULT
    """
    创建单个轴网
    param grid_name: 轴网名称
    param start_x, start_y: 起点坐标（毫米）
    param end_x, end_y: 终点坐标（毫米）
    """
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)

        start_point = XYZ(start_x / FEET_TO_MM, start_y / FEET_TO_MM, 0)
        end_point = XYZ(end_x / FEET_TO_MM, end_y / FEET_TO_MM, 0)
        grid_line = Line.CreateBound(start_point, end_point)

        grid = Grid.Create(doc, grid_line)
        grid.Name = grid_name

        TransactionManager.Instance.TransactionTaskDone()
        res = [f"✅ 轴网创建成功：{grid_name}"]
        LAST_EXEC_RESULT = res
        return res
    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        res = [f"❌ 轴网创建失败：{str(e)}"]
        LAST_EXEC_RESULT = res
        return res

def get_all_grids():
    global LAST_EXEC_RESULT
    """
    获取项目中所有轴网
    """
    grids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Grids).\
            WhereElementIsNotElementType().ToElements()
    if grids:
        grid_id_list = List[ElementId]()
        for grid in grids:
            grid_id_list.Add(grid.Id)
        uidoc.Selection.SetElementIds(grid_id_list)
    LAST_EXEC_RESULT = grids
    return grids

def delete_grid_by_name(grid_name: str):
    global LAST_EXEC_RESULT
    """
    按名称删除轴网
    param grid_name: 轴网名称
    """
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)
        grids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()

        target_grid = next((g for g in grids if g.Name.strip() == grid_name.strip()), None)
        if not target_grid:
            raise Exception(f"未找到轴网：{grid_name}")

        doc.Delete(target_grid.Id)

        TransactionManager.Instance.TransactionTaskDone()
        res = [f"✅ 轴网删除成功：{grid_name}"]
        LAST_EXEC_RESULT = res
        return res
    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        res = [f"❌ 轴网删除失败：{str(e)}"]
        LAST_EXEC_RESULT = res
        return res

def modify_grid_name(old_name: str, new_name: str):
    global LAST_EXEC_RESULT
    """
    修改轴网名称
    param old_name: 原轴网名称
    param new_name: 新轴网名称
    """
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)
        grids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()

        target_grid = next((g for g in grids if g.Name.strip() == old_name.strip()), None)
        if not target_grid:
            raise Exception(f"未找到轴网：{old_name}")

        target_grid.Name = new_name

        TransactionManager.Instance.TransactionTaskDone()
        res = [f"✅ 轴网重命名成功：{old_name} → {new_name}"]
        LAST_EXEC_RESULT = res
        return res
    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        res = [f"❌ 轴网重命名失败：{str(e)}"]
        LAST_EXEC_RESULT = res
        return res

# ==================================================
# 第九部分：视图管理工具
# ==================================================
def create_plan_view(level_name: str, view_name: str = None):
    global LAST_EXEC_RESULT
    """
    创建平面视图
    param level_name: 标高名称
    param view_name: 视图名称（可选）
    """
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)
        levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
        target_level = next((lvl for lvl in levels if lvl.Name.strip() == level_name.strip()), None)

        if not target_level:
            raise Exception(f"未找到标高：{level_name}")

        view_family_type = next((vft for vft in FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
                                if vft.ViewFamily == ViewFamily.FloorPlan), None)

        if not view_family_type:
            raise Exception("未找到平面视图类型")

        view = ViewPlan.Create(doc, view_family_type.Id, target_level.Id)
        if view_name:
            view.Name = view_name
        else:
            view.Name = f"{level_name} 平面"

        TransactionManager.Instance.TransactionTaskDone()
        res = [f"✅ 平面视图创建成功：{view.Name}"]
        LAST_EXEC_RESULT = res
        return res
    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        res = [f"❌ 平面视图创建失败：{str(e)}"]
        LAST_EXEC_RESULT = res
        return res

def create_elevation_view(level_name: str, direction: str, view_name: str = None):
    global LAST_EXEC_RESULT
    """
    创建立面视图
    :param level_name: 标高名称
    :param direction: 立面方向（"东"、"西"、"南"、"北"）
    :param view_name: 视图名称（可选）
    """
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)

        # 获取标高
        levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
        target_level = next((lvl for lvl in levels if lvl.Name.strip() == level_name.strip()), None)
        if not target_level:
            raise Exception(f"未找到标高：{level_name}")

        # 获取立面视图类型
        view_family_type = next((vft for vft in FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
                                if vft.ViewFamily == ViewFamily.Elevation), None)
        if not view_family_type:
            raise Exception("未找到立面视图类型")

        # 获取立面标记
        elevation_markers = FilteredElementCollector(doc).OfClass(ElevationMarker).ToElements()
        if not elevation_markers:
            # 创建新的立面标记
            elevation_marker = ElevationMarker.CreateElevationMarker(doc, view_family_type.Id, XYZ(0, 0, 0), 0)
        else:
            elevation_marker = elevation_markers[0]

        # 确定立面索引
        direction_map = {"东": 0, "南": 1, "西": 2, "北": 3}
        if direction not in direction_map:
            raise Exception(f"不支持的方向：{direction}，支持的方向：{list(direction_map.keys())}")

        # 创建立面视图
        view = elevation_marker.CreateElevation(doc, target_level.Id, direction_map[direction])
        if view_name:
            view.Name = view_name
        else:
            view.Name = f"{level_name} {direction}立面"

        TransactionManager.Instance.TransactionTaskDone()
        res = [f"✅ 立面视图创建成功：{view.Name}"]
        LAST_EXEC_RESULT = res
        return res
    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        res = [f"❌ 立面视图创建失败：{str(e)}"]
        LAST_EXEC_RESULT = res
        return res

def create_section_view(start_x: float, start_y: float, end_x: float, end_y: float, view_name: str = None):
    global LAST_EXEC_RESULT
    """
    创建剖面视图
    :param start_x, start_y: 剖面线起点坐标（毫米）
    :param end_x, end_y: 剖面线终点坐标（毫米）
    :param view_name: 视图名称（可选）
    """
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)

        # 获取剖面视图类型
        view_family_type = next((vft for vft in FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
                                if vft.ViewFamily == ViewFamily.Section), None)
        if not view_family_type:
            raise Exception("未找到剖面视图类型")

        # 创建剖面线
        start_point = XYZ(start_x / FEET_TO_MM, start_y / FEET_TO_MM, 0)
        end_point = XYZ(end_x / FEET_TO_MM, end_y / FEET_TO_MM, 0)
        section_line = Line.CreateBound(start_point, end_point)

        # 创建剖面视图
        view = ViewSection.CreateSection(doc, view_family_type.Id, section_line)
        if view_name:
            view.Name = view_name
        else:
            view.Name = "剖面"

        TransactionManager.Instance.TransactionTaskDone()
        res = [f"✅ 剖面视图创建成功：{view.Name}"]
        LAST_EXEC_RESULT = res
        return res
    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        res = [f"❌ 剖面视图创建失败：{str(e)}"]
        LAST_EXEC_RESULT = res
        return res

def create_3d_view(view_name: str = None):
    global LAST_EXEC_RESULT
    """
    创建三维视图
    :param view_name: 视图名称（可选）
    """
    try:
        TransactionManager.Instance.EnsureInTransaction(doc)

        # 获取三维视图类型
        view_family_type = next((vft for vft in FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
                                if vft.ViewFamily == ViewFamily.ThreeDimensional), None)
        if not view_family_type:
            raise Exception("未找到三维视图类型")

        # 创建三维视图
        view = View3D.CreateIsometric(doc, view_family_type.Id)
        if view_name:
            view.Name = view_name
        else:
            view.Name = "三维视图"

        TransactionManager.Instance.TransactionTaskDone()
        res = [f"✅ 三维视图创建成功：{view.Name}"]
        LAST_EXEC_RESULT = res
        return res
    except Exception as e:
        TransactionManager.Instance.TransactionTaskDone()
        res = [f"❌ 三维视图创建失败：{str(e)}"]
        LAST_EXEC_RESULT = res
        return res

# ==================================================
# 第十部分：模型检查工具
# ==================================================
def check_unplaced_rooms():
    global LAST_EXEC_RESULT
    """
    检查项目中未放置的房间
    """
    try:
        all_rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).ToElements()
        placed_count = 0
        unplaced_count = 0

        for room in all_rooms:
            if room.Location and room.Location.Point and room.Area > 0:
                placed_count += 1
            else:
                unplaced_count += 1

        res = {
            "总房间数": len(all_rooms),
            "已放置房间": placed_count,
            "未放置房间": unplaced_count,
            "状态": "正常" if unplaced_count == 0 else "存在未放置房间"
        }
        LAST_EXEC_RESULT = res
        return res
    except Exception as e:
        res = {"错误": str(e)}
        LAST_EXEC_RESULT = res
        return res

def check_model_health_status():
    global LAST_EXEC_RESULT
    """
    检查模型健康状态
    """
    try:
        levels = list(FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements())
        walls = list(FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements())
        floors = list(FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements())
        doors = list(FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements())
        windows = list(FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements())
        rooms = list(FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).ToElements())
        grids = list(FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements())

        unplaced = sum(1 for r in rooms if not r.Location or not r.Location.Point or r.Area <= 0)

        res = {
            "模型构件统计": {
                "标高": len(levels),
                "轴网": len(grids),
                "墙体": len(walls),
                "楼板": len(floors),
                "门": len(doors),
                "窗": len(windows),
                "房间": len(rooms)
            },
            "模型健康检查": {
                "未放置房间": unplaced,
                "状态": "✅ 健康" if unplaced == 0 else f"⚠️ 存在{unplaced}个未放置房间"
            }
        }
        LAST_EXEC_RESULT = res
        return res
    except Exception as e:
        res = {"错误": str(e)}
        LAST_EXEC_RESULT = res
        return res

def check_duplicate_elements():
    global LAST_EXEC_RESULT
    """
    检查重复元素
    """
    try:
        duplicates = []
        collector = FilteredElementCollector(doc).WhereElementIsNotElementType()

        # 按类别分组检查
        categories = {}
        for elem in collector:
            cat_name = elem.Category.Name if elem.Category else "无类别"
            if cat_name not in categories:
                categories[cat_name] = []
            categories[cat_name].append(elem)

        # 检查每个类别中的重复元素
        for cat_name, elems in categories.items():
            seen = set()
            for elem in elems:
                # 用位置和类型作为重复判断依据
                key = (elem.GetTypeId().ToString(), elem.Location.Point.ToString() if elem.Location else "")
                if key in seen:
                    duplicates.append({"id": elem.Id.IntegerValue, "category": cat_name, "name": elem.Name})
                else:
                    seen.add(key)

        res = {
            "重复元素数量": len(duplicates),
            "重复元素详情": duplicates,
            "状态": "✅ 无重复元素" if len(duplicates) == 0 else f"⚠️ 发现{len(duplicates)}个重复元素"
        }
        LAST_EXEC_RESULT = res
        return res
    except Exception as e:
        res = {"错误": str(e)}
        LAST_EXEC_RESULT = res
        return res

def check_missing_parameters(param_name: str, category_name: str):
    global LAST_EXEC_RESULT
    """
    检查指定类别元素是否缺少指定参数
    :param param_name: 参数名称
    :param category_name: 类别名称
    """
    try:
        if category_name not in CATEGORY_MAP:
            raise Exception(f"不支持的类别：{category_name}，支持的类别：{list(CATEGORY_MAP.keys())}")

        elements = FilteredElementCollector(doc).OfCategory(CATEGORY_MAP[category_name]).\
                WhereElementIsNotElementType().ToElements()

        missing = []
        for elem in elements:
            param = elem.LookupParameter(param_name)
            if not param:
                missing.append({"id": elem.Id.IntegerValue, "name": elem.Name})

        res = {
            "检查类别": category_name,
            "检查参数": param_name,
            "总元素数": len(elements),
            "缺少参数的元素数": len(missing),
            "缺少参数的元素详情": missing,
            "状态": "✅ 所有元素都有该参数" if len(missing) == 0 else f"⚠️ 发现{len(missing)}个元素缺少该参数"
        }
        LAST_EXEC_RESULT = res
        return res
    except Exception as e:
        res = {"错误": str(e)}
        LAST_EXEC_RESULT = res
        return res
