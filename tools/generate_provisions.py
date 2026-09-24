#!/usr/bin/env python3
"""Source of truth for the Steward Cache loot tables (data/ninjacatskies/loot_table/provisions/*.json).

    python tools/generate_provisions.py

Four pools per tier: supplies (resources), garden (saplings, seeds, crops, plants, flowers and passive
vanilla spawn eggs, because a skyblock pad has no other way to get a chicken or a cow), decor, and one
rare draw (Thread Shard / Thread of Return). tools/gates/test_steward_caches.py bounds all four.
"""
import json
from pathlib import Path

D = str(Path(__file__).resolve().parents[1] / 'mods/ninjacatskies/src/main/resources/data/ninjacatskies/loot_table/provisions') + '/'
def e(name,w,lo,hi):
    ns='' if ':' in name else 'minecraft:'
    return {"type":"minecraft:item","name":ns+name,"weight":w,"functions":[{"function":"minecraft:set_count","count":{"type":"minecraft:uniform","min":lo,"max":hi}}]}
SUPPLIES={
 'small':(2,[e('bread',3,2,4),e('torch',2,4,8),e('bone_meal',2,4,8),e('string',2,2,4),e('clay_ball',1,3,6),e('oak_sapling',1,1,2),
             e('wheat_seeds',1,2,4),e('leather',1,1,2),e('copper_ingot',2,2,4),e('iron_ingot',1,1,2),e('ninjacatskies:frayed_thread',2,2,4)]),
 'medium':(5,[e('bread',2,3,6),e('torch',1,6,10),e('bone_meal',2,6,10),e('string',1,3,6),e('clay_ball',1,4,8),e('leather',2,1,3),
             e('copper_ingot',3,3,6),e('iron_nugget',1,4,8),e('flower_pot',1,1,2),e('iron_ingot',3,2,4),e('gold_ingot',1,1,3),
             e('redstone',2,4,8),e('lapis_lazuli',1,3,6),e('experience_bottle',1,1,3),e('ninjacatskies:frayed_thread',2,4,8)]),
 'large':(12,[e('cooked_beef',2,3,6),e('bone_meal',2,6,12),e('string',1,4,8),e('leather',2,2,4),e('copper_ingot',2,4,8),
             e('iron_ingot',3,2,5),e('gold_ingot',2,1,3),e('lantern',1,1,2),e('book',2,1,3),e('honeycomb',1,2,4),
             e('experience_bottle',2,2,4),e('redstone',2,6,12),e('lapis_lazuli',1,4,8),e('diamond',2,1,2),e('emerald',1,1,3),
             e('ender_pearl',1,1,2),e('obsidian',1,2,4),e('ninjacatskies:thread_skein',1,1,2)]),
}

SAPLINGS=['oak_sapling','spruce_sapling','birch_sapling','jungle_sapling','acacia_sapling','dark_oak_sapling','cherry_sapling','mangrove_propagule']
SEEDS=['wheat_seeds','beetroot_seeds','melon_seeds','pumpkin_seeds']
CROPS=['potato','carrot','sugar_cane','cactus','bamboo','sweet_berries','glow_berries','cocoa_beans','kelp','brown_mushroom','red_mushroom','nether_wart']
PLANTS=['lily_pad','vine','moss_block','fern','azalea','flowering_azalea','sea_pickle','big_dripleaf','spore_blossom']
FLOWERS=['dandelion','poppy','blue_orchid','allium','azure_bluet','red_tulip','orange_tulip','white_tulip','pink_tulip','oxeye_daisy','cornflower','lily_of_the_valley','sunflower','lilac','rose_bush','peony','torchflower_seeds','pitcher_pod']
EGGS_FARM=['chicken','cow','pig','sheep']
EGGS_MORE=['rabbit','bee','goat','turtle','frog','cat','wolf','horse','donkey','llama','mooshroom','parrot','fox','panda','axolotl','armadillo']
DECOR=[('flower_pot',1,3),('candle',1,4),('lantern',1,2),('soul_lantern',1,2),('item_frame',1,3),('painting',1,2),('armor_stand',1,1),
       ('chain',2,6),('ladder',4,8),('glass_pane',4,12),('white_wool',4,8),('white_carpet',3,8),('red_carpet',3,6),('blue_carpet',3,6),
       ('green_carpet',3,6),('yellow_carpet',3,6),('white_banner',1,1),('bookshelf',1,2),('decorated_pot',1,1),('campfire',1,1),
       ('terracotta',4,8),('white_glazed_terracotta',2,4),('brick',4,8),('oak_trapdoor',2,4),('spruce_fence',2,6),('stone_brick_wall',2,6),
       ('shroomlight',1,2),('sea_lantern',1,2),('end_rod',1,2),('flower_banner_pattern',1,1),('white_dye',2,4),('red_dye',2,4),
       ('blue_dye',2,4),('yellow_dye',2,4),('green_dye',2,4),('black_dye',2,4)]
def garden(egg_weight, more_eggs):
    out=[e(x,30,1,2) for x in SAPLINGS]+[e(x,30,2,4) for x in SEEDS]+[e(x,20,1,3) for x in CROPS]+[e(x,10,1,2) for x in PLANTS]+[e(x,10,1,3) for x in FLOWERS]
    base=sum(x['weight'] for x in out)
    eggs=[x+'_spawn_egg' for x in EGGS_FARM]+([x+'_spawn_egg' for x in EGGS_MORE] if more_eggs else [])
    # the farm four are the ones a pad needs, so they carry most of the egg share
    farm_w, more_w = (egg_weight*base)//100, 0
    ws=[max(1,round(farm_w*(0.6 if more_eggs else 1)/4))]*4+([max(1,round(farm_w*0.4/len(EGGS_MORE)))]*len(EGGS_MORE) if more_eggs else [])
    return out+[e(x,w,1,2) for x,w in zip(eggs,ws)]
EXTRA_POOLS={'small':[(1,garden(10,False)),(1,[e(d[0],1,d[1],d[2]) for d in DECOR])],
             'medium':[(2,garden(14,True)),(1,[e(d[0],1,d[1],d[2]) for d in DECOR])],
             'large':[(3,garden(18,True)),(2,[e(d[0],1,d[1],d[2]) for d in DECOR])]}
# One extra draw out of 1000 per cache: the rare pieces of a life.
RARE={'small':(15,2),'medium':(40,5),'large':(120,15)}
for tier,(rolls,entries) in SUPPLIES.items():
    shard,ret=RARE[tier]
    rare={"rolls":1,"entries":[{"type":"minecraft:empty","weight":1000-shard-ret},
        {"type":"minecraft:item","name":"ninjacatskies:thread_shard","weight":shard},
        {"type":"minecraft:item","name":"ninjacatskies:thread_of_return","weight":ret}]}
    d={"type":"minecraft:gift","pools":[{"rolls":rolls,"entries":entries}]+[{"rolls":r,"entries":es} for r,es in EXTRA_POOLS[tier]]+[rare]}
    open(D+tier+'.json','w',encoding='utf-8',newline='\n').write(json.dumps(d,indent=2)+'\n')
    good=sum(x['weight'] for x in entries if x['name'].split(':')[1] in ('copper_ingot','iron_ingot','gold_ingot','diamond','emerald','ender_pearl','experience_bottle','frayed_thread','thread_skein','redstone','lapis_lazuli','obsidian'))
    eggs=[x for r,es in EXTRA_POOLS[tier][:1] for x in es if x['name'].endswith('_spawn_egg')]
    gw=sum(x['weight'] for x in EXTRA_POOLS[tier][0][1])
    print(tier,'egg share per garden roll',round(sum(x['weight'] for x in eggs)/gw,3),'garden rolls',EXTRA_POOLS[tier][0][0],'decor rolls',EXTRA_POOLS[tier][1][0])
    print(tier,'rolls',rolls,'good share',round(good/sum(x['weight'] for x in entries),2),'shard',shard/10,'% return',ret/10,'%')
