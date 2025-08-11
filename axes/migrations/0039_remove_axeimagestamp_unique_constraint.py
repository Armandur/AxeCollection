from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('axes', '0038_alter_axestamp_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='axeimagestamp',
            unique_together=set(),
        ),
    ] 