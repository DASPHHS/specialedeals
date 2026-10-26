/**
 * Compare an internet/mobile renewal over the WHOLE fixed horizon.
 * Never show this hypothetical estimate as realised savings.
 */
export function compareContract(input) {
  const {months, promoMonths, currentMonthly, introMonthly, normalMonthly,
    activationEUR = 0, benefitType = "none", benefitEUR = 0, giftCopayEUR = 0, resaleFeesEUR = 0} = input;
  const valid = [currentMonthly, introMonthly, normalMonthly, activationEUR, benefitEUR, giftCopayEUR, resaleFeesEUR]
    .every(v => Number.isFinite(v) && v >= 0 && v <= 100000);
  if (!Number.isInteger(months) || months < 1 || months > 48 ||
      !Number.isInteger(promoMonths) || promoMonths < 0 || promoMonths > months ||
      !["none", "cash", "gift", "resale"].includes(benefitType) || !valid) {
    return {status:"invalid_input", potentialOnly:true};
  }
  const baselineCost = months * currentMonthly;
  const charges = promoMonths * introMonthly +
    (months - promoMonths) * normalMonthly + activationEUR;
  const cashCost = charges + (["gift", "resale"].includes(benefitType) ? giftCopayEUR : 0) -
    (benefitType === "cash" ? benefitEUR : 0);
  // Gift value is strictly user-supplied personal use value, NOT the store's MSRP.
  const personalValue = benefitType === "gift" ? benefitEUR : 0;
  // Estimated resale proceeds are NEVER cash earned until the item is actually sold.
  const resaleNet = benefitType === "resale" ? Math.max(0, benefitEUR - resaleFeesEUR) : 0;
  const personalEffectiveCost = cashCost - personalValue - resaleNet;
  const result = {
    status:"estimate_only", potentialOnly:true, months,
    baselineCostEUR:Math.round(baselineCost * 100) / 100,
    chargesEUR:Math.round(charges * 100) / 100,
    cashCostEUR:Math.round(cashCost * 100) / 100,
    userGiftValueEUR:personalValue,
    hypotheticalResaleNetEUR:Math.round(resaleNet * 100) / 100,
    resaleProceedsVerified:false,
    effectiveCostEUR:Math.round(personalEffectiveCost * 100) / 100,
    possibleEconomicDifferenceEUR:Math.round((baselineCost - personalEffectiveCost) * 100) / 100,
    benefitType,
    allConditionsVerified:false, eligibleForOfferVerified:false, realizedSavingsEUR:null
  };
  return result;
}
