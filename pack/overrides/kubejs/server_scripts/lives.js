// The repeatable life: four Thread Shards stitch into a Thread of Return (+1 shared Clowder life).
// The six quest "Thread of Return" rewards stay one-per-Clowder; this path is priced, not counted.
// Shard = one Rift Shard (a Remnant kill) plus real materials. The Spark stall sells shards for Thread
// instead, so a Clowder can pay in fights or in currency — see dock_shop/spark_thread_shard.json.
ServerEvents.recipes(event => {
  if (!Item.exists('driftwrecks:rift_shard')) return
  event.shaped('ninjacatskies:thread_shard', [
    'DYD',
    'YRY',
    'DYD'
  ], {
    D: 'minecraft:diamond',
    Y: 'voidloom:void_yarn',
    R: 'driftwrecks:rift_shard'
  }).id('ninjacatskies:thread_shard')
})
