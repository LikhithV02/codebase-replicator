# Codebase Replicator

A Streamlit web app that uses Groq AI to reconstruct code from screenshots!

## 🚀 Features

- **Take or upload screenshots** of code (max 5 per batch)
- **AI-powered code reconstruction** using Groq's Llama model
- **Edit and download** the generated code
- **Project overview** for managing multiple files
- **Download all files as a ZIP**
- **Step-by-step instructions** for best results

---

## 🛠️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/codebase-replicator.git
cd codebase-replicator
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your Groq API key

The app requires a Groq API key. Set it as an environment variable:

```bash
export GROQ_API_KEY=your_groq_api_key_here
```

> **Note:** The current code uses a hardcoded API key for demo purposes. For production, always use environment variables for security.

### 4. Run the app
```bash
streamlit run app.py
```

---

## 🖥️ Usage

1. **Enter the filename** (e.g., `main.py`, `utils.py`).
2. **Take screenshots** of your code (or upload existing screenshots).
3. **Generate code** from the screenshots using Groq AI.
4. **Review, edit, and download** the generated code.
5. **Repeat** for other files or more screenshots.
6. **Download all files as a ZIP** from the Project Overview section.

---

## 📋 Tips for Best Results

- Use a consistent font size in your code editor
- Ensure good contrast between text and background
- Include some overlap between screenshots to avoid missing lines
- The AI works best with Python code, but can handle other languages
- For large files, process in batches and manually combine the generated code

---

## 📝 Example Workflow

1. Open your code in your editor.
2. Enter the filename in the sidebar.
3. Click "Take Screenshot" (you have 2 seconds to switch to your code window).
4. Scroll and take more screenshots as needed (up to 5 per batch).
5. Click "Generate Code from Screenshots".
6. Review, edit, and download the code.
7. Repeat for other files.

---

## 🧑‍💻 Tech Stack
- [Streamlit](https://streamlit.io/)
- [Groq API](https://console.groq.com/)
- [Pillow (PIL)](https://python-pillow.org/)

---

## ⚠️ Limitations & Notes
- Max 5 screenshots per batch (Groq API limitation)
- The app currently uses a hardcoded API key (update for production use)
- Only works on systems where PIL.ImageGrab is supported (may not work on some Linux servers)

---

## 📄 License

MIT License. See [LICENSE](LICENSE).