import { create } from 'zustand';

interface UIState {
  sidebarCollapsed: boolean;
  commandPaletteOpen: boolean;
  activeNavItem: string;
  notificationCount: number;
  aiCopilotActive: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  toggleCommandPalette: () => void;
  setCommandPaletteOpen: (open: boolean) => void;
  setActiveNavItem: (item: string) => void;
  setNotificationCount: (count: number) => void;
  toggleAICopilot: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarCollapsed: false,
  commandPaletteOpen: false,
  activeNavItem: 'Dashboard',
  notificationCount: 5,
  aiCopilotActive: false,
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  setSidebarCollapsed: (collapsed: boolean) => set({ sidebarCollapsed: collapsed }),
  toggleCommandPalette: () => set((state) => ({ commandPaletteOpen: !state.commandPaletteOpen })),
  setCommandPaletteOpen: (open: boolean) => set({ commandPaletteOpen: open }),
  setActiveNavItem: (item: string) => set({ activeNavItem: item }),
  setNotificationCount: (count: number) => set({ notificationCount: count }),
  toggleAICopilot: () => set((state) => ({ aiCopilotActive: !state.aiCopilotActive })),
}));
