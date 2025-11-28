# Quick Start Guide

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/Divyansh-K-Art/Project-Orpheus.git
cd project-orpheus
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the server**
```bash
python web_ui.py
```

4. **Access the application**
Open your browser and navigate to: `http://localhost:8000`

## First Generation

1. Click "Enter Studio" on the landing page
2. In the prompt box, type: "Epic cinematic orchestral music"
3. Click "Generate Track"
4. Wait for the AI to create a plan (~5-10 seconds)
5. Review the generated plan (structure, key, BPM, instruments)
6. Click "Generate Audio" or edit the plan first
7. Wait for generation to complete (~30-60 seconds)
8. Play and download your music!

## Troubleshooting

**Server won't start:**
- Ensure Python 3.10+ is installed
- Check all dependencies are installed
- Verify port 8000 is not in use

**Generation fails:**
- Check you have enough RAM (4GB minimum)
- Verify model downloads successfully
- Check console for error messages

**UI looks broken:**
- Hard refresh browser (Ctrl+Shift+R)
- Clear browser cache
- Check static files are served correctly

## Getting Help

- Check the [README.md](README.md)
- Review [deployment_guide.md](deployment_guide.md)
- Open an issue on GitHub
