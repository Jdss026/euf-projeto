'use client'
import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'

// 1. Definimos o "formato" da questão para o TypeScript
interface Questao {
  id: string;
  numero: number;
  materia: string;
  imagem_url: string;
  gabarito: string;
}

export default function SimuladoEUF() {
  // 2. Avisamos ao useState que ele receberá uma lista de Objetos do tipo Questao
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
      
      if (data) {
        setQuestoes(data as Questao[])
      }
    }
    carregar()
  }, [])

  if (questoes.length === 0) {
    return <div className="p-10 text-center font-mono">Carregando questões do EUF...</div>
  }

  const q = questoes[index]

  const handleResposta = (letra: string) => {
    if (respondida) return
    setEscolha(letra)
    setRespondida(true)
  }

  return (
    <main className="min-h-screen bg-slate-50 p-4 font-sans text-slate-900">
      <div className="max-w-2xl mx-auto space-y-6">
        
        {/* Progresso */}
        <div className="flex justify-between items-center text-sm font-bold text-slate-500">
          <span>Questão {index + 1} de {questoes.length}</span>
          <span className="bg-slate-200 px-3 py-1 rounded-full uppercase text-[10px] tracking-widest">
            {q.materia}
          </span>
        </div>

        {/* Imagem da Questão */}
        <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-200 flex justify-center">
          <img 
            src={q.imagem_url} 
            alt={`Questão ${q.numero}`} 
            className="max-w-full h-auto rounded-lg" 
          />
        </div>

        {/* Alternativas */}
        <div className="grid grid-cols-5 gap-3">
          {['A', 'B', 'C', 'D', 'E'].map((letra) => (
            <button
              key={letra}
              onClick={() => handleResposta(letra)}
              className={`py-4 rounded-xl font-black text-xl border-b-4 transition-all
                ${!respondida ? 'bg-white border-slate-200 hover:border-blue-500 hover:bg-blue-50' : 
                  letra === q.gabarito ? 'bg-green-500 border-green-700 text-white shadow-green-200 shadow-lg' : 
                  letra === escolha ? 'bg-red-500 border-red-700 text-white' : 'bg-slate-100 text-slate-300'}
              `}
            >
              {letra}
            </button>
          ))}
        </div>

        {/* Botão Próxima */}
        {respondida && (
          <button
            onClick={() => { setIndex((index + 1) % questoes.length); setRespondida(false); setEscolha(null); }}
            className="w-full py-4 bg-slate-900 text-white rounded-2xl font-bold shadow-lg hover:scale-[1.01] active:scale-95 transition-all"
          >
            Próxima Questão →
          </button>
        )}
      </div>
    </main>
  )
}