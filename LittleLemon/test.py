from django.test import TestCase
from LittleLemonAPI.models import Menu, Category

class MenuTest(TestCase):
    def setUp(self):
        category = Category.objects.create(slug="desserts", title="Desserts")
        self.item = Menu.objects.create(
            title="IceCream", price=80, featured=True, category=category
        )

    def test_get_item_title(self):
        self.assertEqual(self.item.title, 'IceCream')
