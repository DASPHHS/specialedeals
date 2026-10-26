import {eligibleNL, priority} from "./contest-ranking.mjs";

/** Priority queue from verified editorial records, not from raw contest candidates.
 * Personal participation status is deliberately absent from public GitHub.
 */
export function selectActionable(contests, events, todayISO, now = new Date(), limit = 6) {
  const today = Date.parse(todayISO + "T12:00:00Z");
  if (!Number.isFinite(today)) return [];
  const actions = [];
  for (const c of contests || []) {
    const key = String(c.id || "");
    const date = String(c.deadline || "");
    const remaining = Math.round((Date.parse(date + "T12:00:00Z") - today) / 86400000);
    const checked = Date.parse(c.verifiedAt);
    const recent = Number.isFinite(checked) && checked <= now.getTime() &&
      now.getTime() - checked <= 7 * 86400000;
    if (!key || !Number.isFinite(remaining) || remaining < 0 ||
        c.free !== true || c.purchaseRequired !== false || c.reviewRequired === true ||
        !eligibleNL(c) || !recent ||
        !/^https:\/\//.test(c.sourceUrl || "") ||
        !/^https:\/\//.test(c.termsUrl || "") ||
        !c.organizer || !c.conditions || !c.evidence ||
        (c.startsAt && c.startsAt > todayISO)) continue;
    const rank = priority(c, todayISO);
    actions.push({
      id:"contest:"+key,kind:"contest",title:c.title,deadline:date,
      detail:c.prize,location:"",
      url:c.sourceUrl,score:rank.score + (remaining <= 2 ? 8 : 0),
      action:"Bekijk deelnamevoorwaarden",
      status:"Officiële regels gecontroleerd op " + c.verifiedAt.slice(0,10),
      remaining
    });
  }
  for (const e of events || []) {
    const date = String(e.endDate || "");
    const remaining = Math.round((Date.parse(date + "T12:00:00Z") - today) / 86400000);
    const beginning = String(e.startDate || "");
    const seen = Date.parse(e.lastSeenAt || "");
    if (!/^https:\/\//.test(e.url || "") || !beginning || !Number.isFinite(remaining) ||
        remaining < 0 || remaining > 30 || !e.title ||
        !Number.isFinite(seen) || now.getTime() - seen > 14 * 86400000) continue;
    const dateUrgency = remaining <= 2 ? 25 : remaining <= 7 ? 17 : 8;
    actions.push({
      id:"sample:"+e.url,kind:"sample",title:e.title,deadline:date,
      detail:e.sizes || "Maat niet bevestigd",location:e.city || "Locatie controleren",
      url:e.url,score:Math.round((e.priority || 40) / 2) + dateUrgency,
      action:"Bekijk tijden, maten en toegang",
      status:"Evenementaankondiging, geen maat- of voorraadgarantie",
      remaining
    });
  }
  return actions.sort((a,b)=>b.score-a.score || a.deadline.localeCompare(b.deadline))
    .slice(0,Math.max(0,limit));
}
