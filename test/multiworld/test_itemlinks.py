
from unittest import TestCase

from BaseClasses import MultiWorld
from worlds.AutoWorld import AutoWorldRegister
from ..general import gen_steps, setup_multiworld


class ItemLinkTestBase(TestCase):
    multiworld: MultiWorld


class TestTwoPlayerItemLink(ItemLinkTestBase):
    def test_defaults(self) -> None:
        """Tests that the ItemLink Defaults are set correctly."""
        # Prepare
        for world in AutoWorldRegister.world_types.values():
            if not ("Progression Items" in world.item_name_groups.keys()):
                continue    # We only run this test on worlds that have a "Progression Items" group

            self.multiworld = setup_multiworld([world, world], ())
            
            self.multiworld.calculate_item_links()
        # Act

        # Assert