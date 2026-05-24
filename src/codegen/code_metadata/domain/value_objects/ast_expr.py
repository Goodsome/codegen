from typing import Annotated

from pydantic import Field
from pydantic.type_adapter import TypeAdapter

from .ast_attribute import AstAttribute
from .ast_bin_op import AstBinOp
from .ast_bool_op import AstBoolOp
from .ast_call import AstCall
from .ast_compare import AstCompare
from .ast_constant import AstConstant
from .ast_dict import AstDict
from .ast_dict_comp import AstDictComp
from .ast_formatted_value import AstFormattedValue
from .ast_generator_exp import AstGeneratorExp
from .ast_if_exp import AstIfExp
from .ast_joined_str import AstJoinedStr
from .ast_lambda import AstLambda
from .ast_list import AstList
from .ast_list_comp import AstListComp
from .ast_name import AstName
from .ast_set import AstSet
from .ast_set_comp import AstSetComp
from .ast_slice import AstSlice
from .ast_starred import AstStarred
from .ast_subscript import AstSubscript
from .ast_tuple import AstTuple
from .ast_unary_op import AstUnaryOp

AstExpr = Annotated[
    AstConstant | AstName | AstAttribute | AstCall
    | AstBinOp | AstBoolOp | AstUnaryOp | AstCompare
    | AstIfExp | AstLambda | AstJoinedStr | AstFormattedValue
    | AstListComp | AstSetComp | AstDictComp | AstGeneratorExp
    | AstSlice | AstStarred | AstSubscript
    | AstTuple | AstList | AstSet | AstDict,
    Field(discriminator="kind")
]

ast_expr_adapter: TypeAdapter[AstExpr] = TypeAdapter(AstExpr)