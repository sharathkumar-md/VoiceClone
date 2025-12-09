# RunPod Serverless Deployment Guide

## Quick Setup (5 minutes)

### Step 1: Create New Serverless Endpoint

1. Go to https://www.runpod.io/console/serverless
2. Click **"+ New Endpoint"**
3. Click **"New Template"** button

### Step 2: Configure Template

Fill in the following settings:

**Template Configuration:**
- **Template Name**: `chatterbox-tts`
- **Container Image**: `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04`
- **Container Disk**: `20 GB` (minimum for models)
- **Docker Command**: Leave empty (uses default)

**Advanced Settings:**
- Expose HTTP Ports: Leave at `8000` (default)
- Expose TCP Ports: Leave empty

### Step 3: Environment Variables

Click **"Environment Variables"** and add:

```
GOOGLE_API_KEY=AIzaSyAH4hSlaRt9dYzfkBAyuDTYeqdgWJF5N-E
GEMINI_MODEL=gemini-2.5-flash
```

### Step 4: Configure GitHub Integration

**IMPORTANT: This is the key step!**

1. Scroll to **"Source Code"** section
2. Select **"GitHub Repository"**
3. Click **"Connect GitHub Account"** (if not already connected)
4. Enter Repository Details:
   - **Repository URL**: `https://github.com/sharathkumar-md/VoiceClone`
   - **Branch**: `main`
   - **Python Version**: `3.10`

5. **Handler Configuration**:
   - **Handler Path**: `runpod_handler.handler`
   - **Build Commands** (Optional, for extra dependencies):
     ```bash
     pip install --upgrade pip
     pip install -r requirements.txt
     ```

### Step 5: GPU Selection

Choose your GPU tier:
- **Recommended**: `NVIDIA A100 (40GB)` or `NVIDIA RTX 4090 (24GB)`
- **Budget Option**: `NVIDIA RTX 3090 (24GB)`

**Scaling Settings:**
- **Min Workers**: `0` (saves money when idle)
- **Max Workers**: `3` (handles concurrent requests)
- **Idle Timeout**: `10 seconds`
- **Max Wait Time**: `600 seconds` (10 min for first model load)

### Step 6: Deploy

1. Click **"Create Template"**
2. Wait for template to be created (~30 seconds)
3. Click **"Deploy"** on the template
4. Name your endpoint: `chatterbox-tts-production`
5. Click **"Deploy Endpoint"**

### Step 7: Get Your Endpoint ID

After deployment completes (~2-5 minutes):
1. You'll see your endpoint in the dashboard
2. Copy the **Endpoint ID** (looks like: `abc123xyz456`)
3. Update your `.env` file:
   ```
   RUNPOD_ENDPOINT_ID=your-new-endpoint-id-here
   ```

---

## Testing Your Deployment

Run the test script:

```powershell
cd chatterbox-runpod
python deploy_runpod.py
```

Expected output:
```
Testing endpoint: abc123xyz456
Sending test request...
✅ Success! Endpoint is working.
Audio data received: 12345 characters
```

---

## Cost Estimation

**GPU Pricing (approximate):**
- A100 40GB: ~$1.89/hour (~$0.0005/second)
- RTX 4090: ~$0.89/hour (~$0.0002/second)
- RTX 3090: ~$0.49/hour (~$0.0001/second)

**Your Use Case (15-chunk story):**
- Expected runtime: 15-30 minutes on A100
- Cost: ~$0.50 - $1.00 per story
- vs Local: 6-7 hours per story

**With Min Workers = 0:**
- You only pay when actively generating
- Worker spins down after 10 seconds of inactivity
- First request after idle takes ~30-60 seconds (model loading)

---

## Troubleshooting

### Issue: "Handler not found"
- Verify handler path is exactly: `runpod_handler.handler`
- Check that `runpod_handler.py` exists in repository root

### Issue: "Module not found" errors
- Add build commands in template configuration
- Verify `requirements.txt` is in repository root

### Issue: Timeout on first request
- Increase **Max Wait Time** to 600 seconds (10 min)
- First request loads models (~30-60 seconds on A100)
- Subsequent requests are fast (~1-2 min per chunk)

### Issue: CUDA out of memory
- Use A100 40GB or RTX 4090 24GB
- Smaller GPUs (3090/3080) might run out of VRAM

### Issue: 400 Bad Request
- Your old endpoint `oxwicer9fveosp` is not configured
- Create a NEW endpoint following steps above
- Update `.env` with new endpoint ID

---

## Monitoring

View logs in real-time:
1. Go to RunPod dashboard
2. Click on your endpoint
3. Click **"Logs"** tab
4. Watch model loading and inference progress

---

## Next Steps

Once deployed, you can:

1. **Use the Gradio UI** with RunPod backend:
   ```python
   # In src/ui/gradio_app.py, add:
   USE_RUNPOD = True
   ```

2. **Run full story narration**:
   ```powershell
   python src/story_narrator/cli.py --use-runpod
   ```

3. **Monitor costs** in RunPod dashboard

---

## GitHub Updates

To update your deployed code:
1. Push changes to GitHub: `git push`
2. RunPod will automatically rebuild on next cold start
3. Or manually rebuild in RunPod dashboard

---

**Need Help?** Check RunPod docs: https://docs.runpod.io/serverless/workers/overview
