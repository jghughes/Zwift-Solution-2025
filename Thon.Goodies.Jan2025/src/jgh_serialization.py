from typing import Type, TypeVar, List, Dict, Union, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict, is_dataclass
from pydantic import BaseModel, ValidationError
import json


# Helper function to write a pretty error message
def pretty_error_message(ex: Exception) -> str:
    """
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


T = TypeVar('T')

class JghSerialization:
    """
    A class for serializing and deserializing certian generic types that are
    expressly serialisable, i.e. Pydantic models and DataClasses. Ordinary
    Python classes are not serialisable. Use Pydantic classes for their
    superiority in type coercion and validation. This class is of limited 
    applicability. It might not work for your exact requirements. It is not
    a one-size-fits-all solution. It is not a substitute for a full-fledged
    serialization. Be sure to test it thoroughly in your specific use case.

    Methods:
        serialise: Serializes an object to a JSON string. 
        validate: Deserializes a JSON string to a generic type.
    """

    @staticmethod
    def serialise(inputmodel: Any) -> str:
        """
        Attempts to serialise an expressly serialisable object to a JSON string.
        JSON is printed with an indent of 4 spaces.

        This method can explicitly handle:
        - Individual dataclasses
        - Individual Pydantic models
        - Lists of dataclasses or Pydantic models
        - Dictionaries with dataclasses or Pydantic models as values
        - Tuples of dataclasses or Pydantic models
        - Sets of integers and strings but not value types

        For dataclasses, it uses the `asdict` function to convert them to dictionaries.
        For Pydantic models, it uses the `model_dump` method to convert them to dictionaries.
        For other objects, it attempts to serialize their `__dict__` attribute.

        Args:
            inputmodel (Any): The object to attempt to serialize.

        Returns:
            str: The JSON string representation of the object.

        Raises:
            ValueError: If the object cannot be serialized to JSON.

        Limitations:
        - Cannot handle ordinary Python classes that are not dataclasses or Pydantic models.
        - Cannot handle nested complex types beyond the specified types (e.g. nested lists of dictionaries).
        - Extra fields in the JSON that are not defined in the model will be ignored for dataclasses.
        - Sets can only be serialized if the elements are integers or strings.
        """
        _failure = "Unable to serialize object to JSON."
        _locus = "[serialise]"
        _locus2 = "[JghSerialization]"
   
        if not inputmodel:
            return "{}"
        try:
            if isinstance(inputmodel, list):
                candidate_json = json.dumps([asdict(item) if is_dataclass(item) else item.model_dump() if isinstance(item, BaseModel) else item for item in inputmodel], indent=4)
            elif isinstance(inputmodel, dict):
                candidate_json = json.dumps({k: asdict(v) if is_dataclass(v) else v.model_dump() if isinstance(v, BaseModel) else v for k, v in inputmodel.items()}, indent=4)
            elif isinstance(inputmodel, tuple):
                candidate_json = json.dumps([asdict(item) if is_dataclass(item) else item.model_dump() if isinstance(item, BaseModel) else item for item in inputmodel], indent=4)
            elif isinstance(inputmodel, set):
                candidate_json = json.dumps(list(inputmodel), indent=4)
            elif is_dataclass(inputmodel) and not isinstance(inputmodel, type):
                candidate_json = json.dumps(asdict(inputmodel), indent=4)
            elif isinstance(inputmodel, BaseModel):
                candidate_json = inputmodel.model_dump_json(indent=4, by_alias=True)
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
    def validate(inputJson: str, requiredModel: Union[Type[T], Type[List[T]], Type[Dict[Union[str, int], T]], Type[Tuple[T, ...]], Type[Set[T]]]) -> Union[T, List[T], Dict[Union[str, int], T], Tuple[T, ...], Set[T]]:
        """
        Attempts to validates a JSON string and uses it to instantiate a model 
        of the specified object and type. It is strongly recommended to use Pydantic 
        objects for validation.

        This method can validate and deserialize JSON strings into generic objects:
        - Pydantic models
        - Dataclasses
        - Lists of the above types
        - Dictionaries with string keys or int keys and the above types as values
        - Tuples of the above types
        - Sets of the above types (only if T is int or string)

        Args:
            inputJson (str): The JSON string to validate.
            requiredModel (Union[Type[T], Type[List[T]], Type[Dict[Union[str, int], T]], Type[Tuple[T, ...]], Type[Set[T]]]): The model type to deserialize to.

        Returns:
            Union[T, List[T], Dict[Union[str, int], T], Tuple[T, ...], Set[T]]: An instance of the specified model type.

        Raises:
            ValueError: If the JSON string cannot be deserialized to the specified model type or if a field in the JSON string is of the wrong type.

        Limitations:
            - Cannot validate and deserialize ordinary Python classes that are not Pydantic models or dataclasses.
            - Cannot handle nested complex types beyond the specified types (e.g., nested lists of dictionaries).
            - Extra fields in the JSON that are not defined in the model will be ignored for dataclasses.
            - Sets can only be validated and deserialized if T is hashable.
        """
        _failure = "Unable to deserialize JSON to object."
        _locus = "[validate]"
        _locus2 = "[JghSerialization]"
        
        if not inputJson:
            raise ValueError(f"Error: {_failure} {_locus} {_locus2}\nComment: The input JSON string is null or empty.")
        
        try:
            if hasattr(requiredModel, '__origin__') and requiredModel.__origin__ is list:
                answer = json.loads(inputJson)
                return [JghSerialization.validate(json.dumps(item), requiredModel.__args__[0]) for item in answer]
            elif hasattr(requiredModel, '__origin__') and requiredModel.__origin__ is dict:
                answer = json.loads(inputJson)
                key_type = requiredModel.__args__[0]
                value_type = requiredModel.__args__[1]
                if key_type is int:
                    try:
                        return {int(k): JghSerialization.validate(json.dumps(v), value_type) for k, v in answer.items()}
                    except ValueError as e:
                        raise ValueError(f"Error: {_failure} {_locus} {_locus2}\nComment: The input JSON string contains non-integer keys for a dictionary with integer keys.\nError Message: {pretty_error_message(e)}\nInput string:\n\t{inputJson}")
                else:
                    return {k: JghSerialization.validate(json.dumps(v), value_type) for k, v in answer.items()}
            elif hasattr(requiredModel, '__origin__') and requiredModel.__origin__ is tuple:
                answer = json.loads(inputJson)
                return tuple(JghSerialization.validate(json.dumps(item), requiredModel.__args__[i]) if isinstance(item, dict) else item for i, item in enumerate(answer))
            elif hasattr(requiredModel, '__origin__') and requiredModel.__origin__ is set:
                answer = json.loads(inputJson)
                return set(JghSerialization.validate(json.dumps(item), requiredModel.__args__[0]) if isinstance(item, dict) else item for item in answer)
            elif is_dataclass(requiredModel):
                answer = json.loads(inputJson)
                filtered_answer = {k: v for k, v in answer.items() if k in requiredModel.__annotations__} # Filter out any extra fields that are not in the dataclass if any
                return requiredModel(**filtered_answer) # type: ignore
            elif issubclass(requiredModel, BaseModel): # type: ignore
                # Handle Pydantic model deserialization - with powerful and clever type coercion for numbers and bools (strict=False)
                answer = requiredModel.model_validate_json(inputJson, strict=False)
                return answer
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

    import logging
    from jgh_logging import jgh_configure_logging
    # Configure logging
    jgh_configure_logging("appsettings.json")
    logger = logging.getLogger(__name__)

    # Define nested dataclasses with optional fields
    @dataclass
    class AddressDataclass:
        street: str
        city: str
        zipcode: Optional[str] = None

    @dataclass
    class UserDataclass:
        id: int
        name: str
        address: AddressDataclass
        friends: Optional[List[Dict[str, Any]]] = None

    # Define nested Pydantic models with optional fields
    class AddressPydantic(BaseModel):
        street: str
        city: str
        zipcode: Optional[str] = None

    class UserPydantic(BaseModel):
        id: int
        name: str
        address: AddressPydantic
        friends: Optional[List[Dict[str, Any]]] = None

    # Create an instance of the nested model with optional fields
    user_instance = UserPydantic(
        id=1,
        name="John Doe",
        address=AddressPydantic(street="123 Main St", city="Anytown"),
        friends=[
            {"id": 2, "name": "Jane Smith"},
            {"id": 3, "name": "Emily Johnson"}
        ]
    )

    # Serialize the nested model to a JSON string
    json_string = JghSerialization.serialise(user_instance)
    logger.info("\nSerialized JSON string for UserPydantic:\n")
    logger.info(json_string)

    # Deserialize the JSON string back to a User instance
    deserialized_user = JghSerialization.validate(json_string, UserPydantic)
    logger.info("\nDeserialized User instance:\n")
    logger.info(deserialized_user)

    # Create an instance of the nested dataclass with optional fields
    user_instance = UserDataclass(
        id=1,
        name="John Doe",
        address=AddressDataclass(street="123 Main St", city="Anytown"),
        friends=[
            {"id": 2, "name": "Jane Smith"},
            {"id": 3, "name": "Emily Johnson"}
        ]
    )

    # Serialize the nested dataclass to a JSON string
    json_string = JghSerialization.serialise(user_instance)
    logger.info("\nSerialized JSON string for UserDataclass:\n")
    logger.info(json_string)

    # Deserialize the JSON string back to a UserDataclass instance
    deserialized_user = JghSerialization.validate(json_string, UserDataclass)
    logger.info("\nDeserialized UserDataclass instance:\n")
    logger.info(deserialized_user)

    # Test serialization and deserialization of a list of three addresses
    addresses_list = [
        AddressDataclass(street="123 Main St", city="Anytown", zipcode="12345"),
        AddressDataclass(street="456 Elm St", city="Othertown", zipcode="67890"),
        AddressDataclass(street="789 Oak St", city="Sometown", zipcode="11223")
    ]
    json_string = JghSerialization.serialise(addresses_list)
    logger.info("\nSerialized JSON string for list of addresses:\n")
    logger.info(json_string)
    deserialized_addresses_list = JghSerialization.validate(json_string, List[AddressDataclass])
    logger.info("\nDeserialized list of addresses:\n")
    logger.info(deserialized_addresses_list)
    reserialized_json_string = JghSerialization.serialise(deserialized_addresses_list)
    logger.info("\nReserialized JSON string for list of addresses:\n")
    logger.info(reserialized_json_string)

    # Test serialization and deserialization of a dictionary of three addresses
    addresses_dict = {
        "home": AddressPydantic(street="123 Main St", city="Anytown", zipcode="12345"),
        "work": AddressPydantic(street="456 Elm St", city="Othertown", zipcode="67890"),
        "vacation": AddressPydantic(street="789 Oak St", city="Sometown", zipcode="11223")
    }
    json_string = JghSerialization.serialise(addresses_dict)
    logger.info("\nSerialized JSON string for dictionary of addresses:\n")
    logger.info(json_string)
    deserialized_addresses_dict = JghSerialization.validate(json_string, Dict[str, AddressPydantic])
    logger.info("\nDeserialized dictionary of addresses:\n")
    logger.info(deserialized_addresses_dict)
    reserialized_json_string = JghSerialization.serialise(deserialized_addresses_dict)
    logger.info("\nReserialized JSON string for dictionary of addresses:\n")
    logger.info(reserialized_json_string)

    # Test serialization and deserialization of a list of three UserDataclass instances
    users_list = [
        UserDataclass(
            id=1,
            name="John Doe",
            address=AddressDataclass(street="123 Main St", city="Anytown", zipcode="12345"),
            friends=[{"id": 2, "name": "Jane Smith"}, {"id": 3, "name": "Emily Johnson"}]
        ),
        UserDataclass(
            id=2,
            name="Jane Smith",
            address=AddressDataclass(street="456 Elm St", city="Othertown", zipcode="67890"),
            friends=[{"id": 1, "name": "John Doe"}, {"id": 3, "name": "Emily Johnson"}]
        ),
        UserDataclass(
            id=3,
            name="Emily Johnson",
            address=AddressDataclass(street="789 Oak St", city="Sometown", zipcode="11223"),
            friends=[{"id": 1, "name": "John Doe"}, {"id": 2, "name": "Jane Smith"}]
        )
    ]

    json_string = JghSerialization.serialise(users_list)
    logger.info("\nSerialized JSON string for list of UserDataclass instances:\n")
    logger.info(json_string)
    deserialized_users_list = JghSerialization.validate(json_string, List[UserDataclass])
    logger.info("\nDeserialized list of UserDataclass instances:\n")
    logger.info(deserialized_users_list)
    reserialized_json_string = JghSerialization.serialise(deserialized_users_list)
    logger.info("\nReserialized JSON string for list of UserDataclass instances:\n")
    logger.info(reserialized_json_string)

    # Test serialization and deserialization of a dictionary of three UserDataclass instances
    users_dict = {
        "john": UserDataclass(
            id=1,
            name="John Doe",
            address=AddressDataclass(street="123 Main St", city="Anytown", zipcode="12345"),
            friends=[{"id": 2, "name": "Jane Smith"}, {"id": 3, "name": "Emily Johnson"}]
        ),
        "jane": UserDataclass(
            id=2,
            name="Jane Smith",
            address=AddressDataclass(street="456 Elm St", city="Othertown", zipcode="67890"),
            friends=[{"id": 1, "name": "John Doe"}, {"id": 3, "name": "Emily Johnson"}]
        ),
        "emily": UserDataclass(
            id=3,
            name="Emily Johnson",
            address=AddressDataclass(street="789 Oak St", city="Sometown", zipcode="11223"),
            friends=[{"id": 1, "name": "John Doe"}, {"id": 2, "name": "Jane Smith"}]
        )
    }

    json_string = JghSerialization.serialise(users_dict)
    logger.info("\nSerialized JSON string for dictionary of UserDataclass instances:\n")
    logger.info(json_string)
    deserialized_users_dict = JghSerialization.validate(json_string, Dict[str, UserDataclass])
    logger.info("\nDeserialized dictionary of UserDataclass instances:\n")
    logger.info(deserialized_users_dict)
    reserialized_json_string = JghSerialization.serialise(deserialized_users_dict)
    logger.info("\nReserialized JSON string for dictionary of UserDataclass instances:\n")
    logger.info(reserialized_json_string)

    # Test serialization and deserialization of a dictionary of three UserDataclass instances with integer keys
    users_dict_int_keys = {
        1: UserDataclass(
            id=1,
            name="John Doe",
            address=AddressDataclass(street="123 Main St", city="Anytown", zipcode="12345"),
            friends=[{"id": 2, "name": "Jane Smith"}, {"id": 3, "name": "Emily Johnson"}]
        ),
        2: UserDataclass(
            id=2,
            name="Jane Smith",
            address=AddressDataclass(street="456 Elm St", city="Othertown", zipcode="67890"),
            friends=[{"id": 1, "name": "John Doe"}, {"id": 3, "name": "Emily Johnson"}]
        ),
        3: UserDataclass(
            id=3,
            name="Emily Johnson",
            address=AddressDataclass(street="789 Oak St", city="Sometown", zipcode="11223"),
            friends=[{"id": 1, "name": "John Doe"}, {"id": 2, "name": "Jane Smith"}]
        )
    }

    json_string = JghSerialization.serialise(users_dict_int_keys)
    logger.info("\nSerialized JSON string for dictionary of UserDataclass instances with integer keys:\n")
    logger.info(json_string)
    deserialized_users_dict_int_keys = JghSerialization.validate(json_string, Dict[int, UserDataclass])
    logger.info("\nDeserialized dictionary of UserDataclass instances with integer keys:\n")
    logger.info(deserialized_users_dict_int_keys)
    reserialized_json_string = JghSerialization.serialise(deserialized_users_dict_int_keys)
    logger.info("\nReserialized JSON string for dictionary of UserDataclass instances with integer keys:\n")
    logger.info(reserialized_json_string)


    # Test serialization and deserialization of a tuple - sample_tuple = (1, 2, 3)
    sample_tuple = (1, 2, 3)
    json_string = JghSerialization.serialise(sample_tuple)
    logger.info("\nSerialized JSON string for sample tuple '(1, 2, 3)':\n")
    logger.info(json_string)
    deserialized_tuple = JghSerialization.validate(json_string, Tuple[int, int, int])
    logger.info("\nDeserialized tuple:\n")
    logger.info(deserialized_tuple)

    # Test serialization and deserialization of a tuple with int, bool, and UserDataclass
    sample_tuple = (
        42,
        True,
        UserDataclass(
            id=1,
            name="John Doe",
            address=AddressDataclass(street="123 Main St", city="Anytown", zipcode="12345"),
            friends=[{"id": 2, "name": "Jane Smith"}, {"id": 3, "name": "Emily Johnson"}]
        )
    )

    json_string = JghSerialization.serialise(sample_tuple)
    logger.info("\nSerialized JSON string for tuple (int, bool, UserDataclass):\n")
    logger.info(json_string)
    deserialized_tuple = JghSerialization.validate(json_string, Tuple[int, bool, UserDataclass])
    logger.info("\nDeserialized tuple (int, bool, UserDataclass):\n")
    logger.info(deserialized_tuple)

    # # Test serialization and deserialization of a simple set (not value types!)
    sample_set = {1, 2, 3}
    json_string = JghSerialization.serialise(sample_set)
    logger.info("\nSerialized JSON string for set:\n")
    logger.info(json_string)
    deserialized_set = JghSerialization.validate(json_string, Set[int])
    logger.info("\nDeserialized set:\n")
    logger.info(deserialized_set)


if __name__ == "__main__":
    main()
