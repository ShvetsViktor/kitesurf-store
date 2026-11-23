"""Context processors for shopping bag data."""


def bag_contents(request):
    """Provide the total shopping bag quantity to templates."""
    bag = request.session.get("bag", {})

    return {
        "bag_count": sum(bag.values()),
    }
