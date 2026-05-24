from typing import Annotated

from pydantic import Field
from pydantic.type_adapter import TypeAdapter

from .ast_ann_assign import AstAnnAssign
from .ast_assign import AstAssign
from .ast_attribute import AstAttribute
from .ast_aug_assign import AstAugAssign
from .ast_bin_op import AstBinOp
from .ast_bool_op import AstBoolOp
from .ast_call import AstCall
from .ast_compare import AstCompare
from .ast_comprehension import AstComprehension
from .ast_constant import AstConstant
from .ast_break import AstBreak
from .ast_continue import AstContinue
from .ast_dict import AstDict
from .ast_dict_comp import AstDictComp
from .ast_expr_stmt import AstExprStmt
from .ast_for import AstFor
from .ast_formatted_value import AstFormattedValue
from .ast_generator_exp import AstGeneratorExp
from .ast_if import AstIf
from .ast_if_exp import AstIfExp
from .ast_joined_str import AstJoinedStr
from .ast_lambda import AstLambda
from .ast_list import AstList
from .ast_list_comp import AstListComp
from .ast_match import AstMatch
from .ast_match_case import AstMatchCase
from .ast_name import AstName
from .ast_pass import AstPass
from .ast_raise import AstRaise
from .ast_return import AstReturn
from .ast_set import AstSet
from .ast_set_comp import AstSetComp
from .ast_slice import AstSlice
from .ast_starred import AstStarred
from .ast_subscript import AstSubscript
from .ast_tuple import AstTuple
from .ast_unary_op import AstUnaryOp
from .ast_with import AstWith
from .ast_with_item import AstWithItem
from .call_expr import CallExpr
from .constant_expr import ConstantExpr
from .dict_expr import DictExpr
from .dict_item import DictItem
from .expr_def import ExprDef
from .lambda_expr import LambdaExpr
from .parsed_path import ParsedPath
from .reference_expr import ReferenceExpr
from .sequence_expr import SequenceExpr

from .ast_stmt import AstStmt
from .ast_expr import AstExpr
from .match_pattern import MatchPattern, match_pattern_adapter


__all__ = [
    "AstAnnAssign",
    "AstAssign",
    "AstAttribute",
    "AstAugAssign",
    "AstBinOp",
    "AstBoolOp",
    "AstCall",
    "AstCompare",
    "AstComprehension",
    "AstConstant",
    "AstBreak",
    "AstContinue",
    "AstDict",
    "AstDictComp",
    "AstExpr",
    "AstExprStmt",
    "AstFor",
    "AstFormattedValue",
    "AstGeneratorExp",
    "AstIf",
    "AstIfExp",
    "AstJoinedStr",
    "AstLambda",
    "AstList",
    "AstListComp",
    "AstMatch",
    "AstMatchCase",
    "MatchPattern",
    "match_pattern_adapter",
    "AstName",
    "AstPass",
    "AstRaise",
    "AstReturn",
    "AstSet",
    "AstSetComp",
    "AstSlice",
    "AstStarred",
    "AstStmt",
    "AstSubscript",
    "AstTuple",
    "AstUnaryOp",
    "AstWith",
    "AstWithItem",
    "CallExpr",
    "ConstantExpr",
    "DictExpr",
    "DictItem",
    "ExprDef",
    "LambdaExpr",
    "ParsedPath",
    "ReferenceExpr",
    "SequenceExpr",
]

# model_rebuild() for ExprDef members
CallExpr.model_rebuild()
DictItem.model_rebuild()
DictExpr.model_rebuild()
LambdaExpr.model_rebuild()
SequenceExpr.model_rebuild()
ReferenceExpr.model_rebuild()

AstAnnAssign.model_rebuild()
AstAssign.model_rebuild()
AstAugAssign.model_rebuild()
AstExprStmt.model_rebuild()
AstFor.model_rebuild()
AstIf.model_rebuild()
AstWith.model_rebuild()
AstMatch.model_rebuild()
AstAttribute.model_rebuild()
AstCall.model_rebuild()
AstBinOp.model_rebuild()
AstBoolOp.model_rebuild()
AstCompare.model_rebuild()
AstIfExp.model_rebuild()
AstLambda.model_rebuild()
AstJoinedStr.model_rebuild()
AstFormattedValue.model_rebuild()
AstListComp.model_rebuild()
AstSetComp.model_rebuild()
AstDictComp.model_rebuild()
AstGeneratorExp.model_rebuild()
AstSlice.model_rebuild()
AstStarred.model_rebuild()
AstSubscript.model_rebuild()
AstTuple.model_rebuild()
AstList.model_rebuild()
AstSet.model_rebuild()
AstDict.model_rebuild()
AstWithItem.model_rebuild()
AstMatchCase.model_rebuild()
AstComprehension.model_rebuild()
AstReturn.model_rebuild()
AstUnaryOp.model_rebuild()
AstRaise.model_rebuild()
