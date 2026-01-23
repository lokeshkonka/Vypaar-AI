export default function Footer() {
  return (
    <footer className="relative mt-20">
      {/* Soft green background wash */}
      <div className="absolute inset-0 bg-gradient-to-b from-emerald-50/20 via-emerald-50/40 to-emerald-100/40 pointer-events-none" />

      <div className="relative px-6 sm:px-8 md:px-16 lg:px-24 xl:px-32">
        {/* Main footer content */}
        <div className="py-10 sm:py-12 border-t border-emerald-200/50 flex flex-col md:flex-row gap-8 md:gap-12 justify-between">
          
          {/* Brand / Description */}
          <div className="max-w-md">
            <h3 className="text-sm sm:text-base font-semibold text-gray-900">
              Demand Forecasting Platform
            </h3>
            <p className="mt-3 sm:mt-4 text-sm leading-relaxed text-gray-600">
              Intelligent, localized demand forecasting powered by real-world
              data signals, seasonality, and market behavior — built to help
              businesses plan inventory with confidence.
            </p>
          </div>

          {/* Links */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-3 text-sm text-gray-600">
            <a
              href="/privacy"
              className="hover:text-emerald-700 transition-colors"
            >
              Privacy Policy
            </a>
            <a
              href="/terms"
              className="hover:text-emerald-700 transition-colors"
            >
              Terms of Service
            </a>
            <a
              href="/support"
              className="hover:text-emerald-700 transition-colors"
            >
              Support
            </a>
            <a
              href="/docs"
              className="hover:text-emerald-700 transition-colors"
            >
              Documentation
            </a>
            <a
              href="/status"
              className="hover:text-emerald-700 transition-colors"
            >
              System Status
            </a>
            <a
              href="/contact"
              className="hover:text-emerald-700 transition-colors"
            >
              Contact
            </a>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="py-5 sm:py-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs sm:text-sm text-gray-500">
          <span className="text-center sm:text-left">
            © {new Date().getFullYear()} LOKI OP. All rights reserved.
          </span>

          <span className="text-gray-400">
            Built with data-driven precision
          </span>
        </div>
      </div>
    </footer>
  );
}
