"""Tab registry.

Each tab is a module exposing a uniform interface so the app can render them
generically. To add a tab: create a module with the attributes below and append
it to :data:`TABS` -- nothing else in the app needs to change.

Tab module interface:
    * ``TAB_LABEL`` (str): text shown on the tab button.
    * ``TAB_VALUE`` (str): unique id used to select the tab.
    * ``layout() -> Component``: builds the tab's content.
    * ``register_callbacks(app) -> None``: registers the tab's callbacks.
"""

from __future__ import annotations

from typing import Protocol

from dash import Dash
from dash.development.base_component import Component

from . import ks_tab, umap_tab


class TabModule(Protocol):
    """Structural type every tab module must satisfy."""

    TAB_LABEL: str
    TAB_VALUE: str

    def layout(self) -> Component:
        """Return the tab's content."""
        ...

    def register_callbacks(self, app: Dash) -> None:
        """Register the tab's callbacks on the app."""
        ...


# Order here is the order the tabs appear in the UI.
TABS: list[TabModule] = [umap_tab, ks_tab]
