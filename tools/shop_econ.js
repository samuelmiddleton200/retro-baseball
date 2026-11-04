const PACKS = {
  bronze:  { n:'Bronze',  price:2500,  col:'#b07a46', col2:'#e0a86a', p:[.545,.30,.12,.03,.004,.001] },
  silver:  { n:'Silver',  price:6500,  col:'#8d97a8', col2:'#d2dae6', p:[.297,.35,.25,.08,.02,.003] },
  gold:    { n:'Gold',    price:15000, col:'#b8902c', col2:'#ffd964', p:[.12,.25,.35,.22,.05,.01] },
  diamond: { n:'Diamond', price:39500, col:'#49a7c8', col2:'#b6f0ff', p:[.02,.10,.28,.40,.16,.04] },
};
const BULK = [[1, 1], [5, .9], [10, .8]];        // buy 5 for 10% off, 10 for 20% off
const TIER_LO = [60, 70, 80, 90, 100, 110], TIER_HI = [69, 79, 89, 99, 109, 120];
const TIER_KEYS = ['bronze', 'silver', 'gold', 'diamond'];
// position packs: every card plays one of these spots. TODAY is one spot that changes every day.
const POSGROUPS = [
  { k:'infield',  n:'INFIELD',  sub:'1B 2B SS 3B',   pos:['1B', '2B', 'SS', '3B'], mult:1.2 },
  { k:'outfield', n:'OUTFIELD', sub:'LF CF RF C',    pos:['LF', 'CF', 'RF', 'C'], mult:1.2 },
  { k:'pitcher',  n:'PITCHER',  sub:'SP RP CP',      pos:['SP', 'SP', 'SP', 'RP', 'RP', 'CP'], mult:1.2 },
  { k:'today',    n:'TODAY',    sub:'NEW EVERY DAY', pos:null, mult:1.3 },
];
const TODAY_POS = ['1B', '2B', '3B', 'SS', 'C', 'CF', 'RF', 'LF'];
const POSTIERS = ['silver', 'gold', 'diamond'];
const dayKey = (d = new Date()) => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
const seedRng = str => { let a = 0; for (const ch of str) a = (Math.imul(a, 31) + ch.charCodeAt(0)) | 0;
  return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; };
const todayPos = () => TODAY_POS[Math.floor(seedRng('pos' + dayKey())() * TODAY_POS.length)];
const posPackPrice = (grp, tier) => Math.round(PACKS[tier].price * grp.mult);

// what a card is worth in coins: the table from 80 to 109, the same 17.5% a point either side of it
const VAL_T = { 80:380, 81:450, 82:525, 83:620, 84:725, 85:855, 86:1000, 87:1175, 88:1375, 89:1625, 90:1900, 91:2250, 92:2625, 93:3100, 94:3625, 95:4275, 96:5025, 97:5900, 98:6925, 99:8125,
  100:9550, 101:11200, 102:13200, 103:15500, 104:18200, 105:21350, 106:25100, 107:29450, 108:34600, 109:40650 };
const VAL_STEP = Math.pow(40650 / 380, 1 / 29);
const valueOf = r => { r = clamp(r, 60, 125); const f = Math.floor(r); if (r === f && VAL_T[f]) return VAL_T[f]; return 380 * Math.pow(VAL_STEP, r - 80); };
const sellPrice = c => Math.round(valueOf(ovrOf(c)) * .4);                              // selling pays 40% of what a card is worth
const upCost = c => Math.round(1.3 * (valueOf(ovrOf(c) + 5) - valueOf(ovrOf(c))) / 10);  // one of its ten levels: 1.3 x the value it adds
// the hot deal prices: Epics 20% off, Legendaries 10% off
const DEAL_PRICE = { 90:1525, 91:1800, 92:2100, 93:2475, 94:2900, 95:3425, 96:4025, 97:4725, 98:5525, 99:6500,
  100:8600, 101:10100, 102:11850, 103:13950, 104:16350, 105:19200, 106:22550, 107:26500, 108:31150, 109:36600 };
const dealPrice = c => DEAL_PRICE[clamp(ovrOf(c), 90, 109)] || Math.round(valueOf(ovrOf(c)) * .85);

// one new card at a rating: a random player, or at one position / with one face
function makeCardAt(lvl, o = {}){
  lvl = clamp(Math.round(lvl), 60, 120);
  const pitcher = o.pitcher != null ? o.pitcher : o.pos ? ['SP', 'RP', 'CP'].includes(o.pos) : chance(.26);
  const c = pitcher ? makePitcher(lvl, o.pos || pick(['SP', 'SP', 'SP', 'RP', 'RP', 'CP']))
                    : makeHitter(lvl, o.pos || pick(POS));
  // the rolled number is the card's headline rating, so the overall lands on it
  const keys = statsOf(c).map(s => s[1]);
  const cur = ovrOf(c), d = lvl - cur;
  if (c.fielding != null){                                    // a hitter: speed follows fielding, so the three real stats carry the shift
    const k3 = ['contact', 'power', 'fielding'];
    for (let n = 0; n < 6; n++){ c.speed = c.fielding; const dd = lvl - ovrOf(c); if (!dd) break; k3.forEach(k => c[k] = clamp(c[k] + dd, 60, 120)); }
    c.speed = c.fielding;
  } else keys.forEach(k => c[k] = clamp(c[k] + d, 60, 120));
  c.id = _cardId++; c.lvl = 0; c.fz = 0; c.ovr = ovrOf(c); c.num = ri(1, 72);
  c.tm = ri(0, G.teams.length - 1);                            // which club's colours he wears on his card
  if (o.face != null) c.face = o.face;
  return c;
}
// roll one card out of a pack
function rollCard(packKey, forceTier, o){
  let tier = 0;
  if (forceTier != null) tier = forceTier;
  else { const p = PACKS[packKey].p; let r = Math.random(), a = 0;
    for (let i = 0; i < 6; i++){ a += p[i]; if (r < a){ tier = i; break; } } }
  return makeCardAt(TIER_LO[tier] + Math.floor(Math.random() * (TIER_HI[tier] - TIER_LO[tier] + 1)), o);
}

// ── fusing: two cards with one face (+5) or one position (+3), in the same band of the 4-3-3 ladder ──
const bandOf = r => { const d = Math.floor(r / 10) * 10, o = r - d; return d + (o < 4 ? 0 : o < 7 ? 4 : 7); };
const bandText = b => { const o = b % 10; return b + '-' + (b + (o === 0 ? 3 : 2)); };
function fuseKey(c, mode){
  const band = bandOf(ovrOf(c));
  if (mode === 'face'){ const f = portraitFor(c); return (f >= 0 ? 'f' + f : 'x' + c.id) + '|' + band; }
  return 'p' + c.pos + '|' + band;
}
function fuseGroups(mode){
  const m = new Map();
  G.cards.filter(c => (c.fz || 0) < 2).forEach(c => { const k = fuseKey(c, mode); if (!m.has(k)) m.set(k, []); m.get(k).push(c); });
  const out = []; m.forEach((list, k) => { if (list.length >= 2) out.push({ k, list:list.sort((a, b) => ovrOf(b) - ovrOf(a)), band:+k.split('|')[1], top:ovrOf(list[0]) }); });
  return out.sort((a, b) => b.top - a.top);
}
const fuseRating = (a, b, mode) => clamp(Math.floor((ovrOf(a) + ovrOf(b)) / 2 + (mode === 'face' ? 5 : 3) + .5), 60, 120);
const canFuse = (a, b, mode) => !!(a && b && a.id !== b.id && (a.fz || 0) < 2 && (b.fz || 0) < 2 && fuseKey(a, mode) === fuseKey(b, mode) && !(inUse(a.id) && inUse(b.id)));
function doFuse(a, b, mode){
  if (!canFuse(a, b, mode)) return null;
  const slotCard = inUse(a.id) ? a : inUse(b.id) ? b : null;
  const o = {};
  if (mode === 'face') o.face = portraitFor(a);
  if (slotCard || mode === 'pos') o.pos = slotCard ? slotCard.pos : a.pos;            // a lineup spot keeps his position
  const nc = makeCardAt(fuseRating(a, b, mode), o);
  nc.lvl = Math.max(a.lvl || 0, b.lvl || 0); nc.fz = Math.max(a.fz || 0, b.fz || 0) + 1;
  G.cards = G.cards.filter(c => c.id !== a.id && c.id !== b.id); G.cards.push(nc);
  ['lineup', 'rot', 'pen'].forEach(k => { G.slots[k] = G.slots[k].map(id => id === a.id || id === b.id ? nc.id : id); });
  rebuildTeam(); G.seen = G.seen || {}; G.seen[nc.name] = 1; save();
  return nc;
}

// ── hot deals: three a day, 75% Epic and 25% Legendary, the same all day ──
function dealsToday(){
  const k = dayKey();
  if (!G.deals || G.deals.key !== k){
    const R = seedRng('deals' + k + G.team), cards = [];
    for (let i = 0; i < 3; i++){ const epic = R() < .75; const c = makeCardAt(epic ? 90 + Math.floor(R() * 10) : 100 + Math.floor(R() * 10)); c.id = null; cards.push(c); }
    G.deals = { key:k, cards, sold:[0, 0, 0] }; save();
  }
  return G.deals;
}
function buyDeal(i){
  const D = dealsToday(), c = D.cards[i]; if (!c || D.sold[i]) return;
  const cost = dealPrice(c); if (G.coins < cost) return;
  G.coins -= cost; c.id = _cardId++; D.sold[i] = 1; G.cards.push(c); G.seen = G.seen || {}; G.seen[c.name] = 1;
  shopMsg = 'BOUGHT ' + c.name.toUpperCase(); shopMsgT = 2200; save();
}

// ── the daily pack and its streak ──
function streakInfo(){
  const s = G.streak || { day:0, last:'' }, today = dayKey(), yest = dayKey(new Date(Date.now() - 86400000));
  const run = (s.last === today || s.last === yest) ? s.day : 0;
  return { run, next: s.last === today ? run : run >= 7 ? 1 : run + 1, claimedToday: s.last === today };
}
const STREAK_COINS = [500, 1000, 1500, 2000, 2500, 3000];
function freePack(){
  if (Date.now() < (G.freeAt || 0)) return;
  const si = streakInfo(), day = si.claimedToday ? si.run : si.next;
  G.streak = { day, last:dayKey() }; G.freeAt = Date.now() + 24 * 3600 * 1000;
  const batches = [{ tier:'bronze', cards:Array.from({ length:5 }, () => rollCard('bronze')) }];
  let bonus = '';
  if (day >= 7) batches.push({ tier:'gold', cards:Array.from({ length:3 }, () => rollCard('gold')) });
  else { G.coins += STREAK_COINS[day - 1]; bonus = 'DAY ' + day + ' STREAK  +' + STREAK_COINS[day - 1].toLocaleString() + ' COINS'; }
  startOpen({ kind:'pack', batches, bonus, free:true }); save();
}
function buyPack(kind, n){
  const cost = Math.round(PACKS[kind].price * BULK.find(b => b[0] === n)[1] * n);
  if (G.coins < cost) return;
  G.coins -= cost;
  const batches = []; for (let i = 0; i < n; i++) batches.push({ tier:kind, cards:[rollCard(kind), rollCard(kind), rollCard(kind)] });
  startOpen({ kind:'pack', batches, again:{ type:'pack', kind, n } }); save();
}
function buyPosPack(gk, tier){
  const grp = POSGROUPS.find(x => x.k === gk), cost = posPackPrice(grp, tier);
  if (G.coins < cost) return;
  G.coins -= cost;
  const cards = [0, 1, 2].map(() => rollCard(tier, null, { pos: grp.k === 'today' ? todayPos() : pick(grp.pos) }));
  startOpen({ kind:'pack', batches:[{ tier, cards }], again:{ type:'pos', gk, tier } }); save();
}
const againCost = A => !A ? 0 : A.type === 'pack' ? Math.round(PACKS[A.kind].price * BULK.find(b => b[0] === A.n)[1] * A.n) : posPackPrice(POSGROUPS.find(x => x.k === A.gk), A.tier);
function openAgain(A){ if (A.type === 'pack') buyPack(A.kind, A.n); else buyPosPack(A.gk, A.tier); }

// ── trading in: 5 cards of one colour make a card rated (their average + 10), rounded down ──
const TRADE_N = 5;
const tradeRating = cards => clamp(Math.floor(cards.reduce((s, c) => s + ovrOf(c), 0) / cards.length + 10), 60, 120);
