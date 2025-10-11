# JobMatch AI - Skill-to-Job Recommender System

A hackathon project that predicts job-role compatibility using NLP embeddings of resumes and job descriptions. Features salary prediction and company-fit scoring for monetization.

## 🚀 Features

- **Resume Analysis**: Upload PDF/DOCX resumes and extract skills, experience, and education
- **Job Matching**: Semantic similarity matching using Sentence-BERT embeddings (384-dim vectors)
- **Salary Prediction**: ML-powered salary range predictions using Random Forest
- **Company-Fit Scoring**: Calculate cultural and work-style compatibility
- **Premium Features**: Detailed insights and analytics for premium users ($9.99/month)

## 🛠 Tech Stack

### Backend
- **FastAPI**: Modern Python web framework with automatic API docs
- **Sentence-BERT**: NLP embeddings (all-MiniLM-L6-v2 model)
- **NeonDB**: Serverless PostgreSQL database (free tier)
- **Qdrant Cloud**: Vector database for similarity search (free tier)
- **scikit-learn**: Random Forest for salary prediction

### Frontend
- **React 18**: UI framework with hooks
- **Vite**: Fast build tool
- **Tailwind CSS**: Utility-first styling
- **React Router**: Client-side routing

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- NeonDB account (https://neon.tech - free tier)
- Qdrant Cloud account (https://cloud.qdrant.io - free tier)

## 🔧 Setup Instructions

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

**Update `.env` with your credentials:**
```env
DATABASE_URL=postgresql://user:password@host/dbname  # From NeonDB
QDRANT_URL=https://your-cluster.qdrant.io           # From Qdrant Cloud
QDRANT_API_KEY=your-api-key-here                    # From Qdrant Cloud
JWT_SECRET=your-secret-key-here                      # Generate random string
QDRANT_COLLECTION_NAME=jobs
```

**Initialize database and load sample data:**
```bash
# Create tables
python scripts/init_db.py

# Load sample jobs (15 jobs across different roles)
python scripts/load_jobs.py

# Create demo users (optional)
python scripts/seed_demo_users.py
```

**Start backend server:**
```bash
uvicorn app.main:app --reload --port 8000
```

API available at: `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend available at: `http://localhost:5173`

## 👤 Demo Accounts

After running `seed_demo_users.py`:

1. **Free User**: demo@jobmatch.ai / demo123
2. **Premium User**: premium@jobmatch.ai / premium123
3. **Test User**: john@example.com / password123

## 📁 Project Structure

```
jobmatch-ai/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints (auth, jobs, resumes, profile, premium)
│   │   ├── core/             # Config, security, database
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic validation schemas
│   │   └── services/         # Business logic (embeddings, matching, ML)
│   ├── data/                 # Sample data (jobs, salary training data)
│   ├── scripts/              # Database initialization and seeding
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable components (Layout, ProtectedRoute)
│   │   ├── context/          # React context (AuthContext)
│   │   ├── pages/            # Page components (Login, Dashboard, Profile, etc.)
│   │   └── App.jsx
│   └── package.json
└── README.md
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login (returns JWT token)

### Resume
- `POST /api/resumes/upload` - Upload PDF/DOCX resume

### Jobs
- `GET /api/jobs/recommendations` - Get personalized job matches (top 10)
- `GET /api/jobs/{job_id}` - Get job details
- `POST /api/jobs/save` - Save job to favorites
- `GET /api/jobs/saved/list` - Get saved jobs

### Profile
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update preferences

### Premium
- `POST /api/premium/upgrade` - Upgrade to premium
- `GET /api/premium/features` - List premium features
- `GET /api/premium/status` - Check premium status

## 💎 Free vs Premium Features

### Free Tier
- Basic job matching (top 10 results)
- Compatibility scores
- Basic salary ranges
- Basic company-fit scores
- Skill matching/gap analysis

### Premium Tier ($9.99/month)
- Unlimited job searches
- Detailed salary predictions with percentiles
- Salary confidence intervals
- Company-fit score explanations
- Detailed skill gap analysis
- Priority support

## 🚀 How It Works

1. **Resume Upload**: User uploads PDF/DOCX resume
2. **Text Extraction**: PyPDF2/python-docx extracts text
3. **Skill Extraction**: Keyword matching identifies 50+ skills
4. **Embedding Generation**: Sentence-BERT creates 384-dim vector
5. **Vector Search**: Qdrant finds similar job embeddings
6. **Scoring**: Calculate compatibility (0-100%)
7. **ML Predictions**: Random Forest predicts salary
8. **Company Fit**: Weighted scoring on preferences

## 🧪 Testing

```bash
# Backend
cd backend
pytest  # (if tests are written)

# Frontend
cd frontend
npm run test  # (if tests are configured)
```

## 📦 Deployment

### Backend (Render.com / Railway.app)
1. Connect GitHub repo
2. Set environment variables
3. Deploy command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel / Netlify)
1. Connect GitHub repo
2. Build command: `npm run build`
3. Publish directory: `dist`
4. Set environment variable: `VITE_API_URL=https://your-backend.com`

## 🐛 Troubleshooting

**Backend won't start:**
- Check `.env` file has all required variables
- Verify NeonDB and Qdrant credentials
- Ensure Python 3.9+ is installed

**No job recommendations:**
- Run `python scripts/load_jobs.py` to load sample jobs
- Upload a resume first
- Check backend logs for errors

**Frontend can't connect:**
- Verify backend is running on port 8000
- Check CORS settings in `backend/app/main.py`
- Clear browser cache

## 📝 License

MIT License - Hackathon Project

## 🙏 Acknowledgments

- Sentence-Transformers for NLP embeddings
- NeonDB for serverless PostgreSQL
- Qdrant for vector search
- FastAPI for the amazing framework
