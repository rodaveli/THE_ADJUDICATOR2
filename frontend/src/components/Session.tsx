import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

interface Argument {
  id: number;
  content: string;
  submitted_at: string;
  is_locked: boolean;
  user: string;
}

interface SessionData {
  id: number;
  title: string;
  status: string;
  creator: string;
  opponent: string | null;
  created_at: string;
  join_link: string | null;
}

const Session: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [session, setSession] = useState<SessionData | null>(null);
  const [sessionArguments, setSessionArguments] = useState<Argument[]>([]);
  const [newArgument, setNewArgument] = useState('');
  const [judgment, setJudgment] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSessionData();
    fetchArguments();
  }, [id]);

  const fetchSessionData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:5000/session/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSession(response.data);
    } catch (err) {
      setError('Failed to fetch session data');
      console.error(err);
    }
  };

  const fetchArguments = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:5000/session_arguments/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSessionArguments(response.data.arguments);
    } catch (err) {
      setError('Failed to fetch arguments');
      console.error(err);
    }
  };

  const submitArgument = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      await axios.post(`http://localhost:5000/submit_argument/${id}`, 
        { content: newArgument },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setNewArgument('');
      fetchArguments();
    } catch (err) {
      setError('Failed to submit argument');
      console.error(err);
    }
  };

  const lockArgument = async (argumentId: number) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`http://localhost:5000/lock_argument/${argumentId}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchArguments();
    } catch (err) {
      setError('Failed to lock argument');
      console.error(err);
    }
  };

  const getJudgment = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`http://localhost:5000/get_judgment/${id}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setJudgment(response.data.judgment);
    } catch (err) {
      setError('Failed to get judgment');
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-light-blue-500 shadow-lg transform -skew-y-6 sm:skew-y-0 sm:-rotate-6 sm:rounded-3xl"></div>
        <div className="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          {session && (
            <div>
              <h1 className="text-2xl font-semibold mb-5">{session.title}</h1>
              <p>Status: {session.status}</p>
              <p>Creator: {session.creator}</p>
              <p>Opponent: {session.opponent || 'Not joined yet'}</p>
              {session.join_link && (
                <p>Join Link: {session.join_link}</p>
              )}
            </div>
          )}

          <div className="mt-5">
            <h2 className="text-xl font-semibold mb-2">Arguments</h2>
            <ul>
              {sessionArguments.map(arg => (
                <li key={arg.id} className="mb-2">
                  <p>{arg.content}</p>
                  <p className="text-sm text-gray-500">By: {arg.user} at {new Date(arg.submitted_at).toLocaleString()}</p>
                  {!arg.is_locked && (
                    <button
                      onClick={() => lockArgument(arg.id)}
                      className="mt-1 bg-yellow-500 text-white px-2 py-1 rounded-md text-sm hover:bg-yellow-600"
                    >
                      Lock Argument
                    </button>
                  )}
                </li>
              ))}
            </ul>
          </div>

          <form onSubmit={submitArgument} className="mt-5">
            <textarea
              value={newArgument}
              onChange={(e) => setNewArgument(e.target.value)}
              placeholder="Type your argument here"
              className="w-full px-3 py-2 border rounded-md"
              rows={4}
              required
            />
            <button type="submit" className="mt-2 w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600">
              Submit Argument
            </button>
          </form>

          {session?.status === 'awaiting_judgment' && (
            <button
              onClick={getJudgment}
              className="mt-5 w-full bg-green-500 text-white py-2 rounded-md hover:bg-green-600"
            >
              Get Judgment
            </button>
          )}

          {judgment && (
            <div className="mt-5">
              <h2 className="text-xl font-semibold mb-2">Judgment</h2>
              <p>{judgment}</p>
            </div>
          )}

          {error && <p className="text-red-500 mt-5">{error}</p>}
        </div>
      </div>
    </div>
  );
};

export default Session;