"use client";
import { useState, useEffect } from "react";
import { supabase } from "@/lib/supabase";

export default function SimuladoEUF() {
  const [questoes, setQuestoes] = useState([]);
  const [index, setIndex] = useState(0);
  const [respondida, setRespondida] = useState(false);
  const [escolha, setEscolha] = useState(null);

  // Carrega as 80 questões do Supabase ao iniciar
  useEffect(() => {
    async function carregarQuestoes() {
      const { data, error } = await supabase
        .from("questoes")
        .select("*")
        .order("numero", { ascending: true });

      if (error) {
        console.error("Erro ao carregar banco:", error.message);
      } else {
        setQuestoes(data);
      }
    }
    carregarQuestoes();
  }, []);

  if (questoes.length === 0) {
    return (
      <div className="flex h-screen items-center justify-center font-mono text-slate-500">
        Carregando simulado de Física...
      </div>
    );
  }

  const q = questoes[index];

  const verificarResposta = (letra) => {
    if (respondida) return;
    setEscolha(letra);
    setRespondida(true);
  };

  const proximaQuestao = () => {
    setIndex((prev) => (prev + 1) % questoes.length);
    setRespondida(false);
    setEscolha(null);
  };

  return (
    <main className="min-h-screen p-4 md:p-8">
      <div className="max-w-2xl mx-auto space-y-6">
        
        {/* Progresso e Matéria */}
        <div className="flex justify-between items-end border-b pb-4 border-slate-200">
          <div>
            <h1 className="text-xl font-black text-slate-800 uppercase tracking-tight">EUF 2023/2</h1>
            <p className="text-blue-600 font-bold text-xs uppercase tracking-widest">{q.materia}</p>
          </div>
          <div className="text-right">
            <span className="text-xs font-bold text-slate-400 block mb-1">PROCESSO: {index + 1} / {questoes.length}</span>
            <div className="w-32 h-1.5 bg-slate-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-blue-600 transition-all duration-500" 
                style={{ width: `${((index + 1) / questoes.length) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Imagem da Questão */}
        <div className="bg-white p-4 rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100">
          <img 
            src={q.imagem_url} 
            alt={`Questão ${q.numero}`} 
            className="w-full h-auto rounded-xl pointer-events-none select-none" 
          />
        </div>

        {/* Alternativas A-E */}
        <div className="grid grid-cols-5 gap-3">
          {["A", "B", "C", "D", "E"].map((letra) => (
            <button
              key={letra}
              onClick={() => verificarResposta(letra)}
              className={`py-5 rounded-2xl font-black text-xl border-b-4 transition-all active:scale-95
                ${!respondida ? "bg-white border-slate-200 hover:border-blue-500 text-slate-700" : 
                  letra === q.gabarito ? "bg-green-500 border-green-700 text-white" : 
                  letra === escolha ? "bg-red-500 border-red-700 text-white" : "bg-slate-100 text-slate-300"}
              `}
            >
              {letra}
            </button>
          ))}
        </div>

        {/* Navegação */}
        {respondida && (
          <div className="pt-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <button
              onClick={proximaQuestao}
              className="w-full py-5 bg-slate-900 text-white rounded-2xl font-bold text-lg shadow-xl hover:bg-black transition-all flex items-center justify-center gap-3"
            >
              PRÓXIMA QUESTÃO 
              <span className="text-2xl">→</span>
            </button>
          </div>
        )}
      </div>
    </main>
  );
}