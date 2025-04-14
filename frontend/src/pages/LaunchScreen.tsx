

import { useNavigate } from "react-router-dom"

const LaunchScreen = () => {
  const navigate = useNavigate()

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center bg-black text-white p-4"
      style={{
        backgroundImage: `url('/images/burger-explode.png')`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      <div className="text-center z-10">
        <h1 className="text-4xl font-bold mb-4">Welcome to Cuisine Craft.</h1>
        <h2 className="text-3xl font-bold mb-8">Let's Get Cooking.</h2>

        <button
          className="btn bg-red-400 hover:bg-red-500 text-white border-none px-6"
          onClick={() => navigate("/login")}
        >
          Start cooking
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-2" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>
    </div>
  )
}

export default LaunchScreen