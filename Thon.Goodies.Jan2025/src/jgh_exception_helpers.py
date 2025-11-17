from typing import  Dict, Any
from typing import Any, Dict

def flatten_dict(
    d: Dict[str, Any], 
    parent_key: str = '', 
    sep: str = '.'
) -> Dict[str, Any]:
    """
    Recursively flattens a nested dictionary into a single-level dictionary.

    Nested keys are concatenated into a single string, separated by the specified delimiter.
    This is useful for serializing or logging complex, nested data structures.

    Args:
        d (Dict[str, Any]): The dictionary to flatten.
        parent_key (str, optional): The base key to prepend to each key. Defaults to ''.
        sep (str, optional): Separator to use between concatenated keys. Defaults to '.'.

    Returns:
        Dict[str, Any]: A flat dictionary with compound keys representing the original nested structure.

    Example:
        >>> flatten_dict({'a': {'b': 1, 'c': 2}, 'd': 3})
        {'a.b': 1, 'a.c': 2, 'd': 3}
    """
    items: Dict[str, Any] = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items

def traverse_deepest_exception(exc: Exception) -> tuple[str, str]:
    """
    Traverses an exception chain to find the deepest (most nested) exception.

    The function follows attributes commonly used for exception chaining:
    - 'inner_exception' (custom attribute)
    - '__cause__' (PEP 3134)
    - '__context__' (PEP 3134)

    Returns the message and the location (filename and line number) of the deepest exception.
    If traceback information is unavailable, location is set to "Unknown".

    Args:
        exc (Exception): The exception to traverse.

    Returns:
        tuple[str, str]: A tuple containing the exception message and its location as "filename:lineno".
    """ 
    visited = set()
    deepest = exc
    while deepest:
        if id(deepest) in visited:
            break
        visited.add(id(deepest))
        next_exc = getattr(deepest, "inner_exception", None)
        if next_exc and next_exc is not deepest:
            deepest = next_exc
        elif getattr(deepest, "__cause__", None):
            deepest = deepest.__cause__
        elif getattr(deepest, "__context__", None):
            deepest = deepest.__context__
        else:
            break
    message = getattr(deepest, "message", str(deepest)) if deepest else ""
    tb = getattr(deepest, "__traceback__", None)
    if tb:
        while tb.tb_next:
            tb = tb.tb_next
        filename = tb.tb_frame.f_code.co_filename
        lineno = tb.tb_lineno
        location = f"{filename}:{lineno}"
    else:
        location = "Unknown"
    return message, location

def describe_exception(exc: Exception) -> str:
    message, location = traverse_deepest_exception(exc)
    return f"Message: {message} Location: {location}"

