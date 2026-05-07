from pathlib import Path
from typing import List

# ====================== markdown文档读取 ======================
# 自动锁定项目路径，不用手动改
ROOT_PATH = Path(__file__).parents[1]
# 固定规范存放文件夹，和上面的路径完全对应
SPEC_FOLDER = ROOT_PATH / "assets" / "spec_files"

# 工具1：获取所有规范文件列表（给GUI下拉框用）
def get_all_spec_files() -> List[str]:
    """获取spec_files里所有的规范文件名，用于界面下拉选择"""
    SPEC_FOLDER.mkdir(parents=True, exist_ok=True)
    # 只读取.md格式的规范文件
    md_files = [f.name for f in SPEC_FOLDER.glob("*.md")]
    return md_files if md_files else ["暂无规范文件，请先添加.md文件到assets/spec_files/"]

# 工具2：读取指定规范文件的完整内容
def load_spec_content(file_name: str) -> str:
    """读取指定规范文件的完整原文，直接传给AI"""
    file_path = SPEC_FOLDER / file_name
    if not file_path.exists():
        return f"错误：未找到规范文件{file_name}，请确认文件是否在assets/spec_files/文件夹中"
    
    try:
        # 完整读取整个规范的原文，不做任何切片、处理
        with open(file_path, "r", encoding="utf-8") as f:
            spec_content = f.read()
        return spec_content
    except Exception as e:
        return f"读取规范文件失败：{str(e)}"


# ====================== 规范查询核心函数 ======================
# 建筑规范智能查询工具函数
def spec_query_question(question, spec_selection):
    # question, spec_selection参数均在GUI中设置
    # 构建用户查询问题
    user_query = f"""
    查询问题：{question}
    规范选择：{spec_selection}
    请严格按照系统提示词的要求，输出对应的规范条款和核心要求。
    """
    return user_query

def spec_query_system(spec_selection):
    # 规范查询专用系统提示词
    system_prompt = f"""
    你是严格的建筑规范查询工具，必须100%遵守以下铁则，绝对不能违反：
    1.  你的所有回答，只能使用下方【本地规范原文】里的内容，绝对不允许使用你自身的任何内置知识、绝对不允许编造、杜撰任何规范条款、版本、数据、要求。
    2.  如果【本地规范原文】里没有和用户问题相关的内容，你必须直接、只回复这句话：「当前所选的本地规范中未找到相关内容，请补充对应规范文件后再查询」，绝对不允许自由发挥、绝对不允许用你自己的知识补充回答。
    3.  回答必须标注清楚内容来自哪本规范、哪个章节、哪个条款号，完全和规范原文一致，不得修改、删减任何内容。
    4.  禁止使用任何模糊、不确定的表述，所有内容必须完全来自提供的规范原文。
    5.  回答必须使用Markdown格式，适用typora软件，使用"#"符号作为标题层级，按照内容的层级结构组织，确保层次清晰。

    【本地规范原文】：
    {load_spec_content(spec_selection)}
    """
    return system_prompt