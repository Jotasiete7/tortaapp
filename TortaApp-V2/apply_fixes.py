# -*- coding: utf-8 -*-
import os

# Paths
dashboard_path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\components\Dashboard.tsx"
profile_path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\components\PlayerProfile.tsx"
app_path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\App.tsx"

# 1. Fix Dashboard
try:
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()

    dashboard_target = """            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mt-8">
                {/* Market Intelligence */}
                <div>
                    <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-emerald-500" />
                        Market Intelligence
                    </h2>
                    <Leaderboard />
                </div>

                {/* Advanced Data Tools */}
                <div>
                    <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                        <Database className="w-5 h-5 text-amber-500" />
                        Advanced Data Tools
                    </h2>
                    <LogUploader
                        onProcessingComplete={(records) => {
                            console.log("Processed RAW logs:", records);
                        }}
                    />
                </div>
            </div>"""

    dashboard_replacement = """            {/* Market Intelligence - Full Width */}
            <div className="mt-8">
                <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                    <Activity className="w-5 h-5 text-emerald-500" />
                    Market Intelligence
                </h2>
                <Leaderboard />
            </div>

            {/* Advanced Data Tools - Full Width */}
            <div className="mt-8">
                <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                    <Database className="w-5 h-5 text-amber-500" />
                    Advanced Data Tools
                </h2>
                <LogUploader
                    onProcessingComplete={(records) => {
                        console.log("Processed RAW logs:", records);
                    }}
                />
            </div>"""

    # Normalize
    content = content.replace('\r\n', '\n')
    dashboard_target = dashboard_target.replace('\r\n', '\n')
    dashboard_replacement = dashboard_replacement.replace('\r\n', '\n')

    if dashboard_target in content:
        content = content.replace(dashboard_target, dashboard_replacement)
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Dashboard fixed.")
    else:
        print("Dashboard target not found.")
except Exception as e:
    print(f"Error fixing Dashboard: {e}")

# 2. Fix PlayerProfile
try:
    with open(profile_path, 'r', encoding='utf-8') as f:
        content = f.read()

    profile_target = """                                <ServerIcon server={stats.fav_server || 'Unknown'} className="text-base" />
                                <span className="font-bold ml-1">{stats.fav_server || 'Unknown'}</span>"""

    profile_replacement = """                                <ServerIcon server={stats.fav_server || 'Unknown'} className="text-base" />
                                <span className="font-bold ml-1">
                                    {(() => {
                                        const s = (stats.fav_server || '').toLowerCase();
                                        if (s.includes('har')) return 'Harmony';
                                        if (s.includes('mel')) return 'Melody';
                                        if (s.includes('cad')) return 'Cadence';
                                        return stats.fav_server || 'Unknown';
                                    })()}
                                </span>"""

    content = content.replace('\r\n', '\n')
    profile_target = profile_target.replace('\r\n', '\n')
    profile_replacement = profile_replacement.replace('\r\n', '\n')

    if profile_target in content:
        content = content.replace(profile_target, profile_replacement)
        with open(profile_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("PlayerProfile fixed.")
    else:
        print("PlayerProfile target not found.")
except Exception as e:
    print(f"Error fixing PlayerProfile: {e}")

# 3. Fix App.tsx
try:
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Use unicode escape for bullet point to avoid encoding issues
    # \u2022 is the bullet point
    app_target = """                                    <div className="flex items-center gap-2 mt-1">
                                        <span className="text-xs text-slate-500">
                                            {showEmail ? user.email : '\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022'}
                                        </span>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setShowEmail(!showEmail);
                                            }}
                                            className="text-slate-600 hover:text-slate-400 transition-colors"
                                            title={showEmail ? "Hide Email" : "Show Email"}
                                        >
                                            {showEmail ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                                        </button>
                                    </div>"""

    app_replacement = """                                    <div className="flex items-center gap-2 mt-1 bg-slate-800/50 px-2 py-1 rounded border border-slate-700/50">
                                        <span className="text-xs text-slate-400 font-mono tracking-wide">
                                            {showEmail ? user.email : '\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022'}
                                        </span>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setShowEmail(!showEmail);
                                            }}
                                            className="text-slate-500 hover:text-white transition-colors p-0.5 rounded hover:bg-slate-700"
                                            title={showEmail ? "Hide Email" : "Show Email"}
                                        >
                                            {showEmail ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                                        </button>
                                    </div>"""

    content = content.replace('\r\n', '\n')
    app_target = app_target.replace('\r\n', '\n')
    app_replacement = app_replacement.replace('\r\n', '\n')

    if app_target in content:
        content = content.replace(app_target, app_replacement)
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("App.tsx fixed.")
    else:
        print("App.tsx target not found.")

except Exception as e:
    print(f"Error fixing App.tsx: {e}")
