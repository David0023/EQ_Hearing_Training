import { useEffect, useState } from "react";
import "./AudioUploader.css";

export function AudioUploader() {
  const [file, setFile] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);

  useEffect(() => {
    if (!file) {
      setAudioUrl(null);
      return;
    }

    const url = URL.createObjectURL(file);
    setAudioUrl(url);

    // Clean up code that runs after the page is closed.
    return () => {
      URL.revokeObjectURL(url);
    };
  }, [file]);

  function handleFileChange(event) {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) return;

    if (!selectedFile.type.startsWith("audio/")) {
      alert("Select Audio File");
      event.target.value = "";
      return;
    }

    setFile(selectedFile);
  }

  function handleRemove() {
    setFile(null);
  }

  return (
    <section className="audio-uploader">
      <h2 className="audio-uploader__title">EQ Training</h2>
      <p>Select Audio file and play.</p>

      <label className="audio-uploader__label" htmlFor="audio-upload">
        Select Audio File
      </label>
      <input
        className="audio-uploader__input"
        id="audio-upload"
        type="file"
        accept="audio/*"
        onChange={handleFileChange}
      />

      {file && (
        <div className="audio-uploader__file">
          <h3 className="audio-uploader__file-title">Selected File</h3>
          <p className="audio-uploader__file-name">{file.name}</p>
          <p className="audio-uploader__file-size">
            {(file.size / (1024 * 1024)).toFixed(2)} MB
          </p>

          {audioUrl && (
            <audio
              className="audio-uploader__audio"
              key={audioUrl}
              controls
              src={audioUrl}
              onError={() => {console.error('Failed to play audio')}}
            >
              Browser does not support audio play.
            </audio>
          )}

          <div className="audio-uploader__actions">
            <button className="audio-uploader__remove" type="button" onClick={handleRemove}>
              Remove File
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
