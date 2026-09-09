# Woven Relics — the 13 boss rewards

One relic per Snapped Guardian. On a win, **every Clowder member present gets their own copy** (granted straight to inventory, no shared drop). Each is a trophy with one small, on-theme power. Tuned so none of them trivialise the pack: every active power sits on a cooldown, and the two insane-boss relics are the only ones that feel "endgame".

Files: `relics/tex16/<id>.png` are the 16×16 item textures (ready to drop into `assets/ninjacatskies/textures/item/`), `relics/renders/<id>.png` are the 3D showcase renders (for the Codex / quest reward art), `relics/showcase.py` regenerates the renders, `relics/pixel.py` regenerates the textures.

All relics: rarity **Epic** (Loomthread, First Cut shard and Overweaver's Shuttle **Legendary**), unbreakable, not craftable, not tradeable via villagers, one per player per kill (re-kills give a Frayed Thread cosmetic instead). They live in the off-hand or a Curios "relic" slot (pack already ships Curios via other mods; a dedicated `relic` slot type is a one-line data file). Passive effects only apply while the relic is in that slot; actives are used by right-click from the slot's keybind or held in hand.

## The nine Strand relics

### Rootheart (Soil — the Beddown)
Teal heart-crystal bound in living roots, a gold stitch down its cut-seam.
- **Passive — Anchored.** Knockback taken −60 %, and you cannot be pulled by fishing rods / leashes / vortex effects.
- **Active — Root Down (right-click, 30 s cd).** For 5 s you are rooted in place: 8 hearts of absorption, immune to fall damage on landing, and any mob that hits you gets Slowness II for 3 s. Cancelled early by sneaking.
- **Effect.** Roots burst out of the ground around your feet (brown `composter` + teal `glow` particles), a soft low thud. The heart pulses teal in the icon while Root Down is up.

### Grindcore (Stone — the Grindmaw)
Millstone gear with a teal grit-core and brass channels; stone chips fly off the rim.
- **Passive — Grit.** Mining fatigue immunity; +1 fortune-style bonus roll on Ex Deorum sieve outputs while worn (rewards the sieve loop the boss taught).
- **Active — Shred (25 s cd).** Next melee hit within 6 s strips 2 armour points from the target for 8 s and breaks up to 4 shield/ward blocks around it (boss ward blocks, obsidian excluded). 
- **Effect.** Grinding rasp sound, ring of `crit` + grey `block_crumble` particles, the gear icon spins in the hotbar for the 6 s window.

### Thornseed (Sprout — the Thornmother)
Green seed-pod with glowing teal veins, gold thorns, sepal leaves and a sprouting tendril.
- **Passive — Bramble Skin.** Thorns I (attackers take 1 heart) and immunity to berry-bush / cactus contact damage.
- **Active — Bloom (40 s cd).** Grows a 5-block-wide ring of thorn-hedge blocks (a real block, `ninjacatskies:thorn_hedge`, breaks in ~20 s or when walked into by the owner) around you, and gives Regeneration II for 6 s to you and Clowder-mates inside it.
- **Effect.** Leaf-burst (`happy_villager` green + teal `glow`), a wet snap sound; hedge blocks glow along their veins.

### Edgestep (Claw — the Edgewalker)
Black cat-claw sickle with a gold cutting edge and cord-wrapped haunch; gold afterimage streaks.
- **Passive — Cat's Landing.** No fall damage from ≤ 12 blocks; sneaking on an edge won't slip you off.
- **Active — Edgestep (12 s cd, 2 charges).** Dash 6 blocks in the look direction (works in air = a directional double-jump). i-frames for 0.3 s during the dash. Hitting a mob at the end of the dash deals +50 % damage.
- **Effect.** Gold afterimage of the player (client-side ghost render), `sweep_attack` + gold `end_rod` trail, quick cloth-whip sound.

### Drumpulse (Spark — the Drumheart)
Brass-hooped drum with a glowing, ringed skin; a mallet frozen mid-beat and a shockwave ring.
- **Passive — On the Beat.** Every 4th hit you land deals +2 hearts bonus and plays a drum hit.
- **Active — Downbeat (35 s cd).** Slam: all mobs within 7 blocks are stunned (no AI, no attacks) for 2 s and knocked back; Create mechanisms in range get a 3 s speed burst (cosmetic + a little free stress).
- **Effect.** Expanding orange shock-ring (three staggered `flame`/`lava` rings), screen shake for the owner, deep drum boom.

### Cogloop (Clock — the Cogwright)
Brass gear-ring with a teal clock-core and gold hands; a smaller cog trails behind.
- **Passive — Wound Tight.** Haste I while worn; tools lose durability 20 % slower.
- **Active — Rewind (60 s cd).** Resets the cooldown of every other relic you carry and refills your Edgestep charges; also snaps your position back to where you stood 3 s ago (a small blink-back, Chronos-style).
- **Effect.** Clock ticks speed up then a single chime; the cog icon spins backwards; teal tick-marks `enchant` particles orbit you.

### Hivecall (Swarm — the Hivemind)
Hexagonal honeycomb amulet, cells brimming with glowing honey, the queen's bee in front, three drones circling.
- **Passive — Keeper.** Bees never aggro you; Productive Bees / vanilla hives near you (16 blocks) tick 10 % faster.
- **Active — Call the Swarm (45 s cd).** Summon 4 friendly relic-bees for 20 s that harass whatever you hit; each bee sting applies Poison I 2 s and they pop into 1 honey bottle each when they expire (so the ability also gives a trickle of honey).
- **Effect.** Buzzing swell, gold `falling_honey` + `wax_on` particles, bees leave faint gold lanes.

### Sealmark (Sigil — the Sealbreaker)
Violet stone tablet engraved with a gold ward-sigil and teal eye, hex ward-plates hovering around it.
- **Passive — Warded.** Magic damage taken −20 % (Ars spells, potions, wither, dragon breath).
- **Active — Sealmark (50 s cd).** Place a ward on yourself: the next hit that would deal ≥ 3 hearts is negated entirely, once. The ward lasts 20 s or until spent. Casting it on a Clowder-mate by looking at them within 8 blocks wards them instead.
- **Effect.** Teal hex-plate shell flashes into place (`ars` glyph-style particles), a glass chime; when the ward breaks, a shatter sound and the plates fly off.

### Loomthread (Spindle — the Unwoven)
Gold spool wound with glowing teal thread, a faceted gold keystone floating above, thread trailing to the ground.
- **Passive — Re-woven.** +2 max Loom Tension for your Clowder (the shared pool the pack already tracks) and Tension decays 25 % slower.
- **Active — Loomthread (90 s cd).** Tether: pulls every Clowder-mate within 24 blocks to your side (no cross-dimension), gives everyone Resistance I for 5 s.
- **Keystone.** Also a crafting ingredient: 1 Loomthread + the Reweave Ring recipe = the true Reweave (the finale), and it's the key that opens the sealed door to the two insane arenas. Consumed only in the Reweave craft, not by the tether.
- **Effect.** Teal threads snap out to each mate and reel them in (`end_rod` lines), loom-shuttle clack sound.

## The two easy (optional) relics

### Lintwisp (the Lint Golem)
A tuft of grey fluff with two gold button eyes and a loose thread.
- **Passive — Soft.** Immune to cactus/sweet-berry/thorn-hedge damage and to being pushed by other players. Purely a "you did your first boss" trophy with a tiny perk.
- **Active — Puff (20 s cd).** A harmless cloud of lint that blinds nearby mobs (Blindness 4 s) — great for escaping, does no damage.
- **Effect.** Grey `poof` cloud, sneeze sound.

### Knotcharm (the Tangle)
A rope trefoil knot with a teal core thread and a gold charm-tag.
- **Passive — Sure-footed.** No slowdown on cobwebs, soul sand, honey, or powder snow; −50 % slip on ice.
- **Active — Tangle (30 s cd).** Throws a knot: the first mob hit is bound (rooted, can still attack) for 4 s.
- **Effect.** Rope-creak sound, gold rope-loop particle around the target.

## The two insane relics (locked behind all nine Reweaves)

### Shard of the First Cut
A faceted obsidian shard split by a glowing gold cut-seam, a teal rip of void behind it, fragments floating.
- **Passive — Severed.** Your melee hits ignore 30 % of the target's armour and 100 % of boss ward phases (you can damage Guardians during their "immune" windows for 25 % damage).
- **Active — The Cut (120 s cd).** Slash a 6-block line in front of you: every mob in it takes 12 hearts true damage; players (friendly fire off) are unharmed. Also cuts through any boss projectile in the line.
- **Effect.** The screen briefly tears along the slash line (a gold seam post-effect for 0.4 s), glass-shatter + low drone, teal void particles pour from the seam.

### Overweaver's Shuttle
Violet loom-shuttle with gold tips, a windowed body showing the bobbin wound with glowing gold thread, nine strands fanning out beneath it.
- **Passive — Nine Strands.** Carries a weakened echo of every Strand relic passive at once (knockback −30 %, Thorns I, Haste I, magic −10 %, bees passive, cat's landing to 8 blocks, etc.). This is the "one relic to wear" endgame trinket.
- **Active — Reweave (180 s cd).** For 10 s every Clowder-mate within 16 blocks shares your buffs, takes 20 % less damage, and any downed mate (the pack's shared-lives system) within range is revived at half health once.
- **Effect.** Nine coloured threads (teal/gold alternating) shoot from the shuttle to every mate, a rising loom-chorus sound, the shuttle icon shows the bobbin unwinding.

## Balance notes
- Actives are strong but cooldown-bound; nothing here out-damages endgame Create/Ars kit. Edgestep and Cogloop are the two people will "build around"; keep their numbers conservative first.
- Grindcore's sieve bonus and Hivecall's hive speed are the only economy effects, both small and capped to "while worn".
- Loomthread being the Reweave key means the finale relic can't be skipped, which matches the totem gate design.
- The two insane relics are meant to make the *next* run of the nine easy — that's the intended reward for the "nearly impossible" fights.

## Implementation notes
- Items: `ninjacatskies:relic_<id>` (13 items), all extend one `RelicItem` with `RelicPower` data (cooldown, passive attribute modifiers, active handler). Cooldowns via `Player.getCooldowns()` so they show on the hotbar icon natively.
- Team-fair drop: on boss death, iterate the party's online members in the arena (`FtbParties` mirror from Clowder Hall 0.6.5) and `player.getInventory().placeItemBackInInventory(new ItemStack(relic))`, dropping at the player's feet if full.
- Textures: 16×16 PNGs in this folder are final; item models are the standard `item/generated` layer0. Enchant-glint off (they glow enough); use a custom `foil` shader later if wanted.
- Save-safe: all new item IDs, no changes to existing ones.
