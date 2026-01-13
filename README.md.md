# 🧠 CATMS: Cognitive Assistive Task Management System

An intelligent Streamlit-based system designed to assist with task management through cognitive support.

![Version](https://img.shields.io/badge/version-1.0.0-blue) ![License](https://img.shields.io/badge/license/CATMS-green) ![Stars](https://img.shields.io/github/stars/shubhammhaske-6610/CATMS?style=social) ![Forks](https://img.shields.io/github/forks/shubhammhaske-6610/CATMS?style=social)

![example-preview-image](/preview_example.png)

## ✨ Features

CATMS is built to provide an intuitive and assistive experience for managing your daily tasks.

*   💡 **Intuitive Task Interface**: Easily add, view, and manage your tasks through a clean and responsive Streamlit user interface.
*   🧠 **Cognitive Assistance**: Get smart suggestions and reminders to help prioritize and complete your tasks effectively.
*   🚀 **Quick Setup & Deployment**: Get the system up and running in minutes with straightforward installation steps.
*   🐍 **Python-Powered**: Developed entirely in Python, making it highly extensible and easy to integrate with other Python tools and libraries.
*   ✅ **Simple Task Tracking**: Mark tasks as complete and keep a clear overview of your progress.

## 🛠️ Installation Guide

Follow these steps to get CATMS running on your local machine.

### Prerequisites

Ensure you have Python 3.8+ installed on your system.

### Step-by-Step Installation

1.  **Clone the Repository**
    Start by cloning the CATMS repository to your local machine:

    ```bash
    git clone https://github.com/shubhammhaske-6610/CATMS.git
    cd CATMS
    ```

2.  **Create a Virtual Environment**
    It's highly recommended to use a virtual environment to manage dependencies:

    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment**
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4.  **Install Dependencies**
    Install all required Python packages using pip:

    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Usage Examples

Once installed, you can launch the CATMS application using Streamlit.

### Running the Application

1.  **Navigate to the Project Root**
    Ensure your virtual environment is active and you are in the `CATMS` directory.

2.  **Start the Streamlit App**
    Run the main application file:

    ```bash
    streamlit run app/main.py
    ```
    This command will open a new tab in your web browser with the CATMS interface (usually at `http://localhost:8501`).

### Basic Interaction

*   **Add a Task**: Use the input field and button to add new tasks to your list.
*   **View Tasks**: All active tasks will be displayed clearly.
*   **Mark as Complete**: Interact with the UI elements (e.g., checkboxes) to mark tasks as finished.

![UI Screenshot Placeholder]

## 🗺️ Project Roadmap

CATMS is continuously evolving! Here are some planned features and improvements:

*   **Version 1.1 - Enhanced Task Management**:
    *   Implement task editing and deletion functionalities.
    *   Add due dates and priority levels for tasks.
    *   Basic data persistence (e.g., using a simple file or SQLite).
*   **Version 1.2 - Smarter Assistance**:
    *   Integrate more advanced cognitive features, such as reminder notifications.
    *   Develop a basic recommendation engine for task prioritization.
*   **Future Enhancements**:
    *   User authentication and multi-user support.
    *   Integration with external calendars or productivity tools.
    *   More sophisticated AI for task breakdown and progress tracking.

## 🤝 Contribution Guidelines

We welcome contributions to make CATMS even better! Please follow these guidelines:

1.  **Fork the Repository**: Start by forking the CATMS repository to your GitHub account.
2.  **Create a New Branch**: Create a new branch for your feature or bug fix. Use descriptive names like `feature/add-task-editing` or `bugfix/fix-ui-alignment`.
3.  **Code Style**: Adhere to PEP 8 style guidelines for Python code.
4.  **Commit Messages**: Write clear and concise commit messages.
5.  **Testing**: If applicable, add or update tests to cover your changes. Ensure all existing tests pass.
6.  **Pull Request (PR)**:
    *   Open a pull request to the `main` branch of the original repository.
    *   Provide a clear description of the changes in your PR.
    *   Reference any related issues.
7.  **Review**: Your PR will be reviewed by the maintainers. Be prepared to make requested changes.

## 📄 License Information

This project is currently not licensed.

Copyright © 2023 shubhammhaske-6610. All rights reserved.