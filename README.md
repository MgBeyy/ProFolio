# CV Creation and Interview Simulation Project

This project is designed to help users easily manage and evaluate their career information. The project offers the following two main features:

## Features
1. **CV Creation**  
    - Collects educational background, work experience, and other career details from the user.  
    - Information can be uploaded as a file or entered through a web interface.  
    - Generates a professional CV based on the user's information.

2. **Interview Simulation**  
    - Provides an AI-powered system to simulate interviews for the user.  
    - Offers feedback based on the user's responses and evaluates interview performance.

## License
All rights reserved. Please do not steal :) 


## How to Run the Project

To run this Django REST Framework (DRF) project, follow these steps:

1. **Clone the Repository**  
    Clone the project repository to your local machine:
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2. **Set Up a Virtual Environment**  
    Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Dependencies**  
    Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

4. **Apply Migrations**  
    Set up the database by applying migrations:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
    **Note:** If migration files are not created automatically after running `makemigrations`, execute the following commands before running `migrate`:
    ```bash
    python manage.py makemigrations accounts
    python manage.py makemigrations cvgen
    ```

5. **Run the Development Server**  
    Start the Django development server:
    ```bash
    python manage.py runserver
    ```

6. **Access the Application**  
    Open your browser and navigate to `http://127.0.0.1:8000/` to access the application.

7. **API Documentation**  
    If API documentation is available, you can access it at `http://127.0.0.1:8000/api/docs/` (not yet configured).

**Note:** Ensure you have Python installed on your system before running the project


