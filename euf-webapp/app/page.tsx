'use client'
import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'

// 1. Definimos o "Contrato" (Interface) para o TypeScript
// Isso resolve o erro de 'any' vs 'never'
interface Questao {
  id: string;
  numero: number;
  materia: string;
  imagem_url: string;
  gabarito: string;
  ano?: string;
  periodo?: string;
}

export default function SimuladoEUF() {
  // 2. Definimos explicitamente que o estado guardará um Array de Objetos do tipo Questao
  const [questoes, setQuestoes] = useState<Questao[]>([])
  const [index, setIndex] = useState(0)
  const [respondida, setRespondida] = useState(false)
  const [escolha, setEscolha] = useState<string | null>(null)

  useEffect(() => {
    async function carregar() {
      const { data, error } = await supabase
        .from('questoes')
        .select('*')
        .order('numero', { ascending: true })
      
      if (error) {
        console.error('Erro ao buscar dados:', error)
        return
      }

      if (data) {
        // 3. O 'as Questao[]' é o que garante que o TS aceite os dados do banco
        setQuestoes(data as Questao[])
      }
    }
    carregar()
  }, [])

  // Proteção para o estado inicial de carregamento
  if (questoes.length === 0) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50 font-mono text-slate-500">
        Carregando simulado...
      </div>
    )
  }

  const q = questoes[index]

  const handleResposta = (letra: string) => {
    if (respondida) return
    setEscolha(letra)
    setRespondida(true)
  }

  const proximaQuestao = () => {
    setIndex((prev) => (prev + 1) % questoes.length)
    setRespondida(false)
    setEscolha(null)
  }

  return (
    <main className="min-h-screen bg-slate-50 p-4 md:p-8 font-sans antialiased text-slate-900">
      <div className="max-w-2xl mx-auto space-y-6">
        
        {/* Header e Progresso */}
        <div className="flex justify-between items-center text-sm font-bold text-slate-400">
          <div className="flex flex-col">
            <span className="text-xs uppercase tracking-tighter">Simulado EUF</span>
            <span className="text-slate-800 text-lg uppercase font-black">Questão {index + 1} de {questoes.length}</span>
          </div>
          <span className="bg-blue-600 text-white px-3 py-1 rounded-lg text-[10px] tracking-widest uppercase">
            {q.materia}
          </span>
        </div>

        {/* Card do Enunciado (Imagem) */}
        <div className="bg-white p-4 rounded-3xl shadow-sm border border-slate-200 overflow-hidden">
          <img 
            src={q.imagem_url} 
            alt={`Questão ${q.numero}`} 
            className="w-full h-auto rounded-xl select-none pointer-events-none" 
          />
        </div>

        {/* Grid de Alternativas */}
        <div className="grid grid-cols-5 gap-3">
          {['A', 'B', 'C', 'D', 'E'].map((letra) => (
            <button
              key={letra}
              onClick={() => handleResposta(letra)}
              className={`py-5 rounded-2xl font-black text-xl border-b-4 transition-all active:scale-95
                ${!respondida ? 'bg-white border-slate-200 hover:border-blue-500 text-slate-700' : 
                  letra === q.gabarito ? 'bg-green-500 border-green-700 text-white shadow-lg' : 
                  letra === escolha ? 'bg-red-500 border-red-700 text-white' : 'bg-slate-100 text-slate-300'}
              `}
            >
              {letra}
            </button>
          ))}
        </div>

        {/* Feedback e Navegação */}
        {respondida && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
             <div className={`p-4 rounded-2xl text-center font-bold text-sm ${escolha === q.gabarito ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {escolha === q.gabarito ? "Excelente! Você acertou." : `A resposta correta é a letra ${q.gabarito}.`}
             </div>
             
             <button
              onClick={proximaQuestao}
              className="w-full py-5 bg-slate-900 text-white rounded-2xl font-bold shadow-xl hover:bg-black transition-all flex items-center justify-center gap-3"
            >
              PRÓXIMA QUESTÃO 
              <span className="text-2xl">→</span>
            </button>
          </div>
        )}
      </div>
    </main>
  )
}