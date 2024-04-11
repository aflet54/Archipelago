
from unittest import TestCase

from BaseClasses import MultiWorld
from Options import ItemLinks
from worlds.AutoWorld import AutoWorldRegister
from worlds.generic import GenericWorld
from ..general import gen_steps, setup_multiworld


class ItemLinkTestBase(TestCase):
    multiworld: MultiWorld

    def get_partial_world_items(self, world : GenericWorld, size: int = 5) -> list[str]:
        size = min(size, len(world.item_name_groups["Everything"]))
        item_list = list(world.item_name_groups["Everything"])
        
        return item_list[:size]

class TestTwoPlayerItemLink(ItemLinkTestBase):
    def test_all_games_items_link(self) -> None:
        """Tests that the ItemLink Defaults are set correctly."""
        # Prepare
        for world in AutoWorldRegister.world_types.values():
            linked_items = self.get_partial_world_items(world)

            self.multiworld = setup_multiworld([world, world], gen_steps)
            for world_id, world_data in self.multiworld.worlds.items():
                world_data.options.item_links = ItemLinks([{'name': 'ItemLinkTest', 'item_pool' : linked_items, 'replacement_item' : None, 'link_replacement' : None}])
                self.multiworld.worlds[world_id] = world_data
            
        # Act
            self.multiworld.set_item_links()
            self.multiworld.calculate_item_links()
        # Assert
            self.assertTrue(any(group['name'] == "ItemLinkTest" for group in self.multiworld.groups.values()))
            
