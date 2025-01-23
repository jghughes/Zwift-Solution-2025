# install ruff on your machine if you haven't already. pip install ruff 
# ruff is for using in the terminal. 
# type 'ruff -h' for help. 
# type ruff check {filename} to check the file for errors
# type ruff fix {filename} to fix the file errors
# type ruff format {filename} to format the file beautifully
import sys 
import json


from ClubMemberClass import ClubMemberItem

print("Welcome. This is a demonstration of how to use the ClubMemberItem class in your code. The class stores a ClubMemberItem's key admin data. It is not intended to store any other data, such as power data, performance data, or event data. It is intended for use in a ClubMembershipRepository.")

# Create an instance of the ClubMemberItem class for a member (joe) by inserting sample data into the constructor when instantiating the class. This is the most common way to create a ClubMemberItem instance.
joe = ClubMemberItem(
    zwift_id=3147366,
    zwift_firstname="joe",
    zwift_lastname="soap",
    discord_accountusername="Joe Soap",
    discord_accountdisplayname="Crusher Joe",
    discord_profiledisplayname="Joe the beast",
    comment="This is a comment"
)

# Create an instance of the ClubMemberItem class for a member (joanna) by instantiating a new instance and then populating sample data manually. This is an equally valid way to create a ClubMemberItem instance.

joanna = ClubMemberItem()
joanna.zwift_id = 88888888
joanna.zwift_firstname = "joanna"
joanna.zwift_lastname = "soap"
joanna.discord_accountusername = "Joanna Soap"
joanna.discord_accountdisplayname = "Sweet Joanna"
joanna.discord_profiledisplayname = "Joanna the amazon"
joanna.comment = "This is a comment"

# Change the value of an property of a ClubMemberItem (joanna)
joanna.zwift_id = 99999999

# Given an instance of a ClubMemberItem (joe), convert the ClubMemberItem to an object that can be used to serialise the ClubMemberItem as JSON.
# For a ClubMemberItem, the object is a dictionary of the member's properties with the property names as keys and the property values as values.

joe_as_object = joe.to_equivalentobject()

# Given an object that can be used to serialise the ClubMemberItem as JSON i.e. is a valid dict[str, str], use the object to instantiate a new ClubMemberItem.
# In an integrated system, this object will most likely have generated in the first place by member.to_equivalentobject() 
# This is a simulation of the process of receiving a python dictionary from somewhere, anywhere and using it to create a member.

joe = ClubMemberItem.from_equivalentobject(joe_as_object)

#Show how to serialise a ClubMemberItem instance into a JSON string that can be saved to a file or sent over the network and/or stored in a database

joe_as_json = json.dumps(joe_as_object)

# Combine two steps into one. This is the most common operation you will use in your projects.
# Convert a ClubMemberItem instance into a JSON string in one step that you can then save, send, and/or store in a JSON database.

joe_as_json = json.dumps(joe.to_equivalentobject())


# Print the JSON of a ClubMemberItem (joe) to the console in the format it will be saved, sent, and/or stored in a database
print("\n")
print("Printing a ClubMemberItem (joe) serialised into JSON as it will be saved or transmitted in machine-readable format:-")
print("\n")
print(joe_as_json)

# Print the JSON of a ClubMemberItem (joe) to the console in a more human-readable format
print("\n")
print("Printing a ClubMemberItem (joe) serialised into JSON in a more human-readable format with pretty line-breaks and indenting:-")
print("\n")
joe_as_json = json.dumps(joe_as_object, indent=4)
print(joe_as_json)

# Demonstrate how to translate JSON strings into a ClubMemberItem. This is most likely the most common function you will use in your projects
# Simulates the process of receiving JSON strings from the web, a file, or a database and converting them into a ClubMemberItem instance.
# The JSON could have come from anywhere, but to represent a valid ClubMemberItem it must deserialise successfully into a Dict[string, string].

# Example A. Use this this string to show that that superfluous additional properties in the JSON string are no problem.
# Extra properties are skipped and ignored by the from_json method.
# The ClubMemberItem instance is created with only the properties that are in the ClubMemberItem class.


random_string_obtained_from_web1 = """{
    "zwift_id": 11111111,
    "zwift_firstname": "happy",
    "zwift_lastname": "larry",
    "discord_accountusername": "happy larry",
    "discord_accountdisplayname": "Happy as Larry",
    "discord_profiledisplayname": "Even happier than larry", 
    "when_touched": 1735500066,
    "originating_guid": "8ebabe1f-72e1-478f-94c8-362007b26c20",
    "comment": "This is a comment",
    "property_added_later": "something later",
    "property_added_much_later": "something much later",
    "property_added_much_much_later": "something much much later"
}"""

# Example A. Use this string to show that missing properties are safely skipped. 
# Missing properties are assigned default values as specified in the ClubMemberItem class.

random_string_obtained_from_web2 = """{
    "zwift_id": 11111111,
    "zwift_firstname": "happy"
}"""

# Use this string to show what happens if the JSON string is not a tolerable represention of a ClubMemberItem.
# In this sample the JSON is a list!
# The process of deserialisation is aborted and an error is raised.

random_string_obtained_from_web3 = """[1, 2, 3, 4, 5]"""


# Use this string to show that the process of deserialisation is aborted if the JSON string is not a passable represention of a ClubMemberItem. 
# In this sample the JSON is wrong becuase the zwift_id property is a string instead of an integer.
# The process of deserialisation is aborted and an error is raised.

random_string_obtained_from_web4 = """{
    "zwift_id": "rubbish",
    "zwift_firstname": "happy"
}"""

try:
    # Comment out all but one of the following lines to test the different JSON strings. The first two strings pass the test, the last two fail.
    member_from_web = ClubMemberItem.from_json(random_string_obtained_from_web1)
    # member_from_web = ClubMemberItem.from_json(random_string_obtained_from_web2)
    # member_from_web = ClubMemberItem.from_json(random_string_obtained_from_web3)
    # member_from_web = ClubMemberItem.from_json(random_string_obtained_from_web4)
except ValueError as e:
    print("\n\n")
    print(f"Error: {e}")
    print("\n\n")
    sys.exit()

# Print the successfully created instance's underlying structure using a dunder method (__dict__) as the print argument
print("\n")
print("Printing a ClubMemberItem object obtained from a JSON string using the dunder method (__dict__) to reveal the object's internal structure:-")
print("\n")
print(member_from_web.__dict__)
print("\n\n")

print("All demonstrations of the operation and usages of the ClubMemberItem class are complete. Enjoy using the class in your projects.")
print("\n")

def main():
    pass

if __name__ == "__main__":
    main()