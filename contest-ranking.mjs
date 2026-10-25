// Winactieprioriteit. Dit is een persoonlijke relevantiescore, GEEN kans op winst.
export function eligibleNL(c) {
  if (c.eligibleFromNetherlands === false) return false;
  if (Array.isArray(c.eligibleCountries))
    return c.eligibleCountries.some(x => /^(NL|Nederland|Netherlands)$/i.test(String(x)));
  if (c.eligibleFromNetherlands === true) return true;
  const terms = String(c.conditions || "");
  return /(Nederland|Netherlands|nederlandse? (?:inwoner|resident)|alle nationaliteiten|wereldwijd|worldwide|international(?:e)? deelname toegestaan|Nederland of Belgi[eë])/i.test(terms);
}
export function priority(c, referenceDay = new Date().toISOString().slice(0, 10)) {
  const end = Date.parse(String(c.deadline || "") + "T23:59:59Z");
  const now = Date.parse(referenceDay + "T12:00:00Z");
  const days = Number.isFinite(end) ? Math.ceil((end - now) / 86400000) : 9999;
  const eligible = eligibleNL(c);
  if (c.free !== true || c.purchaseRequired === true || !eligible || days < 0)
    return {score: -999, label: "Toelating/voorwaarden controleren", days, eligible};
  const category = String(c.category || "").toLowerCase();
  const interest = /(auto|ev|geld|cash|reizen|vakantie|renovatie|verduur|huis|tuin|apparat)/.test(category) ? 18 : 9;
  const value = Number(c.value);
  // Prize values are not win probabilities. Known value contributes up to 24 points.
  const prize = Number.isFinite(value) && value > 0 ? Math.min(24, Math.round(7 * Math.log10(value + 1))) : 6;
  const urgency = days <= 2 ? 23 : days <= 7 ? 17 : days <= 14 ? 11 : days <= 30 ? 5 : 0;
  const barrier = (c.newsletterRequired ? 8 : 0) + Math.min(6, Math.max(0, Number(c.minutes) || 0));
  const popularity = Number(c.entrants), winners = Number(c.winners);
  const oddsKnown = Number.isFinite(popularity) && popularity > 0 && Number.isFinite(winners) && winners > 0;
  // Only a modest evidence-backed odds tie-breaker, not fabricated precision.
  const oddsBonus = oddsKnown ? Math.min(8, Math.round(20 * Math.min(1, winners / popularity))) : 0;
  const score = interest + prize + urgency + 6 - barrier + oddsBonus;
  return {score, label: score >= 52 ? "Hoge prioriteit" : score >= 35 ? "Interessant" : "Overwegen",
          days, eligible, oddsKnown, reason: days <= 2 ? "Sluit zeer binnenkort" : days <= 7 ? "Sluit deze week" : "Geselecteerd op waarde en relevantie"};
}
