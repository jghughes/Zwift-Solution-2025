from enum import Enum
from typing import List, Tuple, Dict
import numpy as np

RIDERS_FILE_NAME = "everyone_in_club_ZsunRiderItems.json"


DATA_DIRPATH = "C:/Users/johng/source/repos/Zwift-Solution-2025/Zsun01/data/"


# POWER_CURVE_IN_PACELINE = np.array([350, 252, 236, 217], dtype=np.float64) #Follower's in the paceline are based on ZwiftInsider's power matrix.
POWER_CURVE_IN_PACELINE = np.array([350, 252, 236, 217, 202, 190, 180, 172], dtype=np.float64) #extras added arbitrarily by JGH to cater for more riders in the paceline. 

STANDARD_PULL_PERIODS_SEC_AS_LIST: list[float] = [0.0, 30.0, 60.0, 120.0, 180.0, 240.0, 300.0] # NB. the elements MUST BE IN ASCENDING ORDER. Standard pull periods (in seconds) for all pull planning N.B. be sure to list these from smallest to largest, otherwise the algorithms will not work correctly. The order of the pull periods is important for the logic that determines the best pull period for each rider. the elements in this array must be consistent with the specs in ZsunRiderItem, specifically the suite of methods def get_standard_30sec_pull_watts(..) e.t.c. and the method def get_standard_pull_watts(..).  Assuming 8 riders, I recommend max 5 pull periods, otherwise the solution space becomes too large and the algorithm takes too long to compute (more than a minute). The pull periods are in seconds, and they represent the time each rider spends at the front of the paceline during a ride. The first element (0.0) is included to represent the case where a rider does not take a pull. This function affected by STANDARD_PULL_PERIODS_SEC_AS_LIST produces the Cartesian product of the allowed pull periods for each rider. For n riders and k allowed pull periods, it generates k^n possible sequences. Each row in the returned array is a sequence of pull periods for the paceline. For instance, six pull periods and eight riders generates 6^8 = 1,679,616 possible sequences. This is a large number, but it is manageable for the algorithm to process within a reasonable time frame, especially with the filtering applied later in the process.

EXERTION_INTENSITY_FACTOR_LIMIT = 0.95 # maximum intensity factor for exertion of individuals in the paceline: 1.05 for Sirius. 0.95 for Betel

SAFE_LOWER_BOUND_KPH = 10.0 # let's conservatively assume 30 kph is the highest safe speed to launch the binary search. most TTT will be 35 - 55 kph. round lower bound to to 10 to be safe.

CHUNK_OF_KPH_PER_ITERATION = 5.0 # The speed is increased by this chunk in each iteration of the binary search. This is an arbitrary value chosen to ensure that the search progresses quickly enough to find a constraint-busting speed within the maximum number of iterations. It is not derived from any specific mathematical or domain-specific principle, but rather serves as a practical step size for the search algorithm.

SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND_KPH = 20 # the ample maximum number of attempts to find the upper bound for the binary search. This is empirically determined and may change with hardware and software improvements. The number is an arbitrary upper limit chosen to prevent the loop from running indefinitely in case a constraint-busting speed is never found. It acts as a safety net to avoid infinite loops.There is no mathematical or domain-specific reason for the value in this context. It is not derived from the number of riders, the range of speeds, or any other parameter. It is simply a "reasonable" number of attempts to find a speed that invalidates at least one rider's . 

REQUIRED_PRECISION_OF_SPEED = 0.01 # The desired precision for the speed binary search algorithm. This is the smallest difference in speed that we consider significant for the purpose of finding a constraint-busting speed. It is not derived from any specific mathematical or domain-specific principle, but rather serves as a practical threshold for determining when to halt the algorithm.

MAX_PERMITTED_ITERATIONS_TO_ACHIEVE_REQUIRED_PRECISION = 30 # Having applied SUFFICIENT_ITERATIONS_TO_GUARANTEE_FINDING_A_SAFE_UPPER_BOUND_KPH Maximum number of iterations for the binary search to find a constraint-busting speed. This is an arbitrary limit chosen to prevent the search from running indefinitely. It is not derived from any specific mathematical or domain-specific principle, but rather serves as a practical upper bound for the search algorithm. The algorithm typically takes 10 iterations when commencing from a safe starting base.



SERIAL_TO_PARALLEL_PROCESSING_THRESHOLD = 512 # Below this threshold, serial-processing is faster than parallel-processing.Above this threshold, parallel- processing is faster so that is what we use. The threshold is empirically determined and will be different on different machines. 

SOLUTION_FILTERING_THRESHOLD = 1024 # Somewhat arbirtary. A threshold for the number of alternative solutions we are willing to analyse by uncompromising brute force before we lose patience with the amount of time it is taking to compute. More than this and our strategy to limt the time is to apply a heuristic to prune the solution space. It is preferable to avoid filtering because filtering is a heuristic and all heuristics entail risk (albeit tiny in this case) that they will inadvertently exclude a winning solution. The Cartesian cross product of eight riders and six pull sequences generates a solution space of 1.7 million. By filtering, we prune these very nearly down to the SOLUTION_FILTERING_THRESHOLD. Compute time is about twenty seconds.

# SOLUTION CONFIGURATION STUFF

class PacelinePlanTypeEnum(Enum):
    THIRTY_SEC_PULL = "thirty_sec_pull"
    IDENTICAL_PULL = "identical_pull"
    BALANCED_INTENSITY = "balanced_intensity"
    EVERYBODY_PULL_HARD = "everybody_pull_hard"
    FASTEST = "fastest"
    LAST_FIVE = "last_five"
    LAST_FOUR = "last_four"

DISPLAY_ORDER_OF_CONSOLIDATED_PACELINE_PLANS = [
    PacelinePlanTypeEnum.THIRTY_SEC_PULL,
    PacelinePlanTypeEnum.IDENTICAL_PULL,
    PacelinePlanTypeEnum.BALANCED_INTENSITY,
    PacelinePlanTypeEnum.EVERYBODY_PULL_HARD,
    PacelinePlanTypeEnum.FASTEST,
    PacelinePlanTypeEnum.LAST_FIVE,
    PacelinePlanTypeEnum.LAST_FOUR,
]


LIST_OF_PACELINE_PLAN_TYPES_AND_CAPTIONS: List[Tuple[PacelinePlanTypeEnum, str, str]] = [
    (PacelinePlanTypeEnum.THIRTY_SEC_PULL,     "\n1. THIRTY-SECOND PULLS",            "everybody pulls for 30 seconds "),
    (PacelinePlanTypeEnum.IDENTICAL_PULL,      "\n2. IDENTICAL-PULLS",                "everybody pulls for same time "),
    (PacelinePlanTypeEnum.BALANCED_INTENSITY,  "\n3. NO-DROP BALANCED-WORKLOAD",      "everybody pulls "),
    (PacelinePlanTypeEnum.EVERYBODY_PULL_HARD, "\n4. NO-DROP PULL-HARD",              "everybody pulls "),
    (PacelinePlanTypeEnum.FASTEST,             "\n5. RACE - FULL-TEAM",            "some might tire or drop"),
    (PacelinePlanTypeEnum.LAST_FIVE,           "\n6. RACE - LAST-FIVE",            "some might tire or drop"),
    (PacelinePlanTypeEnum.LAST_FOUR,           "\n7. RACE - LAST-FOUR",            "some might tire or drop"),
]

DICT_OF_SAVE_FILE_NAMES_FOR_PACELINE_PLANS : Dict[PacelinePlanTypeEnum, str] = {
    PacelinePlanTypeEnum.THIRTY_SEC_PULL:    "1_everybody_does_thirty_second_pulls_plan.html",
    PacelinePlanTypeEnum.IDENTICAL_PULL:     "2_everybody_does_identical_pulls_plan.html",
    PacelinePlanTypeEnum.BALANCED_INTENSITY: "3_no_drop_balanced_workload_plan.html",
    PacelinePlanTypeEnum.EVERYBODY_PULL_HARD:"4_no_drop_pull_hard_plan.html",
    PacelinePlanTypeEnum.FASTEST:            "5_fastest_plan_for_full_team.html",
    PacelinePlanTypeEnum.LAST_FIVE:          "6_fastest_plan_for_last_five_riders.html",
    PacelinePlanTypeEnum.LAST_FOUR:          "7_fastest_plan_for_last_four_riders.html",
}

def get_save_filename_for_single_paceline_plan(team_name: str, plan_type: PacelinePlanTypeEnum) -> str:
    suffix = DICT_OF_SAVE_FILE_NAMES_FOR_PACELINE_PLANS.get(plan_type, "unknown_plan_type.html")
    answer = f"{team_name}_{suffix}"
    return answer


def get_caption_for_summary_of_all_paceline_plans(team_name: str) -> str:
    return f"TTT paceline plans for {team_name}"


def get_save_filename_for_summary_of_all_paceline_plans(team_name: str) -> str:
    return f"{team_name}_0_summary_of_all_paceline_plans.html"


FOOTNOTES = """
<div class="footnote">
    <div class="footnote-item"><sup>1</sup> Pull: Watts and duration for each rider's main pull. Higher ranking riders are prioritised for longer pulls and are located top and bottom of the paceline list, protecting weaker riders in the middle. Standard pulls range between 30 seconds and five minutes and corresponding pull capabilities are taken from a curve fitted to a rider's ZwiftPower data in their 3.5 - 20 minute window. Riders are not ranked according to zFTP, they are ranked according to how hard they can pull for one-minute.</div>
    <div class="footnote-item"><sup>2</sup> zFTP: Zwift Functional Threshold Power. zFTP metrics are displayed, but play no role in computations.</div>
    <div class="footnote-item"><sup>3</sup> NP: Normalized Power. Calculated from rolling-average watts using a five-second window.</div>
    <div class="footnote-item"><sup>4</sup> IF: Intensity factor. Intensity of effort measured in terms of normalised power divided by one-hour pulling capability. One-hour capability is taken from a curve fitted to a rider's ZwiftPower data in the 8 - 40-minute window and extrapolated to one hour. Sigma is the standard deviation of all IFs for the team. Smaller is superior.</div>
    <div class="footnote-item"><sup>5</sup> Limit: For ride plans where everybody pulls, the speed of the paceline is restricted to the available pulling capability of the weakest rider and the intensity of effort of the hardest-working rider. There is no protection for weaker or harder-working riders in other plans.</div>
</div>
"""

PACELINE_PLAN_SUMMARY_CSS_STYLE_SHEET = """
    <style>
        /* =========================================================================
           1. CSS Reset/Normalize
           -------------------------------------------------------------------------
           Removes default browser styling and ensures consistent box-sizing.
           ========================================================================= */
        html, body, div, span, applet, object, iframe,
        h1, h2, h3, h4, h5, h6, p, blockquote, pre,
        a, abbr, acronym, address, big, cite, code,
        del, dfn, em, img, ins, kbd, q, s, samp,
        small, strike, strong, sub, sup, tt, var,
        b, u, i, center,
        dl, dt, dd, ol, ul, li,
        fieldset, form, label, legend,
        table, caption, tbody, tfoot, thead, tr, th, td,
        article, aside, canvas, details, embed,
        figure, figcaption, footer, header, hgroup,
        menu, nav, output, ruby, section, summary,
        time, mark, audio, video {
            margin: 0;
            padding: 0;
            border: 0;
            font-size: 100%;
            font: inherit;
            vertical-align: baseline;
            box-sizing: border-box;
        }

        /* Ensures all elements and pseudo-elements use border-box sizing */
        *, *::before, *::after {
            box-sizing: inherit;
        }

        /* =========================================================================
           2. Base HTML Elements
           -------------------------------------------------------------------------
           Sets up base font, background, and color for the page and headings.
           ========================================================================= */
        body {
            font-family: 'Roboto Mono', 'Consolas', 'Menlo', 'Monaco', monospace;
            background: #fff;
            color: #222;
            margin: 0;
            padding: 1rem 2rem;
        }

        h1 {
            font-family: 'Roboto', Arial, sans-serif;
            font-size: 1.05em;
            font-weight: 700;
            color: #222;
            letter-spacing: 0.01em;
            margin: 0 0 1em 0;
        }

        /* =========================================================================
           3. Layout Containers
           -------------------------------------------------------------------------
           Styles for main containers and section separators.
           ========================================================================= */
        .table-container {
            width: 100%;
            max-width: 100vw;
            margin: 0 auto;
            overflow-x: auto; /* Enables horizontal scrolling for wide tables */
            padding: 0;
        }

        .section-separator {
            margin: 32px 0;
        }
        .section-separator:last-of-type {
            margin-bottom: 0.25em;
        }

        /* =========================================================================
           4. Component Classes - Table Styling
           -------------------------------------------------------------------------
           Styles for the main rider table and its elements.
           ========================================================================= */
        .rider-table {
            border-collapse: collapse;
            width: 100%;
            table-layout: auto;
            font-family: 'Roboto Mono', 'Consolas', 'Menlo', 'Monaco', monospace;
            font-size: 0.95em;
            border: 1px solid #b0b0b0;
        }

        .rider-table caption {
            /* Table caption styled as a heading above the table */
            caption-side: top;
            font-family: 'Roboto', Arial, sans-serif;
            font-size: 1.05em;
            font-weight: 700;
            color: #222;
            letter-spacing: 0.01em;
            text-align: left;
            margin-bottom: 0.50em;
        }

        .rider-table th,
        .rider-table td {
            font-size: 0.95em;
            padding: 6px 6px;
            white-space: nowrap;
            border: 1px solid #b0b0b0;
        }

        .rider-table th {
            background-color: #e6ecf5;
            font-weight: bold;
            text-align: center;
            border-bottom: 2px solid #444;
            letter-spacing: 0.02em;
        }

        .rider-table th.left-header,
        .rider-table td.left-header {
            text-align: left;
        }

        .rider-table th:nth-child(1),
        .rider-table td:nth-child(1),
        .rider-table th:nth-child(2),
        .rider-table td:nth-child(2) {
            /* Use proportional font for first two columns for readability */
            font-family: 'Roboto', Arial, sans-serif;
            font-weight: 400;
        }

        .rider-table tr:nth-child(even) td {
            background-color: #f7fafd; /* Zebra striping for rows */
        }

        .rider-table tr:hover td {
            background-color: #dbeafe; /* Highlight row on hover */
        }

        .rider-table td:nth-child(3),
        .rider-table td:nth-child(9) {
            /* Emphasize key numeric columns with right alignment and background */
            text-align: right;
            font-weight: bold;
            background-color: #f0f4fa;
        }

        .rider-table td:nth-child(4) {
            text-align: left;
        }

        .rider-table td:nth-child(n+5):nth-child(-n+8) {
            /* Right-align columns 5-8 (numeric data) */
            text-align: right;
        }

        /* =========================================================================
           5. Utility/Helpers
           -------------------------------------------------------------------------
           Styles for footnotes and other helper classes.
           ========================================================================= */
        .footnote {
            font-family: 'Roboto', Arial, sans-serif;
            font-size: 0.95em;
            font-weight: 500;
            color: #666;
            text-align: left;
            margin-top: 1.5em;
        }

        .footnote-item {
            margin-bottom: 0.5em;
            padding-left: 2em;
            text-indent: -2em; /* Hanging indent for footnote numbers */
        }

        .footnote-item:hover {
            background-color: #dbeafe;
            transition: background 0.2s;
            cursor: pointer;
        }

        .footnote sup, .rider-table th sup {
            font-size: 0.8em;
            vertical-align: super;
            font-weight: bold;
        }

        .summary-footnote {
            margin-top: 0.25em;
        }

        /* =========================================================================
           6. Media Queries
           -------------------------------------------------------------------------
           Responsive and print-specific styles for better usability on small screens
           and for printing. These are more sophisticated and ensure the table is
           readable on mobile and print-friendly.
           ========================================================================= */

        /* --- Mobile: Stack table rows and add data-labels for accessibility --- */
        @media (max-width: 600px) {
            .rider-table, .rider-table thead, .rider-table tbody, .rider-table th, .rider-table td, .rider-table tr {
                display: block;
                width: 100%;
            }
            .rider-table thead {
                display: none;
            }
            .rider-table tr {
                margin-bottom: 1em;
                border-bottom: 2px solid #ccc;
            }
            .rider-table td {
                text-align: right;
                padding-left: 50%;
                position: relative;
                min-height: 2.5em;
                border: none;
                border-bottom: 1px solid #eee;
                background: #fff;
            }
            .rider-table td::before {
                /* Shows the column name before each cell for accessibility */
                content: attr(data-label);
                position: absolute;
                left: 0;
                width: 50%;
                padding-left: 6px;
                font-weight: bold;
                text-align: left;
                color: #333;
                white-space: normal;
            }
        }

        /* --- Tablet: Slightly smaller font and padding --- */
        @media (max-width: 900px) {
            body {
                padding: 0.5rem 0.5rem;
            }
            .table-container {
                padding: 0;
            }
            .rider-table {
                font-size: 0.9em;
            }
        }

        /* --- Print: Optimized for paper, removes backgrounds, adjusts font sizes --- */
        @media print {
            body {
                background: #fff !important;
                color: #000 !important;
                margin: 0;
                padding: 0;
            }
            .table-container {
                overflow-x: visible !important;
                width: 100% !important;
                max-width: 100% !important;
                padding: 0 !important;
            }
            .rider-table {
                font-size: 10pt !important;
                width: 100% !important;
                page-break-inside: avoid;
            }
            .rider-table th,
            .rider-table td {
                padding: 4px 4px !important;
                white-space: normal !important;
                background: none !important;
                color: #000 !important;
            }
            .rider-table th {
                border-bottom: 1px solid #444 !important;
                background: #eee !important;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }
            .rider-table tr:nth-child(even) td,
            .rider-table tr:hover td {
                background: none !important;
            }
            .footnote,
            .footnote-item {
                color: #000 !important;
                background: none !important;
            }
            @page {
                size: A4 landscape;
                margin: 12mm 10mm 12mm 10mm;
            }
            .section-separator {
                page-break-before: always;
            }
        }
    </style>
    """

