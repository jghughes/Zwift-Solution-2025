"""
This module defines the JghSerialization class, which provides methods for 
serializing and deserializing objects.
"""
# Standard library imports
import json
from typing import Any, Type, TypeVar
from dataclasses import dataclass, asdict, is_dataclass

# Local application imports
from pydantic import BaseModel, ValidationError, Field

T = TypeVar('T')
# T = TypeVar('T', bound=pydantic.BaseModel)

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

class JghSerialization:
    """
    A class for serializing and deserializing generic types.

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
    def validate(inputJson: str, requiredModel: Type[T]) -> T:
        """
        Validates a JSON string and uses it to instatiate a model  
        of the specified type. if the model derives from the Pydantic
        BaseModel, and if aliases or validation_aliases are specified
        for the attributes of the model, the aliases are respected
        during validation.

        Args:
            inputJson (str): The JSON string to validate.
            requiredModel (Type[T]): The model type to deserialize to.

        Returns:
            T: An instance of the specified model type.

        Raises:
            ValueError: If the JSON string cannot be deserialized to the specified
            model type or if a field in the JSON string is of the wrong type.
            To avoid a validation error if a field in the JSON is missing, provide 
            a default value for the field in the model definition. If a field is 
            superfluous (not defined in the model), it will be ignored during validation.
        """
        _failure = "Unable to deserialize JSON to object using Pydantic."
        _locus = "[validate]"
        _locus2 = "[JghSerialization]"
        
        if not inputJson:
            raise ValueError(f"Error: {_failure} {_locus} {_locus2}\nComment: The input JSON string is null or empty.")
        
        try:
            
            if is_dataclass(requiredModel):
                # Handle dataclass deserialization
                answer = json.loads(inputJson)
                return requiredModel(**answer)
            elif issubclass(requiredModel, BaseModel):
                # Handle Pydantic model deserialization - with type coercion (strict=True)
                return requiredModel.model_validate_json(inputJson)
            else:
                # Handle generic object deserialization
                answer = json.loads(inputJson)
                return requiredModel(**answer)
        except TypeError as e:
            raise ValueError((f"Error: {_failure} {_locus} {_locus2}\nComment: The input JSON string failed to deserialize as an object of Type '{requiredModel.__name__}' \n\t\tdue to a TypeError.\nError Message: {pretty_error_message(e)}\nInput string:\n\t{inputJson}"))
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

    # the even greater beauty of using powerful pydantic to define a class and make it serialisable
    class SimpleModelV3(BaseModel):
        """
        A beautiful pydantic model deriving from BaseModel. Uses Pydantic Field to explicitly define required/not required fields and their defaults.

        Only 'id' is required, other fields are provided with defaults using pydantic and are therefore optional.
        """
        id: int
        name: str = ""
        is_active: bool = Field(default=False, description="The active status of the model")
    simple_instance_v3 = SimpleModelV3(id=3)
    simple_instance_v3.name = "SimpleModelV3"
    simple_instance_v3.is_active = True
    json_string_v3 = JghSerialization.serialise(simple_instance_v3)
    print("\nSerialized JSON string for SimpleModelV3:\n")
    print(json_string_v3)
    roundtripped_instance_v3 = JghSerialization.validate(json_string_v3, SimpleModelV3)
    print("\nRound tripped SimpleModelV3 object:\n")
    print(roundtripped_instance_v3)

    # the even greater beauty of using powerful pydantic to define a class and make it serialisable
    class SimpleModelV4(BaseModel):
        """
        Same SimpleModelV3, adding 'is_active' and 'is_valid' to demonstrate the use of aliases. 
        Alias and serialization_alias are very similar in that they are both used for serialisation. 
        Both survive roundtripping. Validation_alias has no effect on serialisation, it's brilliant
        for deserialisation
        """
        id: int = Field(default=4)
        name: str = Field(default="SimpleModelV4")
        is_valid: bool = Field(default=True, alias="alias_for_prop_is_valid")
        is_legal: bool = Field(default=True, validation_alias="validation_alias_for_prop_is_legal")
        is_active: bool = Field(default=True, serialization_alias="serialization_alias_for_prop_is_active")
    # example 1: Create an instance of SimpleModelV4 with only one field. The other fields will
    # be set to their defaults.
    simple_instance_v4 = SimpleModelV4(id=4)
    # example 2: create an instance of SimpleModelV4 specifying all fields. Notice that if a field 
    # has a pydantic alias, the alias akwardly suppresses the field name in the ctor. 
    # The same is not true for serialization_alias (used for serialization only),
    # or for validation_alias (used for validation only).
    # The alias is used in the JSON serialization and deserialization as is 
    # the serialization_alias. The validation_alias is ignored in serialization.
    # In all three cases, field name usage is normal outside the ctor.
    simple_instance_v4 = SimpleModelV4(
        id=4,
        name="Test Model",
        alias_for_prop_is_valid=False,
        is_legal=True,
        is_active=False
    )
    simple_instance_v4.is_valid = True
    simple_instance_v4.is_legal = True
    simple_instance_v4.is_active = True
    json_string_v4 = JghSerialization.serialise(simple_instance_v4)
    print("\nSerialized JSON string for SimpleModelV4:\n")
    print(json_string_v4)
    roundtripped_instance_v4 = JghSerialization.validate(json_string_v4, SimpleModelV4)
    print("\nRoundTripped SimpleModelV4 object:\n")
    print(roundtripped_instance_v4)
    # Assertions to prove that roundtripped_instance_v4 is identical to simple_instance_v4
    assert simple_instance_v4.id == roundtripped_instance_v4.id, "ID does not match"
    assert simple_instance_v4.name == roundtripped_instance_v4.name, "Name does not match"
    assert simple_instance_v4.is_active == roundtripped_instance_v4.is_active, "is_active does not match"
    assert simple_instance_v4.is_valid == roundtripped_instance_v4.is_valid, "is_valid does not match"
    assert simple_instance_v4.is_legal == roundtripped_instance_v4.is_legal, "is_legal does not match"
    print("\nAll assertions passed. The roundtripped instance is identical to the original instance.\n")

if __name__ == "__main__":
    main()