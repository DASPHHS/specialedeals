from decimal import Decimal

def discount_percent(price, reference):
    price=Decimal(str(price)); reference=Decimal(str(reference))
    return (reference-price)*100/reference if reference>0 and price>0 else Decimal(0)

import datetime as dt
from urllib.parse import urlsplit

def verified_offers(items, minimum=10, now=None):
    """Accept only genuine current >=10% discounts on the exact same product."""
    now=now or dt.datetime.now(dt.timezone.utc)
    results=[]
    for x in items:
        try:
            if not (x.get("verified") is True and x.get("inStock") is True and
                    x.get("shipsToNL") is True and x.get("identicalVariantChecked") is True
                    and x.get("includesAllDeliveryCosts") is True and x.get("sellerTrusted") is True):
                continue
            if not x.get("sku") or x.get("sku")!=x.get("comparisonSku") or not x.get("title") or not x.get("source"):continue
            if x.get("condition")!=x.get("comparisonCondition"):continue
            if x.get("comparisonType") not in ("competing_retailer","historical_transaction_price"):continue
            links=[urlsplit(x.get(k,"")) for k in ("url","comparisonUrl")]
            if any(link.scheme!="https" or not link.hostname for link in links):continue
            if x.get("comparisonType")=="competing_retailer" and links[0].hostname==links[1].hostname:continue
            checked=dt.datetime.fromisoformat(x["verifiedAt"].replace("Z","+00:00"))
            if checked.tzinfo is None or not dt.timedelta(0)<=now-checked<=dt.timedelta(hours=36):continue
            reduction=discount_percent(x["totalPriceEUR"],x["comparisonTotalPriceEUR"])
            if reduction<Decimal(str(minimum)):continue
            current=Decimal(str(x["totalPriceEUR"]))
            reference=Decimal(str(x["comparisonTotalPriceEUR"]))
            result=dict(x,kind="deals",priceVerified=True,status="Korting gecontroleerd",
                        discountPercent=float(round(reduction,1)),savingsEUR=float(reference-current),
                        price="€"+format(current,".2f"),
                        referencePrice="€"+format(reference,".2f"),
                        score=min(100,60+int(reduction)),audience=x.get("audience","all"))
            results.append(result)
        except (KeyError,ValueError,TypeError,ArithmeticError):
            continue
    return results
