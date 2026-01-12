import { useState } from 'react'
import FileUpload from './components/FileUpload'
import Results from './components/Results'
import ConnectGmail from './components/ConnectGmail'
import { Wallet } from 'lucide-react'

export interface Subscription {
  Description: string
  Amount: number
  Date: string
  Frequency?: string
  Risk?: string
}

export interface AnalysisResult {
  preview: Subscription[]
  status: string
  message: string
}

function App() {
  const [data, setData] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)

  return (
    <div className="min-h-screen bg-slate-50 relative selection:bg-indigo-100 selection:text-indigo-900">
      {/* Background patterns */}
      <div className="fixed inset-0 bg-grid-pattern opacity-[0.4] pointer-events-none" />
      <div className="fixed top-0 left-0 w-full h-96 bg-gradient-to-b from-indigo-50/50 to-transparent pointer-events-none" />

      <div className="relative max-w-xl mx-auto px-4 py-12">
        <header className="mb-10 text-center space-y-2">
          <div className="inline-flex items-center justify-center p-3 rounded-2xl bg-white shadow-lg shadow-indigo-100 mb-4 animate-in fade-in zoom-in duration-500">
            <Wallet className="w-8 h-8 text-indigo-600" />
          </div>
          <h1 className="text-4xl font-black text-slate-900 tracking-tight">
            Sub<span className="text-indigo-600">Detect</span>
            <span className="text-indigo-600 inline-block align-top text-xs ml-1 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100 font-bold uppercase tracking-widest">AI</span>
          </h1>
          <p className="text-slate-500 text-lg max-w-sm mx-auto">
            Intelligent subscription tracking for your bank statements.
          </p>
        </header>

        <main className="space-y-6">
          {!data && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-8 duration-700">
              <ConnectGmail />

              <div className="relative flex items-center gap-4 py-2">
                <div className="h-px bg-slate-200 flex-1" />
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Or upload manually</span>
                <div className="h-px bg-slate-200 flex-1" />
              </div>

              <FileUpload onAnalyze={(result) => setData(result)} setLoading={setLoading} loading={loading} />
            </div>
          )}

          {data && (
            <Results data={data} onReset={() => setData(null)} />
          )}
        </main>

        <footer className="mt-16 text-center">
          <p className="text-xs text-slate-400 flex items-center justify-center gap-1">
            Powered by Renaissance Algorithm Engine
          </p>
        </footer>
      </div>
    </div>
  )
}

export default App
