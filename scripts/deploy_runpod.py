"""
RunPod Serverless Deployment Script

This script will help you deploy your Chatterbox TTS to RunPod Serverless.

INSTRUCTIONS:
1. Go to https://www.runpod.io/console/serverless
2. Click "New Endpoint"
3. Choose "Serverless" (not "Pod")
4. Under "Select a Template", choose "Python" or "PyTorch"
5. Configure:
   - Name: chatterbox-tts
   - GitHub Repository: https://github.com/sharathkumar-md/VoiceClone
   - Branch: main
   - Handler: runpod_handler.handler
   - Docker Image: runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel
6. Set Environment Variables:
   - GOOGLE_API_KEY: (your key)
   - GEMINI_MODEL: gemini-2.5-flash
7. Choose GPU: A100 40GB or 4090 24GB
8. Set scaling:
   - Min Workers: 0 (to save money)
   - Max Workers: 3
   - Idle Timeout: 10 seconds
9. Click "Deploy"

After deployment, you'll get a new ENDPOINT_ID. Update your .env file with it.
"""

import runpod
import os
from dotenv import load_dotenv

load_dotenv()

def test_endpoint():
    """Test the deployed endpoint"""
    api_key = os.getenv("RUNPOD_API_KEY")
    endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")
    
    if not api_key or not endpoint_id:
        print("❌ Please set RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID in .env file")
        return
    
    print(f"Testing endpoint: {endpoint_id}")
    
    runpod.api_key = api_key
    endpoint = runpod.Endpoint(endpoint_id)
    
    # Test with simple TTS request
    test_input = {
        "task": "tts",
        "text": "Hello, this is a test of the Chatterbox TTS system.",
        "reference_audio": None,  # Will use default voice
        "exaggeration": 0.3,
        "temperature": 0.6,
        "cfg_weight": 0.3,
        "max_new_tokens": 250
    }
    
    print("Sending test request...")
    try:
        result = endpoint.run_sync(test_input, timeout=300)
        print("✅ Success! Endpoint is working.")
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        if isinstance(result, dict) and 'audio_base64' in result:
            print(f"Audio data received: {len(result['audio_base64'])} characters")
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print(__doc__)
    print("\n" + "="*60)
    print("Once you've created the endpoint, run this script to test it:")
    print("python deploy_runpod.py")
    print("="*60 + "\n")
    
    # Check if endpoint exists
    api_key = os.getenv("RUNPOD_API_KEY")
    endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")
    
    if api_key and endpoint_id:
        response = input(f"\nFound endpoint ID: {endpoint_id}\nTest it now? (y/n): ")
        if response.lower() == 'y':
            test_endpoint()
    else:
        print("\n⚠️  Set RUNPOD_ENDPOINT_ID in .env after creating the endpoint")
