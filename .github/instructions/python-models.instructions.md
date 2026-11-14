---
applyTo: "Zsun.DataModels.Jan2024/**/*.py"
---

# Domain models (Python)

Applies only to the domain-model project. The repository-wide rules in `copilot-instructions.md` still apply.

- A domain model is a `@dataclass` named `<Name>Item` with defaulted, fully typed fields.
- Each item that has a DTO exposes two static converters, `to_dataTransferObject` and `from_dataTransferObject`.
  Both accept `None` and return a default-constructed result instead of raising.
  See `my_models/simple_rider_item.py` for the pattern.
- Items depend on DTOs (import the `*DTO` class); DTOs never import items.
- Keep conversion logic in the converters; do not put I/O or Azure calls in models.
