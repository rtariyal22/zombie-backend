from django.db.models import QuerySet

from survivors.models import Survivor


def infected_survivors(survivors: list[int]) -> QuerySet[Survivor]:
    """
    Filter survivors who are infected.
    """
    return Survivor.objects.filter(
        is_infected=True,
        id__in=survivors,
    )
