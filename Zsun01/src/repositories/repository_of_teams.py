from typing import  List
from collections import defaultdict
from typing import List, Dict
from collections import defaultdict

def get_teams() -> Dict[str, defaultdict[str, str]]:
    return {
        "betel": betelguese_Roster,
        "sirius": sirius_Roster,
        "giants": giants_Roster,
        "fire": zsunderfire_Roster,
        "kissed": sunkissed_Roster,
    }

def get_team_riderIDs(team_name: str) -> List[str]:
    teams = get_teams()
    if team_name in teams:
        return list(teams[team_name].keys())
    else:
        raise ValueError(f"Team '{team_name}' not found. Available teams: {list(teams.keys())}")

def get_rider_name_by_zwiftID(zwiftID: str) -> str:
    teams = get_teams()
    for roster in teams.values():
        if zwiftID in roster:
            return roster[zwiftID]
    return ""

betelguese_Roster = defaultdict(
    str,
    {
        # "5490373": "barry_beck",
        # "991817": "brandi_steeve",
        # "9011": "bryan_bumpas",
        # "5569057": "cory_cook",
        # "3147366": "dave_konicek",
        "4945836": "david_evanetich",
        # "183277": "giao_nguyen",
        # "5134": "husky_crone",
        "1884456": "john_hughes",
        "2508033": "josh_neil",
        "383480": "lynsey_segal",
        # "5530045": "mark_brzezinski",
        # "1024413": "matt_steeve",
        "1657744": "melissa_warwick",
        "1707548": "meridith_leubner",
        # # "1193": "richard_mann",
        # "384442": "roland_segal",
        # "11526": "scott_mcveigh",
        # "1956": "scott_yarosh",
        # "2682791": "selena_shaikh",
        # "6142432": "steve_seiler",
        # "5421258": "tim_reid",
        # "11741": "tom_bick",
    }
)

sirius_Roster = defaultdict(
    str,
    {
        "5490373": "barry_beck",
        "9011": "bryan_bumpas",
        "5569057": "cory_cook",
        "3147366": "dave_konicek",
        "5134": "husky_crone",
        # "1884456": "john_hughes",
        # "383480": "lynsey_segal",
        "1657744": "melissa_warwick",
        "1707548": "meridith_leubner",
        # "11526": "scott_mcveigh",
        # "1956": "scott_yarosh",
        # "5421258": "tim_reid",
        # "11741": "tom_bick",
    }
)

giants_Roster = defaultdict(
    str,
    {
        "4204538": "ceri_pritchard",
        "407780": "colin_humphrey",
        "3147366": "dave_konicek",
        "2449352": "ed_bentley",
        "106298": "eltjo_biemold",
        "2847282": "ivan_parks",
        "172221": "john_glass",
        "197937": "roy_roesthuis",
        # "1662067": "steve_james",
    }
)

zsunderfire_Roster = defaultdict(
    str,
    {
        "3147366": "dave_konicek",
        "1408923": "gertjan_buisman",
        "4348809": "harrison_clark",
        "5959864": "james_veitch",
        "2873877": "rick_porteous",
        "2705238": "sjors_van_liempt",
        "11741": "tom_bick",
        "2419188": "xander_crawshaw",
    }
)

sunkissed_Roster = defaultdict(
    str,
    {
        "383480": "lynsey_segal",
        "": "j_daniell",
        "": "j_de_vries",
        "": "z_mackay",
        "": "c_williams",
    }
)

