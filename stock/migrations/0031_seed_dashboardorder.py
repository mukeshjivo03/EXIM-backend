# Seed DashboardOrder with the previously hardcoded ITEM_CODE_DISPLAY_ORDER.
# The old order was keyed by TankItem.id (UUID); DashboardOrder.item_code stores
# tank_item_code (to_field='tank_item_code'), so we resolve id -> tank_item_code
# at migration time. UUIDs that no longer resolve to a TankItem are skipped.
from django.db import migrations


ITEM_CODE_DISPLAY_ORDER = [
    'c2c38f74-2449-483f-b096-4ef91584f782',  # RM0CDRO - CRUDE CANOLA
    '73109f7d-4e6b-46c1-9209-dfcbc463775e',  # RM00C01 - CANOLA
    'a7caf120-054f-4ffe-89ce-2b3c1f5a9718',  # RM00CPC - COLDPRESS CANOLA
    'a4e8fc5d-0e43-45e9-afae-0b6ebdee1dc0',  # RM00C02 - CANOLA 2B

    'e25db225-689b-4fb5-b1c0-d7fcdde5fc70',  # RM00SBR - SOYABEAN
    '4d637889-a625-4f03-8f9d-4babb62fa3be',  # RM00SBD - SOYADEO
    'fca27ec7-a34a-4532-907c-657f89c62501',  # RM0SB02 - SOYABEAN 2B

    'd195cbd9-992b-463a-90f7-484c767bca1f',  # RM00MK01 - MUSTARD KACHI GHANI
    'a8e79643-62ea-4835-9242-5aa5f63aad7b',  # RM0GNCP - GROUNDNUT FILTER

    '4a1d3b03-6540-4373-8220-d072c69c8371',  # RM000SF - SUNFLOWER
    '5c5c043c-d172-49ec-a8cf-bd2a3d409452',  # RM00SF2 - SUNFLOWER OIL 2B
    '77a8fd67-495e-481d-b751-6dcc8323acaa',  # RM00MDO
    'c4a67ea6-b9bd-4051-bdb9-997e2f24b1e5',  # RM000MR - MUSTARD REFINED

    'e6d97064-2345-4ada-ad6e-2da929b62068',  # RMMKG02 - MUSTARD KACHI GHANI 2B

    'b11dc909-4a6b-4f79-9194-1bced0f802a2',  # RM00GNR - GROUNDNUT REFINED

    # RM00GNR02 - NOT FOUND IN TABLE
    '5e890081-d306-426e-a5cf-ed989dbf2189',
    '3d6f4ce7-5996-4d60-bdd4-3bb4fb997c2a',  # RM00GD - GOLD

    '3d1056b1-25aa-4663-8c71-4e90790c510b',  # RM00RBR - RICE BRAN REFINED
    '22d62296-c24b-4536-8bcc-821ff379b1d2',  # RM00RBD - RICEDEO
    '516ac941-33e9-4e1c-b1f9-d9e067c9e6f8',  # RM0RB02 - RICEBRAN 2B

    'e9f7e282-8270-488d-a70c-99bc3d8ea701',  # RM00CSR - COTTONSEED
    '5ec9baaa-a208-4916-8a23-376f617ab934',  # RMCSR02 - COTTONSEED 2B

    'a1a93ca9-ffeb-4ea1-a68b-605e28255678',  # RM00VNP - VANASPATI
    '9ea3691d-73b8-4351-8242-d773e4f0e64f',  # RM0CCNT - COCONUT

    'c6420d4c-c736-4f5e-990b-7771b059f1ac',  # RM0SESM - SESAME
    '6bdeafc4-be36-490a-bf9e-c063ae8eb8c6',  # RMSESMT - SESAME TOASTED

    # t2
    '88eeac70-62a0-4158-af25-87a3a96599ca',  # RM00P02 - POMACE 2B
    '12ac4727-f72e-456e-845b-d2597bccf42d',  # RM00P03 - POMACE 3C
    'e601fc1c-2c13-489c-a858-c7132b828293',  # RM0EV02 - EXTRA VIRGIN 2B
    'b9f57f80-9ce6-4a98-a120-b42eecb90896',  # RM0EL02 - EXTRA LIGHT 2B
    'cef9e19e-164a-4026-9ee0-ff090e619925',  # RMSOLIVE - SO OLIVE

    # t3
    'a9da1950-0e88-4fdb-85a3-19f419174a0b',  # RM00P01 - POMACE
    '03cbc3fb-b16f-4fc9-adf2-380787ba06b4',  # RM0EL01 - EXTRA LIGHT
    '8a1de505-adc7-497a-8d89-e654bebadf7a',  # RM0EV01 - EXTRA VIRGIN
    '5949da6f-c2d1-435c-9a7c-13607265e5b8',  # RM0HOSF - HIGH OLIEC SF
]


def seed_dashboard_order(apps, schema_editor):
    TankItem = apps.get_model('tank', 'TankItem')
    DashboardOrder = apps.get_model('stock', 'DashboardOrder')

    id_to_code = {
        str(row['id']): row['tank_item_code']
        for row in TankItem.objects.filter(
            id__in=ITEM_CODE_DISPLAY_ORDER
        ).values('id', 'tank_item_code')
    }

    order_number = 0
    for item_uuid in ITEM_CODE_DISPLAY_ORDER:
        tank_item_code = id_to_code.get(item_uuid)
        if not tank_item_code:
            continue
        DashboardOrder.objects.update_or_create(
            item_code_id=tank_item_code,
            defaults={'order_number': order_number},
        )
        order_number += 1


def unseed_dashboard_order(apps, schema_editor):
    DashboardOrder = apps.get_model('stock', 'DashboardOrder')
    DashboardOrder.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0030_dashboardorder'),
    ]

    operations = [
        migrations.RunPython(seed_dashboard_order, unseed_dashboard_order),
    ]
