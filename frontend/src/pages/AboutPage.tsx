export default function AboutPage() {
  return (
    <div className="page about">
      <p className="eyebrow">About us</p>
      <h1>A Broadway shop that still knows your size.</h1>
      <div className="about__grid">
        <div>
          <p>
            Campus Customs started in 1975 when the family opened a Yale memorabilia store across from campus.
            The same address, 57 Broadway, is still the front door. Parents, students, and alumni come in for the
            sweater with the big Y, a college crest, or something small to take home after the game.
          </p>
          <p>
            Printing and embroidery sit next to the retail floor, so a team order and a single hoodie can leave
            from the same building. That is the whole idea: a neighborhood shop that can also outfit a reunion.
          </p>
          <p>
            This website is the rack, plus a shop assistant that reads our catalogue and our size counts. If it
            tells you a price or a quantity, that number is in the store database. If a size is gone, it will say
            so.
          </p>
        </div>
        <aside className="visit-card">
          <h2>Come by</h2>
          <p>57 Broadway, New Haven, CT 06511</p>
          <p>203-789-1608</p>
          <ul>
            <li>Monday–Saturday, 9am–9pm</li>
            <li>Sunday, 10am–6pm</li>
          </ul>
          <p className="fine">Custom printing, embroidery, and event merch — ask in the store or call the shop.</p>
        </aside>
      </div>
    </div>
  );
}
