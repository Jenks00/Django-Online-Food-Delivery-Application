from allauth.account.adapter import DefaultAccountAdapter


class BasilAccountAdapter(DefaultAccountAdapter):
    """Prints phone verification codes to the console, mirroring
    EMAIL_BACKEND's console backend for local development. Swap this out
    for a real SMS gateway (e.g. Twilio) in production.

    Phone numbers are stored on customer.models.Customer (one per user)
    since Django's default User model has no phone field of its own.
    """

    def send_verification_code_sms(self, user, phone, code, **kwargs):
        print(f'[dev SMS] Verification code for {phone}: {code}')

    def get_phone(self, user):
        from .models import Customer

        customer = Customer.objects.filter(user=user).exclude(phone__isnull=True).exclude(phone='').first()
        if not customer:
            return None
        return (customer.phone, customer.phone_verified)

    def set_phone(self, user, phone, verified):
        from .models import Customer

        customer, _ = Customer.objects.get_or_create(
            user=user, defaults={'name': user.get_username()}
        )
        customer.phone = phone
        customer.phone_verified = verified
        customer.save(update_fields=['phone', 'phone_verified'])

    def set_phone_verified(self, user, phone):
        from .models import Customer

        Customer.objects.filter(user=user, phone=phone).update(phone_verified=True)

    def get_user_by_phone(self, phone):
        from .models import Customer

        customer = Customer.objects.filter(phone=phone, phone_verified=True).select_related('user').first()
        return customer.user if customer and customer.user else None
