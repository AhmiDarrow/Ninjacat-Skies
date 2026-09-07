// Rootbinders' kitchen — Farmer's Delight crops on a void pad.
// FD's cabbage and tomato only come from wild plants that generate in the world (and tomato seeds craft from a
// tomato you don't have yet — circular). Onion is fine: zombies drop it. So the missing seeds fall from the
// sieve alongside the vanilla ones, and cabbage leaf too, so the kitchen line is reachable from Root.
ServerEvents.recipes(event => {
  const sieve = (input, mesh, result, p, compressed) => {
    event.custom({
      type: compressed ? 'exdeorum:compressed_sieve' : 'exdeorum:sieve',
      ingredient: { item: input },
      mesh: { item: mesh },
      result: { id: result, count: 1 },
      result_amount: { type: 'minecraft:binomial', n: 1.0, p: p },
    }).id(`ninjacatskies:farmers/${compressed ? 'compressed_' : ''}${input.split(':')[1]}_${mesh.split(':')[1]}_${result.split(':')[1]}`)
  }
  const both = (input, mesh, result, p) => {
    sieve(input, mesh, result, p, false)
    sieve(input, mesh, result, Math.min(1, p * 4), true)
  }

  // Seeds from dirt, like the vanilla ones Ex Deorum already sieves. String mesh so Root can start.
  ;['exdeorum:string_mesh', 'exdeorum:flint_mesh', 'exdeorum:iron_mesh'].forEach((m, i) => {
    const p = 0.05 + i * 0.02
    both('minecraft:dirt', m, 'farmersdelight:tomato_seeds', p)
    both('minecraft:dirt', m, 'farmersdelight:cabbage_seeds', p)
    both('minecraft:dirt', m, 'farmersdelight:rice', p)
  })

  // A cabbage seed grows cabbage, but the "from leaves" craft also wants leaves — let a leaf come off the sieve too.
  both('minecraft:dirt', 'exdeorum:flint_mesh', 'farmersdelight:cabbage_leaf', 0.05)

  // Onion is a zombie drop, but a seed on the sieve keeps a peaceful pad in the kitchen too.
  both('minecraft:dirt', 'exdeorum:flint_mesh', 'farmersdelight:onion', 0.04)
})
