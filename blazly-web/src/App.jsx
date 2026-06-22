import React, { useState, useEffect } from 'react';

function App() {
  const [file, setFile] = useState(null);
  const [mode, setMode] = useState('wav2lip');
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState({ stage: 'Idle', progress: 0 });
  const [videoUrl, setVideoUrl] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleGenerate = async () => {
    if (!file) {
      alert("Please select a PDF first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("mode", mode);

    try {
      setStatus({ stage: 'Uploading...', progress: 0 });
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setJobId(data.job_id);
    } catch (error) {
      console.error(error);
      alert("Error starting job. Is the backend running?");
      setStatus({ stage: 'Idle', progress: 0 });
    }
  };

  // Poll status every 2 seconds
  useEffect(() => {
    let interval;
    if (jobId && status.stage !== 'Completed' && status.stage !== 'Error') {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`http://localhost:8000/status/${jobId}`);
          const data = await res.json();
          if (data.stage !== 'Not Found') {
            setStatus(data);
          }
          if (data.stage === 'Completed') {
            setVideoUrl(`http://localhost:8000/download/${jobId}`);
          }
        } catch (e) {
          console.error(e);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [jobId, status.stage]);

  return (
    <div className="min-h-screen bg-background text-textMain font-sans flex flex-col items-center py-12 px-4">
      <div className="w-full max-w-4xl">
        <header className="mb-10 text-center">
          <h1 className="text-5xl font-bold text-primary mb-2">Blazly AI</h1>
          <p className="text-gray-400 text-lg">Educational Video Generator</p>
        </header>

        <main className="bg-slate-800 rounded-2xl shadow-2xl p-8 border border-slate-700">
          
          {/* Upload Section */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 text-accent">1. Upload PDF Material</h2>
            <div className="border-2 border-dashed border-slate-600 rounded-xl p-8 text-center hover:bg-slate-700/50 transition cursor-pointer relative">
              <input 
                type="file" 
                accept="application/pdf"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                onChange={handleFileChange}
              />
              {file ? (
                <div className="text-primary font-medium flex items-center justify-center gap-2">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  {file.name}
                </div>
              ) : (
                <div className="text-gray-400">
                  <svg className="w-12 h-12 mx-auto mb-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                  <p>Drag and drop your PDF here, or click to browse</p>
                </div>
              )}
            </div>
          </div>

          {/* Settings Section */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 text-accent">2. Select Avatar Mode</h2>
            <div className="grid grid-cols-2 gap-4">
              <div 
                className={`p-4 rounded-xl border-2 cursor-pointer transition ${mode === 'liveportrait' ? 'border-primary bg-primary/10' : 'border-slate-700 bg-slate-800'}`}
                onClick={() => setMode('liveportrait')}
              >
                <h3 className="font-bold text-lg mb-1">Image Avatar</h3>
                <p className="text-sm text-gray-400">LivePortrait engine. High-res face, no hand gestures.</p>
              </div>
              <div 
                className={`p-4 rounded-xl border-2 cursor-pointer transition ${mode === 'wav2lip' ? 'border-primary bg-primary/10' : 'border-slate-700 bg-slate-800'}`}
                onClick={() => setMode('wav2lip')}
              >
                <div className="flex justify-between items-start">
                  <h3 className="font-bold text-lg mb-1">Template Video</h3>
                  <span className="bg-primary/20 text-primary text-xs px-2 py-1 rounded-full font-bold">NEW</span>
                </div>
                <p className="text-sm text-gray-400">Wav2Lip engine. Natural hand gestures, perfect lip sync.</p>
              </div>
            </div>
          </div>

          {/* Generate Button */}
          <div className="mb-8">
            <button 
              onClick={handleGenerate}
              disabled={!file || (jobId && status.stage !== 'Completed' && status.stage !== 'Error')}
              className="w-full bg-gradient-to-r from-primary to-accent hover:opacity-90 text-slate-900 font-bold py-4 rounded-xl text-xl shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Generate Educational Video
            </button>
          </div>

          {/* Progress Section */}
          {jobId && (
            <div className="bg-slate-900 rounded-xl p-6 border border-slate-700">
              <div className="flex justify-between items-center mb-2">
                <span className="font-medium text-gray-300">Status: <span className="text-primary font-bold">{status.stage}</span></span>
                <span className="font-bold text-accent">{status.progress}%</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-4 mb-6 overflow-hidden">
                <div 
                  className="bg-gradient-to-r from-primary to-accent h-4 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${status.progress}%` }}
                ></div>
              </div>

              {/* Video Player */}
              {status.stage === 'Completed' && videoUrl && (
                <div className="mt-6">
                  <h3 className="text-lg font-bold mb-3 text-accent flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    Final Video Ready
                  </h3>
                  <video 
                    controls 
                    className="w-full rounded-xl shadow-xl border border-slate-700"
                    src={videoUrl}
                  />
                  <div className="mt-4 flex justify-end">
                    <a 
                      href={videoUrl} 
                      download 
                      className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg font-medium transition"
                    >
                      Download Video
                    </a>
                  </div>
                </div>
              )}
            </div>
          )}

        </main>
      </div>
    </div>
  );
}

export default App;
