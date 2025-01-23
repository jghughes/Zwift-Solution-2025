import datetime
from datetime import datetime, timezone
import json
import uuid
from club_member_dto import ClubMemberDto

class ClubMemberItem:
    """
    An object representing a member's basic particulars. The object can be round-tripped to and from JSON using ClubMemberDto.

    properties:
        primarykey (str):                   The primary key of the member.
        zsun_id (str):                      The ZSUN ID of the member.
        zsun_firstname (str):               The first name of the member.
        zsun_lastname (str):                The last name of the member.
        zwift_id (int):                     The Zwift ID of the member.
        zwift_firstname (str):              The first name of the member.
        zwift_lastname (str):               The last name of the member.
        discord_accountusername (str):      The Discord account username of the member.
        discord_accountdisplayname (str):   The Discord account display name of the member.
        discord_profiledisplayname (str):   The Discord profile display name of the member.
        when_touched (int):                 The ISO 8601 datetime converted to seconds.
        originating_guid (str):             A unique identifier for this instantiated object.
        comment (str):                      An optional comment about the member or entry.

    functions:
        set_primarykey:         Computes a key for the ClubMemberItem instance based on specified conditions.
        to_json_dto:            Converts the ClubMemberItem instance to a matching ClubMemberDto as a JSON string.
        from_json_dto:          Creates a ClubMemberItem instance from a JSON string representing a ClubMemberDto.
        to_dto:                 Converts a ClubMemberItem instance to a ClubMemberDto instance.
        from_dto:               Creates a ClubMemberItem instance from a ClubMemberDto instance.
        to_dto_list:            Converts a list of ClubMemberItem instances to a list of ClubMemberDto instances.
        from_dto_list:          Creates a list of ClubMemberItem instances from a list of ClubMemberDto instances.
        __str__:                Override to make a pretty string representation of the ClubMemberItem instance, with the timestamp being human-readable.
    """
    primarykey: str =  ""
    zsun_id: str =  ""
    zsun_firstname: str =  ""
    zsun_lastname: str =  ""
    zwift_id: int = 0
    zwift_firstname: str =  ""
    zwift_lastname: str =  ""
    discord_accountusername: str =  ""
    discord_accountdisplayname: str =  ""
    discord_profiledisplayname: str =  ""
    when_touched: int = int(datetime.now(timezone.utc).timestamp())
    originating_guid: str =  str(uuid.uuid4())
    comment: str =  ""

    def set_primarykey(self):
        """
        Computes a key for the ClubMemberItem instance sequentially based on the specified conditions.

        Args:
            clubmember (ClubMemberItem): The ClubMemberItem instance to compute the key for.

        Returns:
            str: The computed key.
        """
        if self.zwift_id != 0:
            self.primarykey = f"{self.zwift_id}"
        elif (
            self.discord_accountdisplayname and self.discord_accountdisplayname.strip()
        ):
            self.primarykey = f"discord-{self.discord_accountdisplayname}"
        else:
            self.primarykey = f"blank-{str(uuid.uuid4())[:4]}"

    @staticmethod
    def to_json_dto(item: 'ClubMemberItem') -> str:
        """
        Converts the ClubMemberItem instance to a matching ClubMemberDto as a JSON string.
        Use this function to return a JSON string representation of the ClubMemberDto.

        Returns:
            str: A JSON string representation of the ClubMemberDto instance.
        """

        dto = ClubMemberItem.to_dto(item)

        return json.dumps(dto)

    @staticmethod
    def from_json_dto(text: str)-> 'ClubMemberItem':
        """
        Creates a ClubMemberItem instance from a string of text.

        Args:
            text (str): A JSON string representing a ClubMemberDto.

        Returns:
            ClubMemberItem: A new instance of the ClubMemberItem class.
        """
        try:
            try:
                pythonobject = json.loads(text)
            except json.JSONDecodeError as e:
                raise ValueError(f"The provided input string is not valid JSON. It is malformed: {e}")

            # Explanation: The following code is a bit of a hack. It is a workaround to the fact that the json.loads() method does not 
            # return a ClubMemberDto object, or any object, just like magic. Returns a dictionary with string keys and values as JSON strings. 
            # The dictionary is then used to create
            # The code attempts to create a new instance of a ClubMemberDto object from the JSON string. 
            # The ** operator is used to unpack the pythonobject dictionary. This means that each key-value pair 
            # in the dictionary is passed as a keyword argument to the ClubMemberDto constructor
            # For example, if pythonobject is {"primarykey": "1", "zsun_id": "123", ...}, it is equivalent to calling ClubMemberDto(primarykey="1"

            try:
                dto = ClubMemberDto(**pythonobject)
            except ValueError as e:
                raise ValueError(
                    f"Instantiation of new instance of a ClubMemberDto object failed. The input string of JSON did not satisfy the minimum requirements: {e}"
                )

            answer = ClubMemberItem.from_dto(dto)
            
            # one last thing: test the timestamp because who knows what its provenence is, replace if invalid
            try:
                _ = datetime.fromtimestamp(answer.when_touched, tz=timezone.utc).isoformat()  
            except (ValueError, OSError): # If the timestamp is invalid, set it to utcnow
                answer.when_touched = int(datetime.now(timezone.utc).timestamp()) 

            return answer

        except ValueError as e:
            raise ValueError(
                f"Instantiation of new instance of a ClubMemberItem object failed. The input string of JSON did not satisfy the minimum requirements to represent the object: {e}"
            )

    @staticmethod
    def to_dto(item: 'ClubMemberItem') -> ClubMemberDto:
        """
        Converts a ClubMemberItem instance to a ClubMemberDto instance.
        Args:
            item (ClubMemberItem): The ClubMemberItem instance to convert to a ClubMemberDto instance.
        Returns:
            ClubMemberDto: A new instance of the ClubMemberDto class.
        """
        return ClubMemberDto(
            primarykey=item.primarykey,
            zsun_id=item.zsun_id,
            zsun_firstname=item.zsun_firstname,
            zsun_lastname=item.zsun_lastname,
            zwift_id=item.zwift_id,
            zwift_firstname=item.zwift_firstname,
            zwift_lastname=item.zwift_lastname,
            discord_accountusername=item.discord_accountusername,
            discord_accountdisplayname=item.discord_accountdisplayname,
            discord_profiledisplayname=item.discord_profiledisplayname,
            when_touched=item.when_touched,
            originating_guid=item.originating_guid,
            comment=item.comment,
        )

    @staticmethod
    def from_dto(dto: ClubMemberDto) -> 'ClubMemberItem':
        """
        Creates a ClubMemberItem instance from a ClubMemberDto instance.
        Args:
            dto (ClubMemberDto): The ClubMemberDto instance to create the ClubMemberItem instance from.
        Returns:
            ClubMemberItem: A new instance of the ClubMemberItem class.
        """

        item = ClubMemberItem()
        item.primarykey = dto.primarykey
        item.zsun_id = dto.zsun_id
        item.zsun_firstname = dto.zsun_firstname
        item.zsun_lastname = dto.zsun_lastname
        item.zwift_id = dto.zwift_id
        item.zwift_firstname = dto.zwift_firstname
        item.zwift_lastname = dto.zwift_lastname
        item.discord_accountusername = dto.discord_accountusername
        item.discord_accountdisplayname = dto.discord_accountdisplayname
        item.discord_profiledisplayname = dto.discord_profiledisplayname
        item.when_touched = dto.when_touched
        item.originating_guid = dto.originating_guid
        item.comment = dto.comment
        return item

    @staticmethod
    def to_dto_list(items: list['ClubMemberItem']) -> list[ClubMemberDto]:
        """
        Converts a list of ClubMemberItem instances to a list of ClubMemberDto instances.
        Args:
            items (list[ClubMemberItem]): The list of ClubMemberItem instances to convert to a list of ClubMemberDto instances.
        Returns:
            list[ClubMemberDto]: A list of new instances of the ClubMemberDto class.
        """
        return [ClubMemberItem.to_dto(z) for z in items]

    @staticmethod
    def from_dto_list(dtos: list[ClubMemberDto]) -> list['ClubMemberItem']:
        """
        Creates a list of ClubMemberItem instances from a list of ClubMemberDto instances.

        Args:
            dtos (list[ClubMemberDto]): The list of ClubMemberDto instances to create the ClubMemberItem instances from.

        Returns:
            list[ClubMemberItem]: A list of new instances of the ClubMemberItem class.
        """
        return [ClubMemberItem.from_dto(z) for z in dtos]
  
    def __str__(self):
        # sole purpose of this overload is to provide a pretty string representation which needs to make timestamp human readable
        try:
            if self.when_touched == 0:
                pretty_timestamp = "[no timestamp]"
            else:
                pretty_timestamp = f"[{datetime.fromtimestamp(self.when_touched, tz=timezone.utc).isoformat()}]"
        except (ValueError, OSError):
            pretty_timestamp = "[no timestamp]"

        return f"ClubMemberItem: {self.primarykey} - {self.zsun_id} - {self.zsun_firstname} {self.zsun_lastname} {self.zwift_id} {self.zwift_firstname} {self.zwift_lastname} {self.discord_accountusername} {self.discord_accountdisplayname} {self.discord_profiledisplayname} {pretty_timestamp}"


# the following code is for testing the ClubMember classes

def test_club_member_dto():
    dto = ClubMemberDto(
        primarykey="1",
        zsun_id="123",
        zsun_firstname="John",
        zsun_lastname="Doe",
        zwift_id=456,
        zwift_firstname="John",
        zwift_lastname="Doe",
        discord_accountusername="john_doe",
        discord_accountdisplayname="JohnDoe",
        discord_profiledisplayname="JohnDoeProfile",
        when_touched=1633036800,
        originating_guid="123e4567-e89b-12d3-a456-426614174000",
        comment="Test comment"
    )
    print(dto)

def test_clubmemberitem():
    item = ClubMemberItem()
    item.primarykey = "1"
    item.zsun_id = "123"
    item.zsun_firstname = "John"
    item.zsun_lastname = "Doe"
    item.zwift_id = 456
    item.zwift_firstname = "John"
    item.zwift_lastname = "Doe"
    item.discord_accountusername = "john_doe"
    item.discord_accountdisplayname = "JohnDoe"
    item.discord_profiledisplayname = "JohnDoeProfile"
    item.when_touched = 1633036800
    item.originating_guid = "123e4567-e89b-12d3-a456-426614174000"
    item.comment = "Test comment"
    print(item)

if __name__ == "__main__":
    test_club_member_dto()
    test_clubmemberitem()
