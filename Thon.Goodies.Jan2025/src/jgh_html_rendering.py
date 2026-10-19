"""
Generic HTML template rendering built on Jinja2 (double-brace syntax: {{ name }}).

This module knows nothing about any particular application. The caller owns the
templates and the folder they live in, supplies a model (a dataclass or a mapping)
whose fields are the template variables, and gets back a string.

Autoescape is on by default. Values are HTML-escaped unless the template marks them
as already-safe HTML, e.g. {{ table_html | safe }}. Use `| safe` for pre-rendered HTML,
CSS and similar trusted fragments only.

Example:
    renderer = HtmlTemplateRenderer(Path("templates"))
    html = renderer.render("page.html", PageModel(title="Hello", body_html="<p>Hi</p>"))
"""
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any, Mapping

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from jgh_path_helpers import throw_if_dirpath_invalid_or_not_exists


class HtmlTemplateRenderer:
    """
    Renders named HTML templates from a single template directory.

    Construct once and reuse. Jinja2 caches compiled templates inside the instance.
    A template that references a variable missing from the model raises an error
    rather than silently rendering an empty string.
    """

    def __init__(
        self,
        template_dirpath: Path,
        *,
        autoescape: bool = True,
        trim_blocks: bool = True,
        lstrip_blocks: bool = True,
    ) -> None:
        throw_if_dirpath_invalid_or_not_exists(template_dirpath)
        self._environment = Environment(
            loader=FileSystemLoader(str(template_dirpath)),
            autoescape=select_autoescape(["html", "htm", "xml"]) if autoescape else False,
            trim_blocks=trim_blocks,
            lstrip_blocks=lstrip_blocks,
            undefined=StrictUndefined,
        )

    def render(self, template_name: str, model: Any) -> str:
        """
        Render the named template with the model's fields as template variables.

        `model` may be a dataclass instance or a mapping. Raises TypeError for anything else,
        and jinja2.TemplateNotFound if the template does not exist in the template directory.
        """
        return self._environment.get_template(template_name).render(**_model_to_context(model))


def _model_to_context(model: Any) -> Mapping[str, Any]:
    # Shallow conversion: dataclasses.asdict() would deep-copy every field,
    # which is wasteful for models holding large pre-rendered HTML strings.
    if isinstance(model, Mapping):
        return model
    if is_dataclass(model) and not isinstance(model, type):
        return {f.name: getattr(model, f.name) for f in fields(model)}
    raise TypeError(f"Template model must be a dataclass instance or a mapping, not {type(model).__name__}.")