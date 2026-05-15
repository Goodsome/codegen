from abc import ABC, abstractmethod


class Mapper[T_DTO, T_DOMAIN](ABC):
    
    @abstractmethod
    def dto_to_domain(self, dto: T_DTO) -> T_DOMAIN:
        pass