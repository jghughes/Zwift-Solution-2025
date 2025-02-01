"""
This module defines the JghSerialization class, which provides methods for 
serializing and deserializing objects.
"""
# Standard library imports
import json
from typing import Any
from dataclasses import dataclass, asdict, is_dataclass

# Local application imports
from pydantic import BaseModel, ValidationError

# Helper function to write a pretty error message
def pretty_error_message(ex: Exception) -> str:
    """
    This function writes a pretty error message to the console.
    The function attempts to unpack the args attribute of the exception ex
    into code and message. If the unpacking fails (e.g., if args does not
    contain two elements), it falls back to setting code to 0 and message
    to the first and only element of args.

    If an exception ex has args like (404, "Not Found"), the function
    will return "Not Found ErrorCode=404". If an exception ex has args
    like ("An error occurred",), the function will return "An error occurred".
    """
    try:
        (code, message) = ex.args
    except:
        code = 0
        message = ex.args[0]
    if code == 0:
        return f"{str(message)}"
    return f"{str(message)} ErrorCode={str(code)}"

# Custom JSON decoder to handle int, float, and bool coercion for dataclasses
class CustomJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, target_types=None, **kwargs): # type: ignore
        super().__init__(*args, **kwargs)
        self.target_types = target_types or {} # type: ignore


    def decode(self, s: str, _w=json.decoder.WHITESPACE.match) -> Any: # type: ignore
        try:
            decoded_data = super().decode(s, _w)
            return self._coerce_types(decoded_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Structure or content of JSON content is fatally flawed. It cannot be decoded.\n\n\t{pretty_error_message(e)}\n\n")

    def _coerce_types(self, decoded_data: Any) -> Any:
        if isinstance(decoded_data, dict):
            return {key: self._coerce_value(key, value) for key, value in decoded_data.items()} # type: ignore
        elif isinstance(decoded_data, list):
            return [self._coerce_value(None, item) for item in decoded_data] # type: ignore
        else:
            return decoded_data

    def _coerce_value(self, key: Any, value: Any) -> Any:
        if isinstance(value, str):
            # Check the type of the target attribute before attempting coercion
            if key in self.target_types: # type: ignore
                target_type = self.target_types[key] # type: ignore
                if target_type == int:
                    try:
                        return int(value)
                    except ValueError:
                        pass
                elif target_type == float:
                    try:
                        return float(value)
                    except ValueError:
                        pass
                elif target_type == bool:
                    if value.lower() in ['true', 'false']:
                        return value.lower() == 'true'
        return value

    def set_target_types(self, target_types: dict) -> None: # type: ignore
        self.target_types = target_types # type: ignore


class JghSerialization:
    """
    A class for serializing and deserializing generic types, primarily 
    Pydantic models. It can also handle dataclasses at a push but is not
    as powerful as Pydantic in terms of type coercion and validation.

    Attributes:
        None

    Properties:
        None

    Methods:
        serialise: Serializes an object to a JSON string. 
        validate: Deserializes a JSON string to a generic type.


    Functions:
        None
    """


    @staticmethod
    def serialise(inputmodel: Any) -> str:
        """
        Serializes any object to a JSON string. JSON is printed with an indent of 4 spaces.

        Args:
            inputmodel (Any): The object to serialize.

        Returns:
            str: The JSON string representation of the object.

        Raises:
            ValueError: If the object cannot be serialized to JSON.
        """
        _failure = "Unable to serialize object to JSON."
        _locus = "[serialise]"
        _locus2 = "[JghSerialization]"
   
        if not inputmodel:
            return "{}"
        try:
            if is_dataclass(inputmodel) and not isinstance(inputmodel, type):
                candidate_json = json.dumps(asdict(inputmodel), indent=4)
            elif isinstance(inputmodel, BaseModel):
                candidate_json = inputmodel.model_dump_json(indent=4, by_alias = True)
            else:
                candidate_json = json.dumps(inputmodel.__dict__, indent=4)
        except TypeError as e:
            input_type = type(inputmodel).__name__
            raise ValueError((f"Error: {_failure} {_locus} {_locus2}\nComment: The object of type '{input_type}' failed to serialise to JSON due to a TypeError.\nError Message: {pretty_error_message(e)}"))
        except ValueError as e:
            input_type = type(inputmodel).__name__
            raise ValueError((f"Error: {_failure} {_locus} {_locus2}\nComment: The object of type '{input_type}' failed to serialise to JSON due to a ValueError.\nError Message: {pretty_error_message(e)}"))
        
        return candidate_json

    @staticmethod
    def validate[T](inputJson: str, requiredModel: T) -> T:
        """
        Validates a JSON string and uses it to instatiate a model  
        of the specified type. if the model derives from the Pydantic
        BaseModel, and if serialisation_alias's or validation_aliase
        Choices are specified for the attributes of the model, the 
        aliases are respected during validation.

        Args:
            inputJson (str): The JSON string to validate.
            requiredModel[T]: The model type to deserialize to.
            It must be a dataclass or a Pydantic model.

        Returns:
            T: An instance of the specified model type.

        Raises:
            ValueError: If the JSON string cannot be deserialized to the specified
            model type or if a field in the JSON string is of the wrong type.
            To avoid a validation error if a field in the JSON is missing, provide 
            a default value for the field in the model definition. If a field is 
            superfluous (not defined in the model), it will be ignored during validation.
        """
        _failure = "Unable to deserialize JSON to object."
        _locus = "[validate]"
        _locus2 = "[JghSerialization]"
        
        if not inputJson:
            raise ValueError(f"Error: {_failure} {_locus} {_locus2}\nComment: The input JSON string is null or empty.")
        
        try:
            
            if is_dataclass(requiredModel):
                target_types = requiredModel.__annotations__
                answer = json.loads(inputJson, cls=CustomJSONDecoder, target_types=target_types)
                # answer = json.loads(inputJson, cls=CustomJSONDecoder)
                filtered_answer = {k: v for k, v in answer.items() if k in requiredModel.__annotations__} # Filter out any extra fields that are not in the dataclass if any
                return requiredModel(**filtered_answer) # type: ignore
            elif issubclass(requiredModel, BaseModel): # type: ignore
                # Handle Pydantic model deserialization - with powerful and clever type coercion for numbers and bools (strict=False)
                return requiredModel.model_validate_json(inputJson, strict=False)
            else:
                # Handle generic object deserialization
                answer = json.loads(inputJson)
                return requiredModel(**answer) # type: ignore
        except TypeError as e:
            raise ValueError((f"Error: {_failure} {_locus} {_locus2}\nComment: The input JSON string failed to deserialize as an object of Type '{requiredModel.__name__}' \n\t\tdue to a TypeError.\nError Message: {pretty_error_message(e)}\nInput string:\n\t{inputJson}")) # type: ignore
        except json.JSONDecodeError as e:
            raise ValueError((f"Error: {_failure} {_locus} {_locus2}\nComment: The input JSON string failed to deserialize as an object of Type '{requiredModel.__name__}' \n\t\tdue to a JSONDecodeError.\nError Message: {pretty_error_message(e)}\nInput string:\n\t{inputJson}"))
        except ValidationError as e:
            error_messages = "\n".join([f"\tField: {err['loc']}\n\tError: {err['msg']}" for err in e.errors()])
            raise ValueError((f"Error: {_failure} {_locus} {_locus2}\nComment: The input JSON string failed to validate as an object of Type '{requiredModel.__name__}' due to validation errors.\nValidation errors:\n{error_messages}\nInput string:\n\t{inputJson}"))


# example usage of the JghSerialization class
def main():
    # the tedious legwork to manually define and initialise attributes (__init__) to make a class serialisable and printable(__repr__)
    class SimpleModelV1:
        def __init__(self, id: int=0, name: str = "", is_active: bool = False):
            self.id = id
            self.name = name
            self.is_active = is_active
        def __repr__(self):
            return f"SimpleModelv1(id={self.id}, name='{self.name}', is_active={self.is_active})"
    simple_instance_v1 = SimpleModelV1()
    simple_instance_v1.id = 1
    simple_instance_v1.name = "simplemodelv1"
    simple_instance_v1.is_active = True
    json_string_v1 = JghSerialization.serialise(simple_instance_v1)
    print("\nSerialized JSON string for SimpleModelv1:\n")
    print(json_string_v1)
    roundtripped_instance_v1 = JghSerialization.validate(json_string_v1, SimpleModelV1)
    print("\nRound tripped SimpleModelv1 object:\n")
    print(roundtripped_instance_v1)

    # the beauty of using @dataclass to define a class to make it serialisable
    @dataclass
    class SimpleModelV2:
        id: int
        name: str = ""
        is_active: bool = False
    simple_instance_v2 = SimpleModelV2(id=2)
    simple_instance_v2.name = "simplemodelV2"
    simple_instance_v2.is_active = True
    json_string_v2 = JghSerialization.serialise(simple_instance_v2)
    print("\nSerialized JSON string:\n")
    print(json_string_v2)
    roundtripped_instance_v2 = JghSerialization.validate(json_string_v2, SimpleModelV2)
    print("\nRound tripped SimpleModelV2 object:\n")
    print(roundtripped_instance_v2)


if __name__ == "__main__":
    main()