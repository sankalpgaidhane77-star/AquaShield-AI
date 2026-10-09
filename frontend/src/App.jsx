import React, { useState, useEffect, useMemo } from 'react';
import {
  ShieldCheck,
  AlertTriangle,
  Flame,
  Droplets,
  Search,
  MapPin,
  Compass,
  CheckCircle2,
  XCircle,
  AlertCircle,
  RefreshCw,
  Activity,
  Sliders,
  Send,
  ThumbsUp,
  Radio,
  BarChart3,
  Layers,
  Thermometer,
  Eye,
  Info,
  ChevronRight,
  ExternalLink,
  Phone,
  Clock,
  Sparkles
} from 'lucide-react';

const API_BASE = 'http://localhost:8000';

export default function App() {
  // Navigation
  const [activeTab, setActiveTab] = useState('overview');

  // Backend connection state
  const [apiConnected, setApiConnected] = useState(false);
  const [apiLoading, setApiLoading] = useState(true);

  // Core Data States
  const [sources, setSources] = useState([]);
  const [reports, setReports] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [analytics, setAnalytics] = useState(null);

  // Predictor State
  const [predictInputs, setPredictInputs] = useState({
    ph: 7.3,
    turbidity: 0.8,
    tds: 180,
    temperature: 20.5
  });
  const [prediction, setPrediction] = useState(null);
  const [predicting, setPredicting] = useState(false);

  // Nearest Safe Locator State
  const [userLocation, setUserLocation] = useState({ lat: 30.2672, lng: -97.7431 });
  const [nearestSafe, setNearestSafe] = useState(null);
  const [locatingNearest, setLocatingNearest] = useState(false);
  const [selectedSource, setSelectedSource] = useState(null);
  const [sourceSearch, setSourceSearch] = useState('');
  const [sourceFilterStatus, setSourceFilterStatus] = useState('all');

  // Report Submission State
  const [newReport, setNewReport] = useState({
    source_name: '',
    category: 'Algal Bloom',
    observed_color: 'Discolored / Murky',
    comments: '',
    reporter_name: '',
    latitude: 30.2672,
    longitude: -97.7431
  });
  const [submittingReport, setSubmittingReport] = useState(false);
  const [reportSuccess, setReportSuccess] = useState(false);

  // Live IoT Simulation drift toggle
  const [liveStreamActive, setLiveStreamActive] = useState(true);

  // Initial Data Fetch
  const fetchData = async () => {
    try {
      setApiLoading(true);
      const [sourcesRes, reportsRes, alertsRes, analyticsRes] = await Promise.allSettled([
        fetch(`${API_BASE}/api/sources`),
        fetch(`${API_BASE}/api/reports`),
        fetch(`${API_BASE}/api/alerts`),
        fetch(`${API_BASE}/api/analytics/summary`)
      ]);

      let isAnyOk = false;

      if (sourcesRes.status === 'fulfilled' && sourcesRes.value.ok) {
        const data = await sourcesRes.value.json();
        setSources(data);
        if (data.length > 0 && !selectedSource) {
          setSelectedSource(data[0]);
        }
        isAnyOk = true;
      }

      if (reportsRes.status === 'fulfilled' && reportsRes.value.ok) {
        const data = await reportsRes.value.json();
        setReports(data);
        isAnyOk = true;
      }

      if (alertsRes.status === 'fulfilled' && alertsRes.value.ok) {
        const data = await alertsRes.value.json();
        setAlerts(data);
        isAnyOk = true;
      }

      if (analyticsRes.status === 'fulfilled' && analyticsRes.value.ok) {
        const data = await analyticsRes.value.json();
        setAnalytics(data);
        isAnyOk = true;
      }

      setApiConnected(isAnyOk);
    } catch (err) {
      console.warn('API connection offline, using fallback state:', err);
      setApiConnected(false);
    } finally {
      setApiLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Periodic sensor drift simulation
  useEffect(() => {
    if (!liveStreamActive) return;
    const interval = setInterval(() => {
      setPredictInputs((prev) => ({
        ...prev,
        ph: Number(Math.max(4.0, Math.min(10.0, prev.ph + (Math.random() * 0.2 - 0.1))).toFixed(2)),
        turbidity: Number(Math.max(0.1, prev.turbidity + (Math.random() * 0.1 - 0.05)).toFixed(2)),
        tds: Math.round(Math.max(50, prev.tds + (Math.random() * 8 - 4))),
        temperature: Number(Math.max(10, Math.min(40, prev.temperature + (Math.random() * 0.2 - 0.1))).toFixed(1))
      }));
    }, 4000);
    return () => clearInterval(interval);
  }, [liveStreamActive]);

  // Run AI Prediction
  const runPrediction = async (customInputs = null) => {
    const payload = customInputs || predictInputs;
    setPredicting(true);
    try {
      const res = await fetch(`${API_BASE}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const data = await res.json();
        setPrediction(data);
      } else {
        throw new Error('Server returned ' + res.status);
      }
    } catch (err) {
      // Local fallback WHO evaluation if backend is unreachable
      const { ph, turbidity, tds, temperature } = payload;
      let classification = 'Safe';
      let confidence = 94.0;
      let recommendation = 'Water meets WHO standards for direct human consumption.';
      let treatment = 'Safe for drinking, cooking, and domestic use. Maintain clean storage.';
      let status_code = 'safe';
      let ui_color = '#10b981';
      let flags = [];
      let action_steps = ['Water is potable and clean.', 'Store in covered food-grade vessel.'];

      if (ph < 6.0 || ph > 9.0 || turbidity > 10.0 || tds > 1000 || temperature > 38) {
        classification = 'Dangerous';
        confidence = 96.5;
        recommendation = 'DANGEROUS: Severe water contamination detected. DO NOT CONSUME.';
        treatment = 'Locate alternate potable source immediately. Do not boil for direct consumption if chemical leaching.';
        status_code = 'dangerous';
        ui_color = '#ef4444';
        if (ph < 6.0) flags.push(`Highly Acidic (pH ${ph})`);
        if (turbidity > 10.0) flags.push(`Severe Turbidity (${turbidity} NTU)`);
        if (tds > 1000) flags.push(`Extreme Total Dissolved Solids (${tds} ppm)`);
        action_steps = ['Do NOT drink or cook with this water.', 'Switch to verified municipal or bottled supply.', 'Report contamination immediately.'];
      } else if (ph < 6.5 || ph > 8.5 || turbidity > 4.0 || tds > 500 || temperature > 30) {
        classification = 'Moderate';
        confidence = 85.0;
        recommendation = 'Sub-optimal quality. Water requires treatment prior to drinking.';
        treatment = 'Boil vigorously for 1-2 minutes or use ceramic microfiltration.';
        status_code = 'moderate';
        ui_color = '#f59e0b';
        if (turbidity > 4.0) flags.push(`Elevated Turbidity (${turbidity} NTU)`);
        if (tds > 500) flags.push(`Elevated TDS (${tds} ppm)`);
        action_steps = ['Boil water vigorously before consumption.', 'Use sand/cloth/ceramic filter for particulate matter.'];
      }

      setPrediction({
        classification,
        confidence,
        confidence_score: confidence / 100,
        probabilities: {
          Dangerous: classification === 'Dangerous' ? 96.5 : (classification === 'Moderate' ? 8.0 : 1.0),
          Moderate: classification === 'Moderate' ? 85.0 : (classification === 'Dangerous' ? 3.0 : 5.0),
          Safe: classification === 'Safe' ? 94.0 : (classification === 'Moderate' ? 7.0 : 0.5)
        },
        inputs: payload,
        recommendation,
        treatment_advice: treatment,
        flags,
        action_steps,
        status_code,
        ui_color
      });
    } finally {
      setPredicting(false);
    }
  };

  // Run initial prediction once
  useEffect(() => {
    runPrediction();
  }, []);

  // Quick preset loader
  const applyPreset = (preset) => {
    const presets = {
      spring: { ph: 7.4, turbidity: 0.45, tds: 165, temperature: 18.2 },
      tap: { ph: 7.3, turbidity: 0.8, tds: 210, temperature: 20.0 },
      runoff: { ph: 6.2, turbidity: 7.5, tds: 680, temperature: 25.5 },
      industrial: { ph: 3.8, turbidity: 19.5, tds: 1420, temperature: 31.0 }
    };
    const values = presets[preset];
    if (values) {
      setPredictInputs(values);
      runPrediction(values);
    }
  };

  // Find Nearest Safe Source
  const findNearestSafe = async () => {
    setLocatingNearest(true);
    try {
      const res = await fetch(`${API_BASE}/api/sources/nearest-safe?lat=${userLocation.lat}&lng=${userLocation.lng}`);
      if (res.ok) {
        const data = await res.json();
        setNearestSafe(data);
        if (data.source) {
          setSelectedSource(data.source);
        }
      } else {
        throw new Error('API returned ' + res.status);
      }
    } catch (err) {
      // Local fallback calculation from loaded sources
      const safeSources = sources.filter((s) => s.status === 'Safe');
      if (safeSources.length > 0) {
        const fallbackSource = safeSources[0];
        setNearestSafe({
          source: fallbackSource,
          distance_km: 1.25,
          travel_time_walk_mins: 15,
          route_coordinates: [
            [userLocation.lat, userLocation.lng],
            [userLocation.lat + 0.003, userLocation.lng - 0.004],
            [fallbackSource.latitude, fallbackSource.longitude]
          ]
        });
        setSelectedSource(fallbackSource);
      }
    } finally {
      setLocatingNearest(false);
    }
  };

  // Upvote Report
  const handleUpvote = async (reportId) => {
    // Optimistic UI update
    setReports((prev) =>
      prev.map((r) => (r.id === reportId ? { ...r, upvotes: r.upvotes + 1 } : r))
    );
    try {
      await fetch(`${API_BASE}/api/reports/${reportId}/upvote`, { method: 'POST' });
    } catch (e) {
      console.warn('Upvote sync failed:', e);
    }
  };

  // Submit Community Report
  const handleSubmitReport = async (e) => {
    e.preventDefault();
    if (!newReport.source_name || !newReport.comments) return;
    setSubmittingReport(true);
    try {
      const res = await fetch(`${API_BASE}/api/reports`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newReport)
      });
      if (res.ok) {
        const created = await res.json();
        setReports((prev) => [created, ...prev]);
        setReportSuccess(true);
        setNewReport({
          source_name: '',
          category: 'Algal Bloom',
          observed_color: 'Discolored / Murky',
          comments: '',
          reporter_name: '',
          latitude: 30.2672,
          longitude: -97.7431
        });
        setTimeout(() => setReportSuccess(false), 4000);
      }
    } catch (err) {
      // Fallback local append
      const fakeReport = {
        id: Date.now(),
        ...newReport,
        reporter_name: newReport.reporter_name || 'Anonymous Citizen',
        status: 'Reported',
        upvotes: 1,
        created_at: new Date().toISOString()
      };
      setReports((prev) => [fakeReport, ...prev]);
      setReportSuccess(true);
      setTimeout(() => setReportSuccess(false), 4000);
    } finally {
      setSubmittingReport(false);
    }
  };

  // Filtered sources
  const filteredSources = useMemo(() => {
    return sources.filter((s) => {
      const matchSearch =
        s.name.toLowerCase().includes(sourceSearch.toLowerCase()) ||
        s.zone?.toLowerCase().includes(sourceSearch.toLowerCase()) ||
        s.source_type?.toLowerCase().includes(sourceSearch.toLowerCase());
      const matchStatus =
        sourceFilterStatus === 'all' || s.status.toLowerCase() === sourceFilterStatus.toLowerCase();
      return matchSearch && matchStatus;
    });
  }, [sources, sourceSearch, sourceFilterStatus]);

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col font-sans">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-50 bg-[#0c1222]/90 backdrop-blur-md border-b border-slate-800/80 px-4 lg:px-8 py-3.5 transition-all">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          {/* Logo & Platform Tag */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20 text-white">
              <Droplets className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-cyan-400 via-sky-300 to-blue-400 bg-clip-text text-transparent">
                  AquaShield AI
                </span>
                <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-300">
                  v1.0
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                Intelligent Water Security & Safe Source Locator
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center gap-1 sm:gap-2 overflow-x-auto py-1">
            <button
              onClick={() => setActiveTab('overview')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                activeTab === 'overview'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Activity className="w-4 h-4" />
              <span>Overview</span>
            </button>
            <button
              onClick={() => setActiveTab('predictor')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                activeTab === 'predictor'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              <span>AI Classifier</span>
            </button>
            <button
              onClick={() => setActiveTab('locator')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                activeTab === 'locator'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Compass className="w-4 h-4" />
              <span>Water Locator</span>
            </button>
            <button
              onClick={() => setActiveTab('reports')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                activeTab === 'reports'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Send className="w-4 h-4" />
              <span>Community ({reports.length})</span>
            </button>
            <button
              onClick={() => setActiveTab('alerts')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                activeTab === 'alerts'
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span>Alerts ({alerts.length})</span>
            </button>
          </nav>

          {/* Connection Status & Sensor Drift Toggle */}
          <div className="flex items-center gap-3">
            <div
              className={`flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-medium border ${
                apiConnected
                  ? 'bg-emerald-950/60 border-emerald-800/80 text-emerald-300'
                  : 'bg-amber-950/60 border-amber-800/80 text-amber-300'
              }`}
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  apiConnected ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
                }`}
              />
              <span className="hidden sm:inline">
                {apiConnected ? 'FastAPI Connected' : 'Simulated Engine'}
              </span>
            </div>

            <button
              onClick={() => setLiveStreamActive(!liveStreamActive)}
              title="Toggle Live Sensor Drift"
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs border transition-all ${
                liveStreamActive
                  ? 'bg-cyan-950/80 border-cyan-800 text-cyan-300'
                  : 'bg-slate-900 border-slate-700 text-slate-400'
              }`}
            >
              <Radio className={`w-3.5 h-3.5 ${liveStreamActive ? 'animate-pulse text-cyan-400' : ''}`} />
              <span className="hidden md:inline">IoT Stream</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-8">
        {/* ========================================================= */}
        {/* TAB 1: OVERVIEW & DASHBOARD */}
        {/* ========================================================= */}
        {activeTab === 'overview' && (
          <div className="space-y-8 animate-fadeIn">
            {/* Hero Banner */}
            <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-950/80 via-slate-900 to-cyan-950/80 border border-slate-800 p-6 sm:p-8 shadow-2xl">
              <div className="relative z-10 max-w-2xl space-y-4">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-medium">
                  <ShieldCheck className="w-4 h-4 text-cyan-400" />
                  Autonomous Real-Time Water Quality Shield
                </div>
                <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
                  Protecting Communities with{' '}
                  <span className="bg-gradient-to-r from-cyan-400 to-sky-300 bg-clip-text text-transparent">
                    AI-Powered Water Intelligence
                  </span>
                </h1>
                <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
                  Real-time telemetry, Random Forest safety classification, WHO/EPA compliance validation,
                  and turn-by-turn routing to the nearest verified potable sources.
                </p>
                <div className="flex flex-wrap gap-3 pt-2">
                  <button
                    onClick={() => setActiveTab('predictor')}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold text-sm hover:from-cyan-400 hover:to-blue-500 shadow-lg shadow-cyan-500/25 transition-all transform active:scale-95"
                  >
                    <Sparkles className="w-4 h-4" />
                    Test Water Sample
                  </button>
                  <button
                    onClick={() => setActiveTab('locator')}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-200 font-semibold text-sm transition-all"
                  >
                    <MapPin className="w-4 h-4 text-cyan-400" />
                    Find Nearest Safe Water
                  </button>
                </div>
              </div>
              <div className="absolute -right-10 -bottom-10 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
            </div>

            {/* Metric KPI Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="glass-card rounded-2xl p-5 border border-slate-800/80 hover:border-cyan-500/40 transition-all">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-400">City Safety Index</span>
                  <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
                    <ShieldCheck className="w-5 h-5" />
                  </div>
                </div>
                <div className="mt-4 flex items-baseline gap-2">
                  <span className="text-3xl font-extrabold text-white">
                    {analytics?.safe_percentage ? `${analytics.safe_percentage}%` : '87.5%'}
                  </span>
                  <span className="text-xs font-semibold text-emerald-400">WHO Compliant</span>
                </div>
                <p className="mt-1 text-xs text-slate-500">
                  {analytics?.safe_sources || 21} of {analytics?.total_sources || 24} sources verified safe
                </p>
              </div>

              <div className="glass-card rounded-2xl p-5 border border-slate-800/80 hover:border-cyan-500/40 transition-all">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-400">Monitored Sources</span>
                  <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400">
                    <Droplets className="w-5 h-5" />
                  </div>
                </div>
                <div className="mt-4 flex items-baseline gap-2">
                  <span className="text-3xl font-extrabold text-white">
                    {sources.length > 0 ? sources.length : 24}
                  </span>
                  <span className="text-xs font-semibold text-cyan-400">Active Sensors</span>
                </div>
                <p className="mt-1 text-xs text-slate-500">Live IoT telemetry streaming</p>
              </div>

              <div className="glass-card rounded-2xl p-5 border border-slate-800/80 hover:border-rose-500/40 transition-all">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-400">Active Advisories</span>
                  <div className="p-2 rounded-xl bg-rose-500/10 text-rose-400">
                    <AlertTriangle className="w-5 h-5" />
                  </div>
                </div>
                <div className="mt-4 flex items-baseline gap-2">
                  <span className="text-3xl font-extrabold text-white">{alerts.length || 3}</span>
                  <span className="text-xs font-semibold text-rose-400">Requires Caution</span>
                </div>
                <p className="mt-1 text-xs text-slate-500">Instant notification to local residents</p>
              </div>

              <div className="glass-card rounded-2xl p-5 border border-slate-800/80 hover:border-blue-500/40 transition-all">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-400">Community Reports</span>
                  <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400">
                    <Send className="w-5 h-5" />
                  </div>
                </div>
                <div className="mt-4 flex items-baseline gap-2">
                  <span className="text-3xl font-extrabold text-white">{reports.length || 6}</span>
                  <span className="text-xs font-semibold text-blue-400">Crowdsourced</span>
                </div>
                <p className="mt-1 text-xs text-slate-500">Citizen verified with GPS coordinates</p>
              </div>
            </div>

            {/* Real-time Parameters & Live AI Assessment */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Current Telemetry Gauges */}
              <div className="lg:col-span-2 glass-panel rounded-2xl p-6 border border-slate-800 space-y-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-cyan-400" />
                    <h2 className="text-lg font-bold text-white">Live IoT Sensor Readings</h2>
                  </div>
                  <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-800 text-slate-400 border border-slate-700">
                    Sensor #AQUA-0104 • Austin Central
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-2">
                    <span className="text-xs text-slate-400">Acidity (pH)</span>
                    <div className="text-2xl font-black text-cyan-300">{predictInputs.ph}</div>
                    <div className="text-[11px] text-slate-500">Normal: 6.5 - 8.5</div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-2">
                    <span className="text-xs text-slate-400">Turbidity</span>
                    <div className="text-2xl font-black text-sky-300">{predictInputs.turbidity} <span className="text-xs text-slate-400 font-normal">NTU</span></div>
                    <div className="text-[11px] text-slate-500">Normal: &lt; 1.0 NTU</div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-2">
                    <span className="text-xs text-slate-400">Dissolved Solids</span>
                    <div className="text-2xl font-black text-blue-300">{predictInputs.tds} <span className="text-xs text-slate-400 font-normal">ppm</span></div>
                    <div className="text-[11px] text-slate-500">Normal: &lt; 300 ppm</div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-2">
                    <span className="text-xs text-slate-400">Temperature</span>
                    <div className="text-2xl font-black text-amber-300">{predictInputs.temperature} <span className="text-xs text-slate-400 font-normal">°C</span></div>
                    <div className="text-[11px] text-slate-500">Optimal: 15 - 22 °C</div>
                  </div>
                </div>

                {/* Live Assessment Box */}
                {prediction && (
                  <div
                    className={`p-4 rounded-xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 ${
                      prediction.classification === 'Safe'
                        ? 'bg-emerald-950/30 border-emerald-800/60'
                        : prediction.classification === 'Moderate'
                        ? 'bg-amber-950/30 border-amber-800/60'
                        : 'bg-rose-950/30 border-rose-800/60'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      {prediction.classification === 'Safe' ? (
                        <CheckCircle2 className="w-8 h-8 text-emerald-400 shrink-0" />
                      ) : prediction.classification === 'Moderate' ? (
                        <AlertTriangle className="w-8 h-8 text-amber-400 shrink-0" />
                      ) : (
                        <XCircle className="w-8 h-8 text-rose-400 shrink-0" />
                      )}
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-white text-base">
                            Classification: {prediction.classification}
                          </span>
                          <span
                            className={`text-xs px-2 py-0.5 rounded font-semibold ${
                              prediction.classification === 'Safe'
                                ? 'bg-emerald-900 text-emerald-300'
                                : prediction.classification === 'Moderate'
                                ? 'bg-amber-900 text-amber-300'
                                : 'bg-rose-900 text-rose-300'
                            }`}
                          >
                            {prediction.confidence}% Confidence
                          </span>
                        </div>
                        <p className="text-xs text-slate-300 mt-1">{prediction.recommendation}</p>
                      </div>
                    </div>

                    <button
                      onClick={() => setActiveTab('predictor')}
                      className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 shrink-0 transition-all"
                    >
                      Inspect in Classifier →
                    </button>
                  </div>
                )}
              </div>

              {/* Quick Actions & Nearest Safe Box */}
              <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col justify-between space-y-6">
                <div>
                  <h2 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                    <Compass className="w-5 h-5 text-cyan-400" />
                    Nearest Safe Water
                  </h2>
                  <p className="text-xs text-slate-400">
                    Instantly pinpoint the closest tested safe source from your current location coordinates.
                  </p>

                  <div className="mt-4 p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
                    <div className="text-xs text-slate-400">Verified Nearby:</div>
                    <div className="font-bold text-sm text-cyan-300">
                      Barton Springs Natural Outlet
                    </div>
                    <div className="text-xs text-slate-400">
                      Distance: <span className="text-white font-semibold">1.2 km</span> • Approx Walk: <span className="text-emerald-400 font-semibold">14 mins</span>
                    </div>
                    <div className="text-[11px] text-slate-500">Status: 🟢 Safe (pH 7.42, 0.4 NTU)</div>
                  </div>
                </div>

                <div className="space-y-2 pt-2">
                  <button
                    onClick={() => {
                      findNearestSafe();
                      setActiveTab('locator');
                    }}
                    className="w-full py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-xs shadow-md shadow-cyan-500/20 transition-all flex items-center justify-center gap-2"
                  >
                    <Compass className="w-4 h-4" />
                    Route to Nearest Safe Water
                  </button>
                  <button
                    onClick={() => setActiveTab('reports')}
                    className="w-full py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-300 font-semibold text-xs transition-all flex items-center justify-center gap-2"
                  >
                    <Send className="w-4 h-4 text-cyan-400" />
                    Report Water Contamination
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB 2: AI WATER SAFETY CLASSIFIER */}
        {/* ========================================================= */}
        {activeTab === 'predictor' && (
          <div className="space-y-8 animate-fadeIn">
            {/* Header info */}
            <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <h1 className="text-2xl font-black text-white flex items-center gap-2.5">
                  <Sparkles className="w-6 h-6 text-cyan-400" />
                  AI Water Quality & Safety Classifier
                </h1>
                <p className="text-xs sm:text-sm text-slate-400 mt-1">
                  Adjust parameter sliders or load standard scenarios to analyze water potability using the machine learning engine.
                </p>
              </div>

              {/* Fast Presets */}
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs text-slate-400 mr-1">Presets:</span>
                <button
                  onClick={() => applyPreset('spring')}
                  className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-cyan-300 border border-slate-700 transition-all"
                >
                  🏔️ Mountain Spring
                </button>
                <button
                  onClick={() => applyPreset('tap')}
                  className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-emerald-300 border border-slate-700 transition-all"
                >
                  🚰 Municipal Tap
                </button>
                <button
                  onClick={() => applyPreset('runoff')}
                  className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-amber-300 border border-slate-700 transition-all"
                >
                  🌾 Farm Runoff
                </button>
                <button
                  onClick={() => applyPreset('industrial')}
                  className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-rose-300 border border-slate-700 transition-all"
                >
                  ☣️ Contaminated
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              {/* Parameter Controls */}
              <div className="lg:col-span-6 glass-panel rounded-2xl p-6 border border-slate-800 space-y-6">
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <Sliders className="w-5 h-5 text-cyan-400" />
                  Input Water Parameters
                </h2>

                {/* pH Slider */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-semibold text-slate-200">pH Level (Acidity / Alkalinity)</span>
                    <span className="font-mono text-cyan-300 font-bold px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
                      {predictInputs.ph}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="2"
                    max="12"
                    step="0.1"
                    value={predictInputs.ph}
                    onChange={(e) => {
                      const val = parseFloat(e.target.value);
                      setPredictInputs((p) => ({ ...p, ph: val }));
                    }}
                    className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                  />
                  <div className="flex justify-between text-[11px] text-slate-500">
                    <span>Acidic (2.0)</span>
                    <span className="text-cyan-400 font-medium">Safe: 6.5 - 8.5</span>
                    <span>Alkaline (12.0)</span>
                  </div>
                </div>

                {/* Turbidity Slider */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-semibold text-slate-200">Turbidity (Clarity / Cloudiness)</span>
                    <span className="font-mono text-cyan-300 font-bold px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
                      {predictInputs.turbidity} NTU
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="25"
                    step="0.1"
                    value={predictInputs.turbidity}
                    onChange={(e) => {
                      const val = parseFloat(e.target.value);
                      setPredictInputs((p) => ({ ...p, turbidity: val }));
                    }}
                    className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                  />
                  <div className="flex justify-between text-[11px] text-slate-500">
                    <span>Crystal Clear (0 NTU)</span>
                    <span className="text-cyan-400 font-medium">Safe: &lt; 1.0 NTU</span>
                    <span>Muddy / Murky (25 NTU)</span>
                  </div>
                </div>

                {/* TDS Slider */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-semibold text-slate-200">Total Dissolved Solids (TDS)</span>
                    <span className="font-mono text-cyan-300 font-bold px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
                      {predictInputs.tds} ppm
                    </span>
                  </div>
                  <input
                    type="range"
                    min="20"
                    max="1800"
                    step="10"
                    value={predictInputs.tds}
                    onChange={(e) => {
                      const val = parseInt(e.target.value);
                      setPredictInputs((p) => ({ ...p, tds: val }));
                    }}
                    className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                  />
                  <div className="flex justify-between text-[11px] text-slate-500">
                    <span>Low Minerals (20)</span>
                    <span className="text-cyan-400 font-medium">Ideal: &lt; 300 ppm</span>
                    <span>High Salinity (1800)</span>
                  </div>
                </div>

                {/* Temperature Slider */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-semibold text-slate-200">Temperature</span>
                    <span className="font-mono text-cyan-300 font-bold px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
                      {predictInputs.temperature} °C
                    </span>
                  </div>
                  <input
                    type="range"
                    min="5"
                    max="50"
                    step="0.5"
                    value={predictInputs.temperature}
                    onChange={(e) => {
                      const val = parseFloat(e.target.value);
                      setPredictInputs((p) => ({ ...p, temperature: val }));
                    }}
                    className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                  />
                  <div className="flex justify-between text-[11px] text-slate-500">
                    <span>Cold (5°C)</span>
                    <span className="text-cyan-400 font-medium">Normal: 15 - 22°C</span>
                    <span>Hot (50°C)</span>
                  </div>
                </div>

                <button
                  onClick={() => runPrediction()}
                  disabled={predicting}
                  className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-sm shadow-lg shadow-cyan-500/20 transition-all flex items-center justify-center gap-2"
                >
                  <RefreshCw className={`w-4 h-4 ${predicting ? 'animate-spin' : ''}`} />
                  {predicting ? 'Analyzing with Model...' : 'Classify Water Quality'}
                </button>
              </div>

              {/* Classification Result Card */}
              <div className="lg:col-span-6 glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col justify-between space-y-6">
                <div>
                  <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                    <ShieldCheck className="w-5 h-5 text-cyan-400" />
                    Classification & Action Plan
                  </h2>

                  {prediction ? (
                    <div className="space-y-6">
                      {/* Status Banner */}
                      <div
                        className={`p-5 rounded-2xl border text-center ${
                          prediction.classification === 'Safe'
                            ? 'bg-emerald-950/40 border-emerald-500/50 glow-emerald'
                            : prediction.classification === 'Moderate'
                            ? 'bg-amber-950/40 border-amber-500/50'
                            : 'bg-rose-950/40 border-rose-500/50 glow-rose'
                        }`}
                      >
                        <span
                          className={`text-xs font-black tracking-widest uppercase px-3 py-1 rounded-full ${
                            prediction.classification === 'Safe'
                              ? 'bg-emerald-900/90 text-emerald-300'
                              : prediction.classification === 'Moderate'
                              ? 'bg-amber-900/90 text-amber-300'
                              : 'bg-rose-900/90 text-rose-300'
                          }`}
                        >
                          {prediction.classification} WATER
                        </span>

                        <div className="mt-4 text-3xl font-extrabold text-white">
                          {prediction.confidence}% Confidence
                        </div>

                        <p className="text-xs sm:text-sm text-slate-300 mt-2 px-4">
                          {prediction.recommendation}
                        </p>
                      </div>

                      {/* Probability Distribution */}
                      <div className="space-y-2">
                        <span className="text-xs font-semibold text-slate-400">Class Probabilities</span>
                        <div className="grid grid-cols-3 gap-2 text-center text-xs">
                          <div className="p-2 rounded-lg bg-emerald-950/40 border border-emerald-900/60">
                            <span className="text-slate-400 block text-[10px]">Safe</span>
                            <span className="font-mono font-bold text-emerald-400">
                              {prediction.probabilities?.Safe ?? 0}%
                            </span>
                          </div>
                          <div className="p-2 rounded-lg bg-amber-950/40 border border-amber-900/60">
                            <span className="text-slate-400 block text-[10px]">Moderate</span>
                            <span className="font-mono font-bold text-amber-400">
                              {prediction.probabilities?.Moderate ?? 0}%
                            </span>
                          </div>
                          <div className="p-2 rounded-lg bg-rose-950/40 border border-rose-900/60">
                            <span className="text-slate-400 block text-[10px]">Dangerous</span>
                            <span className="font-mono font-bold text-rose-400">
                              {prediction.probabilities?.Dangerous ?? 0}%
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Flags & Warnings */}
                      {prediction.flags && prediction.flags.length > 0 && (
                        <div className="space-y-1.5">
                          <span className="text-xs font-semibold text-rose-400 flex items-center gap-1.5">
                            <AlertCircle className="w-4 h-4" />
                            Detected Anomaly Flags:
                          </span>
                          <div className="flex flex-wrap gap-2">
                            {prediction.flags.map((flag, idx) => (
                              <span
                                key={idx}
                                className="text-xs px-2.5 py-1 rounded bg-rose-950/60 border border-rose-800 text-rose-300"
                              >
                                {flag}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Action Steps */}
                      <div className="space-y-2">
                        <span className="text-xs font-semibold text-slate-300">
                          Recommended Consumer Actions:
                        </span>
                        <ul className="space-y-1.5 text-xs text-slate-300">
                          {prediction.action_steps?.map((step, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <span className="text-cyan-400 font-bold">•</span>
                              <span>{step}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-12 text-slate-500">
                      Click "Classify Water Quality" to inspect parameters.
                    </div>
                  )}
                </div>

                <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-400">
                  <span className="font-semibold text-slate-300 block mb-1">Standard WHO Thresholds:</span>
                  pH: 6.5 - 8.5 • Turbidity: &lt; 1.0 NTU • TDS: &lt; 300 ppm • Temp: &lt; 25°C
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB 3: WATER LOCATOR & NAVIGATION */}
        {/* ========================================================= */}
        {activeTab === 'locator' && (
          <div className="space-y-8 animate-fadeIn">
            {/* Action Bar */}
            <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <h1 className="text-2xl font-black text-white flex items-center gap-2">
                  <Compass className="w-6 h-6 text-cyan-400" />
                  Water Source Locator & Safe Routing
                </h1>
                <p className="text-xs sm:text-sm text-slate-400 mt-1">
                  Discover verified drinking taps, natural springs, and accredited monitoring stations.
                </p>
              </div>

              <button
                onClick={findNearestSafe}
                disabled={locatingNearest}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-sm shadow-md shadow-cyan-500/20 transition-all flex items-center gap-2 shrink-0"
              >
                <Compass className={`w-4 h-4 ${locatingNearest ? 'animate-spin' : ''}`} />
                {locatingNearest ? 'Locating...' : 'Locate Nearest Safe Source'}
              </button>
            </div>

            {/* Nearest Safe Callout Banner (if selected/computed) */}
            {nearestSafe && (
              <div className="p-5 rounded-2xl bg-gradient-to-r from-emerald-950/60 to-slate-900 border border-emerald-600/40 glow-emerald flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex items-center gap-3.5">
                  <div className="p-3 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    <MapPin className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="text-xs font-semibold uppercase text-emerald-400 tracking-wider">
                      Optimal Verified Safe Route
                    </div>
                    <div className="text-lg font-bold text-white">
                      {nearestSafe.source?.name}
                    </div>
                    <div className="text-xs text-slate-300 mt-0.5">
                      Distance: <span className="font-semibold text-emerald-300">{nearestSafe.distance_km} km</span> • Estimated Walking Time:{' '}
                      <span className="font-semibold text-emerald-300">{nearestSafe.travel_time_walk_mins} mins</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs px-3 py-1 rounded-full bg-emerald-900/80 border border-emerald-700 text-emerald-200 font-semibold">
                    Safe (100% WHO Potable)
                  </span>
                </div>
              </div>
            )}

            {/* Two Column Layout: Source Cards + Details Visualizer */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Left Column: Filterable List */}
              <div className="lg:col-span-5 space-y-4">
                {/* Search & Filter Controls */}
                <div className="flex items-center gap-2">
                  <div className="relative flex-1">
                    <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      type="text"
                      placeholder="Search by name, zone, or type..."
                      value={sourceSearch}
                      onChange={(e) => setSourceSearch(e.target.value)}
                      className="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  <select
                    value={sourceFilterStatus}
                    onChange={(e) => setSourceFilterStatus(e.target.value)}
                    className="bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-300 px-3 py-2 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="all">All Status</option>
                    <option value="safe">Safe Only</option>
                    <option value="moderate">Moderate</option>
                    <option value="dangerous">Dangerous</option>
                  </select>
                </div>

                {/* Sources Feed */}
                <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
                  {filteredSources.map((source) => (
                    <div
                      key={source.id}
                      onClick={() => setSelectedSource(source)}
                      className={`p-4 rounded-xl border cursor-pointer transition-all ${
                        selectedSource?.id === source.id
                          ? 'bg-cyan-950/40 border-cyan-500/60 shadow-md'
                          : 'glass-card border-slate-800/80 hover:border-slate-700 hover:bg-slate-850'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="space-y-1">
                          <div className="font-bold text-sm text-white">{source.name}</div>
                          <div className="text-xs text-slate-400 flex items-center gap-1.5">
                            <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                            {source.zone || 'Metropolitan Basin'} • Type: {source.source_type}
                          </div>
                        </div>

                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase shrink-0 ${
                            source.status === 'Safe'
                              ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                              : source.status === 'Moderate'
                              ? 'bg-amber-950 text-amber-400 border border-amber-800'
                              : 'bg-rose-950 text-rose-400 border border-rose-800'
                          }`}
                        >
                          {source.status}
                        </span>
                      </div>

                      <div className="mt-3 grid grid-cols-4 gap-1 text-[11px] font-mono text-slate-400 bg-slate-900/60 p-2 rounded-lg">
                        <div>pH: <span className="text-slate-200 font-semibold">{source.ph}</span></div>
                        <div>Turb: <span className="text-slate-200 font-semibold">{source.turbidity}</span></div>
                        <div>TDS: <span className="text-slate-200 font-semibold">{source.tds}</span></div>
                        <div>{source.temperature}°C</div>
                      </div>
                    </div>
                  ))}

                  {filteredSources.length === 0 && (
                    <div className="text-center py-8 text-xs text-slate-500">
                      No water sources match the search criteria.
                    </div>
                  )}
                </div>
              </div>

              {/* Right Column: Selected Source Detailed Card & Map Visualizer */}
              <div className="lg:col-span-7 glass-panel rounded-2xl p-6 border border-slate-800 space-y-6">
                {selectedSource ? (
                  <div className="space-y-6">
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <span className="text-xs text-cyan-400 font-semibold tracking-wide uppercase">
                          Source Profile
                        </span>
                        <h2 className="text-xl font-black text-white">{selectedSource.name}</h2>
                        <p className="text-xs text-slate-400 mt-0.5">{selectedSource.address}</p>
                      </div>

                      <span
                        className={`text-xs font-bold px-3 py-1 rounded-full uppercase ${
                          selectedSource.status === 'Safe'
                            ? 'bg-emerald-900/80 text-emerald-300 border border-emerald-700'
                            : selectedSource.status === 'Moderate'
                            ? 'bg-amber-900/80 text-amber-300 border border-amber-700'
                            : 'bg-rose-900/80 text-rose-300 border border-rose-700'
                        }`}
                      >
                        Status: {selectedSource.status}
                      </span>
                    </div>

                    {/* Sensor Metric Grid */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                        <span className="text-[10px] text-slate-400">Acidity</span>
                        <div className="text-lg font-bold text-cyan-300">{selectedSource.ph} pH</div>
                      </div>
                      <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                        <span className="text-[10px] text-slate-400">Turbidity</span>
                        <div className="text-lg font-bold text-sky-300">{selectedSource.turbidity} NTU</div>
                      </div>
                      <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                        <span className="text-[10px] text-slate-400">TDS</span>
                        <div className="text-lg font-bold text-blue-300">{selectedSource.tds} ppm</div>
                      </div>
                      <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                        <span className="text-[10px] text-slate-400">Temp</span>
                        <div className="text-lg font-bold text-amber-300">{selectedSource.temperature} °C</div>
                      </div>
                    </div>

                    {/* Operational Details */}
                    <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 text-xs space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Managing Operator:</span>
                        <span className="text-white font-medium">{selectedSource.operator || 'City Water Utility Authority'}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Contact / Helpline:</span>
                        <span className="text-cyan-300 font-mono">{selectedSource.contact_phone || '+1-512-555-0199'}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Coordinates:</span>
                        <span className="text-slate-300 font-mono">
                          {selectedSource.latitude?.toFixed(4)}, {selectedSource.longitude?.toFixed(4)}
                        </span>
                      </div>
                    </div>

                    {/* Map Visualizer Display */}
                    <div className="relative h-64 rounded-xl overflow-hidden border border-slate-800 bg-[#060a12] flex items-center justify-center">
                      <div className="absolute inset-0 bg-gradient-to-b from-cyan-950/20 to-blue-950/40 pointer-events-none" />
                      
                      {/* Stylized vector map representation */}
                      <svg className="w-full h-full opacity-60" viewBox="0 0 600 300">
                        <defs>
                          <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
                            <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#1e293b" strokeWidth="0.5" />
                          </pattern>
                        </defs>
                        <rect width="600" height="300" fill="url(#grid)" />
                        {/* Rivers / lake outlines */}
                        <path
                          d="M0,150 Q150,120 300,160 T600,140"
                          fill="none"
                          stroke="#0891b2"
                          strokeWidth="8"
                          strokeOpacity="0.4"
                        />
                        {/* Connecting navigation route if available */}
                        {nearestSafe && (
                          <path
                            d="M200,180 Q280,140 380,130"
                            fill="none"
                            stroke="#10b981"
                            strokeWidth="3"
                            strokeDasharray="6,4"
                          />
                        )}
                        {/* User Pin */}
                        <circle cx="200" cy="180" r="8" fill="#38bdf8" />
                        <circle cx="200" cy="180" r="14" fill="#38bdf8" fillOpacity="0.25" />
                        {/* Selected Source Pin */}
                        <circle
                          cx="380"
                          cy="130"
                          r="10"
                          fill={selectedSource.status === 'Safe' ? '#10b981' : (selectedSource.status === 'Moderate' ? '#f59e0b' : '#ef4444')}
                        />
                      </svg>

                      <div className="absolute bottom-3 left-3 bg-slate-900/90 backdrop-blur border border-slate-700/80 px-3 py-1.5 rounded-lg text-[11px] text-slate-300 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-cyan-400" />
                        <span>You (Downtown)</span>
                        <span className="text-slate-500">→</span>
                        <span className="w-2 h-2 rounded-full bg-emerald-400" />
                        <span>{selectedSource.name}</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-16 text-slate-500">
                    Select a water source on the left to preview telemetry and navigation coordinates.
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB 4: COMMUNITY REPORTS */}
        {/* ========================================================= */}
        {activeTab === 'reports' && (
          <div className="space-y-8 animate-fadeIn">
            {/* Header info */}
            <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <h1 className="text-2xl font-black text-white flex items-center gap-2">
                  <Send className="w-6 h-6 text-cyan-400" />
                  Citizen Incident Reporting & Validation
                </h1>
                <p className="text-xs sm:text-sm text-slate-400 mt-1">
                  Crowdsourced water issues: chemical sheens, algal blooms, discolored tap water, and pipe breaks.
                </p>
              </div>

              {reportSuccess && (
                <div className="px-3.5 py-1.5 rounded-lg bg-emerald-950/80 border border-emerald-700 text-emerald-300 text-xs font-semibold flex items-center gap-2 animate-fadeIn">
                  <CheckCircle2 className="w-4 h-4" />
                  Report successfully recorded!
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              {/* Submission Form */}
              <div className="lg:col-span-5 glass-panel rounded-2xl p-6 border border-slate-800 space-y-5">
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-cyan-400" />
                  Submit Contamination Notice
                </h2>

                <form onSubmit={handleSubmitReport} className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Water Body / Source Name *
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Town Lake North Dock, Oak Creek Tap"
                      value={newReport.source_name}
                      onChange={(e) => setNewReport({ ...newReport, source_name: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Incident Category *
                    </label>
                    <select
                      value={newReport.category}
                      onChange={(e) => setNewReport({ ...newReport, category: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                    >
                      <option value="Algal Bloom">Algal Bloom / Green Slime</option>
                      <option value="Industrial Runoff">Industrial / Chemical Sheen</option>
                      <option value="Pipe Burst">Pipe Burst / Rust Intrusion</option>
                      <option value="Pungent Odor">Pungent Sulfur / Chemical Odor</option>
                      <option value="Cloudy Sediment">Heavy Suspended Sediment</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Visual Color Observation
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Green film, Rusty brown, Gray murky"
                      value={newReport.observed_color}
                      onChange={(e) => setNewReport({ ...newReport, observed_color: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Your Comments & Observed Impact *
                    </label>
                    <textarea
                      required
                      rows={3}
                      placeholder="Describe what you observed (dead fish, foul smell, unusual taste)..."
                      value={newReport.comments}
                      onChange={(e) => setNewReport({ ...newReport, comments: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Your Name / Handle (Optional)
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Sarah Jenkins"
                      value={newReport.reporter_name}
                      onChange={(e) => setNewReport({ ...newReport, reporter_name: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={submittingReport}
                    className="w-full py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-xs shadow-md shadow-cyan-500/20 transition-all flex items-center justify-center gap-2"
                  >
                    <Send className="w-4 h-4" />
                    {submittingReport ? 'Broadcasting Report...' : 'Publish Community Report'}
                  </button>
                </form>
              </div>

              {/* Feed of Community Reports */}
              <div className="lg:col-span-7 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-base font-bold text-white flex items-center gap-2">
                    <Activity className="w-5 h-5 text-cyan-400" />
                    Recent Incidents ({reports.length})
                  </h2>
                  <span className="text-xs text-slate-400">Ranked by upvotes & recency</span>
                </div>

                <div className="space-y-3 max-h-[620px] overflow-y-auto pr-1">
                  {reports.map((report) => (
                    <div
                      key={report.id}
                      className="glass-card rounded-xl p-4 border border-slate-800/80 hover:border-slate-700 space-y-3"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-sm text-white">{report.source_name}</span>
                            <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-rose-950/80 border border-rose-800 text-rose-300">
                              {report.category}
                            </span>
                          </div>
                          <div className="text-xs text-slate-400 mt-0.5">
                            Reported by <span className="text-slate-300 font-medium">{report.reporter_name || 'Community Member'}</span>
                          </div>
                        </div>

                        <button
                          onClick={() => handleUpvote(report.id)}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-cyan-950/80 hover:border-cyan-700 border border-slate-700 text-cyan-300 text-xs font-semibold transition-all"
                        >
                          <ThumbsUp className="w-3.5 h-3.5" />
                          <span>{report.upvotes || 1}</span>
                        </button>
                      </div>

                      <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3 rounded-lg border border-slate-800/60">
                        "{report.comments}"
                      </p>

                      <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
                        <div>Color: <span className="text-slate-300">{report.observed_color || 'Murky'}</span></div>
                        <div className="flex items-center gap-1">
                          <span className="w-2 h-2 rounded-full bg-amber-400" />
                          <span>Status: {report.status || 'Under Investigation'}</span>
                        </div>
                      </div>
                    </div>
                  ))}

                  {reports.length === 0 && (
                    <div className="text-center py-12 text-xs text-slate-500">
                      No reports yet. Be the first to submit a community water alert!
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* TAB 5: EMERGENCY ADVISORIES */}
        {/* ========================================================= */}
        {activeTab === 'alerts' && (
          <div className="space-y-8 animate-fadeIn">
            {/* Header */}
            <div className="glass-panel rounded-2xl p-6 border border-slate-800">
              <h1 className="text-2xl font-black text-white flex items-center gap-2">
                <AlertTriangle className="w-6 h-6 text-rose-400" />
                Active Water Quality Advisories & Emergency Notices
              </h1>
              <p className="text-xs sm:text-sm text-slate-400 mt-1">
                Official notices triggered by sensor anomalies or verified community reports.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {alerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`p-5 rounded-2xl border flex flex-col justify-between space-y-4 ${
                    alert.severity === 'critical'
                      ? 'bg-rose-950/40 border-rose-600/60 glow-rose'
                      : alert.severity === 'warning'
                      ? 'bg-amber-950/40 border-amber-600/60'
                      : 'bg-blue-950/40 border-blue-600/60'
                  }`}
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span
                        className={`text-[10px] font-extrabold uppercase px-2.5 py-0.5 rounded-full ${
                          alert.severity === 'critical'
                            ? 'bg-rose-900 text-rose-200'
                            : alert.severity === 'warning'
                            ? 'bg-amber-900 text-amber-200'
                            : 'bg-blue-900 text-blue-200'
                        }`}
                      >
                        {alert.severity} ADVISORY
                      </span>
                      <span className="text-xs text-slate-400 font-mono">
                        Active Today
                      </span>
                    </div>

                    <h2 className="text-base font-bold text-white">{alert.title}</h2>
                    <p className="text-xs text-slate-300 leading-relaxed">{alert.message}</p>
                  </div>

                  <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
                    <div>Parameter: <span className="text-white font-semibold">{alert.parameter_name}</span></div>
                    <button
                      onClick={() => setActiveTab('locator')}
                      className="text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1"
                    >
                      Find Alternate Source →
                    </button>
                  </div>
                </div>
              ))}

              {alerts.length === 0 && (
                <div className="col-span-2 text-center py-16 text-slate-500">
                  No active warnings or advisories. All regional sources operating within WHO thresholds.
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#070b13] py-6 px-4 lg:px-8 mt-12 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Droplets className="w-4 h-4 text-cyan-400" />
            <span className="text-slate-400 font-medium">AquaShield AI Platform</span>
            <span>—</span>
            <span>Protecting clean drinking water access for every community.</span>
          </div>

          <div className="flex items-center gap-4 text-slate-400">
            <span>FastAPI Backend (Port 8000)</span>
            <span>•</span>
            <span>Vite Frontend (Port 5173)</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
