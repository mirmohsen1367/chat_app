from abc import ABC, abstractmethod


class BaseValidationInterface(ABC):
    @abstractmethod
    def validate_province(self, value):
        """
        Checks if the given province ID exists.
        Returns the province object if found, otherwise raises an exception.
        """
        pass

    @abstractmethod
    def validate_city(self, province_id, value):
        """
        Checks if the given city ID exists within the specified province.
        Returns the city object if found, otherwise raises an exception.
        """
        pass
