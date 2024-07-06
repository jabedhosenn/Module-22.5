class SendMoneyForm(TransactionForm):
    account_no = forms.IntegerField()
    amount = forms.DecimalField(max_digits=10, decimal_places=2)

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount <= 0:
            raise forms.ValidationError("Insufficient amount")
        return amount
