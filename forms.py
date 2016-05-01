from flask_wtf import Form, RecaptchaField
from wtforms import StringField, TextAreaField, SubmitField, validators


class ContactForm(Form):
    """This function returns a contact form.
    """
    name = StringField("Ihr Name", [validators.DataRequired('Bitte geben Sie Ihren Namen ein.')])
    email = StringField("E-Mail-Adresse", [validators.DataRequired('Bitte geben Sie Ihre E-Mail-Adresse ein.'), validators.Email('Bitte geben Sie eine korrekte E-Mail-Adresse ein.')])
    message = TextAreaField("Nachricht", [validators.DataRequired('Bitte geben Sie Ihre Nachricht ein.')])
    recaptcha = RecaptchaField()
    submit = SubmitField("Absenden")