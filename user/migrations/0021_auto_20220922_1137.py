# Generated by Django 2.2.13 on 2022-09-22 08:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0020_authgroup_authgrouppermissions_authpermission_authtokentoken_authuser_authusergroups_authuseruserper'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
        migrations.DeleteModel(
            name='UserUserDetails',
        ),
    ]
