# Generated by Django 4.2.2 on 2023-08-01 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urunler', '0005_shopcard_stock'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shopcard',
            name='stock',
        ),
        migrations.AddField(
            model_name='product',
            name='stock',
            field=models.IntegerField(default=0, null=True, verbose_name='Ürün Stok Durumu'),
        ),
    ]
