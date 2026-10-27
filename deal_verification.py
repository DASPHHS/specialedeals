from decimal import Decimal

def discount_percent(price, reference):
    price=Decimal(str(price)); reference=Decimal(str(reference))
    return (reference-price)*100/reference if reference>0 and price>0 else Decimal(0)
