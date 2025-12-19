import re

class NamingService:
    """
    Provide naming conversions used during code generation.
    """
    
    def to_snake(self, text: str) -> str:
        """
        Convert to snake_case
        """
        return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()
    
    def to_pascal(self, text: str) -> str:
        """
        Convert to PascalCase
        """
        return "".join(word.capitalize() for word in text.split("_"))
    
    def to_kebab(self, text: str) -> str:
        """
        Convert to kebab-case
        """
        return self.to_snake(text).replace("_", "-")
    