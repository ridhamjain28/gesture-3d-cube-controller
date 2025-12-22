# 🚀 GitHub Setup Instructions

Follow these steps to push your project to GitHub:

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `gesture-3d-cube-controller`
3. Description: `Control a colorful 3D cube using hand gestures - no keyboard, no mouse!`
4. Keep it **Public**
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

## Step 2: Connect and Push

After creating the repository, run these commands in PowerShell:

```powershell
cd "D:\Img projecy"

# Add your GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/gesture-3d-cube-controller.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Enter Credentials

When prompted:
- **Username**: Your GitHub username
- **Password**: Use a Personal Access Token (not your password)

### How to get a Personal Access Token:
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name it: `gesture-cube-controller`
4. Select scopes: Check `repo` (full control of private repositories)
5. Click "Generate token"
6. **COPY THE TOKEN** (you won't see it again!)
7. Use this token as your password when pushing

## Step 4: Verify

Visit: `https://github.com/YOUR_USERNAME/gesture-3d-cube-controller`

You should see all your files uploaded! 🎉

## Updating README

Don't forget to update the README.md:
1. Replace `YOUR_USERNAME` with your actual GitHub username
2. Replace `[Your Name]` with your name
3. Add your email if you want

Then commit and push:
```powershell
git add README.md
git commit -m "Update README with personal info"
git push
```

## Making it Look Professional

### Add a demo GIF/video
1. Record a short video of the cube in action
2. Upload to GitHub repository
3. Add to README with: `![Demo](demo.gif)`

### Add topics/tags
Go to your repo → Click ⚙️ next to "About" → Add topics:
- `hand-gesture`
- `computer-vision`
- `opencv`
- `mediapipe`
- `3d-graphics`
- `python`

---

**Need help? Ask me anything!** 😊
