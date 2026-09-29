# Design notes

The site is meant to feel like the Broadway shop: navy walls, cream paper, a gold Y on the door, and product photos large enough to read the print.

- **Navy bar and gold Y.** The header stays put while you scroll, the way a store sign stays above the door. The round Y mark is the only logo, so the name Campus Customs does the rest.
- **Fraunces headlines, Outfit text.** The headlines feel like a painted window. The body type stays plain so prices and sizes are easy to scan.
- **Cream page, white cards, warm photo wells.** Product photos sit on a tan square instead of a harsh white grid. Cards lift a few pixels on hover so the rack feels touchable.
- **Hero with hours.** The home page leads with the shop, not a slogan about AI. Hours and the Broadway address are in the first screen because that is how people decide to visit.
- **Rust chat button.** The assistant sits bottom-right in a color that is not the navy of the nav, so it reads as a person you can interrupt, not another menu item. The panel slides up and the stock answer is set as a short note, not a full-page takeover.
- **Motion that means something.** Each page rises in over about a third of a second when you navigate, so moving from the rack to a product feels like one continuous shop. The chat shows three bouncing dots while it checks stock, so a few seconds of waiting reads as "working", not "broken". Shoppers who turn on reduced motion in their system settings get no animation at all.
- **Works on a phone.** Below 800px the nav stacks, the product detail page puts the photo above the text, and the chat panel shrinks to fit the screen. Many people check stock on their phone while walking down Broadway.
- **Shelf strip.** When chat finds items, a dashed-edge band appears under the nav (“Pulled from the shelf”) instead of hiding the matches inside the bubble. The shopper can click straight into the large photo.
