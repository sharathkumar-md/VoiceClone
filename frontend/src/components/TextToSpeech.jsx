import { useState, useRef } from 'react';
import { generateTTS, base64ToAudioBlob } from '../api';
import './TextToSpeech.css';

const TextToSpeech = () => {
  const [text, setText] = useState('');
  const [refAudio, setRefAudio] = useState(null);
  const [exaggeration, setExaggeration] = useState(0.5);
  const [temperature, setTemperature] = useState(0.8);
  const [cfgWeight, setCfgWeight] = useState(0.5);
  const [loading, setLoading] = useState(false);
  const [generatedAudio, setGeneratedAudio] = useState(null);
  const [error, setError] = useState(null);
  const audioRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('audio/')) {
      setRefAudio(file);
      setError(null);
    } else {
      setError('Please select a valid audio file');
    }
  };

  const handleGenerate = async () => {
    if (!text.trim()) {
      setError('Please enter some text');
      return;
    }
    if (!refAudio) {
      setError('Please upload a reference audio file');
      return;
    }

    setLoading(true);
    setError(null);
    setGeneratedAudio(null);

    try {
      const result = await generateTTS(text, refAudio, {
        exaggeration,
        temperature,
        cfg_weight: cfgWeight,
      });

      if (result.error) {
        setError(result.error);
      } else if (result.audio_b64) {
        const audioBlob = base64ToAudioBlob(result.audio_b64);
        const audioUrl = URL.createObjectURL(audioBlob);
        setGeneratedAudio(audioUrl);
      }
    } catch (err) {
      setError(err.message || 'Failed to generate speech');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (generatedAudio) {
      const a = document.createElement('a');
      a.href = generatedAudio;
      a.download = 'generated-speech.wav';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  return (
    <div className="tts-container">
      <h2>Text-to-Speech</h2>
      <p className="description">
        Convert text to speech using a reference voice. Upload an audio sample
        and enter your text.
      </p>

      <div className="form-group">
        <label htmlFor="text-input">Text to synthesize:</label>
        <textarea
          id="text-input"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter the text you want to convert to speech..."
          rows={4}
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="ref-audio">Reference Audio (voice sample):</label>
        <input
          id="ref-audio"
          type="file"
          accept="audio/*"
          onChange={handleFileChange}
          disabled={loading}
        />
        {refAudio && <p className="file-name">Selected: {refAudio.name}</p>}
      </div>

      <div className="controls-grid">
        <div className="form-group">
          <label htmlFor="exaggeration">
            Exaggeration: {exaggeration.toFixed(2)}
          </label>
          <input
            id="exaggeration"
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={exaggeration}
            onChange={(e) => setExaggeration(parseFloat(e.target.value))}
            disabled={loading}
          />
          <p className="help-text">
            Higher values make speech more expressive and dramatic
          </p>
        </div>

        <div className="form-group">
          <label htmlFor="temperature">
            Temperature: {temperature.toFixed(2)}
          </label>
          <input
            id="temperature"
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={temperature}
            onChange={(e) => setTemperature(parseFloat(e.target.value))}
            disabled={loading}
          />
          <p className="help-text">Controls randomness in generation</p>
        </div>

        <div className="form-group">
          <label htmlFor="cfg-weight">
            CFG Weight: {cfgWeight.toFixed(2)}
          </label>
          <input
            id="cfg-weight"
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={cfgWeight}
            onChange={(e) => setCfgWeight(parseFloat(e.target.value))}
            disabled={loading}
          />
          <p className="help-text">
            Lower values (~0.3) for faster speech, higher for slower pacing
          </p>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <button
        onClick={handleGenerate}
        disabled={loading || !text.trim() || !refAudio}
        className="generate-btn"
      >
        {loading ? 'Generating...' : 'Generate Speech'}
      </button>

      {generatedAudio && (
        <div className="audio-result">
          <h3>Generated Audio:</h3>
          <audio ref={audioRef} controls src={generatedAudio} />
          <button onClick={handleDownload} className="download-btn">
            Download Audio
          </button>
        </div>
      )}
    </div>
  );
};

export default TextToSpeech;
