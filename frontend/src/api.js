// API service for communicating with the backend

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Helper function to convert file to base64
export const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      // Remove the data:audio/wav;base64, prefix
      const base64 = reader.result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = (error) => reject(error);
  });
};

// Text-to-Speech API call
export const generateTTS = async (text, refAudioFile, options = {}) => {
  try {
    const refAudioB64 = await fileToBase64(refAudioFile);

    const response = await fetch(`${API_BASE_URL}/tts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        task: 'tts',
        text,
        ref_audio_b64: refAudioB64,
        exaggeration: options.exaggeration || 0.5,
        temperature: options.temperature || 0.8,
        cfg_weight: options.cfg_weight || 0.5,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('TTS API Error:', error);
    throw error;
  }
};

// Voice Conversion API call
export const convertVoice = async (sourceAudioFile, targetVoiceFile) => {
  try {
    const sourceAudioB64 = await fileToBase64(sourceAudioFile);
    const targetVoiceB64 = await fileToBase64(targetVoiceFile);

    const response = await fetch(`${API_BASE_URL}/vc`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        task: 'vc',
        source_audio_b64: sourceAudioB64,
        target_voice_b64: targetVoiceB64,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Voice Conversion API Error:', error);
    throw error;
  }
};

// Convert base64 audio to blob for playback
export const base64ToAudioBlob = (base64Audio) => {
  const binaryString = atob(base64Audio);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return new Blob([bytes], { type: 'audio/wav' });
};
