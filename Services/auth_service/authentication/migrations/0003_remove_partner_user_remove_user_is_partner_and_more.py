# Generated by Django 5.0.6 on 2024-10-14 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('authentication', '0002_customuser'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partner',
            name='user',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_partner',
        ),
        migrations.AddField(
            model_name='user',
            name='partner_documents',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='partner_request_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='partner_request_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('NONE', 'None')], default='NONE', max_length=20),
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('USER', 'Regular User'), ('PARTNER', 'Partner'), ('ADMIN', 'Administrator')], default='USER', max_length=10),
        ),
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='custom_user_set', to='auth.group', verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='custom_user_set', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.DeleteModel(
            name='CustomUser',
        ),
        migrations.DeleteModel(
            name='Partner',
        ),
    ]
