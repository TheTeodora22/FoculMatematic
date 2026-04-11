# Focul Matematic Project Summary

This document provides a summary of the `FoculMatematicProiect`, a Django-based web application.

## Project Overview

`FoculMatematic` (Romanian for "The Fire of Mathematics") appears to be an educational web application or game designed to help users practice mathematics through quizzes. The project incorporates user accounts and a battle pass system to encourage engagement and track progress.

## Directory Structure and Core Components

The project is organized into several Django apps:

*   `FoculMatematicProiect/`: The main project directory containing global settings (`settings.py`) and URL configurations (`urls.py`).

*   `FoculMatematic/`: This seems to be the core application, likely containing the main logic and user-facing views of the math game.

*   `accounts/`: This app manages user authentication and profiles. It is responsible for user registration, login, and profile management.

*   `quizzes/`: This app likely handles the creation, management, and presentation of math quizzes. It probably defines the models for questions, answers, and quiz results.

*   `battlepass/`: This app implements a battle pass or rewards system. It likely tracks user experience points (XP), levels, and rewards unlocked by completing quizzes or other in-game activities.

*   `db.sqlite3`: The SQLite database file, used for development.

*   `manage.py`: The Django command-line utility for administrative tasks.
