from django import forms
from .models import Prosthesis, Request, RequestStatus


class ProsthesisForm(forms.ModelForm):
    class Meta:
        model = Prosthesis
        fields = ['prosthesis_type', 'name', 'description', 'price', 'image', 'tags', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['request_type', 'contact_name', 'contact_email', 'message', 'prosthesis']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем начальный статус автоматически в view,
        # поэтому поле status не включено в форму
        self.fields['prosthesis'].required = False
