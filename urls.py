from django.urls import path
from .views import SendMoneyView, WithdrawMoneyView

urlpatterns = [
    path("withdraw/", WithdrawMoneyView.as_view(), name="withdraw_money"),
    path("sendmoney/", SendMoneyView.as_view(), name="sendmoney"),
]
