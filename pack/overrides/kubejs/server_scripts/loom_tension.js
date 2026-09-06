// Loom Tension — per-player craft milestones (not a nagging XP bar).
// Stored on player.persistentData as ncs_tension (int).
// Soft unlocks at 5 / 9 / 14 Tension. Hub plaque / server-wide flair = later optional.

const TENSION_KEY = 'ncs_tension'

const MILESTONES = [
  { at: 5, flag: 'ncs_tension_reward_1', item: '4x ninjacatskies:frayed_thread', msg: 'A scrap of Tension returns as Thread. Spend it wisely.' },
  { at: 9, flag: 'ncs_tension_reward_2', item: '2x ninjacatskies:codex_page', msg: 'Tension settles into Codex pages — Bind is near.' },
  { at: 14, flag: 'ncs_tension_reward_3', item: '1x ninjacatskies:braid_cord', msg: 'The Loom returns a spare braid. Reweave when ready.' },
]

const STRAND_POINTS = 1
const BRAID_POINTS = 3
const FRAGMENT_POINTS = 5

const STRAND_TOKENS = [
  'ninjacatskies:strand_token_soil',
  'ninjacatskies:strand_token_stone',
  'ninjacatskies:strand_token_sprout',
  'ninjacatskies:strand_token_claw',
  'ninjacatskies:strand_token_spark',
  'ninjacatskies:strand_token_clock',
  'ninjacatskies:strand_token_swarm',
  'ninjacatskies:strand_token_sigil',
  'ninjacatskies:strand_token_spindle',
]

function getTension(player) {
  return player.persistentData.getInt(TENSION_KEY) || 0
}

function setTension(player, value) {
  player.persistentData.putInt(TENSION_KEY, value)
}

function addTension(player, amount, actionbar) {
  const next = getTension(player) + amount
  setTension(player, next)
  player.displayClientMessage(actionbar, true)
  player.displayClientMessage(`Loom Tension: ${next}`, true)
  maybeSoftUnlock(player, next)
}

function maybeSoftUnlock(player, tension) {
  const data = player.persistentData
  for (const m of MILESTONES) {
    if (tension >= m.at && !data.getBoolean(m.flag)) {
      data.putBoolean(m.flag, true)
      player.give(m.item)
      player.displayClientMessage(m.msg, true)
    }
  }
}

ItemEvents.crafted(event => {
  const id = String(event.item.id)
  const player = event.player
  if (!player) return

  if (STRAND_TOKENS.includes(id)) {
    addTension(player, STRAND_POINTS, 'Strand tensioned. The Loom hums faintly.')
    return
  }

  if (id === 'ninjacatskies:braid_cord') {
    const data = player.persistentData
    if (data.getBoolean('ncs_tension_braid')) return
    data.putBoolean('ncs_tension_braid', true)
    addTension(player, BRAID_POINTS, 'Braid holds. Tension climbs.')
    return
  }

  if (id === 'ninjacatskies:spindle_loom_fragment') {
    const data = player.persistentData
    if (data.getBoolean('ncs_tension_fragment')) return
    data.putBoolean('ncs_tension_fragment', true)
    addTension(player, FRAGMENT_POINTS, 'Spindle fragment set. The cut remembers.')
  }
})
