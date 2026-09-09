import dev.latvian.mods.rhino.*;
import java.nio.file.*;

/** Parses every KubeJS script with the pack's own Rhino: node accepts syntax Rhino does not (an ES6 shorthand property killed all of voidloom_recipes.js in 0.6.6). */
public class RhinoCheck {
    public static void main(String[] args) throws Exception {
        Context cx = new ContextFactory().enter();
        int bad = 0, n = 0;
        try (var walk = Files.walk(Path.of(args[0]))) {
            for (Path p : (Iterable<Path>) walk.filter(f -> f.toString().endsWith(".js"))::iterator) {
                n++;
                try { new Parser(cx).parse(Files.readString(p), p.toString(), 1); }
                catch (Throwable t) { bad++; System.out.println("FAIL " + p + " :: " + t.getMessage()); }
            }
        }
        System.out.println(n + " scripts, " + bad + " failed");
        System.exit(bad == 0 ? 0 : 1);
    }
}
