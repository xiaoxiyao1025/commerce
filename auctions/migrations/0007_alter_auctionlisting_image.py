# Generated by Django 4.2.4 on 2023-08-27 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_alter_auctionlisting_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlisting',
            name='image',
            field=models.ImageField(null=True, upload_to='auctions'),
        ),
    ]
