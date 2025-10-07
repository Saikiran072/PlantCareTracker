from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    IntegerField,
    SelectField,
    TextAreaField,
    DateTimeField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    ValidationError,
    NumberRange,
)
from models import User

# --- Existing forms ---


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "Username already exists. Please choose a different one."
            )

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                "Email already registered. Please use a different one."
            )


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class PlantForm(FlaskForm):
    name = StringField("Plant Name", validators=[DataRequired()])
    species = StringField("Species", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    photo = FileField(
        "Plant Photo",
        validators=[FileAllowed(["jpg", "jpeg", "png", "gif"], "Images only!")],
    )
    watering_frequency = IntegerField(
        "Watering Frequency (days)", validators=[DataRequired(), NumberRange(min=1)]
    )
    sunlight_preference = SelectField(
        "Sunlight Preference",
        choices=[
            ("full_sun", "Full Sun"),
            ("partial_shade", "Partial Shade"),
            ("full_shade", "Full Shade"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Save Plant")


class CareEventForm(FlaskForm):
    event_type = SelectField(
        "Event Type",
        choices=[
            ("watering", "Watering"),
            ("fertilizing", "Fertilizing"),
            ("pruning", "Pruning"),
            ("repotting", "Repotting"),
        ],
        validators=[DataRequired()],
    )
    notes = TextAreaField("Notes")
    submit = SubmitField("Add Care Event")


class JournalEntryForm(FlaskForm):
    content = TextAreaField("Journal Entry", validators=[DataRequired()])
    photo = FileField(
        "Photo (optional)",
        validators=[FileAllowed(["jpg", "jpeg", "png", "gif"], "Images only!")],
    )
    submit = SubmitField("Add Entry")


# --- New form for deleting a care event ---
class DeleteEventForm(FlaskForm):
    """Empty form just for CSRF token in delete button"""

    submit = SubmitField("Delete")


# from flask_wtf import FlaskForm
# from flask_wtf.file import FileField, FileAllowed
# from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, TextAreaField, DateTimeField
# from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange
# from models import User

# class RegistrationForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired()])
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
#     submit = SubmitField('Register')

#     def validate_username(self, username):
#         user = User.query.filter_by(username=username.data).first()
#         if user:
#             raise ValidationError('Username already exists. Please choose a different one.')

#     def validate_email(self, email):
#         user = User.query.filter_by(email=email.data).first()
#         if user:
#             raise ValidationError('Email already registered. Please use a different one.')

# class LoginForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     submit = SubmitField('Sign In')

# class PlantForm(FlaskForm):
#     name = StringField('Plant Name', validators=[DataRequired()])
#     species = StringField('Species', validators=[DataRequired()])
#     location = StringField('Location', validators=[DataRequired()])
#     photo = FileField('Plant Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
#     watering_frequency = IntegerField('Watering Frequency (days)', validators=[DataRequired(), NumberRange(min=1)])
#     sunlight_preference = SelectField('Sunlight Preference',
#         choices=[('full_sun', 'Full Sun'), ('partial_shade', 'Partial Shade'), ('full_shade', 'Full Shade')],
#         validators=[DataRequired()])
#     submit = SubmitField('Save Plant')

# class CareEventForm(FlaskForm):
#     event_type = SelectField('Event Type',
#         choices=[('watering', 'Watering'), ('fertilizing', 'Fertilizing'), ('pruning', 'Pruning'), ('repotting', 'Repotting')],
#         validators=[DataRequired()])
#     notes = TextAreaField('Notes')
#     submit = SubmitField('Add Care Event')

# class JournalEntryForm(FlaskForm):
#     content = TextAreaField('Journal Entry', validators=[DataRequired()])
#     photo = FileField('Photo (optional)', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
#     submit = SubmitField('Add Entry')
