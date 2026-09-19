"""Practical lessons and native placement diagrams for the Whisker Codex."""
import json
from pathlib import Path

NS = 'ninjacatskies'


STRAND_BRAID_CHECKS = {
    'wake': (
        '**Goal:** finish Soil and seat the Soil token.\n\n'
        'You need the **Soil Knot** claimed and a **Tension Post** placed.\n\n'
        '**Check:** Finish Soil in the quest screen. Claim the **Soil Knot**, then seat the Soil token. The Soil notch lights.'
    ),
    'recover': (
        '**Goal:** finish Recover and seat the Stone token.\n\n'
        'You need Frayed Thread, a **Loomframe**, a **Tension Barrel**, and a mesh.\n\n'
        '**Check:** Finish Recover. Claim the Stone token and seat it. The Stone notch lights. A working Loomframe and Tension Barrel are the practical check.'
    ),
    'root': (
        '**Goal:** finish Sprout and keep food running.\n\n'
        'You need a kitchen source and the Sprout token from the chapter.\n\n'
        '**Check:** Finish Sprout. Claim the token and seat it. The Sprout notch lights. Keep a food source running before you leave the pad.'
    ),
    'edge': (
        '**Goal:** finish Claw and seat the Claw token.\n\n'
        'You need four **Blueprint Paper** if the join gift is gone, then iron on your back.\n\n'
        '**Check:** Finish Claw. If the Blueprint Package is missing, craft it from four Blueprint Paper, then seat the Claw token. The Claw notch lights.'
    ),
    'pattern': (
        '**Goal:** finish Clock and seat the Clock token.\n\n'
        'You need Create started and a Binding Knot for the precision mechanism.\n\n'
        '**Check:** Finish Clock. Claim the token and seat it. The Clock notch lights.'
    ),
    'colony': (
        '**Goal:** finish Swarm and seat the Swarm token.\n\n'
        'You need a nest the pad can actually grow — oak logs around a flower, woken with a right-click from another flower — then hives.\n\n'
        '**Check:** Finish Swarm. Claim the token and seat it. The Swarm notch lights.'
    ),
    'hum': (
        '**Goal:** finish Spark and seat the Spark token.\n\n'
        'You need a **Drumheart** and the first Pulse trickle from Start here.\n\n'
        '**Check:** Finish Spark. Claim the token and seat it. The Spark notch lights.'
    ),
    'bind': (
        '**Goal:** spin **Braid Cord** and seat Sigil.\n\n'
        'You need any two of Clock, Swarm and Spark seated, a **Strand Filament**, and a **Tension Post**.\n\n'
        '**Check:** Seat any two of Clock, Swarm and Spark. Right-click the Post with a Strand Filament for **Braid Cord**. Finish Sigil, then seat the Sigil token.'
    ),
    'reweave': (
        '**Goal:** close your Clowder\'s cut with March Stone.\n\n'
        'You need nine seated tokens and **March Stone** from the March.\n\n'
        '**Check:** Seat all nine tokens. Right-click the Post with March Stone for a **Spindle Loom Fragment**, then right-click again holding the Fragment. Your Clowder\'s Strand of the Fray closes.'
    ),
}

BRAID_TAIL = (
    'Read **Start here** for worked examples. Recipes live in JEI; the **Spirit Codex** covers Tribal Power machinery. '
    'If you get stuck, test one recipe at a time and sneak-use the Spirit Codex on a silent machine.'
)


def build_lessons(book, write, text, entry, category):
    category('first_steps', 'Start here', f'{NS}:whisker_codex', 0,
             'A safe start, working examples, and what to do when progress stops.')
    lessons = [
        ('using_the_book', 'Using the Codex', 'ninjacatskies:whisker_codex', [
            text('Book and quests',
                 '**Goal:** know which screen does which job before you build anything.\n\n'
                 'You need the **Whisker Codex** from the starter kit or dock chest.\n\n'
                 'Use the **Whisker Codex** to learn a system, then build it. Open the quest screen with the **Grave / backtick** key for tasks, requirements and rewards. If you changed controls, search Controls for Quests.\n\n'
                 'Click a quest item to open its recipe in JEI. Start with **Start here**. **The Loom Braid** is the campaign map. Story chapters wait until you want the why.'),
            text('Read, build, check',
                 'Each practical lesson gives a goal, numbered steps and a way to check the result. Follow the arrows.\n\n'
                 'Exact ingredients live in JEI, not in this book. Recipes can change with the pack. A diagram is a placement example, not a quest requirement.\n\n'
                 '**Tribal Power** is its own mod. Open its **Spirit Codex** for every generator, workshop, rite and camp hand. This book is the pack campaign: pad, quests, Loom, Clowder. Sneak-use the Spirit Codex on a silent Tribal station.'),
            text('Words in this book',
                 '**Pad:** your floating island.\n**Clowder:** your player team.\n**Strand:** one part of the campaign.\n**Token:** the reward proving you completed a Strand.\n**Seat:** right-click a Tension Post with a token.\n**Pulse:** the energy used by Tribal Power.\n**March:** the otherworld beyond the Gate Drum.\n\n'
                 '**Check:** Grave opens quests. A quest item opens JEI. **Start here** is the first category in this book.')]),
        ('safe_start', 'Your first safe workshop', 'minecraft:crafting_table', [
            text('Goal and supplies',
                 '**Goal:** a safe place to grow a tree, craft, store items and cook food.\n\n'
                 'You need a sapling, dirt, and the starter supplies.\n\n'
                 'Keep a sapling, some dirt and the starter supplies. Open the Soil quests before spending rare starter items.'),
            text('Clowder and Hall',
                 '**Goal:** one Clowder, one pad, a way back to the Hall.\n\n'
                 'You need the **Island Charter** and a **Hub Key**.\n\n'
                 '1. **K** opens the island/team panel. The **Island Charter** opens the same panel. Join or create a team, then pick a pad.\n'
                 '2. Hold the Charter and right-click a friend to invite, or `/clowder invite <name>` / `/clowder accept`.\n'
                 '3. Sneak-use the Charter on solid Overworld pad ground to seal spawn.\n'
                 '4. **Hub Key** or `/clowder hub` reaches Clowder Hall. `/clowder return` sends you home. Right-click a Hall Elder to trade Frayed Thread.\n\n'
                 '**Check:** you are on your pad, in the intended Clowder, and `/clowder hub` works.'),
            text('Build in this order',
                 '1. Widen your platform. Add edges and light.\n'
                 '2. Harvest wood. Keep a replacement sapling and replant it on dirt.\n'
                 '3. Make a crafting table and chest. Store spare saplings and valuables.\n'
                 '4. Make a furnace. Cook food as the Soil quests request. Keep walkways clear.'),
            text('Workshop check',
                 '**Check:** a replanted tree, spare materials in storage, cooked food, and a workspace you can walk around without falling.\n\n'
                 'The model on the next page is one compact arrangement. Build a larger platform around it. The exact arrangement is optional. Keep fire and lava away from wooden floors.')], 'starter_workshop'),
        ('water', 'Keep a water supply', 'minecraft:water_bucket', [
            text('Goal and supplies',
                 '**Goal:** a refillable water source that will not burn the pad.\n\n'
                 'You need ice, lava and an empty bucket on Normal/Hard. Easy pads already have water.\n\n'
                 'Easy pads include water. Normal and Hard pads supply ice, lava and an empty bucket.'),
            text('First water source',
                 '1. Make a contained area from nonflammable blocks.\n'
                 '2. Put the ice where the water should remain. Use nearby lava as the heat source, with blocks containing its flow.\n'
                 '3. Let the ice melt. Collect the resulting water source with the bucket.\n\n'
                 'Keep lava away from wood and stored items. Do not let the two liquids flow together.'),
            text('A refillable pool',
                 '**Once you have two water source buckets**, build the four-block pool shown next. Fill opposite corners. On ordinary water-source rules, all four spaces become sources.\n\n'
                 '**Check:** collect a bucket and watch the pool refill before you rely on it. One source alone is not enough for this layout. Keep water available for the Tension Barrel and farming.')], 'water_pool'),
        ('first_token', 'Finish and seat Soil', 'ninjacatskies:strand_token_soil', [
            text('Goal',
                 '**Goal:** finish Soil and seat its token so the pad starts mending you.\n\n'
                 'You need the Soil Knot claimed and a **Tension Post** placed.\n\n'
                 'Completing a quest and seating its token are separate steps.'),
            text('Complete the chapter',
                 '1. Open the quest screen and work through Soil. Read each task: some need you to hold an item; others ask you to craft or perform an action. Click the item to open JEI if the recipe is unclear.\n'
                 '2. Claim the **Soil Knot** reward when its tasks are complete.\n'
                 '3. Craft and place a **Tension Post** using its current recipe.\n'
                 '4. Right-click the Post with the Soil Strand token.'),
            text('Check the Post',
                 '**Check:** the Soil notch lights and your team gains the seated Strand.\n\n'
                 'If the notch stays dark, check that you claimed the token and are holding the right item. Team progress is shared; you do not need a separate Post for every player.\n\n'
                 'Next: Recover introduces the Loomframe, barrel and material processing.')]),
        ('materials', 'Build a material supply', 'voidloom:loomframe', [
            text('Goal and sequence',
                 '**Goal:** turn pad scraps into materials for Recover and the chapters after it.\n\n'
                 'You need Frayed Thread, Recover open, and a mesh.\n\n'
                 '1. Unravel Frayed Thread into string when you need it. Keep some Thread for trading.\n'
                 '2. Follow JEI for Void Yarn, a Binding Knot and a Loomframe.\n'
                 '3. Make a Tension Barrel and keep water nearby.\n'
                 '4. Follow Recover for clay, porcelain and the route to handling lava.'),
            text('Test small batches',
                 'Read the Loomframe and barrel in JEI before adding items. Start with one batch and check the output. Keep the input and result in separate storage until you know the process.\n\n'
                 '**Check:** the Loomframe produces scraps from a loaded mesh, and the barrel returns clay or yarn. Adjacent placement alone does not automate these stations. The next model is a workspace example.'),
            text('Sieves',
                 '**Goal:** a click sieve for early grit, then a hopper Loomframe.\n\n'
                 'You need an oak sieve, a string mesh, and cobble to hammer.\n\n'
                 '1. Craft an **oak sieve**. Hold a mesh and right-click the sieve; this one is hand-only.\n'
                 '2. Hammer cobble toward gravel, sand or dust as Recover asks. String mesh first; iron mesh is when **Strand Filament** starts.\n'
                 '3. The **Loomframe** is the hopper machine: mesh by hand, dirt/gravel/sand/dust in the top, output below.\n\n'
                 '**Check:** the oak sieve yields a click of grit, and the Loomframe ticks with a loaded mesh. Follow Recover and JEI for the current mesh and substrate. Adjacent placement does not automate either station.')], 'material_workshop'),
        ('claw_blueprints', 'Claw Blueprint Package', 'silentgear:blueprint_package', [
            text('Goal',
                 '**Goal:** get Silent Gear starter plans when Claw opens, even if the join gift is gone.\n\n'
                 'You need four **Blueprint Paper**.\n\n'
                 'Claiming a pad wipes Silent Gear\'s first-join **Blueprint Package**. That is Skyblock Builder clearing the inventory, not a missing recipe.'),
            text('Craft the package',
                 '1. Reach the Claw / Edge quests. Open a Blueprint Paper in JEI if you need the current paper recipe.\n'
                 '2. Craft a **Blueprint Package** from four **Blueprint Paper**, shapeless.\n'
                 '3. Right-click the package to unwrap starter plans.\n'
                 '4. Follow Claw for rods, tools, iron on your back, a bow, and a portal frame. Leave the pad on purpose.'),
            text('Check',
                 '**Check:** you are holding the package or the unwrapped plans, and the Claw quest can see them.\n\n'
                 'Do not wait for another join gift. Tokens still are not crafted in a grid. After Claw, Pattern, Colony and Hum open together.')]),
        ('first_power', 'Make the first Echo Shard', 'tribalpower:echo_shatter', [
            text('Goal and supplies',
                 '**Goal:** make an Echo Shard for an automatic generator.\n\n'
                 'You need Echo Shatter, an Earth Resonance Totem, a Drumheart and **stone**, not cobblestone. Smelt cobblestone if necessary.\n\n'
                 'Use the **Spirit Codex** for Tribal Power recipes, diagrams and troubleshooting. Sneak-use it on the station if it stays silent.'),
            text('Build and run it',
                 '1. Place the drum and Earth totem beside Echo Shatter, within 8 blocks.\n'
                 '2. Right-click the drum with an empty hand about once a second. Build a reserve of Pulse.\n'
                 '3. Put stone into Shatter and leave output space.\n'
                 '4. Wait for an Echo Shard. If it stops, charge the drum again and inspect the station with the Spirit Codex.\n\n'
                 'Cobblestone becomes gravel instead. A slow generator can finish a batch using stored energy.'),
            text('Check',
                 '**Check:** an Echo Shard is in the output. The diagram is a compact example, not a quest shape.')], 'shatter_workshop'),
        ('automatic_power', 'Start automatic power', 'tribalpower:pulse_resonator', [
            text('Goal',
                 '**Goal:** a Pulse Resonator that makes a small, steady trickle of Pulse without you standing at the drum.\n\n'
                 'You need a **Pulse Resonator**, an **Echo Shard**, and **Earth and Fire Resonance Totems**.'),
            text('Starter generator',
                 '1. Place the Resonator.\n'
                 '2. Right-click it with the shard to install the reusable catalyst.\n'
                 '3. Place the two different totems within 8 blocks. The diagram shows a compact example.\n'
                 '4. Wait a second and inspect the generator. Stored Pulse should rise.'),
            text('Power budget',
                 '**Check:** stored Pulse climbs while you stand still.\n\n'
                 'The starter generator does not mean every machine can run continuously. If a machine spends power faster than you make it, let a reserve build up or improve generation.\n\n'
                 'Two identical totems count as one element. If generation stops, check the catalyst, different elements and pausing redstone. Read the Spirit Codex before larger totem layouts or a Conductor.')], 'resonator_workshop'),
        ('hold_fluids', 'Hold liquids safely', 'tribalpower:spirit_cistern', [
            text('Goal',
                 '**Goal:** store and move liquids without dumping them on the floor.\n\n'
                 'You need a **Spirit Cistern** (JEI / Tribal Weave). AE2 Sky Stone Tanks empty when broken.\n\n'
                 'AE2 **Sky Stone Tanks** empty when broken. That is AE2\'s design, not a pack bug. Bucket them out before you pick the tank up.'),
            text('Use a Cistern',
                 '1. Craft a **Spirit Cistern**. It holds 16 buckets of one fluid.\n'
                 '2. Fill it with a bucket or a standard fluid pipe. A comparator reads fullness; redstone can lock filling and draining.\n'
                 '3. Break the Cistern when you need to move it. The fluid stays on the dropped block.\n'
                 '4. Relays move fluid between loaded ends. They are paths, not tanks.\n\n'
                 'The **Spirit Codex** has the current piping and Wave Drum details. The diagram is one compact corner, not a quest shape.'),
            text('Check',
                 '**Check:** put a bucket into the Cistern, pick the block up, and place it again. The fluid is still there. If you used a Sky Stone Tank, the liquid is gone unless you bucketed first.')], 'cistern_corner'),
        ('choose_branches', 'Choose two middle branches', 'ninjacatskies:braid_cord', [
            text('Three routes',
                 '**Goal:** seat any two of Clock, Swarm and Spark, then spin **Braid Cord** at the Post.\n\n'
                 'You need two of those tokens seated, a **Strand Filament**, and a **Tension Post**.\n\n'
                 'After Claw, three branches open together:\n\n'
                 '**Pattern / Clock:** mechanical processing.\n'
                 '**Colony / Swarm:** bees and their production chains.\n'
                 '**Hum / Spark:** living power and workshops.\n\n'
                 'A team can divide the work. You will still need all nine Strands for the final reweave.'),
            text('Make Braid Cord',
                 '1. Check that two of Clock, Swarm and Spark are seated at your Post. Merely holding their tokens is not enough.\n'
                 '2. Hold a **Strand Filament**.\n'
                 '3. Right-click the Post to receive **Braid Cord**.\n\n'
                 'Do not put tokens in a crafting grid. They record progress. If the Post refuses, read its message and check which Strands are seated.'),
            text('Check',
                 '**Check:** two of those three notches are lit, and Braid Cord is in your hand. Next: Bind and the Sigil quests.')]),
        ('pad_runners', 'Pad-runners', 'chocobosreborn:chocobo_almanac', [
            text('Goal',
                 '**Goal:** find a wild pad-runner in the March, not on your void pad.\n\n'
                 'You need a **Gate Drum**, **Gysahl**, and the **Chocobo Almanac**.\n\n'
                 'Birds do not spawn on a skyblock island. There is no spawn-egg shortcut and no join gift. Walk the March.'),
            text('Find, tame, ride',
                 '1. Use a **Gate Drum** empty-handed and play the Gate Rite (hit the beats on A, S, D, F; 60% opens it), then walk through. Yellows graze the Steppe and Reed Fen. Snow Fields hide Wonderful grades. Ember Wastes keep Flame birds.\n'
                 '2. Pick **Gysahl** in the March (Reed Fen is densest). Picking drops seeds too; plant them on farmland at home.\n'
                 '3. Craft the **Chocobo Almanac** (book and a gysahl leaf) and use it anywhere: its pages list your own birds.\n'
                 '4. Tame a wild yellow with gysahl, then saddle it. Sprint dashes; ease off to recover stamina.'),
            text('Esther at the hub',
                 'After you have walked the March, **Esther** stands at Clowder Hall (`/clowder hub`). Ride a saddled bird to her, ask the Whiskerwind Guide, or craft a **Chocobo Pocketwatch** (gold nuggets around a clock, with a gysahl).\n\n'
                 '**Check:** you are on a saddled bird, or Esther is waiting at the hub.'),
            text('Farm and colour',
                 '**Goal:** train, mate, and paint colours without chasing dyes that do not exist.\n\n'
                 'You need greens to train, nuts to mate, and the **Chocobo Almanac** to read the bird.\n\n'
                 '1. Train an adult on greens until it is sated on each kind. Gysahl is the only green in the wild; Krakka is two gysahl and bone meal.\n'
                 '2. Mate with nuts. Talent follows the nut. Colour follows the parents unless Carob or Zeio is involved.\n'
                 '3. **Carob** (Bilo at Whiskerwind, or Class A races): two Good-or-better Yellows hatch Green or Blue. Each parent needs 1 first-place race; 4 combined firsts make the colour certain.\n'
                 '4. Green plus Blue hatch Black (a miss is White) — 2 firsts each, 9 combined for a sure roll. **Zeio** (Bilo, rare at Class S): Black plus a Wonderful Yellow hatch Gold — 3 firsts each, 12 combined.\n'
                 '5. There are no Pink or Red birds. The Fair stall does not sell those dyes. Purple is End; Flame is Ember Wastes; Gold flies.\n\n'
                 '**Check:** the Almanac shows colour, grade, class, race wins and the last nut. Recipes stay in JEI.')]),
        ('finish', 'Prepare the final reweave', 'ninjacatskies:spindle_loom_fragment', [
            text('Readiness checklist',
                 '**Goal:** seat all nine Strands, bring March Stone home, and close your Clowder\'s cut.\n\n'
                 'You need nine seated tokens, **March Stone**, and a way home.\n\n'
                 'Count the Post notches before you leave. Prepare food, equipment and a return route. The **Spirit Codex** covers the Gate Drum and March travel.'),
            text('Use the Post twice',
                 '1. With all nine Strands seated, right-click the Tension Post with March Stone. This makes a **Spindle Loom Fragment**.\n'
                 '2. Right-click the Post again, this time holding the Fragment, to reweave your team\'s sky.\n\n'
                 'These are world interactions, not crafting-table recipes.'),
            text('Check',
                 '**Check:** nine notches are lit, then the Fragment seats and the Fray over the Dock is thinner for your Clowder. If nothing happens, read the Post message. Other teams have their own progress.')]),
        ('stuck', 'When progress stops', 'minecraft:book', [
            text('Quest checks',
                 '**Goal:** unstick one blocked task without rebuilding the pad.\n\n'
                 'You need the quest screen, JEI, and (for Tribal) the **Spirit Codex**.\n\n'
                 'Read the exact task and its prerequisites. Check item counts, variants and whether the task wants possession, crafting or another action. Click the quest item to open JEI. Try the task\'s detect button when one is available.\n\n'
                 'Check rewards too: an unclaimed token cannot be seated. If Claw is stuck on plans, craft the Blueprint Package from four Blueprint Paper. If playing together, confirm you are in the intended Clowder before repeating a long crafting chain.'),
            text('Machine checks',
                 'Check these separately:\n'
                 '1. Correct input and recipe.\n'
                 '2. Available power and range.\n'
                 '3. Required totem or other structure.\n'
                 '4. Space for the result.\n'
                 '5. Pausing redstone and side settings.\n\n'
                 'For Tribal Power, crouch and right-click the machine with the Spirit Codex. Test one machine before connecting a whole production line.'),
            text('Shared lives',
                 'When shared lives are on (default), each Clowder mate adds **three** lives to one team pool. A survival death spends one. Food and potions do not put it back. At zero, affected players become spectators.\n\n'
                 '`/skybound lives` prints the pool. Six quest rewards named **Thread of Return** each add one life when claimed. There is no item to use. Operators run `/skybound revive`. Plan trips together.'),
            text('Common traps',
                 'A Sky Stone Tank that you just moved is empty unless you bucketed first. Use a Spirit Cistern to carry liquids.\n\n'
                 'Pad-runners are in the March, not on the pad. After the Gate, Esther waits at `/clowder hub`.\n\n'
                 '**Check:** you have isolated one cause from this page, not rebuilt the whole workshop on a guess.')]),
    ]
    for i, lesson in enumerate(lessons):
        eid, title, icon, pages, *diagram = lesson
        if diagram:
            pages.append({'type':'modonomicon:multiblock','multiblock_id':f'{NS}:codex/{diagram[0]}',
                          'multiblock_name':'Placement example','text':'Example layout, not an exact quest requirement. Read the steps for materials and operation.',
                          'show_visualize_button':True})
        entry('first_steps',eid,title,'Practical steps and checks.',icon,(i%5)*2,(i//5)*3,pages,
              parents=[lessons[i-1][0]] if i else None)

    # Rendered block models use the same native book loader as other multiblocks.
    shapes = {
      'starter_workshop': ([['0 F','   ','B  '],['PPP','PPP','PPP']], {'0':'minecraft:crafting_table','F':'minecraft:furnace','B':'minecraft:chest','P':'minecraft:oak_planks'}),
      'water_pool': ([['SSSS','S0WS','SWWS','SSSS'],['SSSS','SSSS','SSSS','SSSS']], {'S':'minecraft:cobblestone','0':'minecraft:water','W':'minecraft:water'}),
      'material_workshop': ([['L 0 B','  S  ','     '],['PPPPP','PPPPP','PPPPP']], {'L':'minecraft:chest','0':'voidloom:loomframe','B':'voidloom:tension_barrel','S':'exdeorum:oak_sieve','P':'minecraft:oak_planks'}),
      'shatter_workshop': ([['D E',' 0 ','   '],['SSS','SSS','SSS']], {'D':'tribalpower:drumheart','E':'tribalpower:resonance_totem_earth','0':'tribalpower:echo_shatter','S':'minecraft:stone'}),
      'resonator_workshop': ([[' E ',' 0 ',' F '],['SSS','SSS','SSS']], {'E':'tribalpower:resonance_totem_earth','F':'tribalpower:resonance_totem_fire','0':'tribalpower:pulse_resonator','S':'minecraft:stone'}),
      'cistern_corner': ([['L0C','   '],['SSS','SSS']], {'L':'minecraft:lever','0':'tribalpower:spirit_cistern','C':'minecraft:comparator','S':'minecraft:stone'}),
    }
    data_root = book.parents[1]
    for key,(pattern,mapping) in shapes.items():
        write(data_root/'multiblocks'/'codex'/f'{key}.json', {'type':'modonomicon:dense','pattern':pattern,
              'mapping':{k:{'type':'modonomicon:block','block':v} for k,v in mapping.items()}})

    # Strand stages get a completion check. Workshop entries write their own.
    for path in (book/'entries'/'braid').glob('*.json'):
        obj=json.loads(path.read_text(encoding='utf-8'))
        check = STRAND_BRAID_CHECKS.get(path.stem)
        if not check:
            continue
        if any(p.get('title') == 'Before you move on' for p in obj.get('pages', [])):
            continue
        obj['pages'].append(text('Before you move on', check + '\n\n' + BRAID_TAIL))
        write(path,obj)


def sync_pack_primers(book, pack, write):
    names={'first_hour':('Dock, pad, first workshop.','Your first hour'),
           'the_campaign':('Two middle branches after Claw.','Two middle branches')}
    parents={'this_book':None,'first_hour':'this_book','tokens':'first_hour','the_campaign':'tokens'}
    for target,source in [('this_book','using_the_book'),('first_hour','safe_start'),('tokens','first_token'),('the_campaign','choose_branches')]:
        path=pack/'entries'/'the_work'/f'{target}.json'
        if not path.exists():continue
        obj=json.loads(path.read_text(encoding='utf-8'))
        teaching=json.loads((book/'entries'/'first_steps'/f'{source}.json').read_text(encoding='utf-8'))
        obj['pages']=teaching['pages']
        if target in names:
            obj['description'], obj['name'] = names[target]
        parent=parents.get(target)
        if parent:
            obj['parents']=[{'entry':f'{NS}:the_work/{parent}','draw_arrow':True,'line_enabled':True}]
        else:
            obj.pop('parents',None)
        write(path,obj)
    source=book.parents[1]/'multiblocks'/'codex'
    target=pack.parents[1]/'multiblocks'/'codex'
    for path in source.glob('*.json'):
        write(target/path.name,json.loads(path.read_text(encoding='utf-8')))


def paginate_pages(pages):
    """Keep native book pages short and use explicit Markdown breaks between paragraphs."""
    import re
    result=[]
    for page in pages:
        if page['type'] not in ('modonomicon:text','modonomicon:spotlight'):
            result.append(page); continue
        body=page.get('text','').replace('\\\n','\n')
        if not body.strip():
            result.append(page); continue
        paragraphs=[s.strip() for s in re.split(r'\n+',body) if s.strip()]
        groups=[]; current=[]; words=0
        limit=45 if page['type']=='modonomicon:spotlight' else 55
        for paragraph in paragraphs:
            # Split long prose at sentence boundaries, never in the middle of a numbered step.
            pieces=re.split(r'(?<=[.!?]) +(?=[A-Z*])',paragraph) if len(paragraph.split())>limit else [paragraph]
            for piece in pieces:
                if current and (words+len(piece.split())>limit or len(current)>=4):
                    groups.append(current);current=[];words=0;limit=55
                current.append(piece);words+=len(piece.split())
        if current:groups.append(current)
        for i,group in enumerate(groups):
            new=dict(page) if i==0 else {'type':'modonomicon:text','title':'Continue'}
            if i and 'condition' in page:
                new['condition']=page['condition']
            # Paragraph nodes do not insert spacing in the bundled renderer. Hard breaks do.
            new['text']='\\\n'.join(re.sub(r'^(\d+)\.',r'\1\\.',s) for s in group)
            if len(new.get('title',''))>20:
                mapped={
                    'Check before moving on':'Workshop check',
                    'Your two useful screens':'Book and quests',
                    'Check the power budget':'Power budget',
                    'A quest will not complete':'Quest checks',
                    'A machine will not work':'Machine checks',
                    'Words used in this book':'Words in this book',
                    'Three routes after Claw':'Three routes',
                    'Build the starter generator':'Starter generator',
                    'Shared lives and recovery':'Shared lives',
                    'Hands become a workshop':'Hands to workshop',
                    'Claw Blueprint Package':'Blueprint Package',
                    'The camp keeps the beat':'Camp drum',
                    'The halls that kept time':'Ancestor Halls',
                    'How the sky learns to hold':'How the sky holds',
                    'Public, or it does not count':'Keep it public',
                    'What you are not doing':'What you are not',
                    'Where the fallen came to rest':'March harbour',
                    'A schedule, not a mood':'A schedule',
                    'Maintenance, not peace':'Maintenance',
                    'Hearths as first physics':'Hearths first',
                    'The season the roots held':'Roots held',
                    'The Fray is the clock':'The Fray clock',
                    'Nine pulls, nine arguments':'Nine arguments',
                    'What Clock still knows':'What Clock knows',
                }
                new['title']=mapped.get(new['title'], new['title'][:20])
            result.append(new)
    return result


def polish_book(book,write):
    for path in (book/'entries').glob('*/*.json'):
        obj=json.loads(path.read_text(encoding='utf-8'))
        obj['pages']=paginate_pages(obj['pages'])
        write(path,obj)
