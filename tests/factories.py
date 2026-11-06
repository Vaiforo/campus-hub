import factory

from campushub.models import Order


class OrderFactory(factory.Factory):
    class Meta:
        model = Order

    item_name = factory.Faker("word")
    quantity = factory.Faker("random_int", min=1, max=20)
