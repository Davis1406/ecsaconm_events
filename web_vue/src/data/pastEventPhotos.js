// Photo stories for past events, keyed by event id.
// Images live in public/recap/<folder>/{full,thumb}/NN.webp (compressed from the originals).

const base = `${import.meta.env.BASE_URL}recap/`

// pos: optional CSS object-position for photos whose subject isn't centred (e.g. portrait shots)
const photo = (folder, n, caption, pos) => ({
  id: n,
  full: `${base}${folder}/full/${n}.webp`,
  thumb: `${base}${folder}/thumb/${n}.webp`,
  caption,
  pos,
})

const p17 = (n, caption, pos) => photo('17th', n, caption, pos)

export const pastEventPhotos = {
  1: {
    chapters: [
      {
        id: 'arrivals',
        title: 'Opening & Arrivals',
        text: 'Delegates from across East, Central and Southern Africa gathered at the Golden Tulip Zanzibar Airport Hotel for five days of learning and connection.',
        photos: [
          p17('01', 'The Secretariat with the Guest of Honour'),
          p17('02', 'The conference venue, Golden Tulip Zanzibar Airport Hotel'),
          p17('03', 'Registration and welcome at the conference desk'),
          p17('04', 'Delegates arriving for the conference'),
          p17('05', 'Delegates at the 17th ECSACONM conference backdrop'),
          p17('06', 'Guests at the opening of the conference', 'center 18%'),
        ],
      },
      {
        id: 'fellowship',
        title: 'Fellowship & Induction',
        text: 'A proud moment for the region: new Fellows were inducted in full academic regalia, flying the flags of their member states.',
        photos: [
          p17('09', 'Fellows celebrate with the flags of member states'),
          p17('10', 'A Fellow in academic regalia during the induction'),
          p17('11', 'Newly inducted Fellows celebrate'),
          p17('12', 'Fellows fly the flag of Zimbabwe'),
          p17('13', 'Fellows fly the flag of Tanzania'),
        ],
      },
      {
        id: 'sessions',
        title: 'Scientific Sessions & Panels',
        text: 'Nurses and Midwives Sustaining Quality Healthcare in a Changing World: plenaries and panels shared evidence, experience and ideas.',
        photos: [
          p17('14', 'A panel discussion on the main stage'),
          p17('15', 'A panellist shares her experience'),
          p17('16', 'A panellist addresses the plenary'),
          p17('17', 'A panellist during the scientific session'),
          p17('21', 'Panellists and speakers on stage'),
        ],
      },
      {
        id: 'posters',
        title: 'Poster Exhibition',
        text: 'Researchers presented their work in the poster exhibition, sparking conversations between sessions.',
        photos: [
          p17('18', 'A presenter walks through her research poster'),
          p17('19', 'Poster presentation in the exhibition area'),
          p17('20', 'Delegates explore the poster exhibition'),
        ],
      },
      {
        id: 'networking',
        title: 'Conversations & Networking',
        text: 'Old friends reunited and new collaborations began in the spaces between sessions.',
        photos: [
          p17('07', 'Delegates connect at an exhibition stand'),
          p17('08', 'Conversations between sessions'),
        ],
      },
      {
        id: 'gala',
        title: 'Gala Dinner',
        text: 'The week closed with music, dance and celebration under the Zanzibar night sky.',
        photos: [
          p17('22', 'Dancing at the gala dinner'),
          p17('23', 'Delegates on the dance floor'),
          p17('24', 'Remarks at the gala dinner'),
          p17('25', 'Celebrating together at the gala'),
          p17('26', 'Delegates at the gala dinner'),
        ],
      },
    ],
  },
}

export const photosForEvent = (eventId) => pastEventPhotos[eventId] || null
