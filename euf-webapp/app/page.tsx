'use client'
import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'

// 1. Criamos a Interface (o "molde") da Questão
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
  // 2. Informamos ao useState que ele guardará um array de 'Questao'
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
        console.error('Erro ao carregar:', error)
        return
      }

      if (data) {
        // Fazemos o "type casting" para garantir que o TS aceite os dados
        setQuestoes(data as Questao[])
      }
    }
    carregar()
  }, [])

  if (questoes.length === 0) {
    return (
      <div className="flex h-screen items-center justify-center font-mono text-slate-500">
        Carregando simulado de Física...
      </div>
    )
  }

  const q = questoes[index]

  const handleResposta = (letra: string) => {
    if (respondida) return
    setEscolha(letra)
    setRespondida(true)
  }

  return (
    <main className="min-h-screen bg-slate-50 p-4 md:p-8 font-sans">
      <div className="max-w-2xl mx-auto space-y-6">
        
        {/* Cabeçalho de Progresso */}
        <div className="flex justify-between items-center text-sm font-bold text-slate-400">
          <span>QUESTÃO {index + 1} DE {questoes.length}</span>
          <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-[10px] tracking-widest uppercase">
            {q.materia}
          </span>
        </div>

        {/* Área da Imagem */}
        <div className="bg-white p-4 rounded-3xl shadow-sm border border-slate-200 shadow-slate-200/50">
          <img 
            src={q.imagem_url} 
            alt={`Questão ${q.numero}`} 
            className="w-full h-auto rounded-xl select-none" 
          />
        </div>

        {/* Grid de Alternativas */}
        <div className="grid grid-cols-5 gap-3">
          {['A', 'B', 'C', 'D', 'E'].map((letra) => (
            <button
              key={letra}
              onClick={() => handleResposta(letra)}
              className={`py-5 rounded-2xl font-black text-xl border-b-4 transition-all active:scale-95
                ${!respondida ? 'bg-white border-slate-200 hover:border-blue-500 text-slate-600' : 
                  letra === q.gabarito ? 'bg-green-500 border-green-700 text-white shadow-lg shadow-green-200' : 
                  letra === escolha ? 'bg-red-500 border-red-700 text-white' : 'bg-slate-100 text-slate-300'}
              `}
            >
              {letra}
            </button>
          ))}
        </div>

        {/* Botão de Próxima */}
        {respondida && (
          <button
            onClick={() => { setIndex((index + 1) % questoes.length); setRespondida(false); setEscolha(null); }}
            className="w-full py-5 bg-slate-900 text-white rounded-2xl font-bold shadow-xl hover:bg-slate-800 transition-all flex items-center justify-center gap-3"
          >
            PRÓXIMA QUESTÃO 
            <span className="text-2xl">→</span>
          </button>
        )}
      </div>
    </main>
  )
}