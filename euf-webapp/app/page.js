"use client";
import { useState, useEffect } from "react";
import { supabase } from "../lib/supabase"; // Usando caminho relativo para evitar erro de alias

export default function SimuladoEUF() {
  const [questoes, setQuestoes] = useState([]);
  const [index, setIndex] = useState(0);
  const [respondida, setRespondida] = useState(false);
  const [escolha, setEscolha] = useState(null);

  useEffect(() => {
    async function carregar() {
      const { data, error } = await supabase
        .from("questoes")
        .select("*")
        .order("numero", { ascending: true });
      
      if (data) setQuestoes(data);
      if (error) console.error("Erro:", error.message);
    }
    carregar();
  }, []);

  if (questoes.length === 0) return <div className="p-10 text-center font-mono">Carregando banco de dados...</div>;

  const q = questoes[index];

  const verificar = (letra) => {
    if (respondida) return;
    setEscolha(letra);
    setRespondida(true);
  };

  return (
    <main className="min-h-screen bg-slate-50 p-4 font-sans text-slate-900">
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="flex justify-between items-center text-sm font-bold text-slate-500">
          <span>Questão {index + 1} de {questoes.length}</span>
          <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full uppercase text-[10px]">{q.materia}</span>
        </div>

        <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-200">
          <img src={q.imagem_url} alt="Questão" className="w-full h-auto rounded-lg" />
        </div>

        <div className="grid grid-cols-5 gap-3">
          {["A", "B", "C", "D", "E"].map((letra) => (
            <button
              key={letra}
              onClick={() => verificar(letra)}
              className={`py-4 rounded-xl font-black text-xl border-b-4 transition-all
                ${!respondida ? "bg-white border-slate-200 hover:border-blue-500" : 
                  letra === q.gabarito ? "bg-green-500 border-green-700 text-white" : 
                  letra === escolha ? "bg-red-500 border-red-700 text-white" : "bg-slate-100 text-slate-300"}
              `}
            >
              {letra}
            </button>
          ))}
        </div>

        {respondida && (
          <button
            onClick={() => { setIndex((index + 1) % questoes.length); setRespondida(false); setEscolha(null); }}
            className="w-full py-4 bg-slate-900 text-white rounded-2xl font-bold shadow-lg"
          >
            Próxima Questão →
          </button>
        )}
      </div>
    </main>
  );
}