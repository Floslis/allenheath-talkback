// Gemeinsam für alle Seiten: Sprache (Deutsch/Englisch) und Branding-Profil.
// Texte im HTML: data-t="schluessel" (Text), data-t-title / data-t-placeholder (Attribute). Im Code: t('schluessel', {wert}).

const TEXTE = {
  de: {
    einstellungen: 'Einstellungen',
    pausiert: 'Pausiert',
    pause: 'Pause',
    fortsetzen: 'Fortsetzen',
    beenden: 'Beenden',
    beenden_frage: 'Talkback beenden? Es startet bei der nächsten Anmeldung wieder.',
    beendet_titel: 'Talkback ist beendet',
    beendet_text: 'Es startet bei der nächsten Anmeldung am Mac wieder. Sofort starten: Installieren.command im Talkback-Ordner ausführen.',
    verbunden: 'Pult verbunden',
    verbinde: 'verbinde …',
    nicht_erreichbar: 'Pult {ip} nicht erreichbar',
    nicht_erreichbar_text: 'Prüfe, ob der Rechner im selben Netz wie das Pult ist, oder such das Pult unter Einstellungen.',
    pult_suchen: 'Pult suchen',
    programm_aus: 'Talkback-Programm läuft nicht',
    update_da: 'Neue Version {v} verfügbar.',
    update_nachts: 'Wird nachts um 4 Uhr von selbst installiert.',
    update_aus: 'Automatische Updates sind aus.',
    jetzt_installieren: 'Jetzt installieren',
    installiere: 'Installiere … das Tool startet gleich neu.',
    gruppen_titel: 'Talkback geht an',
    gruppen_hinweis: 'Antippen oder Softkey am Pult schaltet eine Gruppe an und aus. Mehrere gleichzeitig gehen.',
    keine_gruppen: 'Noch keine Gruppen. Unter „Einstellungen“ anlegen.',
    alle_uebrigen: 'alle übrigen',
    softkey_mg: 'Softkey MG {n}',
    noch_niemand: 'noch niemand',
    bearbeiten: '{name} bearbeiten',
    mixe_titel: 'In-Ear-Mixe',
    mixe_hinweis: 'Grün = hört dich, wenn du die Taste am Mikro drückst. Antippen schaltet einen Mix einzeln.',
    mixe_bearbeiten: 'Wer gehört zu {name}?',
    mixe_bearbeiten_hinweis: 'Antippen zum Hinzufügen oder Entfernen. Mit dem Zahnrad an einer anderen Gruppe wechselst du die Gruppe.',
    fertig: 'Fertig',
    niemand: 'Talkback an niemanden',
    erklaerung: 'Die Taste am Mikro schaltet das Sprechen. Diese Seite legt nur fest, wer es hört: Sie schaltet am Pult das Assign vom Talkback-Kanal auf die gewählten Mixe. Änderungen am Pult erscheinen hier von selbst.',
    produkt_von: 'Ein Produkt von',
    kofi: 'Unterstütze mich auf Ko-fi',
    // Einstellungen
    zurueck: '← zurück zum Talkback',
    aussehen: 'Aussehen',
    branding: 'Branding',
    branding_klein: 'Logo, Titel und Farben aus dem Ordner „branding“',
    sprache: 'Sprache',
    sprache_klein: 'Automatisch folgt dem Browser',
    sprache_auto: 'Automatisch',
    updates: 'Updates',
    auto_update: 'Neue Versionen nachts um 4 Uhr automatisch installieren',
    updates_hinweis: 'Einstellungen und eigenes Branding bleiben bei Updates erhalten. Das Tool schaut alle 6 Stunden auf GitHub nach.',
    version_ist: 'Installiert: Version {v}',
    nach_updates: 'Nach Updates suchen',
    suche_laeuft: 'Suche …',
    aktuell: 'Du hast die neueste Version.',
    update_fehler: 'GitHub nicht erreichbar. Später nochmal versuchen.',
    pult: 'Pult',
    ip: 'IP-Adresse des Pults',
    ip_klein: 'Oder mit „Pult suchen“ finden',
    tb_kanal: 'Talkback-Kanal',
    tb_kanal_klein: 'Eingang mit dem Talkback-Mikro',
    midi_kanal: 'MIDI-Basiskanal',
    midi_kanal_klein: 'Setup → Control → MIDI, Standard 12',
    mono_aux: 'Mono-Aux im Pult',
    mono_aux_klein: 'Anzahl laut Mix-Konfiguration',
    suche_lauscht: 'Lausche auf Pulte im Netz, das dauert ein paar Sekunden.',
    suche_nichts: 'Kein Pult gefunden. Ist der Rechner im selben Netz wie das Pult?',
    suche_gefunden: 'Gefunden. Antippen übernimmt die IP, dann Speichern.',
    suche_uebernommen: '{ip} übernommen, jetzt Speichern.',
    suche_fehler: 'Suche fehlgeschlagen.',
    firmware: 'Firmware',
    mixe_im_tool: 'Diese Mixe erscheinen im Tool',
    namen_vom_pult: 'Ist das Pult verbunden, erscheinen nur Mixe, die es dort wirklich gibt, mit ihren Namen.',
    gruppen: 'Gruppen',
    name: 'Name',
    softkey: 'Softkey (Mute-Gruppe)',
    keiner: 'keiner',
    mute_gruppe: 'Mute-Gruppe {n}',
    entfernen: 'Entfernen',
    gruppe_neu: '+ Gruppe hinzufügen',
    gruppe_n: 'Gruppe {n}',
    gruppen_erklaerung: '„Alle übrigen“: Die Gruppe enthält jeden Mix, der in keiner anderen Gruppe steckt (z. B. „Band“). Softkey: Lege am Pult einen Softkey auf eine leere Mute-Gruppe und trag ihre Nummer hier ein. Die LED leuchtet grün, wenn die Gruppe an ist.',
    speichern: 'Speichern',
    gespeichert: '✅ Gespeichert',
    nicht_gespeichert: 'Nicht gespeichert: {grund}',
  },
  en: {
    einstellungen: 'Settings',
    pausiert: 'Paused',
    pause: 'Pause',
    fortsetzen: 'Resume',
    beenden: 'Quit',
    beenden_frage: 'Quit Talkback? It starts again at the next login.',
    beendet_titel: 'Talkback has quit',
    beendet_text: 'It starts again at the next login on this Mac. To start it right away, run Installieren.command in the Talkback folder.',
    verbunden: 'Desk connected',
    verbinde: 'connecting …',
    nicht_erreichbar: 'Desk {ip} not reachable',
    nicht_erreichbar_text: 'Check that this computer is on the same network as the desk, or find the desk in the settings.',
    pult_suchen: 'Find desk',
    programm_aus: 'Talkback program is not running',
    update_da: 'New version {v} available.',
    update_nachts: 'It installs itself at 4 am.',
    update_aus: 'Automatic updates are off.',
    jetzt_installieren: 'Install now',
    installiere: 'Installing … the tool restarts in a moment.',
    gruppen_titel: 'Talkback goes to',
    gruppen_hinweis: 'Tap a group or press its softkey on the desk to switch it on or off. Several at once are fine.',
    keine_gruppen: 'No groups yet. Create them in the settings.',
    alle_uebrigen: 'all others',
    softkey_mg: 'Softkey MG {n}',
    noch_niemand: 'nobody yet',
    bearbeiten: 'Edit {name}',
    mixe_titel: 'In-ear mixes',
    mixe_hinweis: 'Green = hears you when you press the button on the mic. Tap a mix to switch it on its own.',
    mixe_bearbeiten: 'Who belongs to {name}?',
    mixe_bearbeiten_hinweis: 'Tap to add or remove. Use the gear on another group to switch groups.',
    fertig: 'Done',
    niemand: 'Talkback to nobody',
    erklaerung: 'The button on the mic switches talking. This page only decides who hears it: it switches the talkback channel\'s assign to the chosen mixes on the desk. Changes made on the desk show up here by themselves.',
    produkt_von: 'A product by',
    kofi: 'Support me on Ko-fi',
    zurueck: '← back to Talkback',
    aussehen: 'Appearance',
    branding: 'Branding',
    branding_klein: 'Logo, title and colours from the "branding" folder',
    sprache: 'Language',
    sprache_klein: 'Automatic follows the browser',
    sprache_auto: 'Automatic',
    updates: 'Updates',
    auto_update: 'Install new versions automatically at 4 am',
    updates_hinweis: 'Settings and your own branding stay during updates. The tool checks GitHub every 6 hours.',
    version_ist: 'Installed: version {v}',
    nach_updates: 'Check for updates',
    suche_laeuft: 'Checking …',
    aktuell: 'You have the latest version.',
    update_fehler: 'GitHub not reachable. Try again later.',
    pult: 'Desk',
    ip: 'Desk IP address',
    ip_klein: 'Or find it with “Find desk”',
    tb_kanal: 'Talkback channel',
    tb_kanal_klein: 'Input with the talkback mic',
    midi_kanal: 'MIDI base channel',
    midi_kanal_klein: 'Setup → Control → MIDI, default 12',
    mono_aux: 'Mono aux on the desk',
    mono_aux_klein: 'Number in the mix configuration',
    suche_lauscht: 'Listening for desks on the network, this takes a few seconds.',
    suche_nichts: 'No desk found. Is this computer on the same network as the desk?',
    suche_gefunden: 'Found. Tap to take the IP, then save.',
    suche_uebernommen: '{ip} taken, now save.',
    suche_fehler: 'Search failed.',
    firmware: 'Firmware',
    mixe_im_tool: 'These mixes appear in the tool',
    namen_vom_pult: 'Once the desk is connected, only mixes that really exist there are shown, with their names.',
    gruppen: 'Groups',
    name: 'Name',
    softkey: 'Softkey (mute group)',
    keiner: 'none',
    mute_gruppe: 'Mute group {n}',
    entfernen: 'Remove',
    gruppe_neu: '+ Add group',
    gruppe_n: 'Group {n}',
    gruppen_erklaerung: '"All others": the group contains every mix that is not in another group (e.g. "Band"). Softkey: put a softkey on an empty mute group on the desk and enter its number here. The LED lights green when the group is on.',
    speichern: 'Save',
    gespeichert: '✅ Saved',
    nicht_gespeichert: 'Not saved: {grund}',
  },
};

let SPRACHE = navigator.language?.toLowerCase().startsWith('de') ? 'de' : 'en';

function t(schluessel, werte = {}) {
  const text = TEXTE[SPRACHE][schluessel] ?? TEXTE.de[schluessel] ?? schluessel;
  return text.replace(/\{(\w+)\}/g, (_, k) => werte[k] ?? '');
}

function uebersetzen(wurzel = document) {
  document.documentElement.lang = SPRACHE;
  for (const el of wurzel.querySelectorAll('[data-t]')) el.textContent = t(el.dataset.t);
  for (const el of wurzel.querySelectorAll('[data-t-title]')) el.title = t(el.dataset.tTitle);
}

// Branding (branding/<name>/profil.json) und Sprache aus den Einstellungen. Gibt ein Promise zurück,
// damit die Seiten erst danach ihre eigenen Texte setzen.
const OBERFLAECHE = (async () => {
  try {
    const b = await (await fetch('/branding.json')).json();
    if (b.sprache === 'de' || b.sprache === 'en') SPRACHE = b.sprache;
    const unter = document.body.dataset.seite ? ' · ' + t(document.body.dataset.seite) : '';
    document.title = b.titel + unter;
    const titel = document.getElementById('titel'); if (titel) titel.textContent = b.titel;
    const logo = document.getElementById('logo'); if (logo) logo.innerHTML = b.logo || '';
    const css = (v) => Object.entries(v || {}).map(([k, w]) => `--${k}: ${w};`).join(' ');
    const f = b.farben || {};
    const s = document.createElement('style');
    s.textContent = `:root { ${css(f.dunkel)} }
@media (prefers-color-scheme: light) { :root:not([data-theme="dark"]) { ${css(f.hell)} } }`;
    document.head.append(s);
  } catch {}
  uebersetzen();
})();
