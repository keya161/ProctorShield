"use client";

import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const ProctorControls = () => {
  // Step constants
  const STEP_REGISTRATION = "registration";
  const STEP_BASELINE = "baseline";
  const STEP_INSTRUCTIONS = "instructions";
  const STEP_TEST = "test";
  const STEP_RESULTS = "results";
  
  const [step, setStep] = useState(STEP_REGISTRATION);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    testId: "",
    examCode: "",
  });
  const [status, setStatus] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('description');

  const API_URL = 'http://localhost:5000/api';

  // Sample practice question for baseline
  const practiceQuestion = {
    title: "Two Sum",
    difficulty: "Easy",
    description: "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice.",
    examples: [
      {
        input: "nums = [2,7,11,15], target = 9",
        output: "[0,1]",
        explanation: "Because nums[0] + nums[1] == 9, we return [0, 1]."
      },
      {
        input: "nums = [3,2,4], target = 6",
        output: "[1,2]",
        explanation: "Because nums[1] + nums[2] == 6, we return [1, 2]."
      }
    ],
    constraints: [
      "2 <= nums.length <= 104",
      "-109 <= nums[i] <= 109",
      "-109 <= target <= 109",
      "Only one valid answer exists."
    ]
  };

  // Sample actual test question
  const testQuestion = {
    title: "Merge Intervals",
    difficulty: "Medium",
    description: "Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.",
    examples: [
      {
        input: "intervals = [[1,3],[2,6],[8,10],[15,18]]",
        output: "[[1,6],[8,10],[15,18]]",
        explanation: "Since intervals [1,3] and [2,6] overlap, merge them into [1,6]."
      },
      {
        input: "intervals = [[1,4],[4,5]]",
        output: "[[1,5]]",
        explanation: "Intervals [1,4] and [4,5] are considered overlapping."
      }
    ],
    constraints: [
      "1 <= intervals.length <= 104",
      "intervals[i].length == 2",
      "0 <= starti <= endi <= 104"
    ]
  };

  // Default code for editor
  const defaultCode = "function solution(nums, target) {\n  // Write your code here\n  \n}";

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSelectChange = (name, value) => {
    setFormData({ ...formData, [name]: value });
  };

  const handleRegistration = async (e) => {
    e.preventDefault();
    // Save registration data
    localStorage.setItem("candidateData", JSON.stringify(formData));
    
    // Start baseline collection automatically after registration
    await startBaseline();
    setStep(STEP_BASELINE);
  };

  const startBaseline = async () => {
    setLoading(true);
    setStatus('Starting baseline collection...');
    try {
      const response = await fetch(`${API_URL}/start_baseline`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      setStatus(`Baseline started: ${data.message}`);
    } catch (error) {
      setStatus(`Error: ${error.message}`);
    }
    setLoading(false);
  };

  const stopBaseline = async () => {
    setLoading(true);
    setStatus('Stopping baseline collection...');
    try {
      const response = await fetch(`${API_URL}/stop_baseline`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      setStatus(`Baseline stopped: ${data.message}. ${data.data_points || 0} data points collected.`);
      setStep(STEP_INSTRUCTIONS);
    } catch (error) {
      setStatus(`Error: ${error.message}`);
    }
    setLoading(false);
  };

  const startTest = async () => {
    setLoading(true);
    setStatus('Starting test...');
    try {
      const response = await fetch(`${API_URL}/start_test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      setStatus(`Test started: ${data.message}`);
      setStep(STEP_TEST);
    } catch (error) {
      setStatus(`Error: ${error.message}`);
    }
    setLoading(false);
  };

  const endTest = async () => {
    setLoading(true);
    setStatus('Ending test and analyzing results...');
    try {
      const response = await fetch(`${API_URL}/end_test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      setResults(data);
      // Only try to access suspicion_level if it exists
      if (data && typeof data.suspicion_level === 'number') {
        setStatus(`Test completed. Suspicion level: ${data.suspicion_level.toFixed(1)}/10`);
      } else {
        setStatus('Test completed. Results received.');
      }
      setStep(STEP_RESULTS);
    } catch (error) {
      setStatus(`Error: ${error.message}`);
    }
    setLoading(false);
  };

  // Component for rendering question description - Updated with dark theme
  const QuestionDescription = ({ question }) => (
    <div className="space-y-4 bg-gray-900 p-4 rounded-md">
      <div>
        <h2 className="text-xl font-bold text-white">{question.title}</h2>
        <span className={`inline-block px-2 py-1 text-xs rounded-full ${
          question.difficulty === 'Easy' ? 'bg-green-700 text-green-100' :
          question.difficulty === 'Medium' ? 'bg-yellow-700 text-yellow-100' :
          'bg-red-700 text-red-100'
        }`}>
          {question.difficulty}
        </span>
      </div>
      
      <div className="text-white">
        <p>{question.description}</p>
      </div>
      
      <div className="space-y-3">
        <h3 className="font-semibold text-white">Examples:</h3>
        {question.examples.map((example, index) => (
          <div key={index} className="bg-gray-800 p-3 rounded-md border border-gray-700">
            <div><strong className="text-white">Input:</strong> <code className="text-blue-300">{example.input}</code></div>
            <div><strong className="text-white">Output:</strong> <code className="text-green-300">{example.output}</code></div>
            {example.explanation && (
              <div><strong className="text-white">Explanation:</strong> <span className="text-gray-300">{example.explanation}</span></div>
            )}
          </div>
        ))}
      </div>
      
      <div>
        <h3 className="font-semibold text-white">Constraints:</h3>
        <ul className="list-disc pl-5 text-gray-300">
          {question.constraints.map((constraint, index) => (
            <li key={index}>{constraint}</li>
          ))}
        </ul>
      </div>
    </div>
  );

  // LeetCode-like code editor component - Updated with dark theme
  const CodeEditor = () => (
    <div className="h-full">
      <textarea 
        className="w-full h-64 p-4 font-mono text-sm bg-gray-900 border border-gray-700 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        defaultValue={defaultCode}
      />
      <div className="mt-4 flex justify-between">
        <div className="text-sm text-gray-300">
          Language: JavaScript
        </div>
        <Button>Run Code</Button>
      </div>
    </div>
  );

  // LeetCode-like problem interface - Updated with dark theme
  const ProblemInterface = ({ question, onComplete, buttonText }) => (
    <div className="w-full max-w-6xl mx-auto bg-gray-800 rounded-xl shadow-md overflow-hidden">
      <div className="flex flex-col md:flex-row h-full">
        {/* Left panel - Problem description */}
        <div className="w-full md:w-1/2 p-6 overflow-y-auto border-r border-gray-700">
          <Tabs defaultValue="description" value={activeTab} onValueChange={setActiveTab} className="text-white">
            <TabsList className="mb-4 bg-gray-700">
              <TabsTrigger value="description" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white">Description</TabsTrigger>
              <TabsTrigger value="solution" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white">Solution</TabsTrigger>
              <TabsTrigger value="submissions" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white">Submissions</TabsTrigger>
            </TabsList>
            
            <TabsContent value="description">
              <QuestionDescription question={question} />
            </TabsContent>
            
            <TabsContent value="solution">
              <div className="text-white bg-gray-900 p-4 rounded-md">
                <p>Solution hints will be available after you submit your answer.</p>
              </div>
            </TabsContent>
            
            <TabsContent value="submissions">
              <div className="text-white bg-gray-900 p-4 rounded-md">
                <p>No submissions yet.</p>
              </div>
            </TabsContent>
          </Tabs>
        </div>
        
        {/* Right panel - Code editor */}
        <div className="w-full md:w-1/2 p-6 bg-gray-800">
          <CodeEditor />
          
          <div className="mt-6 flex justify-end">
            <Button 
              onClick={onComplete}
              disabled={loading}
              className="px-6"
            >
              {buttonText}
            </Button>
          </div>
        </div>
      </div>
      
      {/* Status bar */}
      <div className="bg-gray-700 px-6 py-2 text-sm text-white">
        <p><strong>Status:</strong> {status}</p>
      </div>
    </div>
  );

  return (
    <div className="container mx-auto py-8">
      {step === STEP_REGISTRATION && (
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Candidate Registration</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleRegistration} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Full Name</Label>
                <Input
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="testId">Test Type</Label>
                <Select
                  value={formData.testId}
                  onValueChange={(value) => handleSelectChange("testId", value)}
                >
                  <SelectTrigger id="testId">
                    <SelectValue placeholder="Select test type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="algorithms-test">Data Structures & Algorithms</SelectItem>
                    <SelectItem value="frontend-test">Frontend Development</SelectItem>
                    <SelectItem value="backend-test">Backend Development</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="examCode">Exam Code</Label>
                <Input
                  id="examCode"
                  name="examCode"
                  value={formData.examCode}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={loading}>
                Register & Start Baseline Collection
              </Button>
            </form>
          </CardContent>
        </Card>
      )}
      {step === STEP_BASELINE && (
        <div className="space-y-4">
          <div className="max-w-md mx-auto bg-white p-4 rounded-md shadow text-center">
            <h2 className="text-lg font-medium text-black">Baseline Collection</h2>
            <p className="text-sm text-gray-500">
              Welcome, {formData.name}! Please solve this practice problem while we collect baseline data.
            </p>
          </div>
          
          <ProblemInterface 
            question={practiceQuestion} 
            onComplete={stopBaseline} 
            buttonText="Complete Baseline Collection"
          />
        </div>
      )}

      {step === STEP_INSTRUCTIONS && (
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Test Instructions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <h3 className="font-medium">Welcome, {formData.name}</h3>
              <p className="text-sm text-gray-500">
                Please read the following instructions carefully before starting the test.
              </p>
            </div>
            <div className="space-y-2">
            <h4 className="font-medium text-black">Test Rules:</h4>
              <ul className="list-disc pl-5 text-sm space-y-1 text-black">
                <li>You have 60 minutes to complete this test.</li>
                <li>Do not refresh the page or navigate away from the test environment.</li>
                <li>Tab switching is monitored and may be flagged as suspicious.</li>
                <li>Your webcam and microphone will be active during the test.</li>
                <li>Ensure you are in a quiet, well-lit environment.</li>
                <li>No external help, reference materials, or communication is allowed.</li>
                <li>Any suspicious behavior may result in test termination.</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium text-black">Proctoring Information:</h4>
              <p className="text-sm text-black">
                This test is being monitored using our AI proctoring system. The system will analyze your behavior
                during the test to ensure academic integrity.
              </p>
            </div>
            <Button 
              onClick={startTest} 
              className="w-full"
              disabled={loading}
            >
              Start Test
            </Button>
          </CardContent>
        </Card>
      )}

      {step === STEP_TEST && (
        <div className="space-y-4">
          <div className="max-w-md mx-auto bg-white p-4 rounded-md shadow text-center">
            <h2 className="text-lg font-medium text-black">Live Test</h2>
            <p className="text-sm text-gray-500">
              Test in progress. Complete the following problem.
            </p>
          </div>
          
          <ProblemInterface 
            question={testQuestion} 
            onComplete={endTest} 
            buttonText="Submit and End Test"
          />
        </div>
      )}

      {step === STEP_RESULTS && (
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Test Results</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 bg-gray-50 rounded-md">
              <h3 className="font-medium text-black">Test Summary</h3>
              <p className="text-sm text-gray-500">
                {formData.name} ({formData.email})
              </p>
              <p className="text-sm text-gray-500">
                Test ID: {formData.testId}
              </p>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium text-black">Proctoring Analysis:</h4>
              {results && (
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-black">Suspicion Level:</span>
                    <span className={`font-medium ${
                      results.suspicion_level < 3 ? 'text-green-600' : 
                      results.suspicion_level < 7 ? 'text-yellow-600' : 
                      'text-red-600'
                    }`}>
                      {results.suspicion_level?.toFixed(1)}/10
                    </span>
                  </div>
                  
                  <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${
                        results.suspicion_level < 3 ? 'bg-green-500' : 
                        results.suspicion_level < 7 ? 'bg-yellow-500' : 
                        'bg-red-500'
                      }`}
                      style={{ width: `${results.suspicion_level * 10}%` }}
                    />
                  </div>
                  
                  <div className="mt-4">
                    <h5 className="font-medium text-black">Detected Behaviors:</h5>
                    <ul className="list-disc pl-5 text-sm text-black">
                      {results.behaviors?.map((behavior, index) => (
                        <li key={index}>{behavior.description} (Score: {behavior.score.toFixed(1)})</li>
                      )) || <li>No suspicious behaviors detected</li>}
                    </ul>
                  </div>
                </div>
              )}
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium text-black">Problem Solving Performance:</h4>
              <div className="text-sm text-black">
                <p>Time Spent: {results?.time_spent || '0'} minutes</p>
                <p>Code Correctness: {results?.code_correctness || 'N/A'}</p>
                <p>Code Efficiency: {results?.code_efficiency || 'N/A'}</p>
              </div>
            </div>
            
            <div className="pt-4">
              <Button 
                onClick={() => setStep(STEP_REGISTRATION)}
                className="w-full"
              >
                Start New Test
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ProctorControls;