from allauth.account.adapter import DefaultAccountAdapter

ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True


class NoNewUsersAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False
