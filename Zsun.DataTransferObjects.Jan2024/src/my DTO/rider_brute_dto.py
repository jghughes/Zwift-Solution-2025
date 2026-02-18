from typing import List, Dict, Any
from pydantic import BaseModel, RootModel
from pydantic import BaseModel, AliasChoices, ConfigDict, AliasGenerator, field_validator

validation_alias_choices_map: dict[str, AliasChoices] = {
	"row"									:	AliasChoices("row"),
	"zwift_id"								:	AliasChoices("zwift_id", "zwiftId"),
	"zwift_country_code3"					:	AliasChoices("zwift_country_code3", "zwiftCountry3"),
	"name_racingapp"						:	AliasChoices("name_racingapp", "veloName"),
	"zwift_age_years"						:	AliasChoices("zwift_age_years", "zwiftAgeYears"),
	"zwift_height_cm"						:	AliasChoices("zwift_height_cm", "zwiftHeightCm"),
	"zwift_weight_kg"						:	AliasChoices("zwift_weight_kg", "zwiftWeightKg"),
	"zwift_gender"							:	AliasChoices("zwift_gender", "zwiftGenderCode"),
	"zwift_cat_open"						:	AliasChoices("zwift_cat_open", "zwiftCatOpen"),
	"zwift_cat_women"						:	AliasChoices("zwift_cat_women", "zwiftCatWomen"),
	"zwift_racing_score"					:	AliasChoices("zwift_racing_score", "zwiftRacingScore"),
	"zwift_FTP_watts"						:	AliasChoices("zwift_FTP_watts", "zwiftFTPWatts"),
	# "zwiftpower_zftp_watts"					:	AliasChoices("zwiftpower_zftp_watts", "zwiftpowerZFTPWatts	"),
	"velo_zwiftpower_zFTP_watts"			:	AliasChoices("velo_zwiftpower_zFTP_watts", "veloZwiftpowerZFTPWatts"),
	"velo_cat_num_30_days"					:	AliasChoices("velo_cat_num_30_days", "veloCatNum30Days"),
	"velo_rating_30_days"					:	AliasChoices("velo_rating_30_days", "veloRating30Days"),
	"velo_cat_name_30_days"					:	AliasChoices("velo_cat_name_30_days", "veloCatName30Days"),
	"velo_age_group"						:	AliasChoices("velo_age_group", "veloAgeGroup"),
	"jgh_60_min_watts"						:	AliasChoices("jgh_60_min_watts", "60minWattsCurveFit"),
	"jgh_60_min_curve_coefficient"			:	AliasChoices("jgh_60_min_curve_coefficient", "60minCurveCoefficient"),
	"jgh_60_min_curve_exponent"				:	AliasChoices("jgh_60_min_curve_exponent", "60minCurveExponent"),
	"jgh_ttt_pull_curve_coefficient"		:	AliasChoices("jgh_ttt_pull_curve_coefficient", "tttPullCurveCoefficient"),
	"jgh_ttt_pull_curve_exponent"			:	AliasChoices("jgh_ttt_pull_curve_exponent", "tttPullCurveExponent"),
	"jgh_ttt_pull_curve_fit_r_squared"		:	AliasChoices("jgh_ttt_pull_curve_fit_r_squared", "tttPullCurveFitRSquared"),
	"jgh_when_curves_fitted"				:	AliasChoices("jgh_when_curves_fitted", "jghWhenCurvesFitted"),
}

configdictV1 = ConfigDict(alias_generator=AliasGenerator(
    alias=None,
    validation_alias=lambda field_name: validation_alias_choices_map.get(field_name, field_name)))

preferred_config_dict = configdictV1


class RiderBruteDTO(BaseModel):
	model_config	=	preferred_config_dict
	row										:	int						=	0
	zwift_id								:	str					=	""
	name_racingapp							:	str						=	""
	zwift_country_code3						:	str						=	""
	zwift_age_years							:	float					=	0.0
	zwift_height_cm							:	float					=	0.0
	zwift_weight_kg							:	float					=	0.0
	zwift_gender							:	str						=	""
	zwift_cat_open							:	str						=	""
	zwift_cat_women							:	str						=	""
	zwift_racing_score						:	float					=	0.0
	zwift_FTP_watts							:	float					=	0.0
	# zwiftpower_zftp_watts					:	float					=	0.0
	velo_zwiftpower_zFTP_watts				:	float					=	0.0
	velo_cat_num_30_days					:	int						=	0
	velo_rating_30_days						:	float					=	0.0
	velo_cat_name_30_days					:	str						=	""
	velo_age_group							:	str						=	""
	jgh_60_min_watts						:	float					=	0.0
	jgh_60_min_curve_coefficient			:	float					=	0.0
	jgh_60_min_curve_exponent				:	float					=	0.0
	jgh_ttt_pull_curve_coefficient			:	float					=	0.0
	jgh_ttt_pull_curve_exponent				:	float					=	0.0
	jgh_ttt_pull_curve_fit_r_squared		:	float					=	0.0
	jgh_when_curves_fitted					:	str						=	""

	# Validator for zwift_id to convert int to string
	@field_validator("zwift_id", mode="before")
	def convert_int_to_str(cls, value : Any):
		if isinstance(value, int):
			return str(value)
		return value

class RiderBruteDtoDictModel(RootModel[Dict[str, RiderBruteDTO]]):
    pass

class RiderBruteDtoListModel(RootModel[List[RiderBruteDTO]]):
    pass
