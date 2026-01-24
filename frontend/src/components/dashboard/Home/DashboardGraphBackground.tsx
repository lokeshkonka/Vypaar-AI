import "./home.css"
export default function DashboardGraphBackground() {
  return (
    <svg
      className="dashboard-graph"
      viewBox="0 0 1200 500"
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      {/* === PRIMARY SIGNAL (STRONG) === */}
      <path
        d="M0 220 
           C 150 210, 300 240, 450 230 
           C 600 220, 750 250, 900 240 
           C 1050 230, 1150 245, 1200 235"
        className="dashboard-line line-main"
      />

      {/* === SECONDARY SIGNAL (SUPPORTING) === */}
      <path
        d="M0 245 
           C 180 235, 360 255, 540 245 
           C 720 235, 900 260, 1200 250"
        className="dashboard-line line-secondary"
      />

      {/* === TREND LINE (LONG-TERM) === */}
      <path
        d="M0 300 
           C 300 290, 600 310, 900 300 
           C 1050 295, 1150 305, 1200 300"
        className="dashboard-line line-trend"
      />

      {/* === MID DEPTH LINES === */}
      <path
        d="M0 270 
           C 240 280, 480 260, 720 270 
           C 960 280, 1100 275, 1200 280"
        className="dashboard-line line-faint"
      />

      <path
        d="M0 320 
           C 260 330, 520 310, 780 320 
           C 1040 330, 1150 325, 1200 330"
        className="dashboard-line line-faint delay-1"
      />

      {/* === HIGH-FREQUENCY NOISE (VERY SUBTLE) === */}
      <path
        d="M0 200 
           C 120 195, 240 205, 360 198 
           C 480 190, 600 210, 720 202 
           C 840 195, 960 210, 1200 205"
        className="dashboard-line line-ultra-faint delay-2"
      />

      <path
        d="M0 350 
           C 150 355, 300 345, 450 352 
           C 600 360, 750 340, 900 350 
           C 1050 360, 1150 345, 1200 355"
        className="dashboard-line line-ultra-faint delay-1"
      />
    </svg>
  );
}
