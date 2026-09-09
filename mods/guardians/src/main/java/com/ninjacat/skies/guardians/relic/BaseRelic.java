package com.ninjacat.skies.guardians.relic;

/** Text + cooldown boilerplate shared by every relic power. */
abstract class BaseRelic implements RelicPower {
    private final String title, passive, active;
    private final int cooldown;

    BaseRelic(String title, String passive, String active, int cooldownTicks) {
        this.title = title; this.passive = passive; this.active = active; this.cooldown = cooldownTicks;
    }

    @Override public String title() { return title; }
    @Override public String passiveText() { return passive; }
    @Override public String activeText() { return active; }
    @Override public int cooldownTicks() { return cooldown; }
}
