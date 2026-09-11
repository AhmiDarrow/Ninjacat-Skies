// Whisker Codex is one book. Core 0.4.2 still splits right-click (quests) vs shift-click (lore);
// cancel that split here and always open the campaign pages.
let ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')
let BookDataManager = Java.loadClass('com.klikli_dev.modonomicon.data.BookDataManager')
let BookGuiManager = Java.loadClass('com.klikli_dev.modonomicon.client.gui.BookGuiManager')
let BookAddress = Java.loadClass('com.klikli_dev.modonomicon.client.gui.book.BookAddress')

ItemEvents.rightClicked('ninjacatskies:whisker_codex', event => {
  event.cancel()
  if (event.server) return
  let id = ResourceLocation.parse('ninjacatskies:whisker_codex')
  let book = BookDataManager.get().getBook(id)
  if (!book) return
  BookGuiManager.get().openBook(BookAddress.defaultFor(book))
})
