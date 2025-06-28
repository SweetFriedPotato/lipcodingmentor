import axios from 'axios';
import { User, SignupRequest, LoginRequest, LoginResponse, ProfileUpdateRequest, MatchRequest, MatchRequestCreate } from '../types';

const API_BASE_URL = 'http://localhost:8080/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 토큰 인터셉터
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  async signup(data: SignupRequest): Promise<void> {
    await api.post('/signup', data);
  },

  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/login', data);
    return response.data;
  },

  async getMe(): Promise<User> {
    const response = await api.get<User>('/me');
    return response.data;
  },

  async updateProfile(data: ProfileUpdateRequest): Promise<User> {
    const response = await api.put<User>('/profile', data);
    return response.data;
  },

  // 매칭 요청 관련 메서드들
  async getIncomingRequests(): Promise<MatchRequest[]> {
    const response = await api.get<MatchRequest[]>('/match-requests/incoming');
    return response.data;
  },

  async getOutgoingRequests(): Promise<MatchRequest[]> {
    const response = await api.get<MatchRequest[]>('/match-requests/outgoing');
    return response.data;
  },

  async acceptRequest(id: number): Promise<MatchRequest> {
    const response = await api.put<MatchRequest>(`/match-requests/${id}/accept`);
    return response.data;
  },

  async rejectRequest(id: number): Promise<MatchRequest> {
    const response = await api.put<MatchRequest>(`/match-requests/${id}/reject`);
    return response.data;
  },

  async cancelRequest(id: number): Promise<MatchRequest> {
    const response = await api.delete<MatchRequest>(`/match-requests/${id}`);
    return response.data;
  },

  // 매칭 요청 생성
  async createMatchRequest(data: { mentorId: number; message: string }): Promise<MatchRequest> {
    const response = await api.post<MatchRequest>('/match-requests', data);
    return response.data;
  },
};

export const mentorService = {
  async getMentors(skill?: string, orderBy?: string): Promise<User[]> {
    const params = new URLSearchParams();
    if (skill) params.append('skill', skill);
    if (orderBy) params.append('order_by', orderBy);
    
    const response = await api.get<User[]>(`/mentors?${params.toString()}`);
    return response.data;
  },
};

export const matchRequestService = {
  async createRequest(data: MatchRequestCreate): Promise<MatchRequest> {
    const response = await api.post<MatchRequest>('/match-requests', data);
    return response.data;
  },

  async getIncomingRequests(): Promise<MatchRequest[]> {
    const response = await api.get<MatchRequest[]>('/match-requests/incoming');
    return response.data;
  },

  async getOutgoingRequests(): Promise<MatchRequest[]> {
    const response = await api.get<MatchRequest[]>('/match-requests/outgoing');
    return response.data;
  },

  async acceptRequest(id: number): Promise<MatchRequest> {
    const response = await api.put<MatchRequest>(`/match-requests/${id}/accept`);
    return response.data;
  },

  async rejectRequest(id: number): Promise<MatchRequest> {
    const response = await api.put<MatchRequest>(`/match-requests/${id}/reject`);
    return response.data;
  },

  async cancelRequest(id: number): Promise<MatchRequest> {
    const response = await api.delete<MatchRequest>(`/match-requests/${id}`);
    return response.data;
  },
};

export default api;
