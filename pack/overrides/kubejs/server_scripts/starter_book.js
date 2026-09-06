// OOC first-join starter book — plain how-to-start, once per player.
// Complements lectern / dock chest copies; does not replace Whisker Codex voice.
// Keep in sync with island chest howto pages and Hall book.

const STARTER_BOOK_FLAG = 'ncs_starter_howto_v4'
const STARTER_TITLE = 'How to Start'

function starterPages() {
  return [
    'HOW TO START (read me)\n\nYou are on Clowder Dock — the shared hub, not your forever island.\n\nGoal: open Create Team, pick a pad template, then open quests.',
    'CLAIM A PAD (guided)\n\n1) Right-click your Island Charter ON THE DOCK\n   (or press C — Sky GUIs key)\n2) Click Create Team\n3) Type a Clowder name\n4) Pick a pad template:\n   Ninjacat Pad = Normal (start here)\n   Dojo Cottage = Easy\n   Frayed Thread = Hard\n5) Click Create — you teleport\n\nDo NOT use chat create if you want to pick a pad —\n/skyblock create <name> skips the picker.\n\nDock: Charter opens Create Team.\nPad: Charter seals spawn here.\nHall: Hub Key toggles leave — Create Team is Dock-only.',
    'QUESTS\n\nOpen FTB Quests (quest book key / inventory button).\nStart Soil (Wake). Do not skip ahead.\n\nEasy ships water already.\nNormal/Hard: ice + lava + empty bucket.\nPlace lava, melt ice into water, fill bucket.\n\nStone / Recover:\n1) Unravel Frayed Thread → 3 string\n2) Craft 4 string → 2 Void Yarn\n3) Spindle Hammer = cobble + sticks\n4) Tension Barrel: water+dirt → clay (bucket returns to you)\n5) Porcelain clay → smelt porcelain bucket\n6) Then sieve grit; slime = dirt+seeds+meal\n\nWhisker Codex is the in-world guide.',
    'HELPFUL COMMANDS\n\n  /clowder help\n  /clowder hub     → Clowder Hall dimension\n  /clowder return  → leave Hall to your pad\n  /clowder revive  → self if spectator (soft hardcore)\n  /clowder revive <mate> → pull a teammate back\n  /skyblock home   → your pad\n  /skyblock create <name>  → advanced (skips pad pick)\n\nOps: /skybound revive [player]\nHub Key toggles Hall enter/leave.\nLost? Charter seals spawn on pad; hub is always safe.',
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
