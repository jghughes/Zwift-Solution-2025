"""
Renders paceline plan reports as HTML using Jinja2 templates.

The HTML lives in the templates folder next to this module:
	templates/one_page_summary.html        - the complete page
	templates/paceline_plan_fragment.html  - one plan: captions, rider table, optional footnotes

This module only prepares the data (the models below) and calls the generic
HtmlTemplateRenderer from jgh_html_rendering. It does no file saving or uploading.
"""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import List

import pandas as pd

from jgh_html_rendering import HtmlTemplateRenderer
from jgh_read_write import read_text_from_path
from jgh_enums import PacelinePlanTypeEnum
from paceline_display_objects import (
	PacelineComputationReportDisplayObject,
	PackageOfPacelineComputationReportDisplayObject,
)
from storage_config import (
	FILEPATH_OF_PACELINE_PLAN_SUMMARY_CSS,
	FILEPATH_OF_PACELINE_PLAN_FOOTNOTES_HTML,
)

TEMPLATE_DIRPATH = Path(__file__).parent / "templates"
TEMPLATE_NAME_ONE_PAGE_SUMMARY = "one_page_summary.html"
TEMPLATE_NAME_PLAN_FRAGMENT = "paceline_plan_fragment.html"

DISPLAY_ORDER_OF_PACELINE_PLANS: List[PacelinePlanTypeEnum] = [
	PacelinePlanTypeEnum.THIRTY_SEC_PULL,
	PacelinePlanTypeEnum.SIXTY_SEC_PULL,
	PacelinePlanTypeEnum.BALANCED_INTENSITY,
	PacelinePlanTypeEnum.EVERYBODY_PULL_HARD,
	PacelinePlanTypeEnum.FASTEST,
	PacelinePlanTypeEnum.FASTEST_STRONGEST_FIVE,
	PacelinePlanTypeEnum.FASTEST_STRONGEST_FOUR,
]

RIDER_TABLE_COLUMN_HEADERS: List[str] = [
	"#",
	"Name<sup>1,2</sup>",
	"Race Cat",
	"Pull<sup>3</sup>",
	"pull 2nd 3rd 4th",
	"zFTP v pull<sup>4</sup>",
	"Ave power",
	"NP<sup>5</sup>",
	"IF<sup>6</sup>",
	"Limit<sup>7</sup>",
]


# ===========================
# Template models. Field names are the variable names used in the templates.
# ===========================

@dataclass(frozen=True)
class PacelinePlanFragmentModel:
	caption_left: str
	caption_right: str
	table_html: str
	footnotes_html: str = ""
	css: str = ""  # leave empty when the fragment is embedded in a page that already has the css


@dataclass(frozen=True)
class OnePageSummaryModel:
	title: str
	css: str
	footnotes_html: str
	plan_fragments: List[str]


# ===========================
# Helpers
# ===========================

@lru_cache(maxsize=1)
def _get_renderer() -> HtmlTemplateRenderer:
	return HtmlTemplateRenderer(TEMPLATE_DIRPATH)


@lru_cache(maxsize=None)
def _read_asset_text(filepath: str) -> str:
	return read_text_from_path(Path(filepath))


def _make_rider_table_html(plan_report: PacelineComputationReportDisplayObject) -> str:
	rows_of_data: List[List[object]] = [
		[
			z.index,
			rider.name,
			z.pretty_concatenated_racing_cat_descriptor,
			z.pretty_pull,
			z.pretty_p1_2_3_4_w,
			z.pretty_pull_comparison,
			z.pretty_average_watts,
			z.pretty_normalised_power_watts,
			z.pretty_intensity_factor,
			z.pretty_effort_constraint_violation_reason,
		]
		for rider, z in plan_report.rider_contributions_display_objects.items()
	]
	df = pd.DataFrame(rows_of_data, columns=RIDER_TABLE_COLUMN_HEADERS)
	return df.to_html(
		index=False,
		border=1,
		classes=["rider-table"],
		escape=False,  # the column headers contain <sup> markup
	)


# ===========================
# Public functions
# ===========================

def format_single_paceline_plan_as_html_fragment(
	plan_report: PacelineComputationReportDisplayObject,
	html_footnotes: str = "",
	css: str = "",
) -> str:
	"""
	Render one plan as an HTML fragment (no <html> or <head>). Pass css only for a standalone fragment.
	"""
	model = PacelinePlanFragmentModel(
		caption_left   = plan_report.display_caption_left_aligned,
		caption_right  = plan_report.display_caption_right_aligned,
		table_html     = _make_rider_table_html(plan_report),
		footnotes_html = html_footnotes,
		css            = css,
	)
	return _get_renderer().render(TEMPLATE_NAME_PLAN_FRAGMENT, model)


def format_paceline_plans_as_one_page_html_doc(
	package_report_displayobject: PackageOfPacelineComputationReportDisplayObject,
) -> str:
	"""
	Render all plans in the package as one complete HTML page. The css and footnotes
	are read from the files named in storage_config.
	"""
	plan_fragments = [
		format_single_paceline_plan_as_html_fragment(solution)
		for plan_type in DISPLAY_ORDER_OF_PACELINE_PLANS
		if (solution := package_report_displayobject.solutions[plan_type]).rider_contributions_display_objects
	]
	model = OnePageSummaryModel(
		title          = package_report_displayobject.caption,
		css            = _read_asset_text(FILEPATH_OF_PACELINE_PLAN_SUMMARY_CSS),
		footnotes_html = _read_asset_text(FILEPATH_OF_PACELINE_PLAN_FOOTNOTES_HTML),
		plan_fragments = plan_fragments,
	)
	return _get_renderer().render(TEMPLATE_NAME_ONE_PAGE_SUMMARY, model)
