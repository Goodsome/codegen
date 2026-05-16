import ast
import difflib

def calculate_ast_similarity(original_code: str, generated_code: str) -> float:
    """
    计算两段 Python 代码的 AST 结构相似度 (0.0 ~ 1.0)
    """
    try:
        # 1. 将代码解析为抽象语法树 (AST)
        tree_orig = ast.parse(original_code)
        tree_gen = ast.parse(generated_code)
        
        # 2. 将 AST 转换为格式化的字符串
        # include_attributes=False 是核心：它会忽略节点在文件中的行号(lineno)和列号(col_offset)
        # 这样只比较代码的"逻辑结构"和"内容"，完全无视换行和缩进
        dump_orig = ast.dump(tree_orig, annotate_fields=True, include_attributes=False)
        dump_gen = ast.dump(tree_gen, annotate_fields=True, include_attributes=False)
        
        # 3. 使用标准库计算相似度比例
        # 为了让比对更精确，我们可以按节点层级拆分成列表进行对比，而不是作为单个超长字符串
        matcher = difflib.SequenceMatcher(
            None, 
            dump_orig.replace("(", "\n").splitlines(), 
            dump_gen.replace("(", "\n").splitlines()
        )
        
        return matcher.ratio()
        
    except SyntaxError as e:
        # 如果生成的代码有语法错误，连 AST 都无法生成，匹配率直接归零
        print(f"语法解析失败: {e}")
        return 0.0

# === 测试用例 ===
if __name__ == "__main__":
    # 原始代码
    code_a = """
class UserEntity:
    def __init__(self, user_id: int):
        self.user_id = user_id
    """
    
    # 生成代码 (逻辑完全一样，但换行、空格、引号甚至单行写法都不同)
    code_b = """class UserEntity:
    def __init__(self, user_id: int): self.user_id = user_id
"""
    
    # 代码 C (稍微改动了逻辑，比如少写了类型提示)
    code_c = """class UserEntity:
    def __init__(self, user_id):
        self.user_id = user_id
"""

    print(f"A 与 B 的 AST 相似度: {calculate_ast_similarity(code_a, code_b):.2%}") 
    # 预期: 100.00% (完全免疫排版差异)
    
    print(f"A 与 C 的 AST 相似度: {calculate_ast_similarity(code_a, code_c):.2%}") 
    # 预期: < 100% (因为缺失了类型提示节点)