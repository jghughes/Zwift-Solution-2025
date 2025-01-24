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
from pydantic import Field, AliasChoices
from typing import Optional

# Local application imports
from jgh_serialization import JghSerialization

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Define aliases for the tests
isactiveALIAS = "isactive_alias"
ageSERIALIZATION_ALIAS = "age_serialization_alias"
emailSERIALIZATION_ALIAS = "email_serialization_alias"
streetSERIALIZATION_ALIAS = "street_serialization_alias"

# Define default values for the model attributes
isactiveDEFAULTisfalse: bool = False
ageDEFAULTis32 = 32
emailDEFAULT = "default.com"
streetDEFAULT = "Default St"


# Helper function to write a pretty error message
def error_message(ex: Exception) -> str:
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


# Define a Pydantic model for testing pyndatic's validation and serialisation. change the signature to @dataclass for testing dataclasses
class TestModel(pydantic.BaseModel):
    """
    id: int                 required in ctor because no default is specified. Can be roundtripped.
    first: Optional[str]    not required because a default is specified (None). Can be roundtripped.
    last: str               required
    isactive: bool          not required. Uses an alias for import/export. Can be roundtripped.
    age: int                not required. Uses serialization_alias for export. Missing Validation_alias. Cannot be roundtripped.
    email: str              not required. Uses serialization_alias for export. Inadequate AliasChoices: not mutually inclusive. Cannot be roundtripped.
    street: str             not required. Uses serialization_alias for export. AliasChoices are not mutually inclusive. Can be roundtripped

    N.B. AliasChoices is a Pydantic class that allows for multiple aliases for a field.
    Beware, if the name of the attribute - 'email' - is not among the AliasChoices, instantiation of TestModel in code will
    ignore whatever you think you have assigned in the ctor and will impose the default.

    In case you use alias together with validation_alias or serialization_alias at the same time, the
    validation_alias will have priority over alias for validation, and serialization_alias will have
    priority over alias for dumping JSON.
    """

    id: int
    first: Optional[str] = None
    last: str = Field()
    isactive: bool = Field(default=isactiveDEFAULTisfalse, alias=isactiveALIAS)
    age: int = Field(default=ageDEFAULTis32, serialization_alias=ageSERIALIZATION_ALIAS)
    email: str = Field(
        default=emailDEFAULT,
        serialization_alias=emailSERIALIZATION_ALIAS,
        validation_alias=AliasChoices("Email", "EMAIL"),
    )
    street: str = Field(
        default=streetDEFAULT,
        serialization_alias=streetSERIALIZATION_ALIAS,
        validation_alias=AliasChoices(
            "street", streetSERIALIZATION_ALIAS, "dummystreetfieldname"
        ),
    )


# All the tests
class Test_JghSerialization(unittest.TestCase):

    def setUp(self):
        logger.info(f"\nTEST NAME: {self._testMethodName}")
        logger.info(f"-" * 100)
        # Print the docstring of the test method
        test_method = getattr(self, self._testMethodName)
        if test_method.__doc__:
            logger.info(f"TEST DOCSTRING:\n\t{test_method.__doc__.strip()}")
            logger.info(f"-" * 100)

    def tearDown(self):
        logger.info(f"-" * 100)
        logger.info(f"TEST FINISHED: {self._testMethodName}")
        logger.info(f"=" * 100)
        logger.info(f"\n")

    def test_to_instantiate_TestModel_multiple_ways(self):
        """
        This test case demonstrates multiple ways to instantiate TestModel in code using a ctor,
        and the pitfalls entailed. It highlights the unexpected side effects that different
        pydantic Field attributes have on the success or failure of a ctor.

        1. if an alias is specified for an attribute, the alias hides the code-name recognised
           in the ctor. Very confusing!
        2. if a serialisation_alias and/or validation_alias is specified, the code-name is
           recognised in the ctor.

        BUT:
        3. if a validation_alias is unthinkingly specified, an assignment of a value to the attribute
           in the ctor will fail. The assignment will be ignored and the default value will prevail.
           To fix this, the list of AliasChoices must include the attribute name.
        """

        errors: list[str] = []

        try:
            dummy = TestModel(id=1, first=None, last="Trump")
            self.assertIsInstance(dummy, TestModel)
            logger.info(
                f"TEST OUTCOME: PASS:\n\tTestModel instantiated successfully with first=None and last={dummy.last}."
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_to_instantiate_TestModel_multiple_ways (Trump):\n\n{error_message(e)}"
            )
            errors.append(f"Trump: error_message(e)")

        try:
            dummy = TestModel(id=1, first="Bill", last="Clinton")
            self.assertIsInstance(dummy, TestModel)
            logger.info(
                f"TEST OUTCOME: PASS:\n\tTestModel instantiated successfully with first={dummy.first} and last={dummy.last}."
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_to_instantiate_TestModel_multiple_ways (Clinton):\n\n{error_message(e)}"
            )
            errors.append(f"Clinton: error_message(e)")

        try:
            dummy = TestModel(
                id=1,
                first="Barak",
                last="Obama",
                isactive_alias=not isactiveDEFAULTisfalse,
                age=17,
            )
            self.assertIsInstance(dummy, TestModel)
            self.assertTrue(dummy.isactive != isactiveDEFAULTisfalse)
            self.assertTrue(dummy.age == 17)
            logger.info(
                f"TEST OUTCOME: PASS:\n\tTestModel instantiated successfully. But note that ctor syntax uses the str value of the alias as the name of the attribute!!!!!!!!!!!"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_to_instantiate_TestModel_multiple_ways (Obama):\n\n{error_message(e)}"
            )
            errors.append(f"Obama: error_message(e)")

        try:
            dummy = TestModel(id=1, first="George", last="Bush", age=93)
            self.assertIsInstance(dummy, TestModel)
            self.assertTrue(dummy.age == 93)
            logger.info(
                f"TEST OUTCOME: PASS:\n\tTestModel instantiated successfully with age={dummy.age}. Note that ctor syntax does not use the str value of the serialisation_alias as the name of the attribute"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_to_instantiate_TestModel_multiple_ways (Bush):\n\n{error_message(e)}"
            )
            errors.append(f"Bush: error_message(e)")

        try:
            dummy = TestModel(id=1, last="Thatcher", street="10 Downing St")
            self.assertIsInstance(dummy, TestModel)
            self.assertTrue(dummy.street == "10 Downing St")
            logger.info(
                f"TEST OUTCOME: PASS:\n\tTestModel instantiated successfully with street={dummy.street}"
            )
            logger.info(
                f"\tThis test was designed to illustrate the impact of validation_alias on instantiation.\n\tWe assigned '10 Downing St' to the street attribute in the ctor. This succeeded only because AliasChoices('street', streetSERIALIZATION_ALIAS, dummystreetfieldname') included the attribute's actual name 'street'."
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_to_instantiate_TestModel_multiple_ways (Thatcher):\n\n{error_message(e)}"
            )
            errors.append(f"Thatcher: error_message(e)")

        try:
            dummy = TestModel(id=1, last="Thatcher", email="maggie@rubbish.com")
            self.assertIsInstance(dummy, TestModel)
            self.assertTrue(dummy.email == emailDEFAULT)
            logger.info(
                f"TEST OUTCOME: PASS:\n\tTestModel instantiated successfully with email={emailDEFAULT}"
            )
            logger.info(
                f"\tThis test was designed to illustrate the impact of validation_alias on instantiation.\n\tWe assigned 'maggie@rubbish.com' to the email attribute in the ctor, but this was correctly ignored because AliasChoices('Email', 'EMAIL') failed to include the attribute's actual name 'email'. Accordingly, the specified default value was imposed. Had the actual attribute name been included, the value initialised in the ctor would have prevailed."
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_to_instantiate_TestModel_multiple_ways (Thatcher):\n\n{error_message(e)}"
            )
            errors.append(f"Thatcher: error_message(e)")

        if errors:
            self.fail(
                f"ERRORS OCCURRED: test_to_instantiate_TestModel_multiple_ways:\n"
                + "\n".join(errors)
            )

    def test_to_json_from_object(self):
        """
        This test case creates an instance of TestModel, serializes it to JSON using
        JghSerialization.to_json_from_object, and asserts that the JSON string contains
        the expected fields and values.

        Illustrates the bizarre usage of alias string as the code-name of an attribute in the ctor syntax.

        Illustrates the usage of alias and serialization_alias to the field names in the emitted JSON string.
        """
        try:
            instance = TestModel(
                id=1, last="Clinton", isactive_alias=True, age=84
            )  # note the use of the alias name in ctor syntax, but not serialization_alias
            json_str = JghSerialization.to_json_from_object(instance)
            logger.info(f"\nJSON STRING:\n\t{json_str}")
            self.assertIsInstance(json_str, str)
            self.assertIn('"id": 1', json_str)
            self.assertIn('"last": "Clinton"', json_str)
            self.assertIn(f'"{isactiveALIAS}": true', json_str)  # the crunch
            self.assertIn(f'"{ageSERIALIZATION_ALIAS}": 84', json_str)  # the crunch
            logger.info(
                f"TEST OUTCOME: PASS:\n\tSerialization succeeded.\nInput object:\n\t{instance}\n\tOutput string:\n\t{json_str}"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_to_json_from_object:-\n\n{error_message(e)}"
            )
            self.fail(f"ERROR OCCURRED: test_to_json_from_object:\nerror_message(e)\n")

    def test_ingest_json_featuring_alias(self):
        """
        This test case deserializes a valid JSON string to an instance of TestModel using
        JghSerialization.to_object_from_json, and asserts that the resulting object has
        the expected attribute values. Note how we (must be sure to) use the aliases in the JSON string
        to be consistent with the aliases we are using for some of our model attributes.

        Illustrates that validation succeeds if an incoming JSON field name is identical
        to an attribute's given alias, in this case for 'is_active'.
        """
        try:
            valid_json = f'{{"id": 1, "last": "Clinton", "{isactiveALIAS}": true}}'
            logger.info(f"JSON STRING:\n\t{valid_json}")
            obj = JghSerialization.to_object_from_json(valid_json, TestModel)
            self.assertIsInstance(obj, TestModel)
            self.assertEqual(obj.id, 1)
            self.assertEqual(obj.last, "Clinton")
            self.assertEqual(obj.isactive, True)  # the crunch
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization succeeded.\n\tInput string:\n\t{valid_json}\n\tOutput object:\n\t{obj}"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_to_object_from_valid_json:-\n{error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_ingest_json_featuring_alias:\nerror_message(e)\n"
            )

    def test_ingest_json_featuring_serialisation_alias(self):
        """
        This test case deserializes a valid JSON string to an instance of TestModel using
        JghSerialization.to_object_from_json, and asserts that the resulting object has
        the expected attribute values. Note how we (must be sure to) use the aliases in the JSON string
        to be consistent with the aliases we are using for some of our model attributes.

        Illustrates that a field in incoming JSON cannot be correctly interpreted unless
        it has a matching alias, or -  when list of validation AliasChoices is specified -
        a matching counterpart on the list. This example simultaneously proves that
        a serialisation_alias doesn't cut it; it is inconsequential for interpreting the JSON.

        An un-interpreted field is ignored. It is assigned its default value by Pydantic.
        In this case 'age'.
        """
        try:
            valid_json = (
                f'{{"id": 1, "last": "Clinton", "{ageSERIALIZATION_ALIAS}": 99}}'
            )
            logger.info(f"JSON STRING:\n\t{valid_json}")
            obj = JghSerialization.to_object_from_json(valid_json, TestModel)
            self.assertIsInstance(obj, TestModel)
            self.assertEqual(obj.id, 1)
            self.assertEqual(obj.last, "Clinton")
            self.assertEqual(obj.age, ageDEFAULTis32)  # the crunch
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization succeeded.\n\tInput string:\n\t{valid_json}\n\tOutput object:\n\t{obj}"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_to_object_from_valid_json:-\n{error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_ingest_json_featuring_serialisation_alias:\nerror_message(e)\n"
            )

    def test_ingest_json_featuring_serialisation_alias_and_validationchoice(self):
        """
        This test case deserializes a valid JSON string to an instance of TestModel using
        JghSerialization.to_object_from_json, and asserts that the resulting object has
        the expected attribute values. Note how we (must be sure to) use the aliases in the JSON string
        to be consistent with the aliases we are using for some of our model attributes.

        Illustrates that a field in incoming JSON can be correctly interpreted as long as
        the associated attribute has a list of validation_alias choices
        that include the name of both the attribute and the incoming field-name.
        In this case 'street' and 'dummystreetfieldname'.
        """
        try:
            valid_json = (
                f'{{"id": 1, "last": "Clinton", "dummystreetfieldname": "Rubbish St"}}'
            )
            logger.info(f"JSON STRING:\n\t{valid_json}")
            obj = JghSerialization.to_object_from_json(valid_json, TestModel)
            self.assertIsInstance(obj, TestModel)
            self.assertEqual(obj.id, 1)
            self.assertEqual(obj.last, "Clinton")
            self.assertEqual(obj.street, "Rubbish St")  # the crunch
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization succeeded.\n\tInput string:\n\t{valid_json}\n\tOutput object:\n\t{obj}"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_to_object_from_valid_json:-\n{error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_ingest_json_featuring_serialisation_alias_and_validationchoice:\nerror_message(e)\n"
            )

    def test_roundtrip_object_featuring_alias(self):
        """
        This test case demonstrates a roundtrip from object to JSON and back to object.
        It creates an instance of TestModel, serializes it to JSON using JghSerialization.to_json_from_object,
        deserializes the JSON back to an instance of TestModel using JghSerialization.to_object_from_json,
        and asserts that the resulting object has the expected attribute values.

        Illustrates that a field with an alias will successfully round-trip i.e. the alias is emitted
        in the JSON, and recognised in incoming JSON
        """
        try:
            instance = TestModel(id=1, last="Clinton", isactive_alias=True)
            json_str = JghSerialization.to_json_from_object(instance)
            logger.info(f"\nJSON STRING:\n\t{json_str}")
            roundtripped = JghSerialization.to_object_from_json(json_str, TestModel)
            self.assertIsInstance(roundtripped, TestModel)
            self.assertEqual(roundtripped.id, 1)
            self.assertEqual(roundtripped.last, "Clinton")
            self.assertEqual(roundtripped.isactive, True)  # the crunch
            logger.info(
                f"TEST OUTCOME: PASS:\n\tRoundtrip succeeded.\nInput object:\n\t{instance}\n\tOutput object:\n\t{roundtripped}"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in roundtrip_object_to_json_and_back_again:-\n{error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_roundtrip_object_featuring_alias:\nerror_message(e)\n"
            )

    def test_roundtrip_object_featuring_serialisation_alias_and_missing_validation_alias(
        self,
    ):
        """
        This test case demonstrates a roundtrip from object to JSON and back to object.
        It creates an instance of TestModel, serializes it to JSON using JghSerialization.to_json_from_object,
        deserializes the JSON back to an instance of TestModel using JghSerialization.to_object_from_json,
        and asserts that the resulting object has the expected attribute values.

        Illustrates that an attribute with a serialisation_alias will fail to correctly roundtrip by itself.
        The attribute needs to have a matching AliasChoice to round-trip correctly. Failing that
        field will be treated as missing and the attribute will end up with its default.
        """
        try:
            instance = TestModel(id=1, last="Clinton", age=84)
            json_str = JghSerialization.to_json_from_object(instance)
            logger.info(f"\nJSON STRING:\n\t{json_str}")
            roundtripped = JghSerialization.to_object_from_json(json_str, TestModel)
            self.assertIsInstance(roundtripped, TestModel)
            self.assertEqual(roundtripped.id, 1)
            self.assertEqual(roundtripped.last, "Clinton")
            self.assertEqual(roundtripped.age, 84)  # the crunch - this will fail
            logger.error(
                f"TEST OUTCOME: FAIL:\n\tRoundtrip succeeded in 'test_roundtrip_object_featuring_serialisation_alias_and_missing_validation_alias'. It should not have.\nInput object:\n\t{instance}\n\tOutput object:\n\t{roundtripped}"
            )
            self.fail(
                f"ERROR OCCURRED:\n\tRoundtrip succeeded in'test_roundtrip_object_featuring_serialisation_alias_and_missing_validation_alias'. It should not have.\nInput object:\n\t{instance}\n\tOutput object:\n\t{roundtripped}"
            )
        except AssertionError as e:
            logger.info(
                f"TEST OUTCOME PASS:\n\tAn assertion correctly failed in test_roundtrip_object_featuring_serialisation_alias_and_missing_validation_alias:-\n{error_message(e)}"
            )

    def test_roundtrip_object_featuring_serialisation_alias_and_inadequate_validation_alias(
        self,
    ):
        """
        This test case demonstrates a roundtrip from object to JSON and back to object.
        It creates an instance of TestModel, serializes it to JSON using JghSerialization.to_json_from_object,
        deserializes the JSON back to an instance of TestModel using JghSerialization.to_object_from_json,
        and asserts that the resulting object has the expected attribute values.

        Illustrates that an attribute with a serialisation_alias will fail to correctly roundtrip by itself.
        The attribute needs to have a matching AliasChoice to round-trip correctly. Failing that
        field will be treated as missing and the attribute will end up with its default.
        """
        try:
            instance = TestModel(id=1, last="Clinton", email="maggie@london.com")
            json_str = JghSerialization.to_json_from_object(instance)
            logger.info(f"\nJSON STRING:\n\t{json_str}")
            roundtripped = JghSerialization.to_object_from_json(json_str, TestModel)
            self.assertIsInstance(roundtripped, TestModel)
            self.assertEqual(roundtripped.id, 1)
            self.assertEqual(roundtripped.last, "Clinton")
            self.assertEqual(
                roundtripped.email, "maggie@london.com"
            )  # the crunch - this will fail
            logger.error(
                f"TEST OUTCOME: FAIL:\n\tRoundtrip succeeded in 'roundtrip_object_to_json_and_back_again'. It should not have.\nInput object:\n\t{instance}\n\tOutput object:\n\t{roundtripped}"
            )
            self.fail(
                f"ERROR OCCURRED:\n\tRoundtrip succeeded in 'roundtrip_object_to_json_and_back_again'. It should not have.\nInput object:\n\t{instance}\n\tOutput object:\n\t{roundtripped}"
            )
        except AssertionError as e:
            logger.info(
                f"TEST OUTCOME PASS:\n\tAn assertion correctly failed in roundtrip_object_to_json_and_back_again:-\n{error_message(e)}"
            )

    def test_roundtrip_object_featuring_serialisation_alias_and_matching_validation_alias(
        self,
    ):
        """
        This test case demonstrates a roundtrip from object to JSON and back to object.
        It creates an instance of TestModel, serializes it to JSON using JghSerialization.to_json_from_object,
        deserializes the JSON back to an instance of TestModel using JghSerialization.to_object_from_json,
        and asserts that the resulting object has the expected attribute values.

        Illustrates that an attribute with a serialisation_alias will correctly roundtrip as long as
        it has a matching AliasChoice. Failing that the attribute will end up with its default.
        """
        try:
            instance = TestModel(
                id=1, last="Clinton", email="maggie@london.com", street="Dundas St"
            )
            json_str = JghSerialization.to_json_from_object(instance)
            logger.info(f"\nJSON STRING:\n\t{json_str}")
            roundtripped = JghSerialization.to_object_from_json(json_str, TestModel)
            self.assertIsInstance(roundtripped, TestModel)
            self.assertEqual(roundtripped.id, 1)
            self.assertEqual(roundtripped.last, "Clinton")
            self.assertEqual(roundtripped.street, "Dundas St")  # the crunch
            logger.info(
                f"TEST OUTCOME: PASS:\n\tRoundtrip succeeded.\nInput object:\n\t{instance}\n\tOutput object:\n\t{roundtripped}"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in 'test_roundtrip_object_featuring_serialisation_alias_and_matching_validation_alias':-\n{error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_roundtrip_object_featuring_serialisation_alias_and_matching_validation_alias:\nerror_message(e)\n"
            )

    def test_json_with_null_value(self):
        """
        Test to illustrate that a JSON field with a null value will be correctly interpreted as None.
        """
        try:
            json_with_null_value = f'{{"id": 1, "first": null,  "last": "Clinton"}}'
            logger.info(f"JSON STRING:\n\t{json_with_null_value}")
            obj = JghSerialization.to_object_from_json(json_with_null_value, TestModel)
            self.assertIsInstance(obj, TestModel)
            self.assertEqual(obj.id, 1)
            self.assertIsNone(obj.first)
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with null value succeeded.\n\tInput string:\n\t{json_with_null_value}\n\tOutput object:\n\t{obj}"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_json_with_null_value:-\n{error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_json_with_null_value:\nerror_message(e)\n"
            )

    def test_json_with_missing_fields(self):
        """
        Test to illustrate that a JSON field that is missing will be correctly assigned the default value.
        """
        try:
            missing_fields_json = '{"id": 1, "last": "Clinton"}'
            logger.info(f"JSON STRING:\n\t{missing_fields_json}")
            obj = JghSerialization.to_object_from_json(missing_fields_json, TestModel)
            self.assertIsInstance(obj, TestModel)
            self.assertEqual(obj.id, 1)
            self.assertIsNone(obj.first)
            self.assertEqual(obj.last, "Clinton")
            self.assertEqual(obj.isactive, isactiveDEFAULTisfalse)  # the crunch
            self.assertEqual(obj.age, ageDEFAULTis32)  # the crunch
            self.assertEqual(obj.email, emailDEFAULT)  # the crunch
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with missing field succeeded.\n\tInput string:\n\t{missing_fields_json}\n\tOutput object:\n\t{obj}"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_json_with_missing_fields:-\n{error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_json_with_missing_fields:\nerror_message(e)\n"
            )

    def test_json_with_extra_fields(self):
        """
        Test to illustrate that a JSON field with extra fields will be correctly interpreted.
        """
        try:
            # JSON string with extra superfluous fields
            extra_fields_json = f'{{"id": 1, "last": "Clinton", "extra_field": "extra_value", "another_extra_field": "another_extra_value"}}'
            logger.info(f"JSON STRING:\n\t{extra_fields_json}")
            obj = JghSerialization.to_object_from_json(extra_fields_json, TestModel)
            self.assertIsInstance(obj, TestModel)
            self.assertEqual(obj.id, 1)
            self.assertEqual(obj.last, "Clinton")
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with extra field succeeded.\n\tInput string:\n\t{extra_fields_json}\n\tOutput object:\n\t{obj}"
            )
        except AssertionError as e:
            logger.error(
                f"TEST OUTCOME FAIL:\n\tAn assertion failed in test_json_with_extra_fields:-\n{error_message(e)}"
            )
            self.fail(
                f"ERROR OCCURRED: test_json_with_extra_fields:\nerror_message(e)\n"
            )

    def test_json_with_invalid_attribute_types_in_the_json(self):
        """
        Test to illustrate that a JSON field with an invalid attribute type will raise a ValueError.
        """
        # Invalid JSON string
        json_with_invalid_types = f'{{"id": "one", "first": 10}}'
        logger.info(f"JSON STRING:\n\t{json_with_invalid_types}")
        try:
            JghSerialization.to_object_from_json(json_with_invalid_types, TestModel)
        except ValueError as e:
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with JSON containing invalid attribute types correctly raised a ValueError.\nError message:\n\t{error_message(e)}"
            )
            self.assertTrue(True)
        else:
            self.fail(
                f"ERROR OCCURRED:\n\t'test_json_with_invalid_attribute_types_in_the_json' ValueError not raised"
            )

    def test_json_with_badly_formatted_json(self):
        """
        This test case attempts to deserialize a JSON string that is badly formatted and contains garbage
        using JghSerialization.to_object_from_json, and asserts that a ValueError is raised.
        """
        # Invalid JSON string
        rubbish_json = f'{{"id"::::}}'
        logger.info(f"JSON STRING:\n\t{rubbish_json}")

        try:
            JghSerialization.to_object_from_json(rubbish_json, TestModel)
        except ValueError as e:
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with badly formatted JSON correctly raised a ValueError.\nError message:\n\t{error_message(e)}"
            )
            self.assertTrue(True)
        else:
            self.fail(
                f"ERROR OCCURRED:\n\t'test_json_with_badly_formatted_json' ValueError not raised"
            )

    def test_json_with_empty_json(self):
        """
        Test to illustrate that deserialization with empty and therefore invalid JSON will raise a ValueError.
        """
        # Empty JSON string
        empty_json = ""
        try:
            JghSerialization.to_object_from_json(empty_json, TestModel)
        except ValueError as e:
            logger.info(
                f"TEST OUTCOME: PASS:\n\tDeserialization with empty and therefore invalid JSON correctly raised a ValueError.\nError message:\n\t{error_message(e)}"
            )
            self.assertTrue(True)
        else:
            self.fail(f"TEST OUTCOME FAIL:\n\tValueError not raised")


# Do the tests (but not if this script is imported as a module)
if __name__ == "__main__":
    print("sys.path (in alphabetical order):-")
    for path in sorted(sys.path):
        print(f" - {path}")
    print(
        "\nExplanation:\n\tThe above paths are where Python will look to find modules and imports\n\treferenced in this file. If imports fail to resolve, it is because of\n\tincorrect paths. In a Visual Studio 2022 project, right-click\n\tthe 'Search Paths' node to add a path."
    )

    unittest.main()
