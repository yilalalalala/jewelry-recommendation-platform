import { FormEvent, useState } from "react";

type Recommendation = {
  sku: string;
  name: string;
  category: string;
  material: string;
  price: number;
  styles: string[];
  colors: string[];
  segment: string;
  score: number;
  explanation: { style: number; color: number; segment: number };
};

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const styleOptions = ["classic", "modern", "romantic", "bold", "bohemian", "minimalist", "vintage", "luxurious"];
const colorOptions = ["black", "white", "silver", "gold", "pink", "red", "green", "blue", "purple"];

export default function App() {
  const [style, setStyle] = useState("modern");
  const [color, setColor] = useState("black");
  const [category, setCategory] = useState("ring");
  const [results, setResults] = useState<Recommendation[]>([]);
  const [status, setStatus] = useState("Choose a profile to see transparent ranking factors.");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setStatus("Ranking the synthetic catalog…");
    try {
      const response = await fetch(`${API_URL}/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ styles: [style], colors: [color], category, limit: 6 }),
      });
      if (!response.ok) throw new Error(`API returned ${response.status}`);
      const payload = await response.json();
      setResults(payload.recommendations);
      setStatus(`${payload.recommendations.length} recommendations with explainable scores.`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "The API request failed.");
    }
  }

  return (
    <main>
      <section className="hero">
        <p className="eyebrow">EXPLAINABLE RECOMMENDATION SYSTEM</p>
        <h1>JewelRank</h1>
        <p>Deterministic ranking across style, color, and catalog segment—without scraped brands or hidden model calls.</p>
      </section>

      <form onSubmit={submit}>
        <label>Style<select value={style} onChange={(event) => setStyle(event.target.value)}>{styleOptions.map((value) => <option key={value}>{value}</option>)}</select></label>
        <label>Color<select value={color} onChange={(event) => setColor(event.target.value)}>{colorOptions.map((value) => <option key={value}>{value}</option>)}</select></label>
        <label>Category<select value={category} onChange={(event) => setCategory(event.target.value)}>{["ring", "necklace", "bracelet", "earrings"].map((value) => <option key={value}>{value}</option>)}</select></label>
        <button type="submit">Generate recommendations</button>
      </form>

      <p className="status" aria-live="polite">{status}</p>
      <section className="grid">
        {results.map((item) => (
          <article key={item.sku}>
            <div className="score">{Math.round(item.score * 100)}</div>
            <p className="eyebrow">{item.sku} · {item.segment}</p>
            <h2>{item.name}</h2>
            <p>${item.price.toLocaleString()} · {item.material}</p>
            <dl>
              <div><dt>Style</dt><dd>{Math.round(item.explanation.style * 100)}%</dd></div>
              <div><dt>Color</dt><dd>{Math.round(item.explanation.color * 100)}%</dd></div>
              <div><dt>Segment</dt><dd>{Math.round(item.explanation.segment * 100)}%</dd></div>
            </dl>
          </article>
        ))}
      </section>
    </main>
  );
}
