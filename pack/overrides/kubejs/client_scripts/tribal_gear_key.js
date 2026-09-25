// Pack-only Gear screen key. Tribal Power still registers apostrophe; that key
// sits on the same reach as the assignment list (grave) in this pack. A Gear
// binding that is still on the mod default, or unbound, moves to numpad minus.
// Any other binding is left alone, and the mod's own default is not changed.

let gearKeyApplied = false
let gearKeyTries = 0

ClientEvents.tick(event => {
  if (gearKeyApplied) return
  try {
    let Minecraft = Java.loadClass('net.minecraft.client.Minecraft')
    let InputConstants = Java.loadClass('com.mojang.blaze3d.platform.InputConstants')
    let KeyModifier = Java.loadClass('net.neoforged.neoforge.client.settings.KeyModifier')
    let KeyMapping = Java.loadClass('net.minecraft.client.KeyMapping')
    let mc = Minecraft.getInstance()
    if (!mc || !mc.options || !mc.options.keyMappings) return
    let mappings = mc.options.keyMappings
    let target = InputConstants.getKey('key.keyboard.keypad.subtract')
    let found = false
    let changed = false
    for (let i = 0; i < mappings.length; i++) {
      let key = mappings[i]
      if (key.getName() !== 'key.tribalpower.gear') continue
      found = true
      if (!(key.isDefault() || key.isUnbound())) continue
      key.setKeyModifierAndCode(KeyModifier.NONE, target)
      changed = true
    }
    if (!found) {
      if (++gearKeyTries > 200) gearKeyApplied = true
      return
    }
    gearKeyApplied = true
    if (changed) {
      KeyMapping.resetMapping()
      mc.options.save()
    }
  } catch (err) {
    gearKeyApplied = true
    console.warn('[Ninjacat Skies] Gear key default skipped: ' + err)
  }
})
