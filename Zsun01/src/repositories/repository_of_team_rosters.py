from typing import  List, Dict
from collections import defaultdict
from constants import DEFAULT_EXERTION_INTENSITY_FACTOR_LIMIT

class RepositoryOfTeamRosters:
    """
    Static repository for managing Zwift team rosters, rider information, and team exertion intensity factors.

    Attributes:
        _team_rosters_as_dict (Dict[str, Dict[str, str]]): 
            Maps team nicknames to dictionaries of rider Zwift IDs and their nicknames.
        _team_exertion_intensity_factors_as_dict (Dict[str, float]): 
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
        get_rider_nickname_by_zwiftID(zwift_id):
            Returns the nickname of a rider given their Zwift ID, or an empty string if not found.
        get_exertion_intensity_factor_for_team(team_nickname):
            Returns the exertion intensity factor for the specified team.
    """

    _team_exertion_intensity_factors_as_dict: Dict[str, float] = defaultdict(
        lambda: DEFAULT_EXERTION_INTENSITY_FACTOR_LIMIT,
        {
            "everybody": 1.0,
            "scratchpad": 1.0,
            "test": 1.0,
            "giants": 1.1,
            "fire": 1.1,
            "kissed": 1.05,
            "sirius": 1.0,
            "betel": 0.9,
            "dome": 1.03,
            "bojo": 1.0,
            "inhibited": 1.0,
        }
    )
 
    _team_rosters_as_dict: Dict[str, Dict[str, str]] = defaultdict(
        lambda: defaultdict(str),
        {
            "scratchpad": defaultdict(str, {
                "5490373": "barry_beck",
                "991817": "brandi_steeve",
                "9011": "bryan_bumpas",
            #     "163795": "colin_fetter",
            #     "5569057": "cory_cook",
            #     "3147366": "dave_konicek",
            #     "4945836": "david_evanetich",
            #     "523861": "gary_putlock",
            #     "5134": "husky_crone",
            #     "1884456": "john_hughes",
            #     "2508033": "josh_neil",
            #     "2803600": "larry_mccamon",
            #     "383480": "lynsey_segal",
            #     "5530045": "mark_brzezinski",
            #     "1024413": "matt_steeve",
            #     "2902662": "matthew_wongkee",
            #     "1657744": "melissa_warwick",
            #     "1707548": "meridith_leubner",
            #     "3142395": "rachel_laponsey",
            #     "1193": "richard_mann",
            #     "4284467": "richard_yamin",
            #     "5524007": "robo_hop",
            #     "384442": "roland_segal",
            #     "6033853": "sarah_madden",
            #     "11526": "scott_mcveigh",
            #     "1956": "scott_yarosh",
            #     "2682791": "selena_shaikh",
            #     "6142432": "steve_seiler",
            #     "5421258": "tim_reid",
            #     "11741": "tom_bick"
            # }),
            # "test": defaultdict(str, {
            #     "5490373": "barry_beck",
            #     "991817": "brandi_steeve",
            #     "9011": "bryan_bumpas",
            #     "163795": "colin_fetter",
            #     "5569057": "cory_cook",
            #     "3147366": "dave_konicek",
            #     "4945836": "david_evanetich",
            #     "523861": "gary_putlock",
            #     "183277": "giao_nguyen",
            #     "5134": "husky_crone",
            #     "1884456": "john_hughes",
            #     "2508033": "josh_neil",
            #     "2803600": "larry_mccamon",
            #     "383480": "lynsey_segal",
            #     "5530045": "mark_brzezinski",
            #     "1024413": "matt_steeve",
            #     "2902662": "matthew_wongkee",
            #     "1657744": "melissa_warwick",
            #     "1707548": "meridith_leubner",
            #     "3142395": "rachel_laponsey",
            #     "1193": "richard_mann",
            #     "4284467": "richard_yamin",
            #     "5524007": "robo_hop",
            #     "384442": "roland_segal",
            #     "6033853": "sarah_madden",
            #     "11526": "scott_mcveigh",
            #     "1956": "scott_yarosh",
            #     "2682791": "selena_shaikh",
            #     "6142432": "steve_seiler",
            #     "5421258": "tim_reid",
            #     "11741": "tom_bick"
            }),
            "sirius": defaultdict(str, {
                "5490373": "barry_beck",
                # "480698": "brent_huser",
                "9011": "bryan_bumpas",
                # "5569057": "cory_cook",
                # "3147366": "dave_konicek",
                "4945836": "david_evanetich",
                # "5134": "husky_crone",
                # "523861": "gary_putlock",
                "1884456": "john_hughes",
                # "2508033": "josh_neil",
                "2803600": "larry_mccamon",
                # "383480": "lynsey_segal",
                # "6454226": "mark_deckard",
                # "276319": "mark_goveia",
                # "1024413": "matt_steeve",
                # "2902662": "matthew_wongkee",
                # "1657744": "melissa_warwick",
                # "1707548": "meridith_leubner",
                # "1609384": "mike_echo",
                # "1193": "richard_mann",
                # "4284467": "richard_yamin",
                # "5524007": "robo_hop",
                # "384442": "roland_segal",
                # "11526": "scott_mcveigh",
                # "1956": "scott_yarosh",
                # "5421258": "tim_reid",
                # "1549984": "tim_chang",
                "11741": "tom_bick",
            }),
            "betel": defaultdict(str, {
                # "5490373": "barry_beck",
                # "5726145": "bill_henson",
                # "480698": "brent_huser",
                # "9011": "bryan_bumpas",
                # "991817": "brandi_steeve",
                # "5569057": "cory_cook",
                # "6944221": "chris_lockwood",
                "4945836": "david_evanetich",
                # "183277": "giao_nguyen",
                # "523861": "gary_putlock",
                "1884456": "john_hughes",
                # "2508033": "josh_neil",
                # "2803600": "larry_mccamon",
                # "383480": "lynsey_segal",
                # "276319": "mark_goveia",
                # "1024413": "matt_steeve",
                # "2902662": "matthew_wongkee",
                # "1657744": "melissa_warwick",
                "1707548": "meridith_leubner",
                "1618188": "michael_rebarchik",
                # "1609384": "mike_echo",
                # "3142395": "rachel_laponsey",
                # "1193": "richard_mann",
                # "4284467": "richard_yamin",
                # "5524007": "robo_hop",
                # "384442": "roland_segal",
                # "6033853": "sarah_madden",
                # "11526": "scott_mcveigh",
                # "85925": "steve_lehman",

            }),
            "dome": defaultdict(str, {
                "5490373": "barry_beck",
                "1363894": "bill_lomax",
                "3236875": "carl_geiser",
                # "5569057": "cory_cook",
                "5365450": "joe_thomasson",
                "5031490": "john_rice",
                # "618585": "kent_johnson",
                "5530045": "mark_brzezinski",
            }),
            "bojo": defaultdict(str, {
                "5569057": "cory_cook",
                "618585": "kent_johnson",
            }),
            "inhibited": defaultdict(str, {
                # "2619046": "alex_shiver",
                # "7712769": "anthony_d'angelo",
                "5726145": "bill_henson",
                # "480698": "brent_huser",
                # "640780": "carl_peltzer",
                # "473087": "curtis_repen",
                "4945836": "david_evanetich",
                # "1604216": "henry_llamas",
                # "4193240": "john_artless",
                "1884456": "john_hughes",
                "618585": "kent_johnson",
                "1111583": "ken_chappell",
                # "1024413": "matt_steeve",
                "7160372": "sean-o-reilly",
                # "7460730": "tony_chang",
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
                "1662067": "steve_james",
            }),
            "fire": defaultdict(str, {
                "3147366": "dave_konicek",
                "1408923": "gertjan_buisman",
                "4348809": "harrison_clark",
                "5959864": "james_veitch",
                "2873877": "rick_porteous",
                "2705238": "sjors_van_liempt",
                "11741": "tom_bick",
                "2419188": "xander_crawshaw",
            }),
            "kissed": defaultdict(str, {
                "383480": "lynsey_segal",
            })
        }
    )


    @staticmethod
    def get_nicknames_of_teams(team_nickname: str) -> List[str]:
        return list(RepositoryOfTeamRosters._team_rosters_as_dict.keys())

    @staticmethod
    def get_IDs_of_riders_on_a_team(team_nickname: str) -> List[str]:
        if team_nickname in RepositoryOfTeamRosters._team_rosters_as_dict:
            return list(RepositoryOfTeamRosters._team_rosters_as_dict[team_nickname].keys())
        else:
            raise ValueError(
                f"Team '{team_nickname}' not found. Available teams: {list(RepositoryOfTeamRosters._team_rosters_as_dict.keys())}"
            )

    @staticmethod
    def get_IDs_of_all_riders_on_all_teams() -> List[str]:
        """
        Returns a sorted list of unique Zwift IDs for all riders across all teams.
        """
        all_ids: set[str] = set()
        for roster in RepositoryOfTeamRosters._team_rosters_as_dict.values():
            all_ids.update(roster.keys())
        return sorted(all_ids)

    @staticmethod
    def get_nicknames_of_riders_on_a_team(team_nickname: str) -> List[str]:
        if team_nickname in RepositoryOfTeamRosters._team_rosters_as_dict:
            return list(RepositoryOfTeamRosters._team_rosters_as_dict[team_nickname].values())
        else:
            raise ValueError(
                f"Team '{team_nickname}' not found. Available teams: {list(RepositoryOfTeamRosters._team_rosters_as_dict.keys())}"
            )

    @staticmethod
    def get_exertion_intensity_factor_for_team(team_nickname: str) -> float:
        if team_nickname in RepositoryOfTeamRosters._team_exertion_intensity_factors_as_dict:
            return RepositoryOfTeamRosters._team_exertion_intensity_factors_as_dict[team_nickname]
        else:
            raise ValueError(
                f"Team '{team_nickname}' not found. Available teams: {list(RepositoryOfTeamRosters._team_exertion_intensity_factors_as_dict.keys())}"
            )

    @staticmethod
    def get_rider_nickname_by_zwiftID(zwift_id: str) -> str:
        for roster in RepositoryOfTeamRosters._team_rosters_as_dict.values():
            if zwift_id in roster:
                return roster[zwift_id]
        return ""

    @staticmethod
    def get_dict_of_teams_and_their_riders() -> Dict[str, Dict[str, str]]:
        return RepositoryOfTeamRosters._team_rosters_as_dict
