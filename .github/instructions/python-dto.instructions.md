---
applyTo: "Zsun.DataTransferObjects.Jan2024/**/*.py"
---

# Data transfer objects (Python)

Applies only to the DTO project. The repository-wide rules in `copilot-instructions.md` still apply.

- A DTO is a Pydantic v2 `BaseModel` named `<Name>DTO`, holding plain serialisable fields with defaults.
- Accept alternative incoming field names with `AliasChoices` through the module's
  `validation_alias_choices_map` and `AliasGenerator`; keep the Python field name first in each `AliasChoices`.
  See `my_DTO/team_member_dto.py` for the pattern.
- Wrap collections in `RootModel[...]` classes named `<Name>DtoDictModel` / `<Name>DtoListModel`.
- Use `@field_validator(..., mode="before")` for input coercion (for example int to str) and annotate the value as `Any`.
- DTOs must not import from the domain-model project (`Zsun.DataModels.Jan2024`); the dependency points the other way.
- Renaming a field is a cross-project change: update the matching `*Item` class and its
  `to_dataTransferObject` / `from_dataTransferObject` converters in the same change.
