class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = "Withdraw Money"

    def get_initial(self):
        initial = {"transaction_type": WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get("amount")
        bank_balance = UserBankAccount.objects.aggregate(total_balance=Sum("balance"))[
            "total_balance"
        ]
        if bank_balance < amount:
            messages.warning(self.request, "Bank Is Bnkrupt")
        else:
            self.request.user.account.balance -= form.cleaned_data.get("amount")
            self.request.user.account.save(update_fields=["balance"])
            messages.success(
                self.request,
                f'Successfully withdrawn {"{:,.2f}".format(float(amount))}$ from your account',
            )
            send_transaction_email(
                self.request.user,
                amount,
                "Withdrawal Message",
                "./transactions/withdraw_email.html",
            )
        return super().form_valid(form)


class SendMoneyView(TransactionCreateMixin):
    form_class = SendMoneyForm
    template_name = "./transactions/sendmoney.html"
    title = "Send Money"
    success_url = reverse_lazy("transaction_report")

    def get_initial(self):
        initial = {"transaction_type": SEND_MONEY}
        return initial

    def form_valid(self, form):
        account_no = form.cleaned_data.get("account_no")
        amount = form.cleaned_data.get("amount")
        sender = self.request.user.account

        if sender.balance < amount:
            messages.warning(
                self.request, "Insufficient funds to complete this transaction."
            )
            return self.form_invalid(form)

        try:
            reciver = UserBankAccount.objects.get(account_no=account_no)
            reciver.balance += amount
            sender.balance -= amount
            reciver.save(update_fields=["balance"])
            sender.save(update_fields=["balance"])
            messages.success(self.request, "Send Money Successful")
            send_transaction_email(
                self.request.user,
                amount,
                "Send Money",
                "transactions/sendmoney_email.html",
            )
            send_transaction_email(
                reciver.user,
                amount,
                "Receive Money",
                "transactions/receivemoney_email.html",
            )

            return super().form_valid(form)

        except UserBankAccount.DoesNotExist:
            form.add_error("account_no", "Invalid Account No")
            return super().form_invalid(form)
