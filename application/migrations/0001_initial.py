# Generated by Django 3.2.12 on 2022-04-14 15:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Engineer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_on_call', models.BooleanField(default=False, help_text='States if engineer is currently on call', verbose_name='on call status')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Meaningful title of the ticket', max_length=300, unique=True, verbose_name='ticket title')),
                ('created', models.DateTimeField(verbose_name='date created')),
                ('priority', models.CharField(choices=[('L', 'Low'), ('M', 'Medium'), ('H', 'High')], default='L', help_text='Describes the importance of the ticket, L = Low, M = Medium, H = High', max_length=50, verbose_name='ticket priority')),
                ('description', models.CharField(default='', help_text='Describes the issue and any action items an on-call engineer has reported', max_length=300, verbose_name='ticket description')),
                ('status', models.CharField(choices=[('TD', 'To do'), ('IP', 'In progress'), ('D', 'Done')], default='TD', help_text='Describes the current state of the ticket. TD = To do, IP = In progress, D = Done', max_length=50, verbose_name='ticket status')),
                ('reporter', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='application.engineer')),
            ],
        ),
    ]
