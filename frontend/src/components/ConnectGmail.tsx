import { Mail, Shield, CheckCircle2 } from 'lucide-react'
import { useState } from 'react'

export default function ConnectGmail() {
    const [status, setStatus] = useState<'idle' | 'connecting' | 'connected'>('idle')

    const handleConnect = () => {
        setStatus('connecting')
        // Simulate connection delay
        setTimeout(() => {
            setStatus('connected')
            alert("Gmail Integration is in Demo Mode. \n\nIn a real deployment, this would use OAuth2 scopes: \n- https://www.googleapis.com/auth/gmail.readonly")
        }, 1500)
    }

    if (status === 'connected') {
        return (
            <div className="bg-green-50 border border-green-100 rounded-2xl p-6 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center text-green-600">
                        <CheckCircle2 className="w-6 h-6" />
                    </div>
                    <div>
                        <h3 className="font-semibold text-green-900">Gmail Connected</h3>
                        <p className="text-sm text-green-700">Scanning for subscriptions...</p>
                    </div>
                </div>
                <div className="px-4 py-2 bg-white text-green-700 text-sm font-medium rounded-lg border border-green-200 shadow-sm">
                    Active
                </div>
            </div>
        )
    }

    return (
        <div className="relative group overflow-hidden bg-white border border-gray-100 rounded-2xl shadow-sm hover:shadow-md transition-all duration-300">
            {/* Background decoration */}
            <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-red-50 rounded-full opacity-50 group-hover:scale-150 transition-transform duration-500 ease-out" />

            <div className="p-6 relative z-10">
                <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 bg-red-50 text-red-600 rounded-xl flex items-center justify-center mb-2 group-hover:bg-red-600 group-hover:text-white transition-colors duration-300">
                        <Mail className="w-6 h-6" />
                    </div>
                    <div className="flex items-center gap-1 text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">
                        <Shield className="w-3 h-3" />
                        <span>Google Verified</span>
                    </div>
                </div>

                <div className="mb-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-1">Connect Gmail</h3>
                    <p className="text-sm text-gray-500">
                        Automatically find subscriptions buried in your email application.
                    </p>
                </div>

                <button
                    onClick={handleConnect}
                    disabled={status === 'connecting'}
                    className="w-full py-3 px-4 bg-gray-900 text-white rounded-xl font-medium text-sm hover:bg-black active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-wait"
                >
                    {status === 'connecting' ? (
                        <>
                            <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            Securely Connecting...
                        </>
                    ) : (
                        <>
                            Connect Account
                        </>
                    )}
                </button>

                <p className="text-[10px] text-center text-gray-400 mt-3">
                    We only read subject lines. Your privacy is protected.
                </p>
            </div>
        </div>
    )
}
