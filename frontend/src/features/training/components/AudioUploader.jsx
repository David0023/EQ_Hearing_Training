import { useEffect, useState } from "react";

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
    <section>
      <h2>EQ Training</h2>
      <p>Select Audio file and play.</p>

      <label htmlFor="audio-upload">
        Select Audio File
      </label>
      <input
        id="audio-upload"
        type="file"
        accept="audio/*"
        onChange={handleFileChange}
      />

      {file && (
        <div>
          <h3>Selected File</h3>
          <p>{file.name}</p>
          <p>
            {(file.size / (1024 * 1024)).toFixed(2)} MB
          </p>

          {audioUrl && (
            <audio
              key={audioUrl}
              controls
              src={audioUrl}
              onError={() => {console.error('Failed to play audio')}}
            >
              Browser does not support audio play.
            </audio>
          )}

          <div>
            <button type="button" onClick={handleRemove}>
              Remove File
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
