# Basil &mdash; Online Food Delivery Platform

A Django application that models a full food-delivery operation as three
connected roles working off one shared order pipeline: a **customer**
storefront, a **kitchen** dashboard, and a **dispatch** dashboard. An order
placed by a customer appears on the kitchen board immediately, moves through
the kitchen's workflow, and hands off to dispatch for delivery &mdash; with
every status change visible in real time to whoever needs to see it.

```
placed --> cooking --> ready --> out for delivery --> delivered
customer         kitchen            dispatch
```

## Screenshots

| Customer menu | Customer cart & checkout |
| --- | --- |
| ![Customer menu](assets/screenshots/customer-menu.png) | ![Customer cart](assets/screenshots/customer-cart.png) |

| Kitchen dashboard | Dispatch dashboard |
| --- | --- |
| ![Kitchen dashboard](assets/screenshots/cook-dashboard.png) | ![Dispatch dashboard](assets/screenshots/dispatch-dashboard.png) |

## Features

### Customer storefront
- Browse the full menu with search by dish name or description.
- Add dishes to a cart that persists for anonymous visitors via a device
  cookie, or against a signed-in account.
- Adjust quantities, remove items, and see a running order total.
- Single-page checkout that captures name, email, delivery address, and
  phone number, then submits the order straight to the kitchen.
- Order confirmation page with a full itemized summary.

### Kitchen dashboard (`/cook/dashboard/`)
- A kanban-style board with three columns: **New**, **Cooking**, and
  **Ready for pickup**.
- Today's revenue and order count at a glance.
- One click to move an order from New &rarr; Cooking &rarr; Ready.
- A detail view per order with the full item list and customer contact
  information.
- Restricted to staff accounts.

### Dispatch dashboard (`/dispatch/dashboard2/`)
- The same kanban layout, picking up where the kitchen leaves off: **Ready
  for pickup**, **Out for delivery**, **Delivered today**.
- One click to move an order from Ready &rarr; Out for delivery &rarr;
  Delivered.
- Restricted to staff accounts.

Both dashboards share one status pipeline defined on the `OrderModel`, so an
order's state is always consistent no matter which dashboard is looking at
it &mdash; there is exactly one source of truth for "where is this order".

## Tech stack

- **Backend:** Django 4.2 (LTS)
- **Auth:** django-allauth, restricted to staff sign-in (public sign-up is
  disabled by a custom account adapter &mdash; this is an internal tool for
  the kitchen and dispatch teams, not a customer login system)
- **Database:** SQLite by default (swap `DATABASES` in `settings.py` for
  Postgres/MySQL in production)
- **Frontend:** hand-written CSS with a small design-token system (no
  Bootstrap, no Tailwind, no CDN dependency &mdash; the UI works fully
  offline) and a handful of lines of vanilla JavaScript
- **Static files / production serving:** WhiteNoise
- **WSGI server:** Gunicorn

## Local setup

```bash
# 1. Clone and enter the project
git clone https://github.com/Jenks00/Django-Online-Food-Delivery-Application.git
cd Django-Online-Food-Delivery-Application

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables (all optional for local dev)
cp .env.example .env

# 5. Apply migrations
python manage.py migrate

# 6. Create a staff account (used to sign in to both dashboards)
python manage.py createsuperuser

# 7. (Optional) seed a demo menu and a handful of sample orders across
#    every stage of the pipeline, so the dashboards aren't empty
python manage.py seed_demo_data

# 8. Run the development server
python manage.py runserver
```

Then visit:

- `http://127.0.0.1:8000/` &mdash; customer storefront
- `http://127.0.0.1:8000/cook/dashboard/` &mdash; kitchen dashboard (staff sign-in required)
- `http://127.0.0.1:8000/dispatch/dashboard2/` &mdash; dispatch dashboard (staff sign-in required)
- `http://127.0.0.1:8000/admin/` &mdash; Django admin, for managing menu items directly

## Configuration

All configuration lives in environment variables, read in `Food_delivery/settings.py`
with safe local-development fallbacks so the project runs out of the box
without a `.env` file:

| Variable | Purpose | Local default |
| --- | --- | --- |
| `SECRET_KEY` | Django's cryptographic signing key | a development-only key baked into the repo |
| `DEBUG` | Enables Django's debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hostnames | `localhost,127.0.0.1` |

See `.env.example` for the full list.

## Deployment

The project ships with a `Procfile` for platforms that use one (Heroku-style
buildpacks, Render, Railway, etc.):

```
web: gunicorn Food_delivery.wsgi --log-file -
release: python manage.py migrate --noinput
```

To deploy:

1. Set real values for `SECRET_KEY`, `DEBUG=False`, and `ALLOWED_HOSTS` in
   your platform's environment variable settings.
2. Static files are served by WhiteNoise directly from the Gunicorn process
   &mdash; no separate static file host is required. Run
   `python manage.py collectstatic` as part of your build step (most
   platforms that read a `Procfile` do this automatically).
3. Point `DATABASES` at a managed Postgres/MySQL instance for anything
   beyond a demo deployment &mdash; SQLite is fine for local development but
   is not suitable for concurrent production traffic.
4. Run the `release` command (or `python manage.py migrate` manually) before
   the first deploy.

## Project structure

```
Food_delivery/        Django project package (settings, root urls, wsgi/asgi)
customer/              Storefront: menu, cart, checkout, order model
cook/                   Kitchen dashboard
dispatch/               Dispatch dashboard
templates/              Shared base templates and django-allauth templates
static/                 Hand-written CSS/JS shared across all three roles
assets/screenshots/     Screenshots used in this README
```

## Known limitations

This is a portfolio project, not a production food-delivery platform. A few
deliberate simplifications:

- Payment is "cash on delivery" only &mdash; there is no payment gateway
  integration.
- Staff accounts are created through the Django admin (`createsuperuser` or
  the admin site); there is no self-service staff onboarding flow.
- There is no real-time push between dashboards &mdash; refreshing the page
  picks up the latest state.
