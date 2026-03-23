from dataclasses import dataclass

@dataclass(frozen=True)
class ParsedAttribute:
    name: str
    type: str
    optional: bool = False
    description: str = ""

class AttributeParser:
    @staticmethod
    def parse(attribute_str: str) -> ParsedAttribute:
        """
        Parses a string in the format 'name:type:optional' into a ParsedAttribute.
        Example: 
            'user_id:UUID' -> ParsedAttribute(name='user_id', type='UUID')
            'email:str:optional' -> ParsedAttribute(name='email', type='str', optional=True)
        """
        parts = attribute_str.split(":")
        name = parts[0].strip()
        if not name:
             raise ValueError(f"Invalid attribute string: '{attribute_str}'. Name cannot be empty.")
             
        type_ = parts[1].strip() if len(parts) > 1 else "str"
        
        optional = False
        if len(parts) > 2:
            extra = parts[2].strip().lower()
            if extra in ("optional", "opt", "true", "1"):
                optional = True
        
        return ParsedAttribute(name=name, type=type_, optional=optional)
