from pathlib import Path
from typing import Union, List

# ====================== markdown文档读取 ======================
ROOT_PATH = Path(__file__).parents[1]
SPEC_FOLDER = ROOT_PATH / "assets" / "spec_files"

# 工具1：获取所有规范文件列表（给GUI下拉框用）
def get_all_spec_files() -> List[str]:
    """获取spec_files里所有的规范文件名，用于界面下拉选择"""
    SPEC_FOLDER.mkdir(parents=True, exist_ok=True)
    md_files = [f.name for f in SPEC_FOLDER.glob("*.md")]
    return md_files if md_files else ["暂无规范文件，请先添加.md文件到assets/spec_files/"]

# 工具2：读取文件内容 → 直接传给AI（终极优化版）
def load_spec_content(file_names: Union[str, List[str]]) -> str:
    """
    读取单个/多个规范文件，返回AI友好的纯文本，直接传给AI使用
    支持：单个文件名(str) / 文件名列表(list[str])
    """
    # 读取单个文件（内部逻辑）
    def _read_single_file(file_name: str) -> str:
        file_path = SPEC_FOLDER / file_name
        if not file_path.exists():
            return f"【文件读取失败】{file_name}：未找到该规范文件"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f"【文件：{file_name}】\n{f.read()}\n"
        except Exception as e:
            return f"【文件读取失败】{file_name}：{str(e)}"

    # 处理单个文件
    if isinstance(file_names, str):
        return _read_single_file(file_names)
    
    # 处理多个文件：拼接为AI友好的纯文本（核心优化）
    full_text = ""
    for name in file_names:
        full_text += _read_single_file(name) + "\n" + "="*50 + "\n\n"
    return full_text


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
    3.  回答时可以先做一个简单总结，然后再列出相关内容，必须标注清楚内容来自哪本规范、哪个章节、哪个条款号，完全和规范原文一致，不得修改、删减任何内容。
    4.  禁止使用任何模糊、不确定的表述，所有内容必须完全来自提供的规范原文。
    5.  回答必须使用Markdown格式，适用typora软件，使用"#"符号作为标题层级，按照内容的层级结构组织，确保层次清晰。

    【本地规范原文】：
    {load_spec_content(spec_selection)}
    """
    return system_prompt