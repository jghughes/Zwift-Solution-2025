from typing import Any, Type, TypeVar
import pydantic as pydantic
import json

T = TypeVar('T', bound=pydantic.BaseModel)

class JghSerialization:
    """
    A class for serializing and deserializing objects using Pydantic models.

    Attributes:
        None

    Properties:
        None

    Methods:
        to_json_from_object: Serializes an object to a JSON string.
        to_object_from_json: Deserializes a JSON string to an object of the specified Pydantic model type.

    Functions:
        None
    """

    @staticmethod
    def to_json_from_object(inputObject: Any) -> str:
        """
        Serializes an object to a JSON string.

        Args:
            inputObject (Any): The object to serialize.

        Returns:
            str: The JSON string representation of the object.

        Raises:
            ValueError: If the object cannot be serialized to JSON.
        """
        _failureMsg = "Unable to serialize object to JSON."
        _locusMsg = "[to_json_from_object]"
        _locus2Msg = "[JghSerialization]"
        
        if not inputObject:
            return "{}"
        try:
            # Convert the Pydantic model instance to a dictionary
            validDict = inputObject.model_dump()
            # Convert the dictionary to a JSON string
            validJson = json.dumps(validDict)
        except TypeError as e:
            input_type = type(inputObject).__name__
            raise ValueError((f"Error: {_failureMsg} {_locusMsg} {_locus2Msg}\nComment: The object of type '{input_type}' failed to serialise to JSON due to a TypeError.\nError Message: {e}"))
        except ValueError as e:
            input_type = type(inputObject).__name__
            raise ValueError((f"Error: {_failureMsg} {_locusMsg} {_locus2Msg}\nComment: The object of type '{input_type}' failed to serialise to JSON due to a ValueError.\nError Message: {e}"))
        
        return validJson

    @staticmethod
    def to_object_from_json(inputString: str, outputmodel: Type[T]) -> T:
        """
        Deserializes a JSON string to an object of the specified Pydantic model type.

        Args:
            inputString (str): The JSON string to deserialize.
            outputmodel (Type[T]): The Pydantic model type to deserialize to.

        Returns:
            T: An instance of the specified Pydantic model type.

        Raises:
            ValueError: If the JSON string cannot be deserialized to the specified model type.
                - If a field in the JSON string is of the wrong type, a validation error will be raised.
                - To avoid a validation error if a field in the JSON is missing, provide a default value for the field in the model definition.
                - If a field is superfluous (not defined in the model), it will be ignored during deserialization.
        """
        _failureMsg = "Unable to deserialize JSON to object."
        _locusMsg = "[to_object_from_json]"
        _locus2Msg = "[JghSerialization]"
        
        if not inputString:
            raise ValueError(f"Error: {_failureMsg} {_locusMsg} {_locus2Msg}\nComment: The input JSON string is null or empty.")
        
        try:
            # Use Pydantic's model_validate_json method to deserialize and validate the JSON string
            return outputmodel.model_validate_json(inputString)
        except TypeError as e:
            raise ValueError((f"Error: {_failureMsg} {_locusMsg} {_locus2Msg}\nComment: The input JSON string failed to deserialize to an object of Type '{outputmodel.__name__}' \n\t\tdue to a TypeError.\nError Message: {e}\nInput string:\n\t{inputString}"))
        except json.JSONDecodeError as e:
            raise ValueError((f"Error: {_failureMsg} {_locusMsg} {_locus2Msg}\nComment: The input JSON string failed to deserialize to an object of Type '{outputmodel.__name__}' \n\t\tdue to a JSONDecodeError.\nError Message: {e}\nInput string:\n\t{inputString}"))
        except pydantic.ValidationError as e:
            error_messages = "\n".join([f"\tField: {err['loc']}\n\tError: {err['msg']}" for err in e.errors()])
            raise ValueError((f"Error: {_failureMsg} {_locusMsg} {_locus2Msg}\nComment: The input JSON string failed to deserialize to an object of Type '{outputmodel.__name__}' \n\t\tdue to validation errors.\nValidation errors:\n{error_messages}\nInput string:\n\t{inputString}"))

