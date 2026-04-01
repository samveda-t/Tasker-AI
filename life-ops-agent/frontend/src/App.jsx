import { useMemo, useState } from "react";
import axios from "axios";

import InputBox from "./components/InputBox.jsx";
import ResultCard from "./components/ResultCard.jsx";

export default function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const apiBase = useMemo(() => {
    if (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_BASE_URL) {
      return import.meta.env.VITE_API_BASE_URL;
    }
    return "http://127.0.0.1:8000";
  }, []);

  const handleSubmit = async () => {
    setError("");
    setResult(null);

    if (!query.trim()) {
      setError("Please enter a question or travel request.");
      return;
    }

    try {
      setLoading(true);
      const response = await axios.get(`${apiBase}/decision`, {
        params: { query: query.trim() },
      });
      setResult(response.data);
    } catch (err) {
      let message =
        err?.response?.data?.detail || err?.message || "Something went wrong.";
      if (message === "Not Found") {
        message =
          "API endpoint not found. Ensure the backend is running and VITE_API_BASE_URL is correct.";
      }
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 px-4 py-10">
      <div className="mx-auto w-full max-w-3xl">
        <header className="text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">
            Life Ops Agent
          </p>
          <h1 className="mt-3 text-3xl font-semibold text-slate-900 sm:text-5xl">
            Ask a decision question in seconds
          </h1>
          <p className="mt-4 text-base text-slate-600 sm:text-lg">
            Describe what you’re trying to decide. We’ll pull live data and
            recommend the best next step.
          </p>
        </header>

        <section className="mt-10 rounded-2xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur">
          <InputBox
            label="Your question"
            placeholder="Should I travel from Indiranagar to MG Road today?"
            value={query}
            onChange={setQuery}
          />

          <div className="mt-6 flex flex-col items-stretch gap-3 sm:flex-row sm:items-center">
            <button
              type="button"
              onClick={handleSubmit}
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white shadow-sm transition-all duration-300 hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {loading ? (
                <>
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
                  Loading...
                </>
              ) : (
                "Get Recommendation"
              )}
            </button>
            <p className="text-xs text-slate-500">
              Uses live weather, ETA, AQI, and news when relevant.
            </p>
          </div>

          <div className="mt-4 min-h-[48px]">
            {error ? (
              <p className="rounded-xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm text-rose-600 transition-all duration-300">
                {error}
              </p>
            ) : null}
          </div>
        </section>

        <ResultCard
          action={result?.decision?.action}
          reason={result?.decision?.reason}
          confidence={result?.decision?.confidence}
          link={result?.plan?.link}
          risk={result?.risk}
          news={result?.context?.news}
          destination={result?.interpretation?.destination}
        />
      </div>
    </div>
  );
}
