from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('care_sast', '0002_sasthospital_sastuser_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sastsubmission',
            old_name='errors',
            new_name='gateway_response',
        ),
        migrations.RenameField(
            model_name='sastsubmission',
            old_name='response',
            new_name='callback_response',
        ),
        migrations.AlterField(
            model_name='sastsubmission',
            name='gateway_response',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sastsubmission',
            name='callback_response',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sastsubmission',
            name='gateway_payload',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
