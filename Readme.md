# Houseplant Care Tracker

## Overview

A web-based houseplant care tracking application that helps users manage their plant collections, monitor care schedules, and document plant growth through journaling. The application allows users to register, add plants with photos, track care events (watering, fertilizing, pruning, repotting), and maintain growth journals with timestamped entries.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology Stack**: Server-side rendered templates using Jinja2 with Bootstrap 5 for responsive UI

**Problem Addressed**: Need for a responsive, user-friendly interface accessible across devices without complex frontend build processes

**Solution**: Flask templates with Bootstrap CSS framework and Bootstrap Icons for visual elements

**Rationale**: Server-side rendering simplifies deployment and reduces JavaScript dependencies while Bootstrap provides professional, mobile-responsive components out of the box

### Backend Architecture

**Framework**: Flask (Python web framework)

**Problem Addressed**: Need for rapid development of a data-driven web application with user authentication

**Solution**: Flask with extensions for common functionality:
- Flask-Login: User session management
- Flask-WTF: Form handling and CSRF protection
- Flask-Migrate: Database schema versioning
- APScheduler: Background task scheduling for watering reminders

**Design Pattern**: MVC-style architecture with:
- Models (models.py): SQLAlchemy ORM definitions
- Views (app.py routes): Request handling and business logic
- Templates (templates/): HTML presentation layer

**Authentication**: Flask-Login with password hashing via Werkzeug security utilities

**Pros**: Mature ecosystem, extensive documentation, lightweight and flexible
**Cons**: Requires manual setup of components that may be built-in to larger frameworks

### Data Storage

**Database**: SQLite (via SQLAlchemy ORM)

**Schema Design**:
- **User**: Authentication and ownership (id, username, email, password_hash)
- **Plant**: Core plant data with care requirements (name, species, location, photo, watering_frequency, sunlight_preference, last_watered, user_id)
- **CareEvent**: Historical care activities (event_type, event_date, notes, plant_id)
- **JournalEntry**: Growth documentation (content, photo, entry_date, plant_id)

**Relationships**: 
- One-to-many: User → Plants
- One-to-many: Plant → CareEvents
- One-to-many: Plant → JournalEntries
- Cascade deletes ensure referential integrity

**Rationale**: SQLite provides zero-configuration persistence suitable for single-user or small-scale deployments. SQLAlchemy ORM enables database portability and simplifies queries.

**Alternative Considered**: PostgreSQL for production scalability, but adds deployment complexity

### File Upload System

**Problem Addressed**: Need to store and serve plant photos and journal images

**Solution**: Local filesystem storage in `static/uploads/` directory with secure filename handling via Werkzeug

**Security Measures**:
- File type validation (images only: jpg, jpeg, png, gif)
- Maximum upload size limit (16MB)
- Secure filename sanitization

**Pros**: Simple implementation, no external dependencies
**Cons**: Not suitable for distributed deployments; files not backed up separately from database

### Background Task Scheduling

**Problem Addressed**: Automated watering reminders without manual user checks

**Solution**: APScheduler with BackgroundScheduler running daily checks

**Implementation**: Compares last watered date + watering frequency against current date to identify plants needing water

**Limitation**: Currently only prints to console; would need email/notification integration for production use

**Conditional Initialization**: Scheduler only runs in main process (not Werkzeug reloader) using `WERKZEUG_RUN_MAIN` environment check

### Form Handling and Validation

**Technology**: Flask-WTF with WTForms validators

**Forms Implemented**:
- RegistrationForm: User signup with duplicate checking
- LoginForm: Authentication
- PlantForm: Add/edit plants with file upload
- CareEventForm: Log care activities
- JournalEntryForm: Add journal entries with optional photos

**CSRF Protection**: Enabled globally via CSRFProtect extension

**Custom Validation**: Username and email uniqueness checks in RegistrationForm

## External Dependencies

### Python Packages

- **Flask**: Core web framework
- **Flask-Login**: User session management and authentication
- **Flask-SQLAlchemy**: ORM for database operations
- **Flask-Migrate**: Alembic-based database migrations
- **Flask-WTF**: Form rendering and validation with CSRF protection
- **WTForms**: Form field definitions and validators
- **APScheduler**: Background task scheduling
- **Werkzeug**: Security utilities (password hashing, secure filenames)

### Frontend Dependencies

- **Bootstrap 5.3.0**: CSS framework via CDN
- **Bootstrap Icons 1.11.1**: Icon library via CDN

### Environment Configuration

- **SESSION_SECRET**: Flask secret key for session encryption (defaults to development value)
- **SQLALCHEMY_DATABASE_URI**: Database connection string (currently hardcoded to SQLite)
- **WERKZEUG_RUN_MAIN**: Internal flag to prevent duplicate scheduler initialization

### Static Assets

- Custom CSS in `static/css/style.css` for timeline visualizations and card hover effects
- User-uploaded images stored in `static/uploads/`
