from typing import  List, DefaultDict
from collections import defaultdict
from constants import DEFAULT_EXERTION_INTENSITY_FACTOR_LIMIT
import logging
logger = logging.getLogger(__name__)

# see inside this class for the objects containing the data on teams and riders. you can change the data anyhow you like
class RepositoryOfTeams:
    """
    Static repository for managing Zwift team rosters, rider information, and team exertion intensity factors.

    Attributes:
        _dict_of_teams (DefaultDict[str, DefaultDict[str, str]]): 
            Maps team nicknames to dictionaries of rider Zwift IDs and their nicknames.
        _dict_of_team_exertion_intensity_factors (DefaultDict[str, float]): 
            Maps team nicknames to their exertion intensity factor.

    Methods:
        get_dict_of_teams_and_their_riders():
            Returns the dictionary of all teams and their riders.
        get_nicknames_of_teams():
            Returns a list of all team nicknames.
        get_IDs_of_riders_on_a_team(team_nickname):
            Returns a list of Zwift IDs for riders on the specified team.
        get_nicknames_of_riders_on_a_team(team_nickname):
            Returns a list of rider nicknames for the specified team.
        get_rider_nickname_by_zwiftID(zwiftID):
            Returns the nickname of a rider given their Zwift ID, or an empty string if not found.
        get_exertion_intensity_factor_for_team(team_nickname):
            Returns the exertion intensity factor for the specified team.
    """

    _dict_of_teams: DefaultDict[str, DefaultDict[str, str]] = defaultdict(
        lambda: defaultdict(str),
        {
            "test_sample": defaultdict(str, {
                # "5490373": "barry_beck",
                # "991817": "brandi_steeve",
                # "9011": "bryan_bumpas",
                # "5569057": "cory_cook",
                "3147366": "dave_konicek",
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
                # "1707548": "meridith_leubner",
                # "1193": "richard_mann",
                # "3142395": "rachel_laponsey",
                # "384442": "roland_segal",
                # "11526": "scott_mcveigh",
                # "1956": "scott_yarosh",
                # "2682791": "selena_shaikh",
                # "6142432": "steve_seiler",
                # "5421258": "tim_reid",
                # "11741": "tom_bick"
            }),
            "betel": defaultdict(str, {
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
            }),
            "sirius": defaultdict(str, {
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
            }),
            "bojo": defaultdict(str, {
                "4945836": "david_evanetich",
                "1884456": "john_hughes",
                "1024413": "matt_steeve",
                "11526": "scott_mcveigh",
                "947338": "mark_pietz",
                "276319": "mark_goveia"
            }),
            "dome": defaultdict(str, {
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
            }),
            "giants": defaultdict(str, {
                "4204538": "ceri_pritchard",
                "407780": "colin_humphrey",
                "3147366": "dave_konicek",
                "2449352": "ed_bentley",
                "106298": "eltjo_biemold",
                "2847282": "ivan_parks",
                "172221": "john_glass",
                "197937": "roy_roesthuis",
                "1662067": "steve_james"
            }),
            "fire": defaultdict(str, {
                "3147366": "dave_konicek",
                "1408923": "gertjan_buisman",
                "4348809": "harrison_clark",
                "5959864": "james_veitch",
                "2873877": "rick_porteous",
                "2705238": "sjors_van_liempt",
                "11741": "tom_bick",
                "2419188": "xander_crawshaw"
            }),
            "kissed": defaultdict(str, {
                "383480": "lynsey_segal"
            })
        }
    )

    _dict_of_team_exertion_intensity_factors: DefaultDict[str, float] = defaultdict(
        lambda: DEFAULT_EXERTION_INTENSITY_FACTOR_LIMIT,
        {
            "test_sample": 0.9,
            "betel": 0.95,
            "sirius": 1.05,
            "bojo": 1.0,
            "dome": 1.05,
            "giants": 1.1,
            "fire": 1.1,
            "kissed": 1.05,
        }
    )

    @staticmethod
    def get_nicknames_of_teams(team_nickname: str) -> List[str]:
        return list(RepositoryOfTeams._dict_of_teams.keys())

    @staticmethod
    def get_IDs_of_riders_on_a_team(team_nickname: str) -> List[str]:
        if team_nickname in RepositoryOfTeams._dict_of_teams:
            return list(RepositoryOfTeams._dict_of_teams[team_nickname].keys())
        else:
            raise ValueError(
                f"Team '{team_nickname}' not found. Available teams: {list(RepositoryOfTeams._dict_of_teams.keys())}"
            )

    @staticmethod
    def get_nicknames_of_riders_on_a_team(team_nickname: str) -> List[str]:
        if team_nickname in RepositoryOfTeams._dict_of_teams:
            return list(RepositoryOfTeams._dict_of_teams[team_nickname].values())
        else:
            raise ValueError(
                f"Team '{team_nickname}' not found. Available teams: {list(RepositoryOfTeams._dict_of_teams.keys())}"
            )

    @staticmethod
    def get_exertion_intensity_factor_for_team(team_nickname: str) -> float:
        if team_nickname in RepositoryOfTeams._dict_of_team_exertion_intensity_factors:
            return RepositoryOfTeams._dict_of_team_exertion_intensity_factors[team_nickname]
        else:
            raise ValueError(
                f"Team '{team_nickname}' not found. Available teams: {list(RepositoryOfTeams._dict_of_team_exertion_intensity_factors.keys())}"
            )

    @staticmethod
    def get_rider_nickname_by_zwiftID(zwiftID: str) -> str:
        for roster in RepositoryOfTeams._dict_of_teams.values():
            if zwiftID in roster:
                return roster[zwiftID]
        return ""

    @staticmethod
    def get_dict_of_teams_and_their_riders() -> DefaultDict[str, DefaultDict[str, str]]:
        return RepositoryOfTeams._dict_of_teams
