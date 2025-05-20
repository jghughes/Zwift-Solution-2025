from typing import  List, Tuple, Union


# ZSUNBetelguese
barry_beck = '5490373' #ftp 273
brandi_steeve = "991817" #ftp 196
bryan_bumpas = "9011" #ftp 214
cory_cook = "5569057"
dave_konicek = "3147366" #ftp 276 critical_power 278
david_evanetich = '4945836'
giao_nguyen = "183277" #ftp 189
husky_crone = "5134" #ftp 268
john_hughes = '1884456' #ftp 240 zmap 292
josh_neil = '2508033' #ftp 260
lynsey_segal = '383480' #ftp 201
mark_brzezinski = '5530045' #ftp 280
matt_steeve = "1024413"
melissa_warwick = "1657744" #ftp 213
meridith_leubner = "1707548" #ftp 220
richard_mann = '1193' # ftp 200
scott_mcveigh = "11526" #ftp 247
selena_shaikh = "2682791" #ftp 214
steve_seiler = "6142432" #ftp 270
tim_reid = "5421258" #ftp 380
tom_bick = "11741" #ftp 303 critical_power 298

betelguese = [
    # barry_beck,
    # brandi_steeve,
    # bryan_bumpas,
    cory_cook,
    # dave_konicek,
    # david_evanetich,
    # giao_nguyen,
    # husky_crone,
    john_hughes,
    josh_neil,
    # lynsey_segal,
    # mark_brzezinski,
    # matt_steeve,
    melissa_warwick,
    # meridith_leubner,
    # richard_mann,
    # scott_mcveigh,
    # selena_shaikh,
    # steve_seiler,
    # tim_reid,
    tom_bick,
]

# ZSUNGiants
ceri_pritchard = "4204538"
colin_humphrey = "407780"
dave_konicek = "3147366" #ftp 276 critical_power 278
ed_bentley = "2449352"
eltjo_biemold = "106298"
ivan_parks = "2847282"
john_glass = "172221"
roy_roesthuis = "197937"
steve_james = "1662067"

giants = [
    ceri_pritchard,
    colin_humphrey,
    # dave_konicek,
    # ed_bentley,
    # eltjo_biemold,
    # ivan_parks,
    john_glass,
    roy_roesthuis,
    steve_james,
]

#ZSUNderFire
dave_konicek = "3147366"
gertjan_buisman = "1408923"
harrison_clark = "4348809"
james_veitch = "5959864"
rick_porteous = "2873877"
sjors_van_liempt = "2705238"
tom_bick = "11741"
xander_crawshaw = "2419188"

zsunderfire = [
    dave_konicek,
    gertjan_buisman,
    # harrison_clark,
    james_veitch,
    rick_porteous,
    sjors_van_liempt,
    tom_bick,
    # xander_crawshaw,
]

def get_teams():
    return {
        "betel": betelguese,
        "giants": giants,
        "underfire": zsunderfire,
    }

def get_team_IDs(team_name :str) -> List[str]:
    teams = get_teams()
    if team_name in teams:
        return teams[team_name]
    else:
        raise ValueError(f"Team '{team_name}' not found. Available teams: {list(teams.keys())}")
