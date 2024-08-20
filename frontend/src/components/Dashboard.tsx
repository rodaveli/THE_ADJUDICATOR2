import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface Session {
  id: number;
  title: string;
  status: string;
}

const Dashboard: React.FC = () => {
  const [createdSessions, setCreatedSessions] = useState<Session[]>([]);
  const [joinedSessions, setJoinedSessions] = useState<Session[]>([]);
  const [newSessionTitle, setNewSessionTitle] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/user_sessions', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCreatedSessions(response.data.created_sessions);
      setJoinedSessions(response.data.joined_sessions);
    } catch (err) {
      setError('Failed to fetch sessions');
      console.error(err);
    }
  };

  const createSession = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/create_session', 
        { title: newSessionTitle },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setNewSessionTitle('');
      fetchSessions();
    } catch (err) {
      setError('Failed to create session');
      console.error(err);
    }
  };

  const joinSession = async (joinLink: string) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`http://localhost:5000/join_session/${joinLink}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchSessions();
    } catch (err) {
      setError('Failed to join session');
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-light-blue-500 shadow-lg transform -skew-y-6 sm:skew-y-0 sm:-rotate-6 sm:rounded-3xl"></div>
        <div className="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <h1 className="text-2xl font-semibold mb-5">Dashboard</h1>
          
          <form onSubmit={createSession} className="mb-5">
            <input
              type="text"
              value={newSessionTitle}
              onChange={(e) => setNewSessionTitle(e.target.value)}
              placeholder="New session title"
              className="w-full px-3 py-2 border rounded-md"
              required
            />
            <button type="submit" className="mt-2 w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600">
              Create New Session
            </button>
          </form>

          <div className="mb-5">
            <h2 className="text-xl font-semibold mb-2">Created Sessions</h2>
            <ul>
              {createdSessions.map(session => (
                <li key={session.id} className="mb-2">
                  <span>{session.title} - {session.status}</span>
                  <button
                    onClick={() => navigate(`/session/${session.id}`)}
                    className="ml-2 bg-green-500 text-white px-2 py-1 rounded-md text-sm hover:bg-green-600"
                  >
                    View
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h2 className="text-xl font-semibold mb-2">Joined Sessions</h2>
            <ul>
              {joinedSessions.map(session => (
                <li key={session.id} className="mb-2">
                  <span>{session.title} - {session.status}</span>
                  <button
                    onClick={() => navigate(`/session/${session.id}`)}
                    className="ml-2 bg-green-500 text-white px-2 py-1 rounded-md text-sm hover:bg-green-600"
                  >
                    View
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {error && <p className="text-red-500 mt-5">{error}</p>}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;