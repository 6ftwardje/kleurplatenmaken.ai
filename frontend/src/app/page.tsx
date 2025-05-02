'use client';

import { useState } from 'react';
import Image from 'next/image';

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium');
  const [isConverting, setIsConverting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [debugInfo, setDebugInfo] = useState<string[]>([]);

  const addDebugInfo = (info: string) => {
    console.log(info);
    setDebugInfo(prev => [...prev, `${new Date().toISOString()}: ${info}`]);
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      addDebugInfo(`Selected file: ${file.name} (${file.type}, ${file.size} bytes)`);
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
        addDebugInfo('File preview generated');
      };
      reader.readAsDataURL(file);
      setError(null);
    }
  };

  const handleConvert = async () => {
    if (!selectedFile) {
      setError('Please select an image first');
      return;
    }

    setIsConverting(true);
    setError(null);
    setDebugInfo([]);

    try {
      addDebugInfo('Starting conversion process');
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('difficulty', difficulty);
      addDebugInfo(`Added file and difficulty (${difficulty}) to form data`);

      addDebugInfo('Sending request to backend...');
      const response = await fetch('http://localhost:8000/convert', {
        method: 'POST',
        body: formData,
      });

      addDebugInfo(`Received response with status: ${response.status}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        addDebugInfo(`Error response from server: ${errorText}`);
        throw new Error(`Failed to convert image: ${errorText}`);
      }

      addDebugInfo('Converting response to blob');
      const blob = await response.blob();
      addDebugInfo(`Received blob of size: ${blob.size} bytes`);

      const url = window.URL.createObjectURL(blob);
      addDebugInfo('Created object URL for download');

      const a = document.createElement('a');
      a.href = url;
      a.download = `coloring_page_${difficulty}.png`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      addDebugInfo('Download initiated');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      addDebugInfo(`Error occurred: ${errorMessage}`);
      setError(errorMessage);
    } finally {
      setIsConverting(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">
          Kleurplatenmaken.ai 🎨
        </h1>
        
        <div className="bg-white rounded-lg shadow-xl p-6 mb-8">
          <div className="space-y-6">
            {/* File Upload */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                Choose an image
              </label>
              {preview && (
                <div className="mt-4">
                  <Image
                    src={preview}
                    alt="Preview"
                    width={300}
                    height={300}
                    className="mx-auto rounded-lg"
                  />
                </div>
              )}
            </div>

            {/* Difficulty Selection */}
            <div className="flex justify-center space-x-4">
              {(['easy', 'medium', 'hard'] as const).map((level) => (
                <button
                  key={level}
                  onClick={() => {
                    setDifficulty(level);
                    addDebugInfo(`Difficulty set to: ${level}`);
                  }}
                  className={`px-4 py-2 rounded-md ${
                    difficulty === level
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </button>
              ))}
            </div>

            {/* Convert Button */}
            <div className="text-center">
              <button
                onClick={handleConvert}
                disabled={!selectedFile || isConverting}
                className={`px-6 py-3 rounded-md text-white font-medium ${
                  !selectedFile || isConverting
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                {isConverting ? 'Converting...' : 'Convert to Coloring Page'}
              </button>
            </div>

            {/* Error Message */}
            {error && (
              <div className="text-red-600 text-center mt-4">
                {error}
              </div>
            )}

            {/* Debug Information */}
            {debugInfo.length > 0 && (
              <div className="mt-4 p-4 bg-gray-100 rounded-lg">
                <h3 className="text-lg font-semibold mb-2">Debug Information:</h3>
                <div className="text-sm font-mono">
                  {debugInfo.map((info, index) => (
                    <div key={index} className="mb-1">{info}</div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Features Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold mb-2">Easy</h3>
            <p className="text-gray-600">Perfect for young children, with simple lines and basic shapes.</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold mb-2">Medium</h3>
            <p className="text-gray-600">Balanced complexity for older children and beginners.</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold mb-2">Hard</h3>
            <p className="text-gray-600">Detailed designs for experienced colorists and adults.</p>
          </div>
        </div>
      </div>
    </main>
  );
}
