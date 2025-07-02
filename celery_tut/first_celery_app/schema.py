import graphene
from graphene_django import DjangoObjectType
from .models import Person,Book,Author
from graphene.types.datetime import Date
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
from django.db.models import Q



class BookStatusEnum(graphene.Enum):
    DRAFT = 'draft'
    PUBLISHED = 'published'

# class PersonType(DjangoObjectType):
#     class Meta:
#         model = Person

# class BookType(DjangoObjectType):
#     class Meta:
#         model = Book

# class AuthorType(DjangoObjectType):
#     class Meta:
#         model = Author

class PersonType(DjangoObjectType):
    class Meta:
        model = Person
        interfaces = (relay.Node,)
        filter_fields = ['name', 'gender', 'age']

class BookType(DjangoObjectType):
    class Meta:
        model = Book
        interfaces = (relay.Node,)
        filter_fields = {
            'title': ['exact', 'icontains', 'istartswith'],
            'status': ['exact'],
            'author__name': ['icontains'],
            'published_date': ['exact', 'gte', 'lte'],
        }

class AuthorType(DjangoObjectType):
    class Meta:
        model = Author
        interfaces = (relay.Node,)
        filter_fields = ['name']


class CreatePerson(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        age = graphene.Int(required=True)
        gender = graphene.String(required=True)

    person = graphene.Field(PersonType)

    def mutate(self, info, name, age, gender):
        person = Person(name=name, age=age, gender=gender)
        person.save()
        return CreatePerson(person=person)
    
class CreateBook(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        author_id = graphene.ID(required=True) 
        published_date = Date(required=True)
        status = BookStatusEnum(required=True)

    book = graphene.Field(BookType)

    def mutate(self, info, title, author_id, published_date, status):
        author = Author.objects.get(pk=author_id)
        book = Book(
            title=title,
            author=author,
            published_date=published_date,
            status=status.value
        )
        book.save()
        return CreateBook(book=book)


class CreateAuthor(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        bio = graphene.String()

    author = graphene.Field(AuthorType)

    def mutate(self, info, name, bio=None):
        author = Author(name=name, bio=bio)
        author.save()
        return CreateAuthor(author=author)

class UpdatePerson(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        age = graphene.Int()
        gender = graphene.String()

    person = graphene.Field(PersonType)

    def mutate(self, info, id, name=None, age=None, gender=None):
        person = Person.objects.get(pk=id)
        if name:
            person.name = name
        if age:
            person.age = age
        if gender:
            person.gender = gender
        person.save()
        return UpdatePerson(person=person)
    
class UpdateBook(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String()
        author_id = graphene.ID()
        published_date = Date()
        status = BookStatusEnum()

    book = graphene.Field(BookType)

    def mutate(self, info, id, title=None, author_id=None, published_date=None, status=None):
        book = Book.objects.get(pk=id)
        if title:
            book.title = title
        if author_id:
            book.author = Author.objects.get(pk=author_id)
        if published_date:
            book.published_date = published_date
        if status:
            book.status = status.value
        book.save()
        return UpdateBook(book=book)
    
class UpdateAuthor(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        bio = graphene.String()

    author = graphene.Field(AuthorType)

    def mutate(self, info, id, name=None, bio=None):
        author = Author.objects.get(pk=id)
        if name:
            author.name = name
        if bio:
            author.bio = bio
        author.save()
        return UpdateAuthor(author=author)

class DeletePerson(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        person = Person.objects.get(pk=id)
        person.delete()
        return DeletePerson(ok=True)
    
class DeleteBook(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        book = Book.objects.get(pk=id)
        book.delete()
        return DeleteBook(ok=True)
    
class DeleteAuthor(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        author = Author.objects.get(pk=id)
        author.delete()
        return DeleteAuthor(ok=True)

class Mutation(graphene.ObjectType):

    create_person = CreatePerson.Field()
    update_person = UpdatePerson.Field()
    delete_person = DeletePerson.Field()

    create_author = CreateAuthor.Field()
    update_author = UpdateAuthor.Field()
    delete_author = DeleteAuthor.Field()

    create_book = CreateBook.Field()
    update_book = UpdateBook.Field()
    delete_book = DeleteBook.Field()



# class Query(graphene.ObjectType):
#     all_people = graphene.List(PersonType)
#     all_books = graphene.List(BookType)
#     all_authors = graphene.List(AuthorType)

#     def resolve_all_people(self, info):
#         return Person.objects.all()
#     def resolve_all_authors(self, info):
#         return Author.objects.all()
#     def resolve_all_books(self, info):
#         return Book.objects.all()

class Query(graphene.ObjectType):
    all_people = DjangoFilterConnectionField(PersonType)
    all_books = DjangoFilterConnectionField(BookType)
    all_authors = DjangoFilterConnectionField(AuthorType)

    search_books = graphene.List(BookType, search=graphene.String(), first=graphene.Int())

    def resolve_search_books(self, info, search=None, first=None):
        qs = Book.objects.all()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(author__name__icontains=search)
            )
        if first:
            qs = qs[:first]
        return qs


#schema = graphene.Schema(query=Query, mutation=Mutation)
schema = graphene.Schema(query=Query, mutation=Mutation, types=[BookType, AuthorType, PersonType])

