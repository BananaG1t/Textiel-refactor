from .models import Product


def lock_products(product_ids) -> dict[int, Product]:
    """Lock and dedupe a set of product ids into a single {id: Product} map.
    Always locks in ascending id order to avoid deadlocks between concurrent calls."""
    product_ids = set(product_ids)
    if not product_ids:
        return {}
    return {
        p.id: p
        for p in Product.objects.select_for_update()
        .filter(id__in=product_ids)
        .order_by("id")
    }