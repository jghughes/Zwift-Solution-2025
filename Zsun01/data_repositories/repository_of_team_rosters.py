from typing import  List
from collections import defaultdict
from typing import List, Dict, DefaultDict
from dataclasses import dataclass, field
import logging
logger = logging.getLogger(__name__)

team_rosters = defaultdict(dict, {
    "test": {
        # "5490373": "barry_beck",
        # "991817": "brandi_steeve",
        # "9011": "bryan_bumpas",
        # "5569057": "cory_cook",
        # "3147366": "dave_konicek",
        # "4945836": "david_evanetich",
        # "183277": "giao_nguyen",
        # "5134": "husky_crone",
        "1884456": "john_hughes",
        "2508033": "josh_neil",
        # # "383480": "lynsey_segal",
        # "5530045": "mark_brzezinski",
        # "1024413": "matt_steeve",
        # "2902662": "matthew_wongkee",
        # "1657744": "melissa_warwick",
        "1707548": "meridith_leubner",
        "1193": "richard_mann",
        # "3142395": "rachel_laponsey",
        # "384442": "roland_segal",
        # "11526": "scott_mcveigh",
        # "1956": "scott_yarosh",
        # "2682791": "selena_shaikh",
        # "6142432": "steve_seiler",
        # "5421258": "tim_reid",
        # "11741": "tom_bick"
    },
    "betel": {
        # "5490373": "barry_beck",
        # "991817": "brandi_steeve",
        "5569057": "cory_cook",
        # "4945836": "david_evanetich",
        # "183277": "giao_nguyen",
        "1884456": "john_hughes",
        # "2508033": "josh_neil",
        "383480": "lynsey_segal",
        # "1024413": "matt_steeve",
        "2902662": "matthew_wongkee",
        # "1657744": "melissa_warwick",
        # "1707548": "meridith_leubner",
        "1193": "richard_mann",
        # "3142395": "rachel_laponsey",
        "384442": "roland_segal",
    },
    "sirius": {
        "5490373": "barry_beck",
        "9011": "bryan_bumpas",
        "5569057": "cory_cook",
        "3147366": "dave_konicek",
        "5134": "husky_crone",
        "1884456": "john_hughes",
        "383480": "lynsey_segal",
        "1657744": "melissa_warwick",
        "1707548": "meridith_leubner",
        "11526": "scott_mcveigh",
        "1956": "scott_yarosh",
        "5421258": "tim_reid",
        "11741": "tom_bick"
    },
    "bojo": {
        "4945836": "david_evanetich",
        "1884456": "john_hughes",
        "1024413": "matt_steeve",
        "11526": "scott_mcveigh",
        "947338": "mark_pietz",
        "276319": "mark_goveia"
    },
    "dome": {
        "5569057": "cory_cook",
        "107802": "jaroslav_kurka",
        "5530045": "mark_brzezinski",
        "6705678": "david_goff",
        "481901": "scott_peirson",
        "5268724": "thomas_elliott",
        "1707548": "meridith_leubner",
        "1193": "richard_mann",
        "384442": "roland_segal",
        "11526": "scott_mcveigh",
        "1956": "scott_yarosh",
        "2682791": "selena_shaikh",
        "6142432": "steve_seiler",
        "5421258": "tim_reid",
        "11741": "tom_bick"
    },
    "giants": {
        "4204538": "ceri_pritchard",
        "407780": "colin_humphrey",
        "3147366": "dave_konicek",
        "2449352": "ed_bentley",
        "106298": "eltjo_biemold",
        "2847282": "ivan_parks",
        "172221": "john_glass",
        "197937": "roy_roesthuis",
        "1662067": "steve_james"
    },
    "fire": {
        "3147366": "dave_konicek",
        "1408923": "gertjan_buisman",
        "4348809": "harrison_clark",
        "5959864": "james_veitch",
        "2873877": "rick_porteous",
        "2705238": "sjors_van_liempt",
        "11741": "tom_bick",
        "2419188": "xander_crawshaw"
    },
    "kissed": {
        "383480": "lynsey_segal"
    }
})

@dataclass
class RepositoryOfTeams:
    """
    Repository for managing Zwift team rosters and rider information.

    This class provides methods to load team data, retrieve team rosters,
    get rider IDs for a team, and look up rider names by Zwift ID.

    All data is encapsulated; no public properties are exposed.
    """

    _teams: Dict[str, DefaultDict[str, str]] = field(default_factory=dict, init=False)

    def populate_repository(
        self,
    ):
        """
        Loads team roster data directly from the team_rosters object.

        Args:
            logger (logging.Logger): Logger for status and error messages.
            log_level (int): Logging level (default: logging.INFO).
        """
        
        try:
            self._teams = {
                team: defaultdict(str, roster)
                for team, roster in team_rosters.items()
            }
            logger.info(f"Loaded {len(self._teams)} teams from in-memory team_rosters object")
        except Exception as e:
            logger.error(f"Failed to load teams from in-memory team_rosters object: {e}")
            self._teams = {}

    def get_dict_of_teams(self) -> Dict[str, DefaultDict[str, str]]:
        """
        Returns all loaded teams and their rosters.

        Returns:
            Dict[str, DefaultDict[str, str]]: Mapping of team names to rosters.
        """
        return self._teams

    def get_IDs_of_riders_on_roster(self, team_nickname: str) -> List[str]:
        """
        Returns a list of Zwift IDs for the specified team.

        Args:
            team_nickname (str): The nickname of the team.

        Returns:
            List[str]: List of Zwift IDs for the team.

        Raises:
            ValueError: If the team nickname is not found.
        """
        if team_nickname in self._teams:
            return list(self._teams[team_nickname].keys())
        else:
            raise ValueError(
                f"Team '{team_nickname}' not found. Available teams: {list(self._teams.keys())}"
            )

    def get_rider_nickname_by_zwiftID(self, zwiftID: str) -> str:
        """
        Returns the rider name for a given Zwift ID, searching all teams.

        Args:
            zwiftID (str): The Zwift ID to look up.

        Returns:
            str: The rider's name, or an empty string if not found.
        """
        for roster in self._teams.values():
            if zwiftID in roster:
                return roster[zwiftID]
        return ""

def get_all_team_rosters() -> Dict[str, DefaultDict[str, str]]:
    """
    Instantiates a RepositoryOfTeams, populates it from the teams_rosters.json file,
    and returns the loaded teams dictionary.

    Returns:
        Dict[str, DefaultDict[str, str]]: Mapping of team nicknames to rosters.
    """
    repo = RepositoryOfTeams()
    repo.populate_repository()
    return repo.get_dict_of_teams()

def get_riderIDs_on_team_roster(team_nickname: str) -> List[str]:
    """
    Instantiates a RepositoryOfTeams, populates it from the teams_rosters.json file,
    and returns the list of Zwift IDs for the specified team nickname.

    Args:
        team_nickname (str): The nickname of the team.

    Returns:
        List[str]: List of Zwift IDs for the team.

    Raises:
        ValueError: If the team nickname is not found.
    """

    repo = RepositoryOfTeams()
    repo.populate_repository()
    return repo.get_IDs_of_riders_on_roster(team_nickname)

def get_rider_shortname_by_zwiftID(zwiftID: str) -> str:
    """
    Instantiates a RepositoryOfTeams, populates it from the teams_rosters.json file,
    and returns the rider name for the given Zwift ID, searching all teams.

    Args:
        zwiftID (str): The Zwift ID to look up.

    Returns:
        str: The rider's name, or an empty string if not found.
    """
    repo = RepositoryOfTeams()
    repo.populate_repository()
    return repo.get_rider_nickname_by_zwiftID(zwiftID)

