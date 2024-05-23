import copy
import typing
from BaseClasses import ItemClassification, MultiWorld
# from Fill import distribute_items_restrictive
from Options import Accessibility, ItemLinks
from test.multiworld.test_multiworlds import MultiworldTestBase
from worlds.AutoWorld import AutoWorldRegister, World
# from worlds.generic import GenericWorld
from ..general import setup_multiworld

pre_link_steps = ("generate_early", "create_regions", "create_items", "set_rules", "generate_basic")

edge_cases = [
    {
        'Description': 'Only items present in both Links should be shared',
        'Game': 'Hollow Knight',
        'LinkOne': {
            'name': 'ItemLinkTest', 
            'item_pool': ['Mothwing_Cloack', 'Mantis_Claw', 'Crystal_Heart', 
                           'Monarch_Wings', 'Shade_Cloak', 'Isma\'s_Tear'], 
            'replacement_item': None, 
            'link_replacement': None,
        },
        'LinkTwo': {
            'name': 'ItemLinkTest', 
            'item_pool': ['Mothwing_Cloack', 'Mantis_Claw', 'Crystal_Heart', 
                           'Dream_Nail', 'Dream_Gate', 'Awoken_Dream_Nail'], 
            'replacement_item': None, 
            'link_replacement': None,
        },
        'ExpectedLinkedItems': set(['Mothwing_Cloack', 'Mantis_Claw', 'Crystal_Heart']),
    },
]

class ItemLinkTestBase(MultiworldTestBase):
    multiworld: MultiWorld

    def get_progression_items(self, world : typing.Type[World]) -> typing.List[str]:
        """Returns a list of items that are in the itempool of a world and considered progression."""
        item_list = []
        complete_item_list = world.item_name_groups["Everything"]
        for item in self.multiworld.itempool:
            if item.name in complete_item_list and \
                item.classification == ItemClassification.progression:
                item_list.append(item.name)
            # if len(item_list) >= size:
            #     break
        return item_list


class TestTwoPlayerItemLink(ItemLinkTestBase):
    def test_itemlink_edge_cases(self) -> None:
        """Tests that various combinations of settings are loaded correctly"""
        for case in edge_cases:
            with self.subTest(game=case['Game'], description=case['Description']):
                # Prepare
                worldBase = AutoWorldRegister.world_types[case['Game']]
                worldOne = copy.deepcopy(worldBase) # Create our test worlds
                worldOne.options.item_links = ItemLinks([case['LinkOne']])
                worldTwo = copy.deepcopy(worldBase)
                worldTwo.options.item_links = ItemLinks([case['LinkTwo']])
                self.multiworld = setup_multiworld([worldOne, worldTwo], pre_link_steps) # Create our test Multiworld
                # Act
                self.multiworld.set_item_links()                # Run the function that creates the itempools
                self.multiworld.calculate_item_links()          # Run the function that creates the item links

                # Assert
                self.assertTrue(any(group['name'] == "ItemLinkTest" for group in self.multiworld.groups.values()), f"ItemLinkTest group not found in {self.multiworld.groups}")
                link_group = [group for group in self.multiworld.groups.values() if group['name'] == "ItemLinkTest"][0]

                self.assertEqual(link_group['game'], case['Game'], f"Game is not set correctly for {case['Game']}")
                self.assertEqual(link_group['item_pool'], case['ExpectedLinkedItems'], f"Item pool is not set correctly for {case['Game']}")
    
    def test_all_games_items_link_defaults(self) -> None:
        """Tests that all worlds are able to link items to each other in a multiworld."""
        # Prepare
        for worldBase in AutoWorldRegister.world_types.values():
            with self.subTest(game=worldBase.game):
                worldOne = copy.deepcopy(worldBase) # Create our test worlds
                worldTwo = copy.deepcopy(worldBase)
                self.multiworld = setup_multiworld([worldOne, worldTwo], pre_link_steps) # Create our test Multiworld
                linked_items = self.get_progression_items(worldBase)

                if len(linked_items) == 0:
                    continue            # if there are no progression items, just skip this test

                for world in self.multiworld.worlds.values(): # Set some basic options on worlds in the multiworld
                    world.options.accessibility.value = Accessibility.option_locations
                    world.options.item_links = ItemLinks([{ # Define a basic itemlink
                        'name': 'ItemLinkTest', 
                        'item_pool' : linked_items, 
                        'replacement_item' : None, 
                        'link_replacement' : None,
                        }])
                
                world_items = {} # Get a list of each item in each world - For testing later
                for player in range(1, self.multiworld.players+1):
                    world_items[player] = [item for item in self.multiworld.itempool if item.player == player]

                # Act
                prior_item_count = len(self.multiworld.itempool) # Get the total itempool size
                self.multiworld.set_item_links()                # Run the function that creates the itempools
                self.multiworld.calculate_item_links()          # Run the function that creates the item links
                # Assert Link was created and contains items
                self.assertTrue(any(group['name'] == "ItemLinkTest" for group in self.multiworld.groups.values()), f"ItemLinkTest group not found in {self.multiworld.groups}")
                link_group = [group for group in self.multiworld.groups.values() if group['name'] == "ItemLinkTest"][0]
                self.assertEqual(link_group['game'], worldBase.game, f"Game is not set correctly for {worldBase.game}")
                self.assertEqual(link_group['item_pool'], set(linked_items), f"Item pool is not set correctly for {worldBase.game}")
                self.assertEqual(len(self.multiworld.itempool), prior_item_count, f"ItemPool length should stay the same")
                for player in range(1, self.multiworld.players+1):
                    new_world_items = [item for item in self.multiworld.itempool if item.player == player]
                    self.assertLessEqual(len(new_world_items), len(world_items[player]), f"Item count for each player should be the same or less. We have {len(linked_items)} linked items")
                # Assert Items are linked

                for world in self.multiworld.worlds.values():
                    for item in linked_items:
                        pass
                        # self.assertEqual(world.item_links[item], link_group['replacement_item'], f"Item {item} is not linked correctly in {world.game}")
                        # self.assertEqual(world.link_replacements[link_group['replacement_item']], link_group['link_replacement'], f"Link replacement is not set correctly in {world.game}")
            