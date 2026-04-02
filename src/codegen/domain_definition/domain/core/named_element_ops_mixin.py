from typing import Any, Self

class NamedElementOpsMixin:
    """底层逻辑复用：管理具备 name 属性的子元素集合"""
    
    def _add_item(self, field_name: str, item: Any, type_name: str) -> Self:
        collection: list = getattr(self, field_name)
        if any(existing.name == item.name for existing in collection):
            raise ValueError(f"{type_name} '{item.name}' already exists in '{getattr(self, 'name', 'Unknown')}'")
        collection.append(item)
        return self

    def _update_item(self, field_name: str, item: Any, type_name: str) -> Self:
        collection: list = getattr(self, field_name)
        for i, existing in enumerate(collection):
            if existing.name == item.name:
                collection[i] = item
                return self
        raise ValueError(f"{type_name} '{item.name}' not found in '{getattr(self, 'name', 'Unknown')}'")

    def _remove_item(self, field_name: str, name: str) -> Self:
        collection: list = getattr(self, field_name)
        # 过滤掉匹配 name 的元素
        setattr(self, field_name, [i for i in collection if i.name != name])
        return self

    def _get_item(self, field_name: str, name: str, type_name: str) -> Any:
        collection: list = getattr(self, field_name)
        for item in collection:
            if item.name == name:
                return item
        raise ValueError(f"{type_name} '{name}' not found in '{getattr(self, 'name', 'Unknown')}'")