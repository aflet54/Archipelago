import copy
import typing
from BaseClasses import ItemClassification, MultiWorld
from Options import Accessibility, ItemLinks
from test.multiworld.test_multiworlds import MultiworldTestBase
from worlds.AutoWorld import AutoWorldRegister, World
from ..general import setup_multiworld

pre_link_steps = ("generate_early", "create_regions", "create_items", "set_rules", "generate_basic")

edge_cases: typing.List[typing.Dict[str, typing.Any]] = [
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

    def get_progression_items(self, world: typing.Type[World]) -> typing.List[str]:
        """Returns a list of items that are in the itempool of a world and considered progression."""
        item_list = []
        complete_item_list = world.item_name_groups["Everything"]
        for item in self.multiworld.itempool:
            if item.name in complete_item_list and \
               item.classification == ItemClassification.progression:
                item_list.append(item.name)
        return item_list


class TestTwoPlayerItemLink(ItemLinkTestBase):
    def test_itemlink_edge_cases(self) -> None:
        """Tests that various combinations of settings are loaded correctly"""
        for case in edge_cases:
            gameName: str = case['Game']
            with self.subTest(game=gameName, description=case['Description']):
                # Prepare our worlds and Set the Item Link information

                worldBase = AutoWorldRegister.world_types[gameName]
                worldOne = copy.deepcopy(worldBase)
                worldOne.options.item_links = ItemLinks([case['LinkOne']])
                worldTwo = copy.deepcopy(worldBase)
                worldTwo.options.item_links = ItemLinks([case['LinkTwo']])
                self.multiworld = setup_multiworld([worldOne, worldTwo], pre_link_steps)
                # Act
                self.multiworld.set_item_links()                # Run the function that creates the itempools
                self.multiworld.calculate_item_links()          # Run the function that creates the item links

                # Assert
                self.assertTrue(any(group['name'] == "ItemLinkTest" for group in self.multiworld.groups.values()),
                                 f"ItemLinkTest group not found in {self.multiworld.groups}")
                link_group = [group for group in self.multiworld.groups.values() if group['name'] == "ItemLinkTest"][0]

                self.assertEqual(link_group['game'], gameName,
                                 f"Game is not set correctly for {gameName}")
                self.assertEqual(link_group['item_pool'], case['ExpectedLinkedItems'],
                                 f"Item pool is not set correctly for {gameName}")


    def test_all_games_items_link_defaults(self) -> None:
        """Tests that all worlds are able to link items to each other in a multiworld."""
        #  Prepare
        for worldBase in AutoWorldRegister.world_types.values():
            with self.subTest(game=worldBase.game):
                #  Prepare our worlds and Set the Item Link information
                worldOne = copy.deepcopy(worldBase)
                worldTwo = copy.deepcopy(worldBase)
                self.multiworld = setup_multiworld([worldOne, worldTwo], pre_link_steps)
                linked_items = self.get_progression_items(worldBase)

                if len(linked_items) == 0:
                    continue            # if there are no progression items, just skip this test

                for world in self.multiworld.worlds.values():   # Set some basic options on worlds in the multiworld
                    world.options.accessibility.value = Accessibility.option_locations
                    world.options.item_links = ItemLinks([{     # Define a basic itemlink
                        'name': 'ItemLinkTest',
                        'item_pool': linked_items,
                        'replacement_item': None,
                        'link_replacement': None,
                        }])
                
                world_items = {} # Get a list of each item in each world - For testing later
                for player in range(1, self.multiworld.players+1):
                    world_items[player] = [item for item in self.multiworld.itempool if item.player == player]

                # Act
                prior_item_count = len(self.multiworld.itempool)    # Get the total itempool size
                self.multiworld.set_item_links()                    # Run the function that creates the itempools
                self.multiworld.calculate_item_links()              # Run the function that creates the item links
                # Assert Link was created and contains items
                self.assertTrue(any(group['name'] == "ItemLinkTest" for group in self.multiworld.groups.values()),
                                f"ItemLinkTest group not found in {self.multiworld.groups}")
                link_group = [group for group in self.multiworld.groups.values() if group['name'] == "ItemLinkTest"][0]
                self.assertEqual(link_group['game'], worldBase.game,
                                 f"Game is not set correctly for {worldBase.game}")
                self.assertEqual(link_group['item_pool'], set(linked_items),
                                 f"Item pool is not set correctly for {worldBase.game}")
                self.assertEqual(len(self.multiworld.itempool), prior_item_count,
                                 f"ItemPool length should stay the same \
                                    {prior_item_count} not {len(self.multiworld.itempool)}")
                for player in range(1, self.multiworld.players+1):
                    new_world_items = [item for item in self.multiworld.itempool if item.player == player]
                    self.assertLessEqual(len(new_world_items), len(world_items[player]),
                                         f"Item count for each player should be the same or less. \
                                            We have {len(linked_items)} linked items")

