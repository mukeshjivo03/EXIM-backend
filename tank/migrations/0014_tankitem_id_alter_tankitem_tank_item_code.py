import uuid
from django.db import migrations, models


def populate_uuids(apps, schema_editor):
    TankItem = apps.get_model('tank', 'TankItem')
    for obj in TankItem.objects.all():
        obj.id = uuid.uuid4()
        obj.save(update_fields=['id'])


class Migration(migrations.Migration):

    dependencies = [
        ('tank', '0013_rename_item_tanklog_item_code_tanklog_item_name'),
    ]

    operations = [
        # Step 1: drop FK constraints from dependent tables
        migrations.RunSQL(
            "ALTER TABLE stock_status DROP CONSTRAINT IF EXISTS stock_status_item_code_id_6bbf67ca_fk_tank_item_tank_item_code;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            "ALTER TABLE tank_data DROP CONSTRAINT IF EXISTS tank_data_item_code_id_908c8fdf_fk_tank_item_tank_item_code;",
            reverse_sql=migrations.RunSQL.noop,
        ),

        # Step 2: drop old PK constraint
        migrations.RunSQL(
            "ALTER TABLE tank_item DROP CONSTRAINT tank_item_pkey;",
            reverse_sql=migrations.RunSQL.noop,
        ),

        # Step 3: add uuid column as nullable
        migrations.AddField(
            model_name='tankitem',
            name='id',
            field=models.UUIDField(null=True, editable=False),
        ),

        # Step 4: populate existing rows
        migrations.RunPython(populate_uuids, migrations.RunPython.noop),

        # Step 5: make uuid the new PK
        migrations.AlterField(
            model_name='tankitem',
            name='id',
            field=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False),
        ),

        # Step 6: keep tank_item_code as unique only
        migrations.AlterField(
            model_name='tankitem',
            name='tank_item_code',
            field=models.CharField(max_length=50, unique=True),
        ),

        # Step 7: recreate FK constraints
        migrations.RunSQL(
            """
            ALTER TABLE stock_status ADD CONSTRAINT stock_status_item_code_id_6bbf67ca_fk_tank_item_tank_item_code
            FOREIGN KEY (item_code_id) REFERENCES tank_item(tank_item_code) DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            """
            ALTER TABLE tank_data ADD CONSTRAINT tank_data_item_code_id_908c8fdf_fk_tank_item_tank_item_code
            FOREIGN KEY (item_code_id) REFERENCES tank_item(tank_item_code) DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]