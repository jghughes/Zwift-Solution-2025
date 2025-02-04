"""
Pydantic is a specialist package for data serialisation and deserialisation in Python.
The term 'validation' is synonymous with 'deserialisation'. Validation
is where the package shows it's sophistication.

In Pydantic, validation is performed on the input JSON when the model 
is instantiated from a dictionary or JSON string. 

Upon validation, Pydantic uses the JSON field name to map the input data to the
model attribute name. If an alias is specified for an attribute, Pydantic will use the
alias to map the input data to the model attribute. If a validation_alias is specified
for an attribute, Pydantic will prefer the validation_alias over the alias to map the
input data to the model attribute. ValidationChoices is a Pydantic class that allows
for multiple multiple validation_aliases for a field.

Upon serialisation, Pydantic uses the attribute name of the model to create the
JSON field name. If an alias is specified for an attribute, Pydantic will use the
alias to create the JSON field name. If a serialization_alias is specified for an
attribute, Pydantic will prefer the serialization_alias over the alias to create 
the JSON field name.

For round-tripping:-

    1. The model attribute name and the JSON field name must be identical. OR
    2. If an alias is specified for an attribute, the alias and the JSON field name must be identical. OR
    3. For sophisticated applications where we want to use an alias for serialisation but enjoy 
        the power and flexibility of a variety of aliases for validation, I recommend to use 
        the serialisation_alias in conjunction with the validation_alias(AliasChoices()). 
        To succeeed, the list of AliasChoices must always include the actual attribute name.
"""

# Standard library imports
import sys
import logging
import unittest
import pydantic as pydantic
from pydantic import ConfigDict, AliasGenerator, AliasChoices, Field, BeforeValidator, AfterValidator
from typing import Any, Annotated

# Local application imports
from jgh_serialization import JghSerialization

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Define convenient default values for the tests.
# Note the intentional use of caps, you can fiddle and add to the ConfigDict 
# to play with ConfigDict(str_to_lower=True)
default_john: str = "John"
default_middlenames : list[str] = ["Gerald", "Elana", "Thomas", "Alexandra"]
default_jones: str = "Jones"
default_false: bool = False
default_99 = 99
default_email: str = "email@zip.com"
default_eglinton: str = "Eglinton"


# Define convenient output aliases for the tests
id_serialization_alias = "id_serialization_alias"
first_serialization_alias = "first_serialization_alias"
middlenames_serialization_alias = "middlenames_serialization_alias"
last_serialization_alias = "last_serialization_alias"
isactive_serialization_alias = "isactive_serialization_alias"
age_serialization_alias = "age_serialization_alias"
email_serialization_alias = "email_serialization_alias"
street_serialization_alias = "street_serialization_alias"
serialization_alias_map : dict[str,str] ={
    "id": f"{id_serialization_alias}",
    "first": f"{first_serialization_alias}",
    "middle_names": f"{middlenames_serialization_alias}",
    "last": f"{last_serialization_alias}",
    "isactive": f"{isactive_serialization_alias}",
    "age": f"{age_serialization_alias}",
    "email": f"{email_serialization_alias}",
    "street" : f"{street_serialization_alias}"
    }

# Make a dict of lists of AliasChoices to map model attributes to field names. NB. Always include attribute name and serialisation_alias (if defined) in each list to ensure roundtripping success.
validation_alias_choices_map : dict[str,AliasChoices] = {
    "id": AliasChoices("id", f"{id_serialization_alias}"),  
    "first": AliasChoices("first", f"{first_serialization_alias}"), 
    "middle_names": AliasChoices("middle_names", f"{middlenames_serialization_alias}"), 
    "last": AliasChoices("last", f"{last_serialization_alias}"),
    "isactive": AliasChoices("isactive", f"{isactive_serialization_alias}"),
    "age": AliasChoices("age", f"{age_serialization_alias}"),
    "email": AliasChoices("email", f"{email_serialization_alias}"),
    "street": AliasChoices("street", f"{street_serialization_alias}") 
}

# Prepare a ConfigDict for all test models. Assign this to the pydantic model's model_config attribute.
# Myriad settings and options available.
# As examples for the tests, we will use the alias_generator to set the serialization_alias and validation_alias for the model.
# To go further, you can use the str_to_lower setting to automatically convert incomming string values to lowerr case
# across the board. In real life, this ensures that all string data in the model is stored in a consistent lowercase format. 
# Helps avoid issues related to case sensitivity.

configdict_default = ConfigDict() # Default configdict
configdictV1 = ConfigDict(str_to_lower=True) # recommended for real life use - but some assertions will fail down below becuase I have not written tests to handle this.
configdictV3 = ConfigDict(
        alias_generator=AliasGenerator(
            alias=None,
            serialization_alias=lambda field_name: serialization_alias_map.get(field_name, field_name), 
            validation_alias=lambda field_name: validation_alias_choices_map.get(field_name, field_name)))

groovy_configdict = configdictV3

# Helper function to write a pretty error messages for the tests
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


# All the tests
class Test_JghSerialization(unittest.TestCase):

    def setUp(self):
        logger.info(f"\nTEST NAME: {self._testMethodName}")
        logger.info(f"-" * 100)
        test_method = getattr(self, self._testMethodName)
        if test_method.__doc__:
            logger.info(f"TEST DOCSTRING:\n\t{test_method.__doc__.strip()}")
            logger.info(f"-" * 100)

    def tearDown(self):
        logger.info(f"-" * 100)
        logger.info(f"TEST FINISHED: {self._testMethodName}")
        logger.info(f"=" * 100)
        logger.info(f"\n")

    def test_01_how_to_define_and_roundtrip_a_pydantic_object_with_no_config(self):
        """
        This test case demonstrates how to define and instantiate a sophisticated Pydantic model
        but with any serialisation config. Tests JghSerialisation.serialise and JghSerialisation.validate.

        The TestModel class showcases various Pydantic features including:
        - Type annotations with the union operator (|) to allow attributes to accept multiple types, making them optional if None is included.
        - Field defaults using the Field class with a factory method (default_factory) for value types like lists, ensuring a new instance is created for each model instance.

        The test verifies:
        - Successful instantiation of the TestModel class.
        - Serialization of the model instance to a JSON string.
        - Validation and deserialization of the JSON string back to a TestModel.
        - Roundtrip success by asserting that the deserialized object is an instance of TestModel and matches the original instance.

        If any assertion fails, the test logs an error message and fails.
        """

        class TestModel(pydantic.BaseModel):
            """
            This Pydantic model demonstrates various features including model configuration, type annotations, and field defaults.

            Pydantic Features:
            - Union Type Annotations:
                The union operator (|) allows attributes to accept multiple types, making them optional if None is included.
            - Field with Factory Method:
                For value types like lists, a factory method (default_factory) is used to set the default value, ensuring a new instance is created for each model instance.

            """
            id: int | None = 0 #NB # The union operator means the attribute value doesn't have to be sent or received as a field in the JSON string.
            first: str | None = default_john
            middle_names: list[str] | None = Field(default_factory=list[str]) #NB. must use a factory for objects, a class or function is passed to the factory and not a instance of such, notice we are not specifying a default here. just to experiment 
            last: str | None = default_jones
            isactive: bool | None = default_false
            age: int | None = default_99
            email: str | None = default_email
            street: str | None = default_eglinton

        try:
            instance = TestModel()
            json_str = JghSerialization.serialise(instance)
            logger.info(f"\nJSON STRING:\n\t{json_str}")
            roundtripped = JghSerialization.validate(json_str, TestModel)
            self.assertIsInstance(roundtripped, TestModel)
            self.assertEqual(roundtripped.id, instance.id)
            self.assertEqual(roundtripped.first, instance.first)
            self.assertEqual(roundtripped.middle_names, instance.middle_names)
            self.assertEqual(roundtripped.last, instance.last)
            self.assertEqual(roundtripped.isactive, instance.isactive)
            self.assertEqual(roundtripped.age, instance.age)
            self.assertEqual(roundtripped.email, instance.email)
            self.assertEqual(roundtripped.street, instance.street)
            logger.info(
                f"TEST OUTCOME: PASS:\n\tRoundtrip succeeded.\nInput object:\n\t{instance}\n\tOutput object:\n\t{roundtripped}"
            )
        except Exception as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_01_how_to_define_and_roundtrip_a_pydantic_object_with_no_config:-\n{pretty_error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_01_how_to_define_and_roundtrip_a_pydantic_object_with_no_config:\n {pretty_error_message(e)}\n"
            )

    def test_02_how_to_define_and_roundtrip_a_pydantic_object_with_serialisation_config(self):
        """
        This test case demonstrates how to define and instantiate a sophisticated Pydantic model.
        Tests JghSerialisation.serialise and JghSerialisation.validate.

        The TestModel class showcases various Pydantic features including:
        - Model configuration using a ConfigDict with alias_generator for handling aliases during serialization and validation.
        - Type annotations with the union operator (|) to allow attributes to accept multiple types, making them optional if None is included.
        - Field defaults using the Field class with a factory method (default_factory) for value types like lists, ensuring a new instance is created for each model instance.

        The test verifies:
        - Successful instantiation of the TestModel class.
        - Serialization of the model instance to a JSON string using JghSerialization.serialise.
        - Validation and deserialization of the JSON string back to a TestModel instance using JghSerialization.validate.
        - Roundtrip success by asserting that the deserialized object is an instance of TestModel and matches the original instance.

        If any assertion fails, the test logs an error message and fails.
        """

        class TestModel(pydantic.BaseModel):
            """
            This Pydantic model demonstrates various features including model configuration, type annotations, and field defaults.

            Pydantic Features:
            - model_config:
                Configures the model using a ConfigDict, which includes an alias_generator for handling aliases during serialization and validation.
            - Union Type Annotations:
                The union operator (|) allows attributes to accept multiple types, making them optional if None is included.
            - Field with Factory Method:
                For value types like lists, a factory method (default_factory) is used to set the default value, ensuring a new instance is created for each model instance.

            Note:
            - AliasChoices is a Pydantic class that allows for multiple aliases for a field. If the attribute name is not among the AliasChoices, the default value will be imposed during instantiation.
            - When using alias together with validation_alias or serialization_alias, validation_alias takes priority for validation, and serialization_alias takes priority for dumping JSON.
            """
            model_config = groovy_configdict 

            id: int | None = 0 #NB # The union operator means the attribute value doesn't have to be sent or received as a field in the JSON string.
            first: str | None = default_john
            middle_names: list[str] | None = Field(default_factory=list[str]) #NB. must use a factory for objects, a class or function is passed to the factory and not a instance of such, notice we are not specifying a default here. just to experiment 
            last: str | None = default_jones
            isactive: bool | None = default_false
            age: int | None = default_99
            email: str | None = default_email
            street: str | None = default_eglinton

        try:
            instance = TestModel()
            json_str = JghSerialization.serialise(instance)
            logger.info(f"\nJSON STRING:\n\t{json_str}")
            roundtripped = JghSerialization.validate(json_str, TestModel)
            self.assertIsInstance(roundtripped, TestModel)
            self.assertEqual(roundtripped.id, instance.id)
            self.assertEqual(roundtripped.first, instance.first)
            self.assertEqual(roundtripped.middle_names, instance.middle_names)
            self.assertEqual(roundtripped.last, instance.last)
            self.assertEqual(roundtripped.isactive, instance.isactive)
            self.assertEqual(roundtripped.age, instance.age)
            self.assertEqual(roundtripped.email, instance.email)
            self.assertEqual(roundtripped.street, instance.street)
            logger.info(
                f"TEST OUTCOME: PASS:\n\tRoundtrip succeeded.\nInput object:\n\t{instance}\n\tOutput object:\n\t{roundtripped}"
            )
        except Exception as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_01how_to_define_and_roundtrip_a_pydantic_object_with_serialisation_config:-\n{pretty_error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_01how_to_define_and_roundtrip_a_pydantic_object_with_serialisation_config:\n {pretty_error_message(e)}\n"
            )

    def test_03_import_json_with_missing_fields_for_a_pydantic_model(self):
        """
        Test to illustrate that a pydantic model attribute corresponding to a JSON field 
        that is missing will be correctly assigned its default value
        by JghSerialization.validate().
        """
        class TestModel(pydantic.BaseModel):
            model_config = groovy_configdict
            age: int = 99
            email: str = default_email

        try:
            missing_fields_json = '{"age": 16}' # Missing email field
            logger.info(f"JSON STRING:\n\t{missing_fields_json}")
            obj = JghSerialization.validate(missing_fields_json, TestModel)
            self.assertIsInstance(obj, TestModel)
            self.assertEqual(obj.age, 16)  # the crunch
            self.assertEqual(obj.email, default_email)  # the crunch
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with missing field succeeded.\n\tInput string:\n\t{missing_fields_json}\n\tOutput object:\n\t{obj}"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_03_import_json_with_missing_fields_for_a_pydantic_model:-\n{pretty_error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_03_import_json_with_missing_fields_for_a_pydantic_model:\n{pretty_error_message(e)}\n"
            )

    def test_04_import_json_with_superfluous_fields_for_a_pydantic_model(self):
        """
        Test to illustrate that superfluous fields in a JSON string will happily ignored
        when a pydantic model is deserialised using JghSerialization.validate().
        """

        class TestModel(pydantic.BaseModel):
            model_config = groovy_configdict 
            age: int

        try:
            extra_fields_json = f'{{"age": 27, "extra_field": "extra_value", "another_extra_field": "another_extra_value"}}' # Extra fields
            logger.info(f"JSON STRING:\n\t{extra_fields_json}")
            obj = JghSerialization.validate(extra_fields_json, TestModel)
            self.assertIsInstance(obj, TestModel)
            self.assertEqual(obj.age, 27)
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with extra field succeeded.\n\tInput string:\n\t{extra_fields_json}\n\tOutput object:\n\t{obj}"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_04_import_json_with_superfluous_fields_for_a_pydantic_model:-\n{pretty_error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_04_import_json_with_superfluous_fields_for_a_pydantic_model:\n{pretty_error_message(e)}\n"
            )

    def test_05_import_json_with_invalid_attribute_types_in_the_json(self):
        """
        Test to illustrate that JghSerialization.validate will raise a ValueError
        if JSON field is an invalid type for the attribute.
        """

        class TestModel(pydantic.BaseModel):
            model_config = groovy_configdict 
            id: int
            first: str | None = None

        # Invalid JSON string
        json_with_invalid_types = f'{{"id": "one", "first": 10}}'
        logger.info(f"JSON STRING:\n\t{json_with_invalid_types}")
        try:
            JghSerialization.validate(json_with_invalid_types, TestModel)
        except ValueError as e:
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with JSON containing invalid attribute types correctly raised a ValueError.\nError message:\n\t{pretty_error_message(e)}"
            )
            self.assertTrue(True)
        else:
            self.fail(
                f"ERROR OCCURRED:\n\t'test_05_import_json_with_invalid_attribute_types_in_the_json' ValueError not raised"
            )

    def test_06_import_json_with_fatally_badly_formatted_json(self):
        """
        Test to illustrate that JghSerialization.validate will raise a ValueError
        if JSON is garbage.
        """

        class TestModel(pydantic.BaseModel):
            model_config = groovy_configdict 
            first: str | None = None

        # Invalid JSON string
        rubbish_json = f'{{":rubbish:::}}'
        logger.info(f"JSON STRING:\n\t{rubbish_json}")

        try:
            JghSerialization.validate(rubbish_json, TestModel)
        except ValueError as e:
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with badly formatted JSON correctly raised a ValueError.\nError message:\n\t{pretty_error_message(e)}"
            )
            self.assertTrue(True)
        else:
            self.fail(
                f"ERROR OCCURRED:\n\t'test_06_import_json_with_fatally_badly_formatted_json' ValueError not raised"
            )

    def test_07_import_json_with_empty_json(self):
        """
        Test to illustrate that JghSerialization.validate with empty and therefore invalid JSON will raise a ValueError.
        """

        class TestModel(pydantic.BaseModel):
            model_config = groovy_configdict 
            id: int = 0

        # Empty JSON string
        empty_json = ""
        try:
            JghSerialization.validate(empty_json, TestModel)
        except ValueError as e:
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with empty and therefore invalid JSON correctly raised a ValueError.\nError message:\n\t{pretty_error_message(e)}"
            )
            self.assertTrue(True)
        else:
            self.fail(f"TEST OUTCOME FAIL:\n\tValueError not raised")

    def test_08_import_json_with_int_and_bool_mistakenly_represented_as_strings(self):
        """
        This test will illustrate how JghSerialization.validate reacts where 
        integer and boolean values are represented as strings in the JSON
        for a pydantic model. It will ensure that Pydantic can successfully coerce these fields to
        the correct types.
        """

        class TestModel(pydantic.BaseModel):
            model_config = groovy_configdict 
            isactive: bool | None = False
            age: int | None = 68

        try:
            # Define a JSON string with integer and boolean values represented as strings
            json_with_strings = """
            {
                "isactive": "true",
                "age": "32"
            }
            """
            logger.info(f"JSON STRING:\n\t{json_with_strings}")
            obj = JghSerialization.validate(json_with_strings, TestModel)
            self.assertIsInstance(obj, TestModel)
            self.assertTrue(obj.isactive)  # Coerced to boolean
            self.assertEqual(obj.age, 32)  # Coerced to integer
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with integer and boolean values represented as strings succeeded.\n\tInput string:\n\t{json_with_strings}\n\tOutput object:\n\t{obj}"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_08_import_json_with_int_and_bool_mistakenly_represented_as_strings:-\n{pretty_error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_08_import_json_with_int_and_bool_mistakenly_represented_as_strings:\n{pretty_error_message(e)}\n"
            )

    def test_09_import_json_using_before_and_after_validators(self):
        """
        This test will illustrate how to use before and after validators to coerce
        JSON string values to the correct types during deserialization.
        """
        def any_to_bool(value : Any) -> bool:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                if value.lower() in ['true', "yes", '1']:
                    return True
                if value.lower() in ['false', 'no', '0']:
                    return False
            if isinstance(value, int):
                if value > 0:
                    return True
            if isinstance(value, float):
                if value > 0:
                    return True
            return False

        def any_to_integer(value : Any) -> int:
            if isinstance(value, int):
                return value;
            if isinstance(value, float):
                return int(value)
            if isinstance(value, str) and value.isnumeric():
                return int(value)
            if isinstance(value, bool):
                return 1 if value else 0
            return 0

        def min_is_zero(value : int) -> int:
            if value < 0:
                value = 0
            return value

        class TestModel(pydantic.BaseModel):
            model_config = groovy_configdict 
            isactive: Annotated[bool, BeforeValidator(any_to_bool)] | None = False
            age: Annotated[int, BeforeValidator(any_to_integer), AfterValidator(min_is_zero)] | None = 68

        try:
            # Define a JSON string with integer and boolean values mistakenly arriving as strings
            json_with_strings = """
            {
                "isactive": "true",
                "age": "32"
            }
            """
            logger.info(f"JSON STRING:\n\t{json_with_strings}")
            obj = JghSerialization.validate(json_with_strings, TestModel)
            self.assertIsInstance(obj, TestModel)
            self.assertTrue(obj.isactive)  # string to boolean
            self.assertEqual(obj.age, 32)  # string to integer
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with integer and boolean values represented as strings succeeded.\n\tInput string:\n\t{json_with_strings}\n\tOutput object:\n\t{obj}"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_09_import_json_using_before_and_after_validators:-\n{pretty_error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_09_import_json_using_before_and_after_validators:\n{pretty_error_message(e)}\n"
            )

    def test_10_import_json_using_before_and_after_validators(self):
        """
        This test will illustrate how to use before and after validators to coerce
        JSON string values to the correct types during deserialization.
        """
        def any_to_bool(value : Any) -> bool:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                if value.lower() in ['true', "yes", '1']:
                    return True
                if value.lower() in ['false', 'no', '0']:
                    return False
            if isinstance(value, int):
                if value > 0:
                    return True
            if isinstance(value, float):
                if value > 0:
                    return True
            return False

        def any_to_integer(value : Any) -> int:
            if isinstance(value, int):
                return value;
            if isinstance(value, float):
                return int(value)
            if isinstance(value, str) and value.isnumeric():
                return int(value)
            if isinstance(value, bool):
                return 1 if value else 0
            return 0

        def min_is_zero(value : int) -> int:
            if value < 0:
                value = 0
            return value

        class TestModel(pydantic.BaseModel):
            model_config = groovy_configdict 
            isactive: Annotated[bool, BeforeValidator(any_to_bool)] | None = False
            age: Annotated[int, BeforeValidator(any_to_integer), AfterValidator(min_is_zero)] | None = 68

        try:
            # Define a JSON string with integer and boolean values mistakenly arriving as strings
            json_with_strings = """
            {
                "isactive": 1,
                "age": "-32"
            }
            """
            logger.info(f"JSON STRING:\n\t{json_with_strings}")
            obj = JghSerialization.validate(json_with_strings, TestModel)
            self.assertIsInstance(obj, TestModel)
            self.assertTrue(obj.isactive)  # string to boolean
            self.assertEqual(obj.age, 0)  # string to integer
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with integer and boolean values represented as strings succeeded.\n\tInput string:\n\t{json_with_strings}\n\tOutput object:\n\t{obj}"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_09_import_json_using_before_and_after_validators:-\n{pretty_error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_09_import_json_using_before_and_after_validators:\n{pretty_error_message(e)}\n"
            )


# Do the tests (but not if this script is imported as a module)
if __name__ == "__main__":
    print("sys.path (in alphabetical order):-")
    for path in sorted(sys.path):
        print(f" - {path}")
    print(
        "\nExplanation:\n\tThe above paths are where Python will look to find modules and imports\n\treferenced in this file. If imports fail to resolve, it is because of\n\tincorrect paths. In a Visual Studio 2022 project, right-click\n\tthe 'Search Paths' node to add a path."
    )

    unittest.main()
