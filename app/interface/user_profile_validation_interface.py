from abc import ABC, abstractmethod


class CreateUserValidationInterface(ABC):
    @abstractmethod
    def validate_input_data(self):
        """
        Calls self.validate_username_exists,
        self.validate_phone_number_exists, and
        self.validate_is_strong. Returns a dictionary:
        {
            "username": validated_username,
            "phone_number": validated_phone_number,
            "password": hashed_password
        }
        """
        pass

    @abstractmethod
    def validate_username_exists(self, value):
        """
        Checks if the username exists in the database.
        Raises an HTTP exception if it already exists.
        """
        pass

    @abstractmethod
    def validate_phone_number_exists(self, value):
        """
        Validates the phone number format using regex and checks if it exists in the database.
        Raises an HTTP exception if the phone number already exists.
        """
        pass

    @abstractmethod
    def validate_is_strong(value: str) -> str:
        """
        Checks if the password is strong. It must contain at least one uppercase letter,
        one lowercase letter, one special character, and be at least 8 characters long.
        """
        pass
