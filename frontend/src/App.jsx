import React, { useState, useEffect } from 'react';
import { 
  ScanLine, 
  LayoutDashboard, 
  UploadCloud, 
  UserCheck, 
  FileText, 
  MapPin, 
  History, 
  LogOut, 
  ShieldCheck 
} from 'lucide-react';

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [user, setUser] = useState({ name: 'Rajesh Sharma', role: 'officer' });

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">
      {/* Top Government Navigation */}
      <header className="bg-sky-950 text-white border-b-4 border-amber-500 shadow-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentPage('dashboard')}>
            <div className="w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center text-amber-500 border border-white/20">
              <ScanLine className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold">LANDLENS <span className="text-amber-500">AI</span></span>
                <span className="text-xs bg-amber-600 px-2 py-0.5 rounded-full font-bold uppercase">SIH26018</span>
              </div>
              <p className="text-xs text-slate-300 hidden md:block">From Legacy Land Records to Verified Digital Intelligence</p>
            </div>
          </div>

          <nav className="flex space-x-1">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
              { id: 'upload', label: 'Upload & Process', icon: UploadCloud },
              { id: 'verification', label: 'Verification Studio', icon: UserCheck },
              { id: 'records', label: 'Land Records', icon: FileText },
              { id: 'gis', label: 'Cadastral GIS', icon: MapPin },
              { id: 'audit', label: 'Audit Trail', icon: History }
            ].map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentPage(item.id)}
                  className={`px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-1.5 transition ${
                    currentPage === item.id ? 'bg-sky-900 text-amber-400' : 'hover:bg-sky-900/60'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 bg-sky-900 px-3 py-1 rounded-full border border-sky-800 text-xs">
              <div className="w-2 h-2 rounded-full bg-emerald-400"></div>
              <span>{user.name}</span>
              <span className="bg-sky-800 text-amber-400 px-1.5 py-0.2 rounded uppercase text-[10px] font-mono">{user.role}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6">
        <div className="bg-white p-8 rounded-xl border border-slate-200 shadow-sm text-center">
          <h2 className="text-2xl font-bold text-slate-900 mb-2">LandLens AI Enterprise Portal</h2>
          <p className="text-slate-600 text-sm max-w-2xl mx-auto mb-6">
            For standard zero-dependency hackathon execution, the production single-page application is served directly by the FastAPI backend at <a href="http://localhost:8000" className="text-sky-700 font-bold underline">http://localhost:8000</a>.
          </p>
          <div className="inline-flex items-center space-x-2 px-4 py-2 bg-slate-100 rounded-lg text-xs font-mono text-slate-700">
            <span>Status: Connected to FastAPI Backend on port 8000</span>
          </div>
        </div>
      </main>
    </div>
  );
}
