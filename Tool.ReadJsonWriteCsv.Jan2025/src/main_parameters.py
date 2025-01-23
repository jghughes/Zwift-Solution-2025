from typing import Dict, List

your_excel_column_headers: Dict[str, str] = {
    "Region": "01 Region",
    "Category": "02 Category",
    "Team": "03 Team",
    "Rider": "04 Rider",
    "Rank by Points": "05 Rank by Points",
    "Riders in Race": "06 Riders in Race",
    "Finishing Position": "07 Finishing Position",
    "Rank in Segments": "08 Rank in Segments",
    "FAL Points": "09 FAL Points",
    "FTS Points": "10 FTS Points",
    "FAL + FTS Points": "11 FAL + FTS Points",
    "Finishing Points": "12 Finishing Points",
    "Podium Bonus Points": "13 Podium Bonus Points",
    "Total Points": "14 Total Points",
    "Finish Time": "15 Finish Time",
    "W/Kg": "16 W/Kg",
    "Watts": "17 Watts",
    "Distance": "18 Distance",
    "Gap": "19 Gap",
    "DQ": "20 DQ",
    "DQ Code": "21 DQ Code",
    "Open/Womens": "22 Open/Womens",
}

your_excel_column_shortlist: List[str] = {
    "Region",
    "Category",
    "Team",
    "Rider",
    # "Rank by Points": "05 Rank by Points",
    # "Riders in Race": "06 Riders in Race",
    # "Finishing Position": "07 Finishing Position",
    # "Rank in Segments": "08 Rank in Segments",
    # "FAL Points": "09 FAL Points",
    # "FTS Points": "10 FTS Points",
    # "FAL + FTS Points": "11 FAL + FTS Points",
    # "Finishing Points": "12 Finishing Points",
    # "Podium Bonus Points": "13 Podium Bonus Points",
    # "Total Points",
    # "Finish Time",
    # "W/Kg": "16 W/Kg",
    # "Watts": "17 Watts",
    # "Distance": "18 Distance",
    # "Gap": "19 Gap",
    # "DQ": "20 DQ",
    # "DQ Code": "21 DQ Code",
    # "Open/Womens": "22 Open/Womens"
}

# file paths
your_input_filename: str = (
    "season-15-race-5-reportzrl-season-15-race-5-rider-performance.json"
)
your_output_filename: str = (
    "season-15-race-5-reportzrl-season-15-race-5-rider-performance.csv"
)
your_input_dirpath: str = (
    "C:/Users/johng/holding_pen/StuffForZsun/DaveKoniekZRLwebsiteData/RawFromWebsite"
)
your_output_dirpath: str = (
    "C:/Users/johng/holding_pen/StuffForZsun/DaveKoniekZRLwebsiteData/ProcessedByPython"
)

# your_input_filename: str = "skinnykeyDictionary.json"
# your_output_filename: str = "skinnykeyDictionary.csv"
# your_input_filename: str = "skinnykeyList.json"
# your_output_filename: str = "skinnykeyList.csv"
# your_input_dirpath: str = "C:/Users/johng/holding_pen/StuffForZsun/Keys"
# your_output_dirpath: str = "C:/Users/johng/holding_pen/StuffForZsun/Keys"
