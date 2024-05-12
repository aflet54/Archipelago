from BaseClasses import ItemClassification, MultiWorld
from Fill import distribute_items_restrictive
from Options import Accessibility, ItemLinks
from test.multiworld.test_multiworlds import MultiworldTestBase
from worlds.AutoWorld import AutoWorldRegister, call_all
from worlds.generic import GenericWorld
from ..general import setup_multiworld

pre_link_steps = ("generate_early", "create_regions", "create_items", "set_rules", "generate_basic")

class ItemLinkTestBase(MultiworldTestBase):
    multiworld: MultiWorld

    def get_partial_world_items(self, world : GenericWorld) -> list[str]:
        """Returns a list of items that are in the itempool of a world and considered progression."""
        item_list = []
        complete_item_list = world.item_name_groups["Everything"]
        for item in self.multiworld.itempool:
            if item.name in complete_item_list and item.classification == ItemClassification.progression:
                item_list.append(item.name)
            # if len(item_list) >= size:
            #     break
        return item_list

class TestTwoPlayerItemLink(ItemLinkTestBase):
    def test_itemlink_default(self) -> None:
        """Tests that various combinations of settings are loaded correctly"""
        pass

    
    def test_all_games_items_link(self) -> None:
        """Tests that all worlds are able to link items to each other in a multiworld."""
        # Prepare
        for world in AutoWorldRegister.world_types.values():
            with self.subTest(game=world.game):
                self.multiworld = setup_multiworld([world, world], pre_link_steps)
                linked_items = self.get_partial_world_items(world)
                
                for world in self.multiworld.worlds.values():
                    world.options.accessibility.value = Accessibility.option_locations
                    world.options.item_links = ItemLinks([{'name': 'ItemLinkTest', 'item_pool' : linked_items, 'replacement_item' : None, 'link_replacement' : None}])
                
                world_items = {}
                for player in range(1, self.multiworld.players+1):
                    world_items[player] = [item for item in self.multiworld.itempool if item.player == player]

                # Act
                prior_item_count = len(self.multiworld.itempool)
                self.multiworld.set_item_links()
                self.multiworld.calculate_item_links()
                # Assert Link was created and contains items
                self.assertTrue(any(group['name'] == "ItemLinkTest" for group in self.multiworld.groups.values()), f"ItemLinkTest group not found in {self.multiworld.groups}")
                link_group = [group for group in self.multiworld.groups.values() if group['name'] == "ItemLinkTest"][0]
                self.assertEqual(link_group['game'], world.game, f"Game is not set correctly for {world.game}")
                self.assertEqual(link_group['item_pool'], set(linked_items), f"Item pool is not set correctly for {world.game}")
                self.assertEqual(len(self.multiworld.itempool), prior_item_count, f"ItemPool length should stay the same")
                for player in range(1, self.multiworld.players+1):
                    new_world_items = [item for item in self.multiworld.itempool if item.player == player]
                    self.assertLessEqual(len(new_world_items), len(world_items[player]), f"Item count for each player should be the same or less. We have {len(linked_items)} linked items")
                # Assert Items are linked
                for world in self.multiworld.worlds.values():
                    for item in linked_items:
                        self.assertEqual(world.item_links[item], link_group['replacement_item'], f"Item {item} is not linked correctly in {world.game}")
                        self.assertEqual(world.link_replacements[link_group['replacement_item']], link_group['link_replacement'], f"Link replacement is not set correctly in {world.game}")
            