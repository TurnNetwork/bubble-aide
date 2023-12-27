from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bubble_aide import Aide


class PrecompileContract:

    def __init__(self, aide: "Aide"):
        self.aide = aide


