module.exports = {
    // 🔍 Contenu à scanner (CRITIQUE pour v3)
    content: [
      "./index.html",
      "./src/**/*.{js,ts,jsx,tsx,vue,svelte}",
      "./pages/**/*.{js,ts,jsx,tsx}",
      "./components/**/*.{js,ts,jsx,tsx}",
      // Vos autres chemins...
    ],
    
    // 🎨 Thème personnalisé
    theme: {
      screens: {
        'xs': '475px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
      },
      extend: {
        colors: {
          primary: {
            50: '#eff6ff',
            100: '#dbeafe',
            500: '#3b82f6',
            600: '#2563eb',
            700: '#1d4ed8',
          },
          secondary: {
            500: '#8b5cf6',
          }
        },
        fontFamily: {
          'sans': ['Inter', 'system-ui', 'sans-serif'],
          'mono': ['Fira Code', 'monospace'],
        },
        animation: {
          'fade-in': 'fadeIn 0.5s ease-in-out',
          'slide-up': 'slideUp 0.3s ease-out',
        },
        keyframes: {
          fadeIn: {
            '0%': { opacity: '0' },
            '100%': { opacity: '1' },
          },
          slideUp: {
            '0%': { transform: 'translateY(10px)', opacity: '0' },
            '100%': { transform: 'translateY(0)', opacity: '1' },
          },
        },
      },
    },
    
    // ⚙️ Variantes
    variants: {
      extend: {
        opacity: ['disabled'],
        cursor: ['disabled'],
      },
    },
    
    // 🔌 Plugins
    plugins: [
      require('@tailwindcss/forms'),
      require('@tailwindcss/typography'),
      require('@tailwindcss/aspect-ratio'),
      // Autres plugins...
    ],
    
    // 🚫 Désactiver le preflight si nécessaire (pour intégration avec d'autres frameworks)
    corePlugins: {
      // preflight: false,
    },
    
    // 🌙 Mode sombre (class-based)
    darkMode: 'class', // ou 'media' pour préférence système
  }