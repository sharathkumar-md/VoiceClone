import { useState, useRef } from 'react';
import { convertVoice, base64ToAudioBlob } from '../api';
import './VoiceConversion.css';

const VoiceConversion = () => {
  const [sourceAudio, setSourceAudio] = useState(null);
  const [targetVoice, setTargetVoice] = useState(null);
  const [loading, setLoading] = useState(false);
  const [convertedAudio, setConvertedAudio] = useState(null);
  const [error, setError] = useState(null);
  const audioRef = useRef(null);

  const handleSourceAudioChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('audio/')) {
      setSourceAudio(file);
      setError(null);
    } else {
      setError('Please select a valid audio file');
    }
  };

  const handleTargetVoiceChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('audio/')) {
      setTargetVoice(file);
      setError(null);
    } else {
      setError('Please select a valid audio file');
    }
  };

  const handleConvert = async () => {
    if (!sourceAudio) {
      setError('Please upload source audio');
      return;
    }
    if (!targetVoice) {
      setError('Please upload target voice sample');
      return;
    }

    setLoading(true);
    setError(null);
    setConvertedAudio(null);

    try {
      const result = await convertVoice(sourceAudio, targetVoice);

      if (result.error) {
        setError(result.error);
      } else if (result.audio_b64) {
        const audioBlob = base64ToAudioBlob(result.audio_b64);
        const audioUrl = URL.createObjectURL(audioBlob);
        setConvertedAudio(audioUrl);
      }
    } catch (err) {
      setError(err.message || 'Failed to convert voice');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (convertedAudio) {
      const a = document.createElement('a');
      a.href = convertedAudio;
      a.download = 'voice-converted.wav';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  return (
    <div className="vc-container">
      <h2>Voice Conversion</h2>
      <p className="description">
        Convert the voice in your audio to sound like another voice. Upload
        both the source audio and a sample of the target voice.
      </p>

      <div className="upload-section">
        <div className="form-group">
          <label htmlFor="source-audio">
            Source Audio (audio to convert):
          </label>
          <input
            id="source-audio"
            type="file"
            accept="audio/*"
            onChange={handleSourceAudioChange}
            disabled={loading}
          />
          {sourceAudio && (
            <div className="audio-preview">
              <p className="file-name">Selected: {sourceAudio.name}</p>
              <audio controls src={URL.createObjectURL(sourceAudio)} />
            </div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="target-voice">
            Target Voice (voice sample to mimic):
          </label>
          <input
            id="target-voice"
            type="file"
            accept="audio/*"
            onChange={handleTargetVoiceChange}
            disabled={loading}
          />
          {targetVoice && (
            <div className="audio-preview">
              <p className="file-name">Selected: {targetVoice.name}</p>
              <audio controls src={URL.createObjectURL(targetVoice)} />
            </div>
          )}
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <button
        onClick={handleConvert}
        disabled={loading || !sourceAudio || !targetVoice}
        className="convert-btn"
      >
        {loading ? 'Converting...' : 'Convert Voice'}
      </button>

      {convertedAudio && (
        <div className="audio-result">
          <h3>Converted Audio:</h3>
          <audio ref={audioRef} controls src={convertedAudio} />
          <button onClick={handleDownload} className="download-btn">
            Download Audio
          </button>
        </div>
      )}
    </div>
  );
};

export default VoiceConversion;
