"""Practical lessons and native placement diagrams for the Whisker Codex."""
import json
from pathlib import Path

NS = 'ninjacatskies'


def build_lessons(book, write, text, entry, category):
    category('first_steps', 'Start here', f'{NS}:whisker_codex', 0,
             'A safe start, working examples, and what to do when progress stops.')
    lessons = [
        ('using_the_book', 'Using the Codex', 'ninjacatskies:whisker_codex', [
            text('Your two useful screens', 'Use the **Whisker Codex** to learn a system before building it. Open the quest screen with the **Grave / backtick** key to see tasks, requirements and rewards. If you changed your controls, search Controls for Quests.\n\nStart with **Start here**. **The Loom Braid** explains the campaign stages. The story chapters are there when you want to learn about the world.'),
            text('Read, build, check', 'Each practical lesson gives you a goal, a short sequence and a way to check the result. Follow the arrows between entries.\n\nFor exact crafting ingredients, hover an item in your inventory or the item list and open its recipe. Recipes can change with the pack; a build diagram shows placement, not a crafting recipe.'),
            text('Words used in this book', '**Pad:** your floating island.\n**Clowder:** your player team.\n**Strand:** one part of the campaign.\n**Token:** the reward proving you completed a Strand.\n**Seat:** right-click a Tension Post with a token.\n**Pulse:** the energy used by Tribal Power.\n\nYou do not need to remember the lore to follow the instructions.')]),
        ('safe_start', 'Your first safe workshop', 'minecraft:crafting_table', [
            text('Goal and supplies', '**Goal:** a safe place to grow a tree, craft, store items and cook food.\n\nAt the Dock, use your Island Charter to open the island/team screen. Join your existing team or create one, then choose your pad.\n\nKeep a sapling, some dirt and the starter supplies. Open the Soil quests before spending rare starter items.'),
            text('Build in this order', '1. Widen your platform. Add edges and light.\n2. Harvest wood. Keep a replacement sapling and replant it on dirt.\n3. Make a crafting table and chest. Store spare saplings and valuables.\n4. Make a furnace. Cook food as the Soil quests request. Keep walkways clear.'),
            text('Check before moving on', 'You should have a replanted tree, spare materials in storage, food and a workspace you can walk around safely.\n\nThe model on the next page is one compact arrangement. Build a larger platform around it. The exact arrangement is optional; the diagram is not a quest requirement. Keep fire and lava away from wooden floors.')], 'starter_workshop'),
        ('water', 'Keep a water supply', 'minecraft:water_bucket', [
            text('Make the first source', 'Easy pads include water. Normal and Hard pads supply ice, lava and an empty bucket.\n\n1. Make a contained area from nonflammable blocks.\n2. Put the ice where the water should remain. Use nearby lava as the heat source, with blocks containing its flow.\n3. Let the ice melt. Collect the resulting water source with the bucket.\n\nKeep lava away from wood and stored items. Do not let the two liquids flow together.'),
            text('A refillable pool', '**Once you have two water source buckets**, build the four-block pool shown next. Fill opposite corners. On ordinary water-source rules, all four spaces become sources.\n\nCollect a bucket and check that the pool refills before relying on it. One source alone is not enough for this layout.\n\nKeep water available for the Tension Barrel and farming.')], 'water_pool'),
        ('first_token', 'Finish and seat Soil', 'ninjacatskies:strand_token_soil', [
            text('Complete the chapter', '1. Open the quest screen and work through Soil. Read each task: some need you to hold an item; others ask you to craft or perform an action.\n2. Claim the **Soil Knot** reward when its tasks are complete.\n3. Craft and place a **Tension Post** using its current recipe.\n4. Right-click the Post with the Soil Strand token.'),
            text('Check the Post', 'The Soil notch should light and your team gains the seated Strand. Completing a quest and seating its token are separate steps.\n\nIf the notch stays dark, check that you claimed the token and are holding the right item. Team progress is shared; you do not need a separate Post for every player.\n\nNext: Recover introduces the Loomframe, barrel and material processing.')]),
        ('materials', 'Build a material supply', 'voidloom:loomframe', [
            text('Goal and sequence', '**Goal:** turn basic resources into materials for the next chapter.\n\n1. Unravel Frayed Thread into string when you need it. Keep some Thread for trading.\n2. Follow recipes for Void Yarn, a Binding Knot and a Loomframe.\n3. Make a Tension Barrel and keep water nearby.\n4. Follow Recover for clay, porcelain and the route to handling lava.'),
            text('Test small batches', 'Read the Loomframe and barrel recipes before adding items. Start with one batch and check the output. Keep the input and result in separate storage until you know the process.\n\nThen work towards sieving and better meshes. An iron mesh opens the route to Strand Filament. Follow the active quests and recipes for the exact substrate and mesh combination.\n\nThe next model is a workspace example; adjacent placement alone does not automate these stations.')], 'material_workshop'),
        ('first_power', 'Make the first Echo Shard', 'tribalpower:echo_shatter', [
            text('Goal and supplies', '**Goal:** make an Echo Shard for an automatic generator.\n\nYou need Echo Shatter, an Earth Resonance Totem, a Drumheart and **stone**, not cobblestone. Smelt cobblestone if necessary.\n\nUse the Spirit Codex for detailed Tribal Power recipes, diagrams and troubleshooting.'),
            text('Build and run it', '1. Place the drum and Earth totem beside Echo Shatter, within 8 blocks.\n2. Right-click the drum with an empty hand about once a second. Build a reserve of Pulse.\n3. Put stone into Shatter and leave output space.\n4. Wait for an Echo Shard. If it stops, charge the drum again and inspect the station with the Spirit Codex.\n\nCobblestone becomes gravel instead. A slow generator can finish a batch using stored energy.')], 'shatter_workshop'),
        ('automatic_power', 'Start automatic power', 'tribalpower:pulse_resonator', [
            text('Build the starter generator', 'You need a **Pulse Resonator**, an **Echo Shard**, and **Earth and Fire Resonance Totems**.\n\n1. Place the Resonator.\n2. Right-click it with the shard to install the reusable catalyst.\n3. Place the two different totems within 8 blocks. The diagram shows a compact example.\n4. Wait a second and inspect the generator. Stored Pulse should rise.'),
            text('Check the power budget', 'The starter generator makes a small amount of Pulse continuously. It does not mean every machine can run continuously. If a machine spends power faster than you make it, let a reserve build up or improve generation.\n\nTwo identical totems count as one element. If generation stops, check the catalyst, different elements and pausing redstone.\n\nRead the Spirit Codex before building larger totem layouts or a Conductor.')], 'resonator_workshop'),
        ('choose_branches', 'Choose two middle branches', 'ninjacatskies:braid_cord', [
            text('Three routes after Claw', 'After the Claw stage, you can work on three branches:\n\n**Pattern / Clock:** mechanical processing.\n**Colony / Swarm:** bees and their production chains.\n**Hum / Spark:** living power and workshops.\n\nComplete and seat **any two** of these three Strands to unlock Braid Cord. A team can divide the work. You will still need all nine Strands for the final reweave.'),
            text('Make Braid Cord', '1. Check that two of Clock, Swarm and Spark are seated at your Post. Merely holding their tokens is not enough.\n2. Hold a **Strand Filament**.\n3. Right-click the Post to receive **Braid Cord**.\n\nDo not put tokens in a crafting grid. They record progress. If the Post refuses, read its message and check which Strands are seated.\n\nNext: follow Bind and the Sigil quests.')]),
        ('finish', 'Prepare the final reweave', 'ninjacatskies:spindle_loom_fragment', [
            text('Readiness checklist', 'Finish the remaining quest branches and seat all **nine** Strand tokens. Count the Post notches before leaving for the final materials.\n\nPrepare food, equipment and a return route before entering the March. Bring back **March Stone**. Read the Spirit Codex for the Gate Drum and March travel details.'),
            text('Use the Post twice', '1. With all nine Strands seated, right-click the Tension Post with March Stone. This makes a **Spindle Loom Fragment**.\n2. Right-click the Post again, this time holding the Fragment, to reweave your team\'s sky.\n\nThese are world interactions, not crafting-table recipes. If nothing happens, check the Post message and the nine seated Strands. Other teams have their own progress.')]),
        ('stuck', 'When progress stops', 'minecraft:book', [
            text('A quest will not complete', 'Read the exact task and its prerequisites. Check item counts, variants and whether the task wants possession, crafting or another action. Try the task\'s detect button when one is available.\n\nCheck rewards too: an unclaimed token cannot be seated. If playing together, confirm you are in the intended Clowder before repeating a long crafting chain.'),
            text('A machine will not work', 'Check these separately:\n1. Correct input and recipe.\n2. Available power and range.\n3. Required totem or other structure.\n4. Space for the result.\n5. Pausing redstone and side settings.\n\nFor Tribal Power, crouch and right-click the machine with the Spirit Codex. Test one machine before connecting a whole production line.'),
            text('Shared lives and recovery', 'When shared lives are enabled, survival deaths spend the Clowder\'s pool. At exhaustion, affected players become spectators. Ordinary food or healing does not restore a spent life.\n\nRare campaign rewards can add lives; a recovery item or operator revive may be needed. Check the quest screen and the recovery item\'s instructions. Plan dangerous trips together and store spare supplies before leaving.')]),
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
      'starter_workshop': ([['C F',' 0 ','B  '],['PPP','PPP','PPP']], {'C':'minecraft:crafting_table','F':'minecraft:furnace','0':'ninjacatskies:tension_post','B':'minecraft:chest','P':'minecraft:oak_planks'}),
      'water_pool': ([['SSSS','S0WS','SWWS','SSSS'],['SSSS','SSSS','SSSS','SSSS']], {'S':'minecraft:cobblestone','0':'minecraft:water','W':'minecraft:water'}),
      'material_workshop': ([['L 0 B','     ','     '],['PPPPP','PPPPP','PPPPP']], {'L':'minecraft:chest','0':'voidloom:loomframe','B':'voidloom:tension_barrel','P':'minecraft:oak_planks'}),
      'shatter_workshop': ([['D E',' 0 ','   '],['SSS','SSS','SSS']], {'D':'tribalpower:drumheart','E':'tribalpower:resonance_totem_earth','0':'tribalpower:echo_shatter','S':'minecraft:stone'}),
      'resonator_workshop': ([[' E ',' 0 ',' F '],['SSS','SSS','SSS']], {'E':'tribalpower:resonance_totem_earth','F':'tribalpower:resonance_totem_fire','0':'tribalpower:pulse_resonator','S':'minecraft:stone'}),
    }
    data_root = book.parents[1]
    for key,(pattern,mapping) in shapes.items():
        write(data_root/'multiblocks'/'codex'/f'{key}.json', {'type':'modonomicon:dense','pattern':pattern,
              'mapping':{k:{'type':'modonomicon:block','block':v} for k,v in mapping.items()}})

    # Every campaign stage gets a clear completion check alongside its narrative.
    for path in (book/'entries'/'braid').glob('*.json'):
        obj=json.loads(path.read_text(encoding='utf-8'))
        if path.stem=='living_lattice':continue
        obj['pages'].append(text('Before you move on', 'Open this stage in the quest screen. Complete its required tasks, claim the reward and seat its Strand token at the Tension Post. Check that the matching notch lights.\n\nRead **Start here** for worked examples. Recipes show the current ingredients; the Spirit Codex covers Tribal Power machinery. If you get stuck, test one recipe at a time and read the machine\'s diagnostic message.'))
        write(path,obj)


def sync_pack_primers(book, pack, write):
    for target,source in [('this_book','using_the_book'),('first_hour','safe_start'),('tokens','first_token'),('the_campaign','choose_branches')]:
        path=pack/'entries'/'the_work'/f'{target}.json'
        if not path.exists():continue
        obj=json.loads(path.read_text(encoding='utf-8'))
        teaching=json.loads((book/'entries'/'first_steps'/f'{source}.json').read_text(encoding='utf-8'))
        obj['pages']=teaching['pages']
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
                new['title']={'Check before moving on':'Workshop check','Your two useful screens':'Book and quests','Check the power budget':'Power budget','A quest will not complete':'Quest checks','A machine will not work':'Machine checks'}.get(new['title'],new['title'][:17]+'...')
            result.append(new)
    return result


def polish_book(book,write):
    for path in (book/'entries').glob('*/*.json'):
        obj=json.loads(path.read_text(encoding='utf-8'))
        obj['pages']=paginate_pages(obj['pages'])
        write(path,obj)
