# Generated by Django 4.1.7 on 2023-02-23 18:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('draft', '0007_alter_people_options'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='people',
            table='draft_people',
        ),
    ]