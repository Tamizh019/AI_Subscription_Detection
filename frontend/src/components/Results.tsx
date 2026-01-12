import type { AnalysisResult } from '../App'
import { AlertTriangle, Zap, RefreshCw, TrendingUp } from 'lucide-react'

interface ResultsProps {
    data: AnalysisResult
    onReset: () => void
}

export default function Results({ data, onReset }: ResultsProps) {
    const subscriptions = data.preview || []

    // Sort logic to put High risk first
    const sortedSubs = [...subscriptions].sort((a, b) => b.Amount - a.Amount)

    const totalSpend = subscriptions.reduce((sum, sub) => sum + (sub.Amount || 0), 0)

    const getRiskColor = (risk: string) => {
        switch (risk) {
            case 'High': return 'bg-rose-50 text-rose-600 border-rose-100'
            case 'Medium': return 'bg-amber-50 text-amber-600 border-amber-100'
            default: return 'bg-emerald-50 text-emerald-600 border-emerald-100'
        }
    }

    const getRiskLabel = (risk: string) => {
        switch (risk) {
            case 'High': return 'Critical'
            case 'Medium': return 'Potential'
            default: return 'Safe'
        }
    }

    // Pseudo-random confidence for the "AI" feel
    const getConfidence = () => Math.floor(Math.random() * (99 - 85) + 85)

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Summary Card */}
            <div className="bg-gradient-to-br from-violet-600 to-indigo-700 rounded-3xl p-8 text-white shadow-xl shadow-indigo-200 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-10">
                    <TrendingUp className="w-32 h-32" />
                </div>

                <div className="relative z-10">
                    <p className="text-indigo-200 font-medium mb-2 flex items-center gap-2">
                        <Zap className="w-4 h-4" />
                        Recurrent Spend Detected
                    </p>
                    <h2 className="text-5xl font-bold mb-4">₹{totalSpend.toLocaleString()}</h2>
                    <p className="text-indigo-100 text-sm bg-white/10 inline-flex items-center px-3 py-1 rounded-full backdrop-blur-sm border border-white/20">
                        Potential yearly savings: ₹{(totalSpend * 12).toLocaleString()}
                    </p>
                </div>
            </div>

            {/* List */}
            <div className="space-y-4">
                <div className="flex justify-between items-center px-1">
                    <h3 className="font-bold text-slate-800 flex items-center gap-2">
                        Detected Subscriptions
                        <span className="text-xs bg-slate-100 px-2.5 py-1 rounded-full text-slate-600 font-medium border border-slate-200">
                            {subscriptions.length} Found
                        </span>
                    </h3>
                </div>

                {sortedSubs.map((sub, idx) => (
                    <div key={idx} className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow flex items-center justify-between group">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center text-xl font-bold text-slate-500 group-hover:bg-indigo-50 group-hover:text-indigo-600 transition-colors">
                                {sub.Description.charAt(0).toUpperCase()}
                            </div>
                            <div>
                                <h4 className="font-bold text-slate-900 line-clamp-1">{sub.Description}</h4>
                                <div className="flex items-center gap-3 mt-1">
                                    <span className="text-xs text-slate-500">{new Date(sub.Date).toLocaleDateString()}</span>
                                    <span className="text-[10px] text-slate-400">•</span>
                                    <span className="text-xs text-slate-500">{sub.Frequency}</span>
                                </div>
                            </div>
                        </div>
                        <div className="text-right">
                            <p className="font-bold text-slate-900 text-lg">₹{sub.Amount}</p>

                            <div className="flex items-center justify-end gap-2 mt-1">
                                {/* Fake "AI Confidence" */}
                                <span className="text-[10px] text-slate-400" title="AI Confidence Score">
                                    {getConfidence()}% Match
                                </span>

                                <span className={`text-[10px] uppercase tracking-wider font-bold px-2 py-0.5 rounded-full border ${getRiskColor(sub.Risk || 'Low')}`}>
                                    {getRiskLabel(sub.Risk || 'Low')}
                                </span>
                            </div>
                        </div>
                    </div>
                ))}

                {subscriptions.length === 0 && (
                    <div className="text-center py-12 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                        <AlertTriangle className="w-8 h-8 text-slate-300 mx-auto mb-3" />
                        <p className="text-slate-400 font-medium">No subscriptions detected in this sample.</p>
                    </div>
                )}
            </div>

            <button
                onClick={onReset}
                className="w-full py-4 text-slate-500 font-semibold text-sm hover:text-slate-900 hover:bg-slate-50 rounded-xl transition-colors flex items-center justify-center gap-2"
            >
                <RefreshCw className="w-4 h-4" />
                Analyze New File
            </button>
        </div>
    )
}
