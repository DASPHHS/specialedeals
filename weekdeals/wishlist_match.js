/* Deterministic wishlist matching for visible Weekdeals products.
 * Candidate discovery only: NEVER proves a real discount, stock, shipping, size, or lowest price.
 * Shared between browser (window.WeekdealsWishlist) and Node tests.
 */
(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.WeekdealsWishlist = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  function normalize(value) {
    return String(value ?? "")
      .normalize("NFKD").replace(/[\u0300-\u036f]/g, "")
      .toLocaleLowerCase("nl-NL").replace(/[’'\u0060]/g, "")
      .replace(/[^a-z0-9]+/g, " ").replace(/\s+/g, " ").trim();
  }
  function containsPhrase(haystack, needle) {
    const word = normalize(needle);
    return !!word && (" " + haystack + " ").includes(" " + word + " ");
  }
  function matches(productTitle, wishlist) {
    const title = normalize(productTitle);
    if (!title || !Array.isArray(wishlist)) return [];
    const hits = [];
    for (const item of wishlist) {
      if (!item || !item.id || !item.name) continue;
      const patterns = Array.isArray(item.matchAny) && item.matchAny.length
        ? item.matchAny : item.keywords;
      if (!Array.isArray(patterns) || !patterns.some(word => containsPhrase(title, word))) continue;
      if (Array.isArray(item.excludeTerms) &&
          item.excludeTerms.some(word => containsPhrase(title, word))) continue;
      // A generic model number or a shop category is insufficient evidence
      // for a wanted product.
      if (item.id === "dyson-handstofzuiger" && !containsPhrase(title, "dyson")) continue;
      if (item.id === "hoka-schoenen" && !containsPhrase(title, "hoka")) continue;
      hits.push({id: String(item.id), name: String(item.name)});
    }
    return hits;
  }
  return {normalize, containsPhrase, matches};
});
