import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/api';
import { MatchingRequest } from '../types';
import './Auth.css';

const Requests: React.FC = () => {
  const { user } = useAuth();
  const [incomingRequests, setIncomingRequests] = useState<MatchingRequest[]>([]);
  const [outgoingRequests, setOutgoingRequests] = useState<MatchingRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState<{ [key: number]: boolean }>({});

  const loadRequests = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      if (user.role === 'mentor') {
        const requests = await authService.getIncomingRequests();
        setIncomingRequests(requests);
      } else {
        const requests = await authService.getOutgoingRequests();
        setOutgoingRequests(requests);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '요청을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRequests();
  }, [user]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleAccept = async (requestId: number) => {
    try {
      setActionLoading(prev => ({ ...prev, [requestId]: true }));
      await authService.acceptRequest(requestId);
      await loadRequests();
    } catch (err: any) {
      setError(err.response?.data?.detail || '요청 수락에 실패했습니다.');
    } finally {
      setActionLoading(prev => ({ ...prev, [requestId]: false }));
    }
  };

  const handleReject = async (requestId: number) => {
    try {
      setActionLoading(prev => ({ ...prev, [requestId]: true }));
      await authService.rejectRequest(requestId);
      await loadRequests();
    } catch (err: any) {
      setError(err.response?.data?.detail || '요청 거절에 실패했습니다.');
    } finally {
      setActionLoading(prev => ({ ...prev, [requestId]: false }));
    }
  };

  const handleCancel = async (requestId: number) => {
    try {
      setActionLoading(prev => ({ ...prev, [requestId]: true }));
      await authService.cancelRequest(requestId);
      await loadRequests();
    } catch (err: any) {
      setError(err.response?.data?.detail || '요청 취소에 실패했습니다.');
    } finally {
      setActionLoading(prev => ({ ...prev, [requestId]: false }));
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return '대기 중';
      case 'accepted':
        return '수락됨';
      case 'rejected':
        return '거절됨';
      case 'cancelled':
        return '취소됨';
      default:
        return status;
    }
  };

  const getStatusClass = (status: string) => {
    switch (status) {
      case 'pending':
        return 'status-pending';
      case 'accepted':
        return 'status-accepted';
      case 'rejected':
        return 'status-rejected';
      case 'cancelled':
        return 'status-cancelled';
      default:
        return '';
    }
  };

  if (!user) {
    return <div>로딩 중...</div>;
  }

  return (
    <div className="requests-container">
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
          📋 요청 관리
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          {user.role === 'mentor' ? '받은 매칭 요청을 관리하세요' : '보낸 매칭 요청을 확인하세요'}
        </p>
      </div>

      {loading && <div style={{ textAlign: 'center' }}>로딩 중...</div>}
      {error && <div className="error-message">{error}</div>}

      {user.role === 'mentor' && (
        <div>
          <h2 style={{ color: 'var(--text-primary)', marginBottom: '1rem' }}>
            📨 받은 요청 ({incomingRequests.length})
          </h2>
          <div className="requests-list">
            {incomingRequests.length === 0 ? (
              <p>받은 요청이 없습니다.</p>
            ) : (
              incomingRequests.map((request) => (
                <div key={request.id} className="request-card">
                  <div className="request-message" {...({ mentee: request.menteeId.toString() } as any)}>
                    <strong>멘티 ID: {request.menteeId}</strong>
                    <p>{request.message}</p>
                  </div>
                  <div id="request-status" className={getStatusClass(request.status)}>
                    상태: {getStatusText(request.status)}
                  </div>
                  {request.status === 'pending' && (
                    <div className="request-actions" style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                      <button
                        id="accept"
                        className="btn-success"
                        onClick={() => handleAccept(request.id)}
                        disabled={actionLoading[request.id]}
                      >
                        {actionLoading[request.id] ? '⏳ 처리 중...' : '✅ 수락'}
                      </button>
                      <button
                        id="reject"
                        className="btn-danger"
                        onClick={() => handleReject(request.id)}
                        disabled={actionLoading[request.id]}
                      >
                        {actionLoading[request.id] ? '⏳ 처리 중...' : '❌ 거절'}
                      </button>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {user.role === 'mentee' && (
        <div>
          <h2 style={{ color: 'var(--text-primary)', marginBottom: '1rem' }}>
            📤 보낸 요청 ({outgoingRequests.length})
          </h2>
          <div className="requests-list">
            {outgoingRequests.length === 0 ? (
              <p>보낸 요청이 없습니다.</p>
            ) : (
              outgoingRequests.map((request) => (
                <div key={request.id} className="request-card">
                  <div>
                    <strong>멘토 ID: {request.mentorId}</strong>
                    <p>{request.message}</p>
                  </div>
                  <div id="request-status" className={getStatusClass(request.status)}>
                    상태: {getStatusText(request.status)}
                  </div>
                  {request.status === 'pending' && (
                    <div className="request-actions" style={{ marginTop: '1rem' }}>
                      <button
                        className="btn-danger"
                        onClick={() => handleCancel(request.id)}
                        disabled={actionLoading[request.id]}
                      >
                        {actionLoading[request.id] ? '⏳ 처리 중...' : '🗑️ 요청 취소'}
                      </button>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Requests;
