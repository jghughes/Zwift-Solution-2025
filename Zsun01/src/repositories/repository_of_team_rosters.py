from collections import defaultdict
from constants import DEFAULT_EXERTION_INTENSITY_FACTOR_LIMIT

class RepositoryOfTeamRosters:
    """
    Static repository for managing Zwift team rosters, rider information, and team exertion intensity factors.

    Attributes:
        _team_rosters_as_dict_of_list (dict[str, list[tuple[str, str]]]):
            Maps team nicknames to ordered lists of (Zwift ID, nickname) tuples. A rider 
            may appear more than once in a roster, filling more than one slot.
        _team_exertion_intensity_factors_as_dict (dict[str, float]):
            Maps team nicknames to their exertion intensity factor.

    Methods:
        get_dict_of_teams_and_their_riders():
            Returns the dictionary of all teams and their riders.
        get_IDs_of_riders_on_a_team(team_nickname):
            Returns a list of Zwift IDs for the slots on the specified team, repeats included.
        get_unique_IDs_of_riders_on_a_team(team_nickname):
            Returns a list of distinct Zwift IDs for riders on the specified team, in roster order.
        get_exertion_intensity_factor_for_team(team_nickname):
            Returns the exertion intensity factor for the specified team.
    """

    _team_exertion_intensity_factors_as_dict: dict[str, float] = defaultdict(
        lambda: DEFAULT_EXERTION_INTENSITY_FACTOR_LIMIT,
        {
            "everybody": 1.0,
            "scratchpad": 1.0,
            "test": 1.0,
            "giants": 1.0,
            "fire": 1.0,
            "kissed": 1.0,
            "sirius": 1.0,
            "sirius_women": 1.0,
            "betel": 0.90,
            "dome": 1.05,
            "bojo": 1.0,
            "inhibited": 0.95,
            "rangers": 0.8,
            "rangers2026": 0.95,
        }
    )

    _team_rosters_as_dict_of_list: dict[str, list[tuple[str, str]]] = defaultdict(
        list,
        {
            "scratchpad": [
                # ("5490373", "barry_beck"),
                # ("991817", "brandi_steeve"),
                # ("9011", "bryan_bumpas"),
                # ("4204538", "ceri_pritchard"),
                # ("163795", "colin_fetter"),
                # ("5569057", "cory_cook"),
                # ("3147366", "dave_konicek"),
                ("4945836", "david_evanetich"),
                # ("523861", "gary_putlock"),
                # ("5134", "husky_crone"),
                ("1884456", "john_hughes"),
                ("2508033", "josh_neil"),
                # ("1111583", "ken_chappell"),
                # ("2803600", "larry_mccamon"),
                # ("846200", "lisa_bick"),
                # ("383480", "lynsey_segal"),
                # ("5530045", "mark_brzezinski"),
                # ("2902662", "matthew_wongkee"),
                # ("1657744", "melissa_warwick"),
                # ("1707548", "meridith_leubner"),
                # ("3142395", "rachel_laponsey"),
                # ("1193", "richard_mann"),
                # ("4284467", "richard_yamin"),
                # ("5524007", "robo_hop"),
                # ("384442", "roland_segal"),
                # ("6033853", "sarah_madden"),
                # ("11526", "scott_mcveigh"),
                # ("1956", "scott_yarosh"),
                # ("2682791", "selena_shaikh"),
                # ("6142432", "steve_seiler"),
                # ("103825", "stewart_lalieu"),
                # ("5421258", "tim_reid"),
                # ("11741", "tom_bick"),
                ("7460730", "tony_chang"),

            ],
            "test": [
                # ("5490373", "barry_beck"),
                # ("991817", "brandi_steeve"),
                # ("9011", "bryan_bumpas"),
            #     ("163795", "colin_fetter"),
            #     ("5569057", "cory_cook"),
            #     ("3147366", "dave_konicek"),
            #     ("4945836", "david_evanetich"),
            #     ("523861", "gary_putlock"),
            #     ("183277", "giao_nguyen"),
            #     ("5134", "husky_crone"),
                ("1884456", "john_hughes"),
                # ("1884456", "john_hughes"),
                # ("1884456", "john_hughes"),
            #     ("2508033", "josh_neil"),
            #     ("2803600", "larry_mccamon"),
            #     ("383480", "lynsey_segal"),
            #     ("5530045", "mark_brzezinski"),
            #     ("1024413", "matt_steeve"),
            #     ("2902662", "matthew_wongkee"),
            #     ("1657744", "melissa_warwick"),
            #     ("1707548", "meridith_leubner"),
            #     ("3142395", "rachel_laponsey"),
            #     ("1193", "richard_mann"),
            #     ("4284467", "richard_yamin"),
            #     ("5524007", "robo_hop"),
            #     ("384442", "roland_segal"),
            #     ("6033853", "sarah_madden"),
            #     ("11526", "scott_mcveigh"),
            #     ("1956", "scott_yarosh"),
            #     ("2682791", "selena_shaikh"),
            #     ("6142432", "steve_seiler"),
            #     ("5421258", "tim_reid"),
            #     ("11741", "tom_bick"),
            ],
            "sirius": [
                ("5490373", "barry_beck"),
                # ("480698", "brent_huser"),
                # ("9011", "bryan_bumpas"),
                # ("5569057", "cory_cook"),
                # ("3147366", "dave_konicek"),
                # ("4945836", "david_evanetich"),
                # ("5134", "husky_crone"),
                # ("523861", "gary_putlock"),
                # ("1884456", "john_hughes"),
                # ("2508033", "josh_neil"),
                # ("2803600", "larry_mccamon"),
                # ("846200", "lisa_bick"),
                # ("383480", "lynsey_segal"),
                # ("6454226", "mark_deckard"),
                # ("276319", "mark_goveia"),
                # ("1024413", "matt_steeve"),
                # ("2902662", "matthew_wongkee"),
                # ("1657744", "melissa_warwick"),
                ("1707548", "meridith_leubner"),
                ("1618188", "michael_rebarchik"),
                # ("1609384", "mike_echo"),
                # ("1193", "richard_mann"),
                # ("4284467", "richard_yamin"),
                # ("5524007", "robo_hop"),
                # ("384442", "roland_segal"),
                # ("11526", "scott_mcveigh"),
                # ("1956", "scott_yarosh"),
                ("6142432", "steve_seiler"),
                # ("5421258", "tim_reid"),
                # ("1549984", "tim_chang"),
                # ("11741", "tom_bick"),
            ],
            "magnetar": [
                ("456545", "carrie_merritt"),
                ("525104", "iva_gotz"),
                ("2398312", "kristen-dumoulin"),
                ("207797", "lori_pridham"),
                ("4750594", "lydia_lequesne"),
                # ("1657744", "melissa_warwick"),
                # ("1707548", "meridith_leubner"),
                # ("3142395", "rachel_laponsey"),
                # ("6033853", "sarah_madden"),
                ("87284", "sylvie_holmes"),
            ],
            "betel": [
                # ("5490373", "barry_beck"),
                # ("5726145", "bill_henson"),
                # ("480698", "brent_huser"),
                # ("9011", "bryan_bumpas"),
                # ("991817", "brandi_steeve"),
                # ("1646703", "cara_houston"),
                # ("456545", "carrie_merritt"),
                # ("5569057", "cory_cook"),
                # ("6944221", "chris_lockwood"),
                ("4945836", "david_evanetich"),
                # ("183277", "giao_nguyen"),
                # ("523861", "gary_putlock"),
                # ("525104", "iva_gotz"),
                # ("1884456", "john_hughes"),
                ("2508033", "josh_neil"),
                # ("1111583", "ken_chapple"),
                # ("618585", "kent_johnson"),
                # ("207797", "lori_pridham"),
                # ("2803600", "larry_mccamon"),
                # ("846200", "lisa_bick"),
                ("383480", "lynsey_segal"),
                # ("4750594", "lydia_lequesne"),
                # ("7720774", "mario_bautista"),
                # ("276319", "mark_goveia"),
                # ("1024413", "matt_steeve"),
                # ("2902662", "matthew_wongkee"),
                # ("1657744", "melissa_warwick"),
                # ("1707548", "meridith_leubner"),
                # ("1618188", "michael_rebarchik"),
                # ("1609384", "mike_echo"),
                # ("3142395", "rachel_laponsey"),
                ("1193", "richard_mann"),
                # ("4284467", "richard_yamin"),
                ("5524007", "robo_hop"),
                ("384442", "roland_segal"),
                # ("6033853", "sarah_madden"),
                # ("11526", "scott_mcveigh"),
                # ("85925", "steve_lehman"),
                # ("6142432", "steve_seiler"),


            ],
            "dome": [
                ("5490373", "barry_beck"),
                ("1363894", "bill_lomax"),
                ("3236875", "carl_geiser"),
                # ("5569057", "cory_cook"),
                ("5365450", "joe_thomasson"),
                ("5031490", "john_rice"),
                # ("618585", "kent_johnson"),
                ("5530045", "mark_brzezinski"),
            ],
            "bojo": [
                ("5569057", "cory_cook"),
                ("618585", "kent_johnson"),
            ],
            "inhibited": [
                ("2619046", "alex_shiver"),
                ("7712769", "anthony_d'angelo"),
                ("5726145", "bill_henson"),
                ("480698", "brent_huser"),
                ("640780", "carl_peltzer"),
                ("473087", "curtis_repen"),
                ("4945836", "david_evanetich"),
                ("1604216", "henry_llamas"),
                ("4193240", "john_artless"),
                ("1884456", "john_hughes"),
                ("618585", "kent_johnson"),
                ("1111583", "ken_chappell"),
                ("1024413", "matt_steeve"),
                ("7160372", "sean-o-reilly"),
                ("7460730", "tony_chang"),
            ],
            "giants": [
                ("4204538", "ceri_pritchard"),
                ("407780", "colin_humphrey"),
                ("3147366", "dave_konicek"),
                ("2449352", "ed_bentley"),
                ("106298", "eltjo_biemold"),
                ("2847282", "ivan_parks"),
                ("172221", "john_glass"),
                ("197937", "roy_roesthuis"),
                ("1662067", "steve_james"),
            ],
            "fire": [
                ("3147366", "dave_konicek"),
                ("1408923", "gertjan_buisman"),
                ("4348809", "harrison_clark"),
                ("5959864", "james_veitch"),
                ("2873877", "rick_porteous"),
                ("2705238", "sjors_van_liempt"),
                ("11741", "tom_bick"),
                ("2419188", "xander_crawshaw"),
            ],
            "kissed": [
                ("383480", "lynsey_segal"),
            ],
            "rangers": [
                # ("5726145", "bill_henson"),
                # ("1363894", "bill_lomax"),
                # ("456545", "carrie_merrit"),
                # ("473087", "curtis_repen"),
                # ("4945836", "david_evanetich"),
                ("1884456", "john_hughes"),
                 # ("2508033", "josh_neil"),
                # ("618585", "kent_johnson"),
                # ("7460730", "tony_chang"),
            ],
            "rangers2025": [
                ("991817", "brandi_steeve"),
                ("6944221", "chris_lockwood"),
                ("4945836", "david_evanetich"),
                ("1884456", "john_hughes"),
                ("846200", "lisa_bick"),
            ],
        }
    )

    @staticmethod
    def get_dict_of_teams_and_their_riders() -> dict[str, list[tuple[str, str]]]:
        return RepositoryOfTeamRosters._team_rosters_as_dict_of_list

    @staticmethod
    def get_IDs_of_riders_on_a_team(team_nickname: str) -> list[str]:
        """Zwift IDs in roster order, one per slot. A rider filling two slots appears twice."""
        if team_nickname in RepositoryOfTeamRosters._team_rosters_as_dict_of_list:
            return [zwift_id for zwift_id, _ in RepositoryOfTeamRosters._team_rosters_as_dict_of_list[team_nickname]]
        else:
            raise ValueError(
                f"Team '{team_nickname}' not found. Available teams: {list(RepositoryOfTeamRosters._team_rosters_as_dict_of_list.keys())}"
            )

    @staticmethod
    def get_unique_IDs_of_riders_on_a_team(team_nickname: str) -> list[str]:
        """Distinct Zwift IDs in order of first appearance on the roster."""
        return list(dict.fromkeys(RepositoryOfTeamRosters.get_IDs_of_riders_on_a_team(team_nickname)))

    @staticmethod
    def get_exertion_intensity_factor_for_team(team_nickname: str) -> float:
        if team_nickname in RepositoryOfTeamRosters._team_exertion_intensity_factors_as_dict:
            return RepositoryOfTeamRosters._team_exertion_intensity_factors_as_dict[team_nickname]
        else:
            raise ValueError(
                f"Team '{team_nickname}' not found. Available teams: {list(RepositoryOfTeamRosters._team_exertion_intensity_factors_as_dict.keys())}"
            )

    @staticmethod
    def get_rider_nick_name(team_nickname: str, zwift_id: str) -> str:
        if team_nickname in RepositoryOfTeamRosters._team_rosters_as_dict_of_list:
            team_roster = RepositoryOfTeamRosters._team_rosters_as_dict_of_list[team_nickname]
            for roster_zwift_id, nick_name in team_roster:
                if roster_zwift_id == zwift_id:
                    return nick_name
            raise ValueError(f"Zwift ID '{zwift_id}' not found in team '{team_nickname}'. Available IDs: {[i for i, _ in team_roster]}")
        else:
            raise ValueError(f"Team '{team_nickname}' not found. Available teams: {list(RepositoryOfTeamRosters._team_rosters_as_dict_of_list.keys())}")

