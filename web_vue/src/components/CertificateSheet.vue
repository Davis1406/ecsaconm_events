<template>
  <!-- 1920x1080 certificate, positioned exactly as the designer's HTML source.
       Fonts (@font-face) are declared in this component's global style block. -->
  <section class="cert" style="position:relative; width:1920px; height:1080px; overflow:hidden; background:#ffffff">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 260" style="position:absolute; top:0; left:0; width:260px; height:260px">
      <defs>
        <linearGradient :id="`cornerTL${uid}`" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#6E1420"/>
          <stop offset="100%" stop-color="#FE5066"/>
        </linearGradient>
      </defs>
      <polygon points="0,0 220,0 0,220" :fill="`url(#cornerTL${uid})`"/>
      <polygon points="220,0 260,0 0,260 0,220" fill="#FBE3E7"/>
    </svg>
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 260" style="position:absolute; right:0; bottom:0; width:260px; height:260px">
      <defs>
        <linearGradient :id="`cornerBR${uid}`" x1="100%" y1="100%" x2="0%" y2="0%">
          <stop offset="0%" stop-color="#6E1420"/>
          <stop offset="100%" stop-color="#FE5066"/>
        </linearGradient>
      </defs>
      <polygon points="260,260 40,260 260,40" :fill="`url(#cornerBR${uid})`"/>
      <polygon points="40,260 0,260 260,0 260,40" fill="#FBE3E7"/>
    </svg>
    <img :src="watermark" alt="" style="position:absolute; top:425px; left:775px; width:370px; height:553px; object-fit:contain; opacity:0.45">
    <div style="position:absolute; top:56px; left:56px; width:1808px; height:968px; border:3px solid #fe5066; border-radius:6px; box-sizing:content-box"></div>
    <img :src="logo" alt="ECSACONM logo" style="position:absolute; top:64.01px; left:110.01px; width:189.99px; height:191.99px; object-fit:contain">
    <h3 style="position:absolute; top:96px; left:330px; width:1565px; font-family:Montserrat, Arial, sans-serif; font-size:35px; font-weight:800; line-height:1.25; text-align:justify; color:#1a1a1a">EAST, CENTRAL AND SOUTHERN AFRICA COLLEGE OF NURSING AND MIDWIFERY<br><span v-html="'&nbsp;'.repeat(59)"></span>(ECSACONM)</h3>
    <div style="position:absolute; top:201px; left:552px; width:950px; height:3px; background:#fe5066"></div>
    <h1 style="position:absolute; top:244px; left:160px; width:1600px; font-family:'Alex Brush', 'Brush Script MT', serif; font-size:172px; font-weight:400; line-height:1; text-align:center; color:#7a1220">Certificate</h1>
    <div style="position:absolute; top:478px; left:460px; width:140px; height:2px; background:#fe5066"></div>
    <h2 style="position:absolute; top:446px; left:160px; width:1600px; font-family:Montserrat, Arial, sans-serif; font-size:50px; font-weight:700; line-height:1; letter-spacing:8px; text-align:center; color:#f4253f">OF PARTICIPATION</h2>
    <div style="position:absolute; top:470px; left:1320px; width:140px; height:2px; background:#fe5066"></div>
    <p style="position:absolute; top:526px; left:160px; width:1600px; font-family:Montserrat, Arial, sans-serif; font-size:32px; font-weight:600; letter-spacing:3px; text-align:center; color:#555555">THE FOLLOWING AWARD IS GIVEN TO</p>
    <!-- Fixed height so the underline stays put when a long name is shrunk to fit (see fitName). -->
    <p ref="name" style="position:absolute; top:600px; left:610px; width:700px; height:84px; line-height:84px; padding:0 0 16px; white-space:nowrap; overflow:hidden; font-family:'Playfair Display', Georgia, serif; font-size:63px; font-weight:600; font-style:italic; text-align:center; color:#1a1a1a; border-bottom:3px solid #fe5066; box-sizing:content-box">{{ name }}</p>
    <!-- 1400px wide (source: 1200px) — the usher wording overflowed onto a 4th line and hit the signature.
         fitBody() shrinks the type if the body still runs long (e.g. a long event name). -->
    <p ref="body" style="position:absolute; top:724px; left:260px; width:1400px; font-family:Montserrat, Arial, sans-serif; font-size:29px; font-weight:400; line-height:1.5; text-align:center; color:#2b2b2b">
      <template v-for="(line, i) in bodyLines" :key="i"><br v-if="i">{{ line }}</template>
    </p>
    <div style="position:absolute; top:900px; left:790px; width:340px; height:2px; background:#2b2b2b"></div>
    <img :src="signature" alt="President's signature" style="position:absolute; top:838px; left:812px; width:300px; height:55px; object-fit:contain">
    <p style="position:absolute; top:914px; left:790px; width:340px; font-family:Montserrat, Arial, sans-serif; font-size:29px; font-weight:700; text-align:center; color:#1a1a1a">Dr. Glory Msibi</p>
    <p style="position:absolute; top:950px; left:790px; width:340px; font-family:Montserrat, Arial, sans-serif; font-size:21px; font-weight:600; letter-spacing:3px; text-align:center; color:#666666">PRESIDENT</p>
    <!-- Verification QR — scanning it shows the confirmation message below.
         Placed bottom-right, mirroring the CPD badge on the left. -->
    <div style="position:absolute; top:840px; left:1650px; width:160px; height:160px; background:#ffffff; padding:5px; box-sizing:border-box; border:1px solid #e5e7eb; border-radius:6px">
      <QRCodeVue :value="qrValue" :size="150" foreground="#0f172a" background="#ffffff" />
    </div>
    <p style="position:absolute; top:1010px; left:1650px; width:160px; font-family:Montserrat, Arial, sans-serif; font-size:14px; font-weight:600; letter-spacing:0.5px; text-align:center; color:#666666">SCAN TO VERIFY</p>
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 160" style="position:absolute; top:840px; left:110px; width:160px; height:160px">
      <defs>
        <linearGradient :id="`badgeGrad${uid}`" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#FE5066"/>
          <stop offset="100%" stop-color="#7A1220"/>
        </linearGradient>
      </defs>
      <polygon points="80.0,4.0 95.0,24.0 118.0,14.2 121.0,39.0 145.8,42.0 136.0,65.0 156.0,80.0 136.0,95.0 145.8,118.0 121.0,121.0 118.0,145.8 95.0,136.0 80.0,156.0 65.0,136.0 42.0,145.8 39.0,121.0 14.2,118.0 24.0,95.0 4.0,80.0 24.0,65.0 14.2,42.0 39.0,39.0 42.0,14.2 65.0,24.0" :fill="`url(#badgeGrad${uid})`"/>
      <text x="80" y="76" :font-size="type.cpd >= 10 ? 36 : 40" font-weight="700" fill="#FFFFFF" text-anchor="middle" font-family="Montserrat, Arial, sans-serif">{{ type.cpd }}</text>
      <text x="80" y="102" font-size="13" font-weight="700" fill="#FFFFFF" text-anchor="middle" font-family="Montserrat, Arial, sans-serif">CPD POINTS</text>
    </svg>
  </section>
</template>

<script>
import QRCodeVue from 'qrcode.vue'
import logo from '@/assets/certificate/logo.png'
import watermark from '@/assets/certificate/watermark.png'
import signature from '@/assets/certificate/signature.png'

export default {
  name: 'CertificateSheet',
  components: { QRCodeVue },
  props: {
    name: { type: String, required: true },
    type: { type: Object, required: true },
    // The selected event's name — the usher/secretariat certificate says which
    // event the person supported, so it has to be passed in at render time.
    eventName: { type: String, default: '' },
    // Keeps SVG gradient ids unique when many certificates share one page.
    uid: { type: [String, Number], required: true },
  },
  data() {
    return { logo, watermark, signature }
  },
  computed: {
    bodyLines() {
      const b = this.type.body
      return typeof b === 'function' ? b(this.eventName) : b
    },
    // What a scan of the certificate's QR shows: a confirmable statement that
    // this person attended the event and received the certificate, plus the
    // ECSACONM contact block. Plain text (not a URL) so any scanner renders it.
    qrValue() {
      const name = this.name || ''
      const event = this.eventName || 'the ECSACONM conference'
      return [
        'ECSACONM Certificate Verification',
        '',
        `This is to confirm ${name} attended ${event}, from 14th to 18th September 2026 at Golden Tulip Airport Hotel, Zanzibar, and was awarded this certificate.`,
        '',
        'For further enquiries please contact:',
        'Address: Plot No. 157, Oloirien Njiro Road, P.O. Box 1009, Arusha, Tanzania',
        'Tel: +255-27-254 9362, +255-27-254 9365 / 9366',
        'Fax: +255-27-254 9392',
        'Email: info@ecsaconm.org (General enquiries)',
      ].join('\n')
    },
  },
  methods: {
    // Long names: shrink the font until the name fits on the 700px line.
    // Called by the parent once the webfonts have loaded.
    fitName() {
      const el = this.$refs.name
      if (!el) return
      let size = 63
      el.style.fontSize = size + 'px'
      while (el.scrollWidth > el.clientWidth && size > 30) {
        el.style.fontSize = (--size) + 'px'
      }
    },
    // The body sits at y=724 and the signature image at y=838, so it has
    // ~114px to live in — two lines at 29px/1.5 is 87px. A longer event name
    // can wrap onto a 3rd line and hit the signature, so shrink to fit.
    fitBody() {
      const el = this.$refs.body
      if (!el) return
      const max = 112
      let size = 29
      el.style.fontSize = size + 'px'
      while (el.scrollHeight > max && size > 20) {
        el.style.fontSize = (--size) + 'px'
      }
    },
  },
}
</script>

<style>
/* Certificate webfonts, declared here (not in a page component) so every page
   that renders a CertificateSheet gets them — the print route *and* the
   off-screen sheet Certificates.vue rasterizes for the email preview. Without
   these the 172px "Certificate" falls back to a system font, its line box
   overflows, and it collides with "OF PARTICIPATION". */
@font-face { font-family: 'Alex Brush'; src: url('../assets/certificate/fonts/AlexBrush-Regular.woff2') format('woff2'); font-weight: 400; font-style: normal; }
@font-face { font-family: 'Montserrat'; src: url('../assets/certificate/fonts/Montserrat-400.woff2') format('woff2'); font-weight: 400; font-style: normal; }
@font-face { font-family: 'Montserrat'; src: url('../assets/certificate/fonts/Montserrat-500.woff2') format('woff2'); font-weight: 500; font-style: normal; }
@font-face { font-family: 'Montserrat'; src: url('../assets/certificate/fonts/Montserrat-600.woff2') format('woff2'); font-weight: 600; font-style: normal; }
@font-face { font-family: 'Montserrat'; src: url('../assets/certificate/fonts/Montserrat-700.woff2') format('woff2'); font-weight: 700; font-style: normal; }
@font-face { font-family: 'Montserrat'; src: url('../assets/certificate/fonts/Montserrat-800.woff2') format('woff2'); font-weight: 800; font-style: normal; }
@font-face { font-family: 'Playfair Display'; src: url('../assets/certificate/fonts/PlayfairDisplay-600italic.woff2') format('woff2'); font-weight: 600; font-style: italic; }
</style>

<style scoped>
/* The app root sets tracking-wide; the design uses normal spacing. */
.cert { letter-spacing: normal; }
.cert h1, .cert h2, .cert h3, .cert p { margin: 0; }
</style>
