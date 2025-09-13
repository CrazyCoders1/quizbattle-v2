import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/apiService';
import toast from 'react-hot-toast';

const Practice = () => {
  const { isAuthenticated } = useAuth();
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [quizStarted, setQuizStarted] = useState(false);
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [score, setScore] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    exam_type: 'CBSE 11',
    difficulty: 'easy',
    question_count: 10
  });

  useEffect(() => {
    let interval = null;
    if (quizStarted && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft(timeLeft => timeLeft - 1);
      }, 1000);
    } else if (timeLeft === 0 && quizStarted) {
      handleSubmitQuiz();
    }
    return () => clearInterval(interval);
  }, [timeLeft, quizStarted]);

  const startQuiz = async () => {
    setLoading(true);
    try {
      const response = await apiService.getQuestions(filters.exam_type, filters.difficulty);
      const allQuestions = response.data.questions;
      
      // Shuffle and take required number of questions
      const shuffled = allQuestions.sort(() => 0.5 - Math.random());
      const selectedQuestions = shuffled.slice(0, filters.question_count);
      
      setQuestions(selectedQuestions);
      setTimeLeft(filters.question_count * 60); // 1 minute per question
      setQuizStarted(true);
      setCurrentQuestion(0);
      setAnswers({});
      setQuizCompleted(false);
      setScore(null);
    } catch (error) {
      toast.error('Failed to load questions');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSelect = (questionId, answerIndex) => {
    setAnswers({
      ...answers,
      [questionId]: answerIndex
    });
  };

  const handleNextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmitQuiz = async () => {
    let correctAnswers = 0;
    let wrongAnswers = 0;

    questions.forEach(question => {
      const userAnswer = answers[question.id];
      if (userAnswer !== undefined) {
        if (userAnswer === question.answer) {
          correctAnswers++;
        } else {
          wrongAnswers++;
        }
      }
    });

    const totalScore = Math.max(0, (correctAnswers * 4) - (wrongAnswers * 1));
    
    const result = {
      correct: correctAnswers,
      wrong: wrongAnswers,
      unanswered: questions.length - (correctAnswers + wrongAnswers),
      total: questions.length,
      score: totalScore,
      percentage: Math.round((correctAnswers / questions.length) * 100)
    };
    
    setScore(result);
    setQuizCompleted(true);
    setQuizStarted(false);

    // Submit results to backend for leaderboard
    try {
      await apiService.post('/quizzes/practice/submit', {
        questions: questions.map(q => ({ id: q.id, answer: q.answer })),
        answers: answers,
        score: totalScore,
        correct_answers: correctAnswers,
        wrong_answers: wrongAnswers,
        time_taken: (filters.question_count * 60) - timeLeft
      });
    } catch (error) {
      console.error('Failed to submit practice results:', error);
      // Don't show error to user as this is just for leaderboard
    }
  };

  const resetQuiz = () => {
    setQuestions([]);
    setCurrentQuestion(0);
    setAnswers({});
    setTimeLeft(0);
    setQuizStarted(false);
    setQuizCompleted(false);
    setScore(null);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!isAuthenticated) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Please Login to Practice</h2>
        <p className="text-gray-600 mb-6">You need to be logged in to access practice quizzes.</p>
        <a
          href="/login"
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          Login Now
        </a>
      </div>
    );
  }

  if (quizCompleted && score) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <div className="text-6xl mb-4">🎉</div>
          <h2 className="text-3xl font-bold text-gray-900 mb-6">Quiz Completed!</h2>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-green-100 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{score.correct}</div>
              <div className="text-sm text-green-700">Correct</div>
            </div>
            <div className="bg-red-100 p-4 rounded-lg">
              <div className="text-2xl font-bold text-red-600">{score.wrong}</div>
              <div className="text-sm text-red-700">Wrong</div>
            </div>
            <div className="bg-gray-100 p-4 rounded-lg">
              <div className="text-2xl font-bold text-gray-600">{score.unanswered}</div>
              <div className="text-sm text-gray-700">Unanswered</div>
            </div>
            <div className="bg-blue-100 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{score.score}</div>
              <div className="text-sm text-blue-700">Score</div>
            </div>
          </div>

          <div className="mb-6">
            <div className="text-4xl font-bold text-gray-900 mb-2">{score.percentage}%</div>
            <div className="text-gray-600">Overall Performance</div>
          </div>

          <div className="flex justify-center space-x-4">
            <button
              onClick={resetQuiz}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Practice Again
            </button>
            <button
              onClick={() => window.location.href = '/leaderboard'}
              className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              View Leaderboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (quizStarted && questions.length > 0) {
    const question = questions[currentQuestion];
    const userAnswer = answers[question.id];

    return (
      <div className="max-w-4xl mx-auto">
        {/* Timer */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex justify-between items-center">
            <div className="text-lg font-semibold">
              Question {currentQuestion + 1} of {questions.length}
            </div>
            <div className={`text-lg font-bold ${timeLeft < 60 ? 'text-red-500' : 'text-blue-600'}`}>
              {formatTime(timeLeft)}
            </div>
          </div>
          <div className="mt-2 bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-1000"
              style={{ width: `${((questions.length * 60 - timeLeft) / (questions.length * 60)) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Question */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">{question.text}</h3>
          
          <div className="space-y-3">
            {question.options.map((option, index) => (
              <label
                key={index}
                className={`block p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                  userAnswer === index
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <input
                  type="radio"
                  name={`question-${question.id}`}
                  value={index}
                  checked={userAnswer === index}
                  onChange={() => handleAnswerSelect(question.id, index)}
                  className="sr-only"
                />
                <div className="flex items-center">
                  <div className={`w-6 h-6 rounded-full border-2 mr-3 flex items-center justify-center ${
                    userAnswer === index
                      ? 'border-blue-500 bg-blue-500'
                      : 'border-gray-300'
                  }`}>
                    {userAnswer === index && (
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    )}
                  </div>
                  <span className="text-gray-900">{option}</span>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-between">
          <button
            onClick={handlePreviousQuestion}
            disabled={currentQuestion === 0}
            className="bg-gray-500 hover:bg-gray-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Previous
          </button>
          
          <div className="flex space-x-2">
            {questions.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentQuestion(index)}
                className={`w-10 h-10 rounded-full text-sm font-medium transition-colors ${
                  index === currentQuestion
                    ? 'bg-blue-600 text-white'
                    : answers[questions[index].id] !== undefined
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>
          
          {currentQuestion === questions.length - 1 ? (
            <button
              onClick={handleSubmitQuiz}
              className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Submit Quiz
            </button>
          ) : (
            <button
              onClick={handleNextQuestion}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Next
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Practice Quiz</h1>
        <p className="text-gray-600">Test your knowledge with custom practice quizzes</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Quiz Settings</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Exam Type
            </label>
            <select
              value={filters.exam_type}
              onChange={(e) => setFilters({...filters, exam_type: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="CBSE 11">CBSE 11</option>
              <option value="CBSE 12">CBSE 12</option>
              <option value="JEE Main">JEE Main</option>
              <option value="JEE Advanced">JEE Advanced</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Difficulty Level
            </label>
            <select
              value={filters.difficulty}
              onChange={(e) => setFilters({...filters, difficulty: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="tough">Tough</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Number of Questions
            </label>
            <select
              value={filters.question_count}
              onChange={(e) => setFilters({...filters, question_count: parseInt(e.target.value)})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value={5}>5 Questions</option>
              <option value={10}>10 Questions</option>
              <option value={15}>15 Questions</option>
              <option value={20}>20 Questions</option>
              <option value={30}>30 Questions</option>
            </select>
          </div>
        </div>

        <div className="mt-8">
          <button
            onClick={startQuiz}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            {loading ? 'Loading Questions...' : 'Start Practice Quiz'}
          </button>
        </div>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">Scoring System:</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• +4 points for each correct answer</li>
            <li>• -1 point for each wrong answer</li>
            <li>• Minimum score: 0 (no negative scores)</li>
            <li>• Time limit: 1 minute per question</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Practice;
