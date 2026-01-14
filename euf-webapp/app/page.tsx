'use client'
import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'

export default function SimuladoEUF() {
  const [questoes, setQuestoes] = useState([])
  const [index, setIndex] = useState(0)
  const [respondida, setRespondida] = useState(false)
  const [escolha, setEscolha] = useState(null)

  useEffect(() => {
    async function carregar() {
      const { data } = await supabase.from('questoes').select('*').order('numero')
      if (data) setQuestoes(data)
    }
    carregar()
  }, [])

  if (questoes.length === 0) return <div className="p-10 text-center font-mono">Carregando EUF 2023.2...</div>

  const q = questoes[index]

  const handleResposta = (letra) => {
    if (respondida) return
    setEscolha(letra)
    setRespondida(true)
  }

  return (
    <main className="min-h-screen bg-slate-50 p-4 font-sans text-slate-900">
      <div className="max-w-2xl mx-auto space-y-6">
        
        {/* Barra de Progresso */}
        <div className="flex justify-between items-center text-sm font-bold text-slate-500">
          <span>Questão {index + 1} de {questoes.length}</span>
          <span className="bg-slate-200 px-3 py-1 rounded-full">{q.materia}</span>
        </div>

        {/* Imagem da Questão */}
        <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-200">
          <img src={q.imagem_url} alt="Questão" className="w-full h-auto rounded-lg" />
        </div>

        {/* Alternativas A-E */}
        <div className="grid grid-cols-5 gap-3">
          {['A', 'B', 'C', 'D', 'E'].map((letra) => (
            <button
              key={letra}
              onClick={() => handleResposta(letra)}
              className={`py-4 rounded-xl font-black text-xl border-b-4 transition-all
                ${!respondida ? 'bg-white border-slate-200 hover:border-blue-500' : 
                  letra === q.gabarito ? 'bg-green-500 border-green-700 text-white' : 
                  letra === escolha ? 'bg-red-500 border-red-700 text-white' : 'bg-slate-100 text-slate-300'}
              `}
            >
              {letra}
            </button>
          ))}
        </div>

        {/* Botão de Navegação */}
        {respondida && (
          <button
            onClick={() => { setIndex((index + 1) % questoes.length); setRespondida(false); setEscolha(null); }}
            className="w-full py-4 bg-slate-900 text-white rounded-2xl font-bold shadow-lg hover:scale-[1.02] transition-transform"
          >
            Próxima Questão →
          </button>
        )}
      </div>
    </main>
  )
}