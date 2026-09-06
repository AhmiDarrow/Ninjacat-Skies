// Codex-voice steward whispers on first obtain of each Strand token.
// Optional: ninjacatskies:codex_page every 3rd unique token.
const STEWARD = {
  soil: {
    tribe: 'Pad-keepers',
    lines: [
      'Soil answers. Pad-keepers once banked hearth-warmth in dirt this thin.',
      'Claim the pad. Cache what grows. Wake is not a race.',
    ],
  },
  stone: {
    tribe: 'Grit-singers',
    lines: [
      'Stone hums under the sieve. Grit-singers named every shard by echo.',
      'Shatter grit; knot yarn. Recover what the cut left scattered.',
    ],
  },
  sprout: {
    tribe: 'Rootbinders',
    lines: [
      'Sprout takes hold. Rootbinders grew living anchors where pads would drift.',
      'Food is infrastructure. Root before you wander.',
    ],
  },
  claw: {
    tribe: 'Edge-walkers',
    lines: [
      'Claw finds the rim. Edge-walkers kept footholds beyond the pad.',
      'Kit up. Leave safely. The void does not forgive soft soles.',
    ],
  },
  spark: {
    tribe: 'Drumhearts',
    lines: [
      'Spark wakes a pulse. Drumhearts left orphan engines humming in the cut.',
      'Rhythm first—Tribal Power as primary hum. Bridge FE later if you must.',
    ],
  },
  clock: {
    tribe: 'Pattern-weavers',
    lines: [
      'Clock repeats. Pattern-weavers sang factory as loom song.',
      'Gear is a braid strand—peer to Swarm and Spark, not a ladder rung.',
    ],
  },
  swarm: {
    tribe: 'Colony-keepers',
    lines: [
      'Swarm thickens. Colony-keepers tended living industry in the March\'s shadow.',
      'Bees and deep crops braid beside Clock. Specialize; do not choke.',
    ],
  },
  sigil: {
    tribe: 'Seal-carvers',
    lines: [
      'Sigil bites. Seal-carvers left rites where stewards once bound spirit to matter.',
      'Bind with leftover Tribal tricks. Peer magic still answers if called.',
    ],
  },
  spindle: {
    tribe: 'Loom-stitchers',
    lines: [
      'Spindle draws taut. Loom-stitchers cut gate-paths and meant to reweave.',
      'Stitch the cut—digital loom, March foothold, trophy. Reweave finishes the braid.',
    ],
  },
}

const PAGE_EVERY = 3
const FLAG_PREFIX = 'ncs_steward_'
const COUNT_KEY = 'ncs_steward_count'

Object.keys(STEWARD).forEach(name => {
  PlayerEvents.inventoryChanged(`ninjacatskies:strand_token_${name}`, event => {
    const player = event.player
    if (player.level.isClientSide()) return

    const data = player.persistentData
    const flag = FLAG_PREFIX + name
    if (data.getBoolean(flag)) return
    data.putBoolean(flag, true)

    const entry = STEWARD[name]
    player.tell(Text.of(entry.lines[0]).color(0x3D7A7A))
    player.tell(Text.of(entry.lines[1]).color(0xD4A84B))

    const count = data.getInt(COUNT_KEY) + 1
    data.putInt(COUNT_KEY, count)
    if (count % PAGE_EVERY === 0) {
      player.give('ninjacatskies:codex_page')
      player.tell(Text.of(`A Codex Page slips free — ${entry.tribe} margin note.`).color(0x2A2F4F))
    }
  })
})
