# Generated by Django 4.2.4 on 2023-08-29 00:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0010_catagory_alter_auctionlisting_image_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='auctionlisting',
            old_name='Catagory',
            new_name='catagories',
        ),
    ]
