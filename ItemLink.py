import collections
from typing import Dict, List, Optional, Set, Tuple

from BaseClasses import MultiWorld
from BaseClasses import Item, Location, MultiWorld, Region
from worlds import AutoWorld

def calculate_item_links(multiworld: MultiWorld) -> MultiWorld:
    for group_id, group in multiworld.groups.items():
        def find_common_pool(players: Set[int], shared_pool: Set[str]) -> Tuple[
            Optional[Dict[int, Dict[str, int]]], Optional[Dict[str, int]]
        ]:
            classifications: Dict[str, int] = collections.defaultdict(int)
            counters = {player: {name: 0 for name in shared_pool} for player in players}
            for item in multiworld.itempool:
                if item.player in counters and item.name in shared_pool:
                    counters[item.player][item.name] += 1
                    classifications[item.name] |= item.classification

            for player in players.copy():
                if all([counters[player][item] == 0 for item in shared_pool]):
                    players.remove(player)
                    del (counters[player])

            if not players:
                return None, None

            for item in shared_pool:
                count = min(counters[player][item] for player in players)
                if count:
                    for player in players:
                        counters[player][item] = count
                else:
                    for player in players:
                        del (counters[player][item])
            return counters, classifications

        common_item_count, classifications = find_common_pool(group["players"], group["item_pool"])
        if not common_item_count:
            continue

        new_itempool: List[Item] = []
        for item_name, item_count in next(iter(common_item_count.values())).items():
            for _ in range(item_count):
                new_item = group["world"].create_item(item_name)
                # mangle together all original classification bits
                new_item.classification |= classifications[item_name]
                new_itempool.append(new_item)

        region = Region("Menu", group_id, multiworld, "ItemLink")
        multiworld.regions.append(region)
        locations = region.locations
        for item in multiworld.itempool:
            count = common_item_count.get(item.player, {}).get(item.name, 0)
            if count:
                loc = Location(group_id, f"Item Link: {item.name} -> {multiworld.player_name[item.player]} {count}",
                               None, region)
                loc.access_rule = lambda state, item_name = item.name, group_id_ = group_id, count_ = count: \
                    state.has(item_name, group_id_, count_)

                locations.append(loc)
                loc.place_locked_item(item)
                common_item_count[item.player][item.name] -= 1
            else:
                new_itempool.append(item)

        itemcount = len(multiworld.itempool)
        multiworld.itempool = new_itempool

        while itemcount > len(multiworld.itempool):
            items_to_add = []
            for player in group["players"]:
                if group["link_replacement"]:
                    item_player = group_id
                else:
                    item_player = player
                if group["replacement_items"][player]:
                    items_to_add.append(AutoWorld.call_single(multiworld, "create_item", item_player,
                                                                group["replacement_items"][player]))
                else:
                    items_to_add.append(AutoWorld.call_single(multiworld, "create_filler", item_player))
            multiworld.random.shuffle(items_to_add)
            multiworld.itempool.extend(items_to_add[:itemcount - len(multiworld.itempool)])
    return multiworld