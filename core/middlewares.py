from core.methods import _user
from shop.models import UserInstallmentPayDetail


def get_incomplete_installment_ids(user):
    qs = UserInstallmentPayDetail.objects.filter(user=user, completed=False, amount_paid=None)
    if qs.count() > 0:
        ids = qs.values_list('id', flat=True)
        return list(ids)
    return None


class ShopMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = _user(request)
        if user.is_authenticated:
            installment_ids = get_incomplete_installment_ids(user)
            if installment_ids:
                request.installment_ids = installment_ids
        response = self.get_response(request)
        return response
