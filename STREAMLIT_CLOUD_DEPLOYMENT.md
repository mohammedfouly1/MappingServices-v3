# Streamlit Cloud Deployment Guide

## Main File Path for Streamlit Cloud

### ⚠️ IMPORTANT: Use the `restructure-project` branch!

**Main file path:** `ui/app.py`

---

## Quick Setup - Streamlit Cloud Community

### 1. **Go to Streamlit Cloud**
Visit: https://share.streamlit.io/

### 2. **Deploy New App**
Click "New app" button

### 3. **Fill in Configuration**

| Field | Value |
|-------|-------|
| **Repository** | `mohammedfouly1/MappingServices-v3` |
| **Branch** | `restructure-project` |
| **Main file path** | `ui/app.py` |
| **App URL** (optional) | Choose your custom subdomain |

### 4. **Advanced Settings (Click "Advanced settings...")**

#### Python version:
```
3.11
```

#### Secrets (REQUIRED):
Click "Advanced settings" → "Secrets" and paste:

```toml
# OpenAI API Key
OPENAI_API_KEY = "sk-your-openai-api-key-here"

# OpenRouter API Key (optional, if using OpenRouter)
OPENROUTER_API_KEY = "sk-or-your-openrouter-api-key-here"

# Settings
[settings]
provider = "OpenAI"
model = "gpt-4o-mini"
temperature = 0.2
top_p = 0.9
threshold = 80
max_tokens = 16000
max_batch_size = 300
wait_between_batches = 120
max_concurrent_batches = 10
use_compact_json = true
abbreviate_keys = true
```

**⚠️ IMPORTANT:** Replace `sk-your-openai-api-key-here` with your actual OpenAI API key!

### 5. **Deploy**
Click "Deploy!" button

### 6. **Wait for Deployment**
- Initial deployment takes 2-5 minutes
- You'll see build logs in real-time
- App will automatically open when ready

---

## File Structure (What Streamlit Cloud Needs)

```
MappingServices-v3/
├── ui/
│   └── app.py                 ← Main file (Streamlit app)
├── requirements.txt           ← Python dependencies (in root)
├── .streamlit/
│   └── config.toml            ← Streamlit config (optional)
├── packages.txt               ← System packages (optional)
└── runtime.txt                ← Python version (optional)
```

---

## Current Files Status

### ✅ Already Included
- `ui/app.py` - Main Streamlit application
- `requirements.txt` - All Python dependencies

### 📝 Optional Files (You Can Add)

#### 1. `.streamlit/config.toml` (Theme customization)

Create this file in your repository:

```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 50
enableCORS = false
enableXsrfProtection = true
```

#### 2. `packages.txt` (System dependencies)

Only needed if you need system-level packages. For this project, **NOT REQUIRED**.

#### 3. `runtime.txt` (Specify Python version)

```
python-3.11.7
```

---

## Environment Variables vs Secrets

### ✅ Use Secrets (Recommended)
- API keys
- Sensitive configuration
- Access via `st.secrets["OPENAI_API_KEY"]`

### ❌ Don't Use Environment Variables
- Less secure on Streamlit Cloud
- Harder to manage

---

## Deployment Checklist

### Before Deploying:
- [ ] Repository is public OR you've connected your GitHub account
- [ ] You're on `restructure-project` branch
- [ ] `ui/app.py` exists in the branch
- [ ] `requirements.txt` is in root directory
- [ ] You have your OpenAI API key ready

### During Deployment:
- [ ] Repository: `mohammedfouly1/MappingServices-v3`
- [ ] Branch: `restructure-project`
- [ ] Main file path: `ui/app.py`
- [ ] Secrets configured with API key
- [ ] Python version: 3.11

### After Deployment:
- [ ] App loads successfully
- [ ] Can upload Excel files
- [ ] Can select mapping type
- [ ] API calls work (check you have credits!)
- [ ] Results display correctly

---

## Troubleshooting Common Issues

### Issue 1: "File not found: ui/app.py"
**Solution:** Make sure you selected the `restructure-project` branch, not `main`

### Issue 2: "ModuleNotFoundError"
**Solution:**
- Check `requirements.txt` includes all dependencies
- Make sure `requirements.txt` is in the root directory
- Verify dependencies are spelled correctly

### Issue 3: "API key not found"
**Solution:**
- Check Secrets configuration in Streamlit Cloud settings
- Make sure the key is named `OPENAI_API_KEY` (exact match)
- Verify the key format: `sk-...`

### Issue 4: "Quota exceeded" error
**Solution:**
- Add credits to your OpenAI account
- OR switch to OpenRouter in the app sidebar
- OR use a different API key

### Issue 5: App takes too long to load
**Solution:**
- First load is slower (2-5 minutes)
- Subsequent loads are faster (30-60 seconds)
- Check if there are any import errors in logs

---

## Managing Your Deployed App

### View Logs:
1. Click on your app in Streamlit Cloud dashboard
2. Click "Manage app" (⚙️ icon)
3. View logs in real-time

### Update App:
1. Push changes to GitHub (`restructure-project` branch)
2. App will auto-deploy (takes 1-2 minutes)
3. Or manually click "Reboot app"

### Update Secrets:
1. Go to Streamlit Cloud dashboard
2. Click on your app
3. Click "⚙️ Settings"
4. Edit Secrets
5. Save (app will reboot automatically)

### Delete App:
1. Go to Streamlit Cloud dashboard
2. Click on your app
3. Click "⚙️ Settings"
4. Scroll to "Delete app"

---

## Cost Considerations

### Streamlit Cloud Community (FREE):
- ✅ Unlimited public apps
- ✅ 1 private app
- ✅ Auto-sleep after inactivity
- ✅ Community support
- ❌ Limited resources (1 GB RAM)
- ❌ No custom domains

### OpenAI API Costs:
- You pay for OpenAI API usage separately
- Costs depend on model and token usage
- Monitor at: https://platform.openai.com/usage

**Recommended for this app:**
- Use `gpt-4o-mini` (cheapest, 4M TPM)
- Or `gpt-3.5-turbo` (if available on your account)
- Monitor token usage in the app

---

## Alternative: Deploy from Main Branch

If you want to use the `main` branch instead:

**Main file path:** `streamlit_app.py`

However, this lacks all the recent improvements. **Recommended to use `restructure-project` branch instead.**

---

## Example Deployment Flow

```bash
# Step 1: Ensure code is pushed
cd "G:\My Drive\MappingServices-v2"
git status
git push origin restructure-project

# Step 2: Go to Streamlit Cloud
# https://share.streamlit.io/

# Step 3: Click "New app"

# Step 4: Fill in:
Repository: mohammedfouly1/MappingServices-v3
Branch: restructure-project
Main file path: ui/app.py

# Step 5: Advanced settings → Secrets → Paste:
OPENAI_API_KEY = "sk-your-actual-key"

# Step 6: Click "Deploy!"

# Step 7: Wait 2-5 minutes

# Step 8: App is live! 🎉
```

---

## Testing Before Deployment

### Test Locally First:
```bash
cd "G:\My Drive\MappingServices-v2"
git checkout restructure-project
streamlit run ui/app.py
```

### Check:
- [ ] App loads without errors
- [ ] All tabs work
- [ ] Can upload Excel
- [ ] API calls work (if you have credits)
- [ ] Results display correctly

---

## Post-Deployment Configuration

### 1. Share Your App
Get the URL from Streamlit Cloud (e.g., `https://your-app.streamlit.app`)

### 2. Monitor Usage
- Check Streamlit Cloud metrics
- Monitor OpenAI API usage
- Watch for errors in logs

### 3. Update Documentation
Update your GitHub README with:
- Link to live app
- Usage instructions
- Screenshots

---

## Summary

**Main file path for Streamlit Cloud:** `ui/app.py`

**Required:**
1. Repository: `mohammedfouly1/MappingServices-v3`
2. Branch: `restructure-project`
3. Main file: `ui/app.py`
4. Secrets: OpenAI API key

**That's it!** Your app will be live at `https://[your-app-name].streamlit.app` 🚀

---

## Quick Reference Card

```
┌─────────────────────────────────────────┐
│  STREAMLIT CLOUD DEPLOYMENT CARD        │
├─────────────────────────────────────────┤
│ Repository: mohammedfouly1/MappingServices-v3
│ Branch: restructure-project             │
│ Main file: ui/app.py                    │
│ Python: 3.11                            │
│ Secrets: OPENAI_API_KEY                 │
└─────────────────────────────────────────┘
```

Copy this card and keep it handy! 📋
