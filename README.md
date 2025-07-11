# Callture 2 Drive

This project provides a form and backend that, given a beginning and end date uploads all Callture recordings to a specified folder in a Shared drive.

## Running Locally

### 1. Set Up Virtual Environment

Create a virtual environment using Python’s built-in `venv`:

```bash
python -m venv .venv
```

Activate the virtual environment:

- On Windows: \
  `.venv\Scripts\activate`
- On MacOS/Linux: \
  `source .venv/bin/activate`

This ensures that any Python packages you install are isolated to this specific environment

### 2. Install Dependencies

Install the required dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. **Add a service account key**

To run the backend, a Google Cloud service account key is required.

1. Obtain or create a service account key file.
   - To create your own key, follow the instructions [here to create a project](https://cloud.google.com/iam/docs/service-accounts-create), and then [here to get the service account key](https://stackoverflow.com/questions/46287267/how-can-i-get-the-file-service-account-json-for-google-translate-api)
2. Place it in the project root as `service_account.json`
3. This file is **ignored by git** and must never be committed.

### 4. Create a .env file

Certain environment variables are needed for this to run.
You can add them to the environment, or copy the example .env file by running the command

```bash
cp .env.example .env
```

Then fill out the .env file. The following variables are required

| **Variable**   | **Description**                                                    |
| -------------- | ------------------------------------------------------------------ |
| USERNAME       | Your callture username you use to log in                           |
| PASSWORD       | Your callture password you use to log in                           |
| ROOT_FOLDER_ID | The ID for the root folder your are uploading to in Google Drive   |
| DRIVE_ID       | The ID for the shared folder your are uploading to in Google Drive |

### 5. Run the Backend

To start the Flask backend locally, run:

```bash
python -m flask --app api/index run
```

The application is now available at `http://localhost:5000`
