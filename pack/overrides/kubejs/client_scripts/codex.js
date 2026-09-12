// Whisker Codex is one book. Java opens Modonomicon on use; this client hook keeps the same
// behaviour if an older Core jar is still loaded (right-click must not open FTB Quests).
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
