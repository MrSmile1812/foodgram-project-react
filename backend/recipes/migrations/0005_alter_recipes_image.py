# Generated by Django 4.2.2 on 2023-07-25 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_recipes_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipes',
            name='image',
            field=models.ImageField(help_text='Фотография блюда', upload_to='recipes/images/', verbose_name='Фотография'),
        ),
    ]
