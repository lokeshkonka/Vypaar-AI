import { useState } from "react";
import { Link, NavLink, useNavigate, useLocation } from "react-router-dom";
import {
  SignedIn,
  SignedOut,
  UserButton,
} from "@clerk/clerk-react";

import {
  FiMenu,
  FiBell,
  FiUser,
  FiBarChart2,
  FiBox,
  FiTrendingUp,
  FiActivity,
  FiChevronLeft,
  FiSun,
  FiMoon,
  FiMousePointer,
} from "react-icons/fi";

import NavLoader from "./NavLoader";
import { useTheme } from "../../../context/ThemeContext";
import { useNotify } from "../../../context/NotifyContext";
import NotificationComponent from "./NotificationComponent";

/* =========================
   NAVBAR
   ========================= */

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [showNotif, setShowNotif] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const { unreadCount } = useNotify();

  const isActive = (path: string) =>
    location.pathname.startsWith(path);

  return (
    <>
      {/* ================= TOP NAVBAR ================= */}
      <header className="fixed top-0 z-30 w-full bg-white dark:bg-[#0f1f1b] border-b border-gray-200 dark:border-[#1f3a33]">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">

          {/* LEFT */}
          <div className="flex items-center gap-4">
            <button
              onClick={() => setOpen(true)}
              className="text-gray-600 dark:text-gray-300 hover:text-black dark:hover:text-white transition"
            >
              <FiMenu size={22} />
            </button>

            <Link to="/" className="flex items-center gap-2">
              <img src="/icon.png" className="h-8 w-8" />
              <span className="font-semibold text-gray-900 dark:text-white">
                Vypaar AI
              </span>
            </Link>
          </div>

          {/* CENTER */}
          <nav className="hidden md:flex items-center gap-10 text-sm">
            <NavLink
              to="/blog"
              className={({ isActive }) =>
                isActive
                  ? "text-black dark:text-white font-medium"
                  : "text-gray-600 dark:text-gray-300 hover:text-black dark:hover:text-white"
              }
            >
              Blog
            </NavLink>

            <NavLink
              to="/pricing"
              className={({ isActive }) =>
                isActive
                  ? "text-black dark:text-white font-medium"
                  : "text-gray-600 dark:text-gray-300 hover:text-black dark:hover:text-white"
              }
            >
              Pricing
            </NavLink>
          </nav>

          {/* RIGHT */}
          <div className="flex items-center gap-4 ">
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="cursor-pointer rounded-2xl translate-x-3 p-2 text-gray-600 dark:text-gray-300 hover:bg-black/5 dark:hover:bg-white/10 transition"
              aria-label="Toggle theme"
            >
              {theme === "dark" ? <FiSun size={18} /> : <FiMoon size={18} />}
            </button>

            {/* Notifications */}
            <div className=" px-3 translate-y-1 ">
              <button
                onClick={() => setShowNotif(v => !v)}
                className="cursor-pointer  relative text-gray-600 dark:text-gray-300 hover:text-black dark:hover:text-white transition"
              >
                <FiBell size={20} />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-emerald-400" />
                )}
              </button>

              {showNotif && <NotificationComponent />}
            </div>

            {/* User */}
            <SignedIn>
              <UserButton
                appearance={{
                  elements: {
                    avatarBox:
                      "h-8 w-8 border border-gray-300 dark:border-white/20 rounded-full",
                  },
                }}
              />
            </SignedIn>

            <SignedOut>
              <FiUser size={20} className="text-gray-500 dark:text-gray-300" />
            </SignedOut>
          </div>
        </div>
      </header>

      {/* ================= SIDE NAVBAR ================= */}
      <NavLoader open={open}>
        <div className="flex h-full flex-col px-5 py-6 bg-white dark:bg-[#0f1f1b]">

          {/* HEADER */}
          <div className="flex items-center justify-between">
            <Link
              to="/"
              onClick={() => setOpen(false)}
              className="flex items-center gap-2"
            >
              <img src="/icon.png" className="h-8 w-8" />
              <span className="text-lg font-semibold text-gray-900 dark:text-white">
                Vypaar AI
              </span>
            </Link>

            <button
              onClick={() => setOpen(false)}
              className="rounded-md p-1 cursor-pointer text-gray-500 dark:text-gray-300 hover:text-black dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/10 transition"
            >
              <FiChevronLeft size={22} />
            </button>
          </div>

          <div className="my-5 h-px bg-gray-200 dark:bg-white/10" />

          {/* DASHBOARD NAV */}
          <div className="space-y-1">
            <SideItem
              icon={<FiBarChart2 />}
              label="Product Analysis"
              active={isActive("/dashboard/product-analysis")}
              onClick={() => {
                navigate("/dashboard/product-analysis");
                setOpen(false);
              }}
            />
            <SideItem
              icon={<FiBox />}
              label="Inventory"
              active={isActive("/dashboard/inventory")}
              onClick={() => {
                navigate("/dashboard/inventory");
                setOpen(false);
              }}
            />
            <SideItem
              icon={<FiTrendingUp />}
              label="Insights"
              active={isActive("/dashboard/insights")}
              onClick={() => {
                navigate("/dashboard/insights");
                setOpen(false);
              }}
            />
            <SideItem
              icon={<FiActivity />}
              label="Model Accuracy"
              active={isActive("/dashboard/model-accuracy")}
              onClick={() => {
                navigate("/dashboard/model-accuracy");
                setOpen(false);
              }}
            />
            <SideItem
              icon={<FiMousePointer />}
              label="Selector"
              active={isActive("/dashboard/selector")}
              onClick={() => {
                navigate("/dashboard/selector");
                setOpen(false);
              }}
            />
          </div>

          <div className="my-5 h-px bg-gray-200 dark:bg-white/10" />

          {/* MOBILE LINKS */}
          <div className="md:hidden space-y-2">
            <NavLink
              to="/pricing"
              onClick={() => setOpen(false)}
              className="block text-sm text-gray-600 dark:text-gray-300 hover:text-black dark:hover:text-white"
            >
              Pricing
            </NavLink>
            <NavLink
              to="/blog"
              onClick={() => setOpen(false)}
              className="block text-sm text-gray-600 dark:text-gray-300 hover:text-black dark:hover:text-white"
            >
              Blog
            </NavLink>
          </div>

          <div className="flex-1" />

          <span className="text-xs text-gray-400 dark:text-gray-500">
            © Vypaar AI
          </span>
        </div>
      </NavLoader>
    </>
  );
}

/* =========================
   SIDE ITEM
   ========================= */

function SideItem({
  icon,
  label,
  onClick,
  active,
}: {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  active: boolean;
}) {
  return (
    <button
      onClick={onClick}
      className={`
        flex w-full items-center gap-3 rounded-lg px-4 py-2.5 transition cursor-pointer
        ${
          active
            ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
            : "text-gray-700 dark:text-gray-300 hover:bg-black/5 dark:hover:bg-white/10"
        }
      `}
    >
      <span className="text-lg">{icon}</span>
      <span className="text-sm font-medium">{label}</span>
    </button>
  );
}
