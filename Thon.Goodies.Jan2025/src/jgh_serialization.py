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
    A class for serializing and deserializing generic types, primarily 
    Pydantic models. It can also handle dataclasses at a push but is not
    as powerful as Pydantic in terms of type coercion and validation.

    N.B. the class cannot handle classes such as ordinary Python classes
    which as a rule are not serialisable to JSON without additional code.

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
            if isinstance(inputmodel, list):
                candidate_json = json.dumps([asdict(item) if is_dataclass(item) else item.model_dump() if isinstance(item, BaseModel) else item for item in inputmodel], indent=4)
            elif isinstance(inputmodel, dict):
                candidate_json = json.dumps(inputmodel, indent=4)
            elif isinstance(inputmodel, tuple):
                candidate_json = json.dumps(list(inputmodel), indent=4)
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
    def validate(inputJson: str, requiredModel: Union[Type[T], Type[List[T]], Type[Dict[str, T]], Type[Tuple[T, ...]], Type[Set[T]]]) -> Union[T, List[T], Dict[str, T], Tuple[T, ...], Set[T]]:
        """
        Validates a JSON string and uses it to instantiate a model  
        of the specified type. If the model derives from the Pydantic
        BaseModel, and if serialization_alias's or validation_aliases
        Choices are specified for the attributes of the model, the 
        aliases are respected during validation.

        Args:
            inputJson (str): The JSON string to validate.
            requiredModel (Union[Type[T], Type[List[T]], Type[Dict[str, T]], Type[Tuple[T, ...]], Type[Set[T]]]): The model type to deserialize to.
            It must be a dataclass, a Pydantic model, a list, a dictionary, a tuple, or a set.

        Returns:
            Union[T, List[T], Dict[str, T], Tuple[T, ...], Set[T]]: An instance of the specified model type.

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
            if hasattr(requiredModel, '__origin__') and requiredModel.__origin__ is list:
                answer = json.loads(inputJson)
                return [JghSerialization.validate(json.dumps(item), requiredModel.__args__[0]) for item in answer]
            elif hasattr(requiredModel, '__origin__') and requiredModel.__origin__ is dict:
                answer = json.loads(inputJson)
                return {k: JghSerialization.validate(json.dumps(v), requiredModel.__args__[1]) for k, v in answer.items()}
            elif hasattr(requiredModel, '__origin__') and requiredModel.__origin__ is tuple:
                answer = json.loads(inputJson)
                return tuple(JghSerialization.validate(json.dumps(item), requiredModel.__args__[0]) for item in answer)
            elif hasattr(requiredModel, '__origin__') and requiredModel.__origin__ is set:
                answer = json.loads(inputJson)
                return set(JghSerialization.validate(json.dumps(item), requiredModel.__args__[0]) for item in answer)
            elif is_dataclass(requiredModel):
                answer = json.loads(inputJson)
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
    print("\nSerialized JSON string for UserPydantic:\n")
    print(json_string)

    # Deserialize the JSON string back to a User instance
    deserialized_user = JghSerialization.validate(json_string, UserPydantic)
    print("\nDeserialized User instance:\n")
    print(deserialized_user)

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
    print("\nSerialized JSON string for UserDataclass:\n")
    print(json_string)

    # Deserialize the JSON string back to a UserDataclass instance
    deserialized_user = JghSerialization.validate(json_string, UserDataclass)
    print("\nDeserialized UserDataclass instance:\n")
    print(deserialized_user)


    # # Define nested regular Python classes with optional fields
    # class AddressPythonclass:
    #     def __init__(self, street: str, city: str, zipcode: Optional[str] = None):
    #         self.street = street
    #         self.city = city
    #         self.zipcode = zipcode

    #     def to_dict(self) -> Dict[str, Any]:
    #         return {
    #             "street": self.street,
    #             "city": self.city,
    #             "zipcode": self.zipcode
    #         }

    #     @classmethod
    #     def from_dict(cls, data: Dict[str, Any]) -> 'AddressPythonclass':
    #         return cls(
    #             street=data.get("street"),
    #             city=data.get("city"),
    #             zipcode=data.get("zipcode")
    #         )

    # class UserPythonclass:
    #     def __init__(self, id: int, name: str, address: AddressPythonclass, friends: Optional[List[Dict[str, Any]]] = None):
    #         self.id = id
    #         self.name = name
    #         self.address = address
    #         self.friends = friends

    #     def to_dict(self) -> Dict[str, Any]:
    #         return {
    #             "id": self.id,
    #             "name": self.name,
    #             "address": self.address.to_dict(),
    #             "friends": self.friends
    #         }

    #     @classmethod
    #     def from_dict(cls, data: Dict[str, Any]) -> 'UserPythonclass':
    #         return cls(
    #             id=data.get("id"),
    #             name=data.get("name"),
    #             address=AddressPythonclass.from_dict(data.get("address")),
    #             friends=data.get("friends")
    #         )
    # # Create an instance of the nested regular Python class with optional fields
    # user_instance = UserPythonclass(
    #     id=1,
    #     name="John Doe",
    #     address=AddressPythonclass(street="123 Main St", city="Anytown"),
    #     friends=[
    #         {"id": 2, "name": "Jane Smith"},
    #         {"id": 3, "name": "Emily Johnson"}
    #     ]
    # )

    # # Serialize the nested regular Python class to a JSON string
    # json_string = JghSerialization.serialise(user_instance)
    # print("\nSerialized JSON string for UserPythonclass:\n")
    # print(json_string)

    # # Deserialize the JSON string back to a UserPythonclass instance
    # deserialized_user = JghSerialization.validate(json_string, UserPythonclass)
    # print("\nDeserialized UserPythonclass instance:\n")
    # print(deserialized_user)

    # # Test serialization and deserialization of a tuple
    # sample_tuple = (1, 2, 3)
    # json_string = JghSerialization.serialise(sample_tuple)
    # print("\nSerialized JSON string for tuple:\n")
    # print(json_string)
    # deserialized_tuple = JghSerialization.validate(json_string, Tuple[int, int, int])
    # print("\nDeserialized tuple:\n")
    # print(deserialized_tuple)

    # # Test serialization and deserialization of a set
    # sample_set = {1, 2, 3}
    # json_string = JghSerialization.serialise(sample_set)
    # print("\nSerialized JSON string for set:\n")
    # print(json_string)
    # deserialized_set = JghSerialization.validate(json_string, Set[int])
    # print("\nDeserialized set:\n")
    # print(deserialized_set)

if __name__ == "__main__":
    main()
