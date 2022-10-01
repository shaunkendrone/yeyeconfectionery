

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20190214_1013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='default.jpg', upload_to='profile_pics'),
        ),
    ]
