package com.ninjacat.skies.guardians.entity;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.Guardians;
import com.ninjacat.skies.guardians.entity.bosses.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

import javax.annotation.Nullable;
import java.util.EnumMap;
import java.util.Map;

/** One entity type per guardian, all sharing {@link GuardianEntity}. */
public final class ModEntities {
    private ModEntities() {}
    public static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(Registries.ENTITY_TYPE, Guardians.MOD_ID);
    public static final Map<GuardianKind, DeferredHolder<EntityType<?>, EntityType<? extends GuardianEntity>>> TYPES = new EnumMap<>(GuardianKind.class);

    static {
        reg(GuardianKind.BEDDOWN, BeddownGuardian::new);
        reg(GuardianKind.GRINDMAW, GrindmawGuardian::new);
        reg(GuardianKind.THORNMOTHER, ThornmotherGuardian::new);
        reg(GuardianKind.EDGEWALKER, EdgewalkerGuardian::new);
        reg(GuardianKind.DRUMHEART, DrumheartGuardian::new);
        reg(GuardianKind.COGWRIGHT, CogwrightGuardian::new);
        reg(GuardianKind.HIVEMIND, HivemindGuardian::new);
        reg(GuardianKind.SEALBREAKER, SealbreakerGuardian::new);
        reg(GuardianKind.UNWOVEN, UnwovenGuardian::new);
        reg(GuardianKind.LINTGOLEM, LintGolemGuardian::new);
        reg(GuardianKind.TANGLE, TangleGuardian::new);
        reg(GuardianKind.FIRSTCUT, FirstCutGuardian::new);
        reg(GuardianKind.OVERWEAVER, OverweaverGuardian::new);
    }

    private static <T extends GuardianEntity> void reg(GuardianKind kind, EntityType.EntityFactory<T> factory) {
        // hitboxes: the models are 1 unit = 1 block; vanilla copes with ender-dragon-sized boxes, so use the real size
        DeferredHolder<EntityType<?>, EntityType<? extends GuardianEntity>> h = ENTITIES.register(kind.id, () ->
                EntityType.Builder.of(factory, MobCategory.MONSTER)
                        .sized(Math.min(kind.width * 0.7F, 12.0F), kind.height)
                        .eyeHeight(kind.height * 0.85F)
                        .clientTrackingRange(24).updateInterval(2).fireImmune()
                        .build(Guardians.MOD_ID + ":" + kind.id));
        TYPES.put(kind, h);
    }

    public static void attributes(EntityAttributeCreationEvent e) {
        for (var en : TYPES.entrySet()) e.put(en.getValue().get(), GuardianEntity.attributes(en.getKey()).build());
    }

    @Nullable
    public static GuardianEntity create(GuardianKind kind, ServerLevel level) {
        var h = TYPES.get(kind); return h == null ? null : h.get().create(level);
    }
}
