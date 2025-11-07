import django.db.models.deletion
from django.db import migrations, models


def forwards_func(apps, schema_editor):
    Contact = apps.get_model('contacts', 'Contact')
    ContactEmail = apps.get_model('contacts', 'ContactEmail')
    ContactPhone = apps.get_model('contacts', 'ContactPhone')

    for contact in Contact.objects.all():
        if contact.email:
            ContactEmail.objects.create(contact=contact, email=contact.email)
        if contact.phone_number:
            ContactPhone.objects.create(contact=contact, phone_number=contact.phone_number)


def backwards_func(apps, schema_editor):
    Contact = apps.get_model('contacts', 'Contact')
    ContactEmail = apps.get_model('contacts', 'ContactEmail')
    ContactPhone = apps.get_model('contacts', 'ContactPhone')

    for contact in Contact.objects.all():
        first_email = ContactEmail.objects.filter(contact=contact).first()
        first_phone = ContactPhone.objects.filter(contact=contact).first()
        contact.email = first_email.email if first_email else ''
        contact.phone_number = first_phone.phone_number if first_phone else ''
        contact.save(update_fields=['email', 'phone_number'])


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name='contact',
            name='phone_number',
            field=models.CharField(blank=True, max_length=25),
        ),
        migrations.CreateModel(
            name='ContactEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emails', to='contacts.contact')),
            ],
        ),
        migrations.CreateModel(
            name='ContactPhone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=25)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phones', to='contacts.contact')),
            ],
        ),
        migrations.RunPython(forwards_func, backwards_func),
    ]


