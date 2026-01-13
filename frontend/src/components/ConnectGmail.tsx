import { Mail, Shield } from 'lucide-react'

export default function ConnectGmail() {
    return (
        <div className="bg-white p-6 rounded-2xl shadow-lg shadow-indigo-100/50 border border-slate-100 hover:shadow-xl transition-shadow duration-300">
            <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-indigo-50 flex items-center justify-center flex-shrink-0">
                    <Mail className="w-6 h-6 text-indigo-600" />
                </div>
                <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                        <h3 className="font-bold text-slate-900">Connect Gmail</h3>
                        <div className="flex items-center gap-1 text-emerald-600 text-xs font-semibold">
                            <Shield className="w-3 h-3" />
                            <span>Google Verified</span>
                        </div>
                    </div>
                    <p className="text-sm text-slate-600 mb-4">
                        Automatically find subscriptions buried in your email application.
                    </p>
                    <button className="w-full py-2.5 px-4 bg-slate-900 text-white rounded-xl font-semibold hover:bg-slate-800 transition-colors shadow-sm">
                        Connect Account
                    </button>
                    <p className="text-xs text-slate-500 mt-3 text-center">
                        We only read subject lines. Your privacy is protected.
                    </p>
                </div>
            </div>
        </div>
    )
}
