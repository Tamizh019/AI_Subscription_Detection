import { useState } from 'react'
import type { AnalysisResult } from '../App'
import { AlertTriangle, ArrowLeft } from 'lucide-react'

interface ResultsProps {
    data: AnalysisResult
    onReset: () => void
}

export default function Results({ data, onReset }: ResultsProps) {
    const [viewMode, setViewMode] = useState<'verified' | 'patterns'>('verified')

    const allSubscriptions = data.subscriptions || []
    const verifiedSubscriptions = allSubscriptions.filter(sub => sub.PatternType === 'subscription')
    const spendingPatterns = allSubscriptions.filter(sub => sub.PatternType === 'pattern')
    const matches = viewMode === 'verified' ? verifiedSubscriptions : spendingPatterns

    const sortedSubs = [...matches].sort((a, b) => {
        if (a.Risk === 'High' && b.Risk !== 'High') return -1
        if (b.Risk === 'High' && a.Risk !== 'High') return 1
        return b.Amount - a.Amount
    })

    const currentTotal = sortedSubs.reduce((sum, sub) => sum + sub.Amount, 0)

    const getRiskColor = (risk: string) => {
        if (risk === 'High') return 'bg-red-50 text-red-700 border-red-200'
        if (risk === 'Medium') return 'bg-yellow-50 text-yellow-700 border-yellow-200'
        return 'bg-green-50 text-green-700 border-green-200'
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between pb-4 border-b border-gray-200">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
                    <p className="text-sm text-gray-600 mt-1">
                        Found {verifiedSubscriptions.length} subscriptions
                    </p>
                </div>
                <button
                    onClick={onReset}
                    className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Back
                </button>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 border-b border-gray-200">
                <button
                    onClick={() => setViewMode('verified')}
                    className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
                        viewMode === 'verified'
                            ? 'border-gray-900 text-gray-900'
                            : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                >
                    Subscriptions ({verifiedSubscriptions.length})
                </button>
                <button
                    onClick={() => setViewMode('patterns')}
                    className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
                        viewMode === 'patterns'
                            ? 'border-gray-900 text-gray-900'
                            : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                >
                    Patterns ({spendingPatterns.length})
                </button>
            </div>

            {/* Total */}
            <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">
                    {viewMode === 'verified' ? 'Monthly Total' : 'Pattern Total'}
                </p>
                <p className="text-3xl font-bold text-gray-900">
                    ₹{currentTotal.toLocaleString('en-IN')}
                </p>
            </div>

            {/* List */}
            <div className="space-y-3">
                {sortedSubs.map((sub, idx) => (
                    <div
                        key={idx}
                        className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
                    >
                        <div className="flex items-start justify-between">
                            <div className="flex-1">
                                <h4 className="font-semibold text-gray-900">{sub.UnifiedName}</h4>
                                <div className="flex items-center gap-3 mt-1 text-sm text-gray-600">
                                    <span>{sub.Category}</span>
                                    <span>•</span>
                                    <span>{sub.Frequency}</span>
                                </div>
                            </div>
                            <div className="text-right">
                                <p className="font-bold text-gray-900">₹{sub.Amount.toLocaleString('en-IN')}</p>
                                <span className={`inline-block mt-1 text-xs px-2 py-1 rounded border ${getRiskColor(sub.Risk)}`}>
                                    {sub.Risk}
                                </span>
                            </div>
                        </div>
                    </div>
                ))}

                {sortedSubs.length === 0 && (
                    <div className="text-center py-12 border border-dashed border-gray-200 rounded-lg">
                        <AlertTriangle className="w-8 h-8 text-gray-400 mx-auto mb-3" />
                        <p className="text-gray-600">
                            {viewMode === 'verified' ? 'No subscriptions found' : 'No patterns detected'}
                        </p>
                    </div>
                )}
            </div>
        </div>
    )
}
