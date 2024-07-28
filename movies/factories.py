import factory
from django.contrib.auth import get_user_model
from movies.models import Collection, Movie, Genre

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall('set_password', 'password')


class GenreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Genre

    name = factory.Sequence(lambda n: f"Genre {n}")


class MovieFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Movie

    title = factory.Sequence(lambda n: f"Movie {n}")
    description = "A test movie"
    uuid = factory.Faker('uuid4')


class CollectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Collection

    user = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f"Collection {n}")
    description = "A test collection"
    uuid = factory.Faker('uuid4')
