# Generated by Django 4.2.2 on 2023-07-25 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_shoppingcart_alter_tags_slug_delete_buylist_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientsinrecipes',
            name='amount',
            field=models.SmallIntegerField(help_text='Количество ингредиента', verbose_name='Количество'),
        ),
    ]
