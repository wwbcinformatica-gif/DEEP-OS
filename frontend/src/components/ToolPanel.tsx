import { useState } from 'react';

type ToolResponse = {
  status: string;
  stdout?: string;
  stderr?: string;
  returncode?: number;
};

export default function ToolPanel() {
  const [path, setPath] = useState('');
  const [content, setContent] = useState('');
  const [output, setOutput] = useState<ToolResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const callApi = async (endpoint: string, body: object) => {
    setLoading(true);
    try {
      const res = await fetch(`/api${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      setOutput(data);
    } catch (e) {
      setOutput({ status: 'error', stderr: `${e}` });
    } finally {
      setLoading(false);
    }
  };

  const handleRead = () => callApi('/tool/read', { path, root: true });
  const handleWrite = () => callApi('/tool/write', { path, content, root: true });
  const handleBash = () => callApi('/tool/bash', { command: content, workdir: '' });

  return (
    <div className="p-4 bg-gray-800 text-gray-100 rounded-lg shadow-lg">
      <h2 className="text-xl font-semibold mb-4">Tool Panel</h2>
      <div className="mb-3">
        <label className="block mb-1">Caminho</label>
        <input
          type="text"
          className="w-full px-2 py-1 rounded bg-gray-700 text-white focus:outline-none"
          value={path}
          onChange={(e) => setPath(e.target.value)}
          placeholder="ex.: data/interactions.db"
        />
      </div>
      <div className="mb-3">
        <label className="block mb-1">Conteúdo / Comando</label>
        <textarea
          className="w-full h-24 px-2 py-1 rounded bg-gray-700 text-white focus:outline-none"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="texto para gravar ou comando bash"
        />
      </div>
      <div className="flex space-x-2 mb-4">
        <button
          className="flex-1 px-3 py-1 bg-blue-600 hover:bg-blue-500 rounded transition"
          onClick={handleRead}
          disabled={loading}
        >
          Read
        </button>
        <button
          className="flex-1 px-3 py-1 bg-green-600 hover:bg-green-500 rounded transition"
          onClick={handleWrite}
          disabled={loading}
        >
          Write
        </button>
        <button
          className="flex-1 px-3 py-1 bg-purple-600 hover:bg-purple-500 rounded transition"
          onClick={handleBash}
          disabled={loading}
        >
          Bash
        </button>
      </div>
      {output && (
        <div className="mt-3 p-2 bg-gray-900 rounded text-sm overflow-auto max-h-48">
          <pre className="whitespace-pre-wrap">
            {output.status === 'ok'
              ? `STDOUT:\n${output.stdout}\nSTDERR:\n${output.stderr}`
              : `Erro:\n${output.stderr || 'Desconhecido'}`}
          </pre>
        </div>
      )}
    </div>
  );
}
