"use client";

import { EXAMPLE_QUESTIONS } from "../../data/exampleQuestions";

interface ExampleQuestionsProps {
  onSelect: (question: string) => void;
}

export function ExampleQuestions({ onSelect }: ExampleQuestionsProps) {
  return (
    <div className="max-w-2xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-2xl sm:text-3xl font-semibold text-gray-900 dark:text-gray-100 mb-3">
          💬 Velkommen til Demens-assistenten
        </h2>
        <p className="text-gray-600 dark:text-gray-400 text-lg">
          Her er noen spørsmål jeg kan hjelpe deg med:
        </p>
      </div>

      {/* Questions Grid */}
      <div className="grid gap-3 sm:gap-4 grid-cols-1 sm:grid-cols-2 mb-8">
        {EXAMPLE_QUESTIONS.map((question, index) => (
          <button
            key={index}
            onClick={() => onSelect(question)}
            className="w-full text-left p-4 sm:p-5 rounded-xl
                       bg-white dark:bg-gray-800
                       border border-gray-200 dark:border-gray-700
                       hover:border-blue-300 dark:hover:border-blue-600
                       hover:bg-blue-50 dark:hover:bg-blue-900/20
                       shadow-sm hover:shadow-md
                       transition-all duration-200 ease-in-out
                       focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                       group"
          >
            <span className="text-gray-800 dark:text-gray-200
                           group-hover:text-blue-700 dark:group-hover:text-blue-300
                           text-sm sm:text-base leading-relaxed
                           transition-colors duration-200">
              {question}
            </span>
          </button>
        ))}
      </div>

      {/* Footer */}
      <div className="text-center">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Eller skriv ditt eget spørsmål nedenfor
        </p>
      </div>
    </div>
  );
}