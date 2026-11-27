// OOC first-join starter book — plain how-to-start, once per player.
// Complements lectern / dock chest copies; does not replace Whisker Codex voice.
// Keep in sync with island chest howto pages and Hall book.

const STARTER_BOOK_FLAG = 'ncs_starter_howto_v7'
const STARTER_TITLE = 'How to Start'

// Translation keys, so the book reads in the player's language. All but the campaign and Tension Post pages are the
// ones the Dock chest copy uses (ModDimensions.createHowToStartBook).
const STARTER_PAGES = [
  'message.clowderhall.book_start.page_1',
  'message.clowderhall.book_start.page_2',
  'book.ninjacatpack.howto.campaign',
  'book.ninjacatpack.howto.post',
  'message.clowderhall.book_start.page_3',
  'message.clowderhall.book_start.page_4',
  'message.clowderhall.book_start.page_5',
]

function makeStarterBook() {
  // 1.21 written_book_content: title/pages use Filterable {raw:...} form.
  let pages = STARTER_PAGES.map((key) => ({ raw: JSON.stringify({ translate: key }) }))
  return Item.of('minecraft:written_book', {
    'minecraft:custom_name': JSON.stringify({ translate: 'message.clowderhall.book_start.title', italic: false }),
    'minecraft:written_book_content': {
      pages: pages,
      title: { raw: STARTER_TITLE },
      author: 'Skybound Field Desk',
      generation: 0,
      resolved: true,
    },
  })
}

PlayerEvents.loggedIn((event) => {
  let player = event.player
  if (player.persistentData.getBoolean(STARTER_BOOK_FLAG)) return
  player.persistentData.putBoolean(STARTER_BOOK_FLAG, true)

  try {
    player.give(makeStarterBook())
  } catch (e) {
    // Fallback: tell the player where the lectern/chest copy lives if component give fails.
    player.tell(Text.translate('message.ninjacatpack.howto.give_failed').red())
  }
  player.tell(Text.translate('message.ninjacatpack.howto.read_first').gold())
  player.tell(Text.translate('message.ninjacatpack.howto.create_team').aqua())
})
