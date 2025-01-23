"""
This module defines the JghSerialization class, which provides methods for 
serializing and deserializing objects.
"""
# Standard library imports
import json
from typing import Any, Type, TypeVar

# Local application imports
import pydantic as pydantic
from pydantic import Field

T = TypeVar('T', bound=pydantic.BaseModel)

class JghSerialization:
    """
    A class for serializing and deserializing generic types using Pydantic models.
    The type of the object to serialize or deserialize must be a Pydantic model.

    Attributes:
        None

    Properties:
        None

    Methods:
        to_json_from_object: Serializes an object to a JSON string. 
        to_object_from_json: Deserializes a JSON string to an object of 
                                the specified Pydantic model type.


    Functions:
        None
    """

    @staticmethod
    def to_json_from_object(inputmodel: Any) -> str:
        """
        Serializes an object to a JSON string. JSON is printed with an indent of 4 spaces.
        Field aliases are used in the serialization.

        Args:
            inputmodel (Any): The object to serialize.

        Returns:
            str: The JSON string representation of the object.

        Raises:
            ValueError: If the object cannot be serialized to JSON.
        """
        _failure = "Unable to serialize object to JSON using Pydantic."
        _locus = "[to_json_from_object]"
        _locus2 = "[JghSerialization]"
        
        if not inputmodel:
            return "{}"
        try:
            candidate_json = inputmodel.model_dump_json(indent=4, by_alias=True)

            # # Convert the Pydantic model instance to a dictionary
            # validDict = inputmodel.model_dump()
            # # Convert the dictionary to a JSON string
            # validJson = json.dumps(validDict)
        except TypeError as e:
            input_type = type(inputmodel).__name__
            raise ValueError((f"Error: {_failure} {_locus} {_locus2}\nComment: The object of type '{input_type}' failed to serialise to JSON due to a TypeError.\nError Message: {e}"))
        except ValueError as e:
            input_type = type(inputmodel).__name__
            raise ValueError((f"Error: {_failure} {_locus} {_locus2}\nComment: The object of type '{input_type}' failed to serialise to JSON due to a ValueError.\nError Message: {e}"))
        
        return candidate_json
        # return validJson

    @staticmethod
    def to_object_from_json(inputString: str, outputmodel: Type[T]) -> T:
        """
        Deserializes a JSON string to an object of the specified Pydantic model type.
        Field aliases are used in the deserialization.

        Args:
            inputString (str): The JSON string to deserialize.
            outputmodel (Type[T]): The Pydantic model type to deserialize to.

        Returns:
            T: An instance of the specified Pydantic model type.

        Raises:
            ValueError: If the JSON string cannot be deserialized to the specified
            model type or if a field in the JSON string is of the wrong type.
            To avoid a validation error if a field
            in the JSON is missing, provide a default value for the field in the
            model definition. If a field is superfluous (not defined in the model),
            it will be ignored during deserialization.
        """
        _failure = "Unable to deserialize JSON to object using Pydantic."
        _locus = "[to_object_from_json]"
        _locus2 = "[JghSerialization]"
        
        if not inputString:
            raise ValueError(f"Error: {_failure} {_locus} {_locus2}\nComment: The input JSON string is null or empty.")
        
        try:
            # Use Pydantic's model_validate_json method to deserialize and validate the JSON string
            return outputmodel.model_validate_json(inputString, strict=True)
        except TypeError as e:
            raise ValueError((f"Error: {_failure} {_locus} {_locus2}\nComment: The input JSON string failed to deserialize to an object of Type '{outputmodel.__name__}' \n\t\tdue to a TypeError.\nError Message: {e}\nInput string:\n\t{inputString}"))
        except json.JSONDecodeError as e:
            raise ValueError((f"Error: {_failure} {_locus} {_locus2}\nComment: The input JSON string failed to deserialize to an object of Type '{outputmodel.__name__}' \n\t\tdue to a JSONDecodeError.\nError Message: {e}\nInput string:\n\t{inputString}"))
        except pydantic.ValidationError as e:
            error_messages = "\n".join([f"\tField: {err['loc']}\n\tError: {err['msg']}" for err in e.errors()])
            raise ValueError((f"Error: {_failure} {_locus} {_locus2}\nComment: The input JSON string failed to deserialize to an object of Type '{outputmodel.__name__}' due to validation errors.\nValidation errors:\n{error_messages}\nInput string:\n\t{inputString}"))


# example usage of the JghSerialization class

if __name__ == "__main__":
#Following code defines a new class SimpleModelV1. because no defaults are provided, the parameters are implicitly required in the ctor
    class SimpleModelV1(pydantic.BaseModel):
        """
        all fields are required
        """
        id: int
        name: str
        is_active: bool

    # Create an instance of SimpleModelV1
    simple_instance = SimpleModelV1(id=1, name="Test", is_active=True)

    # Serialize the SimpleModelV1 instance to JSON
    json_string = JghSerialization.to_json_from_object(simple_instance)
    print("\nSerialized JSON string:")
    print(json_string)

    # Deserialize the JSON string back to a SimpleModelV1 instance
    roundtripped_instance = JghSerialization.to_object_from_json(json_string, SimpleModelV1)
    print("\nRound tripped SimpleModelV1 object:")
    print(roundtripped_instance)

#Following code defines a new class SimpleModelV2 with the same requirements as SimpleModelV1, but only id is required this time.

    class SimpleModelV2(pydantic.BaseModel):
        """
        Only 'id' is required, other fields are provided with defaults and are therefore optional.
        """
        id: int
        name: str = ""
        is_active: bool = False

    # Create an instance of SimpleModelV2 with only the required field
    simple_instance_v2 = SimpleModelV2(id=2)

    # Serialize the SimpleModelV2 instance to JSON
    json_string_v2 = JghSerialization.to_json_from_object(simple_instance_v2)
    print("\nSerialized JSON string for SimpleModelV2:")
    print(json_string_v2)

    # Deserialize the JSON string back to a SimpleModelV2 instance
    roundtripped_instance_v2 = JghSerialization.to_object_from_json(json_string_v2, SimpleModelV2)
    print("\nRound tripped SimpleModelV2 object:")
    print(roundtripped_instance_v2)

# Following code defines a new class SimpleModelV3 with the same attributes and requirements as SimpleModelV2, but uses Pydantic Field to explicitly define required/not required fields and their defaults.

    class SimpleModelV3(pydantic.BaseModel):
        """
        Only 'id' is required, other fields are provided with defaults using pydantic and are therefore optional.
        """
        id: int
        name: str = ""
        is_active: bool = Field(default=False, description="The active status of the model")

    # Create an instance of SimpleModelV3 with only the required field
    simple_instance_v3 = SimpleModelV3(id=3)

    # Serialize the SimpleModelV3 instance to JSON
    json_string_v3 = JghSerialization.to_json_from_object(simple_instance_v3)
    print("\nSerialized JSON string for SimpleModelV3:")
    print(json_string_v3)

    # Deserialize the JSON string back to a SimpleModelV3 instance
    roundtripped_instance_v3 = JghSerialization.to_object_from_json(json_string_v3, SimpleModelV3)
    print("\nRound tripped SimpleModelV3 object:")
    print(roundtripped_instance_v3)

# Following code defines SimpleModelV4 with the same attributes and requirements as SimpleModelV3.
# adds 'is_active' and 'is_valid', with differing Pydantic properties. 
# The roundtrip serialization and deserialization process respects the serialization_alias.

class SimpleModelV4(pydantic.BaseModel):
    """
    Only 'id' is required, other fields are provided with defaults using pydantic and are therefore optional.
    This time we demonstrate the use of aliases. alias and serialization_alias are very similar
    in that they are both used for serialisation. Both survive roundtripping. Validation_alias has no effect
    on serialisation. 
    """
    id: int = Field()
    name: str = Field(default="")
    is_valid: bool = Field(default=True, alias="alias_for_prop_is_valid")
    is_legal: bool = Field(default=True, validation_alias="validation_alias_for_prop_is_legal")
    is_active: bool = Field(default=True, serialization_alias="serialization_alias_for_prop_is_active")

# example 1: Create an instance of SimpleModelV4 with only the required field
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


# Serialize the SimpleModelV4 instance to JSON
json_string_v4 = JghSerialization.to_json_from_object(simple_instance_v4)
print("\nSerialized JSON string for SimpleModelV4:")
print(json_string_v4)

# Deserialize the JSON string back to a SimpleModelV4 instance
roundtripped_instance_v4 = JghSerialization.to_object_from_json(json_string_v4, SimpleModelV4)
print("\nRoundTripped SimpleModelV4 object:")
print(roundtripped_instance_v4)

# Assertions to prove that roundtripped_instance_v4 is identical to simple_instance_v4
assert simple_instance_v4.id == roundtripped_instance_v4.id, "ID does not match"
assert simple_instance_v4.name == roundtripped_instance_v4.name, "Name does not match"
assert simple_instance_v4.is_active == roundtripped_instance_v4.is_active, "is_active does not match"
assert simple_instance_v4.is_valid == roundtripped_instance_v4.is_valid, "is_valid does not match"
assert simple_instance_v4.is_legal == roundtripped_instance_v4.is_legal, "is_legal does not match"

print("All assertions passed. The roundtripped instance is identical to the original instance.")
