from wtforms import Form, TextAreaField, validators


class MessageForm(Form):
    message = TextAreaField("message", validators=[validators.Length(min=1)])