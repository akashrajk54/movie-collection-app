# movie-collection-app
This repository contains a Django-based web application for managing movie collections. Users can browse movies from a third-party API, create collections of their favorite movies. The application features user authentication using JWT and custom middleware to monitor and count the number of requests.


# Setup

   1. Clone the repository:
       git clone https://github.com/akashrajk54/movie-collection-app.git

   2. Navigate to the project directory:
       cd movie-collection-app

   3. Create a virtual environment (optional but recommended):
       python -m venv venv

   4. Activate the virtual environment:
      a). Windows:
          venv\Scripts\activate
      b). Linux/macOS:
          source venv/bin/activate

   5. Install dependencies:
      pip install -r requirements.txt

   6. Set up environment variables by creating a .env file:

       ## DATABASE Use: PostgresSQL
       DATABASE_NAME=
       DATABASE_USER=
       DATABASE_PASSWORD=
       DATABASE_HOST=localhost
       DATABASE_PORT=5432
       
       ## Movie urls
       MOVIE_API_USERNAME=
       MOVIE_API_PASSWORD=
       MOVIE_API_URL=

       Note: There should be no spaces around the "=" sign in to .env file

      ## Please Update DEFAULT_THROTTLE_RATES into the settings currently set to 100/Hours

   7. Run migrations to create the database schema:
      python manage.py makemigrations
      python manage.py makemigrations accounts_engine
      python manage.py makemigrations movies
      python manage.py migrate

   8. Create a superuser (admin) account:
      python manage.py createsuperuser  # Put a username and password.

   9. Run the development server:
      python manage.py runserver
      (by default it will use 8000 port)
