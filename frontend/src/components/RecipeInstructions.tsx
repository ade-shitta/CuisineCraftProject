import React, { useState } from "react";

interface InstructionStep {
  text: string;
  completed: boolean;
}

interface RecipeInstructionsProps {
  rawInstructions: string[];
  recipeId: string; // Add recipeId prop
  onComplete?: (recipeId: string) => void; // Update to pass recipeId
}

const RecipeInstructions: React.FC<RecipeInstructionsProps> = ({ 
  rawInstructions,
  recipeId,
  onComplete
}) => {
  // Process instructions into clean steps
  const processedSteps = React.useMemo(() => {
    return rawInstructions
      .map(step => step.trim())
      .filter(step => step && !/^\d+\.?\s*$/.test(step))
      .map(text => ({ text, completed: false }));
  }, [rawInstructions]);
  
  const [steps, setSteps] = useState<InstructionStep[]>(processedSteps);
  const [cookingMode, setCookingMode] = useState(false);
  const [completionRecorded, setCompletionRecorded] = useState(false);
  
  // Track progress
  const progress = steps.filter(step => step.completed).length / steps.length;
  const allCompleted = steps.every(step => step.completed);
  
  // Toggle step completion
  const toggleStep = (index: number) => {
    const newSteps = [...steps];
    newSteps[index].completed = !newSteps[index].completed;
    setSteps(newSteps);
    
    // Check if all steps are now completed
    const nowAllCompleted = newSteps.every(step => step.completed);
    
    // If all steps are completed and completion hasn't been recorded yet
    if (nowAllCompleted && !completionRecorded && onComplete) {
      onComplete(recipeId);
      setCompletionRecorded(true);
    }
  };

  return (
    <div className="recipe-instructions">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">Instructions</h2>
        <button 
          onClick={() => setCookingMode(!cookingMode)}
          className={`px-3 py-1 rounded-full text-sm font-medium ${
            cookingMode 
              ? "bg-red-500 text-white" 
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          }`}
        >
          {cookingMode ? "Exit Cooking Mode" : "Start Cooking"}
        </button>
      </div>
      
      {/* Progress bar */}
      {cookingMode && steps.length > 0 && (
        <div className="mb-4">
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              className="bg-red-500 h-2.5 rounded-full transition-all duration-300 ease-in-out"
              style={{ width: `${progress * 100}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-500 mt-1 text-right">
            {Math.round(progress * 100)}% complete
          </p>
        </div>
      )}
      
      {/* Instructions list */}
      <ul className="space-y-4">
        {steps.map((step, index) => (
          <li 
            key={index} 
            className={`p-3 rounded-lg transition-all duration-200 cursor-pointer ${
              cookingMode 
                ? "bg-white shadow-sm border border-gray-100" 
                : ""
            } ${step.completed ? "bg-green-50" : ""}`}
            onClick={() => cookingMode && toggleStep(index)}
          >
            <div className="flex items-start gap-3">
              {cookingMode && (
                <>
                  <div 
                    className="flex-shrink-0 w-5 h-5 border border-gray-300 rounded bg-white overflow-hidden relative"
                    style={{ minWidth: '1.25rem' }} 
                  >
                    {step.completed && (
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path 
                          fillRule="evenodd" 
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" 
                          clipRule="evenodd" 
                        />
                      </svg>
                    )}
                  </div>
                  <span 
                    className={`ml-2 ${step.completed ? "line-through text-gray-400" : "text-gray-800"}`}
                  >
                    {step.text}
                  </span>
                </>
              )}
              {!cookingMode && (
                <span className="text-gray-800">
                  {step.text}
                </span>
              )}
            </div>
          </li>
        ))}
      </ul>
      
      {/* Completion message */}
      {allCompleted && cookingMode && (
        <div className="mt-6 p-4 bg-green-100 text-green-700 rounded-lg text-center">
          <p className="font-medium">You've completed all the steps! Enjoy your meal! 🎉</p>
        </div>
      )}
    </div>
  );
};

export default RecipeInstructions;