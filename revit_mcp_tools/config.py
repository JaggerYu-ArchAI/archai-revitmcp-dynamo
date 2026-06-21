# -*- coding:utf-8 -*-
# 固定配置文件（优化版：精简、规范、AI友好）

# ==================================================
# 第一部分：通用建筑项目基准参数
# ==================================================
# 单位转换常量
FEET_TO_MM = 304.8
METERS_TO_FEET = 3.28084

# 大模型接口配置
BASE_URL = "https://api.deepseek.com"
# MODEL = "deepseek-v4-flash"
MODEL = "deepseek-v4-pro"

# BASE_URL = "http://172.16.5.20:7979/v1"
# MODEL = "Qwen3.5-122B-A10B"

# ==================================================
# 第二部分：MCP工具白名单
# ==================================================
MCP_TOOL_WHITELIST = [
    # ==================================================
    # 模块1：选择查询工具（收集器）
    # ==================================================
    {
        "tool_name": "按类别查询元素",
        "function_name": "get_elements_by_category",
        "description": "按类别获取元素，支持：标高、墙体、房间、门、窗、楼板、屋面、结构柱、结构梁、轴网，结果自动缓存，用于后续批量操作",
        "required_params": {
            "category_name": "str，类别名称"
        },
        "optional_params": {
            "active_view_only": "bool，是否仅当前视图，默认False"
        }
    },
    {
        "tool_name": "按族查询元素",
        "function_name": "get_elements_by_family",
        "description": "按族名称+族类型名称获取元素，结果自动缓存，用于后续批量操作",
        "required_params": {
            "family_name": "str，族名称",
            "type_name": "str，族类型名"
        },
        "optional_params": {}
    },
    {
        "tool_name": "按参数查询元素",
        "function_name": "get_elements_by_parameter",
        "description": "按类别+参数值筛选元素，支持精确/开头/包含匹配，结果自动缓存，用于后续批量操作",
        "required_params": {
            "category_name": "str，类别名称",
            "parameter_name": "str，参数名称",
            "parameter_value": "any，参数值"
        },
        "optional_params": {
            "match_mode": "str，匹配模式：exact/start_with/contains，默认exact",
            "active_view_only": "bool，是否仅当前视图，默认False"
        }
    },
    {
        "tool_name": "获取选中元素",
        "function_name": "get_selected_elements",
        "description": "获取当前选中的元素，结果自动缓存，用于后续批量操作",
        "required_params": {},
        "optional_params": {
            "limit": "int，返回最大元素数量，默认100"
        }
    },

    # ==================================================
    # 模块2：建筑方案设计工具
    # ==================================================
    {
        "tool_name": "建筑方案设计（矩形）",
        "function_name": "architecture_design_rectangle",
        "description": "自动生成矩形建筑：标高+外墙+楼板，单位：米",
        "required_params": {
            "length": "float，建筑长度",
            "width": "float，建筑宽度",
            "floor_h": "float，单层高度",
            "floors": "int，建筑层数"
        },
        "optional_params": {}
    },
    {
        "tool_name": "建筑方案设计（圆形）",
        "function_name": "architecture_design_circle",
        "description": "自动生成圆形建筑：标高+外墙+楼板，单位：米",
        "required_params": {
            "diameter": "float，建筑直径",
            "floor_h": "float，单层高度",
            "floors": "int，建筑层数"
        },
        "optional_params": {}
    },

    # ==================================================
    # 模块3：常用构件创建工具
    # ==================================================
    {
        "tool_name": "创建直线墙体",
        "function_name": "create_wall",
        "description": "创建直线墙，坐标/高度单位：毫米",
        "required_params": {
            "start_x": "float，起点X",
            "start_y": "float，起点Y",
            "end_x": "float，终点X",
            "end_y": "float，终点Y",
            "wall_height": "float，墙体高度",
            "level_name": "str，标高名称"
        },
        "optional_params": {}
    },
    {
        "tool_name": "批量创建标高",
        "function_name": "create_levels",
        "description": "批量创建标高，高程单位：毫米",
        "required_params": {
            "level_names": "list，标高名称列表",
            "elevations": "list，标高高程列表"
        },
        "optional_params": {}
    },
    {
        "tool_name": "创建门",
        "function_name": "create_door",
        "description": "墙体上创建门，单位：毫米；支持智能缓存",
        "required_params": {},
        "optional_params": {
            "wall_id": "int，墙体ID",
            "x": "float，插入点X",
            "y": "float，插入点Y"
        }
    },
    {
        "tool_name": "创建窗",
        "function_name": "create_window",
        "description": "墙体上创建窗，单位：毫米；支持智能缓存",
        "required_params": {},
        "optional_params": {
            "wall_id": "int，墙体ID",
            "x": "float，插入点X",
            "y": "float，插入点Y"
        }
    },
    {
        "tool_name": "创建房间",
        "function_name": "create_room",
        "description": "在指定坐标位置创建房间，需在封闭区域内",
        "required_params": {
            "name": "str，房间名称",
            "x": "float，X坐标（毫米）",
            "y": "float，Y坐标（毫米）"
        },
        "optional_params": {
            "z": "float，Z坐标（毫米）",
            "number": "str，房间编号",
            "department": "str，部门",
            "comments": "str，注释"
        }
    },
    {
        "tool_name": "创建项目参数",
        "function_name": "create_project_parameter",
        "description": "为指定类别构件创建项目参数，项目参数默认作为共享参数存储",
        "required_params": {
            "category_name": "str，类别名称",
            "param_name": "str，参数名称"
        },
        "optional_params": {
            "shared_group": "str，共享参数组",
            "is_instance": "bool，是否为实例参数",
            "spec_type": "参数类型默认为文字",
            "group_type": "分组默认为标识数据"
        }
    },

    # ==================================================
    # 模块4：常用构件修改工具
    # ==================================================
    {
        "tool_name": "操作元素",
        "function_name": "operate_elements",
        "description": "可执行选中/删除/隐藏/隔离/取消隐藏/重置隔离/着色/设置透明度；元素优先级：传入元素ID > 手动选中构件 > 上一轮执行缓存构件",
        "required_params": {
            "action": "str，操作类型：Select/Delete/Hide/Isolate/Unhide/ResetIsolate/SetColor/SetTransparency"
        },
        "optional_params": {
            "element_ids": "list[int]，元素ID",
            "transparency_value": "int，透明度0-100",
            "color": "str，颜色名称",
            "rgb": "list[int]，RGB颜色"
        }
    },
    {
        "tool_name": "批量修改元素参数文本",
        "function_name": "batch_modify_element_param_text",
        "description": "批量修改参数文本：插入/删除/替换，支持房间/门/窗",
        "required_params": {
            "category_name": "str，类别：房间/门/窗",
            "operation": "str，操作：insert/remove/replace",
            "target_param_name": "str，目标参数名称"
        },
        "optional_params": {
            "old_text": "str，replace必填：旧文本",
            "new_text": "str，insert/replace必填：新文本",
            "position": "int，insert/remove必填：位置索引",
            "count": "int，remove必填：删除字符数",
            "active_view_only": "bool，默认False",
            "replace_mode": "str，替换模式：all/first/last，默认all"
        }
    },
    {
        "tool_name": "按族批量修改参数文本",
        "function_name": "batch_modify_element_param_text_by_family",
        "description": "按族+类型批量修改参数文本：插入/删除/替换",
        "required_params": {
            "family_name": "str，族名称",
            "type_name": "str，族类型名称",
            "operation": "str，操作：insert/remove/replace",
            "target_param_name": "str，目标参数名称"
        },
        "optional_params": {
            "old_text": "str，replace必填：旧文本",
            "new_text": "str，insert/replace必填：新文本",
            "position": "int，insert/remove必填：位置索引",
            "count": "int，remove必填：删除字符数",
            "replace_mode": "str，替换模式：all/first/last，默认all"
        }
    },
    {
        "tool_name": "移动元素",
        "function_name": "move_element",
        "description": "平移元素，距离单位：毫米；支持智能缓存",
        "required_params": {},
        "optional_params": {
            "element_id": "int，元素ID",
            "dx": "float，X轴偏移",
            "dy": "float，Y轴偏移",
            "dz": "float，Z轴偏移"
        }
    },
    {
        "tool_name": "旋转元素",
        "function_name": "rotate_element",
        "description": "旋转元素，角度单位：度；支持智能缓存",
        "required_params": {},
        "optional_params": {
            "element_id": "int，元素ID",
            "x": "float，旋转中心X",
            "y": "float，旋转中心Y",
            "angle": "float，旋转角度"
        }
    },
    {
        "tool_name": "删除元素",
        "function_name": "delete_element",
        "description": "删除元素；支持智能缓存",
        "required_params": {},
        "optional_params": {
            "element_id": "int，元素ID"
        }
    },
    {
        "tool_name": "设置元素参数",
        "function_name": "set_element_parameter",
        "description": "修改元素参数，支持自动使用上一次查询结果",
        "required_params": {
            "param_name": "str，参数名称",
            "param_value": "str，参数值"
        },
        "optional_params": {
            "element_id": "int，元素ID（可选）"
        }
    },

    # ==================================================
    # 模块5：消防疏散路径工具
    # ==================================================
    {
        "tool_name": "消防疏散路径-门到出口",
        "function_name": "evacuation_paths_door2exit",
        "description": "生成房间疏散门到安全出口的最短路径",
        "required_params": {},
        "optional_params": {}
    },
    {
        "tool_name": "消防疏散路径-房间到出口",
        "function_name": "evacuation_paths_room2exit",
        "description": "生成房间最远点到安全出口的疏散路径",
        "required_params": {},
        "optional_params": {}
    },

    # ==================================================
    # 模块6：房间管理优化工具
    # ==================================================
    {
        "tool_name": "房间居中",
        "function_name": "center_rooms",
        "description": "将当前视图房间定位到几何中心",
        "required_params": {},
        "optional_params": {}
    },
    {
        "tool_name": "房间标记对齐",
        "function_name": "room_tags_move_to_room_location",
        "description": "房间标记与房间位置对齐",
        "required_params": {},
        "optional_params": {}
    },
    
    # ==================================================
    # 模块7：可视化与标记工具
    # ==================================================
    {
        "tool_name": "标记房间",
        "function_name": "tag_rooms",
        "description": "批量标记当前视图所有房间",
        "required_params": {},
        "optional_params": {}
    },
    {
        "tool_name": "标记门",
        "function_name": "tag_doors",
        "description": "批量标记当前视图所有门",
        "required_params": {},
        "optional_params": {}
    },
    {
        "tool_name": "标记窗",
        "function_name": "tag_windows",
        "description": "批量标记当前视图所有窗",
        "required_params": {},
        "optional_params": {}
    },
    {
        "tool_name": "标记所有墙体",
        "function_name": "tag_all_walls",
        "description": "为当前视图中的所有墙体添加标记",
        "required_params": {},
        "optional_params": {}
    },

    # ==================================================
    # 模块8：轴网管理工具
    # ==================================================
    {
        "tool_name": "批量创建轴网",
        "function_name": "create_grids",
        "description": "创建轴网，间距单位：毫米；自动跳过I/O字母",
        "required_params": {
            "vertical_grid_spacings": "list，垂直轴网间距",
            "horizontal_grid_spacings": "list，水平轴网间距"
        },
        "optional_params": {}
    },
    {
        "tool_name": "创建单个轴网",
        "function_name": "create_single_grid",
        "description": "两点创建轴网，单位：毫米",
        "required_params": {
            "grid_name": "str，轴网名称",
            "start_x": "float，起点X",
            "start_y": "float，起点Y",
            "end_x": "float，终点X",
            "end_y": "float，终点Y"
        },
        "optional_params": {}
    },
    {
        "tool_name": "获取所有轴网",
        "function_name": "get_all_grids",
        "description": "获取项目中所有轴网并选中",
        "required_params": {},
        "optional_params": {}
    },
    {
        "tool_name": "删除轴网",
        "function_name": "delete_grid_by_name",
        "description": "按名称删除轴网",
        "required_params": {
            "grid_name": "str，轴网名称"
        },
        "optional_params": {}
    },
    {
        "tool_name": "修改轴网名称",
        "function_name": "modify_grid_name",
        "description": "重命名轴网",
        "required_params": {
            "old_name": "str，原名称",
            "new_name": "str，新名称"
        },
        "optional_params": {}
    },

    # ==================================================
    # 模块9：视图管理工具
    # ==================================================
    {
        "tool_name": "创建平面视图",
        "function_name": "create_plan_view",
        "description": "基于标高创建楼层平面",
        "required_params": {
            "level_name": "str，标高名称"
        },
        "optional_params": {
            "view_name": "str，自定义视图名称"
        }
    },
    {
        "tool_name": "创建立面视图",
        "function_name": "create_elevation_view",
        "description": "创建立面视图，方向：东/西/南/北",
        "required_params": {
            "level_name": "str，标高名称",
            "direction": "str，立面方向"
        },
        "optional_params": {
            "view_name": "str，自定义视图名称"
        }
    },
    {
        "tool_name": "创建剖面视图",
        "function_name": "create_section_view",
        "description": "两点创建剖面，单位：毫米",
        "required_params": {
            "start_x": "float，剖面起点X",
            "start_y": "float，剖面起点Y",
            "end_x": "float，剖面终点X",
            "end_y": "float，剖面终点Y"
        },
        "optional_params": {
            "view_name": "str，自定义视图名称"
        }
    },
    {
        "tool_name": "创建三维视图",
        "function_name": "create_3d_view",
        "description": "创建正交三维视图",
        "required_params": {},
        "optional_params": {
            "view_name": "str，自定义视图名称"
        }
    },

    # ==================================================
    # 模块10：模型检查工具
    # ==================================================
    {
        "tool_name": "检查未放置房间",
        "function_name": "check_unplaced_rooms",
        "description": "统计项目中未放置的房间",
        "required_params": {},
        "optional_params": {}
    },
    {
        "tool_name": "检查模型健康状态",
        "function_name": "check_model_health_status",
        "description": "全模型构件统计+健康检查",
        "required_params": {},
        "optional_params": {}
    },
    {
        "tool_name": "检查重复元素",
        "function_name": "check_duplicate_elements",
        "description": "检测重复构件（位置+类型）",
        "required_params": {},
        "optional_params": {}
    },
    {
        "tool_name": "检查缺少参数",
        "function_name": "check_missing_parameters",
        "description": "检查指定类别是否缺少参数",
        "required_params": {
            "param_name": "str，参数名称",
            "category_name": "str，类别名称"
        },
        "optional_params": {}
    }
]

# ==================================================
# 第三部分：AI约束提示词（优化版）
# ==================================================
def get_mcp_tool_prompt():
    strict_json_prompt = """
【最高优先级：仅输出纯JSON，禁止任何其他内容】
1. 禁止自然语言、解释、前缀、后缀、标点
2. 禁止生成Python代码/Revit API代码
3. 仅允许两种JSON格式输出

【格式1：调用工具】
{
    "type": "tool",
    "tool_name": "工具名称",
    "parameters": {"参数名": "参数值"}
}

【格式2：任务完成】
{
    "type": "finish",
    "message": "任务完成描述"
}
"""

    tool_prompt = "\n【可调用工具列表】\n"
    for tool in MCP_TOOL_WHITELIST:
        tool_prompt += f"""
【{tool['tool_name']}】
功能：{tool['description']}
必填：{tool['required_params']}
可选：{tool['optional_params']}
"""

    rules = """
【执行规则】
1. 每次只调用一个工具，分步完成任务
2. 需要批量操作某类构件时，先查询再操作
3. 参数缺失主动询问，不随意猜测传参
4. 优先使用上一步缓存结果，无需重复查询
5. 任务完成输出finish格式
6. 若用户问题超出所有MCP工具的支持范围：输出finish格式，明确告知用户无法处理该问题，并推荐功能最相近的MCP工具
7. 若用户询问「MCP白名单工具数量/有多少个MCP白名单」：直接输出finish格式，在message中回复准确的工具数量，无需调用任何工具
"""

    return (strict_json_prompt + tool_prompt + rules).strip()
