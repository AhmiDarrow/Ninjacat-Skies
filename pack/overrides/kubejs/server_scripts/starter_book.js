// OOC first-join starter book — plain how-to-start, once per player.
// Complements lectern / dock chest copies; does not replace Whisker Codex voice.
// Keep in sync with island chest howto pages and Hall book.

const STARTER_BOOK_FLAG = 'ncs_starter_howto_v5'
const STARTER_TITLE = 'How to Start'

function starterPages() {
  return [
    'HOW TO START (read me)\n\nYou are on Clowder Dock — the shared hub, not your forever island.\n\nGoal: open Create Team, pick a pad template, then open quests.',
    'CLAIM A PAD (guided)\n\n1) Right-click your Island Charter ON THE DOCK\n   (or press C — Sky GUIs key)\n2) Click Create Team\n3) Type a Clowder name\n4) Pick a pad template:\n   Ninjacat Pad = Normal (start here)\n   Dojo Cottage = Easy\n   Frayed Thread = Hard\n5) Click Create — you teleport\n\nDo NOT use chat create if you want to pick a pad —\n/skyblock create <name> skips the picker.\n\nDock: Charter opens Create Team.\nPad: Charter seals spawn here.\nHall: Hub Key toggles leave — Create Team is Dock-only.',
    'QUESTS\n\nOpen FTB Quests (quest book key / inventory button).\nStart Soil (Wake). Each Strand chapter ends in a KNOT quest that gives a Strand token.\n\nRight-click the Whisker Codex for the story book; sneak-click for the next step.\n\nEasy ships water already.\nNormal/Hard: ice + lava + empty bucket.\nPlace lava, melt ice into water, fill bucket.',
    'TENSION POST\n\nCraft: logs around a Binding Knot, Thread on top.\nPlace it on your pad.\nRight-click it with a Strand token to SEAT it.\n\nSeated Strands = Loom Tension. The pad heals you near the Post, feeds you after Sprout, catches falls after Claw.\n\nBraid Cord: Post + Strand Filament (2 of Clock/Swarm/Spark seated).\nLoom Fragment: Post + March stone (all nine seated). Seat the Fragment to Reweave.',
    'STONE / RECOVER\n\n1) Unravel Frayed Thread -> 3 string\n2) 4 string -> 2 Void Yarn\n3) Spindle Hammer = cobble + sticks\n4) Tension Barrel: pour water (bucket returns), add up to 8 dirt -> clay\n5) Porcelain clay -> smelt porcelain bucket\n6) Loomframe: mesh + dirt/gravel, it sifts on its own; hoppers work\n7) Then Ex Deorum sieves. Slime = dirt+seeds+meal',
    'HELPFUL COMMANDS\n\n  /clowder help\n  /clowder hub     → Clowder Hall dimension\n  /clowder return  → leave Hall to your pad\n  /skybound lives → shared team life pool\n  Rare late quests → +1 shared life (six total)\n  /skyblock home   → your pad\n  /skyblock create <name>  → advanced (skips pad pick)\n\nOps: /skybound revive [player]\nHub Key toggles Hall enter/leave.\nLost? Charter seals spawn on pad; hub is always safe.',
    'WHAT IS THIS PACK?\n\nVoid skyblock + Loom Braid quests.\nTribal Power (drums / Pulse / March) is a core pillar — not a side mod.\n\nThis book is OOC on purpose. Signs & Codex stay in-voice.',
  ]
}

function makeStarterBook() {
  // 1.21 written_book_content: title/pages use Filterable {raw:...} form.
  const pages = starterPages().map((text) => ({ raw: JSON.stringify({ text: text }) }))
  return Item.of('minecraft:written_book', {
    'minecraft:written_book_content': {
      pages: pages,
      title: { raw: STARTER_TITLE },
      author: 'Skybound Field Desk',
      generation: 0,
      resolved: true,
    },
  })
}

PlayerEvents.loggedIn((event) => {
  const player = event.player
  if (player.persistentData.getBoolean(STARTER_BOOK_FLAG)) return
  player.persistentData.putBoolean(STARTER_BOOK_FLAG, true)

  try {
    player.give(makeStarterBook())
  } catch (e) {
    // Fallback: tell the player where the lectern/chest copy lives if component give fails.
    player.tell(Text.red('[Skybound] Could not place How to Start in inventory — read the Dock lectern / chest book.'))
  }
  player.tell(Text.gold('[Skybound] How to Start — read it before claiming a pad.'))
  player.tell(Text.aqua('[Skybound] Right-click Island Charter (or press C) → Create Team → pick a pad.'))
})
