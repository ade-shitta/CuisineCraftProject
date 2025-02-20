module.exports = {
    content: [
      "./src/**/*.{js,jsx,ts,tsx}",
      "../backend/users/templates/**/*.{html}",
    ],
    theme: {
      extend: {},
    },
    plugins: [require("daisyui")],
  }