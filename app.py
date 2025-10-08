import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from zoneinfo import ZoneInfo
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from models import db, User, Plant, CareEvent, JournalEntry
from forms import (
    RegistrationForm,
    LoginForm,
    PlantForm,
    CareEventForm,
    JournalEntryForm,
    DeleteEventForm,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SESSION_SECRET", "dev-secret-key-change-in-production"
)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///houseplants.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def to_localtime(utc_dt):
    if utc_dt is None:
        return None
    return utc_dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Asia/Kolkata"))


def check_watering_reminders():
    with app.app_context():
        plants = Plant.query.all()
        for plant in plants:
            if plant.last_watered:
                next_watering = plant.last_watered + timedelta(
                    days=plant.watering_frequency
                )
                if datetime.utcnow() >= next_watering:
                    print(f"Reminder: {plant.name} needs watering!")


if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_watering_reminders, trigger="interval", hours=24)
    scheduler.start()


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now registered!", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "danger")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    search_species = request.args.get("species", "").strip()
    search_location = request.args.get("location", "").strip()

    query = Plant.query.filter_by(user_id=current_user.id)

    if search_species:
        query = query.filter(Plant.species.ilike(f"%{search_species}%"))
    if search_location:
        query = query.filter(Plant.location.ilike(f"%{search_location}%"))

    plants = query.all()
    return render_template(
        "dashboard.html",
        plants=plants,
        search_species=search_species,
        search_location=search_location,
    )


@app.route("/plant/add", methods=["GET", "POST"])
@login_required
def add_plant():
    form = PlantForm()
    if form.validate_on_submit():
        filename = None
        if form.photo.data:
            file = form.photo.data
            filename = secure_filename(
                f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
            )
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        plant = Plant(
            name=form.name.data,
            species=form.species.data,
            location=form.location.data,
            photo_filename=filename,
            watering_frequency=form.watering_frequency.data,
            sunlight_preference=form.sunlight_preference.data,
            user_id=current_user.id,
        )
        db.session.add(plant)
        db.session.commit()
        flash("Plant added successfully!", "success")
        return redirect(url_for("dashboard"))
    return render_template("add_plant.html", form=form)


@app.route("/plant/<int:id>")
@login_required
def plant_detail(id):
    plant = Plant.query.get_or_404(id)
    if plant.user_id != current_user.id:
        flash("You do not have permission to view this plant.", "danger")
        return redirect(url_for("dashboard"))

    care_events = (
        CareEvent.query.filter_by(plant_id=id)
        .order_by(CareEvent.event_date.asc())
        .all()
    )
    journal_entries = (
        JournalEntry.query.filter_by(plant_id=id)
        .order_by(JournalEntry.entry_date.asc())
        .all()
    )

    for event in care_events:
        event.local_time = to_localtime(event.event_date)

    for entry in journal_entries:
        entry.local_time = to_localtime(entry.entry_date)

    if plant.last_watered:
        plant.local_last_watered = to_localtime(plant.last_watered)
    else:
        plant.local_last_watered = None

    delete_form = DeleteEventForm()
    care_form = CareEventForm()  # 👈 add this
    journal_form = JournalEntryForm()  # 👈 add this

    return render_template(
        "plant_detail.html",
        plant=plant,
        care_events=care_events,
        journal_entries=journal_entries,
        delete_form=delete_form,
        care_form=care_form,
        journal_form=journal_form,
        form=care_form,
    )


@app.route("/plant/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_plant(id):
    plant = Plant.query.get_or_404(id)
    if plant.user_id != current_user.id:
        flash("You do not have permission to edit this plant.", "danger")
        return redirect(url_for("dashboard"))

    form = PlantForm(obj=plant)
    if form.validate_on_submit():
        plant.name = form.name.data
        plant.species = form.species.data
        plant.location = form.location.data
        plant.watering_frequency = form.watering_frequency.data
        plant.sunlight_preference = form.sunlight_preference.data

        if form.photo.data:
            file = form.photo.data
            filename = secure_filename(
                f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
            )
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            plant.photo_filename = filename

        db.session.commit()
        flash("Plant updated successfully!", "success")
        return redirect(url_for("plant_detail", id=plant.id))

    return render_template("edit_plant.html", form=form, plant=plant)


@app.route("/journal_entry/delete/<int:entry_id>", methods=["POST"])
@login_required
def delete_journal_entry(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    if entry.plant.user_id != current_user.id:
        flash("You do not have permission to delete this journal entry.", "danger")
        return redirect(url_for("dashboard"))

    db.session.delete(entry)
    db.session.commit()
    flash("Journal entry deleted successfully!", "success")
    return redirect(request.referrer or url_for("dashboard"))


@app.route("/plant/<int:id>/delete", methods=["POST"])
@login_required
def delete_plant(id):
    plant = Plant.query.get_or_404(id)
    if plant.user_id != current_user.id:
        flash("You do not have permission to delete this plant.", "danger")
        return redirect(url_for("dashboard"))

    db.session.delete(plant)
    db.session.commit()
    flash("Plant deleted successfully!", "success")
    return redirect(url_for("dashboard"))


@app.route("/care_event/delete/<int:event_id>", methods=["POST"])
@login_required
def delete_care_event(event_id):
    form = DeleteEventForm()
    if form.validate_on_submit():  # <-- ensures CSRF token is valid
        event = CareEvent.query.get_or_404(event_id)
        if event.plant.user_id != current_user.id:
            flash("You do not have permission to delete this event.", "danger")
            return redirect(url_for("dashboard"))

        db.session.delete(event)
        db.session.commit()
        flash("Care event deleted successfully!", "success")
    else:
        flash("Invalid request.", "danger")

    return redirect(request.referrer or url_for("dashboard"))


@app.route("/plant/<int:id>/add_care_event", methods=["POST"])
@login_required
def add_care_event(id):
    plant = Plant.query.get_or_404(id)
    if plant.user_id != current_user.id:
        flash("You do not have permission to add care events to this plant.", "danger")
        return redirect(url_for("dashboard"))

    form = CareEventForm()
    if form.validate_on_submit():
        care_event = CareEvent(
            plant_id=id,
            event_type=form.event_type.data,
            notes=form.notes.data,
            event_date=datetime.utcnow(),
        )
        db.session.add(care_event)

        if form.event_type.data == "watering":
            plant.last_watered = datetime.utcnow()

        db.session.commit()
        flash("Care event added successfully!", "success")

    return redirect(url_for("plant_detail", id=id))


@app.route("/plant/<int:id>/add_journal_entry", methods=["GET", "POST"])
@login_required
def add_journal_entry(id):
    plant = Plant.query.get_or_404(id)
    if plant.user_id != current_user.id:
        flash(
            "You do not have permission to add journal entries to this plant.", "danger"
        )
        return redirect(url_for("dashboard"))

    form = JournalEntryForm()
    if form.validate_on_submit():
        filename = None
        if form.photo.data:
            file = form.photo.data
            filename = secure_filename(
                f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')}_{file.filename}"
            )
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        journal_entry = JournalEntry(
            plant_id=id, content=form.content.data, photo_filename=filename
        )
        db.session.add(journal_entry)
        db.session.commit()
        flash("Journal entry added successfully!", "success")
        return redirect(url_for("plant_detail", id=id))

    return render_template("add_journal_entry.html", form=form, plant=plant)


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

