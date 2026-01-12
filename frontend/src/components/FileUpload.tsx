import { useState } from 'react'
import { UploadCloud, FileText, AlertCircle, ShieldCheck } from 'lucide-react'

interface FileUploadProps {
    onAnalyze: (data: any) => void
    setLoading: (loading: boolean) => void
    loading: boolean
}

export default function FileUpload({ onAnalyze, setLoading, loading }: FileUploadProps) {
    const [error, setError] = useState<string | null>(null)

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return
        processFile(file)
    }

    const processFile = async (file: File) => {
        setLoading(true)
        setError(null)

        const formData = new FormData()
        formData.append('file', file)

        try {
            const response = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                body: formData,
            })

            const result = await response.json()

            if (!response.ok) {
                throw new Error(result.error || 'Failed to analyze')
            }

            onAnalyze(result)
        } catch (err: any) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100 text-center relative overflow-hidden group">
            {/* Decoration */}
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-indigo-600" />

            <div className="mb-8">
                <div className="w-20 h-20 bg-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                    <UploadCloud className="w-10 h-10 text-blue-600" />
                </div>
                <h3 className="text-xl font-bold text-slate-900">Upload Bank Statement</h3>
                <p className="text-slate-500 text-sm mt-2 max-w-[260px] mx-auto">
                    Upload your CSV statement to detect hidden recurring payments.
                </p>
            </div>

            <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
            />

            <label
                htmlFor="file-upload"
                className={`flex items-center justify-center gap-2 w-full py-4 px-6 rounded-xl font-semibold transition-all cursor-pointer border-2 border-transparent ${loading
                    ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg shadow-blue-200 active:scale-[0.98]'
                    }`}
            >
                {loading ? (
                    <>
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        <span>Analyzing Transaction Patterns...</span>
                    </>
                ) : (
                    <>
                        <FileText className="w-5 h-5" />
                        <span>Select CSV File</span>
                    </>
                )}
            </label>

            {error && (
                <div className="mt-6 flex items-start gap-3 text-left bg-red-50 p-4 rounded-xl border border-red-100">
                    <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                    <p className="text-red-600 text-sm font-medium">{error}</p>
                </div>
            )}

            <div className="mt-8 pt-6 border-t border-slate-100">
                <div className="flex items-center justify-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-widest mb-4">
                    <ShieldCheck className="w-4 h-4" />
                    <span>Bank Level Security</span>
                </div>
                <p className="text-xs text-slate-400 max-w-xs mx-auto leading-relaxed">
                    Your data is processed locally in memory and is never stored on our servers.
                </p>
            </div>
        </div>
    )
}
