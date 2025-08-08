# 🧠 AI-Powered Lecture Companion

An AI-based interactive learning platform that transforms lecture PDFs or scanned notes into structured, visual, and personalized study material. This platform enhances student understanding through deep summarization, flashcards, MCQs, animated diagrams, and creative educational video suggestions — all generated using Python, GPT, and web APIs.

---

## 🚀 Project Goals

- Summarize lecture PDFs (or scanned images) using GPT
- Remove filler, extract keywords and key points
- Enrich notes with web search, analogies, and real-world examples
- Generate:
  - Deep Summaries & Learning Roadmaps
  - Flashcards with export to Anki or PDF
  - Timed MCQs with Bloom’s Taxonomy tagging
  - Block diagrams (Mermaid.js) and animations
  - Doubt-solving via teacher-style chatbot
  - Ranked educational videos via a YouTube Creativity Filter

---

## 🧱 Tech Stack (Python First)

| Layer       | Technology                |
|------------|----------------------------|
| Frontend   | React.js + TailwindCSS     |
| Backend    | Python (Flask/FastAPI)     |
| AI/LLMs    | OpenAI GPT-4 / Claude via Python |
| PDF/OCR    | PyMuPDF, pdfplumber, pytesseract |
| Video API  | YouTube Data API + Transcripts |
| Sentiment  | VADER / Hugging Face Transformers |
| Diagrams   | Mermaid.js, python-pptx    |
| Auth       | Firebase / Supabase        |
| Database   | MongoDB or PostgreSQL      |
| Deployment | Vercel (frontend), Render (backend) |

---

## 📁 Project Structure (Core Modules)

├── app/
│ ├── api/ # API endpoints
│ ├── services/ # Core logic: summarizer, flashcard_gen, etc.
│ ├── utils/ # Helpers: prompts, exporters, GPT wrappers
│ ├── models/ # DB models
│ └── main.py # Flask or FastAPI entry
frontend/
├── src/components/ # Upload, SummaryView, Flashcards, Quiz, etc.
scripts/
├── youtube_filter.py # Creativity score for educational videos
data/
├── sample_input.pdf


---

## 🧠 Key Features to Implement (Modules)

### ✅ Summarization + Web-Enrichment (GPT via Python)
- `summarizer.py` should generate deep, structured summaries
- Includes roadmap, key concepts, analogies, and misconceptions

### ✅ Flashcard & MCQ Generation
- `flashcard_generator.py` creates Q/A with difficulty tags
- `mcq_generator.py` outputs timed quizzes + answer key

### ✅ Diagram Generator
- `diagram_creator.py` outputs Mermaid.js syntax
- Diagrams rendered on frontend and exported via `python-pptx`

### ✅ YouTube Creativity Filter
- `youtube_filter.py` ranks videos by:
  - Transcript keywords (story, example, imagine)
  - Comment sentiment
  - Teaching style
- Output: top 5 creative videos per topic

### ✅ Doubt Solver
- `doubt_resolver.py` returns tutor-style answers
- Responds conversationally using analogies + visuals

---

## 🧪 How to Run (Dev Mode)

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app/main.py

# Frontend
cd frontend
npm install
npm run dev


📤 Export Options (in export_tools.py):
   PDF (via WeasyPrint or reportlab)

   PPT (via python-pptx)

   Flashcards (PDF or .apkg using genanki)

    MP3 narrated summary (TTS API)

🎯 Next Features To Build:
     Flashcard tagging system

     Audio narration of summaries

     “Explain Highlight” popup in notes

     AI assistant that re-explains in simpler terms

     User dashboard tracking time spent + XP

🔐 Environment Variables (.env):
OPENAI_API_KEY=sk-...
YOUTUBE_API_KEY=...
SERPER_API_KEY=...

💡 Prompt Engineering:
Store all prompt templates in utils/prompts.py. Use role-based prompting for:
  Summarizer
  Flashcard Creator
  MCQ Generator
  Analogies/Examples
  YouTube scoring 
  Doubt resolution



🤝 Contributing
   Clone the repo
   Set up .env with required API keys
   Run backend and frontend
   Submit PR with module-based changes