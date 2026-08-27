from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(email, name, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'users'

class SystemAccess(models.Model):
    class Meta:
        managed  = False
        default_permissions = ()

        permissions = [
            ('view_exim_rates' , 'Can see Exim Rates'),
            ('view_director_report' , 'Can See Director Report'),
            ('add_opening_rate' , 'Can Add Opening Rate'),
            ('view_bank_accounts' , 'Can View bank Accounts'),
            ('view_bank_closing' , 'Can View bank closing'),

            # Umbrella permissions kept so existing grants keep working. New work
            # should use the per-report permissions below; these two used to gate
            # every customer/vendor report at once.
            ('view_customer_balance_sheet' , 'Can View Customer Balance Sheet') ,

            # --- Customer reports (was: view_customer_balance_sheet) ---
            ('view_customer_outstanding' , 'Can view Customer Outstanding'),
            ('view_customer_ledger' , 'Can view Customer Ledger'),
            ('view_customer_aging' , 'Can view Customer Aging'),
            ('view_open_ars' , 'Can view Open ARs'),

            # --- Vendor / payable reports (was: sap_sync.sync_balance_sheet) ---
            ('view_vendor_outstanding' , 'Can view Vendor Outstanding'),
            ('view_vendor_ledger' , 'Can view Vendor Ledger'),
            ('view_open_aps' , 'Can view Open APs'),
            ('view_open_pos' , 'Can view Open POs'),

            # --- Bank / finance ---
            ('view_finance_dashboard' , 'Can view Finance Dashboard'),
            ('view_bank_ledger' , 'Can view Bank Ledger'),
        ]

