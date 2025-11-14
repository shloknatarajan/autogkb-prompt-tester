import { useState, useEffect } from 'react';
import { BenchmarkResult, BenchmarkResultListItem } from '../types';

const API_BASE = 'http://localhost:8000';

export function useBenchmarks() {
  const [benchmarkResults, setBenchmarkResults] = useState<
    BenchmarkResultListItem[]
  >([]);
  const [selectedResult, setSelectedResult] = useState<BenchmarkResult | null>(
    null,
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // Load benchmark results list on mount
  useEffect(() => {
    loadBenchmarkResults();
  }, []);

  const loadBenchmarkResults = async () => {
    try {
      const response = await fetch(`${API_BASE}/benchmark-results`);
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const data = await response.json();
      setBenchmarkResults(data.files);
    } catch (err) {
      console.error('Failed to load benchmark results:', err);
      setError('Failed to load benchmark results: ' + (err as Error).message);
    }
  };

  const loadBenchmarkDetail = async (filename: string) => {
    try {
      setLoading(true);
      const response = await fetch(
        `${API_BASE}/benchmark-results/${filename}`,
      );
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const data = await response.json();
      setSelectedResult(data);
    } catch (err) {
      console.error('Failed to load benchmark detail:', err);
      setError('Failed to load benchmark detail: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const runBenchmark = async (text: string, pmcid: string) => {
    try {
      setLoading(true);
      setError('');

      const response = await fetch(`${API_BASE}/run-benchmarks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          pmcid,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || response.statusText);
      }

      const data = await response.json();

      // Reload the benchmark results list
      await loadBenchmarkResults();

      // Set the new result as selected
      setSelectedResult(data.results);

      return data.results;
    } catch (err) {
      const errorMessage = (err as Error).message;
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    benchmarkResults,
    selectedResult,
    loading,
    error,
    loadBenchmarkResults,
    loadBenchmarkDetail,
    runBenchmark,
    setSelectedResult,
  };
}
