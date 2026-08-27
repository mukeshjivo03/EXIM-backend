"""Carry existing access across the balance-sheet permission split.

The customer and vendor reports used to share two umbrella permissions. Splitting
them per report would silently lock people out on deploy, so every group and user
holding an umbrella permission is granted the per-report permissions it used to
imply. Nobody gains access to a report they could not already reach.

Reversing the migration removes only the granular grants, leaving the umbrellas.
"""

from django.db import migrations

# umbrella permission -> the per-report permissions it used to cover
GRANT_MAP = {
    ("accounts", "view_customer_balance_sheet"): [
        "view_customer_outstanding",
        "view_customer_ledger",
        "view_customer_aging",
        "view_open_ars",
    ],
    ("sap_sync", "sync_balance_sheet"): [
        "view_vendor_outstanding",
        "view_vendor_ledger",
        "view_open_aps",
        "view_open_pos",
    ],
    # The finance dashboard and bank ledger endpoints were previously ungated;
    # the frontend already gated both pages on bank accounts, so that is the
    # group who legitimately used them.
    ("accounts", "view_bank_accounts"): [
        "view_finance_dashboard",
        "view_bank_ledger",
    ],
}


def _granular(Permission, codename):
    """The new permissions all live on accounts.SystemAccess."""
    return Permission.objects.filter(
        codename=codename, content_type__app_label="accounts"
    ).first()


def ensure_permissions_exist(apps, schema_editor):
    """Create the new Permission rows now.

    Django's create_permissions runs on post_migrate, i.e. after every migration
    in this run has finished - so without this the grant below would find none of
    the new permissions and silently do nothing.
    """
    from django.apps import apps as global_apps
    from django.contrib.auth.management import create_permissions

    app_config = global_apps.get_app_config("accounts")
    app_config.models_module = app_config.models_module or app_config.module
    create_permissions(app_config, verbosity=0)


def grant_granular(apps, schema_editor):
    ensure_permissions_exist(apps, schema_editor)
    Permission = apps.get_model("auth", "Permission")
    Group = apps.get_model("auth", "Group")
    User = apps.get_model("accounts", "User")

    for (app_label, umbrella_code), new_codes in GRANT_MAP.items():
        umbrella = Permission.objects.filter(
            codename=umbrella_code, content_type__app_label=app_label
        ).first()
        if umbrella is None:
            continue                       # umbrella never existed here; nothing to carry

        new_perms = [p for p in (_granular(Permission, c) for c in new_codes) if p]
        if not new_perms:
            continue

        for group in Group.objects.filter(permissions=umbrella):
            group.permissions.add(*new_perms)
        for user in User.objects.filter(user_permissions=umbrella):
            user.user_permissions.add(*new_perms)


def revoke_granular(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    Group = apps.get_model("auth", "Group")
    User = apps.get_model("accounts", "User")

    all_new = [code for codes in GRANT_MAP.values() for code in codes]
    perms = [p for p in (_granular(Permission, c) for c in all_new) if p]
    if not perms:
        return
    for group in Group.objects.all():
        group.permissions.remove(*perms)
    for user in User.objects.all():
        user.user_permissions.remove(*perms)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0009_alter_systemaccess_options"),
    ]

    operations = [
        migrations.RunPython(grant_granular, revoke_granular),
    ]
