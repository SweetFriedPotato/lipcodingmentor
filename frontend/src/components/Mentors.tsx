import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { mentorService, authService } from '../services/api';
import { User } from '../types';
import './Auth.css';

const Mentors: React.FC = () => {
  const { user } = useAuth();
  const [mentors, setMentors] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchSkill, setSearchSkill] = useState('');
  const [orderBy, setOrderBy] = useState('');
  const [requestMessages, setRequestMessages] = useState<{[key: number]: string}>({});
  const [requestLoading, setRequestLoading] = useState<{[key: number]: boolean}>({});

  useEffect(() => {
    loadMentors();
  }, [searchSkill, orderBy]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadMentors = async () => {
    try {
      setLoading(true);
      const data = await mentorService.getMentors(searchSkill || undefined, orderBy || undefined);
      setMentors(data);
    } catch (err: any) {
      setError('멘토 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleMessageChange = (mentorId: number, message: string) => {
    setRequestMessages(prev => ({
      ...prev,
      [mentorId]: message,
    }));
  };

  const handleSendRequest = async (mentorId: number) => {
    if (!user) return;

    const message = requestMessages[mentorId] || '';
    if (!message.trim()) {
      alert('메시지를 입력해주세요.');
      return;
    }

    setRequestLoading(prev => ({ ...prev, [mentorId]: true }));

    try {
      const requestData = {
        mentorId,
        message: message.trim(),
      };

      await authService.createMatchRequest(requestData);
      alert('매칭 요청이 성공적으로 전송되었습니다.');
      setRequestMessages(prev => ({ ...prev, [mentorId]: '' }));
    } catch (err: any) {
      alert(err.response?.data?.detail || '요청 전송에 실패했습니다.');
    } finally {
      setRequestLoading(prev => ({ ...prev, [mentorId]: false }));
    }
  };

  if (user?.role !== 'mentee') {
    return (
      <div className="mentors-container">
        <div className="error-message">
          <h2>🚫 접근 권한이 없습니다</h2>
          <p>멘티만 멘토 목록을 조회할 수 있습니다.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mentors-container">
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem' }}>🎯 멘토 찾기</h1>
        <p style={{ color: 'var(--text-secondary)' }}>나에게 맞는 멘토를 찾아보세요</p>
      </div>
      
      <div className="search-controls">
        <input
          id="search"
          type="text"
          placeholder="기술 스택으로 검색..."
          value={searchSkill}
          onChange={(e) => setSearchSkill(e.target.value)}
        />
        <select
          value={orderBy}
          onChange={(e) => setOrderBy(e.target.value)}
        >
          <option value="">정렬 기준</option>
          <option id="name" value="name">이름순</option>
          <option id="skill" value="skill">기술 스택순</option>
        </select>
      </div>

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>멘토 목록을 불러오는 중...</p>
        </div>
      )}
      
      {error && <div className="error-message">{error}</div>}

      <div className="mentors-grid">
        {mentors.map((mentor) => (
          <div key={mentor.id} className="mentor">
            <img
              src={`http://localhost:8080${mentor.profile.imageUrl}`}
              alt={mentor.profile.name}
              className="mentor-image"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.src = 'https://placehold.co/500x500.jpg?text=MENTOR';
              }}
            />
            <h3>{mentor.profile.name}</h3>
            <p>{mentor.profile.bio}</p>
            {mentor.profile.skills && mentor.profile.skills.length > 0 && (
              <div className="skills-list">
                {mentor.profile.skills.map((skill, index) => (
                  <span key={index} className="skill-tag">
                    {skill}
                  </span>
                ))}
              </div>
            )}
            <div className="form-group">
              <textarea
                id="message"
                data-mentor-id={mentor.id}
                data-testid={`message-${mentor.id}`}
                placeholder="멘토링 요청 메시지를 입력하세요..."
                value={requestMessages[mentor.id] || ''}
                onChange={(e) => handleMessageChange(mentor.id, e.target.value)}
                rows={3}
              />
            </div>
            <button
              id="request"
              className="btn-primary"
              style={{ width: '100%', marginTop: '1rem' }}
              onClick={() => handleSendRequest(mentor.id)}
              disabled={requestLoading[mentor.id]}
            >
              {requestLoading[mentor.id] ? '📤 전송 중...' : '💌 매칭 요청'}
            </button>
          </div>
        ))}
      </div>

      {!loading && mentors.length === 0 && (
        <div className="empty-state">
          <h3>🔍 조건에 맞는 멘토가 없습니다</h3>
          <p>다른 검색 조건을 시도해보세요.</p>
        </div>
      )}
    </div>
  );
};

export default Mentors;
