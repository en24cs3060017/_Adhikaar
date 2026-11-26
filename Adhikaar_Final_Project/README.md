# ADHIKAAR browser project

This is a browser-based classroom version of the original ADHIKAAR Tkinter project. Its welcome screen follows `main1.py`: dark brown and gold styling, a Lady Justice image, English/Hindi selection, a location step, and three clear Urgent/Summarised/Detailed cards. The guided screen adds a situation choice (such as missing vehicle papers or a traffic challan), cyber issue guidance, report statement examples, and official resources. The original desktop app is included in `desktop_original/` for reference.

The app now requires an account to open the guide. Accounts are stored in MongoDB using a normalized email and a salted PBKDF2 password hash; passwords are not stored as readable text. Registration checks email format, password length and composition, and matching confirmation. The user email is account data; it is not added to feedback records.

The guide includes an optional live legal-document search using the Indian Kanoon API. It searches only preset terms for the selected topic and situation; it never sends the user's description to that API. Results link to their documents and are labeled as research references, not legal conclusions. You need your own API token to use it. API calls are prepaid; pricing currently lists ₹0.50 per search, and the provider advertises ₹500 of development credit after signup. Its terms require the unmodified "Powered by IKanoon" logo when showing results and describe its data as provided as-is. Check the provider's current pricing and terms before deploying.

Use Madhya Pradesh for state-specific guidance. This project has not yet reviewed legal guidance for other states; the welcome screen displays this caution and routes other selections only to national resources. Madhya Pradesh districts must be selected from the official district list; the app does not accept arbitrary location text. Guided answers are educational; they do not provide legal advice, diagnose an offence, or assign a legal section to a person's facts. Situation choices cover missing vehicle papers, traffic challans, police interactions, and detention/arrest, with cautious general next steps. The app requires a meaningful description of at least 15 characters that matches the selected topic and situation. It blocks common sensitive details, harmful requests, and clear topic mismatches with a correction message. These checks cannot catch every kind of private information, so users should still avoid entering it. The optional AI follow-up feature from the original app is also available when you provide an Anthropic API key; questions sent through it go to Anthropic and may incur API charges. Chat descriptions and follow-up questions are not stored in MongoDB. Feedback is stored separately and is not linked to the login email. The original `main1.py` is preserved in `desktop_original/` as a reference.

## Run it on your laptop

1. Install Python 3.10 or newer and MongoDB Community Server.
2. Start the MongoDB Server service in Windows: press **Windows+R**, type `services.msc`, find the MongoDB Server service, and choose **Start**. The local default connection is `mongodb://localhost:27017`.
3. Open CMD in this project folder.
4. Create and activate an environment:

   ```cmd
   py -m venv .venv
   .venv\Scripts\activate
   ```

5. Install packages and start the website:

   ```cmd
   py -m pip install -r requirements.txt
   py -m streamlit run app.py
   ```

Streamlit opens the sign-in page in your browser. Create an account, then sign in. The guide requires MongoDB; local setup uses the laptop's MongoDB service. If MongoDB is configured with authentication, set the correct `MONGODB_URI` in `.streamlit/secrets.toml`.

## Connect the MongoDB on your laptop

Make sure MongoDB Community Server is installed and running locally. If you want to set a database name or other settings, copy `secrets.example.toml` to `.streamlit/secrets.toml` (the `.streamlit` folder is already included). The district choices come from the [official Madhya Pradesh District Portal](https://mpdistricts.nic.in/). The example uses:

```toml
MONGODB_URI = "mongodb://localhost:27017"
MONGODB_DATABASE = "adhikaar_demo"
ANTHROPIC_API_KEY = ""
```

The app creates a `users` collection for login and a separate `feedback` collection. User records store email, a random salt, a password hash, and account creation time. Feedback stores the rating, selected category, language, answer style, selected topic, and timestamp; it is not linked to the login email. The app does not write the description or chat text. Keep `.streamlit/secrets.toml` private.

## Enable the legal-document API

1. Create an account at [Indian Kanoon API Services](https://api.indiankanoon.org/) and create/copy your API token from its service profile.
2. Add the token to `.streamlit/secrets.toml`:

   ```toml
   INDIANKANOON_API_TOKEN = "your token"
   ```

3. Restart Streamlit. After a guide is generated, open **Search legal references (Indian Kanoon API)** and click **Search legal documents**. The search is run only when you click the button.

The integration uses Indian Kanoon's documented HTTPS search endpoint and `Authorization: Token …` header. Its API pricing and token process can change. The service is not an official government legal authority, so open and review each linked source. Keep the token private and add it to Streamlit's private Secrets settings when hosted.

## Publish a shareable link

1. Create a GitHub account if you do not already have one.
2. Create a new repository and upload the contents of this project folder. Do not upload `.streamlit/secrets.toml`, `.env`, or any passwords.
3. For online MongoDB, create a MongoDB Atlas database. Add a database user and allow network access from Streamlit Community Cloud (Atlas may require `0.0.0.0/0` for this host; use a strong unique database password and least-privilege database access).
4. In Streamlit Community Cloud, choose **Create app**, select your GitHub repository, and set the main file to `app.py`.
5. In the app's **Settings → Secrets**, add:

   ```toml
   MONGODB_URI = "your Atlas connection string"
   MONGODB_DATABASE = "adhikaar_demo"
   INDIANKANOON_API_TOKEN = "your Indian Kanoon API token"
   ```

6. If you want AI follow-up, add `ANTHROPIC_API_KEY = "your key"` to Streamlit's private Secrets settings. Otherwise leave it out.
7. Deploy. Streamlit gives you a link you can share with your teacher. MongoDB must be configured for account creation and sign-in to work online.

Your laptop's `mongodb://localhost:27017` address only points to MongoDB on your laptop. A hosted website cannot reach that local database, so use Atlas for the published app. Never put a real database password in GitHub or in this README.

## Original desktop version

The unmodified source from the supplied ZIP is in `desktop_original/`. Its original startup command is `python main.py` after installing its requirements and optional background image. The browser app is started with `streamlit run app.py` instead.
