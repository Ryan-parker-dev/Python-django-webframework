<div align="center">

<h1>🏛️ Nova Global University</h1>

<h3>Full-Stack University Admission Portal</h3>

<p>
  <strong>Python • Flask • HTML • CSS • JavaScript • OTP Verification</strong>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5">
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3">
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript">
</p>

</div>

---

<h2>📖 About The Project</h2>

<p>
<strong>Nova Global University</strong> is a full-stack university admission
portal built with <strong>Python Flask</strong>.
</p>

<p>
The project combines a custom university website with an interactive
admission system where students can explore university information,
choose a program, submit their details, and verify their email using
a temporary OTP before completing their application.
</p>

---

<h2>🎯 Project Concept</h2>

<p>
The main idea behind this project is to demonstrate how a modern
university admission website can work as an interactive web application
instead of being only a static webpage.
</p>

<table>
<tr>
<th>Stage</th>
<th>Process</th>
</tr>

<tr>
<td>01</td>
<td>Student explores the university website</td>
</tr>

<tr>
<td>02</td>
<td>Student selects an admission program</td>
</tr>

<tr>
<td>03</td>
<td>Student enters their email and application details</td>
</tr>

<tr>
<td>04</td>
<td>Flask generates a 6-digit OTP</td>
</tr>

<tr>
<td>05</td>
<td>Student verifies the OTP</td>
</tr>

<tr>
<td>06</td>
<td>Verified student submits the application</td>
</tr>

<tr>
<td>07</td>
<td>Application confirmation is displayed</td>
</tr>

</table>

---

<h2>✨ Features</h2>

<ul>
<li>🏛️ University landing page</li>
<li>📚 Schools and program information</li>
<li>👨‍🏫 Faculty and university sections</li>
<li>📝 Online admission application</li>
<li>🔐 6-digit OTP verification</li>
<li>⏱️ 5-minute OTP expiration</li>
<li>🔑 Flask session-based verification</li>
<li>🌍 Country selection</li>
<li>🎓 Course/program selection</li>
<li>📱 Responsive frontend</li>
<li>✅ Application confirmation system</li>
</ul>

---

<h2>🔐 OTP Verification System</h2>

<p>
The application uses a temporary <strong>6-digit OTP</strong> to verify
the applicant's email before allowing the application to be submitted.
</p>

<details>
<summary><strong>How OTP Verification Works</strong></summary>

<br>

```text
Student enters email
        ↓
     Send OTP
        ↓
Flask generates OTP
        ↓
OTP stored temporarily
        ↓
Student enters OTP
        ↓
Flask checks OTP
        ↓
   ┌────┴────┐
   ↓         ↓
 Valid     Invalid
   ↓         ↓
Session    Rejected
Created
   ↓
Application
Allowed
```

</details>

---

<h2>⚙️ Backend</h2>

<p>
The backend is powered by <strong>Flask</strong> and handles routing,
OTP generation, verification, sessions, and application processing.
</p>

<table>
<tr>
<th>Route</th>
<th>Purpose</th>
</tr>

<tr>
<td><code>/</code></td>
<td>University website and application submission</td>
</tr>

<tr>
<td><code>/send-otp</code></td>
<td>Generates and stores a temporary OTP</td>
</tr>

<tr>
<td><code>/verify-otp</code></td>
<td>Verifies the submitted OTP</td>
</tr>

</table>

---

<h2>🖥️ Frontend</h2>

<p>
The frontend is built directly into the Flask application using
<strong>HTML, CSS and JavaScript</strong>.
</p>

<p>
JavaScript communicates with the Flask backend using
<strong>fetch()</strong> requests for OTP generation and verification.
</p>

---

<h2>🧰 Technology Stack</h2>

<table>
<tr>
<th>Technology</th>
<th>Used For</th>
</tr>

<tr>
<td>🐍 Python</td>
<td>Backend programming</td>
</tr>

<tr>
<td>⚗️ Flask</td>
<td>Web framework and backend routes</td>
</tr>

<tr>
<td>🌐 HTML</td>
<td>Website structure</td>
</tr>

<tr>
<td>🎨 CSS</td>
<td>UI design and responsive layout</td>
</tr>

<tr>
<td>⚡ JavaScript</td>
<td>Frontend interaction and API requests</td>
</tr>

<tr>
<td>🔐 Flask Session</td>
<td>Maintaining verification state</td>
</tr>

<tr>
<td>📦 JSON</td>
<td>Communication between frontend and backend</td>
</tr>

</table>

---

<h2>📁 Project Structure</h2>

```text
nova-global-university/
│
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

<details>
<summary><strong>File Details</strong></summary>

<br>

<table>
<tr>
<th>File</th>
<th>Description</th>
</tr>

<tr>
<td><code>app.py</code></td>
<td>Main Flask application containing the backend and frontend</td>
</tr>

<tr>
<td><code>requirements.txt</code></td>
<td>Python dependencies required by the project</td>
</tr>

<tr>
<td><code>.gitignore</code></td>
<td>Files and folders excluded from Git</td>
</tr>

<tr>
<td><code>README.md</code></td>
<td>Project documentation</td>
</tr>

</table>

</details>

---

<h2>🚀 Installation & Setup</h2>

<h3>1. Clone the repository</h3>

```bash
git clone https://github.com/Ryan-parker-dev/nova-global-university.git
```

<h3>2. Enter the project directory</h3>

```bash
cd nova-global-university
```

<h3>3. Install dependencies</h3>

```bash
pip install -r requirements.txt
```

<h3>4. Run the application</h3>

```bash
python app.py
```

<h3>5. Open in your browser</h3>

```text
http://localhost:5000
```

---

<h2>🧪 Demo OTP System</h2>

<p>
For development purposes, the generated OTP is currently printed
to the Flask server console rather than being sent through a real
email service.
</p>

<blockquote>
<strong>Note:</strong> This is a development/demo implementation.
A production application should use a proper email or transactional
messaging provider.
</blockquote>

---

<h2>🔒 Security Notes</h2>

<p>
This project is intended for learning and demonstration purposes.
The current Flask secret key and OTP system should be replaced with
secure production implementations before deploying the application.
</p>

<ul>
<li>Use environment variables for secret keys</li>
<li>Use a secure production secret key</li>
<li>Use a real email/OTP provider</li>
<li>Add persistent database storage</li>
<li>Add stronger input validation</li>
<li>Disable Flask debug mode in production</li>
</ul>

---

<h2>🧠 Concepts Demonstrated</h2>

<p>
This project demonstrates several practical full-stack development
concepts:
</p>

<ul>
<li>Flask application development</li>
<li>HTTP routes and requests</li>
<li>JSON responses</li>
<li>JavaScript-to-Flask communication</li>
<li>OTP generation and expiration</li>
<li>Session-based verification</li>
<li>Form processing</li>
<li>Responsive web design</li>
<li>Frontend/backend integration</li>
</ul>

---

<h2>📌 Project Status</h2>

<p align="center">

<img src="https://img.shields.io/badge/Status-Development-orange?style=for-the-badge">

</p>

<p align="center">
<strong>Built as a full-stack Flask learning and demonstration project.</strong>
</p>

---

<div align="center">

<h3>🏛️ Nova Global University</h3>

<p>Full-Stack University Admission Portal</p>

</div>
