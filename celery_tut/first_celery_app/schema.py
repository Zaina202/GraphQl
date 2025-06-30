import graphene
from .models import Person
from django.db.models import Count


class FemaleNameWithCount(graphene.ObjectType):
    name = graphene.String()
    count = graphene.Int()


class Query(graphene.ObjectType):
    female_names_with_counts = graphene.List(FemaleNameWithCount)

    def resolve_female_names_with_counts(self, info):
        return (
            Person.objects
            .filter(gender='F')
            .values('name')
            .annotate(count=Count('name'))
            .order_by('-count')  
        )


schema = graphene.Schema(query=Query)
