
from unittest import TestCase

from BaseClasses import MultiWorld
from worlds.AutoWorld import AutoWorldRegister
from ..general import setup_multiworld

class ItemLinkTestBase(TestCase):
    multiworld: MultiWorld


class TestTwoPlayerItemLink(ItemLinkTestBase):
    def test_defaults(self) -> None:
        """Tests that the ItemLink Defaults are set correctly."""
        # Prepare
        for world in AutoWorldRegister.world_types.values():
            self.multiworld = setup_multiworld([world, world], ())
            


        # Act

        # Assert