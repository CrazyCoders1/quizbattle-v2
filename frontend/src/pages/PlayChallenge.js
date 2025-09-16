import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/apiService';
import toast from 'react-hot-toast';

const PlayChallenge = () => {
  const { challengeId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [challenge, setChallenge] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [skippedQuestions, setSkippedQuestions] = useState(new Set());
  const [showSkipModal, setShowSkipModal] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);
  const [quizStarted, setQuizStarted] = useState(false);
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [showImageModal, setShowImageModal] = useState(null);

  // Prevent back navigation during quiz
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (quizStarted && !quizCompleted) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    const handlePopState = (e) => {
      if (quizStarted && !quizCompleted) {
        e.preventDefault();
        const confirmLeave = window.confirm('Are you sure you want to leave? Your progress will be lost.');
        if (!confirmLeave) {
          window.history.pushState(null, '', window.location.pathname);
        } else {
          setQuizStarted(false);
          navigate('/challenges');
        }
      }
    };

    if (quizStarted && !quizCompleted) {
      window.addEventListener('beforeunload', handleBeforeUnload);
      window.addEventListener('popstate', handlePopState);
      // Push current state to prevent immediate back
      window.history.pushState(null, '', window.location.pathname);
    }

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      window.removeEventListener('popstate', handlePopState);
    };
  }, [quizStarted, quizCompleted, navigate]);

  // State for time warnings
  const [timeWarnings, setTimeWarnings] = useState({
    fiveMinute: false,
    oneMinute: false,
    thirtySecond: false
  });

  // Auto-submit when time runs out
  const handleAutoSubmit = useCallback(() => {
    if (quizCompleted || submitting) return;
    console.log('⏰ Time is up! Auto-submitting quiz...');
    toast.info('Time is up! Submitting your answers automatically...');
    handleSubmitQuiz(true); // Force submit without skip confirmation
  }, [quizCompleted, submitting, handleSubmitQuiz]);

  // Timer effect
  useEffect(() => {
    let interval = null;
    if (quizStarted && timeLeft > 0 && !quizCompleted && !submitting) {
      interval = setInterval(() => {
        setTimeLeft(prevTime => {
          // Auto-submit when time is up
          if (prevTime <= 1) {
            // Use setTimeout to avoid state update conflicts
            setTimeout(() => handleAutoSubmit(), 0);
            return 0;
          }

          // Show time warnings
          if (prevTime === 300 && !timeWarnings.fiveMinute) { // 5 minutes
            toast.warning('Only 5 minutes remaining!');
            setTimeWarnings(prev => ({ ...prev, fiveMinute: true }));
          } else if (prevTime === 60 && !timeWarnings.oneMinute) { // 1 minute
            toast.warning('Only 1 minute remaining! Quiz will auto-submit.');
            setTimeWarnings(prev => ({ ...prev, oneMinute: true }));
          } else if (prevTime === 30 && !timeWarnings.thirtySecond) { // 30 seconds
            toast.warning('30 seconds left! Auto-submitting soon...');
            setTimeWarnings(prev => ({ ...prev, thirtySecond: true }));
          }

          return prevTime - 1;
        });
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [quizStarted, quizCompleted, submitting, handleAutoSubmit]);

  // Load challenge and questions
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    loadChallengeData();
  }, [challengeId, isAuthenticated, navigate]);

  const loadChallengeData = async () => {
    try {
      setLoading(true);
      console.log('🎮 Loading challenge data for challengeId:', challengeId);
      
      const response = await apiService.getChallengeQuestions(challengeId);
      console.log('📊 API response:', response.data);
      
      const { questions: loadedQuestions, challenge: challengeData } = response.data;
      
      console.log('🎯 Challenge data:', challengeData);
      console.log('❓ Questions loaded:', loadedQuestions?.length || 0);
      
      if (!challengeData) {
        console.error('❌ No challenge data received');
        toast.error('Challenge data not found');
        navigate('/challenges');
        return;
      }
      
      if (!loadedQuestions || loadedQuestions.length === 0) {
        console.error('❌ No questions loaded for challenge');
        toast.error('No questions available for this challenge');
        navigate('/challenges');
        return;
      }
      
      setChallenge(challengeData);
      setQuestions(loadedQuestions);
      setTimeLeft(challengeData.time_limit * 60); // Convert minutes to seconds
      
      console.log('✅ Challenge data loaded successfully');
    } catch (error) {
      console.error('❌ Error loading challenge data:', error);
      toast.error(error.response?.data?.error || 'Failed to load challenge data');
      navigate('/challenges');
    } finally {
      setLoading(false);
    }
  };

  const handleStartQuiz = () => {
    setQuizStarted(true);
    setCurrentQuestion(0);
    setAnswers({});
    setSkippedQuestions(new Set());
    setQuizCompleted(false);
    setResult(null);
    setTimeWarnings({ fiveMinute: false, oneMinute: false, thirtySecond: false });
  };

  const handleAnswerSelect = (questionId, answerIndex) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answerIndex
    }));
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

  const handleSkipQuestion = () => {
    const currentQuestionId = questions[currentQuestion].id;
    setSkippedQuestions(prev => new Set([...prev, currentQuestionId]));
    
    // Move to next question if not the last one
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handleSubmitQuiz = useCallback(async (forceSubmit = false) => {
    if (submitting) return;
    
    // Check for skipped questions if not forcing submit
    if (!forceSubmit && skippedQuestions.size > 0) {
      setShowSkipModal(true);
      return;
    }
    
    setSubmitting(true);
    try {
      const timeTaken = (challenge.time_limit * 60) - timeLeft;
      const response = await apiService.submitChallenge(challengeId, {
        answers,
        time_taken: timeTaken
      });
      const submissionResult = response.data.result;
      
      // Calculate detailed results for display
      let correctAnswers = 0;
      let wrongAnswers = 0;
      const questionResults = [];

      questions.forEach(question => {
        const userAnswer = answers[question.id];
        const isCorrect = userAnswer !== undefined && userAnswer === question.answer;
        const isAnswered = userAnswer !== undefined;
        
        if (isAnswered) {
          if (isCorrect) {
            correctAnswers++;
          } else {
            wrongAnswers++;
          }
        }

        questionResults.push({
          ...question,
          userAnswer,
          isCorrect,
          isAnswered
        });
      });

      const totalQuestions = questions.length;
      const unanswered = totalQuestions - (correctAnswers + wrongAnswers);
      const score = Math.max(0, (correctAnswers * 4) - (wrongAnswers * 1));
      const percentage = Math.round((correctAnswers / totalQuestions) * 100);

      setResult({
        correct: correctAnswers,
        wrong: wrongAnswers,
        unanswered,
        total: totalQuestions,
        score,
        percentage,
        questionResults,
        timeTaken: (challenge.time_limit * 60) - timeLeft
      });

      setQuizCompleted(true);
      setQuizStarted(false);
      toast.success('Quiz submitted successfully!');
      
      // Refresh leaderboards in background with retry logic
      setTimeout(async () => {
        try {
          console.log('📊 Refreshing leaderboards after submission...');
          await Promise.allSettled([
            apiService.getLeaderboard('global'),
            apiService.getLeaderboard('challenge', challengeId)
          ]);
          console.log('✅ Leaderboards refreshed successfully');
        } catch (error) {
          console.warn('⚠️ Failed to refresh leaderboards:', error);
          // Don't show error to user as this is background operation
        }
      }, 1000); // Small delay to ensure backend has processed the result
    } catch (error) {
      toast.error('Failed to submit quiz');
    } finally {
      setSubmitting(false);
    }
  }, [challengeId, answers, questions, challenge, timeLeft, submitting, skippedQuestions]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const ImageModal = ({ imageUrl, onClose }) => (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50" onClick={onClose}>
      <div className="max-w-4xl max-h-full p-4" onClick={e => e.stopPropagation()}>
        <img 
          src={imageUrl} 
          alt="Question" 
          className="max-w-full max-h-full object-contain rounded-lg"
        />
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-white text-2xl bg-black bg-opacity-50 rounded-full w-10 h-10 flex items-center justify-center hover:bg-opacity-75"
        >
          ×
        </button>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading challenge...</p>
        </div>
      </div>
    );
  }

  // Debug logging for challenge/questions state
  console.log('🔍 Debug - challenge:', challenge);
  console.log('🔍 Debug - questions.length:', questions?.length);
  console.log('🔍 Debug - loading:', loading);
  console.log('🔍 Debug - quizStarted:', quizStarted);

  // Handle case where challenge exists but no questions are available
  if (!loading && challenge && questions?.length === 0) {
    console.log('⚠️ Challenge found but no questions available');
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-6xl mb-4">🏆</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">No Questions Available</h2>
          <p className="text-gray-600 mb-6">
            The challenge "{challenge.name}" exists, but there are currently no questions available for 
            {challenge.exam_type} ({challenge.difficulty} difficulty).
          </p>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-yellow-800">
              This might happen if the database hasn't been populated with questions yet. 
              Please contact the administrator or try a different challenge.
            </p>
          </div>
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => navigate('/challenges')}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Back to Challenges
            </button>
            <button
              onClick={() => window.location.reload()}
              className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Only show "Challenge Not Found" if challenge itself is missing
  if (!loading && !challenge) {
    console.log('❌ Challenge not found - redirecting');
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Challenge Not Found</h2>
          <p className="text-gray-600 mb-6">The challenge you're looking for doesn't exist or has been deactivated.</p>
          <button
            onClick={() => navigate('/challenges')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Back to Challenges
          </button>
        </div>
      </div>
    );
  }

  // Quiz completed - show results
  if (quizCompleted && result) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-8">
            {/* Header */}
            <div className="text-center mb-8">
              <div className="text-6xl mb-4">🎉</div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Challenge Completed!</h1>
              <h2 className="text-xl text-gray-600">{challenge.name}</h2>
            </div>

            {/* Score Overview */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-green-100 p-6 rounded-lg text-center">
                <div className="text-3xl font-bold text-green-600">{result.correct}</div>
                <div className="text-sm text-green-700">Correct</div>
              </div>
              <div className="bg-red-100 p-6 rounded-lg text-center">
                <div className="text-3xl font-bold text-red-600">{result.wrong}</div>
                <div className="text-sm text-red-700">Wrong</div>
              </div>
              <div className="bg-gray-100 p-6 rounded-lg text-center">
                <div className="text-3xl font-bold text-gray-600">{result.unanswered}</div>
                <div className="text-sm text-gray-700">Unanswered</div>
              </div>
              <div className="bg-blue-100 p-6 rounded-lg text-center">
                <div className="text-3xl font-bold text-blue-600">{result.score}</div>
                <div className="text-sm text-blue-700">Score</div>
              </div>
            </div>

            {/* Circular Progress */}
            <div className="flex justify-center mb-8">
              <div className="relative">
                <svg className="w-32 h-32 transform -rotate-90">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="transparent"
                    className="text-gray-200"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="transparent"
                    strokeDasharray={`${2 * Math.PI * 56}`}
                    strokeDashoffset={`${2 * Math.PI * 56 * (1 - result.percentage / 100)}`}
                    className="text-blue-600 transition-all duration-1000"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-2xl font-bold text-gray-900">{result.percentage}%</span>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-center space-x-4 mb-8">
              <button
                onClick={() => navigate('/challenges')}
                className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                Back to Challenges
              </button>
              <button
                onClick={() => navigate('/leaderboard')}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                View Leaderboard
              </button>
            </div>

            {/* Detailed Review */}
            <div className="border-t pt-8">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Question Review</h3>
              <div className="space-y-6">
                {result.questionResults.map((question, index) => (
                  <div key={question.id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between mb-3">
                      <h4 className="font-medium text-gray-900">Question {index + 1}</h4>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        !question.isAnswered ? 'bg-gray-100 text-gray-600' :
                        question.isCorrect ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
                      }`}>
                        {!question.isAnswered ? 'Not Answered' : question.isCorrect ? 'Correct' : 'Wrong'}
                      </span>
                    </div>
                    <p className="text-gray-700 mb-4">{question.text}</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {question.options.map((option, optionIndex) => (
                        <div
                          key={optionIndex}
                          className={`p-2 rounded border ${
                            optionIndex === question.answer ? 'bg-green-100 border-green-300' :
                            optionIndex === question.userAnswer && question.userAnswer !== question.answer ? 'bg-red-100 border-red-300' :
                            'bg-gray-50 border-gray-200'
                          }`}
                        >
                          <span className="text-sm">
                            {optionIndex === question.answer && '✓ '}
                            {optionIndex === question.userAnswer && question.userAnswer !== question.answer && '✗ '}
                            {option}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Quiz not started - show challenge info
  if (!quizStarted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-2xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{challenge.name}</h1>
            <p className="text-gray-600 mb-8">Ready to start the challenge?</p>
            
            <div className="bg-blue-50 rounded-lg p-6 mb-8">
              <h3 className="font-semibold text-blue-900 mb-4">Challenge Details</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-blue-700">Exam Type:</span>
                  <span className="font-medium ml-2">{challenge.exam_type}</span>
                </div>
                <div>
                  <span className="text-blue-700">Difficulty:</span>
                  <span className="font-medium ml-2 capitalize">{challenge.difficulty}</span>
                </div>
                <div>
                  <span className="text-blue-700">Questions:</span>
                  <span className="font-medium ml-2">{challenge.question_count}</span>
                </div>
                <div>
                  <span className="text-blue-700">Time Limit:</span>
                  <span className="font-medium ml-2">{challenge.time_limit} minutes</span>
                </div>
              </div>
            </div>

            <div className="bg-yellow-50 rounded-lg p-4 mb-8">
              <h3 className="font-semibold text-yellow-900 mb-2">Instructions</h3>
              <ul className="text-sm text-yellow-800 text-left space-y-1">
                <li>• You have {challenge.time_limit} minutes to complete all questions</li>
                <li>• +4 points for correct answers, -1 for wrong answers</li>
                <li>• You can navigate between questions freely</li>
                <li>• Avoid refreshing or going back during the quiz</li>
                <li>• Submit your answers before time runs out</li>
              </ul>
            </div>

            <button
              onClick={handleStartQuiz}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg font-medium text-lg transition-colors"
            >
              Start Challenge
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Quiz in progress
  const question = questions[currentQuestion];
  const userAnswer = answers[question.id];

  return (
    <div className="min-h-screen bg-gray-50 py-4">
      <div className="max-w-4xl mx-auto px-4">
        {/* Timer and Progress */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex justify-between items-center mb-3">
            <div className="text-lg font-semibold">
              Question {currentQuestion + 1} of {questions.length}
            </div>
            <div className={`text-xl font-bold transition-colors ${
              timeLeft <= 0 ? 'text-red-700 animate-pulse' :
              timeLeft < 60 ? 'text-red-600 animate-pulse' :
              timeLeft < 300 ? 'text-yellow-600' : 'text-blue-600'
            }`}>
              {formatTime(timeLeft)}
              {timeLeft <= 60 && timeLeft > 0 && (
                <span className="text-xs ml-2 text-red-500">(Auto-submit soon!)</span>
              )}
            </div>
          </div>
          <div className="bg-gray-200 rounded-full h-3">
            <div 
              className="bg-blue-600 h-3 rounded-full transition-all duration-300"
              style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Question */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">{question.text}</h3>
          
          {/* Question image if exists */}
          {question.image && (
            <div className="mb-6">
              <img 
                src={question.image} 
                alt="Question" 
                className="max-w-full h-64 object-contain rounded-lg cursor-zoom-in border"
                onClick={() => setShowImageModal(question.image)}
              />
            </div>
          )}
          
          <div className="space-y-3">
            {question.options.map((option, index) => (
              <label
                key={index}
                className={`block p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                  userAnswer === index
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
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
                      <div className="w-2 h-2 bg-white rounded-full" />
                    )}
                  </div>
                  <span className="text-gray-900">{option}</span>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <div className="flex space-x-2">
            <button
              onClick={handlePreviousQuestion}
              disabled={currentQuestion === 0}
              className="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Previous
            </button>
            <button
              onClick={handleSkipQuestion}
              className="bg-yellow-600 hover:bg-yellow-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Skip
            </button>
          </div>
          
          {/* Question indicators */}
          <div className="flex space-x-2 overflow-x-auto">
            {questions.map((_, index) => {
              const questionId = questions[index].id;
              const isAnswered = answers[questionId] !== undefined;
              const isSkipped = skippedQuestions.has(questionId);
              
              return (
                <button
                  key={index}
                  onClick={() => setCurrentQuestion(index)}
                  className={`w-10 h-10 rounded-full text-sm font-medium transition-colors flex-shrink-0 ${
                    index === currentQuestion
                      ? 'bg-blue-600 text-white'
                      : isAnswered
                      ? 'bg-green-500 text-white'
                      : isSkipped
                      ? 'bg-yellow-500 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                  title={isSkipped ? 'Skipped' : isAnswered ? 'Answered' : 'Unanswered'}
                >
                  {index + 1}
                </button>
              );
            })}
          </div>
          
          {currentQuestion === questions.length - 1 ? (
            <button
              onClick={handleSubmitQuiz}
              disabled={submitting}
              className="bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              {submitting ? 'Submitting...' : 'Submit Quiz'}
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

      {/* Image Modal */}
      {showImageModal && (
        <ImageModal 
          imageUrl={showImageModal} 
          onClose={() => setShowImageModal(null)} 
        />
      )}
      
      {/* Skip Confirmation Modal */}
      {showSkipModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="text-center">
              <div className="text-6xl mb-4">⚠️</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Questions Skipped</h3>
              <p className="text-gray-600 mb-4">
                You skipped {skippedQuestions.size} question(s): {Array.from(skippedQuestions)
                  .map(questionId => questions.findIndex(q => q.id === questionId) + 1)
                  .sort((a, b) => a - b)
                  .join(', ')}
              </p>
              <p className="text-gray-600 mb-6">
                Do you want to return and complete them before submitting?
              </p>
              
              <div className="flex space-x-3 justify-center">
                <button
                  onClick={() => {
                    setShowSkipModal(false);
                    // Go to first skipped question
                    const firstSkipped = questions.findIndex(q => skippedQuestions.has(q.id));
                    if (firstSkipped !== -1) {
                      setCurrentQuestion(firstSkipped);
                    }
                  }}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                >
                  Go Back
                </button>
                <button
                  onClick={() => {
                    setShowSkipModal(false);
                    handleSubmitQuiz(true); // Force submit
                  }}
                  className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                >
                  Confirm Submit
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlayChallenge;