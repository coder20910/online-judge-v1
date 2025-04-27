# online-judge-v1
An Online Coding Judge built with Django, Docker, and CodeMirror for compiling and evaluating user-submitted code in Python and C++.

🚀 Features

    🧩 User Authentication — Login, signup, and secure submissions
    💻 Code Editor — Live code editor (with syntax highlighting, themes, comment shortcuts)
    🔥 Run/Submit Code — Execute code with custom input and validate against test cases
    🧪 Test Case Handling — Hidden and sample test cases support
    🛡️ Isolated Execution — Secure server-side code running (subprocess based)
    📝 Submission Tracking — Verdicts like Accepted, Wrong Answer, Runtime Error, etc.
    🎨 Dark/Light Mode Toggle
    📦 Dockerized — Easy deployment anywhere
    ⚡ Performance Optimized — Fast I/O, minimal dependencies

🏗️ Tech Stack

    Layer	Tech Used
    Backend	Django 4.x
    Frontend	HTML5, CSS3, Bootstrap 5, CodeMirror
    Database	SQLite (easy for Docker)
    Code Execution	Python Subprocess
    Containerization	Docker
    Deployment	AWS EC2 (Amzon Linux)

🛠️ Local Setup

    Clone the repository
    git clone https://github.com/coder20910/online-judge-v1
    cd online_judge
    Create .env file
    
    Build and Run Docker containers
    docker build -t online-judge .  
    docker run -p 8000:8000 online-judge

    Visit your app
    http://localhost:8000

⚡ Code Editor Features

    Syntax highlighting for Python, C++
    Toggle Dark/Light Theme
    Auto-language mode switching

🚧 Deployment on AWS EC2

    Launch EC2 instance
    Install Docker
    Clone repository
    Build docker and run
    Open app at http://<your-ec2-ip>:8000

🧹 TODO

    Add Leaderboard
    Add Discussions Section
    Add Another Language Supports like Java and JavaScript 
    Secure Execution inside Docker containers


🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
📜 License

This project is licensed under the MIT License.
🏁 That's it!

Let’s build something amazing 🚀