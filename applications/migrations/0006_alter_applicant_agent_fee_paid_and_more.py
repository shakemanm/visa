# Generated by Django 5.2.1 on 2025-06-07 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0005_applicant_contract_date_applicant_contract_generated_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicant',
            name='agent_fee_paid',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='applicant',
            name='agent_fee_paid_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='applicant',
            name='appointment_booked',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='applicant',
            name='deposit_slip_sent',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='applicant',
            name='deposited_at_standard_bank',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='applicant',
            name='documents_sent',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='applicant',
            name='payment_reflected',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='applicant',
            name='submitted',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='applicant',
            name='visa_status',
            field=models.BooleanField(blank=True, choices=[(None, 'Pending'), (True, 'Granted'), (False, 'Denied')], null=True),
        ),
    ]
